"""
Update and Upgrade Engine for eSim Automated Tool Manager
Checks upstream releases and manages single-click automated tool upgrades.
"""

import os
import sys
import json
import shutil
import urllib.request
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from esim_tool_manager.core.logger import logger, auditor
from esim_tool_manager.core.config import config_manager
from esim_tool_manager.core.platform_detect import PlatformDetector
from esim_tool_manager.modules.dependency_checker import DependencyChecker, compare_versions
from esim_tool_manager.modules.installer import ToolInstaller


class ToolUpdater:
    """Detects newer versions of external tools and performs automated upgrades with rollback support."""

    def __init__(self, manifest_path: Optional[str] = None):
        self.checker = DependencyChecker(manifest_path)
        self.installer = ToolInstaller(manifest_path)
        self.manifest = self.checker.manifest_data

    def fetch_latest_github_release(self, repo: str) -> Optional[str]:
        """Queries GitHub API for the latest release tag."""
        url = f"https://api.github.com/repos/{repo}/releases/latest"
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "eSim-Tool-Manager/1.0 (FOSSEE)"}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
                tag = data.get("tag_name", "").lstrip("v")
                return tag
        except Exception as e:
            logger.debug(f"Could not fetch GitHub release for {repo}: {e}")
            return None

    def fetch_latest_pypi_version(self, package_name: str) -> Optional[str]:
        """Queries PyPI JSON API for latest package version."""
        url = f"https://pypi.org/pypi/{package_name}/json"
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "eSim-Tool-Manager/1.0 (FOSSEE)"}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
                return data.get("info", {}).get("version")
        except Exception as e:
            logger.debug(f"Could not fetch PyPI release for {package_name}: {e}")
            return None

    def get_latest_upstream_version(self, tool_key: str) -> Optional[str]:
        """Determines the latest upstream release for a tool."""
        tool_cfg = self.manifest.get("tools", {}).get(tool_key, {})
        upstream = tool_cfg.get("upstream", {})
        u_type = upstream.get("type")

        if u_type == "github":
            repo = upstream.get("repo")
            if repo:
                return self.fetch_latest_github_release(repo)
        elif u_type == "pip":
            pkg = upstream.get("package", tool_key)
            return self.fetch_latest_pypi_version(pkg)

        # Fallback to recommended version defined in manifest
        return tool_cfg.get("recommended_version")

    def check_for_updates(self, tool_key: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Checks whether an update is available for tool.
        Returns: (update_available, current_version, latest_version)
        """
        tool_cfg = self.manifest.get("tools", {}).get(tool_key, {})
        status = self.checker.check_tool(tool_key, tool_cfg)
        if not status.installed or not status.version or status.version == "Unknown":
            return False, status.version, None

        latest_v = self.get_latest_upstream_version(tool_key)
        if not latest_v:
            return False, status.version, None

        has_update = compare_versions(latest_v, status.version) > 0
        return has_update, status.version, latest_v

    def create_tool_backup(self, tool_key: str) -> Optional[str]:
        """Creates a timestamped backup of the tool folder before upgrading."""
        install_base = config_manager.get("install_dir")
        tool_dir = os.path.join(install_base, tool_key)
        if not os.path.exists(tool_dir):
            return None

        backup_base = config_manager.get("backup_dir")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(backup_base, f"{tool_key}_{timestamp}")

        try:
            os.makedirs(backup_base, exist_ok=True)
            shutil.copytree(tool_dir, backup_dir)
            logger.info(f"Created backup of {tool_key} at {backup_dir}")
            auditor.record_action(
                action="BACKUP",
                tool=tool_key,
                status="SUCCESS",
                details=f"Backup saved to {backup_dir}"
            )
            return backup_dir
        except Exception as e:
            logger.warning(f"Failed to create backup for {tool_key}: {e}")
            return None

    def rollback_backup(self, tool_key: str, backup_dir: str) -> bool:
        """Restores tool directory from backup in case upgrade fails."""
        install_base = config_manager.get("install_dir")
        tool_dir = os.path.join(install_base, tool_key)
        logger.warning(f"Initiating rollback of {tool_key} from {backup_dir}...")
        try:
            if os.path.exists(tool_dir):
                shutil.rmtree(tool_dir)
            shutil.copytree(backup_dir, tool_dir)
            logger.info(f"Rollback of {tool_key} completed successfully.")
            auditor.record_action(
                action="ROLLBACK",
                tool=tool_key,
                status="RESTORED",
                details=f"Restored from {backup_dir}"
            )
            return True
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False

    def upgrade_tool(self, tool_key: str, dry_run: bool = False) -> bool:
        """Performs upgrade of tool with automatic backup and rollback."""
        logger.info(f"Starting upgrade process for {tool_key}...")
        has_update, current_v, latest_v = self.check_for_updates(tool_key)
        if not has_update and not dry_run:
            logger.info(f"Tool {tool_key} is already at latest version ({current_v}).")
            return True

        logger.info(f"Upgrading {tool_key}: {current_v} -> {latest_v}")

        # Create backup if auto_backup is enabled
        backup_dir = None
        if config_manager.get("auto_backup", True) and not dry_run:
            backup_dir = self.create_tool_backup(tool_key)

        # Execute installation/upgrade
        success = self.installer.install_tool(tool_key, dry_run=dry_run)

        if not success and backup_dir:
            logger.error(f"Upgrade for {tool_key} failed! Triggering rollback...")
            self.rollback_backup(tool_key, backup_dir)
            return False

        if success:
            logger.info(f"Successfully upgraded {tool_key} to version {latest_v}!")
            auditor.record_action(
                action="UPGRADE_TOOL",
                tool=tool_key,
                status="SUCCESS",
                details=f"{current_v} -> {latest_v}"
            )
            return True
        return False

    def upgrade_all(self, dry_run: bool = False) -> Dict[str, bool]:
        """Upgrades all installed tools that have updates available."""
        results = {}
        tools_cfg = self.manifest.get("tools", {})
        for key in tools_cfg:
            has_update, curr, latest = self.check_for_updates(key)
            if has_update:
                results[key] = self.upgrade_tool(key, dry_run=dry_run)
            else:
                results[key] = True
        return results
