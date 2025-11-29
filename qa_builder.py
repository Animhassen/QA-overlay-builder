import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import subprocess
import threading
import datetime
import sys

class QABuilder:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("QA Overlay Builder")
        self.root.geometry("600x400")
        self.root.resizable(True, True)
        
        # Variables
        self.api_key = tk.StringVar(value="")
        self.hotkey = tk.StringVar(value="ctrl+alt+q")
        self.model = tk.StringVar(value="llama-3.1-70b-versatile")
        self.overlay_pos = tk.StringVar(value="bottom-right")
        self.icon_path = tk.StringVar(value="image.ico")
        self.output_name = tk.StringVar(value="QA_standalone")
        self.expire_date = tk.StringVar(value="2025-12-31")
        self.expire_hour = tk.StringVar(value="11")
        self.expire_minute = tk.StringVar(value="59")
        self.expire_ampm = tk.StringVar(value="PM")
        
        self.setup_ui()
    
    def setup_ui(self):
        # Title
        title = tk.Label(self.root, text="QA Overlay Builder", font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        # Create canvas and scrollbar
        canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Main frame
        main_frame = scrollable_frame
        
        # API Configuration
        api_frame = ttk.LabelFrame(main_frame, text="API Configuration", padding=10)
        api_frame.pack(fill="x", pady=5)
        
        ttk.Label(api_frame, text="Groq API Key:").pack(anchor="w")
        ttk.Entry(api_frame, textvariable=self.api_key, width=70, show="*").pack(fill="x", pady=2)
        
        ttk.Label(api_frame, text="Model:").pack(anchor="w", pady=(10,0))
        model_combo = ttk.Combobox(api_frame, textvariable=self.model, values=[
            "llama-3.1-8b-instant", "llama-3.1-70b-versatile", "mixtral-8x7b-32768"
        ])
        model_combo.pack(fill="x", pady=2)
        
        # UI Configuration
        ui_frame = ttk.LabelFrame(main_frame, text="UI Configuration", padding=10)
        ui_frame.pack(fill="x", pady=5)
        
        ttk.Label(ui_frame, text="Hotkey:").pack(anchor="w")
        hotkey_combo = ttk.Combobox(ui_frame, textvariable=self.hotkey, values=[
            "ctrl+alt+q", "ctrl+shift+q", "ctrl+shift+a", "ctrl+shift+z", "alt+shift+q", "ctrl+q"
        ])
        hotkey_combo.pack(fill="x", pady=2)
        
        ttk.Label(ui_frame, text="Overlay Position:").pack(anchor="w", pady=(10,0))
        pos_combo = ttk.Combobox(ui_frame, textvariable=self.overlay_pos, values=[
            "bottom-left", "bottom-right", "top-left", "top-right"
        ])
        pos_combo.pack(fill="x", pady=2)
        
        # Build Configuration
        build_frame = ttk.LabelFrame(main_frame, text="Build Configuration", padding=10)
        build_frame.pack(fill="x", pady=5)
        
        ttk.Label(build_frame, text="Output Name:").pack(anchor="w")
        ttk.Entry(build_frame, textvariable=self.output_name, width=30).pack(fill="x", pady=2)
        
        ttk.Label(build_frame, text="Expiration Date (YYYY-MM-DD):").pack(anchor="w", pady=(10,0))
        date_entry = ttk.Entry(build_frame, textvariable=self.expire_date, width=30)
        date_entry.pack(fill="x", pady=2)
        date_entry.bind('<KeyRelease>', self.update_remaining_time)
        
        time_frame = ttk.Frame(build_frame)
        time_frame.pack(fill="x", pady=(5,0))
        ttk.Label(time_frame, text="Time (12-hour format):").pack(anchor="w")
        time_entry_frame = ttk.Frame(time_frame)
        time_entry_frame.pack(fill="x", pady=2)
        
        hour_entry = ttk.Entry(time_entry_frame, textvariable=self.expire_hour, width=5)
        hour_entry.pack(side="left")
        hour_entry.bind('<KeyRelease>', self.update_remaining_time)
        
        ttk.Label(time_entry_frame, text=":").pack(side="left", padx=2)
        
        minute_entry = ttk.Entry(time_entry_frame, textvariable=self.expire_minute, width=5)
        minute_entry.pack(side="left")
        minute_entry.bind('<KeyRelease>', self.update_remaining_time)
        
        ampm_combo = ttk.Combobox(time_entry_frame, textvariable=self.expire_ampm, values=["AM", "PM"], width=5)
        ampm_combo.pack(side="left", padx=(5,0))
        ampm_combo.bind('<<ComboboxSelected>>', self.update_remaining_time)
        
        # Remaining time label
        self.remaining_label = tk.Label(build_frame, text="", fg="blue", font=("Arial", 9))
        self.remaining_label.pack(anchor="w", pady=(5,0))
        
        # Initial remaining time calculation
        try:
            self.update_remaining_time()
        except:
            pass
        
        icon_frame = ttk.Frame(build_frame)
        icon_frame.pack(fill="x", pady=(10,0))
        ttk.Label(icon_frame, text="Icon File:").pack(anchor="w")
        icon_entry_frame = ttk.Frame(icon_frame)
        icon_entry_frame.pack(fill="x", pady=2)
        ttk.Entry(icon_entry_frame, textvariable=self.icon_path).pack(side="left", fill="x", expand=True)
        ttk.Button(icon_entry_frame, text="Browse", command=self.browse_icon).pack(side="right", padx=(5,0))
        
        # Progress
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill="x", pady=10)
        
        self.status_label = tk.Label(main_frame, text="Ready to build", fg="green")
        self.status_label.pack(pady=5)
        
        # Quick buttons frame
        quick_frame = ttk.LabelFrame(main_frame, text="Quick Setup", padding=10)
        quick_frame.pack(fill="x", pady=5)
        
        quick_buttons_frame = ttk.Frame(quick_frame)
        quick_buttons_frame.pack(fill="x")
        
        ttk.Button(quick_buttons_frame, text="30 Days (Ctrl+Alt+Q)", 
                  command=lambda: self.quick_setup(30, "ctrl+alt+q")).pack(side="left", padx=2)
        ttk.Button(quick_buttons_frame, text="7 Days (Ctrl+Shift+A)", 
                  command=lambda: self.quick_setup(7, "ctrl+shift+a")).pack(side="left", padx=2)
        ttk.Button(quick_buttons_frame, text="1 Day (Ctrl+Shift+Z)", 
                  command=lambda: self.quick_setup(1, "ctrl+shift+z")).pack(side="left", padx=2)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=10)
        
        ttk.Button(button_frame, text="Generate Script", command=self.generate_script).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Build Executable", command=self.build_executable).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Test Script", command=self.test_script).pack(side="left", padx=5)
    
    def quick_setup(self, days, hotkey):
        """Quick setup with predefined expiration"""
        from datetime import datetime, timedelta
        expire_dt = datetime.now() + timedelta(days=days)
        
        self.expire_date.set(expire_dt.strftime("%Y-%m-%d"))
        self.expire_hour.set("11")
        self.expire_minute.set("59")
        self.expire_ampm.set("PM")
        self.hotkey.set(hotkey)
        
        self.update_remaining_time()
        self.status_label.config(text=f"Quick setup: {days} days with {hotkey}", fg="blue")
    
    def update_remaining_time(self, event=None):
        try:
            date_parts = self.expire_date.get().split('-')
            if len(date_parts) != 3:
                self.remaining_label.config(text="Invalid date format")
                return
                
            hour = int(self.expire_hour.get() or 12)
            minute = int(self.expire_minute.get() or 0)
            
            # Convert to 24-hour format
            hour_24 = hour
            if self.expire_ampm.get() == 'PM' and hour != 12:
                hour_24 += 12
            elif self.expire_ampm.get() == 'AM' and hour == 12:
                hour_24 = 0
                
            expire_datetime = datetime.datetime(
                int(date_parts[0]), int(date_parts[1]), int(date_parts[2]),
                hour_24, minute, 59
            )
            
            now = datetime.datetime.now()
            if expire_datetime > now:
                diff = expire_datetime - now
                days = diff.days
                hours, remainder = divmod(diff.seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                
                if days > 0:
                    self.remaining_label.config(text=f"Expires in: {days} days, {hours}h {minutes}m", fg="green")
                else:
                    self.remaining_label.config(text=f"Expires in: {hours}h {minutes}m", fg="orange")
            else:
                self.remaining_label.config(text="Already expired!", fg="red")
                
        except (ValueError, IndexError):
            self.remaining_label.config(text="Invalid date/time format", fg="red")
    
    def browse_icon(self):
        filename = filedialog.askopenfilename(
            title="Select Icon File",
            filetypes=[("Icon files", "*.ico"), ("All files", "*.*")]
        )
        if filename:
            self.icon_path.set(filename)
    
    def get_position_geometry(self):
        positions = {
            "bottom-left": "150x60+10+{screen_height}",
            "bottom-right": "150x60+{screen_width}+{screen_height}",
            "top-left": "150x60+10+10",
            "top-right": "150x60+{screen_width}+10"
        }
        return positions.get(self.overlay_pos.get(), positions["bottom-right"])
    
    def generate_script(self):
        self.status_label.config(text="Generating script...", fg="blue")
        
        expire_parts = self.expire_date.get().split('-')
        position_template = self.get_position_geometry()
        
        script_content = f"""import tkinter as tk
import requests
import threading
import pyperclip
import keyboard
import re
import datetime
import os
import sys

class QAOverlay:
    def __init__(self):
        if self.check_expiration():
            self.self_destruct()
            return
            
        self.root = tk.Tk()
        self.root.withdraw()
        self.overlay = tk.Toplevel()
        self.overlay.overrideredirect(True)
        self.overlay.attributes('-topmost', True)
        self.overlay.attributes('-alpha', 0.9)
        self.overlay.attributes('-toolwindow', True)
        self.overlay.configure(bg='black')
        
        # Set position based on configuration
        screen_width = self.overlay.winfo_screenwidth() - 160
        screen_height = self.overlay.winfo_screenheight() - 70
        geometry = "{position_template}".format(screen_width=screen_width, screen_height=screen_height)
        self.overlay.geometry(geometry)
        
        self.overlay.lift()
        self.overlay.focus_force()
        
        self.label = tk.Label(self.overlay, text="Ready", fg='lime', bg='black', 
                             font=('Arial', 12, 'bold'), justify='center')
        self.label.pack(fill='both', expand=True)
        
        self.last_question = ""
        keyboard.add_hotkey('{self.hotkey.get()}', self.process_question, suppress=True)
        
        self.check_expiration_periodically()
        self.overlay.after(2000, self.hide_overlay)
    
    def check_expiration_periodically(self):
        if self.check_expiration():
            self.self_destruct()
        self.root.after(30000, self.check_expiration_periodically)
    
    def extract_questions(self, text):
        questions = []
        lines = text.split('\\n')
        current_question = []
        
        for line in lines:
            if re.match(r'^\\s*\\d+\\s*\\.', line.strip()):
                if current_question:
                    questions.append('\\n'.join(current_question))
                current_question = [line]
            else:
                if current_question:
                    current_question.append(line)
        
        if current_question:
            questions.append('\\n'.join(current_question))
        
        return questions if questions else [text]
    
    def check_expiration(self):
        hour_24 = int({self.expire_hour.get()})
        ampm = '{self.expire_ampm.get()}'
        if ampm == 'PM' and hour_24 != 12:
            hour_24 += 12
        elif ampm == 'AM' and hour_24 == 12:
            hour_24 = 0
        expire_date = datetime.datetime({expire_parts[0]}, {expire_parts[1]}, {expire_parts[2]}, hour_24, {self.expire_minute.get()}, 59)
        return datetime.datetime.now() > expire_date
    
    def self_destruct(self):
        import subprocess
        try:
            if getattr(sys, 'frozen', False):
                exe_path = sys.executable
                batch_content = '@echo off\\ntimeout /t 2 /nobreak >nul\\ndel "' + exe_path + '"\\ndel "%~f0"'
                with open('temp_delete.bat', 'w') as f:
                    f.write(batch_content)
                subprocess.Popen(['temp_delete.bat'], shell=True)
            else:
                file_path = os.path.abspath(__file__)
                subprocess.Popen('timeout /t 2 && del "' + file_path + '"', shell=True)
        except:
            pass
        sys.exit()
    
    def extract_question_number(self, text):
        match = re.search(r'^\\s*(\\d+)\\s*\\.', text.strip())
        if match:
            return match.group(1)
        first_line = text.split('\\n')[0]
        match = re.search(r'(\\d+)\\s*\\.', first_line)
        return match.group(1) if match else '1'
    
    def hide_overlay(self):
        self.overlay.withdraw()
    
    def show_overlay(self):
        self.overlay.deiconify()
        self.overlay.lift()
        self.overlay.attributes('-topmost', True)
    
    def process_question(self):
        self.show_overlay()
        self.label.config(text="Analyzing...", fg='yellow')
        
        import time
        keyboard.send('ctrl+c')
        time.sleep(0.1)
        
        question = pyperclip.paste().strip()
        
        if not question or len(question) < 5:
            self.label.config(text="Select Text", fg='yellow')
            self.overlay.after(2000, self.hide_overlay)
            return
        
        self.overlay.after(500, self.hide_overlay)
            
        questions = self.extract_questions(question)
        if len(questions) > 1:
            threading.Thread(target=self.get_multiple_answers, args=(questions,), daemon=True).start()
        else:
            threading.Thread(target=self.get_answer, args=(question,), daemon=True).start()
    
    def get_multiple_answers(self, questions):
        try:
            answers = []
            for i, question in enumerate(questions):
                qnum = self.extract_question_number(question)
                
                system_prompt = "Analyze this multiple choice question and respond with ONLY the correct letter (a, b, c, or d). No explanation needed."
                
                response = requests.post(
                    'https://api.groq.com/openai/v1/chat/completions',
                    headers={{
                        'Authorization': 'Bearer {self.api_key.get()}',
                        'Content-Type': 'application/json'
                    }},
                    json={{
                        'model': '{self.model.get()}',
                        'messages': [
                            {{'role': 'system', 'content': system_prompt}},
                            {{'role': 'user', 'content': question}}
                        ],
                        'max_tokens': 3,
                        'temperature': 0
                    }},
                    timeout=15
                )
                
                if response.status_code == 200:
                    raw_answer = response.json()['choices'][0]['message']['content'].strip()
                    letter = re.search(r'[abcd]', raw_answer.lower())
                    if letter:
                        answers.append(f"{{qnum}}.{{letter.group()}}")
                    else:
                        answers.append(f"{{qnum}}.?")
                else:
                    answers.append(f"{{qnum}}.?")
            
            self.show_overlay()
            final_text = ' '.join(answers)
            self.label.config(text=final_text, fg='lime', font=('Arial', 10, 'bold'))
            self.overlay.after(3000, self.hide_overlay)
            
        except Exception as e:
            self.show_overlay()
            self.label.config(text="Error", fg='red')
            self.overlay.after(3000, self.hide_overlay)
    
    def get_answer(self, question):
        try:
            qnum = self.extract_question_number(question)
            
            system_prompt = "You are a highly knowledgeable academic expert. Analyze the multiple choice question step by step:\\n1. Read the question carefully\\n2. Evaluate each option (a, b, c, d) against the question\\n3. Select the most accurate answer\\n4. Respond with ONLY the correct letter (a, b, c, or d)\\n\\nBe very careful and accurate. Only return the single letter of the correct answer."
            
            response = requests.post(
                'https://api.groq.com/openai/v1/chat/completions',
                headers={{
                    'Authorization': 'Bearer {self.api_key.get()}',
                    'Content-Type': 'application/json'
                }},
                json={{
                    'model': '{self.model.get()}',
                    'messages': [
                        {{'role': 'system', 'content': system_prompt}},
                        {{'role': 'user', 'content': question}}
                    ],
                    'max_tokens': 5,
                    'temperature': 0
                }},
                timeout=20
            )
            
            if response.status_code == 200:
                raw_answer = response.json()['choices'][0]['message']['content'].strip()
                
                letter = re.search(r'[abcd]', raw_answer.lower())
                if letter:
                    final_answer = f"{{qnum}}.{{letter.group()}}"
                    self.show_overlay()
                    self.label.config(text=final_answer, fg='lime')
                    self.overlay.after(1500, self.hide_overlay)
                else:
                    self.show_overlay()
                    self.label.config(text="Parse Error", fg='red')
                    self.overlay.after(3000, self.hide_overlay)
            else:
                self.show_overlay()
                self.label.config(text="API Error", fg='red')
                self.overlay.after(3000, self.hide_overlay)
                
        except Exception as e:
            self.show_overlay()
            self.label.config(text="Error", fg='red')
            self.overlay.after(3000, self.hide_overlay)
    
    def run(self):
        self.root.mainloop()

QAOverlay().run()"""
        
        with open("QA_generated.py", "w") as f:
            f.write(script_content)
        
        self.status_label.config(text="Script generated successfully!", fg="green")
    
    def test_script(self):
        if not os.path.exists("QA_generated.py"):
            messagebox.showerror("Error", "Generate script first!")
            return
        
        self.status_label.config(text="Testing script...", fg="blue")
        try:
            subprocess.Popen([sys.executable, "QA_generated.py"])
            self.status_label.config(text="Script launched for testing", fg="green")
        except Exception as e:
            self.status_label.config(text=f"Test failed: {str(e)}", fg="red")
    
    def build_executable(self):
        if not os.path.exists("QA_generated.py"):
            messagebox.showerror("Error", "Generate script first!")
            return
        
        def build():
            self.progress.start()
            self.status_label.config(text="Building executable...", fg="blue")
            
            try:
                # Check if pyinstaller is available
                try:
                    subprocess.run([sys.executable, "-m", "PyInstaller", "--version"], capture_output=True, check=True)
                except (subprocess.CalledProcessError, FileNotFoundError):
                    self.status_label.config(text="Installing PyInstaller...", fg="blue")
                    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
                
                cmd = [
                    sys.executable, "-m", "PyInstaller",
                    "--onefile",
                    "--noconsole",
                    f"--name={self.output_name.get()}"
                ]
                
                if os.path.exists(self.icon_path.get()):
                    cmd.append(f"--icon={self.icon_path.get()}")
                
                cmd.append("QA_generated.py")
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.status_label.config(text="Build completed successfully!", fg="green")
                else:
                    self.status_label.config(text=f"Build failed: {result.stderr}", fg="red")
                    
            except Exception as e:
                self.status_label.config(text=f"Build error: {str(e)}", fg="red")
            finally:
                self.progress.stop()
        
        threading.Thread(target=build, daemon=True).start()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    QABuilder().run()