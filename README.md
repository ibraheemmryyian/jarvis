# Jarvis - Sentient Suite (Two-Brain Architecture)

Jarvis is a local, voice-activated AI assistant designed with a "Two-Brain" architecture to balance a sarcastic personality with strict engineering capabilities.

## 🧠 Architecture

- **Brain 1 (The Soul)**: Handles conversation, insults, and personality logic.
- **Brain 2 (The Engineer)**: A silent, JSON-based agent that executes tools (Web Search, File I/O) without breaking character.

## ✨ Features

- **Voice Interaction**: Wake word detection ("Hey Jarvis") and voice response.
- **Deep Research**: Can search the web using DuckDuckGo.
- **File Management**: Can read, write, and list files in the `jarvis_workspace` directory.
- **Memory**: Retains context for up to 100 conversation turns.

## 🛠️ Prerequisites & Downloads

To run Jarvis, you must download and install these external components:

### 1. LM Studio (The Brain)
- **Download**: [lmstudio.ai](https://lmstudio.ai/)
- **Setup**:
    1.  Install and launch LM Studio.
    2.  Download a model (recommended: `Llama 3` or `Mistral`).
    3.  Go to the **Local Server** tab (double-headed arrow icon).
    4.  Start the server on port `1234`.
    5.  Ensure "Cors" is enabled (usually default).

### 2. Models (The Voice & Ears)
You need to place these files in the root `jarvis` folder:

- **Vosk Model (Speech-to-Text)**
    -   **Download**: [Vosk Models](https://alphacephei.com/vosk/models)
    -   **Recommended**: `vosk-model-small-en-us-0.15` (fast) or `vosk-model-en-us-0.22` (accurate).
    -   **Action**: Extract the downloaded zip. Rename the folder to `model`.

- **Kokoro ONNX (Text-to-Speech)**
    -   **Download**: [Kokoro ONNX Releases](https://github.com/thewh1teagle/kokoro-onnx/releases)
    -   **Files Needed**:
        -   `kokoro-v1.0.onnx`
        -   `voices-v1.0.bin`
    -   **Action**: Place both files directly in the `jarvis` folder.

- **Whisper (Command Recognition)**
    -   **Download**: [Whisper.cpp Releases](https://github.com/ggerganov/whisper.cpp/releases/latest)
    -   **File Needed**: `whisper-cli.exe` (Windows)
    -   **Model**: [ggml-base.bin](https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin)
    -   **Action**: Place `whisper-cli.exe` and `ggml-base.bin` in the `jarvis` folder.

### 3. Dependencies
- **[FFmpeg](https://ffmpeg.org/download.html)**: Required for audio processing. Ensure `ffmpeg.exe` is in your system PATH or the `jarvis` folder.

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
