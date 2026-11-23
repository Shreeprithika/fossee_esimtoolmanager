"""
Dependency Checker & eSim Diagnostic Engine
"""

import os
import re
import sys
import json
import shutil
import subprocess
import importlib.util
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from esim_tool_manager.core.models import (
    StatusEnum,
    ToolStatus,
    DependencyStatus,
    DiagnosticReport,
    SystemPlatformInfo
)
from esim_tool_manager.core.config import config_manager
from esim_tool_manager.core.logger import logger
from esim_tool_manager.core.platform_detect import PlatformDetector


def parse_version_tuple(version_str: str) -> Tuple[int, ...]:
    """Extracts integer tuple from version string for clean comparison (e.g. '42.0.1' -> (42, 0, 1))."""
    if not version_str:
        return (0,)
    clean_parts = re.findall(r"\d+", version_str)
    return tuple(map(int, clean_parts)) if clean_parts else (0,)


def compare_versions(v1: str, v2: str) -> int:
    """Returns: 1 if v1 > v2, 0 if v1 == v2, -1 if v1 < v2."""
    t1 = parse_version_tuple(v1)
    t2 = parse_version_tuple(v2)
    # Pad shorter tuple with zeros
    max_len = max(len(t1), len(t2))
    t1 = t1 + (0,) * (max_len - len(t1))
    t2 = t2 + (0,) * (max_len - len(t2))
    if t1 > t2:
        return 1
    elif t1 < t2:
        return -1
    return 0


