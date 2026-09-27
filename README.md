# Windows Keystream Monitor (Advanced Auditing Tool)

A high-performance, modern Python implementation of a low-level keystroke capture agent designed specifically for the **Windows Operating System**. This project modernizes legacy hooking concepts by combining native Windows API structures with efficient, robust data storage mechanisms to simulate an advanced user-monitoring payload.

---

## 🚀 Key Features

* **Modern Hooking Engine:** Employs `pynput` for precise, thread-safe asynchronous keyboard monitoring, avoiding outdated and unstable 32-bit wrapper constraints.
* **Stealth Initialization:** Automatically detaches from the standard terminal interface, executing cleanly as a background process.
* **Persistent Integration:** Writes an automated runtime key configuration directly to the Windows CurrentUser Registry environment (`Software\Microsoft\Windows\CurrentVersion\Run`), enabling full execution survival across system restarts.
* **Single-Instance Verification:** Integrates an OS-level global Mutex lock to enforce single-process execution and prevent resource conflicts.
* **Optimized Data Compression:** Implements real-time text archiving to maximize storage efficiency and obscure local disk footprint.

---

## 💾 Why Compressed Binary Storage?

Unlike standard keyloggers that write directly to plain text (`.txt`) files, this engine streams captured string entries directly into a compressed binary Gzip archive named `sys_log.dat.gz`. This choice addresses two critical design challenges:

1. **Storage Optimization:** Raw logging generates massive quantities of repetitive character strings over extended periods. Real-time Gzip compression compresses this footprint by up to **80-90%**, ensuring the tool remains practically unnoticeable on host systems with monitored storage capacity.
2. **Basic Defense Evasion:** If a standard system user stumbles into the localized `SystemData` directory, a plain text file instantly compromises the tool's presence. Storing logs in an abstract `.dat.gz` file format disguises the capture buffer as a standard or corrupted OS telemetry data file.

---

🧩 Core Code Architecture Breakdown

The engine is split into four core architectural pillars working in tandem to intercept, translate, and securely stream system input telemetry:
[Main Entry Point]
       │
       ├──► 1. Windows Environment Setup (Process Hiding & Mutex Lock)
       ├──► 2. OS Persistence Layer (Registry Key Injection)
       │
       └──► 3. Asynchronous Monitoring Engine
                     │
                     └──► [pynput Key Listener Loop]
                                  │
                                  ├──► 4. Event Handler & Native Mapping
                                  └──► 5. Streaming Gzip Compression File-write

### 1. Native Windows Integration & Stealth Initialization
* **Window Suppression:** The script interacts with native Win32 binaries using `win32console.GetConsoleWindow()` and `win32gui.ShowWindow()`. This dynamically captures the unique ID handle of the terminal process at the exact millisecond of startup and sets its display flag to hidden (`0`).
* **Concurrency Protection (Mutex):** To prevent duplicate scripts from fighting over keyboard hardware control, the script uses `win32event.CreateMutex()`. If a system-wide flag named `BestInClass_Secure_Mutex_v3` already exists, the operating system throws an `ERROR_ALREADY_EXISTS` flag, causing the new process to safely terminate instantly (`sys.exit(0)`).

### 2. Persistence Injection Layer
* **`ensure_persistence()`:** This function calls the Python `winreg` library to access the operating system's native startup settings. It targets the location `Software\Microsoft\Windows\CurrentVersion\Run` inside the `HKEY_CURRENT_USER` hive. It writes a persistent string configuration pointing back to the compiled executable path, instructing the Windows kernel to launch the program automatically every time the target user authenticates a new session.

### 3. Low-Level Event Hooking & Mapping
* **`keyboard.Listener(on_press=on_press)`:** Instead of running a heavy `while True` loop that consumes critical CPU cycles, the `pynput` framework attaches an asynchronous background hook into the Windows input thread pipeline.
* **Layout Parsing:** The event handler attempts to grab alphanumeric text using `key.char`. If a system modifier is encountered (like `Ctrl`, `Alt`, or `Backspace`), the script intercepts the raised `AttributeError` exception and translates the key cleanly using custom text templates (e.g., converting hardware key entries to `[Bck]` or `[Tab]`).

