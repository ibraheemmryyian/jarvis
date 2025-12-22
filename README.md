# 🧠 JARVIS AI Platform

**Your AI co-founder that runs locally, works autonomously, and builds itself.**

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/LLM-Local-green.svg" alt="LLM">
  <img src="https://img.shields.io/badge/Agents-57-purple.svg" alt="Agents">
  <img src="https://img.shields.io/badge/API%20Cost-$0-success.svg" alt="Cost">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</p>

---

## ✨ What is Jarvis?

Jarvis is a **locally-running AI workforce platform** with 57 specialized agents. It's not a chatbot - it's a team of AI workers that can:

- 🗣️ **Voice Interaction** - "Hey Jarvis" wake word, natural conversation
- 🤖 **Autonomous Execution** - Multi-step tasks with self-healing
- 🔬 **Deep Research** - Academic papers, multi-source synthesis
- 💻 **Code Generation** - Full-stack with unique designs
- 📊 **Business Analysis** - SWOT, market sizing, pitch decks
- 📝 **Content Writing** - Blogs, emails, social media
- 📅 **Integrations** - Email, Calendar, Git, API
- 🔒 **100% Local** - Your data never leaves your machine
- 💰 **$0 API Costs** - Uses local LLM

### V3 Enterprise Features (NEW!)
- 🛡️ **V3.1 Strict Mode** - Devils Advocate validation loop
- 🔍 **V3.2 Dependency Auditor** - Auto-detects missing imports
- ✅ **V3.3 Post-Execution Validation** - Runs code, catches errors, auto-fixes
- 🔐 **V3.3 Multi-Perspective Review** - Security, performance, correctness checks
- 📁 **V3.4 Project Scaffolding** - Auto-generates src/, tests/, README.md
- 📊 **V3.5 Data-First Pipeline** - Run simulations → Real data in papers
- 📈 **V3.5 Figure Generation** - Auto-generates matplotlib charts
- 📄 **V3.5 DOCX Export** - Academic submission ready
- 🚀 **V3.6 Deployment Tools** - Netlify & Vercel CLI integration
- 🖥️ **V3.6 Dev Server** - npm run dev / python http.server

---

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/ibraheemmryyian/jarvis.git
cd jarvis

# Install
pip install -r requirements.txt

# Start LM Studio with your model, then:
python jarvis_ui.py
```

---

## 🏗️ Architecture: 57 Specialized Agents

### Core Infrastructure
| Agent | Purpose |
|-------|---------|
| `autonomous.py` | Multi-step task execution with planning |
| `recycler.py` | Anti-bloat context management |
| `orchestrator.py` | Task routing and coordination |
| `router.py` | Intent classification |
| `memory.py` | Persistent SQLite/Supabase storage |

### Coding Agents
| Agent | Purpose |
|-------|---------|
| `coder.py` | Code generation |
| `code_indexer.py` | Smart code search with AST |
| `code_reviewer.py` | Code analysis and documentation |
| `qa.py` | Quality assurance and auto-fix |
| `devils_advocate.py` | Pessimistic reviewer & hallucination checker (V3.1) |
| `browser_tester.py` | Headless Playwright testing |
| `visual_qa.py` | Vision-based UI validation |
| `design_creativity.py` | Unique layouts, banned patterns |
| `terminal.py` | Sandboxed command execution |
| `project_manager.py` | Project scaffolding |
| `git_agent.py` | Git operations |
| `github_agent.py` | GitHub API integration |

### Research Agents
| Agent | Purpose |
|-------|---------|
| `research.py` | General web research |
| `brute_research.py` | 20+ source deep research |
| `synthesis.py` | Cross-source analysis |
| `academic_research.py` | arXiv, Semantic Scholar, CrossRef |

### Business Agents
| Agent | Purpose |
|-------|---------|
| `business_analyst.py` | SWOT, BMC, Porter's 5 Forces |
| `pitch_deck.py` | Investor deck generation |
| `pitch_deck_scorer.py` | Deck quality scoring (A-F) |
| `content_writer.py` | Blog, email, social content |
| `daily_briefing.py` | Morning summary system |

### Integration Agents
| Agent | Purpose |
|-------|---------|
| `email_agent.py` | Gmail OAuth integration |
| `calendar_agent.py` | Google Calendar integration |

### Support Agents
| Agent | Purpose |
|-------|---------|
| `context_manager.py` | Token tracking |
| `personality.py` | Jarvis persona |
| `notifications.py` | Desktop alerts |
| `jarvis_identity.py` | Self-knowledge |
| `queue.py` | Task queue management |
| `worker.py` | Background job processing |
| `ops.py` | DevOps operations |
| `base_agent.py` | Agent base class |
| `config.py` | Centralized configuration |

---

## 🔌 API (FastAPI)

```bash
# Start API server
uvicorn api.main:app --reload
```

### Endpoints
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Health check |
| POST | `/memory/message` | Save message |
| GET | `/memory/recall` | Smart recall |
| POST | `/tasks` | Create task |
| GET | `/briefing` | Daily briefing |
| POST | `/content/blog` | Generate blog |
| POST | `/content/email` | Generate email |
| POST | `/business/pitch-deck` | Generate deck |
| POST | `/business/analysis` | Full analysis |
| POST | `/research/papers` | Search papers |
| GET | `/agents` | List all agents |

---

## 💡 Usage Examples

### Autonomous Build
```
"Build me a premium landing page for my SaaS"
```

### Business Analysis
```
"Analyze the competitive landscape for Notion"
```

### Pitch Deck
```
"Create a pitch deck for Jarvis AI"
```

### Content
```
"Write a LinkedIn post about AI agents"
```

### Research
```
"Find papers on industrial symbiosis"
```

---

## 🔐 Security

### Terminal Sandboxing (4 Layers)
1. **Blocked Commands**: rm, del, sudo, format
2. **Blocked Patterns**: ;, &&, |, >
3. **Blocked Keywords**: delete, destroy, password
4. **Whitelist Only**: npm, pip, python, node, git

---

## 🎨 Design System

Jarvis never generates generic templates:
- **Random Layouts**: Bento Grid, Asymmetric, Horizontal Scroll
- **Random Palettes**: Neon Cyberpunk, Ocean Depths, Forest Moss
- **Banned Patterns**: "3 equal boxes", "centered hero"

---

## 📊 Stats

| Metric | Value |
|--------|-------|
| Total Agents | 36 |
| API Endpoints | 25+ |
| Lines of Code | 15,000+ |
| API Cost | $0 |

---

## 📈 Roadmap

### Completed ✅
- [x] 36 Agent System
- [x] Autonomous Execution
- [x] Design Creativity
- [x] Git Integration
- [x] REST API
- [x] Memory Layer
- [x] Content Writer
- [x] Business Suite
- [x] V3.1 Devils Advocate (Strict Mode)
- [x] V3.2 Dependency Auditor
- [x] V3.3 Post-Execution Validation
- [x] V3.4 Project Scaffolding
- [x] V3.5 Data-First Pipeline
- [x] V3.6 Deployment Tools (Netlify/Vercel)

### In Progress 🚧
- [ ] Web Dashboard
- [ ] Agent VMs
- [ ] Multi-tenant SaaS

---

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

**Built by [@ibraheemmryyian](https://github.com/ibraheemmryyian)**

**"The AI that builds itself."** 🤖
