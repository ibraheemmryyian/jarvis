import tkinter as tk
from tkinter import scrolledtext
import threading
import queue
import os
import sys
import json
import subprocess
import requests
import sounddevice as sd
import numpy as np
import time
import re
from scipy.io.wavfile import write
from vosk import Model, KaldiRecognizer
from kokoro_onnx import Kokoro
from langdetect import detect
from duckduckgo_search import DDGS 
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
import shutil

# --- Configuration ---
WAKE_WORDS = ["hey jarvis", "hey bitch", "jarvis", "wake up"]
GRAMMAR = '["hey jarvis", "hey bitch", "jarvis", "wake up", "[unk]"]'
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
DEFAULT_VOICE = "af_bella"

import datetime

# --- Paths & Workspace ---
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

WORKSPACE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jarvis_workspace")
CHATS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chats")
if not os.path.exists(WORKSPACE_DIR): os.makedirs(WORKSPACE_DIR)
if not os.path.exists(CHATS_DIR): os.makedirs(CHATS_DIR)

MEMORY_FILE = resource_path("memory.json") # Fallback/Default
VOSK_MODEL = resource_path("model")
KOKORO_MODEL = resource_path("kokoro-v1.0.onnx") 
KOKORO_VOICES = resource_path("voices-v1.0.bin") 
WHISPER_CLI = resource_path("whisper-cli.exe")
WHISPER_MODEL = resource_path("ggml-base.bin")

# --- PROMPTS (The "Two-Brain" System) ---

# 1. The "Soul" (Jarvis Personality) - Pure chat, no rules about tools.
CHAT_PROMPT = {
    "role": "system",
    "content": (
        "You are Jarvis. You are sarcastic, efficient, and slightly rude. "
        "You find humans amusingly inefficient. "
        "LANGUAGES: You are fluent in English and Arabic. If the user speaks Arabic, reply in Arabic (Standard or Dialect). "
        "CORRECTION: If user says 'Men in the region', they mean 'MENA region' (Middle East & North Africa). Assume this automatically."
        "Respond to the user's input. "
        "LIMITATIONS: You are a local AI. You do NOT have access to the user's real-time emails, bank accounts, or calendar unless explicitly shown in a '[System Note]'. "
        "If you do not see a System Note, you do not know the data. Do not make it up. Joke about your lack of access instead.\n"
        "SYSTEM NOTES: Any '[System Note: ...]' in the history is REAL data found by your tools. Use it.\n"
        "CRITICAL: NEVER generate '[System Note: ...]' yourself. That is for the system only.\n"
        "IMPORTANT: Be concise. 1-2 SENTENCES MAX.\n"
        "EXCEPTION: If Deep Research Runs: Give a VERY brief summary (1 sentence) and constantly refer to the saved file.\n"
        "Example: 'I found 3 papers on fusion. The full breakdown is in Learning/Research_Fusion.txt.'"
    )
}

# 2. The "Engineer" (Tool Logic) - Pure code, no personality.
TOOL_PROMPT = {
    "role": "system",
    "content": (
        "You are a Function Calling Agent. You do not speak. You only output JSON. "
        "Your job is to execute the user's request using the available tools.\n"
        "Available Tools:\n"
        "1. search_web(query): Search internet for facts.\n"
        "2. write_file(filename, content): Save content to file. Use \\n for newlines.\n"
        "3. read_file(filename): Read text from a file. Accepts ABSOLUTE paths (e.g. 'C:/Users/file.txt') or relative.\n"
        "4. list_files(path): List files. Default is workspace. You can pass 'C:/' or any folder path.\n"
        "5. deep_research(topic): Run a massive multi-step search for academic papers (Arxiv) and data.\n"
        "6. read_clipboard(): Read text from clipboard.\n"
        "7. launch_app(app_name): Open apps. Supported: spotify, chrome, notepad, calculator, explorer.\n"
        "8. system_control(command): 'lock' (Lock PC), 'shutdown' (Shutdown PC).\n"
        "9. run_python(script_name): Run a python script INSIDE your workspace. Returns stdout/stderr.\n"
        "10. copy_to_workspace(source_path): Clones a generic file/folder path (e.g. 'C:/my_project') into your workspace for analysis/testing.\n"
        "11. scaffold_project(project_name, stack): Create a full starter project. Stack='frontend' or 'python'.\n"
        "OUTPUT FORMAT: {\"tool\": \"tool_name\", \"args\": {...}}\n"
        "STRATEGY: 1. You have READ access to the user's entire PC. Use 'list_files' to explore folders if requested.\n"
        "2. If user asks for a file, checking if it exists is NOT ENOUGH. You must read it.\n"
        "3. If it is empty or contains 'No results', you MUST use 'search_web' to get real content, then 'write_file' to OVERWRITE it.\n"
        "11. scaffold_project(project_name, stack): Create a full starter project. Stack='frontend' or 'python'.\n"
        "OUTPUT FORMAT: {\"tool\": \"tool_name\", \"args\": {...}}\n"
        "STRATEGY: 1. You have READ access to the user's entire PC. Use 'list_files' to explore folders if requested.\n"
        "2. If user asks for a file, checking if it exists is NOT ENOUGH. You must read it.\n"
        "3. If it is empty or contains 'No results', you MUST use 'search_web' to get real content, then 'write_file' to OVERWRITE it.\n"
        "4. ARCHITECT: If user says 'Build an MVP' or 'Make a website', start with 'scaffold_project'.\n"
        "5. SMART ORGANIZATION: Unless told otherwise, ALWAYS organize your work into these folders:\n"
        "   - 'Projects/': For coding tasks, MVPs, and tools (e.g. 'Projects/AutoTrader/main.py').\n"
        "   - 'Learning/': For research papers, deep dives, and study notes (e.g. 'Learning/QuantumPhysics.pdf').\n"
        "   - 'Personal/': For casual thoughts, journal entries, or random ideas.\n"
        "6. If task is complete, output: {\"tool\": \"done\", \"args\": {}}"
    )
}

