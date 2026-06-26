import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException
from datetime import datetime
import threading
 
# =========================
# DEVICE LIST
# Layer 2 switch = cisco_ios
# Layer 3 switch = cisco_ios (with routing commands available)
# Nexus switch   = cisco_nxos
# IOS-XE         = cisco_xe
# =========================
devices = {
    "R1 (Router)": {
        "device_type": "cisco_ios",
        "host": "devnetsandboxiosxec8k.cisco.com",
        "username": "jaxnaipao",
        "password": "rw67Ek-8cA-Rwg",
        "port": 22,
        "fast_cli": False,
    },
    # Example switch entry — update host/credentials as needed
    # "SW1 (L2 Switch)": {
    #     "device_type": "cisco_ios",
    #     "host": "192.168.1.2",
    #     "username": "admin",
    #     "password": "yourpassword",
    #     "port": 22,
    #     "fast_cli": False,
    # },
    # "SW2 (Nexus)": {
    #     "device_type": "cisco_nxos",
    #     "host": "192.168.1.3",
    #     "username": "admin",
    #     "password": "yourpassword",
    #     "port": 22,
    #     "fast_cli": False,
    # },
}
 
# =========================
# COMMANDS
# Marked with device type support:
#   [R]  = Router only
#   [L3] = Layer 3 switch or router
#   [ALL] = Works on all Cisco devices
# =========================
commands = [
    # (command,                     scope,      label)
    ("show version",               "ALL",      "🔀 Both    │ show version"),
    ("show ip interface brief",    "ALL",      "🔀 Both    │ show ip interface brief"),
    ("show cdp neighbors",         "ALL",      "🔀 Both    │ show cdp neighbors"),
    ("show ip route",              "ROUTER",   "🔵 Router  │ show ip route"),
    ("show interfaces status",     "SWITCH",   "🟢 Switch  │ show interfaces status"),
    ("show vlan brief",            "SWITCH",   "🟢 Switch  │ show vlan brief"),
    ("show spanning-tree",         "SWITCH",   "🟢 Switch  │ show spanning-tree"),
    ("show mac address-table",     "SWITCH",   "🟢 Switch  │ show mac address-table"),
    ("show etherchannel summary",  "SWITCH",   "🟢 Switch  │ show etherchannel summary"),
    ("show interfaces trunk",      "SWITCH",   "🟢 Switch  │ show interfaces trunk"),
]
 
# =========================
# SESSION LOG (one file per session)
# =========================
session_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
conn = None
current_device_name = None
 
 
def connect_device(device):
    return ConnectHandler(**device)
 
 
def save_output(device_name, command, output):
    filename = f"{device_name}_{session_timestamp}.txt"
    with open(filename, "a") as f:
        f.write(f"COMMAND: {command}\n")
        f.write(output)
        f.write("\n" + "=" * 50 + "\n")
    return filename
 
 
