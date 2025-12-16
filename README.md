# J.A.R.V.I.S

> **Just A Rather Very Intelligent System**
> Local AI Assistant with Multi-Agent Architecture

## Quick Start

```bash
# Ensure LM Studio is running with a model loaded at localhost:1234
python jarvis_ui_v2.py
```

## Architecture

Jarvis v2 uses a **Split-Brain Multi-Agent System**:

```
┌─────────────────────────────────────────────────────────────┐
│                      USER INPUT                              │
└───────────────────────┬─────────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    ROUTER AGENT                              │
│        Intent Classification + Task Decomposition           │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┬─────────────────┐
        ▼               ▼               ▼                 ▼
┌───────────┐   ┌───────────┐   ┌───────────┐   ┌───────────┐
│ RESEARCH  │   │   CODER   │   │    OPS    │   │   CHAT    │
│   Agent   │   │   Agent   │   │   Agent   │   │   Agent   │
└───────────┘   └───────────┘   └───────────┘   └───────────┘
```

## Features

### Core Capabilities
- **Voice Control**: Wake word detection + TTS responses (Vosk + Kokoro)
- **Multi-Agent Routing**: Automatic task classification and dispatch
- **Deep Research**: Multi-phase web + academic source aggregation
- **Code Generation**: Full project scaffolding and multi-file creation
- **Autonomous Mode**: End-to-end research → build pipeline

### Context Management
Token-efficient memory using task-specific `.md` files:
- `active_task.md` - Current objective
- `research_notes.md` - Research findings
- `codebase_map.md` - Project structure
- `decisions.md` - Design rationale
- `deployment_log.md` - CI/CD history
- `documentation.md` - Docs context

## File Structure

```
jarvis/
├── jarvis_ui_v2.py      # Main UI (run this)
├── jarvis_ui.py         # Legacy UI (preserved)
├── agents/
│   ├── __init__.py
│   ├── config.py        # Settings & paths
│   ├── context_manager.py
│   ├── base_agent.py
│   ├── router.py
│   ├── research.py
│   ├── coder.py
│   ├── ops.py
│   └── orchestrator.py
├── jarvis_workspace/    # Sandboxed file operations
│   └── .context/        # Memory files
└── chats/               # Session history
```

## Requirements

```
tkinter
requests
sounddevice
numpy
scipy
vosk
kokoro-onnx
duckduckgo-search
pyautogui
```

## Configuration

Edit `agents/config.py`:
```python
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
MAX_CONTEXT_TOKENS = 8000
MAX_OUTPUT_TOKENS = 4000
```

## License

MIT