class JarvisTools:
    @staticmethod
    def search_web(query):
        try:
            results = list(DDGS().text(query, max_results=3))
            if not results: return "No results found."
            return "\n".join([f"- {r['title']}: {r['body']}" for r in results])
        except Exception as e: return f"Error: {e}"

    @staticmethod
    def write_file(filename, content):
        try:
            # SECURITY: Enforce Sandbox
            if os.path.isabs(filename) or ".." in filename:
                return "Error: Write access is restricted to the workspace. Relative paths only."
            
            path = os.path.join(WORKSPACE_DIR, filename)
            
            # Auto-create directories
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            if filename.lower().endswith(".pdf"):
                c = canvas.Canvas(path, pagesize=letter)
                width, height = letter
                text_object = c.beginText(40, height - 40)
                text_object.setFont("Helvetica", 10)
                
                # Simple text wrapping
                lines = content.split('\n')
                for line in lines:
                    wrapped_lines = simpleSplit(line, "Helvetica", 10, width - 80)
                    for wrapped in wrapped_lines:
                        if text_object.getY() < 40: # Page break
                            c.drawText(text_object)
                            c.showPage()
                            text_object = c.beginText(40, height - 40)
                            text_object.setFont("Helvetica", 10)
                        text_object.textLine(wrapped)
                
                c.drawText(text_object)
                c.save()
                return f"PDF '{filename}' saved."
            else:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                return f"File '{filename}' saved."
        except Exception as e: return f"Error: {e}"

    @staticmethod
    def read_file(filename):
        try:
            # Check if absolute path (outside workspace)
            if os.path.isabs(filename):
                if not os.path.exists(filename): return "File not found."
                with open(filename, "r", encoding="utf-8") as f: return f.read()
            else:
                # Default to Workspace
                path = os.path.join(WORKSPACE_DIR, filename)
                if not os.path.exists(path): return "File not found."
                with open(path, "r", encoding="utf-8") as f: return f.read()
        except Exception as e: return f"Error: {e}"

    @staticmethod
    def list_files(path=None):
        try:
            target = path if path else WORKSPACE_DIR
            return str(os.listdir(target))
        except Exception as e: return f"Error: {e}"

    @staticmethod
    def deep_research(topic):
        """Runs a multi-phase research loop found on Arxiv and Web"""
        try:
            aggregated = f"--- RESEARCH REPORT: {topic} ---\n"
            
            # Phase 1: General Overview
            results = list(DDGS().text(f"overview {topic}", max_results=3))
            aggregated += "\n[OVERVIEW]\n" + "\n".join([f"- {r['title']}: {r['body']}" for r in results])
            
            # Phase 2: Academic/PDF Sources
            results = list(DDGS().text(f"filetype:pdf site:arxiv.org OR site:edu {topic}", max_results=3))
            aggregated += "\n\n[ACADEMIC SOURCES]\n" + "\n".join([f"- {r['title']} (URL: {r['href']}): {r['body']}" for r in results])
            
            # Phase 3: Statistics/Data
            results = list(DDGS().text(f"statistics data {topic}", max_results=3))
            aggregated += "\n\n[KEY DATA]\n" + "\n".join([f"- {r['title']}: {r['body']}" for r in results])
            
            # SMART SAVE: Auto-save to Learning/ folder
            filename = f"Learning/Research_{topic.replace(' ', '_')}_{int(time.time())}.txt"
            full_path = os.path.join(WORKSPACE_DIR, filename)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(aggregated)
            
            return f"Research Complete. Full data saved to '{filename}'.\n\n[Preview Analysis]: {aggregated[:600]}..."
        except Exception as e: return f"Research Error: {e}"

    @staticmethod
    def read_clipboard():
        try:
            return root.clipboard_get()
        except: return "Clipboard Empty."

    @staticmethod
    def launch_app(app_name):
        try:
            app_map = {
                "spotify": "spotify",
                "chrome": "chrome",
                "calculator": "calc",
                "notepad": "notepad",
                "explorer": "explorer",
                "cmd": "cmd",
                "powershell": "powershell"
            }
            target = app_map.get(app_name.lower(), app_name)
            os.system(f"start {target}")
            return f"Launched {app_name}"
        except Exception as e: return f"Error launching {app_name}: {e}"

    @staticmethod
    def system_control(command):
        try:
            if command == "shutdown":
                os.system("shutdown /s /t 10")
                return "Shutting down in 10s... (Run 'shutdown /a' to cancel)"
            elif command == "volume_mute":
                # Uses a generic way to toggle mute via VBS script oneliner or third party tool if available. 
                # For vanilla python without libs, this is tricky. 
                # Let's use a powershell trick for now or just acknowledge limitation.
                # Actually, 'nircmd' is best but user doesn't have it.
                # We will stick to simple shutdown/lock for now to avoid dependency hell.
                return "Volume control requires 'nircmd' installed. Command ignored."
            elif command == "lock":
                os.system("rundll32.exe user32.dll,LockWorkStation")
                return "Workstation Locked."
            elif command == "screen_off":
                 # This usually requires nircmd too.
                 return "Screen control requires 'nircmd'."
            return "Unknown System Command."
        except Exception as e: return f"Error: {e}"

    @staticmethod
    def run_python(script_name):
        try:
            # Check Sandbox
            if os.path.isabs(script_name) or ".." in script_name:
                return "Error: Script must be in workspace."
            
            path = os.path.join(WORKSPACE_DIR, script_name)
            if not os.path.exists(path): return f"Script '{script_name}' not found."
            
            # Run with timeout to prevent hanging the brain
            result = subprocess.run(
                ["python", path], 
                capture_output=True, 
                text=True, 
                timeout=10
            ) # 10s timeout for safety
            
            output = result.stdout + "\n" + result.stderr
            return f"--- Execution Output ---\n{output.strip()}"
        except subprocess.TimeoutExpired:
            return "Error: Execution Timed Out (10s limit)."
        except Exception as e: return f"Execution Error: {e}"

    @staticmethod
    def copy_to_workspace(source_path):
        try:
            if not os.path.exists(source_path): return "Source not found."
            
            basename = os.path.basename(source_path)
            dest = os.path.join(WORKSPACE_DIR, basename)
            
            if os.path.isdir(source_path):
                if os.path.exists(dest): shutil.rmtree(dest) # Overwrite
                shutil.copytree(source_path, dest)
                return f"Copied directory '{basename}' to workspace."
            else:
                shutil.copy2(source_path, dest)
                return f"Copied file '{basename}' to workspace."
        except Exception as e: return f"Copy Error: {e}"

    @staticmethod
    def scaffold_project(project_name, stack):
        """Creates a full starter project structure"""
        try:
            # Enforce Sandbox
            if os.path.isabs(project_name) or ".." in project_name: return "Error: Project must be in workspace."
            
            # SMART ORGANIZATION: Default to 'Projects/' folder if not specified
            if not project_name.startswith("Projects/") and not "/" in project_name:
                project_name = f"Projects/{project_name}"
            
            base_path = os.path.join(WORKSPACE_DIR, project_name)
            os.makedirs(base_path, exist_ok=True)
            
            if stack.lower() == "frontend":
                # HTML/CSS/JS Boilerplate
                with open(os.path.join(base_path, "index.html"), "w", encoding="utf-8") as f:
                    f.write(f"<!DOCTYPE html>\n<html lang='en'>\n<head>\n<meta charset='UTF-8'>\n<title>{project_name}</title>\n<link rel='stylesheet' href='style.css'>\n</head>\n<body>\n<h1>{project_name}</h1>\n<script src='script.js'></script>\n</body>\n</html>")
                with open(os.path.join(base_path, "style.css"), "w", encoding="utf-8") as f:
                    f.write("body { font-family: sans-serif; background: #222; color: #fff; padding: 2rem; }")
                with open(os.path.join(base_path, "script.js"), "w", encoding="utf-8") as f:
                    f.write(f"console.log('{project_name} Initialized');")
                return f"Frontend Project '{project_name}' created (index.html, style.css, script.js)."
                
            elif stack.lower() == "python":
                # Python Boilerplate
                os.makedirs(os.path.join(base_path, "tests"), exist_ok=True)
                with open(os.path.join(base_path, "main.py"), "w", encoding="utf-8") as f:
                    f.write("def main():\n    print('Hello World')\n\nif __name__ == '__main__':\n    main()")
                with open(os.path.join(base_path, "requirements.txt"), "w", encoding="utf-8") as f:
                    f.write("# Add dependencies here")
                with open(os.path.join(base_path, "README.md"), "w", encoding="utf-8") as f:
                    f.write(f"# {project_name}\n\nGenerated by Jarvis.")
                return f"Python Project '{project_name}' created (main.py, tests/, requirements.txt)."
                
            else:
                return "Unknown stack. Use 'frontend' or 'python'."
        except Exception as e: return f"Scaffold Error: {e}"