### 4. Time Management & Thread-Safe Streaming Data Writing
* **3-Hour Anchoring:** Every time a keypress occurs, the current system runtime is checked against the `last_timestamp` global state. If more than 10,800 seconds (3 hours) have passed since the last tracked interaction window, a clean `--- [Log Session: YYYY-MM-DD HH:MM:SS] ---` string anchor is generated to organize the data block chronologically.
* **Non-Volatile Streaming:** The data string is appended directly into `gzip.open(LOG_FILE_PATH, "at")`. The `"at"` modifier stands for **Append Text** inside a binary stream wrapper. This flushes the data out of volatile RAM and locks it safely inside the hard drive immediately upon capture.

---

### 🛠️ Compilation Guide: Generating a Standalone `.exe`

To deploy this script natively on environments without requiring a functional Python interpreter or external dependencies, compile it into an executable using **PyInstaller**.

### Step 1: Install PyInstaller
Open your command terminal (`cmd`) and install the distribution package:
```bash
pip install pyinstaller
```

### Step 2: Build the Payload
Navigate to the directory containing your main python file (e.g., `monitor.py`) and compile using the optimized flags:
```bash
pyinstaller --onefile --noconsole monitor.py
```

### Deployment Flag Breakdown:
* `--onefile`: Compresses the internal Python runtime environment, operational scripts, and dependency libraries into a **single, standalone `.exe` executable**.
* `--noconsole`: Forces Windows to immediately categorize the process as a background service without opening or rendering a command prompt window at startup.

Once the compilation concludes, the self-contained executable file can be found in the newly generated `dist/` directory.

---

## 🔍 Retrieval Scenarios & Post-Exploitation Lifecycle

Once data collection has successfully populated the local host storage, the compressed file requires extraction. In practical red-teaming scenarios, extraction takes place via two key methodologies:

### Scenario A: Physical / Local Extraction
This scenario assumes a localized secondary access window. An analyst or operator connects to the host machine directly, navigates to the hidden `%LOCALAPPDATA%\SystemData` subdirectory, and copies the `sys_log.dat.gz` file out to external hardware storage or maps it over an open localized SMB configuration.

### Scenario B: Advanced Network Exfiltration (C2 / RAT Access)
In complex, high-tier threat landscapes, active telemetry logs are exfiltrated using dedicated remote network pipelines. 
> 🔔 **Stay Tuned:** To maintain deep viewer engagement and demonstrate complete operational lifecycles, **our next upcoming repository release will detail the construction of a customized Remote Access Trojan (RAT) and Command & Control (C2) server** designed specifically to establish interactive shells, manage remote directory manipulation, and quietly download these logs across network boundaries! **Star the repository to receive notifications.**

---

## 🔓 How to Read & Decompress the Log Files

If you have extracted the log file via **Scenario A**, you cannot read the data directly through Notepad. Use the following auxiliary decoding utility to automatically decompress the binary collection back into a human-readable plain text audit log.

### Extraction Code (`decoder.py`)

```python
import gzip
import os

# Path to the file retrieved from the target machine
RETRIEVED_FILE = "sys_log.dat.gz"
OUTPUT_TEXT_FILE = "decrypted_keystrokes.txt"

def read_and_extract_logs():
    if not os.path.exists(RETRIEVED_FILE):
        print(f"[-] Error: {RETRIEVED_FILE} not found in the current directory.")
        return

    try:
        # Open in 'rt' (Read Text) mode inside the Gzip compressed layer
        with gzip.open(RETRIEVED_FILE, "rt", encoding="utf-8") as compressed_file:
            log_content = compressed_file.read()
        
        print("[+] Successfully decompressed the log file. Content preview:\n")
        print(log_content)
        
        # Save output back into standard plain text formatting
        with open(OUTPUT_TEXT_FILE, "w", encoding="utf-8") as plain_file:
            plain_file.write(log_content)
            
        print(f"\n[+] Full plain text log saved to: {OUTPUT_TEXT_FILE}")

    except Exception as e:
        print(f"[-] Failed to decompress file: {e}")

if __name__ == "__main__":
    read_and_extract_logs()
```

### Steps to Run the Decoder:
1. Place the copied `sys_log.dat.gz` file into the same directory as the script above.
2. Execute the python script:
   ```bash
   python decoder.py
   ```
3. Open `decrypted_keystrokes.txt` to analyze your final, timestamped data array.

---

## ⚖️ Disclaimer & Educational Notice
This tool was created solely for advanced academic research, system optimization tests, and authorized security auditing purposes. Running this tool without explicit administrative privilege or prior consent on hardware systems you do not own constitutes an unauthorized system violation. The developer assumes zero liability for system degradation or security policy violations caused by misuse.