# =========================
# GUI
# =========================
class NetworkToolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Automation Tool")
        self.root.configure(bg="#1e1e2e")
        self.root.geometry("900x680")
        self.root.resizable(True, True)
 
        self.conn = None
        self.current_device = None
        self._build_ui()
 
    def _build_ui(self):
        # ── Header ──────────────────────────────────────────────
        header = tk.Frame(self.root, bg="#181825", pady=10)
        header.pack(fill="x")
        tk.Label(
            header, text="⚡ Network Automation Tool",
            font=("Courier New", 16, "bold"),
            fg="#cba6f7", bg="#181825"
        ).pack()
        tk.Label(
            header, text="Cisco IOS · IOS-XE · NX-OS",
            font=("Courier New", 9),
            fg="#6c7086", bg="#181825"
        ).pack()
 
        # ── Main body ───────────────────────────────────────────
        body = tk.Frame(self.root, bg="#1e1e2e")
        body.pack(fill="both", expand=True, padx=16, pady=12)
 
        # Left panel: device + commands
        left = tk.Frame(body, bg="#1e1e2e", width=240)
        left.pack(side="left", fill="y", padx=(0, 12))
        left.pack_propagate(False)
 
        # Device selector
        tk.Label(left, text="DEVICE", font=("Courier New", 9, "bold"),
                 fg="#6c7086", bg="#1e1e2e").pack(anchor="w", pady=(0, 4))
 
        self.device_var = tk.StringVar()
        device_names = list(devices.keys())
        self.device_var.set(device_names[0])
 
        device_menu = ttk.Combobox(
            left, textvariable=self.device_var,
            values=device_names, state="readonly", width=26
        )
        device_menu.pack(anchor="w", pady=(0, 10))
 
        # Style the combobox
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox",
                        fieldbackground="#313244",
                        background="#313244",
                        foreground="#cdd6f4",
                        selectbackground="#45475a",
                        selectforeground="#cdd6f4")
 
        # Connect button
        self.connect_btn = tk.Button(
            left, text="Connect",
            command=self._connect,
            bg="#a6e3a1", fg="#1e1e2e",
            font=("Courier New", 10, "bold"),
            relief="flat", cursor="hand2",
            activebackground="#94d49a", activeforeground="#1e1e2e",
            padx=8, pady=5
        )
        self.connect_btn.pack(fill="x", pady=(0, 4))
 
        self.disconnect_btn = tk.Button(
            left, text="Disconnect",
            command=self._disconnect,
            bg="#313244", fg="#f38ba8",
            font=("Courier New", 10),
            relief="flat", cursor="hand2",
            activebackground="#45475a", activeforeground="#f38ba8",
            padx=8, pady=5, state="disabled"
        )
        self.disconnect_btn.pack(fill="x", pady=(0, 16))
 
        # Status indicator
        self.status_label = tk.Label(
            left, text="● Disconnected",
            font=("Courier New", 9), fg="#f38ba8", bg="#1e1e2e"
        )
        self.status_label.pack(anchor="w", pady=(0, 16))
 
        # Commands label
        tk.Label(left, text="COMMANDS", font=("Courier New", 9, "bold"),
                 fg="#6c7086", bg="#1e1e2e").pack(anchor="w", pady=(0, 6))
 
        # Legend
        legend_frame = tk.Frame(left, bg="#1e1e2e")
        legend_frame.pack(anchor="w", pady=(0, 6))
        tk.Label(legend_frame, text="🔵 Router  ", font=("Courier New", 8), fg="#89b4fa", bg="#1e1e2e").pack(side="left")
        tk.Label(legend_frame, text="🟢 Switch  ", font=("Courier New", 8), fg="#a6e3a1", bg="#1e1e2e").pack(side="left")
        tk.Label(legend_frame, text="🔀 Both",    font=("Courier New", 8), fg="#cdd6f4", bg="#1e1e2e").pack(side="left")
 
        # Command buttons
        self.cmd_buttons = []
        for cmd, scope, label in commands:
            if scope == "ROUTER":
                fg_color = "#89b4fa"
            elif scope == "SWITCH":
                fg_color = "#a6e3a1"
            else:
                fg_color = "#cdd6f4"
 
            btn = tk.Button(
                left,
                text=label,
                command=lambda c=cmd: self._run_command(c),
                bg="#313244", fg=fg_color,
                font=("Courier New", 9),
                relief="flat", cursor="hand2",
                activebackground="#45475a", activeforeground=fg_color,
                anchor="w", padx=8, pady=4,
                state="disabled"
            )
            btn.pack(fill="x", pady=2)
            self.cmd_buttons.append(btn)
 
        # Clear button at bottom of left panel
        tk.Button(
            left, text="Clear Output",
            command=self._clear_output,
            bg="#181825", fg="#6c7086",
            font=("Courier New", 9),
            relief="flat", cursor="hand2",
            activebackground="#313244", activeforeground="#cdd6f4",
            pady=4
        ).pack(fill="x", pady=(12, 0))
 
        # Right panel: output
        right = tk.Frame(body, bg="#1e1e2e")
        right.pack(side="left", fill="both", expand=True)
 
        tk.Label(right, text="OUTPUT", font=("Courier New", 9, "bold"),
                 fg="#6c7086", bg="#1e1e2e").pack(anchor="w", pady=(0, 4))
 
        self.output_box = scrolledtext.ScrolledText(
            right,
            font=("Courier New", 10),
            bg="#11111b", fg="#cdd6f4",
            insertbackground="#cdd6f4",
            relief="flat", bd=0,
            wrap="word",
        )
        self.output_box.pack(fill="both", expand=True)
 
        # Tag colours for output
        self.output_box.tag_config("header", foreground="#cba6f7", font=("Courier New", 10, "bold"))
        self.output_box.tag_config("success", foreground="#a6e3a1")
        self.output_box.tag_config("error", foreground="#f38ba8")
        self.output_box.tag_config("info", foreground="#89b4fa")
        self.output_box.tag_config("divider", foreground="#313244")
 
        # Bottom status bar
        self.bar = tk.Label(
            self.root, text="Ready.",
            font=("Courier New", 8), fg="#6c7086", bg="#181825",
            anchor="w", padx=10
        )
        self.bar.pack(fill="x", side="bottom")
 
    # ── Helpers ─────────────────────────────────────────────────
 
    def _write(self, text, tag=None):
        if tag:
            self.output_box.insert("end", text, tag)
        else:
            self.output_box.insert("end", text)
        self.output_box.see("end")
 
    def _clear_output(self):
        self.output_box.delete("1.0", "end")
 
    def _set_status(self, connected: bool, device_name=""):
        if connected:
            self.status_label.config(text=f"● {device_name}", fg="#a6e3a1")
            self.connect_btn.config(state="disabled")
            self.disconnect_btn.config(state="normal")
            for btn in self.cmd_buttons:
                btn.config(state="normal")
        else:
            self.status_label.config(text="● Disconnected", fg="#f38ba8")
            self.connect_btn.config(state="normal")
            self.disconnect_btn.config(state="disabled")
            for btn in self.cmd_buttons:
                btn.config(state="disabled")
 
    def _set_bar(self, text):
        self.bar.config(text=text)
 
    # ── Actions ─────────────────────────────────────────────────
 
    def _connect(self):
        device_name = self.device_var.get()
        self._set_bar(f"Connecting to {device_name}...")
        self.connect_btn.config(state="disabled", text="Connecting...")
        self._write(f"\nConnecting to {device_name}...\n", "info")
        threading.Thread(target=self._connect_worker, args=(device_name,), daemon=True).start()
 
    def _connect_worker(self, device_name):
        device = devices[device_name]
        try:
            self.conn = ConnectHandler(**device)
            self.current_device = device_name
            self.root.after(0, lambda: self._on_connected(device_name))
        except NetmikoAuthenticationException:
            self.root.after(0, lambda: self._on_connect_error("Authentication failed — check credentials."))
        except NetmikoTimeoutException:
            self.root.after(0, lambda: self._on_connect_error("Connection timed out — check host/port."))
        except Exception as e:
            self.root.after(0, lambda: self._on_connect_error(str(e)))
 
    def _on_connected(self, device_name):
        self._write(f"Connected to {device_name}\n", "success")
        self._write("─" * 50 + "\n", "divider")
        self._set_status(True, device_name)
        self.connect_btn.config(text="Connect")
        self._set_bar(f"Connected — {device_name}")
 
    def _on_connect_error(self, msg):
        self._write(f"\nError: {msg}\n", "error")
        self.connect_btn.config(state="normal", text="Connect")
        self._set_bar("Connection failed.")
 
    def _disconnect(self):
        if self.conn:
            try:
                self.conn.disconnect()
            except Exception:
                pass
            self.conn = None
        self._write("\nDisconnected.\n", "info")
        self._write("─" * 50 + "\n", "divider")
        self._set_status(False)
        self._set_bar("Disconnected.")
 
    def _run_command(self, command):
        if not self.conn:
            messagebox.showerror("Not connected", "Please connect to a device first.")
            return
        self._set_bar(f"Running: {command}...")
        for btn in self.cmd_buttons:
            btn.config(state="disabled")
        threading.Thread(target=self._run_worker, args=(command,), daemon=True).start()
 
    def _run_worker(self, command):
        try:
            output = self.conn.send_command(command, delay_factor=2)
            self.root.after(0, lambda: self._on_output(command, output))
        except Exception as e:
            self.root.after(0, lambda: self._on_run_error(str(e)))
 
    def _on_output(self, command, output):
        self._write(f"\n▶ {command}\n", "header")
        self._write(output + "\n")
        self._write("─" * 50 + "\n", "divider")
 
        filename = save_output(self.current_device, command, output)
        self._write(f"💾 Saved to {filename}\n", "info")
 
        for btn in self.cmd_buttons:
            btn.config(state="normal")
        self._set_bar(f"Done: {command}")
 
    def _on_run_error(self, msg):
        self._write(f"\nCommand error: {msg}\n", "error")
        for btn in self.cmd_buttons:
            btn.config(state="normal")
        self._set_bar("Command failed.")
 
 
# =========================
# RUN
# =========================
if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkToolApp(root)
    root.mainloop()
 