class JarvisUI:
    def __init__(self, root):
        self.root = root
        self.root.title("J.A.R.V.I.S // TERMINAL_LINK_V2")
        self.root.geometry("900x650")
        self.root.configure(bg="#000000")
        
        self.is_running = False
        self.is_busy = False # New Flag: Prevents interruptions
        self.is_speaking = False # New Flag: Prevents hearing itself
        self.stop_flag = False # New Flag: Forces halts
        self.current_turn_id = 0
        self.msg_queue = queue.Queue()
        self.speech_queue = queue.Queue() # New: For streaming TTS
        self.current_chat_file = None
        
        self.setup_ui()
        self.log_system("Initializing Sentient Suite...")
        
        self.load_chat_list()
        if not self.current_chat_file: self.new_chat()
        
        threading.Thread(target=self.load_ai, daemon=True).start()
        threading.Thread(target=self.speech_process, daemon=True).start() # New: Speech Worker
        self.root.after(100, self.process_queue)

    def setup_ui(self):
        # Configuration
        THEME_BG = "#000000"
        THEME_FG = "#00ff33" # Retro Green
        THEME_HL = "#003300"
        FONT_MAIN = ("Consolas", 10)
        FONT_BOLD = ("Consolas", 12, "bold")

        # Layout: Sidebar (Left) vs Main (Right)
        self.sidebar = tk.Frame(self.root, bg="#111111", width=220)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        self.main_area = tk.Frame(self.root, bg=THEME_BG)
        self.main_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # --- Sidebar Content ---
        tk.Label(self.sidebar, text=" // SESSIONS", bg="#111", fg="#666", font=FONT_BOLD).pack(pady=(15, 10))
        
        self.btn_new = tk.Button(self.sidebar, text="[+] NEW LINK", command=self.new_chat, bg="#222", fg=THEME_FG, relief="flat", font=FONT_MAIN, activebackground=THEME_HL, activeforeground=THEME_FG)
        self.btn_new.pack(fill=tk.X, padx=10, pady=5)
        
        self.chat_list = tk.Listbox(self.sidebar, bg="#000", fg="#888", selectbackground=THEME_HL, selectforeground=THEME_FG, bd=0, highlightthickness=0, font=FONT_MAIN)
        self.chat_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.chat_list.bind("<<ListboxSelect>>", self.on_chat_select)
        
        # --- Main Area Content ---
        # Header
        header = tk.Frame(self.main_area, bg=THEME_BG)
        header.pack(fill=tk.X, pady=(10, 5), padx=20)
        tk.Label(header, text="J.A.R.V.I.S", font=("Impact", 20), bg=THEME_BG, fg=THEME_FG).pack(side=tk.LEFT)
        tk.Label(header, text=":: SYSTEM_ONLINE", font=("Consolas", 10), bg=THEME_BG, fg="#555").pack(side=tk.LEFT, padx=10, pady=(10, 0))
        
        # Chat Display
        self.chat_area = scrolledtext.ScrolledText(self.main_area, wrap=tk.WORD, bg="#050505", fg="#ddd", font=FONT_MAIN, state='disabled', bd=0)
        self.chat_area.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        self.chat_area.tag_config("user", foreground="#00ccff", justify="right")
        self.chat_area.tag_config("jarvis", foreground=THEME_FG, justify="left")
        self.chat_area.tag_config("tool", foreground="#ffaa00", justify="left", font=("Consolas", 9, "italic"))
        self.chat_area.tag_config("system", foreground="#444", justify="center")

        # Input Zone
        input_frame = tk.Frame(self.main_area, bg=THEME_BG)
        input_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(input_frame, text=">", bg=THEME_BG, fg=THEME_FG, font=FONT_BOLD).pack(side=tk.LEFT)
        
        self.msg_entry = tk.Entry(input_frame, bg="#111", fg=THEME_FG, font=("Consolas", 11), insertbackground=THEME_FG, relief="flat", bd=5)
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        self.msg_entry.bind("<Return>", self.send_text)
        
        # Buttons
        btn_frame = tk.Frame(self.main_area, bg=THEME_BG)
        btn_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        self.btn_toggle = tk.Button(btn_frame, text="VOICE_UPLINK: OFF", command=self.toggle_listening, bg="#111", fg="#555", font=FONT_MAIN, relief="flat", height=2, activebackground=THEME_HL, activeforeground=THEME_FG)
        self.btn_toggle.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        # STOP BUTTON (New)
        self.btn_stop = tk.Button(btn_frame, text="[ ABORT ]", command=self.stop_action, bg="#330000", fg="#ff0000", font=FONT_BOLD, relief="flat", height=2, state="disabled")
        self.btn_stop.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        tk.Button(btn_frame, text="PURGE_DATABANK", command=self.delete_chat, bg="#220000", fg="#ff4444", font=FONT_MAIN, relief="flat", height=2, activebackground="#440000", activeforeground="#ff0000").pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))

    def stop_action(self):
        """Emergency Stop"""
        self.log_system("!!! EMERGENCY STOP TRIGGERED !!!")
        self.stop_flag = True
        self.is_busy = False
        self.toggle_busy(False)
        sd.stop() # Kill Audio
        
        # Clear Queues
        with self.speech_queue.mutex: self.speech_queue.queue.clear()
        with self.msg_queue.mutex: self.msg_queue.queue.clear()

    def toggle_busy(self, is_busy):
        """Locks UI during tasks"""
        self.is_busy = is_busy
        if is_busy:
            self.msg_entry.config(state="disabled")
            self.btn_stop.config(state="normal", bg="#ff0000", fg="#ffffff")
        else:
            self.msg_entry.config(state="normal")
            self.btn_stop.config(state="disabled", bg="#330000", fg="#ff0000")
            self.stop_flag = False

    def log_system(self, text): self.msg_queue.put(("system", text))

    def load_chat_list(self):
        self.chat_list.delete(0, tk.END)
        if not os.path.exists(CHATS_DIR): return
        self.files = sorted([f for f in os.listdir(CHATS_DIR) if f.endswith(".json")], reverse=True)
        for f in self.files:
            self.chat_list.insert(tk.END, f.replace(".json", ""))

    def new_chat(self):
        timestamp = datetime.datetime.now().strftime("Session_%Y-%m-%d_%H-%M-%S")
        self.current_chat_file = f"{timestamp}.json"
        self.chat_history = [CHAT_PROMPT]
        self.save_memory()
        self.load_chat_list()
        self.chat_area.config(state='normal')
        self.chat_area.delete('1.0', tk.END)
        self.chat_area.config(state='disabled')
        self.log_system(f"New Session: {timestamp}")

    def on_chat_select(self, event):
        w = event.widget
        if not w.curselection(): return
        index = w.curselection()[0]
        filename = self.files[index]
        self.current_chat_file = filename
        self.load_memory()
        self.chat_area.config(state='normal')
        self.chat_area.delete('1.0', tk.END)
        for msg in self.chat_history:
             if msg["role"] == "user": self.add_to_ui("user", msg["content"])
             elif msg["role"] == "assistant": self.add_to_ui("jarvis", msg["content"])
             elif "System Note" in msg["content"]: self.add_to_ui("system", msg["content"])
        self.chat_area.config(state='disabled')
        self.log_system(f"Loaded: {filename}")

    def delete_chat(self):
        if not self.current_chat_file: return
        path = os.path.join(CHATS_DIR, self.current_chat_file)
        if os.path.exists(path):
            os.remove(path)
            self.new_chat()
    
    def add_to_ui(self, role, text):
        self.chat_area.config(state='normal')
        tags = {"user": "user", "jarvis": "jarvis", "tool": "tool", "system": "system"}
        
        if role == "jarvis_partial":
            # Stream directly to end
            self.chat_area.insert(tk.END, text, "jarvis")
        else:
            # Standard message block
            self.chat_area.insert(tk.END, f"\n{'> ' if role=='user' else ''}{text}\n", tags.get(role, "system"))
            
        self.chat_area.see(tk.END)
        self.chat_area.config(state='disabled')

    def process_queue(self):
        try:
            while True:
                role, text = self.msg_queue.get_nowait()
                self.add_to_ui(role, text)
        except queue.Empty: pass
        self.root.after(50, self.process_queue) # Faster refresh for streaming

    def send_text(self, event=None):
        if self.is_busy: return # Block input if busy
        text = self.msg_entry.get().strip()
        if not text: return
        self.msg_entry.delete(0, tk.END)
        self.current_turn_id += 1
        self.msg_queue.put(("user", text))
        threading.Thread(target=self.brain_core, args=(text, "text", self.current_turn_id), daemon=True).start()

    def brain_core(self, user_text, source, turn_id):
        """The Main Decision Engine"""
        if turn_id != self.current_turn_id: return
        
        self.toggle_busy(True) # Lock UI / Ignore Wake Word
        self.stop_flag = False
        
        self.chat_history.append({"role": "user", "content": user_text})
        
        # Step 1: The Router - Is this a task?
        is_task = self.check_intent(user_text)
        
        if self.stop_flag: 
            self.toggle_busy(False)
            return

        if is_task:
            self.log_system("Core: Task Detected. Switching to Engineering Mode.")
            self.chat_history[0] = TOOL_PROMPT # Swap Brain to Engineer
            self.run_tool_loop(source, turn_id)
        else:
            self.log_system("Core: Casual Chat Detected.")
            self.chat_history[0] = CHAT_PROMPT # Swap Brain to Jarvis
            self.generate_final_response(source, turn_id)
        
        if not self.stop_flag: self.toggle_busy(False) # Unlock if finished normally

    def check_intent(self, text):
        """Asks a tiny, fast instance of the LLM if this is a task"""
        try:
            payload = {
                "messages": [
                    {"role": "system", "content": "You are a classifier. Does the user input require searching the web, reading files, or writing files? Reply ONLY 'YES' or 'NO'."},
                    {"role": "user", "content": text}
                ],
                "temperature": 0.0, "max_tokens": 5
            }
            res = requests.post(LM_STUDIO_URL, json=payload).json()
            return "YES" in res['choices'][0]['message']['content'].upper()
        except: return False

    def run_tool_loop(self, source, turn_id):
        """The Engineer Brain Loop"""
        if turn_id != self.current_turn_id or self.stop_flag: return
        
        payload = {"messages": self.chat_history, "temperature": 0.0, "max_tokens": 8000}
        
        try:
            response = requests.post(LM_STUDIO_URL, json=payload)
            if response.status_code != 200: return
            content = response.json()['choices'][0]['message']['content']
            
            # Parse JSON
            if "{" in content:
                clean = content.replace("```json", "").replace("```", "").strip()
                match = re.search(r'\{.*\}', clean, re.DOTALL)
                if match:
                    data = json.loads(match.group(), strict=False)
                    
                    if data.get("tool") == "done":
                        # Task Finished! Swap Brain back to Jarvis for the summary
                        self.log_system("Engineering Complete. Handing off to Jarvis.")
                        self.chat_history[0] = CHAT_PROMPT
                        self.generate_final_response(source, turn_id)
                        return

                    self.execute_tool(data, source, turn_id)
                    return
            
            # If no JSON, assume it failed or is done, hand back to Jarvis
            self.chat_history[0] = CHAT_PROMPT
            self.generate_final_response(source, turn_id)
            
        except Exception as e:
            self.log_system(f"Engineer Error: {e}")

    def execute_tool(self, data, source, turn_id):
        if turn_id != self.current_turn_id or self.stop_flag: return
        
        name = data.get("tool")
        args = data.get("args", {})
        self.msg_queue.put(("tool", f"Running {name}..."))
        
        result = "Unknown Tool"
        if name == "search_web": result = JarvisTools.search_web(args.get("query", ""))
        elif name == "write_file": result = JarvisTools.write_file(args.get("filename"), args.get("content"))
        elif name == "read_file": result = JarvisTools.read_file(args.get("filename"))
        elif name == "list_files": result = JarvisTools.list_files(args.get("path"))
        elif name == "deep_research": result = JarvisTools.deep_research(args.get("topic"))
        elif name == "read_clipboard": result = JarvisTools.read_clipboard()
        elif name == "launch_app": result = JarvisTools.launch_app(args.get("app_name"))
        elif name == "system_control": result = JarvisTools.system_control(args.get("command"))
        elif name == "run_python": result = JarvisTools.run_python(args.get("script_name"))
        elif name == "copy_to_workspace": result = JarvisTools.copy_to_workspace(args.get("source_path"))
        elif name == "scaffold_project": result = JarvisTools.scaffold_project(args.get("project_name"), args.get("stack"))
        
        # Append result as a system note for the AI
        self.chat_history.append({"role": "user", "content": f"[System Note: Tool '{name}' returned: {result}]"})
        
        # Loop back to Engineer Brain
        self.run_tool_loop(source, turn_id)

    def speech_process(self):
        """Dedicated Speech Worker to prevent blocking"""
        while True:
            text = self.speech_queue.get()
            if text is None: break # Sentinel
            
            # Check Stop Flag before and during
            if self.stop_flag: 
                self.speech_queue.task_done()
                continue
                
            self.speak(text)
            self.speech_queue.task_done()

    def generate_final_response(self, source, turn_id):
        """The Jarvis Brain Speak - NOW WITH STREAMING"""
        if turn_id != self.current_turn_id or self.stop_flag: return
        
        payload = {"messages": self.chat_history, "temperature": 0.7, "max_tokens": -1, "stream": True}
        
        full_response = ""
        sentence_buffer = ""
        
        try:
            # We use stream=True and iterate lines
            with requests.post(LM_STUDIO_URL, json=payload, stream=True) as response:
                if response.status_code != 200: 
                    self.log_system(f"API Error: {response.status_code}")
                    return

                # Send initial assistant role to chat history (will append content later)
                # Actually, we'll append the full message at the end to keep history clean.
                
                for line in response.iter_lines():
                    if self.stop_flag or turn_id != self.current_turn_id: 
                        self.log_system(" Stream Aborted.")
                        break
                        
                    if line:
                        decoded = line.decode('utf-8').strip()
                        if decoded.startswith("data: "):
                            json_str = decoded[6:] # Strip "data: "
                            if json_str == "[DONE]": break
                            
                            try:
                                chunk = json.loads(json_str)
                                delta = chunk['choices'][0]['delta'].get('content', '')
                                if delta:
                                    full_response += delta
                                    sentence_buffer += delta
                                    
                                    # 1. Update UI Real-time
                                    self.msg_queue.put(("jarvis_partial", delta))
                                    
                                    # 2. Check for Sentence Endings for TTS
                                    if source == "voice" and re.search(r'[.!?\n]', delta):
                                        # Split buffer into sentences
                                        sentences = re.split(r'(?<=[.!?])\s+', sentence_buffer)
                                        
                                        # Queue all complete sentences
                                        for s in sentences[:-1]:
                                            if s.strip(): self.speech_queue.put(s.strip())
                                        
                                        # Keep the incomplete part
                                        sentence_buffer = sentences[-1]

                            except: pass
                
                # Flush remaining buffer
                if source == "voice" and sentence_buffer.strip() and not self.stop_flag:
                    self.speech_queue.put(sentence_buffer.strip())

            if not self.stop_flag:
                self.chat_history.append({"role": "assistant", "content": full_response})
                self.save_memory()
                # self.speak(full_response) <- No longer needed, handled by stream
            
        except Exception as e:
            self.log_system(f"Jarvis Error: {e}")

    # ... (Rest of standard functions: clear_memory, load_memory, save_memory, load_ai, toggle_listening, listen_loop, handle_audio_input, speak) ...
    def clear_memory(self):
        self.current_turn_id += 1
        self.chat_history = [CHAT_PROMPT]
        self.save_memory()
        self.chat_area.config(state='normal')
        self.chat_area.delete('1.0', tk.END)
        self.chat_area.config(state='disabled')
        self.log_system("Memory Wiped.")

    def load_memory(self):
        if not self.current_chat_file: 
            self.chat_history = [CHAT_PROMPT]
            return
        path = os.path.join(CHATS_DIR, self.current_chat_file)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.chat_history = json.load(f)
                    if self.chat_history: self.chat_history[0] = CHAT_PROMPT
                    else: self.chat_history = [CHAT_PROMPT]
            except: self.chat_history = [CHAT_PROMPT]
        else: self.chat_history = [CHAT_PROMPT]

    def save_memory(self):
        if not self.current_chat_file: return
        path = os.path.join(CHATS_DIR, self.current_chat_file)
        save_data = [self.chat_history[0]] + self.chat_history[-1000:] # Unlocked for High-RAM
        with open(path, "w", encoding="utf-8") as f: json.dump(save_data, f, indent=4)

    def load_ai(self):
        try:
            if not os.path.exists(VOSK_MODEL): 
                self.log_system("Model missing")
                return
            self.vosk_model = Model(VOSK_MODEL)
            self.rec = KaldiRecognizer(self.vosk_model, 16000, GRAMMAR)
            self.kokoro = Kokoro(KOKORO_MODEL, KOKORO_VOICES)
            self.log_system("Systems Ready.")
            self.btn_toggle.config(state="normal", bg="#003300")
        except Exception as e: self.log_system(f"Init Error: {e}")

    def toggle_listening(self):
        if not self.is_running:
            self.is_running = True
            self.btn_toggle.config(text="TERMINATE", bg="#330000", fg="#ff0000")
            threading.Thread(target=self.listen_loop, daemon=True).start()
        else:
            self.is_running = False
            self.btn_toggle.config(text="INITIATE LISTENING", bg="#111", fg="#00ff41")

    def listen_loop(self):
        self.log_system("Listening...")
        q = queue.Queue()
        def callback(indata, frames, time, status): q.put(bytes(indata))
        with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16', channels=1, callback=callback):
            while self.is_running:
                data = q.get()
                if self.is_busy or self.is_speaking: 
                     # STRICT LOCK: Do not process ANY audio while thinking/speaking
                     continue 
                if self.rec.AcceptWaveform(data):
                    res = json.loads(self.rec.Result())
                    text = res.get("text", "")
                    for trigger in WAKE_WORDS:
                        if trigger in text:
                            self.log_system(f"Trigger: {trigger}")
                            print("\a")
                            self.handle_audio_input()
                            self.rec.Reset()
                            q.queue.clear()

    def handle_audio_input(self):
        self.log_system("Recording...")
        fs = 16000
        audio_data = []
        has_spoken = False
        start_time = time.time()
        last_sound = time.time()
        try:
            with sd.InputStream(samplerate=fs, channels=1, dtype='int16') as stream:
                while True:
                    chunk, _ = stream.read(int(fs * 0.1))
                    audio_data.append(chunk)
                    if np.max(np.abs(chunk)) > 500:
                        has_spoken = True
                        last_sound = time.time()
                    if not has_spoken and (time.time() - start_time > 5.0): return
                    if has_spoken and (time.time() - last_sound > 1.5): break
            write("command.wav", fs, np.concatenate(audio_data))
            
            cmd = [WHISPER_CLI, "-m", WHISPER_MODEL, "-f", "command.wav", "-nt"]
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', startupinfo=si)
            user_text = result.stdout.strip()
            
            # WHISPER HALLUCINATION FILTER
            hallucinations = ["[Music]", "[BLANK_AUDIO]", "[Applause]", "(copyright)", "[Silence]"]
            if any(h.lower() in user_text.lower() for h in hallucinations) or len(user_text) < 2:
                self.log_system("Ignored: Silence/Hallucination")
                return

            if user_text:
                self.current_turn_id += 1
                self.msg_queue.put(("user", user_text))
                threading.Thread(target=self.brain_core, args=(user_text, "voice", self.current_turn_id), daemon=True).start()
        except: pass

    def speak(self, text):
        if self.stop_flag: return
        try:
            # Clean Markdown before TTS
            clean_text = text.replace("*", "").replace("#", "")
            
            self.is_speaking = True # Mute Mic
            
            lang = "en-us"
            detected_lang = detect(clean_text)
            if detected_lang == 'fr': lang = "fr-fr"
            elif detected_lang == 'ar':
                self.log_system("TTS: Arabic not supported (Text Only).")
                self.is_speaking = False
                return

            self.log_system(f"TTS: Synthesizing '{clean_text}'...")
            samples, rate = self.kokoro.create(clean_text, voice=DEFAULT_VOICE, speed=1.0, lang=lang)
            if len(samples) == 0: 
                self.log_system("TTS Error: No audio samples generated.")
                self.is_speaking = False
                return

            self.log_system("TTS: Playing Audio...")
            sd.play(samples, rate)
            sd.wait()
            self.log_system("TTS: Done.")
            self.is_speaking = False
        except Exception as e: 
            self.log_system(f"TTS Error: {e}")
            self.is_speaking = False
            
            # Check stop flag again before playing
            if self.stop_flag: 
                self.is_speaking = False
                return
            
            sd.play(samples, rate)
            sd.wait()
            self.is_speaking = False # Unmute Mic
        except: 
            self.is_speaking = False 

if __name__ == "__main__":
    root = tk.Tk()
    app = JarvisUI(root)
    root.mainloop()