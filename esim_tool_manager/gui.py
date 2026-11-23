"""
Modern Graphical User Interface (GUI) for eSim Automated Tool Manager
Built using Tkinter & TTK with a modern responsive theme and non-blocking background workers.
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Dict, Any

from esim_tool_manager.core.logger import logger, auditor
from esim_tool_manager.core.config import config_manager
from esim_tool_manager.core.models import StatusEnum
from esim_tool_manager.core.platform_detect import PlatformDetector
from esim_tool_manager.modules.dependency_checker import DependencyChecker
from esim_tool_manager.modules.installer import ToolInstaller
from esim_tool_manager.modules.updater import ToolUpdater
from esim_tool_manager.modules.configurator import ToolConfigurator


class ToolManagerApp(tk.Tk):
    """Main window application for eSim Tool Manager."""

    def __init__(self):
        super().__init__()
        self.title("eSim Automated Tool & Dependency Manager - FOSSEE")
        self.geometry("960x680")
        self.minsize(850, 550)

        # Initialize engines
        self.checker = DependencyChecker()
        self.installer = ToolInstaller()
        self.updater = ToolUpdater()
        self.configurator = ToolConfigurator()
        self.plat_info = PlatformDetector.get_system_info()

        # Apply styling
        self._setup_styles()

        # Build UI layout
        self._build_header()
        self._build_notebook()
        self._build_statusbar()

        # Load initial diagnostic in background
        self.after(200, self.refresh_diagnostic_async)

    def _setup_styles(self):
        self.configure(bg="#1e1e2e")
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        # Color palette
        bg_dark = "#1e1e2e"
        card_bg = "#252538"
        text_light = "#cdd6f4"
        accent_blue = "#89b4fa"

        style.configure(".", background=bg_dark, foreground=text_light, font=("Segoe UI", 10))
        style.configure("TFrame", background=bg_dark)
        style.configure("Card.TFrame", background=card_bg, relief="flat")
        
        style.configure("TLabel", background=bg_dark, foreground=text_light, font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground=accent_blue)
        style.configure("SubHeader.TLabel", font=("Segoe UI", 10), foreground="#a6adc8")
        style.configure("CardTitle.TLabel", background=card_bg, font=("Segoe UI", 12, "bold"), foreground="#cdd6f4")
        style.configure("Status.TLabel", background="#181825", font=("Segoe UI", 9), foreground="#a6adc8")

        # Treeview styling
        style.configure("Treeview",
                        background=card_bg,
                        foreground=text_light,
                        fieldbackground=card_bg,
                        rowheight=28,
                        font=("Segoe UI", 10))
        style.map("Treeview", background=[("selected", "#45475a")])
        style.configure("Treeview.Heading",
                        background="#313244",
                        foreground=accent_blue,
                        font=("Segoe UI", 10, "bold"))

        # Buttons
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), padding=6)
        style.configure("TButton", font=("Segoe UI", 9), padding=5)

    def _build_header(self):
        header_frame = ttk.Frame(self, padding=(20, 15, 20, 10))
        header_frame.pack(fill=tk.X)

        title_lbl = ttk.Label(header_frame, text="eSim Automated Tool Manager", style="Header.TLabel")
        title_lbl.pack(anchor=tk.W)

        sub_text = (
            f"FOSSEE eSim EDA Suite | OS: {self.plat_info.os_name} ({self.plat_info.architecture}) "
            f"| Python: {self.plat_info.python_version} | Package Managers: {', '.join(self.plat_info.available_package_managers) or 'None'}"
        )
        sub_lbl = ttk.Label(header_frame, text=sub_text, style="SubHeader.TLabel")
        sub_lbl.pack(anchor=tk.W, pady=(2, 0))

    def _build_notebook(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=(5, 10))

        # Tab 1: Tools
        self.tab_tools = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_tools, text="  External Tools  ")
        self._init_tab_tools()

        # Tab 2: Python Stack
        self.tab_python = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_python, text="  Python Dependencies  ")
        self._init_tab_python()

        # Tab 3: Settings & Paths
        self.tab_settings = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_settings, text="  Settings & Environment  ")
        self._init_tab_settings()

        # Tab 4: Logs
        self.tab_logs = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_logs, text="  Action & Audit Logs  ")
        self._init_tab_logs()

    def _init_tab_tools(self):
        # Action Toolbar
        btn_bar = ttk.Frame(self.tab_tools)
        btn_bar.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(btn_bar, text="🩺 Run Doctor", command=self.refresh_diagnostic_async).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_bar, text="⬇ Install Selected", command=self.install_selected_tool).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_bar, text="⚡ Install Missing", command=self.install_all_missing_async).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_bar, text="🔄 Check Updates", command=self.check_updates_async).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_bar, text="⬆ Update Selected", command=self.update_selected_tool).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_bar, text="⚙ Configure eSim Paths", command=self.configure_paths).pack(side=tk.LEFT, padx=3)

        # Tools Treeview
        columns = ("key", "name", "status", "version", "rec_version", "path")
        self.tree_tools = ttk.Treeview(self.tab_tools, columns=columns, show="headings", selectmode="browse")
        self.tree_tools.heading("key", text="Tool Key")
        self.tree_tools.heading("name", text="Tool Name")
        self.tree_tools.heading("status", text="Status")
        self.tree_tools.heading("version", text="Installed")
        self.tree_tools.heading("rec_version", text="Recommended")
        self.tree_tools.heading("path", text="Executable Path")

        self.tree_tools.column("key", width=80, anchor=tk.W)
        self.tree_tools.column("name", width=180, anchor=tk.W)
        self.tree_tools.column("status", width=110, anchor=tk.CENTER)
        self.tree_tools.column("version", width=100, anchor=tk.CENTER)
        self.tree_tools.column("rec_version", width=100, anchor=tk.CENTER)
        self.tree_tools.column("path", width=330, anchor=tk.W)

        self.tree_tools.tag_configure("ok", foreground="#a6e3a1")
        self.tree_tools.tag_configure("warn", foreground="#f9e2af")
        self.tree_tools.tag_configure("fail", foreground="#f38ba8")

        scroll = ttk.Scrollbar(self.tab_tools, orient=tk.VERTICAL, command=self.tree_tools.yview)
        self.tree_tools.configure(yscrollcommand=scroll.set)
        self.tree_tools.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def _init_tab_python(self):
        btn_bar = ttk.Frame(self.tab_python)
        btn_bar.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(btn_bar, text="🔄 Rescan Python Stack", command=self.refresh_diagnostic_async).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_bar, text="⬇ Install / Upgrade Dependencies", command=self.install_python_deps_async).pack(side=tk.LEFT, padx=3)

        columns = ("pkg", "status", "installed", "min_ver", "purpose")
        self.tree_python = ttk.Treeview(self.tab_python, columns=columns, show="headings")
        self.tree_python.heading("pkg", text="Package")
        self.tree_python.heading("status", text="Status")
        self.tree_python.heading("installed", text="Installed Version")
        self.tree_python.heading("min_ver", text="Minimum Required")
        self.tree_python.heading("purpose", text="eSim Purpose")

        self.tree_python.column("pkg", width=120, anchor=tk.W)
        self.tree_python.column("status", width=90, anchor=tk.CENTER)
        self.tree_python.column("installed", width=110, anchor=tk.CENTER)
        self.tree_python.column("min_ver", width=110, anchor=tk.CENTER)
        self.tree_python.column("purpose", width=450, anchor=tk.W)

        self.tree_python.tag_configure("ok", foreground="#a6e3a1")
        self.tree_python.tag_configure("fail", foreground="#f38ba8")

        scroll = ttk.Scrollbar(self.tab_python, orient=tk.VERTICAL, command=self.tree_python.yview)
        self.tree_python.configure(yscrollcommand=scroll.set)
        self.tree_python.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def _init_tab_settings(self):
        frame = ttk.Frame(self.tab_settings, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)

        # Install Dir
        ttk.Label(frame, text="Tool Installation Base Directory:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.var_install_dir = tk.StringVar(value=config_manager.get("install_dir", ""))
        e_dir = ttk.Entry(frame, textvariable=self.var_install_dir, width=50)
        e_dir.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Button(frame, text="Browse...", command=self._browse_install_dir).grid(row=0, column=2, padx=5)

        # Preferred Package Manager
        ttk.Label(frame, text="Preferred Installation Backend:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.var_pm = tk.StringVar(value=config_manager.get("preferred_package_manager", "auto"))
        pm_box = ttk.Combobox(frame, textvariable=self.var_pm, values=["auto", "winget", "choco", "apt", "direct", "pip"], state="readonly")
        pm_box.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        # Auto Backup
        self.var_backup = tk.BooleanVar(value=config_manager.get("auto_backup", True))
        chk_backup = ttk.Checkbutton(frame, text="Enable automatic tool backup before upgrades", variable=self.var_backup)
        chk_backup.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=8)

        # Save Settings
        ttk.Button(frame, text="💾 Save Preferences", command=self._save_settings).grid(row=3, column=0, pady=15, sticky=tk.W)

    def _init_tab_logs(self):
        bar = ttk.Frame(self.tab_logs)
        bar.pack(fill=tk.X, pady=(0, 5))
        ttk.Button(bar, text="🔄 Refresh Logs", command=self._refresh_logs).pack(side=tk.LEFT, padx=3)
        ttk.Button(bar, text="🗑 Clear Logs View", command=lambda: self.txt_logs.delete("1.0", tk.END)).pack(side=tk.LEFT, padx=3)

        self.txt_logs = tk.Text(self.tab_logs, bg="#11111b", fg="#cdd6f4", font=("Consolas", 9), relief="flat")
        scroll = ttk.Scrollbar(self.tab_logs, orient=tk.VERTICAL, command=self.txt_logs.yview)
        self.txt_logs.configure(yscrollcommand=scroll.set)
        self.txt_logs.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self._refresh_logs()

    def _build_statusbar(self):
        status_frame = ttk.Frame(self, padding=(10, 5))
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.lbl_status = ttk.Label(status_frame, text="Ready", style="Status.TLabel")
        self.lbl_status.pack(side=tk.LEFT)

        self.prog_bar = ttk.Progressbar(status_frame, mode="indeterminate", length=180)
        self.prog_bar.pack(side=tk.RIGHT)

    def set_busy(self, is_busy: bool, message: str = ""):
        self.lbl_status.config(text=message or ("Working..." if is_busy else "Ready"))
        if is_busy:
            self.prog_bar.start(10)
        else:
            self.prog_bar.stop()

    def _browse_install_dir(self):
        d = filedialog.askdirectory(initialdir=self.var_install_dir.get())
        if d:
            self.var_install_dir.set(d)

    def _save_settings(self):
        config_manager.set("install_dir", self.var_install_dir.get())
        config_manager.set("preferred_package_manager", self.var_pm.get())
        config_manager.set("auto_backup", self.var_backup.get())
        messagebox.showinfo("Settings", "Preferences saved successfully!")

    def _refresh_logs(self):
        self.txt_logs.delete("1.0", tk.END)
        entries = auditor.get_recent_actions(limit=50)
        for e in entries:
            line = f"[{e.get('timestamp','')}] {e.get('action',''):<18} | {e.get('tool',''):<10} | {e.get('status',''):<10} | {e.get('details','')}\n"
            self.txt_logs.insert(tk.END, line)
        self.txt_logs.see(tk.END)

    def refresh_diagnostic_async(self):
        self.set_busy(True, "Running eSim Doctor Diagnostic...")

        def worker():
            rep = self.checker.run_full_diagnostic()
            self.after(0, lambda: self._apply_diagnostic_report(rep))

        threading.Thread(target=worker, daemon=True).start()

    def _apply_diagnostic_report(self, report):
        self.tree_tools.delete(*self.tree_tools.get_children())
        for key, t in report.tools.items():
            status_text = "OK" if t.status == StatusEnum.OK else ("OUTDATED" if t.status == StatusEnum.OUTDATED else "MISSING")
            tag = "ok" if t.status == StatusEnum.OK else ("warn" if t.status == StatusEnum.OUTDATED else "fail")
            self.tree_tools.insert("", tk.END, values=(
                key,
                t.name,
                status_text,
                t.version or "None",
                t.recommended_version,
                t.binary_path or "Not found"
            ), tags=(tag,))

        self.tree_python.delete(*self.tree_python.get_children())
        for key, d in report.dependencies.items():
            tag = "ok" if d.status == StatusEnum.OK else "fail"
            self.tree_python.insert("", tk.END, values=(
                d.name,
                "OK" if d.installed else "MISSING",
                d.installed_version or "None",
                f">={d.min_version}",
                d.purpose
            ), tags=(tag,))

        s = report.summary
        msg = f"Diagnostic Complete | Passed: {s['passed']} | Warnings: {s['warnings']} | Failed: {s['failed']}"
        self.set_busy(False, msg)
        self._refresh_logs()

    def install_selected_tool(self):
        sel = self.tree_tools.selection()
        if not sel:
            messagebox.showwarning("Selection", "Please select a tool from the list first.")
            return
        item = self.tree_tools.item(sel[0])
        tool_key = item["values"][0]

        self.set_busy(True, f"Installing {tool_key}...")
        def worker():
            ok = self.installer.install_tool(tool_key)
            self.after(0, lambda: self._on_install_finish(tool_key, ok))

        threading.Thread(target=worker, daemon=True).start()

    def _on_install_finish(self, tool_key: str, ok: bool):
        self.set_busy(False, f"Installation of {tool_key} finished.")
        if ok:
            messagebox.showinfo("Success", f"{tool_key} installed successfully!")
        else:
            messagebox.showerror("Error", f"Failed to install {tool_key}. Check logs for details.")
        self.refresh_diagnostic_async()

    def install_all_missing_async(self):
        self.set_busy(True, "Installing all missing tools...")
        def worker():
            res = self.installer.install_all_missing()
            self.installer.install_python_dependencies()
            self.after(0, lambda: self._on_install_all_finish(res))

        threading.Thread(target=worker, daemon=True).start()

    def _on_install_all_finish(self, res: Dict[str, bool]):
        self.set_busy(False, "Installation batch completed.")
        messagebox.showinfo("Complete", "Automated installation cycle finished.")
        self.refresh_diagnostic_async()

    def check_updates_async(self):
        self.set_busy(True, "Checking for remote updates...")
        def worker():
            updates = {}
            for k in self.checker.manifest_data.get("tools", {}):
                has_u, curr, lat = self.updater.check_for_updates(k)
                if has_u:
                    updates[k] = (curr, lat)
            self.after(0, lambda: self._on_check_updates_finish(updates))

        threading.Thread(target=worker, daemon=True).start()

    def _on_check_updates_finish(self, updates: Dict[str, Any]):
        self.set_busy(False, f"Check complete. {len(updates)} update(s) available.")
        if updates:
            details = "\n".join([f"• {k}: {curr} -> {lat}" for k, (curr, lat) in updates.items()])
            messagebox.showinfo("Updates Available", f"New versions detected:\n\n{details}")
        else:
            messagebox.showinfo("Up to Date", "All installed tools are up to date!")
        self.refresh_diagnostic_async()

    def update_selected_tool(self):
        sel = self.tree_tools.selection()
        if not sel:
            messagebox.showwarning("Selection", "Please select a tool from the list first.")
            return
        item = self.tree_tools.item(sel[0])
        tool_key = item["values"][0]

        self.set_busy(True, f"Updating {tool_key}...")
        def worker():
            ok = self.updater.upgrade_tool(tool_key)
            self.after(0, lambda: self._on_update_finish(tool_key, ok))

        threading.Thread(target=worker, daemon=True).start()

    def _on_update_finish(self, tool_key: str, ok: bool):
        self.set_busy(False, f"Update of {tool_key} finished.")
        if ok:
            messagebox.showinfo("Success", f"{tool_key} updated successfully!")
        else:
            messagebox.showerror("Error", f"Failed to update {tool_key}.")
        self.refresh_diagnostic_async()

    def configure_paths(self):
        res = self.configurator.configure_environment()
        ps = self.configurator.generate_persistent_system_script()
        files = "\n".join([f"• {k}: {v}" for k, v in res["exported_files"].items()])
        msg = f"eSim Environment Profiles Generated:\n\n{files}\n• Persistent script: {ps}"
        messagebox.showinfo("Environment Configured", msg)
        self._refresh_logs()

    def install_python_deps_async(self):
        self.set_busy(True, "Installing Python dependencies...")
        def worker():
            ok = self.installer.install_python_dependencies()
            self.after(0, lambda: self._on_python_install_finish(ok))

        threading.Thread(target=worker, daemon=True).start()

    def _on_python_install_finish(self, ok: bool):
        self.set_busy(False, "Python installation finished.")
        if ok:
            messagebox.showinfo("Success", "Python scientific stack is up to date!")
        else:
            messagebox.showerror("Error", "Failed to install Python dependencies.")
        self.refresh_diagnostic_async()


def launch_gui():
    app = ToolManagerApp()
    app.mainloop()


if __name__ == "__main__":
    launch_gui()