class DependencyChecker:
    """Scans and validates external tools and Python dependencies required for eSim."""

    def __init__(self, manifest_path: Optional[str] = None):
        if manifest_path is None:
            manifest_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "manifest.json"
            )
        self.manifest_path = manifest_path
        self.manifest_data = self._load_manifest()

    def _load_manifest(self) -> Dict[str, Any]:
        try:
            with open(self.manifest_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load manifest from {self.manifest_path}: {e}")
            return {"tools": {}, "python_dependencies": {}}

    def find_tool_binary(self, tool_key: str, tool_cfg: Dict[str, Any]) -> Optional[str]:
        """Locates tool executable via custom config, PATH, or default install folder."""
        # 1. Check user custom path override
        custom_path = config_manager.get_custom_path(tool_key)
        if custom_path and os.path.exists(custom_path):
            return custom_path

        # 2. Check binary name in PATH
        os_type = PlatformDetector.get_os_type()
        bin_names = tool_cfg.get("binary", {})
        bin_name = bin_names.get(os_type, tool_key)

        path_lookup = shutil.which(bin_name)
        if path_lookup:
            return path_lookup

        # 3. Check within tool manager default install dir
        install_dir = config_manager.get("install_dir")
        if install_dir and os.path.exists(install_dir):
            for root, _, files in os.walk(install_dir):
                if bin_name in files:
                    full_p = os.path.join(root, bin_name)
                    if os.access(full_p, os.X_OK) or sys.platform.startswith("win"):
                        return full_p

        # 4. Check typical installation locations on Windows/Linux
        common_paths = []
        if os_type == "windows":
            prog_files = os.environ.get("ProgramFiles", "C:\\Program Files")
            prog_files_x86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
            if tool_key == "ngspice":
                common_paths.extend([
                    os.path.join(prog_files, "Spice64", "bin", "ngspice.exe"),
                    "C:\\Spice64\\bin\\ngspice.exe",
                    "C:\\ngspice\\bin\\ngspice.exe"
                ])
            elif tool_key == "kicad":
                common_paths.extend([
                    os.path.join(prog_files, "KiCad", "8.0", "bin", "kicad.exe"),
                    os.path.join(prog_files, "KiCad", "7.0", "bin", "kicad.exe"),
                    os.path.join(prog_files, "KiCad", "bin", "kicad.exe")
                ])
            elif tool_key == "ghdl":
                common_paths.extend([
                    os.path.join(prog_files, "GHDL", "bin", "ghdl.exe"),
                    "C:\\GHDL\\bin\\ghdl.exe"
                ])
        elif os_type == "linux":
            common_paths.extend([
                f"/usr/bin/{bin_name}",
                f"/usr/local/bin/{bin_name}",
                f"/opt/{tool_key}/bin/{bin_name}"
            ])

        for p in common_paths:
            if os.path.exists(p):
                return p

        return None

    def query_binary_version(self, binary_path: str, tool_cfg: Dict[str, Any]) -> Optional[str]:
        """Executes binary with version arguments and extracts version via regex."""
        version_check = tool_cfg.get("version_check", {})
        args = version_check.get("args", ["--version"])
        pattern = version_check.get("regex", r"([0-9]+(\.[0-9]+)+)")

        try:
            cmd = [binary_path] + args
            proc = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5,
                shell=False
            )
            output = proc.stdout + " " + proc.stderr
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                # Return the main capturing group or whole match
                return match.group(1) if match.groups() else match.group(0)
            # Fallback: look for general semver pattern
            gen_match = re.search(r"(\d+\.\d+(\.\d+)?)", output)
            if gen_match:
                return gen_match.group(1)
        except Exception as e:
            logger.debug(f"Could not query version for {binary_path}: {e}")
        return None

    def check_tool(self, tool_key: str, tool_cfg: Dict[str, Any]) -> ToolStatus:
        """Evaluates health and status of a single external tool."""
        name = tool_cfg.get("name", tool_key)
        min_v = tool_cfg.get("min_version", "1.0.0")
        rec_v = tool_cfg.get("recommended_version", min_v)
        env_var = tool_cfg.get("env_var", f"{tool_key.upper()}_PATH")
        env_val = os.environ.get(env_var)

        binary_path = self.find_tool_binary(tool_key, tool_cfg)

        status = ToolStatus(
            key=tool_key,
            name=name,
            min_version=min_v,
            recommended_version=rec_v,
            binary_path=binary_path,
            env_var=env_var,
            env_var_value=env_val
        )

        if not binary_path:
            status.installed = False
            status.status = StatusEnum.NOT_FOUND
            status.status_message = "Not found in system PATH or configured directories."
            return status

        status.installed = True
        version = self.query_binary_version(binary_path, tool_cfg)
        status.version = version or "Unknown"

        if version and version != "Unknown":
            if compare_versions(version, min_v) < 0:
                status.status = StatusEnum.INCOMPATIBLE
                status.status_message = f"Version {version} is below minimum requirement ({min_v})."
            elif compare_versions(version, rec_v) < 0:
                status.status = StatusEnum.OUTDATED
                status.status_message = f"Version {version} is older than recommended ({rec_v})."
                status.update_available = True
            else:
                status.status = StatusEnum.OK
                status.status_message = f"Version {version} satisfies requirements (>= {min_v})."
        else:
            status.status = StatusEnum.WARNING
            status.status_message = "Binary found, but version could not be parsed."

        return status

    def check_python_dependency(self, pkg_name: str, dep_cfg: Dict[str, Any]) -> DependencyStatus:
        """Inspects whether a Python dependency is installed and compatible."""
        min_v = dep_cfg.get("min_version", "1.0.0")
        purpose = dep_cfg.get("purpose", "")
        alternative = dep_cfg.get("alternative")

        dep_status = DependencyStatus(
            name=pkg_name,
            min_version=min_v,
            purpose=purpose,
            fix_command=f"python -m pip install {pkg_name}"
        )

        # Check alternative package if primary is PyQt5 and running Python 3.12+
        targets = [pkg_name]
        if alternative:
            targets.append(alternative)

        installed_pkg = None
        installed_version = None

        for target in targets:
            try:
                # Use importlib
                spec = importlib.util.find_spec(target)
                if spec is not None:
                    mod = __import__(target)
                    installed_pkg = target
                    installed_version = getattr(mod, "__version__", None)
                    if not installed_version:
                        try:
                            import importlib.metadata as md
                            installed_version = md.version(target)
                        except Exception:
                            installed_version = "Unknown"
                    break
            except Exception:
                continue

        if not installed_pkg:
            dep_status.installed = False
            dep_status.status = StatusEnum.NOT_FOUND
            return dep_status

        dep_status.installed = True
        dep_status.name = installed_pkg
        dep_status.installed_version = installed_version or "Unknown"

        if installed_version and installed_version != "Unknown":
            if compare_versions(installed_version, min_v) < 0:
                dep_status.status = StatusEnum.OUTDATED
                dep_status.fix_command = f"python -m pip install --upgrade {installed_pkg}"
            else:
                dep_status.status = StatusEnum.OK
        else:
            dep_status.status = StatusEnum.OK

        return dep_status

    def run_full_diagnostic(self) -> DiagnosticReport:
        """Executes full system diagnostic across all tools, Python modules, and env vars."""
        platform_info = PlatformDetector.get_system_info()
        report = DiagnosticReport(platform_info=platform_info)

        # Check Tools
        tools_cfg = self.manifest_data.get("tools", {})
        for key, cfg in tools_cfg.items():
            tool_status = self.check_tool(key, cfg)
            report.tools[key] = tool_status

        # Check Python Dependencies
        deps_cfg = self.manifest_data.get("python_dependencies", {})
        for key, cfg in deps_cfg.items():
            dep_status = self.check_python_dependency(key, cfg)
            report.dependencies[key] = dep_status

        # Check Environment Variables
        for key, cfg in tools_cfg.items():
            env_var = cfg.get("env_var", f"{key.upper()}_PATH")
            report.environment_variables[env_var] = os.environ.get(env_var)

        report.calculate_summary()
        return report
