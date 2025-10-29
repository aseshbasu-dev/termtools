# setup context menu entry for all users, to run TermTools from any folder
# Run once as Administrator.

import sys
import winreg
import ctypes

# Check for admin privileges and re-run with elevation if needed
if ctypes.windll.shell32.IsUserAnAdmin() == 0:
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

# set this to the path of your script under Program Files (no copying done here)
script_path = r"C:\Program Files\BasusTools\TermTools\TermTools.py"

menu_key = r"Software\Classes\Directory\Background\shell\TermTools"
command_key = menu_key + r"\command"

cmd = f'"{sys.executable}" "{script_path}" "%V"'

with winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE) as hk:
    # create menu key and set its displayed text
    with winreg.CreateKeyEx(hk, menu_key, 0, winreg.KEY_WRITE) as k:
        winreg.SetValueEx(k, None, 0, winreg.REG_SZ, "Run TermTools")
    # create command subkey and set the command
    with winreg.CreateKeyEx(hk, command_key, 0, winreg.KEY_WRITE) as k:
        winreg.SetValueEx(k, None, 0, winreg.REG_SZ, cmd)
