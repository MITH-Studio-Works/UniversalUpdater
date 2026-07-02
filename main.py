import tkinter as tk
from tkinter import scrolledtext
import subprocess
import threading
import sys
import ctypes
import os

def is_admin():
    """Check if the script is running with administrative privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def run_updates(log_area, button):
    button.config(state=tk.DISABLED)
    log_area.delete(1.0, tk.END)
    log_area.insert(tk.END, "Checking for system updates (WinGet)...\n")
    log_area.see(tk.END)

    # WinGet command with auto-agreements
    command = [
        "winget", "upgrade", "--all", 
        "--silent", 
        "--accept-package-agreements", 
        "--accept-source-agreements",
        "--include-unknown"
    ]

    try:
        process = subprocess.Popen(
            command, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True, 
            shell=True
        )

        for line in process.stdout:
            log_area.insert(tk.END, line)
            log_area.see(tk.END)

        process.wait()
        log_area.insert(tk.END, "\n[Finished] Update process complete.\n")
    except Exception as e:
        log_area.insert(tk.END, f"\n[Error] {str(e)}\n")
    
    button.config(state=tk.NORMAL)

def start_update_thread(log_area, button):
    threading.Thread(target=run_updates, args=(log_area, button), daemon=True).start()

# --- Elevation Logic ---
if not is_admin():
    # Re-run the script with admin rights
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join([os.path.abspath(sys.argv[0])] + sys.argv[1:]), None, 1
    )
    sys.exit()

# --- GUI Setup (Only runs if Admin) ---
root = tk.Tk()
root.title("Universal App Updater (Elevated)")
root.geometry("650x450")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack(fill=tk.BOTH, expand=True)

update_btn = tk.Button(
    frame, 
    text="Scan & Update All Software", 
    command=lambda: start_update_thread(log_area, update_btn),
    bg="#1a73e8", 
    fg="white", 
    font=("Arial", 11, "bold"), 
    pady=8
)
update_btn.pack(fill=tk.X, pady=(0, 10))

log_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD, font=("Consolas", 10))
log_area.pack(fill=tk.BOTH, expand=True)
log_area.insert(tk.END, "Application running with administrative privileges.\nReady to update.\n")

root.mainloop()