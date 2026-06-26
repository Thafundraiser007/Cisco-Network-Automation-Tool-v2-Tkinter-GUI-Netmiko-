# Cisco-Network-Automation-Tool-v2-Tkinter-GUI-Netmiko-
Original Project: https://github.com/Thafundraiser007/Cisco-Network-Automation-with-Python-Netmiko-Cisco-DevNet-



<img width="2144" height="1295" alt="2  Commands working successfully" src="https://github.com/user-attachments/assets/6f298ae2-146e-4bec-a69e-80f62317e3c9" />

Features:
-Modern GUI
-Modern Tkinter interface
-Device selection via dropdown
-One-click command execution (no typing required)
-Connect / Disconnect buttons
-Live connection status indicator
-Status bar showing current operations
-Clear Output button

Cisco Device Support
Supports multiple Cisco platforms:
-Cisco IOS Routers
-Cisco IOS Layer 2 Switches
-Cisco IOS Layer 3 Switches
-Cisco IOS-XE
-Cisco Nexus (NX-OS)
Example device templates are included for easy expansion.

Works on Routers & Switches
-show version
-show ip interface brief
-show cdp neighbors
-Router Commands
-show ip route
-Switch Commands
-show interfaces status
-show vlan brief
-show spanning-tree
-show mac address-table
-show etherchannel summary
-show interfaces trunk

Commands are colour-coded inside the GUI:
🔵 Router
🟢 Switch
🔀 Both

Threaded Operation
Long-running SSH connections execute in background threads.
This keeps the GUI responsive while:
-Connecting to devices
-Running commands
-Waiting for SSH responses

Error Handling
Gracefully handles:
-Invalid credentials
-Connection timeouts
-SSH failures
-Unexpected runtime exceptions
The application continues running instead of crashing.

Session Logging
Instead of generating one log per command, Version 2 creates:
One log file per session
Example: R1 (Router)_2026-06-26_14-42-11.txt
Each log contains:
-Executed command
-Command output
-Timestamp separator

Enhanced Output Panel
Colour-coded output improves readability.
| Colour | Purpose               |
| ------ | --------------------- |
| Purple | Command headers       |
| Green  | Successful operations |
| Blue   | Status information    |
| Red    | Errors                |
| Grey   | Output separators     |

Device Templates

Pre-configured examples are included for:

Cisco IOS Routers
-Layer 2 Switches
-Layer 3 Switches
-Cisco Nexus
-Cisco IOS-XE
Simply update the IP address and credentials.

Scope-Aware Commands
| Scope  | Description          |
| ------ | -------------------- |
| ROUTER | Router-only commands |
| SWITCH | Switch-only commands |
| ALL    | Supported on both    |
The GUI automatically colours each command button based on its scope.

User Experience Improvements
-Cleaner interface
-Better visual feedback
-Responsive GUI
-Command categorisation
-Device legend
-Improved navigation
-Simplified workflow

Technologies Used
-Python 3
-Netmiko
-Tkinter
-Cisco IOS
-Cisco IOS-XE
-Cisco NX-OS
-SSH

Installation
git clone https://github.com/Thafundraiser007/Cisco-Network-Automation-with-Python-Netmiko-Cisco-DevNet-.git
cd Cisco-Network-Automation-with-Python-Netmiko-Cisco-DevNet-
pip install -r requirements.txt
python network_tool.py


Author
Jamill Naipao
GitHub: https://github.com/Thafundraiser007
LinkedIn: https://www.linkedin.com/in/jamill-naipao-6447982bb
