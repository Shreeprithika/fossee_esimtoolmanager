# eSim Automated Tool Manager (eSim-ATM)

[![Python Version](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-green.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()
[![Tests](https://img.shields.io/badge/tests-17%20passed%2C%200%20failed-brightgreen.svg)]()
[![Video](https://img.shields.io/badge/demo-1080p%20MP4%20included-red.svg)](esim_tool_manager_demo.mp4)
[![Task](https://img.shields.io/badge/eSim%20Internship-Task%205%3A%20Tool%20Manager-orange.svg)]()

> **FOSSEE eSim Winter Internship - 2026 / Semester Long Internship (Autumn 2026)**  
> **Screening Task 5: Tool Manager (CSE and related fields)**  
> **Candidate:** Shreeprithika  
> **Repository:** [https://github.com/Shreeprithika/fossee_esimtoolmanager](https://github.com/Shreeprithika/fossee_esimtoolmanager)

The **eSim Automated Tool Manager** is an automated cross-platform tool and dependency management suite for [FOSSEE eSim EDA](https://esim.fossee.in/). It automates the discovery, installation, configuration, health verification, and updating of external tools and libraries required for circuit simulation and PCB design.

---

## 🎬 Execution Video & Interactive Demo

A Full HD (1080p) execution video demonstrating all features and evaluation criteria has been compiled and included directly in this repository:

* 📥 **Direct Video File:** [**`esim_tool_manager_demo.mp4`**](esim_tool_manager_demo.mp4) *(1.16 MB, Full HD 1080p H.264)*
* 🌐 **Interactive Web Player:** [**`demo_video_player.html`**](demo_video_player.html) *(Open in any browser to watch with chapter navigation)*

```html
<video src="esim_tool_manager_demo.mp4" controls="controls" width="100%" style="max-width: 900px; border-radius: 8px;">
  Your browser does not support the video tag. Download esim_tool_manager_demo.mp4 to view.
</video>
```

### Video Timeline & Chapters:
* **0:00 - 0:04** • Title Card & Candidate Submission Details (Shreeprithika)
* **0:04 - 0:13** • Feature 1 & 4: System Health Check & Diagnostic (`esim-tools doctor`)
* **0:13 - 0:21** • Feature 1 & 2: Automated Multi-Backend Installation & Upstream Update Tracking
* **0:21 - 0:29** • Feature 3: Configuration Handling & eSim Environment Profile Exports
* **0:29 - 0:34** • Feature 5: Modern Graphical User Interface (GUI - Tkinter & TTK)
* **0:34 - 0:40** • Quality Assurance: Automated Test Suite (17 tests, 100% passing)
* **0:40 - 0:44** • Conclusion & Evaluator Access Details (`Eyantra698Sumanto`)

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
│   └── run_tests.py                # Master test runner (17 tests, 100% passing)
├── scripts/                        # Utility, demonstration, and video scripts
│   ├── demo.py                     # 30-second automated end-to-end showcase
│   ├── generate_video.py           # Re-renders the 1080p MP4 execution video
│   └── export_report_html.py       # Converts design doc to styled HTML for PDF export
├── esim_tool_manager_demo.mp4      # Full HD 1080p Execution Showcase Video
├── demo_video_player.html          # Interactive HTML5 Video Player
├── DESIGN_DOCUMENT.md              # Complete Architectural Design Document
├── PRESENTATION_OUTLINE.md         # Video demo script and slide deck outline
├── SUBMISSION_GUIDELINES.md        # Submission procedure and evaluator access instructions
├── requirements.txt                # Optional packages (Zero external required)
├── setup.py                        # Pip-installable setup script
└── .gitignore                      # Git ignore rules
```

---

## 🛠️ Step-by-Step Compilation & Execution Commands

Follow these commented terminal commands to compile, test, run, and explore the project:

### 1. Clone & Set Up Workspace
```bash
# Clone the repository
git clone https://github.com/Shreeprithika/fossee_esimtoolmanager.git

# Enter project directory
cd fossee_esimtoolmanager
```

### 2. Compile & Install the Package
The core system uses 100% Python Standard Library. To register the commands globally:
```bash
# Compile and install in editable development mode (creates 'esim-tools' command)
python -m pip install -e .
```

---

### 3. Run the Automated Demo (30 Seconds)
```bash
# Executes a complete end-to-end demonstration across all 5 features
python scripts/demo.py
```

---

### 4. Run the Full Test Suite
```bash
# Executes all 17 automated unit and integration tests (zero failures)
python tests/run_tests.py
```

---

### 5. Command-Line Interface (CLI) Usage

#### A. Run Health Diagnostic ("eSim Doctor")
```bash
# Scans system OS, architecture, package managers, 6 EDA tools, and 5 Python libraries
python -m esim_tool_manager.cli doctor
```

#### B. List Registered Tools & Status
```bash
# Displays table of tools, installed versions, required versions, and status
python -m esim_tool_manager.cli list
```

#### C. Install External Tools
```bash
# Dry-run installation of Ngspice (simulates command without altering system)
python -m esim_tool_manager.cli install ngspice --dry-run

# Automatically install all missing tools
python -m esim_tool_manager.cli install all

# Install missing Python scientific dependencies
python -m esim_tool_manager.cli install python
```

#### D. Check Upstream Updates & Upgrade
```bash
# Probes GitHub Releases API and PyPI API for newer tool versions
python -m esim_tool_manager.cli check-updates

# Upgrade all tools with automatic backup and rollback on failure
python -m esim_tool_manager.cli update all
```

#### E. Configure eSim Environment & Tool Paths
```bash
# Auto-detects tool paths, generates .esimrc, config.ini, setup_esim_env.bat, and setup_esim_env.sh
python -m esim_tool_manager.cli configure
```

#### F. View Action & Audit Logs
```bash
# Displays the most recent 20 audit events recorded in esim_actions.jsonl
python -m esim_tool_manager.cli logs --limit 20
```

#### G. Interactive Menu
```bash
# Launches the interactive numeric terminal menu
python -m esim_tool_manager.cli
```

---

### 6. Modern Graphical User Interface (GUI) Usage
```bash
# Launch the modern dark-themed desktop GUI (Tkinter/TTK)
python -m esim_tool_manager.gui
# OR
python -m esim_tool_manager.cli gui
```

#### GUI Tabs & Features:
* **External Tools:** Displays real-time table of tools, installed vs. recommended versions, and colorized status tags (`OK`, `MISSING`, `OUTDATED`). Contains 1-click action buttons for Doctor, Install, Update, and Configure.
* **Python Dependencies:** Displays table of Python modules (`matplotlib`, `numpy`, `scipy`, `PyQt5`, `ply`) with 1-click install/upgrade.
* **Settings & Environment:** Interactive directory selector for custom tool installation locations and preferred package managers.
* **Action & Audit Logs:** Live real-time streaming view of the audit log (`esim_actions.jsonl`).

---

### 7. Re-Compiling the Execution Video & Reports

#### Re-render the 1080p MP4 Video:
```bash
# Requires imageio, imageio-ffmpeg, and pillow
python scripts/generate_video.py
```

#### Export Printable HTML/PDF Design Document:
```bash
# Generates eSim_Task5_Design_Document.html for browser viewing or PDF printing
python scripts/export_report_html.py
```

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
Ran 17 tests in 0.889s

OK
======================================================================
Tests Run: 17 | Errors: 0 | Failures: 0 | STATUS: 100% PASS
======================================================================
```

---

## 📬 Official Submission Information

* **Candidate Name:** Shreeprithika
* **Selected Task:** Task 5 - Tool Manager (CSE and related fields)
* **GitHub Repository:** [https://github.com/Shreeprithika/fossee_esimtoolmanager](https://github.com/Shreeprithika/fossee_esimtoolmanager)
* **Evaluator Access:** Granted to GitHub ID [`Eyantra698Sumanto`](https://github.com/Eyantra698Sumanto)
* **Design Document:** [DESIGN_DOCUMENT.md](DESIGN_DOCUMENT.md)
* **Demo Video:** [esim_tool_manager_demo.mp4](esim_tool_manager_demo.mp4)
* **Interactive Player:** [demo_video_player.html](demo_video_player.html)
* **Submission Guide:** [SUBMISSION_GUIDELINES.md](SUBMISSION_GUIDELINES.md)
* **Submission Email:** `contact-esim@fossee.in`
* **Subject Line:** `eSim Semester Long Internship - Autumn 2026 Submission Task 5`
