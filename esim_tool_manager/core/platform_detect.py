"""
Platform and Environment Detection Engine for eSim Automated Tool Manager
"""

import os
import sys
import shutil
import platform
import subprocess
from pathlib import Path
from typing import List, Optional

from esim_tool_manager.core.models import SystemPlatformInfo


class PlatformDetector:
    """Detects host operating system, architecture, package managers, and permissions."""

    @staticmethod
    def get_os_type() -> str:
        """Returns normalized os type: 'windows', 'linux', or 'darwin'."""
        system = platform.system().lower()
        if "windows" in system:
            return "windows"
        elif "darwin" in system:
            return "darwin"
        else:
            return "linux"

    @staticmethod
    def get_os_name() -> str:
        """Returns human-readable OS name and version."""
        try:
            if sys.platform.startswith("win"):
                release = platform.release()
                version = platform.version()
                return f"Windows {release} (Build {version})"
            elif sys.platform.startswith("darwin"):
                mac_ver = platform.mac_ver()[0]
                return f"macOS {mac_ver}"
            else:
                # Linux distribution detection
                if os.path.exists("/etc/os-release"):
                    with open("/etc/os-release", "r", encoding="utf-8") as f:
                        lines = dict(line.strip().split("=", 1) for line in f if "=" in line)
                        name = lines.get("PRETTY_NAME", lines.get("NAME", "Linux")).strip('"')
                        return name
                return f"Linux {platform.release()}"
        except Exception:
            return platform.platform()

    @staticmethod
    def get_architecture() -> str:
        machine = platform.machine().lower()
        if machine in ("amd64", "x86_64", "x64"):
            return "x86_64"
        elif machine in ("arm64", "aarch64"):
            return "arm64"
        elif machine in ("i386", "i686", "x86"):
            return "x86"
        return machine

    @staticmethod
    def is_admin() -> bool:
        """Checks if process has administrative or root rights."""
        try:
            if sys.platform.startswith("win"):
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                return os.geteuid() == 0
        except Exception:
            return False

    @staticmethod
    def detect_package_managers() -> List[str]:
        """Detects available CLI package managers installed on the system."""
        pms = []
        os_type = PlatformDetector.get_os_type()

        candidates = {
            "windows": ["winget", "choco", "scoop"],
            "linux": ["apt-get", "dnf", "yum", "pacman", "zypper"],
            "darwin": ["brew", "port"]
        }

        # Check OS candidates
        for pm in candidates.get(os_type, []):
            if shutil.which(pm) is not None:
                # normalize name (e.g. apt-get -> apt)
                norm = "apt" if pm == "apt-get" else pm
                if norm not in pms:
                    pms.append(norm)

        # Pip is always checked
        if shutil.which("pip") or shutil.which("pip3"):
            pms.append("pip")

        return pms

    @classmethod
    def get_system_info(cls) -> SystemPlatformInfo:
        """Returns structured SystemPlatformInfo dataclass."""
        os_type = cls.get_os_type()
        return SystemPlatformInfo(
            os_type=os_type,
            os_name=cls.get_os_name(),
            architecture=cls.get_architecture(),
            python_version=platform.python_version(),
            available_package_managers=cls.detect_package_managers(),
            is_admin=cls.is_admin(),
            home_dir=str(Path.home()),
            esim_default_path=os.environ.get("ESIM_HOME", "")
        )
