# Jarvis - Sentient Suite (Two-Brain Architecture)

Jarvis is a local, voice-activated AI assistant designed with a "Two-Brain" architecture to balance a sarcastic personality with strict engineering capabilities.

## 🧠 Architecture
- **Brain 1 (The Soul)**: A sarcastic, concise, personality-driven interface.
- **Brain 2 (The Engineer)**: A silent, JSON-based agent using **Qwen3 Coder 30B** (Recommended) for complex tasks.

## ✨ Features

### 1. **Autonomous Builder (Architect Mode)**
- **Scaffold Projects**: "Scaffold a frontend app called 'Dash'." -> Creates HTML/CSS/JS.
- **Python Automation**: "Scaffold a python tool". -> Creates `main.py`, `tests/`, `requirements.txt`.
- **Coding**: "Copy my project here and run the tests." -> Ingests code, runs it safely, reports errors.

### 2. **Deep Research (Scholar Mode)**
- **Academic Scraper**: "Write a paper on fusion." -> Scrapes Arxiv, PDFs, and generic web data.
- **Synthesis**: Compiles multi-source data into a single coherent report.
- **Memory**: Remembers up to **1000 turns** of context (thanks to your 48GB RAM).

### 3. **System Automation (God Mode)**
- **Read-Only Access**: Can read ANY file on your PC (`C:/Users/...`).
- **Sandboxed Write**: Can ONLY write to `jarvis_workspace` (Safety Lock 🔒).
- **Control**: "Launch Spotify", "Lock PC", "Shutdown", "Open Calculator".
- **Clipboard**: "Summarize this" (Reads your clipboard instantly).

## 🛠️ Configuration (CRITICAL)

### 1. LM Studio
- **Model**: **Qwen3 Coder 30B** (Found in your library) -> **REQUIRED** for Builder features.
- **Backup**: DeepSeek Coder v2.
- **Settings**: 
    - Context Window: **32,000** (or more).
    - GPU Layers: Max out your RTX 4060.
    - Server Port: `1234`.

### 2. Audio Models (Check `jarvis/` folder)
- `model/` (Vosk)
- `kokoro-v1.0.onnx` & `voices-v1.0.bin` (TTS)
- `whisper-cli.exe` & `ggml-base.bin` (STT)

## 🎮 Verified Commands
- **"Scaffold a frontend project called 'CryptoTracker'."**
- **"Research quantum computing and save a PDF report."**
- **"Look at my Downloads folder and list the files."**
- **"Copy 'C:/Work/ProjectX' here and run the main script."**
- **"Launch Chrome and open Spotify."**
- **"Lock the computer."**

## ⚠️ Safety
- **Write Sandbox**: He cannot overwrite your system files. He only writes to `jarvis_workspace`.
- **Privacy**: All processing is LOCAL (LM Studio). No data leaves your network.

## 🚀 Installation

1.  **Install Python 3.10+**: [python.org](https://www.python.org/downloads/)
2.  **Install Libraries**:
    ```powershell
    pip install duckduckgo-search sounddevice scipy vosk kokoro-onnx langdetect requests reportlab
    ```
3.  **Verify File Structure**:
    ```text
    jarvis/
    ├── jarvis_ui.py
    ├── model/ (Vosk folder)
    ├── kokoro-v1.0.onnx
    ├── voices-v1.0.bin
    ├── whisper-cli.exe
    ├── ggml-base.bin
    └── jarvis_workspace/
    ```

## 🎮 Usage

Run the main script:
```powershell
py jarvis_ui.py
```

- **Voice Commands**: Say "Hey Jarvis" or "Hey Bitch" followed by your command.
    -   *Example*: "Hey Jarvis, research the history of the Eiffel Tower."
- **Text Commands**: Type in the UI window.
    -   *Example*: "Write a python script to calculate pi."
- **Interruption**: Speak while he is working to cancel the current task.
