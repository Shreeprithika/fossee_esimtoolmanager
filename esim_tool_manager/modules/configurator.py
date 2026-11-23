"""
Configuration and Path Management Engine for eSim Automated Tool Manager
Handles PATH management, environment variables, and eSim configuration exports.
"""

import os
import sys
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List

from esim_tool_manager.core.logger import logger, auditor
from esim_tool_manager.core.config import config_manager
from esim_tool_manager.core.platform_detect import PlatformDetector
from esim_tool_manager.modules.dependency_checker import DependencyChecker


class ToolConfigurator:
    """Manages environment variables, PATH configuration, and eSim tool configuration profiles."""

    def __init__(self, manifest_path: Optional[str] = None):
        self.checker = DependencyChecker(manifest_path)
        self.manifest = self.checker.manifest_data

    def detect_all_tool_paths(self) -> Dict[str, str]:
        """Discovers full absolute paths for all installed tools."""
        paths = {}
        tools_cfg = self.manifest.get("tools", {})
        for key, cfg in tools_cfg.items():
            bin_path = self.checker.find_tool_binary(key, cfg)
            if bin_path:
                paths[key] = os.path.abspath(bin_path)
        return paths

    def configure_environment(self, custom_paths: Optional[Dict[str, str]] = None, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Gathers tool paths, updates configuration manager, and exports:
        - config.ini
        - .esimrc
        - setup_esim_env.bat (Windows)
        - setup_esim_env.sh (Linux/macOS)
        """
        logger.info("Configuring eSim tool paths and environment profiles...")
        active_paths = self.detect_all_tool_paths()

        if custom_paths:
            active_paths.update(custom_paths)
            for k, v in custom_paths.items():
                config_manager.set_custom_path(k, v)

        # Export eSim configuration profiles
        export_results = config_manager.export_esim_profile(active_paths, output_dir)

        # Also set process environment variables for current session
        bin_dirs = []
        for tool, p in active_paths.items():
            env_var = f"{tool.upper()}_PATH"
            os.environ[env_var] = p
            parent_dir = str(Path(p).parent) if os.path.isfile(p) else p
            if parent_dir not in bin_dirs:
                bin_dirs.append(parent_dir)

        if bin_dirs:
            current_path = os.environ.get("PATH", "")
            sep = ";" if sys.platform.startswith("win") else ":"
            new_path = sep.join(bin_dirs) + sep + current_path
            os.environ["PATH"] = new_path

        auditor.record_action(
            action="CONFIGURE_ENVIRONMENT",
            tool="ALL",
            status="SUCCESS",
            details=f"Configured {len(active_paths)} tool paths.",
            extra={"paths": active_paths, "files": export_results}
        )

        logger.info(f"Environment configuration completed for {len(active_paths)} tools.")
        return {
            "configured_tools": active_paths,
            "exported_files": export_results
        }

    def generate_persistent_system_script(self, output_path: Optional[str] = None) -> str:
        """
        Generates a script to permanently apply tool paths to user's system profile.
        Windows: .ps1 setting [Environment]::SetEnvironmentVariable
        Linux: adds exports to ~/.bashrc or provides a sourceable script.
        """
        paths = self.detect_all_tool_paths()
        os_type = PlatformDetector.get_os_type()

        if os_type == "windows":
            script_path = output_path or "apply_persistent_env.ps1"
            lines = [
                "# PowerShell script to set permanent User Environment Variables for eSim",
                "Write-Host '[eSim Tool Manager] Setting permanent environment variables...'"
            ]
            path_dirs = []
            for tool, p in paths.items():
                var_name = f"{tool.upper()}_PATH"
                lines.append(f"[Environment]::SetEnvironmentVariable('{var_name}', '{p}', 'User')")
                parent = str(Path(p).parent)
                if parent not in path_dirs:
                    path_dirs.append(parent)

            if path_dirs:
                joined = ";".join(path_dirs)
                lines.append("$currPath = [Environment]::GetEnvironmentVariable('Path', 'User')")
                lines.append(f"$newDirs = '{joined}'")
                lines.append("if (-not $currPath.Contains($newDirs)) { [Environment]::SetEnvironmentVariable('Path', $currPath + ';' + $newDirs, 'User') }")
            lines.append("Write-Host '[eSim Tool Manager] Environment configured! Restart terminals.'")

            with open(script_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")
            logger.info(f"Generated persistent environment script: {script_path}")
            return script_path
        else:
            script_path = output_path or "apply_persistent_env.sh"
            lines = [
                "#!/usr/bin/env bash",
                "# Shell script to configure persistent environment for eSim",
                "echo '[eSim Tool Manager] Appending tool exports to ~/.bashrc...'"
            ]
            for tool, p in paths.items():
                var_name = f"{tool.upper()}_PATH"
                lines.append(f"grep -qxF 'export {var_name}=\"{p}\"' ~/.bashrc || echo 'export {var_name}=\"{p}\"' >> ~/.bashrc")
            lines.append("echo '[eSim Tool Manager] Done. Run: source ~/.bashrc'")

            with open(script_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")
            os.chmod(script_path, 0o755)
            logger.info(f"Generated persistent environment script: {script_path}")
            return script_path
