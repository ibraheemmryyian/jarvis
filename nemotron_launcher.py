"""
NVIDIA Nemotron Nano v2 Launcher (CUDA + Mamba-2)
Requires: pip install llama-cpp-python (built with CUDA)
"""
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import threading
import os

from llama_cpp import Llama

DEFAULT_MODEL_DIR = r"C:\Users\Imrry\.lmstudio\models\bartowski\nvidia_NVIDIA-Nemotron-Nano-9B-v2-GGUF"

class NemotronLauncher(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Nemotron Nano v2 - CUDA")
        self.geometry("1050x800")
        self.configure(bg="#1a1a2e")

        self._setup_styles()
        self._setup_vars()
        self._create_ui()

    def _setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TFrame", background="#1a1a2e")
        self.style.configure("TLabel", background="#1a1a2e", foreground="#eee", font=("Segoe UI", 10))
        self.style.configure("TButton", background="#76b900", foreground="white", font=("Segoe UI", 10, "bold"))
        self.style.map("TButton", background=[("active", "#5a8f00")])
        self.style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground="#76b900")
        self.style.configure("TLabelframe.Label", foreground="#76b900", background="#1a1a2e", font=("Segoe UI", 11, "bold"))
        self.style.configure("TLabelframe", background="#1a1a2e")
        self.style.configure("TCheckbutton", background="#1a1a2e", foreground="#eee")

    def _setup_vars(self):
        self.model_path = tk.StringVar(value=self._find_model())
        self.n_ctx = tk.IntVar(value=8192)
        self.n_gpu_layers = tk.IntVar(value=99)
        self.temperature = tk.DoubleVar(value=0.7)
        self.max_tokens = tk.IntVar(value=2048)
        self.kv_cache = tk.StringVar(value="f16")
        self.enable_thinking = tk.BooleanVar(value=False)
        
        self.llm = None
        self.chat_history = []
        self.stop_flag = threading.Event()

    def _find_model(self):
        if os.path.exists(DEFAULT_MODEL_DIR):
            for f in os.listdir(DEFAULT_MODEL_DIR):
                if f.endswith('.gguf'):
                    return os.path.join(DEFAULT_MODEL_DIR, f)
        return ""

    def _create_ui(self):
        main = ttk.Frame(self)
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header
        ttk.Label(main, text="🟢 NVIDIA Nemotron Nano v2 (Mamba-2 Hybrid)", style="Header.TLabel").pack(anchor="w")
        self.status = ttk.Label(main, text="Model: Not loaded", foreground="#888")
        self.status.pack(anchor="w", pady=(0, 15))

        # === Settings Frame ===
        settings = ttk.LabelFrame(main, text=" Model Configuration ", padding=10)
        settings.pack(fill=tk.X, pady=(0, 15))

        # Row 1: Model path
        row1 = ttk.Frame(settings)
        row1.pack(fill=tk.X, pady=5)
        ttk.Label(row1, text="Model GGUF:").pack(side=tk.LEFT)
        ttk.Entry(row1, textvariable=self.model_path, width=70).pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        ttk.Button(row1, text="Browse", command=self._browse).pack(side=tk.LEFT)

        # Row 2: Core params
        row2 = ttk.Frame(settings)
        row2.pack(fill=tk.X, pady=10)
        
        ttk.Label(row2, text="Context (n_ctx):").pack(side=tk.LEFT)
        ttk.Entry(row2, textvariable=self.n_ctx, width=8).pack(side=tk.LEFT, padx=(5, 20))
        
        ttk.Label(row2, text="GPU Layers:").pack(side=tk.LEFT)
        ttk.Entry(row2, textvariable=self.n_gpu_layers, width=5).pack(side=tk.LEFT, padx=(5, 20))
        
        ttk.Label(row2, text="KV Cache:").pack(side=tk.LEFT)
        kv_combo = ttk.Combobox(row2, textvariable=self.kv_cache, values=["f16", "q8_0", "q4_0"], state="readonly", width=6)
        kv_combo.pack(side=tk.LEFT, padx=(5, 20))

        ttk.Label(row2, text="Temp:").pack(side=tk.LEFT)
        ttk.Entry(row2, textvariable=self.temperature, width=5).pack(side=tk.LEFT, padx=(5, 20))

        ttk.Checkbutton(row2, text="Thinking Mode", variable=self.enable_thinking).pack(side=tk.LEFT, padx=10)
        
        self.load_btn = ttk.Button(row2, text="LOAD MODEL", command=self._load_thread)
        self.load_btn.pack(side=tk.RIGHT)

        # === Chat Display ===
        self.chat = scrolledtext.ScrolledText(main, wrap=tk.WORD, font=("Consolas", 11), 
                                              bg="#16213e", fg="#e8e8e8", insertbackground="white", height=22)
        self.chat.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.chat.tag_config("user", foreground="#4ecca3", font=("Consolas", 11, "bold"))
        self.chat.tag_config("model", foreground="#ffd369")
        self.chat.tag_config("system", foreground="#a0a0a0", font=("Consolas", 10, "italic"))
        self.chat.tag_config("error", foreground="#ff6b6b")
        self.chat.config(state=tk.DISABLED)

        # === Input ===
        input_frame = ttk.Frame(main)
        input_frame.pack(fill=tk.X)
        
        self.input = tk.Text(input_frame, height=3, bg="#0f0f23", fg="white", 
                             font=("Segoe UI", 11), insertbackground="white")
        self.input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.input.bind("<Return>", self._on_enter)
        self.input.bind("<Shift-Return>", lambda e: "break")

        btn_frame = ttk.Frame(input_frame)
        btn_frame.pack(side=tk.RIGHT)
        self.send_btn = ttk.Button(btn_frame, text="Send", command=self._send)
        self.send_btn.pack(fill=tk.X, pady=(0, 5))
        ttk.Button(btn_frame, text="Stop", command=lambda: self.stop_flag.set()).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(btn_frame, text="Clear", command=self._clear).pack(fill=tk.X)

    def _browse(self):
        f = filedialog.askopenfilename(initialdir=DEFAULT_MODEL_DIR, filetypes=[("GGUF", "*.gguf")])
        if f:
            self.model_path.set(f)

    def _clear(self):
        self.chat_history.clear()
        self.chat.config(state=tk.NORMAL)
        self.chat.delete("1.0", tk.END)
        self.chat.config(state=tk.DISABLED)

    def _log(self, msg, tag="system"):
        def update():
            self.chat.config(state=tk.NORMAL)
            self.chat.insert(tk.END, f"{msg}\n", tag)
            self.chat.see(tk.END)
            self.chat.config(state=tk.DISABLED)
        self.after(0, update)

    def _stream(self, text, tag="model"):
        def update():
            self.chat.config(state=tk.NORMAL)
            self.chat.insert(tk.END, text, tag)
            self.chat.see(tk.END)
            self.chat.config(state=tk.DISABLED)
        self.after(0, update)

    def _load_thread(self):
        threading.Thread(target=self._load_model, daemon=True).start()

    def _load_model(self):
        path = self.model_path.get()
        if not path or not os.path.exists(path):
            self._log("Error: Invalid model path", "error")
            return

        self.after(0, lambda: self.status.config(text="Status: Loading model..."))
        self.after(0, lambda: self.load_btn.config(state=tk.DISABLED))
        
        # KV cache mapping: f16=0, q8_0=8, q4_0=2
        kv_map = {"f16": 0, "q8_0": 8, "q4_0": 2}
        kv_val = kv_map.get(self.kv_cache.get(), 0)
        
        self._log(f"Loading {os.path.basename(path)}...")
        self._log(f"  Context: {self.n_ctx.get()}, GPU Layers: {self.n_gpu_layers.get()}, KV Cache: {self.kv_cache.get()}")

        try:
            self.llm = Llama(
                model_path=path,
                n_ctx=self.n_ctx.get(),
                n_gpu_layers=self.n_gpu_layers.get(),
                type_k=kv_val,
                type_v=kv_val,
                verbose=False,
                chat_format="chatml"
            )
            self.after(0, lambda: self.status.config(text=f"Model: {os.path.basename(path)} ✓", foreground="#76b900"))
            self._log("Model loaded successfully!", "system")
        except Exception as e:
            self._log(f"Error: {e}", "error")
            self.after(0, lambda: self.status.config(text="Status: Load failed", foreground="#ff6b6b"))
        finally:
            self.after(0, lambda: self.load_btn.config(state=tk.NORMAL))

    def _on_enter(self, e):
        if not (e.state & 0x1):
            self._send()
            return "break"

    def _send(self):
        if not self.llm:
            messagebox.showwarning("No Model", "Load a model first!")
            return
        
        text = self.input.get("1.0", tk.END).strip()
        if not text:
            return
        
        self.input.delete("1.0", tk.END)
        self._log(f"\nYou: {text}", "user")
        self.stop_flag.clear()
        threading.Thread(target=self._generate, args=(text,), daemon=True).start()

    def _generate(self, user_input):
        self.after(0, lambda: self.send_btn.config(state=tk.DISABLED))
        self.after(0, lambda: self.status.config(text="Generating..."))

        try:
            messages = []
            if self.enable_thinking.get():
                messages.append({"role": "system", "content": "detailed thinking on"})
            else:
                messages.append({"role": "system", "content": "You are a helpful AI assistant."})
            
            for r, c in self.chat_history[-6:]:
                messages.append({"role": r, "content": c})
            messages.append({"role": "user", "content": user_input})

            self._stream("\nNemotron: ", "system")

            response = ""
            for chunk in self.llm.create_chat_completion(
                messages=messages,
                temperature=self.temperature.get(),
                max_tokens=self.max_tokens.get(),
                stream=True
            ):
                if self.stop_flag.is_set():
                    self._stream("\n[STOPPED]", "error")
                    break
                delta = chunk["choices"][0].get("delta", {})
                if "content" in delta:
                    text = delta["content"]
                    response += text
                    self._stream(text)

            if not self.stop_flag.is_set():
                self.chat_history.append(("user", user_input))
                self.chat_history.append(("assistant", response))
            self._stream("\n")

        except Exception as e:
            self._log(f"Error: {e}", "error")
        finally:
            self.after(0, lambda: self.send_btn.config(state=tk.NORMAL))
            self.after(0, lambda: self.status.config(text=f"Model: {os.path.basename(self.model_path.get())} ✓", foreground="#76b900"))

if __name__ == "__main__":
    NemotronLauncher().mainloop()
