# Import the standard GUI library for creating windows and widgets
import tkinter as tk
# Import the specific scrollable text area widget for logs
from tkinter import scrolledtext
# Import the module used to run external system commands like WinGet or PowerShell
import subprocess
# Import threading to prevent the user interface from freezing during updates
import threading
# Import data types interface to interact with native Windows administrative features
import ctypes
# Import operating system utilities to write and delete temporary files
import os

def run_dual_updates(log_area, button):
    """Executes the dual-layer update pipeline: WinGet first, then Windows Updates."""
    # Temporarily disable the action button to prevent double-clicking
    button.config(state=tk.DISABLED)
    # Clear out any text currently residing inside the log panel
    log_area.delete(1.0, tk.END)
    
    # ==========================================
    # STAGE 1: Standard WinGet Program Updates
    # ==========================================
    log_area.insert(tk.END, "=== STAGE 1: Updating Installed Programs (WinGet) ===\n")
    log_area.see(tk.END)

    # Define the exact parameters used to silently upgrade all standard applications
    winget_command = [
        "winget", "upgrade", "--all", 
        "--silent", 
        "--accept-package-agreements", 
        "--accept-source-agreements",
        "--include-unknown"
    ]

    try:
        # Launch the original WinGet tool inside a background shell execution
        process = subprocess.Popen(
            winget_command, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True, 
            shell=True
        )

        # Continuously read incoming console lines from the running WinGet command
        for line in process.stdout:
            log_area.insert(tk.END, line)
            log_area.see(tk.END)

        # Wait for WinGet to finish execution entirely before proceeding
        process.wait()
    except Exception as e:
        log_area.insert(tk.END, f"\n[WinGet Error] {str(e)}\n")

    # ==========================================
    # STAGE 2: Windows Operating System Updates
    # ==========================================
    log_area.insert(tk.END, "\n" + "="*50 + "\n")
    log_area.insert(tk.END, "=== STAGE 2: Checking OS-Level Windows Updates ===\n")
    log_area.insert(tk.END, "Querying the Microsoft Update Agent (this may take a moment)...\n")
    log_area.see(tk.END)

    # Define a clean multi-line script content block without escaped quote limitations
    powershell_script_content = """
    $UpdateSession = New-Object -ComObject Microsoft.Update.Session
    $UpdateSearcher = $UpdateSession.CreateUpdateSearcher()
    $SearchResult = $UpdateSearcher.Search("IsInstalled=0 and IsHidden=0")
    
    if ($SearchResult.Updates.Count -eq 0) { 
        Write-Output "Your Windows OS is completely up to date. No installation needed."
    } else {
        Write-Output "Found $($SearchResult.Updates.Count) pending OS updates. Initiating download & install..."
        $UpdateCollection = New-Object -ComObject Microsoft.Update.UpdateColl
        foreach ($Update in $SearchResult.Updates) { 
            [void]$UpdateCollection.Add($Update) 
        }
        $Downloader = $UpdateSession.CreateUpdateDownloader()
        $Downloader.Updates = $UpdateCollection
        [void]$Downloader.Download()
        
        Write-Output "Download complete. Beginning silent installation phase..."
        $Installer = $UpdateSession.CreateUpdateInstaller()
        $Installer.Updates = $UpdateCollection
        $InstallResult = $Installer.Install()
        
        Write-Output "Process finalized. Result Code: $($InstallResult.ResultCode)"
        Write-Output "Is a system reboot required? $($InstallResult.RebootRequired)"
    }
    """

    # Define a local name string for the temporary file execution hook
    temp_script_path = "temp_update_check.ps1"

    try:
        # Write out the clean script block directly to disk
        with open(temp_script_path, "w", encoding="utf-8") as script_file:
            script_file.write(powershell_script_content)

        # Formulate execution command calling the local script file while bypassing restrictions
        os_update_command = [
            "powershell", 
            "-NoProfile", 
            "-ExecutionPolicy", "Bypass", 
            "-File", temp_script_path
        ]

        # Open a secondary subprocess tracking the live Windows Update installation stream
        os_process = subprocess.Popen(
            os_update_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            shell=True
        )

        # Read the real-time installation output loop coming back from PowerShell
        for os_line in os_process.stdout:
            log_area.insert(tk.END, os_line)
            log_area.see(tk.END)

        # Wait for the system update mechanism process to exit clean
        os_process.wait()
        log_area.insert(tk.END, "\n=== All update pipelines finalized successfully! ===\n")
        
    except Exception as os_err:
        log_area.insert(tk.END, f"\n[Windows Update Error] {str(os_err)}\n")
        
    finally:
        # CLEANUP: Ensure the temporary script file is dropped from the folder when finished
        if os.path.exists(temp_script_path):
            os.remove(temp_script_path)

    # Reactivate the interactive button trigger so another check can be run down the line
    button.config(state=tk.NORMAL)

def start_update_thread(log_area, button):
    """Spawns a background thread to prevent the interface window from locking up."""
    threading.Thread(target=run_dual_updates, args=(log_area, button), daemon=True).start()

# --- Security check initialization ---
is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0

# Construct the main application window object frame container
root = tk.Tk()
root.title("Universal App & System Updater")
root.geometry("650x500")

# --- UPDATE YOUR ICON PATH HERE ---
try:
    # Point directly to the assets subfolder path
    root.iconbitmap(os.path.join("assets", "app_icon.ico"))
except Exception:
    # Pass safely if the path is not resolved locally
    pass

# Setup layout framing padding margins
frame = tk.Frame(root, padx=10, pady=10)
frame.pack(fill=tk.BOTH, expand=True)

# Build the execution button panel assigning style attributes and callback event connections
update_btn = tk.Button(
    frame, 
    text="Run Program & Windows Updates", 
    command=lambda: start_update_thread(log_area, update_btn),
    bg="#1a73e8", 
    fg="white", 
    font=("Arial", 11, "bold"), 
    pady=8
)
update_btn.pack(fill=tk.X, pady=(0, 10))

# Initialize the scrolling log display container to catch standard logging outputs
log_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD, font=("Consolas", 10))
log_area.pack(fill=tk.BOTH, expand=True)

# Print current privilege status immediately to the log screen
if is_admin:
    log_area.insert(tk.END, "STATUS: Running with administrative privileges.\nReady to run full pipeline.\n\n")
else:
    log_area.insert(tk.END, "WARNING: Administrative privileges not detected.\n")
    log_area.insert(tk.END, "Please run your terminal application as an Administrator before executing this file.\n\n")

# Engage the fundamental persistent execution loop monitoring user UI mouse events indefinitely
root.mainloop()