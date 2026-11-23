# Presentation & Video Demo Guide (5-10 Minutes)
**FOSSEE eSim Winter Internship - 2026 / Semester Long Internship (Autumn 2026)**  
**Screening Task 5: Tool Manager (CSE and related fields)**  
**Topic:** Automated Tool and Dependency Manager for eSim EDA  

---

## 1. Presentation Slide Outline

### Slide 1: Title Slide (Duration: 0:30)
* **Title:** Automated Tool & Dependency Management Suite for eSim
* **Subtitle:** Seamless EDA Toolchain Orchestration, Health Diagnostics, and Cross-Platform Integration
* **Presented by:** Candidate Name
* **Context:** FOSSEE eSim Winter Internship - 2026 (Task 5)

### Slide 2: Problem Statement & Motivation (Duration: 1:00)
* **What is eSim?** An open-source EDA suite integrating schematic capture, circuit simulation, and PCB design.
* **The Challenge:** eSim relies heavily on diverse third-party tools (Ngspice, KiCad, GHDL, Verilator, SandPiper, GCC, Python libraries).
* **Pain Points:**
  * Frequent dependency conflicts and missing executables.
  * Inconsistent PATH and environment variable setups across Windows and Linux.
  * Tedious manual installation and lack of automated version upgrades.
  * Difficulty distinguishing between circuit design bugs and toolchain configuration failures.

### Slide 3: Proposed Architecture & Key Modules (Duration: 1:30)
* **Layered Architecture:** Presentation Layer, Business Logic Layer, Core Services Layer, Data/Manifest Layer.
* **Extensible Schema:** `manifest.json` decouples tool definitions from code logic—adding future tools requires zero core code changes.
* **Core Modules:**
  * `dependency_checker.py`: "eSim Doctor" pre-flight diagnostic engine.
  * `installer.py`: Multi-backend installer (Package Managers + Direct Portable Downloads).
  * `updater.py`: Upstream release monitor with automatic backup and rollback.
  * `configurator.py`: Environment variable manager & `.esimrc` / `config.ini` profile exporter.
  * `cli.py` & `gui.py`: Dual-interface for high-productivity automation and visual control.

### Slide 4: Meeting All Task Requirements (Duration: 1:00)
* Highlight compliance table showing how all 5 task requirements (Installation, Updates, Configuration, Dependency Checker, UI) plus cross-platform package manager integrations are fulfilled and exceeded.
* Zero external required dependencies—built 100% on standard Python libraries.

### Slide 5: Live Demonstration (Duration: 4:00)
*(Follow the Live Demo Walkthrough below)*

### Slide 6: Testing & Quality Assurance (Duration: 1:00)
* 17 automated unit and integration tests passing with 100% success rate.
* Dry-run simulation mode for CI/CD environments.
* Structured action logging in both `.log` and machine-readable `.jsonl` audit trails.

### Slide 7: Conclusion & Future Scope (Duration: 0:30)
* Summary of benefits: Zero-friction onboarding for new eSim users, reproducible environments, reliable simulations.
* Future Scope: Integration into eSim's main GUI installer, cloud PDK downloading (e.g., SkyWater 130nm), and Docker/container synchronization.

---

## 2. Live Demo Walkthrough & Video Script

### Step 1: Introduction & Environment Check
* **Script:**  
  *"Hello everyone. In this presentation, I am demonstrating the Automated Tool Manager designed for FOSSEE eSim EDA, fulfilling Task 5 of the eSim Screening Tasks. Let's start by looking at our environment."*
* **Action:**  
  Run: `python -m esim_tool_manager.cli doctor`
* **Talking Points:**  
  *"Here we run our 'eSim Doctor' command. As you can see, the tool automatically detects the host operating system—in this case Windows 11 on x86_64—and discovers available package managers like winget and pip. It scans all 6 core external EDA tools and the 5 required Python scientific libraries, showing their installed versions, required minimum versions, and exact paths."*

### Step 2: Listing Tools & Status
* **Script:**  
  *"Next, we can list the tools and inspect their statuses."*
* **Action:**  
  Run: `python -m esim_tool_manager.cli list`
* **Talking Points:**  
  *"This table gives engineers an instant snapshot of what tools are missing, installed, or outdated."*

### Step 3: Automated Installation Simulation
* **Script:**  
  *"Now, let's see how our multi-backend installer operates. It supports unattended package manager installation via winget, choco, apt, dnf, or brew, as well as direct zero-privilege portable binary extraction."*
* **Action:**  
  Run: `python -m esim_tool_manager.cli install ngspice --dry-run`
* **Talking Points:**  
  *"With dry-run mode, we can verify that the tool manager correctly crafts the silent winget command with package agreement acceptance flags without modifying the host system during evaluation."*

### Step 4: Environment Profile Generation
* **Script:**  
  *"One of the most critical requirements is configuration handling and path management. Let's run the configure command."*
* **Action:**  
  Run: `python -m esim_tool_manager.cli configure`
* **Talking Points:**  
  *"In a single command, the tool manager exports the JSON .esimrc profile, the standard eSim config.ini, session launcher scripts for Windows (.bat) and Linux (.sh), and a persistent PowerShell script. This ensures eSim can immediately locate every tool binary without manual PATH editing."*

### Step 5: Modern Graphical User Interface (GUI)
* **Script:**  
  *"In addition to the powerful CLI, we also provide a full-featured, dark-themed GUI for desktop users."*
* **Action:**  
  Run: `python -m esim_tool_manager.gui`
* **Talking Points:**  
  *"The GUI features a responsive layout with tabs for External Tools, Python Dependencies, Settings & Paths, and live Action Logs. Users can execute diagnostics, install tools, and configure paths with single-click buttons without freezing the UI thanks to background threading."*

### Step 6: Test Suite & Audit Trail
* **Script:**  
  *"Finally, let's run our automated test suite and review the audit trail."*
* **Action:**  
  Run: `python tests/run_tests.py`  
  Run: `python -m esim_tool_manager.cli logs`
* **Talking Points:**  
  *"All 17 unit and integration tests pass with 0 errors and 0 failures. Every action is recorded with ISO timestamps in esim_actions.jsonl for complete auditability. Thank you!"*
