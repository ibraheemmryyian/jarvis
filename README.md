# Jarvis - Sentient Suite (Two-Brain Architecture)

Jarvis is a local, voice-activated AI assistant designed with a "Two-Brain" architecture to balance a sarcastic personality with strict engineering capabilities.

## Architecture

- **Brain 1 (The Soul)**: Handles conversation, insults, and personality logic.
- **Brain 2 (The Engineer)**: A silent, JSON-based agent that executes tools (Web Search, File I/O) without breaking character.

## Features

- **Voice Interaction**: Wake word detection ("Hey Jarvis") and voice response.
- **Deep Research**: Can search the web using DuckDuckGo.
- **File Management**: Can read, write, and list files in the `jarvis_workspace` directory.
- **Memory**: Retains context for up to 100 conversation turns.

## Prerequisites

To run Jarvis, you need the following external components:

1.  **LM Studio**: Must be running locally on `http://localhost:1234/v1`.
2.  **Models**:
    -   Vosk Model (extracted to `model/`)
    -   Kokoro ONNX Model (`kokoro-v1.0.onnx` + `voices-v1.0.bin`)
    -   Whisper Model (`ggml-base.bin`)
3.  **Binaries**: `whisper-cli.exe` and `ffmpeg` (if required by audio libs).

## Installation

1.  Install Python 3.10+.
2.  Install dependencies:
    ```bash
    pip install duckduckgo-search sounddevice scipy vosk kokoro-onnx langdetect requests
    ```
3.  Ensure all model files are in the root directory.

## Usage

Run the main script:
```bash
py jarvis_ui.py
```

- **Voice**: "Hey Jarvis..."
- **Text**: Type in the UI window.
