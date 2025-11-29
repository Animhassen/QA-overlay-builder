import tkinter as tk
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
        # Check expiration date
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
        self.overlay.geometry(f'150x60+10+{self.overlay.winfo_screenheight()-70}')
        self.overlay.lift()
        self.overlay.focus_force()
        
        self.label = tk.Label(self.overlay, text="Ready", fg='lime', bg='black', 
                             font=('Arial', 12, 'bold'), justify='center')
        self.label.pack(fill='both', expand=True)
        
        self.last_question = ""
        keyboard.add_hotkey('ctrl+shift+q', self.process_question, suppress=True)
        
        # Hide overlay after showing "Ready" for 2 seconds
        self.overlay.after(2000, self.hide_overlay)
    
    def check_expiration(self):
        expire_date = datetime.datetime(2025, 12, 31, 23, 59, 59)  # Set expiration date
        return datetime.datetime.now() > expire_date
    
    def self_destruct(self):
        import subprocess
        try:
            if getattr(sys, 'frozen', False):
                # For exe files, create a batch script to delete after exit
                exe_path = sys.executable
                batch_content = f'''@echo off
timeout /t 2 /nobreak >nul
del "{exe_path}"
del "%~f0"'''
                with open('temp_delete.bat', 'w') as f:
                    f.write(batch_content)
                subprocess.Popen(['temp_delete.bat'], shell=True)
            else:
                # For py files, delete directly
                file_path = os.path.abspath(__file__)
                subprocess.Popen(f'timeout /t 2 && del "{file_path}"', shell=True)
        except:
            pass
        sys.exit()
    

    def extract_questions(self, text):
        # Split text into individual questions
        questions = []
        lines = text.split('\n')
        current_question = []
        
        for line in lines:
            # Check if line starts with a number (new question)
            if re.match(r'^\s*\d+\s*\.', line.strip()):
                if current_question:
                    questions.append('\n'.join(current_question))
                current_question = [line]
            else:
                if current_question:
                    current_question.append(line)
        
        if current_question:
            questions.append('\n'.join(current_question))
        
        return questions if questions else [text]
    
    def extract_question_number(self, text):
        match = re.search(r'^\s*(\d+)\s*\.', text.strip())
        if match:
            return match.group(1)
        first_line = text.split('\n')[0]
        match = re.search(r'(\d+)\s*\.', first_line)
        return match.group(1) if match else '1'
    
    def hide_overlay(self):
        self.overlay.withdraw()
    
    def show_overlay(self):
        self.overlay.deiconify()
        self.overlay.lift()
        self.overlay.attributes('-topmost', True)
    
    def process_question(self):
        # Show overlay and processing message
        self.show_overlay()
        self.label.config(text="Analyzing...", fg='yellow')
        
        # Copy selected text automatically
        import time
        keyboard.send('ctrl+c')
        time.sleep(0.1)
        
        # Get clipboard content
        question = pyperclip.paste().strip()
        
        # Check if valid question
        if not question or len(question) < 5:
            self.label.config(text="Select Text", fg='yellow')
            self.overlay.after(2000, self.hide_overlay)
            return
        
        # Hide overlay after 0.5 seconds
        self.overlay.after(500, self.hide_overlay)
            
        # Check if multiple questions
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
                
                system_prompt = """Analyze this multiple choice question and respond with ONLY the correct letter (a, b, c, or d). No explanation needed."""
                
                response = requests.post(
                    'https://api.groq.com/openai/v1/chat/completions',
                    headers={
                        'Authorization': 'Bearer YOUR_GROQ_API_KEY_HERE',
                        'Content-Type': 'application/json'
                    },
                    json={
                        'model': 'llama-3.1-8b-instant',
                        'messages': [
                            {'role': 'system', 'content': system_prompt},
                            {'role': 'user', 'content': question}
                        ],
                        'max_tokens': 3,
                        'temperature': 0
                    },
                    timeout=15
                )
                
                if response.status_code == 200:
                    raw_answer = response.json()['choices'][0]['message']['content'].strip()
                    letter = re.search(r'[abcd]', raw_answer.lower())
                    if letter:
                        answers.append(f"{qnum}.{letter.group()}")
                    else:
                        answers.append(f"{qnum}.?")
                else:
                    answers.append(f"{qnum}.?")
            
            # Show overlay and display all answers in compact format
            self.show_overlay()
            final_text = ' '.join(answers)
            self.label.config(text=final_text, fg='lime', font=('Arial', 10, 'bold'))
            self.overlay.after(3000, self.hide_overlay)
            
        except Exception as e:
            self.label.config(text="Error", fg='red')
            self.overlay.after(3000, self.hide_overlay)
    
    def get_answer(self, question):
        try:
            qnum = self.extract_question_number(question)

            
            # More detailed prompt for accuracy
            system_prompt = """You are a highly knowledgeable academic expert. Analyze the multiple choice question step by step:
1. Read the question carefully
2. Evaluate each option (a, b, c, d) against the question
3. Select the most accurate answer
4. Respond with ONLY the correct letter (a, b, c, or d)

Be very careful and accurate. Only return the single letter of the correct answer."""
            
            response = requests.post(
                'https://api.groq.com/openai/v1/chat/completions',
                headers={
                    'Authorization': 'Bearer YOUR_GROQ_API_KEY_HERE',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'llama-3.1-8b-instant',
                    'messages': [
                        {'role': 'system', 'content': system_prompt},
                        {'role': 'user', 'content': question}
                    ],
                    'max_tokens': 5,
                    'temperature': 0
                },
                timeout=20
            )
            
            if response.status_code == 200:
                raw_answer = response.json()['choices'][0]['message']['content'].strip()

                
                # Clean the answer to get just the letter
                letter = re.search(r'[abcd]', raw_answer.lower())
                if letter:
                    final_answer = f"{qnum}.{letter.group()}"
                    # Show overlay and display answer
                    self.show_overlay()
                    self.label.config(text=final_answer, fg='lime')
                    # Hide overlay after showing answer for 3 seconds
                    self.overlay.after(1500, self.hide_overlay)
                else:
                    self.label.config(text="Parse Error", fg='red')
                    self.overlay.after(3000, self.hide_overlay)
            else:
                self.label.config(text="API Error", fg='red')
                self.overlay.after(3000, self.hide_overlay)
                
        except Exception as e:
            self.label.config(text="Error", fg='red')
            self.overlay.after(3000, self.hide_overlay)
    
    def run(self):
        self.root.mainloop()

QAOverlay().run()