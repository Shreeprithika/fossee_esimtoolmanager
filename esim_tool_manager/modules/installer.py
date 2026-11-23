"""
Tool Installation Engine for eSim Automated Tool Manager
Supports Package Managers (apt, dnf, pacman, winget, choco, brew) and Direct Portable Downloads.
"""

import os
import sys
import shutil
import zipfile
import tarfile
import urllib.request
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, Callable, List

from esim_tool_manager.core.logger import logger, auditor
from esim_tool_manager.core.config import config_manager
from esim_tool_manager.core.platform_detect import PlatformDetector
from esim_tool_manager.modules.dependency_checker import DependencyChecker


class ToolInstaller:
    """Orchestrates automated download, extraction, package manager execution, and setup of external tools."""

    def __init__(self, manifest_path: Optional[str] = None):
        self.checker = DependencyChecker(manifest_path)
        self.manifest = self.checker.manifest_data

    def download_file(
        self,
        url: str,
        dest_path: str,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> bool:
        """Downloads a remote file with progress reporting."""
        logger.info(f"Downloading from {url} to {dest_path}...")
        try:
            os.makedirs(os.path.dirname(os.path.abspath(dest_path)), exist_ok=True)
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "eSim-Tool-Manager/1.0 (FOSSEE)"}
            )
            with urllib.request.urlopen(req, timeout=30) as response, open(dest_path, "wb") as out_file:
                total_size = int(response.headers.get("Content-Length", 0))
                downloaded = 0
                chunk_size = 65536
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    out_file.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback and total_size > 0:
                        progress_callback(downloaded, total_size)
            logger.info("Download completed successfully.")
            return True
        except Exception as e:
            logger.error(f"Download failed: {e}")
            if os.path.exists(dest_path):
                try:
                    os.remove(dest_path)
                except Exception:
                    pass
            return False

    def extract_archive(self, archive_path: str, extract_to: str) -> bool:
        """Extracts zip or tar archives into destination folder."""
        logger.info(f"Extracting {archive_path} to {extract_to}...")
        try:
            os.makedirs(extract_to, exist_ok=True)
            if zipfile.is_zipfile(archive_path):
                with zipfile.ZipFile(archive_path, "r") as zf:
                    zf.extractall(extract_to)
            elif tarfile.is_tarfile(archive_path):
                with tarfile.open(archive_path, "r:*") as tf:
                    tf.extractall(extract_to)
            else:
                logger.error(f"Unsupported archive format: {archive_path}")
                return False
            logger.info("Extraction completed successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to extract archive: {e}")
            return False

    def install_via_package_manager(
        self,
        tool_key: str,
        pm_name: str,
        package_identifier: Any,
        dry_run: bool = False
    ) -> bool:
        """Executes installation using host package manager."""
        cmd = []
        if pm_name == "winget":
            cmd = ["winget", "install", "--id", str(package_identifier), "--silent",
                   "--accept-package-agreements", "--accept-source-agreements"]
        elif pm_name == "choco":
            cmd = ["choco", "install", str(package_identifier), "-y"]
        elif pm_name == "apt":
            pkgs = package_identifier if isinstance(package_identifier, list) else [package_identifier]
            cmd = ["apt-get", "install", "-y"] + pkgs
            if not PlatformDetector.is_admin():
                cmd = ["sudo"] + cmd
        elif pm_name == "dnf":
            pkgs = package_identifier if isinstance(package_identifier, list) else [package_identifier]
            cmd = ["dnf", "install", "-y"] + pkgs
            if not PlatformDetector.is_admin():
                cmd = ["sudo"] + cmd
        elif pm_name == "pacman":
            pkgs = package_identifier if isinstance(package_identifier, list) else [package_identifier]
            cmd = ["pacman", "-S", "--noconfirm"] + pkgs
            if not PlatformDetector.is_admin():
                cmd = ["sudo"] + cmd
        elif pm_name == "brew":
            pkgs = package_identifier if isinstance(package_identifier, list) else [package_identifier]
            cmd = ["brew", "install"] + pkgs
        elif pm_name == "pip":
            pkg = str(package_identifier)
            cmd = [sys.executable, "-m", "pip", "install", pkg]
        else:
            logger.error(f"Unsupported package manager: {pm_name}")
            return False

        logger.info(f"Running command: {' '.join(cmd)}")
        auditor.record_action(
            action="INSTALL_COMMAND",
            tool=tool_key,
            status="EXECUTING",
            details=" ".join(cmd)
        )

        if dry_run:
            logger.info("[Dry Run] Skipping actual command execution.")
            return True

        try:
            proc = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            if proc.returncode == 0:
                logger.info(f"Package manager install of {tool_key} succeeded.")
                auditor.record_action(
                    action="INSTALL_TOOL",
                    tool=tool_key,
                    status="SUCCESS",
                    details=f"Installed via {pm_name}"
                )
                return True
            else:
                logger.error(f"Installation failed with code {proc.returncode}:\n{proc.stderr}")
                auditor.record_action(
                    action="INSTALL_TOOL",
                    tool=tool_key,
                    status="FAILED",
                    details=f"Code {proc.returncode}: {proc.stderr[:200]}"
                )
                return False
        except Exception as e:
            logger.error(f"Exception executing package manager: {e}")
            auditor.record_action(
                action="INSTALL_TOOL",
                tool=tool_key,
                status="ERROR",
                details=str(e)
            )
            return False

    def install_via_direct_download(
        self,
        tool_key: str,
        download_cfg: Dict[str, Any],
        dry_run: bool = False,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> bool:
        """Downloads pre-built portable binary package, extracts, and registers executable."""
        url = download_cfg.get("url")
        if not url:
            logger.error(f"No direct download URL available for {tool_key}.")
            return False

        install_base = config_manager.get("install_dir")
        tool_dir = os.path.join(install_base, tool_key)
        archive_name = os.path.basename(url.split("?")[0])
        archive_path = os.path.join(install_base, "downloads", archive_name)

        if dry_run:
            logger.info(f"[Dry Run] Would download from {url} to {tool_dir}")
            return True

        # 1. Download archive
        success = self.download_file(url, archive_path, progress_callback)
        if not success:
            return False

        # 2. Extract archive
        success = self.extract_archive(archive_path, tool_dir)
        if not success:
            return False

        # 3. Locate executable
        rel_path = download_cfg.get("executable_relative_path")
        candidate_exe = None
        if rel_path:
            full_exe = os.path.join(tool_dir, rel_path)
            if os.path.exists(full_exe):
                candidate_exe = full_exe

        if not candidate_exe:
            # Fallback search inside tool_dir
            tool_cfg = self.manifest.get("tools", {}).get(tool_key, {})
            os_type = PlatformDetector.get_os_type()
            bin_name = tool_cfg.get("binary", {}).get(os_type, tool_key)
            for root, _, files in os.walk(tool_dir):
                if bin_name in files:
                    candidate_exe = os.path.join(root, bin_name)
                    break

        if candidate_exe:
            if not sys.platform.startswith("win"):
                os.chmod(candidate_exe, 0o755)
            # Register in custom paths configuration
            config_manager.set_custom_path(tool_key, candidate_exe)
            logger.info(f"Registered {tool_key} executable at {candidate_exe}")
            auditor.record_action(
                action="INSTALL_DIRECT",
                tool=tool_key,
                status="SUCCESS",
                details=f"Extracted to {candidate_exe}"
            )
            return True
        else:
            logger.warning(f"Archive extracted to {tool_dir}, but could not locate main executable.")
            auditor.record_action(
                action="INSTALL_DIRECT",
                tool=tool_key,
                status="WARNING",
                details=f"Extracted but executable not verified in {tool_dir}"
            )
            return True

    def install_tool(
        self,
        tool_key: str,
        method: Optional[str] = None,
        dry_run: bool = False,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> bool:
        """High-level installer: selects best method (package manager or direct download) and installs tool."""
        tools_cfg = self.manifest.get("tools", {})
        if tool_key not in tools_cfg:
            logger.error(f"Unknown tool: '{tool_key}' not found in manifest.")
            return False

        tool_cfg = tools_cfg[tool_key]
        os_type = PlatformDetector.get_os_type()
        install_specs = tool_cfg.get("install", {}).get(os_type, {})

        if not install_specs:
            logger.error(f"No installation instructions defined for {tool_key} on {os_type}.")
            return False

        available_pms = PlatformDetector.detect_package_managers()
        user_pm_pref = method or config_manager.get("preferred_package_manager", "auto")

        # 1. Check if pip installation specified
        if "pip" in install_specs:
            return self.install_via_package_manager(
                tool_key=tool_key,
                pm_name="pip",
                package_identifier=install_specs["pip"],
                dry_run=dry_run
            )

        # 2. Try Package Manager
        pm_specs = install_specs.get("package_manager", {})
        if user_pm_pref != "direct":
            for pm in available_pms:
                if user_pm_pref != "auto" and pm != user_pm_pref:
                    continue
                if pm in pm_specs:
                    logger.info(f"Attempting to install {tool_key} using {pm}...")
                    ok = self.install_via_package_manager(tool_key, pm, pm_specs[pm], dry_run)
                    if ok:
                        return True

        # 3. Fallback to Direct Download if available
        if "direct_download" in install_specs:
            logger.info(f"Attempting direct portable installation for {tool_key}...")
            return self.install_via_direct_download(
                tool_key=tool_key,
                download_cfg=install_specs["direct_download"],
                dry_run=dry_run,
                progress_callback=progress_callback
            )

        logger.error(f"Could not find a suitable installation method for {tool_key} on {os_type}.")
        return False

    def install_all_missing(self, dry_run: bool = False) -> Dict[str, bool]:
        """Runs diagnostic and automatically installs all missing or incompatible tools."""
        report = self.checker.run_full_diagnostic()
        results = {}
        for key, status in report.tools.items():
            if not status.installed:
                logger.info(f"Installing missing tool: {key} ({status.name})...")
                results[key] = self.install_tool(key, dry_run=dry_run)
            else:
                logger.info(f"Tool {key} already installed ({status.version}). Skipping.")
                results[key] = True
        return results

    def install_python_dependencies(self, dry_run: bool = False) -> bool:
        """Installs all required Python dependencies via pip."""
        deps = self.manifest.get("python_dependencies", {})
        missing_pkgs = []
        for pkg, cfg in deps.items():
            status = self.checker.check_python_dependency(pkg, cfg)
            if not status.installed or status.status != "OK":
                missing_pkgs.append(pkg)

        if not missing_pkgs:
            logger.info("All Python dependencies are already installed and up to date.")
            return True

        logger.info(f"Installing missing Python dependencies: {', '.join(missing_pkgs)}")
        cmd = [sys.executable, "-m", "pip", "install"] + missing_pkgs
        if dry_run:
            logger.info(f"[Dry Run] Would execute: {' '.join(cmd)}")
            return True

        proc = subprocess.run(cmd, check=False)
        return proc.returncode == 0
