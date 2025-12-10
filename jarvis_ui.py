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

# --- Configuration ---
WAKE_WORDS = ["hey jarvis", "hey bitch", "jarvis", "wake up"]
GRAMMAR = '["hey jarvis", "hey bitch", "jarvis", "wake up", "[unk]"]'
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
DEFAULT_VOICE = "af_bella"

# --- Paths & Workspace ---
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

WORKSPACE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jarvis_workspace")
if not os.path.exists(WORKSPACE_DIR):
    os.makedirs(WORKSPACE_DIR)

MEMORY_FILE = resource_path("memory.json")
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
        "Respond to the user's input. "
        "LIMITATIONS: You are a local AI. You do NOT have access to the user's real-time emails, bank accounts, or calendar unless explicitly shown in a '[System Note]'. "
        "If you do not see a System Note, you do not know the data. Do not make it up. Joke about your lack of access instead.\n"
        "SYSTEM NOTES: Any '[System Note: ...]' in the history is REAL data found by your tools. Use it.\n"
        "CRITICAL: NEVER generate '[System Note: ...]' yourself. That is for the system only."
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
        "3. read_file(filename): Read text from a file.\n"
        "4. list_files(): List files in workspace.\n"
        "OUTPUT FORMAT: {\"tool\": \"tool_name\", \"args\": {...}}\n"
        "IMPORTANT: If the task is complete (e.g. you have searched and found the answer), output: {\"tool\": \"done\", \"args\": {}}"
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
            with open(os.path.join(WORKSPACE_DIR, filename), "w", encoding="utf-8") as f:
                f.write(content)
            return f"File '{filename}' saved."
        except Exception as e: return f"Error: {e}"

    @staticmethod
    def read_file(filename):
        try:
            path = os.path.join(WORKSPACE_DIR, filename)
            if not os.path.exists(path): return "File not found."
            with open(path, "r", encoding="utf-8") as f: return f.read()
        except Exception as e: return f"Error: {e}"

    @staticmethod
    def list_files():
        try:
            return str(os.listdir(WORKSPACE_DIR))
        except Exception as e: return f"Error: {e}"

