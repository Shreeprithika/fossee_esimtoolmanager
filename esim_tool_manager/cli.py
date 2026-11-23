"""
Command-Line Interface (CLI) for eSim Automated Tool Manager
Provides intuitive commands, colorized diagnostic reports, and interactive menus.
"""

import os
import sys
import argparse
from typing import Optional

from esim_tool_manager.core.logger import logger, auditor
from esim_tool_manager.core.config import config_manager
from esim_tool_manager.core.models import StatusEnum
from esim_tool_manager.core.platform_detect import PlatformDetector
from esim_tool_manager.modules.dependency_checker import DependencyChecker
from esim_tool_manager.modules.installer import ToolInstaller
from esim_tool_manager.modules.updater import ToolUpdater
from esim_tool_manager.modules.configurator import ToolConfigurator

BANNER = r"""
========================================================================
     ___ ____  _           _____           _   __  __                                   
    / _ \ ___|(_)_ __ ___ |_   _|__   ___ | | |  \/  | __ _ _ __   __ _  __ _  ___ _ __ 
   / /_\ \___ \| | '_ ` _ \ | |/ _ \ / _ \| | | |\/| |/ _` | '_ \ / _` |/ _` |/ _ \ '__|
  / /_\\ \___) | | | | | | || | (_) | (_) | | | |  | | (_| | | | | (_| | (_| |  __/ |   
  \____/|____/ |_|_| |_| |_||_|\___/ \___/|_| |_|  |_|\__,_|_| |_|\__,_|\__, |\___|_|   
                                                                         |___/          
           FOSSEE eSim Automated Tool & Dependency Management Suite
========================================================================
"""

# Terminal Colors
class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    END = "\033[0m"

    @classmethod
    def wrap(cls, text: str, color: str) -> str:
        if sys.stdout.isatty():
            return f"{color}{text}{cls.END}"
        return text


def format_status_badge(status: StatusEnum) -> str:
    if status == StatusEnum.OK:
        return Colors.wrap("[  OK  ]", Colors.GREEN)
    elif status in (StatusEnum.OUTDATED, StatusEnum.WARNING):
        return Colors.wrap("[ WARN ]", Colors.YELLOW)
    else:
        return Colors.wrap("[ FAIL ]", Colors.RED)


def cmd_doctor(args):
    """Executes full eSim health check."""
    print(BANNER)
    print(Colors.wrap("==> Running eSim System & Dependency Diagnostic (Doctor)...", Colors.CYAN + Colors.BOLD))
    
    checker = DependencyChecker()
    report = checker.run_full_diagnostic()
    plat = report.platform_info

    print(f"\n{Colors.wrap('1. System Environment:', Colors.BOLD)}")
    print(f"  * Host OS:          {plat.os_name} ({plat.os_type})")
    print(f"  * Architecture:     {plat.architecture}")
    print(f"  * Python Version:   {plat.python_version}")
    print(f"  * Admin/Root:       {'Yes' if plat.is_admin else 'No'}")
    print(f"  * Package Managers: {', '.join(plat.available_package_managers) or 'None detected'}")
    print(f"  * Tool Install Dir: {config_manager.get('install_dir')}")

    print(f"\n{Colors.wrap('2. Core EDA Tools Status:', Colors.BOLD)}")
    print(f"  {'Status':<10} {'Tool Name':<25} {'Installed':<15} {'Required':<10} {'Path'}")
    print("  " + "-" * 80)
    for key, t in report.tools.items():
        badge = format_status_badge(t.status)
        installed_v = t.version or "None"
        req_v = f">={t.min_version}"
        path_str = t.binary_path or "Not found"
        print(f"  {badge} {t.name:<25} {installed_v:<15} {req_v:<10} {path_str}")

    print(f"\n{Colors.wrap('3. Python Scientific Stack:', Colors.BOLD)}")
    print(f"  {'Status':<10} {'Package':<20} {'Version':<15} {'Required':<10} {'Purpose'}")
    print("  " + "-" * 80)
    for key, d in report.dependencies.items():
        badge = format_status_badge(d.status)
        v_str = d.installed_version or "Missing"
        req_v = f">={d.min_version}"
        print(f"  {badge} {d.name:<20} {v_str:<15} {req_v:<10} {d.purpose}")

    print(f"\n{Colors.wrap('4. Diagnostic Summary:', Colors.BOLD)}")
    s = report.summary
    print(f"  * Total Checked: {s['total']}")
    print(f"  * Passed:        {Colors.wrap(str(s['passed']), Colors.GREEN)}")
    print(f"  * Warnings:      {Colors.wrap(str(s['warnings']), Colors.YELLOW)}")
    print(f"  * Failed:        {Colors.wrap(str(s['failed']), Colors.RED)}")

    if s["healthy"]:
        print(f"\n{Colors.wrap('>> [PASSED] System is 100% ready for eSim circuit simulations!', Colors.GREEN + Colors.BOLD)}")
    else:
        print(f"\n{Colors.wrap('>> [ACTION REQUIRED] Run `esim-tools install all` to automatically install missing tools.', Colors.YELLOW + Colors.BOLD)}")


