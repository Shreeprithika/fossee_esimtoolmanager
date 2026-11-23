# eSim Automated Tool Manager (eSim-ATM)

[![Python Version](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-green.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()
[![Tests](https://img.shields.io/badge/tests-17%20passed%2C%200%20failed-brightgreen.svg)]()
[![Task](https://img.shields.io/badge/eSim%20Internship-Task%205%3A%20Tool%20Manager-orange.svg)]()

> **FOSSEE eSim Winter Internship - 2026 / Semester Long Internship (Autumn 2026)**  
> **Screening Task 5: Tool Manager (CSE and related fields)**

The **eSim Automated Tool Manager** is a cross-platform tool and dependency management suite for [FOSSEE eSim EDA](https://esim.fossee.in/). It automates the discovery, installation, configuration, health verification, and updating of external tools and libraries required for circuit simulation and PCB design.

---

## 🌟 Key Features

The project fulfills and exceeds **all five requirements** of the screening task:

| Requirement | Implementation Feature | Description |
|:---|:---|:---|
| **1. Tool Installation Management** | Multi-Backend Installer | Automatically downloads and installs required external tools (**Ngspice**, **KiCad**, **GHDL**, **Verilator**, **Makerchip**, **C/C++ Build Toolchain**) via native package managers (`winget`, `choco`, `apt`, `dnf`, `pacman`, `brew`) or zero-privilege direct portable downloads with extraction and version pinning. |
| **2. Update & Upgrade System** | Upstream Version Engine | Checks upstream releases via GitHub Releases API and PyPI API. Performs automated 1-click upgrades with **pre-update backups** and **automatic rollback** upon failure. |
| **3. Configuration Handling** | Path & Environment Manager | Automatically discovers tool binaries, updates system `PATH`, configures environment variables (`NGSPICE_PATH`, `KICAD_PATH`, `GHDL_PATH`, etc.), and exports `.esimrc`, `config.ini`, Windows launcher (`setup_esim_env.bat`), and Linux/macOS launcher (`setup_esim_env.sh`). |
| **4. Dependency Checker** | "eSim Doctor" Diagnostic | Comprehensive pre-flight health scanner that checks binaries, semver requirements, Python dependencies (`matplotlib`, `numpy`, `scipy`, `PyQt5`/`PyQt6`, `ply`), and system permissions. |
| **5. User Interface** | Dual CLI & Modern GUI | High-productivity Command-Line Interface with colorized badges and tables, alongside a responsive, dark-themed Graphical User Interface built with Tkinter/TTK. |
| **Bonus: Audit & Action Logging** | Structured Audit Trail | Every command, download, install, upgrade, and error is recorded in both human-readable logs (`esim_tool_manager.log`) and structured JSON Lines (`esim_actions.jsonl`). |

---

## 📁 Repository Directory Structure

```text
fossee/
├── esim_tool_manager/              # Core Python package
│   ├── __init__.py                 # Package version and metadata
│   ├── cli.py                      # Command-Line Interface with formatted output
│   ├── gui.py                      # Modern Graphical User Interface (Tkinter / TTK)
│   ├── manifest.json               # Extensible JSON schema of external tools
│   ├── core/                       # Core foundation services
│   │   ├── __init__.py
│   │   ├── models.py               # Typed dataclasses and status enums
│   │   ├── config.py               # Configuration manager & profile exporter
│   │   ├── logger.py               # Action auditor and dual file/console logging
│   │   └── platform_detect.py      # Cross-platform OS & package manager detector
│   └── modules/                    # Functional business logic engines
│       ├── __init__.py
│       ├── dependency_checker.py   # Diagnostic scanner & version parser ("eSim Doctor")
│       ├── installer.py            # Package manager & direct download installer
│       ├── updater.py              # Upstream release checker & rollback engine
│       └── configurator.py         # Path manager & environment profile generator
├── tests/                          # Automated test suite (100% standard library)
│   ├── __init__.py
│   ├── test_platform.py            # Tests for OS & package manager detection
│   ├── test_dependency_checker.py  # Tests for version parsing & diagnostic scanner
│   ├── test_config.py              # Tests for configuration and profile export
│   ├── test_installer.py           # Tests for archive extraction & installation logic
│   ├── test_updater.py             # Tests for backups, updates, and rollback
│   └── run_tests.py                # Master test runner
├── scripts/                        # Utility and demonstration scripts
│   └── demo.py                     # 60-second automated end-to-end showcase
├── DESIGN_DOCUMENT.md              # Complete Architectural Design Document
├── PRESENTATION_OUTLINE.md         # Video demo script and slide deck outline
├── SUBMISSION_GUIDELINES.md        # Submission procedure and evaluator access instructions
├── requirements.txt                # Optional packages (Zero external required)
├── setup.py                        # Pip-installable setup script
└── .gitignore                      # Git ignore rules
```

---

## 🚀 Quickstart & Execution Instructions

### Prerequisites
* **Python 3.8 or higher** (Python 3.8 to 3.13 supported).
* **Zero required external dependencies:** The entire core system, CLI, GUI, and test suite run using Python's standard library.

### 1. Run the Automated Demo
To see all 5 features in action in under 30 seconds:
```bash
python scripts/demo.py
```

### 2. Run the Full Test Suite
To execute all 17 automated unit and integration tests:
```bash
python tests/run_tests.py
```

### 3. Using the Command-Line Interface (CLI)

#### A. Run eSim Doctor (Comprehensive Health Check)
```bash
python -m esim_tool_manager.cli doctor
```
*Scans your operating system, package managers, all 6 external EDA tools, and Python dependencies, producing a colorized diagnostic report.*

#### B. List Registered Tools & Status
```bash
python -m esim_tool_manager.cli list
```

#### C. Install Missing Tools
* **Dry-Run Mode (Preview commands without making changes):**
  ```bash
  python -m esim_tool_manager.cli install ngspice --dry-run
  ```
* **Install a specific tool:**
  ```bash
  python -m esim_tool_manager.cli install ngspice
  ```
* **Install all missing tools:**
  ```bash
  python -m esim_tool_manager.cli install all
  ```
* **Install missing Python dependencies:**
  ```bash
  python -m esim_tool_manager.cli install python
  ```

#### D. Check & Upgrade Tools
* **Check upstream releases:**
  ```bash
  python -m esim_tool_manager.cli check-updates
  ```
* **Upgrade all tools (with automated backup):**
  ```bash
  python -m esim_tool_manager.cli update all
  ```

#### E. Configure eSim Environment & Tool Paths
```bash
python -m esim_tool_manager.cli configure
```
*Generates `.esimrc`, `config.ini`, `setup_esim_env.bat` (Windows), `setup_esim_env.sh` (Linux/macOS), and persistent environment scripts.*

#### F. View Action Logs
```bash
python -m esim_tool_manager.cli logs --limit 20
```

#### G. Interactive Menu
Simply run the CLI without arguments to launch the interactive text menu:
```bash
python -m esim_tool_manager.cli
```

---

### 4. Using the Modern Graphical User Interface (GUI)

Launch the modern dark-themed GUI:
```bash
python -m esim_tool_manager.cli gui
# OR
python -m esim_tool_manager.gui
```

#### GUI Capabilities:
* **External Tools Tab:** Displays real-time table of tools, installed vs. recommended versions, and colorized status tags (`OK`, `MISSING`, `OUTDATED`). Contains 1-click action buttons for Doctor, Install, Update, and Configure.
* **Python Dependencies Tab:** Displays table of Python modules (`matplotlib`, `numpy`, `scipy`, `PyQt5`, `ply`) with 1-click install/upgrade.
* **Settings & Environment Tab:** Interactive directory selector for custom tool installation locations and preferred package managers.
* **Action & Audit Logs Tab:** Live real-time streaming view of the audit log (`esim_actions.jsonl`).

---

## ⚙️ Configuration & Output Artifacts

When you run `configure`, the Tool Manager generates:

1. **`.esimrc`**: A structured JSON profile storing full tool paths.
2. **`config.ini`**: Standard INI configuration directly readable by eSim core.
3. **`setup_esim_env.bat` (Windows)** / **`setup_esim_env.sh` (Linux/macOS)**: Session setup scripts that set `NGSPICE_PATH`, `KICAD_PATH`, `GHDL_PATH`, `VERILATOR_PATH`, `MAKERCHIP_PATH`, and prepend tool directories to system `PATH`.
4. **`apply_persistent_env.ps1` / `apply_persistent_env.sh`**: Scripts to permanently register paths into user environment variables.

---

## 🧪 Test Suite Results

```text
======================================================================
 Running eSim Automated Tool Manager Test Suite
======================================================================
test_custom_tool_path (test_config.TestConfigurationManager) ... ok
test_default_values (test_config.TestConfigurationManager) ... ok
test_esim_profile_export (test_config.TestConfigurationManager) ... ok
test_set_and_get (test_config.TestConfigurationManager) ... ok
test_diagnostic_report_generation (test_dependency_checker.TestDependencyChecker) ... ok
test_manifest_loading (test_dependency_checker.TestDependencyChecker) ... ok
test_version_comparison (test_dependency_checker.TestDependencyChecker) ... ok
test_version_parsing (test_dependency_checker.TestDependencyChecker) ... ok
test_dry_run_install_tool (test_installer.TestToolInstaller) ... ok
test_dry_run_package_manager (test_installer.TestToolInstaller) ... ok
test_zip_extraction (test_installer.TestToolInstaller) ... ok
test_architecture (test_platform.TestPlatformDetector) ... ok
test_os_name_non_empty (test_platform.TestPlatformDetector) ... ok
test_os_type_detection (test_platform.TestPlatformDetector) ... ok
test_package_managers_detection (test_platform.TestPlatformDetector) ... ok
test_system_info_model (test_platform.TestPlatformDetector) ... ok
test_backup_and_rollback (test_updater.TestToolUpdater) ... ok

----------------------------------------------------------------------
Ran 17 tests in 0.786s

OK
======================================================================
Tests Run: 17 | Errors: 0 | Failures: 0
======================================================================
```

---

## 📬 Submission Information

* **Candidate Task:** Task 5 - Tool Manager (CSE and related fields)
* **Design Document:** [DESIGN_DOCUMENT.md](DESIGN_DOCUMENT.md)
* **Presentation Outline:** [PRESENTATION_OUTLINE.md](PRESENTATION_OUTLINE.md)
* **Submission Guide:** [SUBMISSION_GUIDELINES.md](SUBMISSION_GUIDELINES.md)
* **Evaluator Access:** GitHub ID [`Eyantra698Sumanto`](https://github.com/Eyantra698Sumanto)
* **Submission Email:** `contact-esim@fossee.in`
* **Subject Line:** `eSim Semester Long Internship - Autumn 2026 Submission Task 5`