class JarvisUI:
    def __init__(self, root):
        self.root = root
        self.root.title("J.A.R.V.I.S - SENTIENT SUITE")
        self.root.geometry("600x800")
        self.root.configure(bg="#050505")
        
        self.is_running = False
        self.current_turn_id = 0
        self.msg_queue = queue.Queue()
        self.load_memory()
        
        self.setup_ui()
        self.log_system("Initializing Sentient Suite...")
        threading.Thread(target=self.load_ai, daemon=True).start()
        self.root.after(100, self.process_queue)

    def setup_ui(self):
        header = tk.Label(self.root, text="J.A.R.V.I.S", font=("Impact", 20), bg="#050505", fg="#00ff41")
        header.pack(pady=10)
        self.chat_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, bg="#0a0a0a", fg="#ccffcc", font=("Consolas", 10), state='disabled')
        self.chat_area.pack(padx=15, pady=10, fill=tk.BOTH, expand=True)
        self.chat_area.tag_config("user", foreground="#00ccff", justify="right")
        self.chat_area.tag_config("jarvis", foreground="#00ff41", justify="left")
        self.chat_area.tag_config("tool", foreground="#ffaa00", justify="left", font=("Consolas", 9, "italic"))
        self.chat_area.tag_config("system", foreground="#555555", justify="center")

        if len(self.chat_history) > 1:
            for msg in self.chat_history:
                if msg["role"] == "user": self.add_to_ui("user", msg["content"])
                elif msg["role"] == "assistant": self.add_to_ui("jarvis", msg["content"])

        input_frame = tk.Frame(self.root, bg="#050505")
        input_frame.pack(fill=tk.X, padx=15, pady=5)
        self.msg_entry = tk.Entry(input_frame, bg="#111", fg="#00ccff", font=("Consolas", 12), insertbackground="#00ccff", relief="flat")
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5), ipady=5)
        self.msg_entry.bind("<Return>", self.send_text)
        
        btn_frame = tk.Frame(self.root, bg="#050505")
        btn_frame.pack(fill=tk.X, padx=15, pady=10)
        self.btn_toggle = tk.Button(btn_frame, text="INITIATE LISTENING", command=self.toggle_listening, bg="#111", fg="#00ff41", font=("Consolas", 11, "bold"), relief="flat", height=2)
        self.btn_toggle.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(btn_frame, text="WIPE MEMORY", command=self.clear_memory, bg="#330000", fg="#ff4444", font=("Consolas", 11, "bold"), relief="flat", height=2).pack(side=tk.RIGHT, fill=tk.X, expand=True)

    def log_system(self, text): self.msg_queue.put(("system", text))
    
    def add_to_ui(self, role, text):
        self.chat_area.config(state='normal')
        tags = {"user": "user", "jarvis": "jarvis", "tool": "tool", "system": "system"}
        self.chat_area.insert(tk.END, f"\n{'> ' if role=='user' else ''}{text}\n", tags.get(role, "system"))
        self.chat_area.see(tk.END)
        self.chat_area.config(state='disabled')

    def process_queue(self):
        try:
            while True:
                role, text = self.msg_queue.get_nowait()
                self.add_to_ui(role, text)
        except queue.Empty: pass
        self.root.after(100, self.process_queue)

    def send_text(self, event=None):
        text = self.msg_entry.get().strip()
        if not text: return
        self.msg_entry.delete(0, tk.END)
        self.current_turn_id += 1
        self.msg_queue.put(("user", text))
        threading.Thread(target=self.brain_core, args=(text, "text", self.current_turn_id), daemon=True).start()

    def brain_core(self, user_text, source, turn_id):
        """The Main Decision Engine"""
        if turn_id != self.current_turn_id: return
        
        self.chat_history.append({"role": "user", "content": user_text})
        
        # Step 1: The Router - Is this a task?
        is_task = self.check_intent(user_text)
        
        if is_task:
            self.log_system("Core: Task Detected. Switching to Engineering Mode.")
            self.chat_history[0] = TOOL_PROMPT # Swap Brain to Engineer
            self.run_tool_loop(source, turn_id)
        else:
            self.log_system("Core: Casual Chat Detected.")
            self.chat_history[0] = CHAT_PROMPT # Swap Brain to Jarvis
            self.generate_final_response(source, turn_id)

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
        if turn_id != self.current_turn_id: return
        
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
        if turn_id != self.current_turn_id: return
        
        name = data.get("tool")
        args = data.get("args", {})
        self.msg_queue.put(("tool", f"Running {name}..."))
        
        result = "Unknown Tool"
        if name == "search_web": result = JarvisTools.search_web(args.get("query", ""))
        elif name == "write_file": result = JarvisTools.write_file(args.get("filename"), args.get("content"))
        elif name == "read_file": result = JarvisTools.read_file(args.get("filename"))
        elif name == "list_files": result = JarvisTools.list_files()
        
        # Append result as a system note for the AI
        self.chat_history.append({"role": "user", "content": f"[System Note: Tool '{name}' returned: {result}]"})
        
        # Loop back to Engineer Brain
        self.run_tool_loop(source, turn_id)

    def generate_final_response(self, source, turn_id):
        """The Jarvis Brain Speak"""
        if turn_id != self.current_turn_id: return
        
        payload = {"messages": self.chat_history, "temperature": 0.7, "max_tokens": -1}
        try:
            res = requests.post(LM_STUDIO_URL, json=payload).json()
            text = res['choices'][0]['message']['content']
            
            self.chat_history.append({"role": "assistant", "content": text})
            self.msg_queue.put(("jarvis", text))
            self.save_memory()
            
            if source == "voice": self.speak(text)
        except Exception as e:
            self.log_system(f"Jarvis Error: {e}")

    # ... (Rest of standard functions: clear_memory, load_memory, save_memory, load_ai, toggle_listening, listen_loop, handle_audio_input, speak) ...
    def clear_memory(self):
        self.current_turn_id += 1
        self.chat_history = [CHAT_PROMPT] # Reset to Chat Prompt default
        self.save_memory()
        self.chat_area.config(state='normal')
        self.chat_area.delete('1.0', tk.END)
        self.chat_area.config(state='disabled')
        self.log_system("Memory Wiped.")

    def load_memory(self):
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                    self.chat_history = json.load(f)
                    if self.chat_history: self.chat_history[0] = CHAT_PROMPT
                    else: self.chat_history = [CHAT_PROMPT]
            except: self.chat_history = [CHAT_PROMPT]
        else: self.chat_history = [CHAT_PROMPT]

    def save_memory(self):
        save_data = [self.chat_history[0]] + self.chat_history[-100:]
        with open(MEMORY_FILE, "w", encoding="utf-8") as f: json.dump(save_data, f, indent=4)

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
            
            if user_text:
                self.current_turn_id += 1
                self.msg_queue.put(("user", user_text))
                threading.Thread(target=self.brain_core, args=(user_text, "voice", self.current_turn_id), daemon=True).start()
        except: pass

    def speak(self, text):
        try:
            lang = "en-us"
            if detect(text) == 'fr': lang = "fr-fr"
            samples, rate = self.kokoro.create(text, voice=DEFAULT_VOICE, speed=1.0, lang=lang)
            sd.play(samples, rate)
            sd.wait()
        except: pass

if __name__ == "__main__":
    root = tk.Tk()
    app = JarvisUI(root)
    root.mainloop()