def cmd_list(args):
    """Lists external tools with detailed versioning and update statuses."""
    checker = DependencyChecker()
    report = checker.run_full_diagnostic()

    print(BANNER)
    print(Colors.wrap("Registered External Tools & Status:", Colors.CYAN + Colors.BOLD))
    print(f"  {'Tool Key':<12} {'Tool Name':<25} {'Installed':<12} {'Recommended':<12} {'Status'}")
    print("  " + "=" * 75)
    for key, t in report.tools.items():
        v = t.version or "None"
        badge = format_status_badge(t.status)
        print(f"  {key:<12} {t.name:<25} {v:<12} {t.recommended_version:<12} {badge} {t.status_message}")


def cmd_install(args):
    """Installs one or all missing tools."""
    target = args.tool.lower()
    dry_run = args.dry_run
    method = args.method

    installer = ToolInstaller()
    print(BANNER)
    if target == "all":
        print(Colors.wrap("==> Installing all missing tools and dependencies...", Colors.CYAN + Colors.BOLD))
        res = installer.install_all_missing(dry_run=dry_run)
        installer.install_python_dependencies(dry_run=dry_run)
        print("\nInstallation Summary:")
        for k, ok in res.items():
            status_text = Colors.wrap("SUCCESS", Colors.GREEN) if ok else Colors.wrap("FAILED", Colors.RED)
            print(f"  * {k}: {status_text}")
    elif target == "python":
        print(Colors.wrap("==> Installing missing Python dependencies...", Colors.CYAN + Colors.BOLD))
        installer.install_python_dependencies(dry_run=dry_run)
    else:
        print(Colors.wrap(f"==> Installing tool: {target}...", Colors.CYAN + Colors.BOLD))
        ok = installer.install_tool(target, method=method, dry_run=dry_run)
        if ok:
            print(Colors.wrap(f"\n[SUCCESS] Successfully installed {target}!", Colors.GREEN + Colors.BOLD))
        else:
            print(Colors.wrap(f"\n[ERROR] Failed to install {target}. See log file for details.", Colors.RED + Colors.BOLD))


def cmd_update(args):
    """Updates external tools to their latest upstream releases."""
    target = args.tool.lower()
    dry_run = args.dry_run

    updater = ToolUpdater()
    print(BANNER)
    if target == "all":
        print(Colors.wrap("==> Checking and updating all external tools...", Colors.CYAN + Colors.BOLD))
        results = updater.upgrade_all(dry_run=dry_run)
        for k, ok in results.items():
            status_text = Colors.wrap("UP TO DATE / SUCCESS", Colors.GREEN) if ok else Colors.wrap("FAILED", Colors.RED)
            print(f"  * {k}: {status_text}")
    else:
        print(Colors.wrap(f"==> Updating tool: {target}...", Colors.CYAN + Colors.BOLD))
        ok = updater.upgrade_tool(target, dry_run=dry_run)
        if ok:
            print(Colors.wrap(f"\n[SUCCESS] {target} updated successfully!", Colors.GREEN + Colors.BOLD))
        else:
            print(Colors.wrap(f"\n[ERROR] Failed to update {target}.", Colors.RED + Colors.BOLD))


def cmd_check_updates(args):
    """Checks remote repositories for newer versions."""
    updater = ToolUpdater()
    print(BANNER)
    print(Colors.wrap("==> Checking upstream releases for external tools...", Colors.CYAN + Colors.BOLD))
    tools_cfg = updater.manifest.get("tools", {})
    for key in tools_cfg:
        has_update, curr, latest = updater.check_for_updates(key)
        curr_str = curr or "Not installed"
        latest_str = latest or "N/A"
        if has_update:
            msg = Colors.wrap(f"UPDATE AVAILABLE ({curr_str} -> {latest_str})", Colors.YELLOW)
        else:
            msg = Colors.wrap(f"Up to date ({curr_str})", Colors.GREEN)
        print(f"  * {key:<12}: {msg}")


def cmd_configure(args):
    """Configures tool paths, exports .esimrc, config.ini, and environment scripts."""
    configurator = ToolConfigurator()
    print(BANNER)
    print(Colors.wrap("==> Configuring eSim environment and path exports...", Colors.CYAN + Colors.BOLD))
    result = configurator.configure_environment(output_dir=args.output)
    print("\nConfigured Tool Paths:")
    for tool, p in result["configured_tools"].items():
        print(f"  * {tool.upper()}_PATH = {p}")

    print("\nExported Configuration Files:")
    for ftype, fpath in result["exported_files"].items():
        print(f"  * {ftype:<16}: {fpath}")

    # Generate persistent system script
    persistent_script = configurator.generate_persistent_system_script()
    print(f"  * Persistent script: {persistent_script}")
    print(Colors.wrap("\n[SUCCESS] eSim configuration files successfully generated!", Colors.GREEN + Colors.BOLD))


