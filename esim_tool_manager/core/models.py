"""
Core Data Models for eSim Automated Tool Manager
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum


class StatusEnum(str, Enum):
    OK = "OK"
    OUTDATED = "OUTDATED"
    NOT_FOUND = "NOT_FOUND"
    INCOMPATIBLE = "INCOMPATIBLE"
    WARNING = "WARNING"
    ERROR = "ERROR"


@dataclass
class ToolDefinition:
    key: str
    name: str
    category: str
    description: str
    min_version: str
    recommended_version: str
    binary: Dict[str, str]
    version_check: Dict[str, Any]
    env_var: str
    install: Dict[str, Any]
    upstream: Dict[str, Any]


@dataclass
class ToolStatus:
    key: str
    name: str
    installed: bool = False
    version: Optional[str] = None
    min_version: str = ""
    recommended_version: str = ""
    latest_upstream_version: Optional[str] = None
    binary_path: Optional[str] = None
    env_var: str = ""
    env_var_value: Optional[str] = None
    status: StatusEnum = StatusEnum.NOT_FOUND
    status_message: str = ""
    update_available: bool = False


@dataclass
class DependencyStatus:
    name: str
    installed: bool = False
    installed_version: Optional[str] = None
    min_version: str = ""
    status: StatusEnum = StatusEnum.NOT_FOUND
    purpose: str = ""
    fix_command: str = ""


@dataclass
class SystemPlatformInfo:
    os_type: str            # 'windows', 'linux', 'darwin'
    os_name: str            # 'Windows 11', 'Ubuntu 25.04', etc.
    architecture: str       # 'x86_64', 'arm64'
    python_version: str     # '3.13.7'
    available_package_managers: List[str] = field(default_factory=list)
    is_admin: bool = False
    home_dir: str = ""
    esim_default_path: str = ""


@dataclass
class DiagnosticReport:
    platform_info: SystemPlatformInfo
    tools: Dict[str, ToolStatus] = field(default_factory=dict)
    dependencies: Dict[str, DependencyStatus] = field(default_factory=dict)
    environment_variables: Dict[str, Optional[str]] = field(default_factory=dict)
    summary: Dict[str, int] = field(default_factory=dict)

    def calculate_summary(self):
        total_items = len(self.tools) + len(self.dependencies)
        passed = sum(1 for t in self.tools.values() if t.status == StatusEnum.OK) + \
                 sum(1 for d in self.dependencies.values() if d.status == StatusEnum.OK)
        warnings = sum(1 for t in self.tools.values() if t.status in (StatusEnum.OUTDATED, StatusEnum.WARNING)) + \
                   sum(1 for d in self.dependencies.values() if d.status in (StatusEnum.OUTDATED, StatusEnum.WARNING))
        failed = sum(1 for t in self.tools.values() if t.status in (StatusEnum.NOT_FOUND, StatusEnum.INCOMPATIBLE, StatusEnum.ERROR)) + \
                 sum(1 for d in self.dependencies.values() if d.status in (StatusEnum.NOT_FOUND, StatusEnum.INCOMPATIBLE, StatusEnum.ERROR))
        self.summary = {
            "total": total_items,
            "passed": passed,
            "warnings": warnings,
            "failed": failed,
            "healthy": failed == 0
        }


@dataclass
class ActionLogEntry:
    timestamp: str
    action: str
    tool: str
    status: str
    details: str
