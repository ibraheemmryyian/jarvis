# 🧠 JARVIS AI Assistant

**Your AI co-founder that runs locally, works autonomously, and has real personality.**

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/LLM-Qwen%203%2030B-green.svg" alt="LLM">
  <img src="https://img.shields.io/badge/Status-Active-success.svg" alt="Status">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</p>

---

## ✨ What is Jarvis?

Jarvis is a **locally-running AI assistant** with personality. Not just a chatbot - it's your co-founder that can:

- 🗣️ **Voice Interaction** - Wake word "Hey Jarvis", natural conversation
- 🤖 **Autonomous Execution** - Give it a task, walk away, come back to results
- 🔬 **Deep Research** - Multi-source academic and web research
- 💻 **Code Generation** - Full-stack development with unique designs
- 📝 **Writing & Analysis** - Content, reports, business analysis
- 🔒 **100% Local** - Your data never leaves your machine
- 💰 **$0 API Costs** - Uses local LLM (LM Studio)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- [LM Studio](https://lmstudio.ai/) with Qwen 3 Coder 30B (or any local LLM)

### Installation

```bash
git clone https://github.com/ibraheemmryyian/jarvis.git
cd jarvis
pip install -r requirements.txt
```

### Start LM Studio
1. Open LM Studio
2. Load your preferred model
3. Start local server (port 1234)

### Run Jarvis

```bash
python jarvis_ui.py
```

---

## 🏗️ Architecture

### 26 Specialized Agents

| Category | Agents |
|----------|--------|
| **Core** | Autonomous Executor, Recycler, Orchestrator, Router |
| **Code** | Coder, Code Indexer, Code Reviewer, QA Agent |
| **Execution** | Terminal (sandboxed), Project Manager, Git Agent |
| **Testing** | Browser Tester |
| **Research** | Deep Research, Brute Research, Synthesizer |
| **Creativity** | Design Creativity (unique layouts + banned patterns) |
| **Comms** | Personality, Notifications |

### Project Structure

```
jarvis/
├── agents/                 # 26 agent modules
│   ├── autonomous.py       # Multi-step task executor
│   ├── recycler.py         # Context management
│   ├── terminal.py         # Sandboxed commands (4-layer security)
│   ├── design_creativity.py # Unique layouts
│   ├── git_agent.py        # Version control
│   └── ...
├── jarvis_ui.py            # Main UI
├── jarvis_workspace/       # Generated projects
└── tests/
```

---

## 💡 Usage Examples

### Build a Website (Autonomous)
```
"Build me a premium landing page for my SaaS product"
```
Jarvis will:
1. Plan 10 steps
2. Generate unique design (not template)
3. Create all files
4. Run QA validation
5. Self-heal any issues

### Deep Research
```
"Research the industrial symbiosis market in the EU"
```

### Code Review
```
"Review my project and generate documentation"
```

### Git Push
```
"Commit and push my changes to GitHub"
```

---

## 🎨 Unique Design System

Jarvis never generates cookie-cutter websites. Each build gets:

- **Random Layout**: Bento Grid, Asymmetric Split, Horizontal Scroll, etc.
- **Random Palette**: Neon Cyberpunk, Ocean Depths, Forest Moss, etc.
- **Banned Patterns**: "3 equal-width boxes", "centered hero with gradient"

---

## 🔐 Security

### Terminal Agent (4-Layer Security)
1. **Blocked Commands**: rm, del, sudo, chmod, etc.
2. **Blocked Patterns**: ;, &&, |, >, etc.
3. **Blocked Keywords**: delete, destroy, format, etc.
4. **Whitelist Only**: npm, pip, python, node, git

---

## 📊 How It Works

```
User Input → UI → Router
              ↓
    ┌─────────────────┐
    │ autonomous.py   │ ← Plans 10 steps
    │                 │
    │ For each step:  │
    │  ├─ context     │ ← code_indexer
    │  ├─ creativity  │ ← design_creativity
    │  ├─ generate    │ ← LM Studio
    │  ├─ save        │ ← project_manager
    │  └─ validate    │ ← qa_agent
    └─────────────────┘
              ↓
         Done! Project saved to jarvis_workspace/
```

---

## 🛠️ Configuration

### `agents/config.py`
```python
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
WORKSPACE_DIR = "jarvis_workspace"
MAX_CONTEXT_TOKENS = 32000
```

### Environment Variables
```bash
GITHUB_TOKEN=your_token  # For git_agent push
```

---

## 📈 Roadmap

- [x] 26 Agent System
- [x] Autonomous Execution
- [x] Design Creativity System
- [x] Git Integration
- [x] UI Wiring
- [ ] Web UI (React)
- [ ] Cloud-Hosted Option
- [ ] Plugin System
- [ ] Multi-Model Support

---

## 🤝 Contributing

PRs welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

---

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

## 🙏 Acknowledgments

- Built by [@ibraheemmryyian](https://github.com/ibraheemmryyian)
- Powered by local LLMs via [LM Studio](https://lmstudio.ai/)

---

**"Not just an AI. Your AI."** 🤖
