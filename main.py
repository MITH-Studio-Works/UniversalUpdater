import tkinter as tk # Imports the standard GUI library
from tkinter import scrolledtext # Imports the specialized text widget for scrolling logs
import subprocess # Imports the module to run external system commands
import threading # Imports threading to keep the GUI responsive during updates
import sys # Imports system-specific parameters and functions
import ctypes # Imports foreign function library to call Windows API commands
import os # Imports operating system interface for file path management

def is_admin():
    """Check if the script is running with administrative privileges."""
    try:
        # Calls the Windows shell32 library to verify administrator status
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        # Returns False if the check fails for any reason
        return False

def run_updates(log_area, button):
    # Disables the button so user can't click it multiple times
    button.config(state=tk.DISABLED)
    # Clears out any existing text in the log display area
    log_area.delete(1.0, tk.END)
    
    # --- PHASE 1: Windows OS Updates ---
    log_area.insert(tk.END, "Phase 1: Checking for Windows OS Updates...\n")
    # Forces the log window to automatically scroll to the bottom
    log_area.see(tk.END)

    # PowerShell command to install the update module and apply pending patches silently
    os_command = [
        "powershell", "-Command", 
        "Install-Module -Name PSWindowsUpdate -Force -AllowClobber -Scope CurrentUser; "
        "Get-WindowsUpdate -Install -AcceptAll -IgnoreReboot"
    ]

    try:
        # Launches the PowerShell update process in the background
        os_process = subprocess.Popen(
            os_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=True
        )

        # Reads the output lines from PowerShell in real-time and pushes them to the log
        for line in os_process.stdout:
            log_area.insert(tk.END, line)
            log_area.see(tk.END)

        # Waits for the OS update command to finish executing
        os_process.wait()
    except Exception as e:
        # Logs any unexpected errors that occur during the Windows Update phase
        log_area.insert(tk.END, f"\n[OS Update Error] {str(e)}\n")

    # --- PHASE 2: Application Updates (WinGet) ---
    log_area.insert(tk.END, "\nPhase 2: Checking for Application Updates (WinGet)...\n")
    log_area.see(tk.END)

    # Standard winget upgrade command with automated flags to bypass prompts
    winget_command = [
        "winget", "upgrade", "--all", "--silent", 
        "--accept-package-agreements", "--accept-source-agreements", "--include-unknown"
    ]

    try:
        # Launches the WinGet upgrade tool in the background
        winget_process = subprocess.Popen(
            winget_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=True
        )

        # Reads and logs the WinGet output lines in real-time
        for line in winget_process.stdout:
            log_area.insert(tk.END, line)
            log_area.see(tk.END)

        # Waits for the application update command to finish executing
        winget_process.wait()
        # Notifies user the master sweep is completely done
        log_area.insert(tk.END, "\n[Finished] Universal Update process complete. Please reboot to apply OS patches.\n")
    except Exception as e:
        # Logs any unexpected errors that occur during the WinGet phase
        log_area.insert(tk.END, f"\n[WinGet Error] {str(e)}\n")
    
    # Re-enables the button so the user can run a scan again later
    button.config(state=tk.NORMAL)

def start_update_thread(log_area, button):
    # Spawns a background thread for the update function to prevent freezing the GUI window
    threading.Thread(target=run_updates, args=(log_area, button), daemon=True).start()

# --- Elevation Logic ---
if not is_admin():
    # Relaunches the entire script using the Windows 'runas' verb to trigger User Account Control (UAC)
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join([os.path.abspath(sys.argv[0])] + sys.argv[1:]), None, 1
    )
    # Exits the non-elevated script instance safely
    sys.exit()

# --- GUI Setup (Only runs if Admin) ---
root = tk.Tk() # Creates the main window container
root.title("Universal Update Engine") # Sets the window header text
root.geometry("650x500") # Sets the starting width and height dimensions of the window

# Determines the absolute path to the asset file dynamically, regardless of where launched
icon_path = os.path.join(os.path.dirname(__file__), "assets", "app_icon.ico")
if os.path.exists(icon_path):
    # Applies the custom application icon to the window title bar if the file exists
    root.iconbitmap(icon_path)

frame = tk.Frame(root, padx=10, pady=10) # Creates an internal frame with padding for layout spacing
frame.pack(fill=tk.BOTH, expand=True) # Forces the frame to stretch to fill the window size

update_btn = tk.Button(
    frame, 
    text="Execute Master Update Sweep", # Renamed button to match the expanded scope
    command=lambda: start_update_thread(log_area, update_btn), # Triggers the multi-phase thread
    bg="#1a73e8", fg="white", font=("Arial", 11, "bold"), pady=8 # Styles the action button
)
update_btn.pack(fill=tk.X, pady=(0, 10)) # Places the button and adds bottom margin layout spacing

log_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD, font=("Consolas", 10)) # Creates logging panel
log_area.pack(fill=tk.BOTH, expand=True) # Stretches the logging text pane to fill available space
log_area.insert(tk.END, "System operating with root administrative credentials.\nReady for deployment.\n")

root.mainloop() # Enters the main execution loop to keep the window open and active