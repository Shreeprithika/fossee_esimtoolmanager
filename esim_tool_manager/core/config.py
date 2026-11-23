"""
Configuration and Environment Profile Manager for eSim Automated Tool Manager
"""

import os
import sys
import json
import configparser
from pathlib import Path
from typing import Dict, Any, Optional

DEFAULT_CONFIG_FILE = "esim_manager_config.json"


class ConfigurationManager:
    """Manages Tool Manager preferences and eSim environment exports."""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.path.abspath(DEFAULT_CONFIG_FILE)
        self.config_data = self._load_default_config()
        self.load()

    def _get_default_install_dir(self) -> str:
        home = Path.home()
        if sys.platform.startswith("win"):
            return str(home / "AppData" / "Local" / "eSim_Tools")
        else:
            return str(home / ".esim" / "tools")

    def _load_default_config(self) -> Dict[str, Any]:
        return {
            "install_dir": self._get_default_install_dir(),
            "preferred_package_manager": "auto",
            "auto_backup": True,
            "backup_dir": str(Path.home() / ".esim" / "backups"),
            "check_updates_on_startup": True,
            "custom_paths": {},
            "esim_home": os.environ.get("ESIM_HOME", ""),
            "log_level": "INFO"
        }

    def load(self):
        """Loads configuration from JSON file if exists, otherwise saves defaults."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.config_data.update(data)
            except Exception as e:
                sys.stderr.write(f"Warning: Failed to parse config file: {e}\n")
        else:
            self.save()

    def save(self):
        """Persists configuration to JSON file."""
        try:
            os.makedirs(os.path.dirname(os.path.abspath(self.config_path)), exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config_data, f, indent=2)
        except Exception as e:
            sys.stderr.write(f"Warning: Failed to save config file: {e}\n")

    def get(self, key: str, default: Any = None) -> Any:
        return self.config_data.get(key, default)

    def set(self, key: str, value: Any):
        self.config_data[key] = value
        self.save()

    def set_custom_path(self, tool_key: str, path: str):
        if "custom_paths" not in self.config_data:
            self.config_data["custom_paths"] = {}
        self.config_data["custom_paths"][tool_key] = path
        self.save()

    def get_custom_path(self, tool_key: str) -> Optional[str]:
        return self.config_data.get("custom_paths", {}).get(tool_key)

    def export_esim_profile(self, tool_paths: Dict[str, str], output_dir: Optional[str] = None) -> Dict[str, str]:
        """
        Exports environment variables and configuration files for eSim:
        - config.ini (eSim standard format)
        - setup_esim_env.bat (Windows launcher/environment activator)
        - setup_esim_env.sh (Linux/macOS launcher/activator)
        - .esimrc (JSON profile)
        """
        target_dir = output_dir or os.getcwd()
        os.makedirs(target_dir, exist_ok=True)
        results = {}

        # 1. Export JSON .esimrc
        json_path = os.path.join(target_dir, ".esimrc")
        profile = {
            "version": "1.0",
            "tools": tool_paths,
            "generated_by": "eSim Automated Tool Manager"
        }
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=2)
        results["json_profile"] = json_path

        # 2. Export INI config
        ini_path = os.path.join(target_dir, "config.ini")
        config = configparser.ConfigParser()
        config["TOOLS"] = tool_paths
        config["GENERAL"] = {
            "auto_configured": "true",
            "manager_version": "1.0.0"
        }
        with open(ini_path, "w", encoding="utf-8") as f:
            config.write(f)
        results["ini_profile"] = ini_path

        # 3. Export Environment Setup scripts
        # Windows BAT
        bat_path = os.path.join(target_dir, "setup_esim_env.bat")
        with open(bat_path, "w", encoding="utf-8") as f:
            f.write("@echo off\nREM Auto-generated eSim Environment Setup\n")
            bin_dirs = []
            for tool, path in tool_paths.items():
                env_var = f"{tool.upper()}_PATH"
                f.write(f'set "{env_var}={path}"\n')
                p = Path(path)
                parent_dir = str(p.parent) if p.is_file() else path
                if parent_dir not in bin_dirs:
                    bin_dirs.append(parent_dir)
            if bin_dirs:
                joined = ";".join(bin_dirs)
                f.write(f'set "PATH={joined};%PATH%"\n')
            f.write('echo [eSim] External tool environment configured successfully.\n')
        results["windows_bat"] = bat_path

        # Linux/macOS Shell Script
        sh_path = os.path.join(target_dir, "setup_esim_env.sh")
        with open(sh_path, "w", encoding="utf-8") as f:
            f.write("#!/usr/bin/env bash\n# Auto-generated eSim Environment Setup\n")
            bin_dirs = []
            for tool, path in tool_paths.items():
                env_var = f"{tool.upper()}_PATH"
                f.write(f'export {env_var}="{path}"\n')
                p = Path(path)
                parent_dir = str(p.parent) if p.is_file() else path
                if parent_dir not in bin_dirs:
                    bin_dirs.append(parent_dir)
            if bin_dirs:
                joined = ":".join(bin_dirs)
                f.write(f'export PATH="{joined}:$PATH"\n')
            f.write('echo "[eSim] External tool environment configured successfully."\n')
        results["shell_script"] = sh_path

        return results


# Global singleton instance
config_manager = ConfigurationManager()
