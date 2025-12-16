"""
Jarvis v2 UI - Terminal Interface
Modernized matrix aesthetic with multi-agent integration.
"""
import tkinter as tk
from tkinter import scrolledtext, ttk
import threading
import queue
import os
import sys
import json
import datetime
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import warnings
warnings.filterwarnings("ignore")

# Voice imports (optional)
try:
    from vosk import Model, KaldiRecognizer
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False

try:
    from kokoro_onnx import Kokoro
    KOKORO_AVAILABLE = True
except ImportError:
    KOKORO_AVAILABLE = False

# Agent imports
from agents import orchestrator, context, router, get_queue_status
from agents.config import LM_STUDIO_URL, WORKSPACE_DIR

# --- Paths ---
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

CHATS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chats")
os.makedirs(CHATS_DIR, exist_ok=True)

VOSK_MODEL = resource_path("model")
KOKORO_MODEL = resource_path("kokoro-v1.0.onnx")
KOKORO_VOICES = resource_path("voices-v1.0.bin")


class JarvisUI:
    """
    Jarvis v2 Terminal Interface
    Enhanced matrix aesthetic with multi-agent integration.
    """
    
    # --- Theme Configuration ---
    THEME = {
        "bg": "#0a0a0a",
        "bg_dark": "#050505",
        "bg_sidebar": "#0d0d0d",
        "fg_primary": "#00ff41",      # Matrix green
        "fg_secondary": "#00cc33",
        "fg_dim": "#336633",
        "fg_user": "#00bfff",         # Cyan for user
        "fg_tool": "#ff9500",         # Orange for tools
        "fg_error": "#ff3333",
        "fg_muted": "#444444",
        "accent": "#00ff41",
        "danger": "#ff0000",
    }
    
    FONTS = {
        "main": ("Consolas", 10),
        "bold": ("Consolas", 11, "bold"),
        "header": ("Consolas", 16, "bold"),
        "small": ("Consolas", 9),
        "mono": ("Cascadia Mono", 10),
    }

    def __init__(self, root):
        self.root = root
        self.root.title("J.A.R.V.I.S // NEXUS_V2")
        self.root.geometry("1100x750")
        self.root.configure(bg=self.THEME["bg"])
        self.root.minsize(900, 600)
        
        # State
        self.is_running = False
        self.is_busy = False
        self.is_speaking = False
        self.stop_flag = False
        self.current_turn_id = 0
        self.msg_queue = queue.Queue()
        self.speech_queue = queue.Queue()
        self.current_chat_file = None
        self.chat_history = []
        
        # AI Models (lazy load)
        self.recognizer = None
        self.tts = None
        
        self._setup_ui()
        self._log_system("NEXUS_V2 :: Initializing...")
        
        self.load_chat_list()
        if not self.current_chat_file:
            self.new_chat()
        
        # Background threads
        threading.Thread(target=self._load_ai, daemon=True).start()
        threading.Thread(target=self._speech_worker, daemon=True).start()
        self.root.after(50, self._process_queue)

    def _setup_ui(self):
        """Build the terminal interface."""
        T = self.THEME
        F = self.FONTS
        
        # --- Layout: Sidebar | Main | Status ---
        self.sidebar = tk.Frame(self.root, bg=T["bg_sidebar"], width=240)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)
        
        self.main_area = tk.Frame(self.root, bg=T["bg"])
        self.main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.status_bar = tk.Frame(self.root, bg=T["bg_dark"], width=200)
        self.status_bar.pack(side=tk.RIGHT, fill=tk.Y)
        self.status_bar.pack_propagate(False)
        
        # === SIDEBAR ===
        self._build_sidebar()
        
        # === MAIN AREA ===
        self._build_main()
        
        # === STATUS BAR ===
        self._build_status()

    def _build_sidebar(self):
        """Session list and controls."""
        T = self.THEME
        F = self.FONTS
        
        # Header
        header = tk.Frame(self.sidebar, bg=T["bg_sidebar"])
        header.pack(fill=tk.X, pady=(15, 10), padx=10)
        tk.Label(header, text="// SESSIONS", bg=T["bg_sidebar"], fg=T["fg_muted"], 
                 font=F["bold"]).pack(anchor="w")
        
        # New session button
        self.btn_new = tk.Button(
            self.sidebar, text="+ NEW_LINK", command=self.new_chat,
            bg=T["bg_dark"], fg=T["fg_primary"], relief="flat", font=F["main"],
            activebackground=T["fg_dim"], activeforeground=T["fg_primary"],
            cursor="hand2", bd=0, padx=10, pady=8
        )
        self.btn_new.pack(fill=tk.X, padx=10, pady=5)
        
        # Session list
        self.chat_list = tk.Listbox(
            self.sidebar, bg=T["bg_dark"], fg=T["fg_muted"], 
            selectbackground=T["fg_dim"], selectforeground=T["fg_primary"],
            bd=0, highlightthickness=0, font=F["small"], activestyle="none"
        )
        self.chat_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.chat_list.bind("<<ListboxSelect>>", self._on_chat_select)
        
        # Delete button
        tk.Button(
            self.sidebar, text="PURGE", command=self.delete_chat,
            bg=T["bg_dark"], fg=T["fg_error"], relief="flat", font=F["small"],
            activebackground="#330000", cursor="hand2", bd=0, pady=5
        ).pack(fill=tk.X, padx=10, pady=(5, 15))

    def _build_main(self):
        """Chat display and input."""
        T = self.THEME
        F = self.FONTS
        
        # Header bar
        header = tk.Frame(self.main_area, bg=T["bg"])
        header.pack(fill=tk.X, pady=(15, 10), padx=20)
        
        tk.Label(header, text="J.A.R.V.I.S", font=F["header"], 
                 bg=T["bg"], fg=T["fg_primary"]).pack(side=tk.LEFT)
        
        self.status_label = tk.Label(
            header, text=":: ONLINE", font=F["small"],
            bg=T["bg"], fg=T["fg_dim"]
        )
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # Chat display with scrollbar
        chat_frame = tk.Frame(self.main_area, bg=T["bg_dark"])
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        self.chat_area = scrolledtext.ScrolledText(
            chat_frame, wrap=tk.WORD, bg=T["bg_dark"], fg="#cccccc",
            font=F["main"], state='disabled', bd=0, padx=10, pady=10,
            insertbackground=T["fg_primary"]
        )
        self.chat_area.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags
        self.chat_area.tag_config("user", foreground=T["fg_user"])
        self.chat_area.tag_config("jarvis", foreground=T["fg_primary"])
        self.chat_area.tag_config("tool", foreground=T["fg_tool"], font=F["small"])
        self.chat_area.tag_config("system", foreground=T["fg_muted"], font=F["small"])
        self.chat_area.tag_config("error", foreground=T["fg_error"])
        
        # Input area
        input_frame = tk.Frame(self.main_area, bg=T["bg"])
        input_frame.pack(fill=tk.X, padx=20, pady=(10, 5))
        
        tk.Label(input_frame, text=">", bg=T["bg"], fg=T["fg_primary"], 
                 font=F["bold"]).pack(side=tk.LEFT)
        
        self.msg_entry = tk.Entry(
            input_frame, bg=T["bg_dark"], fg=T["fg_primary"], 
            font=F["main"], insertbackground=T["fg_primary"],
            relief="flat", bd=8
        )
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        self.msg_entry.bind("<Return>", self._send_text)
        self.msg_entry.focus_set()
        
        # Control buttons
        btn_frame = tk.Frame(self.main_area, bg=T["bg"])
        btn_frame.pack(fill=tk.X, padx=20, pady=(5, 20))
        
        self.btn_voice = tk.Button(
            btn_frame, text="VOICE: OFF", command=self._toggle_listening,
            bg=T["bg_dark"], fg=T["fg_muted"], relief="flat", font=F["main"],
            width=15, cursor="hand2", bd=0, pady=8
        )
        self.btn_voice.pack(side=tk.LEFT, padx=(0, 5))
        
        self.btn_stop = tk.Button(
            btn_frame, text="[ ABORT ]", command=self._stop_action,
            bg="#1a0000", fg=T["fg_error"], relief="flat", font=F["bold"],
            width=12, state="disabled", cursor="hand2", bd=0, pady=8
        )
        self.btn_stop.pack(side=tk.LEFT, padx=5)
        
        self.btn_autonomous = tk.Button(
            btn_frame, text="AUTONOMOUS", command=self._start_autonomous,
            bg=T["bg_dark"], fg=T["fg_secondary"], relief="flat", font=F["main"],
            width=15, cursor="hand2", bd=0, pady=8
        )
        self.btn_autonomous.pack(side=tk.RIGHT, padx=(5, 0))

    def _build_status(self):
        """Right status panel showing agent states."""
        T = self.THEME
        F = self.FONTS
        
        # Header
        tk.Label(self.status_bar, text="// STATUS", bg=T["bg_dark"], 
                 fg=T["fg_muted"], font=F["bold"]).pack(pady=(15, 10), anchor="w", padx=10)
        
        # Agent status indicators
        self.agent_labels = {}
        agents = ["ROUTER", "RESEARCH", "CODER", "OPS"]
        
        for agent in agents:
            frame = tk.Frame(self.status_bar, bg=T["bg_dark"])
            frame.pack(fill=tk.X, padx=10, pady=2)
            
            indicator = tk.Label(frame, text="●", bg=T["bg_dark"], fg=T["fg_muted"], font=F["small"])
            indicator.pack(side=tk.LEFT)
            
            label = tk.Label(frame, text=agent, bg=T["bg_dark"], fg=T["fg_muted"], font=F["small"])
            label.pack(side=tk.LEFT, padx=5)
            
            self.agent_labels[agent] = indicator
        
        # Separator
        tk.Frame(self.status_bar, bg=T["fg_dim"], height=1).pack(fill=tk.X, padx=10, pady=15)
        
        # Context info
        tk.Label(self.status_bar, text="// CONTEXT", bg=T["bg_dark"], 
                 fg=T["fg_muted"], font=F["bold"]).pack(anchor="w", padx=10)
        
        self.context_label = tk.Label(
            self.status_bar, text="No active task", bg=T["bg_dark"],
            fg=T["fg_dim"], font=F["small"], wraplength=180, justify="left"
        )
        self.context_label.pack(anchor="w", padx=10, pady=5)
        
        # Separator
        tk.Frame(self.status_bar, bg=T["fg_dim"], height=1).pack(fill=tk.X, padx=10, pady=10)
        
        # Queue status
        tk.Label(self.status_bar, text="// QUEUE", bg=T["bg_dark"], 
                 fg=T["fg_muted"], font=F["bold"]).pack(anchor="w", padx=10)
        
        self.queue_pending_label = tk.Label(
            self.status_bar, text="Pending: 0", bg=T["bg_dark"],
            fg=T["fg_dim"], font=F["small"]
        )
        self.queue_pending_label.pack(anchor="w", padx=10, pady=2)
        
        self.queue_status_label = tk.Label(
            self.status_bar, text="Worker: Idle", bg=T["bg_dark"],
            fg=T["fg_dim"], font=F["small"]
        )
        self.queue_status_label.pack(anchor="w", padx=10, pady=2)
        
        self.queue_current_label = tk.Label(
            self.status_bar, text="", bg=T["bg_dark"],
            fg=T["fg_secondary"], font=F["small"], wraplength=180, justify="left"
        )
        self.queue_current_label.pack(anchor="w", padx=10, pady=2)
        
        # Start queue status updater
        self.root.after(2000, self._update_queue_status)

    # --- Agent Integration ---
    
    def _set_agent_active(self, agent_name: str, active: bool = True):
        """Update agent status indicator."""
        if agent_name.upper() in self.agent_labels:
            color = self.THEME["fg_primary"] if active else self.THEME["fg_muted"]
            self.agent_labels[agent_name.upper()].config(fg=color)

    def _update_context_display(self):
        """Show current task from context."""
        try:
            task = context.read_active_task()
            if task and "Objective" in task:
                # Extract first line of objective
                lines = task.split("\n")
                for line in lines:
                    if line.strip() and not line.startswith("#"):
                        self.context_label.config(text=line[:50] + "...")
                        return
            self.context_label.config(text="No active task")
        except:
            self.context_label.config(text="No active task")
    
    def _update_queue_status(self):
        """Update queue status display periodically."""
        try:
            status = get_queue_status()
            pending = status.get("pending", 0)
            is_busy = status.get("is_busy", False)
            
            self.queue_pending_label.config(
                text=f"Pending: {pending}",
                fg=self.THEME["fg_primary"] if pending > 0 else self.THEME["fg_dim"]
            )
            
            if is_busy:
                self.queue_status_label.config(text="Worker: RUNNING", fg=self.THEME["fg_tool"])
                current_id = status.get("current_task_id")
                if current_id:
                    self.queue_current_label.config(text=f"Task #{current_id}")
            else:
                self.queue_status_label.config(text="Worker: Idle", fg=self.THEME["fg_dim"])
                self.queue_current_label.config(text="")
                
        except Exception as e:
            pass
        
        # Refresh every 2 seconds
        self.root.after(2000, self._update_queue_status)

    # --- Core Functions ---
    
    def _log_system(self, text):
        self.msg_queue.put(("system", text))
    
    def _log_tool(self, text):
        self.msg_queue.put(("tool", text))
    
    def _log_jarvis(self, text):
        self.msg_queue.put(("jarvis", text))
    
    def _process_queue(self):
        """Process messages from background threads."""
        try:
            while True:
                role, text = self.msg_queue.get_nowait()
                self._add_to_ui(role, text)
        except queue.Empty:
            pass
        self.root.after(50, self._process_queue)
    
    def _add_to_ui(self, role, text):
        """Add message to chat display."""
        self.chat_area.config(state='normal')
        
        if role == "user":
            self.chat_area.insert(tk.END, f"\n> {text}\n", "user")
        elif role == "jarvis":
            self.chat_area.insert(tk.END, f"\n{text}\n", "jarvis")
        elif role == "tool":
            self.chat_area.insert(tk.END, f"[{text}]\n", "tool")
        else:
            self.chat_area.insert(tk.END, f"  {text}\n", "system")
        
        self.chat_area.see(tk.END)
        self.chat_area.config(state='disabled')
    
    def _toggle_busy(self, is_busy):
        """Lock/unlock UI during operations."""
        self.is_busy = is_busy
        if is_busy:
            self.msg_entry.config(state="disabled")
            self.btn_stop.config(state="normal", bg="#ff0000", fg="#ffffff")
            self.status_label.config(text=":: PROCESSING", fg=self.THEME["fg_tool"])
        else:
            self.msg_entry.config(state="normal")
            self.btn_stop.config(state="disabled", bg="#1a0000", fg=self.THEME["fg_error"])
            self.status_label.config(text=":: ONLINE", fg=self.THEME["fg_dim"])
            self.stop_flag = False
            # Reset agent indicators
            for label in self.agent_labels.values():
                label.config(fg=self.THEME["fg_muted"])
    
    def _stop_action(self):
        """Emergency stop."""
        self._log_system("!!! ABORT TRIGGERED !!!")
        self.stop_flag = True
        self._toggle_busy(False)
        sd.stop()
        with self.speech_queue.mutex:
            self.speech_queue.queue.clear()
    
    def _send_text(self, event=None):
        """Handle text input."""
        if self.is_busy:
            return
        
        text = self.msg_entry.get().strip()
        if not text:
            return
        
        self.msg_entry.delete(0, tk.END)
        self.current_turn_id += 1
        self.msg_queue.put(("user", text))
        
        # Add to history
        self.chat_history.append({"role": "user", "content": text})
        self.save_chat()
        
        # Process with agents
        threading.Thread(
            target=self._process_with_agents, 
            args=(text, self.current_turn_id), 
            daemon=True
        ).start()
    
    def _process_with_agents(self, text: str, turn_id: int):
        """Route and process with multi-agent system."""
        if turn_id != self.current_turn_id:
            return
        
        self._toggle_busy(True)
        
        def progress_callback(msg):
            self._log_tool(msg)
            # Highlight active agent
            for agent in ["ROUTER", "RESEARCH", "CODER", "OPS"]:
                if agent.lower() in msg.lower():
                    self._set_agent_active(agent, True)
        
        try:
            # Set router active
            self._set_agent_active("ROUTER", True)
            self._update_context_display()
            
            # Execute via orchestrator
            result = orchestrator.execute(text, callback=progress_callback)
            
            # Display result
            if isinstance(result, dict):
                output = result.get("result", str(result))
            else:
                output = str(result)
            
            self._log_jarvis(output)
            
            # Save to history
            self.chat_history.append({"role": "assistant", "content": output})
            self.save_chat()
            
        except Exception as e:
            self._log_system(f"Error: {e}")
        
        finally:
            self._toggle_busy(False)
            self._update_context_display()
    
    def _start_autonomous(self):
        """Start autonomous mode dialog."""
        # Simple input dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Autonomous Mode")
        dialog.geometry("500x200")
        dialog.configure(bg=self.THEME["bg"])
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(
            dialog, text="Describe your business idea:", 
            bg=self.THEME["bg"], fg=self.THEME["fg_primary"],
            font=self.FONTS["bold"]
        ).pack(pady=(20, 10))
        
        entry = tk.Entry(
            dialog, bg=self.THEME["bg_dark"], fg=self.THEME["fg_primary"],
            font=self.FONTS["main"], width=50
        )
        entry.pack(pady=10, padx=20, fill=tk.X)
        entry.focus_set()
        
        def start():
            idea = entry.get().strip()
            if idea:
                dialog.destroy()
                self._log_system("Starting AUTONOMOUS mode...")
                threading.Thread(
                    target=self._run_autonomous, args=(idea,), daemon=True
                ).start()
        
        tk.Button(
            dialog, text="INITIATE", command=start,
            bg=self.THEME["fg_primary"], fg=self.THEME["bg"],
            font=self.FONTS["bold"], relief="flat", cursor="hand2"
        ).pack(pady=20)
        
        entry.bind("<Return>", lambda e: start())
    
    def _run_autonomous(self, idea: str):
        """Run full autonomous pipeline."""
        self._toggle_busy(True)
        
        def callback(msg):
            self._log_tool(msg)
        
        try:
            result = orchestrator.execute_autonomous(idea, progress_callback=callback)
            
            # Display summary
            self._log_jarvis("=== AUTONOMOUS RUN COMPLETE ===")
            self._log_jarvis(result.get("research", {}).get("synthesis", "")[:500])
            
            if result.get("errors"):
                for err in result["errors"]:
                    self._log_system(f"Error: {err}")
        
        except Exception as e:
            self._log_system(f"Autonomous error: {e}")
        
        finally:
            self._toggle_busy(False)

    # --- Session Management ---
    
    def load_chat_list(self):
        self.chat_list.delete(0, tk.END)
        if not os.path.exists(CHATS_DIR):
            return
        self.files = sorted([f for f in os.listdir(CHATS_DIR) if f.endswith(".json")], reverse=True)
        for f in self.files:
            self.chat_list.insert(tk.END, f.replace(".json", ""))
    
    def save_chat(self):
        if not self.current_chat_file:
            return
        path = os.path.join(CHATS_DIR, self.current_chat_file)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.chat_history, f, indent=2)
    
    def new_chat(self):
        timestamp = datetime.datetime.now().strftime("Session_%Y-%m-%d_%H-%M-%S")
        self.current_chat_file = f"{timestamp}.json"
        self.chat_history = []
        self.save_chat()
        self.load_chat_list()
        self.chat_area.config(state='normal')
        self.chat_area.delete('1.0', tk.END)
        self.chat_area.config(state='disabled')
        self._log_system(f"New session: {timestamp}")
    
    def _on_chat_select(self, event):
        w = event.widget
        if not w.curselection():
            return
        index = w.curselection()[0]
        filename = self.files[index]
        self.current_chat_file = filename
        
        # Load history
        path = os.path.join(CHATS_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            self.chat_history = json.load(f)
        
        # Display
        self.chat_area.config(state='normal')
        self.chat_area.delete('1.0', tk.END)
        for msg in self.chat_history:
            role = msg.get("role", "system")
            content = msg.get("content", "")
            if role == "user":
                self._add_to_ui("user", content)
            elif role == "assistant":
                self._add_to_ui("jarvis", content)
        self.chat_area.config(state='disabled')
    
    def delete_chat(self):
        if not self.current_chat_file:
            return
        path = os.path.join(CHATS_DIR, self.current_chat_file)
        if os.path.exists(path):
            os.remove(path)
        self.new_chat()

    # --- Voice (optional) ---
    
    def _load_ai(self):
        """Load voice models in background."""
        if VOSK_AVAILABLE and os.path.exists(VOSK_MODEL):
            try:
                model = Model(VOSK_MODEL)
                self.recognizer = KaldiRecognizer(model, 16000)
                self._log_system("Voice recognition: READY")
            except Exception as e:
                self._log_system(f"Voice init failed: {e}")
        
        if KOKORO_AVAILABLE and os.path.exists(KOKORO_MODEL):
            try:
                self.tts = Kokoro(KOKORO_MODEL, KOKORO_VOICES)
                self._log_system("TTS: READY")
            except Exception as e:
                self._log_system(f"TTS init failed: {e}")
        
        self._log_system("NEXUS_V2 :: All systems online.")
    
    def _toggle_listening(self):
        """Toggle voice input."""
        if not self.recognizer:
            self._log_system("Voice not available")
            return
        
        self.is_running = not self.is_running
        if self.is_running:
            self.btn_voice.config(text="VOICE: ON", fg=self.THEME["fg_primary"], bg="#003300")
            self._log_system("Listening for wake word...")
            threading.Thread(target=self._listen_loop, daemon=True).start()
        else:
            self.btn_voice.config(text="VOICE: OFF", fg=self.THEME["fg_muted"], bg=self.THEME["bg_dark"])
    
    def _listen_loop(self):
        """Voice listening loop - detects wake word and captures commands."""
        import subprocess
        
        WAKE_WORDS = ["hey jarvis", "jarvis", "hey bitch", "wake up"]
        WHISPER_CLI = resource_path("whisper-cli.exe")
        WHISPER_MODEL = resource_path("ggml-tiny.en.bin")
        
        q = queue.Queue()
        
        def callback(indata, frames, time_info, status):
            q.put(bytes(indata))
        
        try:
            with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16', channels=1, callback=callback):
                while self.is_running:
                    data = q.get()
                    
                    # Skip if busy or speaking
                    if self.is_busy or self.is_speaking:
                        continue
                    
                    if self.recognizer.AcceptWaveform(data):
                        result = json.loads(self.recognizer.Result())
                        text = result.get("text", "").lower()
                        
                        for trigger in WAKE_WORDS:
                            if trigger in text:
                                self._log_system(f"Trigger detected: {trigger}")
                                self._handle_audio_input(WHISPER_CLI, WHISPER_MODEL)
                                self.recognizer.Reset()
                                break
        except Exception as e:
            self._log_system(f"Listen loop error: {e}")
    
    def _handle_audio_input(self, whisper_cli: str, whisper_model: str):
        """Record and transcribe voice command."""
        import subprocess
        import time as time_module
        
        self._log_system("Recording...")
        fs = 16000
        audio_data = []
        has_spoken = False
        start_time = time_module.time()
        last_sound = time_module.time()
        
        try:
            with sd.InputStream(samplerate=fs, channels=1, dtype='int16') as stream:
                while True:
                    chunk, _ = stream.read(int(fs * 0.1))
                    audio_data.append(chunk)
                    
                    if np.max(np.abs(chunk)) > 500:
                        has_spoken = True
                        last_sound = time_module.time()
                    
                    # Timeout if no speech
                    if not has_spoken and (time_module.time() - start_time > 5.0):
                        self._log_system("No speech detected")
                        return
                    
                    # End recording after silence
                    if has_spoken and (time_module.time() - last_sound > 1.5):
                        break
            
            # Save to wav
            write("command.wav", fs, np.concatenate(audio_data))
            
            # Transcribe with whisper
            if os.path.exists(whisper_cli):
                si = subprocess.STARTUPINFO()
                si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                result = subprocess.run(
                    [whisper_cli, "-m", whisper_model, "-f", "command.wav", "-nt"],
                    capture_output=True, text=True, encoding='utf-8', startupinfo=si
                )
                user_text = result.stdout.strip()
            else:
                # Fallback: use vosk for transcription
                with open("command.wav", "rb") as f:
                    f.read(44)  # Skip WAV header
                    audio_bytes = f.read()
                self.recognizer.AcceptWaveform(audio_bytes)
                result = json.loads(self.recognizer.FinalResult())
                user_text = result.get("text", "")
            
            if user_text:
                self._log_system(f"Heard: {user_text}")
                self.current_turn_id += 1
                self.msg_queue.put(("user", user_text))
                self.chat_history.append({"role": "user", "content": user_text})
                threading.Thread(
                    target=self._process_with_agents_voice,
                    args=(user_text, self.current_turn_id),
                    daemon=True
                ).start()
            else:
                self._log_system("Couldn't understand")
                
        except Exception as e:
            self._log_system(f"Audio input error: {e}")
    
    def _process_with_agents_voice(self, text: str, turn_id: int):
        """Process voice input and speak response."""
        # Run normal processing
        self._toggle_busy(True)
        
        try:
            result = orchestrator.execute(text, callback=lambda m: self._log_tool(m))
            
            if isinstance(result, dict):
                output = result.get("result", str(result))
            else:
                output = str(result)
            
            self._log_jarvis(output)
            self.chat_history.append({"role": "assistant", "content": output})
            self.save_chat()
            
            # Speak response
            if self.tts:
                self._speak(output)
                
        except Exception as e:
            self._log_system(f"Error: {e}")
        
        finally:
            self._toggle_busy(False)
    
    def _speak(self, text: str):
        """Convert text to speech."""
        if not self.tts or self.stop_flag:
            return
        
        try:
            # Clean markdown
            clean = text.replace("*", "").replace("#", "").replace("`", "")
            
            # Limit length for voice
            if len(clean) > 300:
                clean = clean[:300] + "..."
            
            self.is_speaking = True
            samples, rate = self.tts.create(clean, voice="af_bella", speed=1.0, lang="en-us")
            
            if not self.stop_flag:
                sd.play(samples, rate)
                sd.wait()
            
            self.is_speaking = False
            
        except Exception as e:
            self.is_speaking = False
            self._log_system(f"TTS error: {e}")
    
    def _speech_worker(self):
        """TTS worker thread for streaming speech."""
        while True:
            try:
                text = self.speech_queue.get(timeout=1)
                if text is None:
                    break
                if not self.stop_flag and self.tts:
                    self._speak(text)
            except queue.Empty:
                continue
            except Exception as e:
                pass


def main():
    root = tk.Tk()
    app = JarvisUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