def cmd_logs(args):
    """Displays action audit logs."""
    entries = auditor.get_recent_actions(limit=args.limit)
    print(BANNER)
    print(Colors.wrap(f"==> Recent Action Audit Logs (Last {args.limit} events):", Colors.CYAN + Colors.BOLD))
    if not entries:
        print("  No recent actions recorded yet.")
        return

    print(f"  {'Timestamp':<25} {'Action':<20} {'Tool':<12} {'Status':<10} {'Details'}")
    print("  " + "-" * 85)
    for e in entries:
        print(f"  {e.get('timestamp',''):<25} {e.get('action',''):<20} {e.get('tool',''):<12} {e.get('status',''):<10} {e.get('details','')[:30]}")


def cmd_gui(args):
    """Launches modern Graphical User Interface."""
    try:
        from esim_tool_manager.gui import launch_gui
        launch_gui()
    except Exception as e:
        logger.error(f"Failed to launch GUI: {e}")
        print(f"Error launching GUI: {e}")


def interactive_menu():
    """Interactive text menu for user-friendly navigation when run without args."""
    while True:
        print(BANNER)
        print("Please choose an operation:")
        print("  1. Run eSim Doctor (Diagnostic Check)")
        print("  2. List All Tools & Status")
        print("  3. Install Missing Tools")
        print("  4. Check for Upstream Updates")
        print("  5. Update Tools")
        print("  6. Configure Environment & Paths (Generate config.ini / .esimrc)")
        print("  7. View Action Logs")
        print("  8. Launch Graphical User Interface (GUI)")
        print("  0. Exit")
        choice = input("\nEnter choice [0-8]: ").strip()

        class DummyArgs:
            def __init__(self, **kwargs):
                self.__dict__.update(kwargs)

        if choice == "1":
            cmd_doctor(DummyArgs())
        elif choice == "2":
            cmd_list(DummyArgs())
        elif choice == "3":
            tool_choice = input("Enter tool key to install (or 'all' / 'python'): ").strip() or "all"
            cmd_install(DummyArgs(tool=tool_choice, dry_run=False, method=None))
        elif choice == "4":
            cmd_check_updates(DummyArgs())
        elif choice == "5":
            tool_choice = input("Enter tool key to update (or 'all'): ").strip() or "all"
            cmd_update(DummyArgs(tool=tool_choice, dry_run=False))
        elif choice == "6":
            cmd_configure(DummyArgs(output=None))
        elif choice == "7":
            cmd_logs(DummyArgs(limit=25))
        elif choice == "8":
            cmd_gui(DummyArgs())
        elif choice == "0":
            print("Exiting eSim Tool Manager. Goodbye!")
            break
        else:
            print("Invalid choice, please select again.")
        input("\nPress Enter to return to menu...")


def main():
    parser = argparse.ArgumentParser(
        description="FOSSEE eSim Automated Tool & Dependency Management Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # doctor
    p_doctor = subparsers.add_parser("doctor", help="Run comprehensive eSim environment diagnostic")
    p_doctor.set_defaults(func=cmd_doctor)

    # list
    p_list = subparsers.add_parser("list", help="List registered tools and status")
    p_list.set_defaults(func=cmd_list)

    # install
    p_install = subparsers.add_parser("install", help="Install external tools or dependencies")
    p_install.add_argument("tool", nargs="?", default="all", help="Tool to install (e.g. ngspice, kicad, all, python)")
    p_install.add_argument("--dry-run", action="store_true", help="Simulate installation without executing changes")
    p_install.add_argument("--method", choices=["auto", "winget", "choco", "apt", "direct", "pip"], default="auto", help="Installation backend method")
    p_install.set_defaults(func=cmd_install)

    # update
    p_update = subparsers.add_parser("update", help="Update tools to latest version")
    p_update.add_argument("tool", nargs="?", default="all", help="Tool to update (or 'all')")
    p_update.add_argument("--dry-run", action="store_true", help="Simulate upgrade")
    p_update.set_defaults(func=cmd_update)

    # check-updates
    p_check = subparsers.add_parser("check-updates", help="Check for upstream updates")
    p_check.set_defaults(func=cmd_check_updates)

    # configure
    p_config = subparsers.add_parser("configure", help="Auto-configure tool paths and export .esimrc and config.ini")
    p_config.add_argument("-o", "--output", default=None, help="Directory to save exported config files")
    p_config.set_defaults(func=cmd_configure)

    # logs
    p_logs = subparsers.add_parser("logs", help="Display recent action logs and audit history")
    p_logs.add_argument("-n", "--limit", type=int, default=30, help="Number of records to display")
    p_logs.set_defaults(func=cmd_logs)

    # gui
    p_gui = subparsers.add_parser("gui", help="Launch Graphical User Interface")
    p_gui.set_defaults(func=cmd_gui)

    if len(sys.argv) == 1:
        interactive_menu()
    else:
        args = parser.parse_args()
        if hasattr(args, "func"):
            args.func(args)
        else:
            parser.print_help()


if __name__ == "__main__":
    main()
