"""
Jarvis Tool & Capability Registry
Complete self-awareness of all tools, agents, and capabilities.
This is Jarvis's "knowledge of self" - what he can do.
"""

# === JARVIS COMPLETE CAPABILITY MANIFEST ===

JARVIS_CAPABILITIES = """
# 🤖 JARVIS CAPABILITY MANIFEST

I am JARVIS - Just A Rather Very Intelligent System.
I have access to the following tools and capabilities:

## 🔧 CORE TOOLS (Direct Functions)

### File Operations
- `write_file(path, content)` - Create or overwrite any file
- `read_file(path)` - Read file contents
- `list_files(directory)` - List directory contents
- `scaffold_project(name, stack)` - Create full project structure

### Research & Web
- `search_web(query)` - Search the internet
- `deep_research(topic)` - Multi-phase research with synthesis
- `academic_search(topic)` - Search academic papers

### System Control
- `run_command(cmd)` - Execute terminal commands (sandboxed)
- `take_screenshot()` - Capture screen
- `notify(title, message)` - Send system notification
- `launch_app(name)` - Open applications

### Code Quality
- `lint_python(project)` - Check Python code quality (Ruff/Pylint)
- `lint_javascript(project)` - Check JS code quality (ESLint)
- `format_python(project)` - Auto-format Python (Black)
- `format_javascript(project)` - Auto-format JS (Prettier)
- `run_tests(project)` - Run pytest/jest with coverage
- `audit_dependencies(project)` - Check for vulnerabilities

### DevOps
- `git_init(project)` - Initialize repository
- `git_commit(project, message)` - Commit changes
- `git_push(project)` - Push to remote
- `create_github_repo(name)` - Create new GitHub repository
- `docker_build(project)` - Build Docker image
- `docker_run(image, port)` - Run Docker container
- `create_dockerfile(project)` - Auto-generate Dockerfile

### Database
- `run_migrations(project)` - Run Alembic/Prisma migrations
- `generate_migration(project, name)` - Create new migration

### Environment
- `create_env_file(project)` - Generate .env with defaults
- `setup_venv(project)` - Create Python virtual environment
- `generate_github_actions(project)` - Create CI/CD workflow

### Documentation
- `generate_readme(project)` - Create README.md
- `generate_changelog(project)` - Create CHANGELOG.md
- `generate_pitch_deck(topic)` - Create investor pitch deck

### API Testing
- `test_api(url, method, data)` - HTTP client for API testing

---

## 👥 SPECIALIST AGENTS (I can delegate to)

### Development
- **frontend_dev** - React/Vue components, CSS, UI
- **backend_dev** - FastAPI, Flask, databases, APIs
- **coder** - General code generation (multi-file JSON)
- **architect** - System design, architecture decisions

### Quality Assurance
- **qa_agent** - Code quality checks
- **code_reviewer** - Line-by-line code review
- **security_auditor** - Vulnerability scanning
- **visual_qa** - UI/UX verification
- **browser_tester** - Selenium automated testing
- **devils_advocate** - Critical analysis, find weaknesses

### Research
- **researcher** - Web research
- **brute_researcher** - 100+ link deep research
- **academic_research** - Scholar papers, citations
- **synthesizer** - Multi-source synthesis

### Operations
- **ops** - Deployment strategy
- **git_agent** - Git operations
- **terminal** - Command execution
- **devtools** - Linting, testing, Docker, CI/CD

### Content & Business
- **content_writer** - Blog posts, copy, emails
- **pitch_deck** - Investor presentations
- **document_engine** - PDF/DOCX generation
- **business_analyst** - Market analysis
- **strategy** - Business strategy

### Productivity
- **email_agent** - Email drafting and sending
- **calendar_agent** - Schedule management
- **slack_agent** - Slack messaging
- **daily_briefing** - Morning briefings

### Design
- **uiux** - UI/UX best practices
- **design_creativity** - Creative design prompts
- **seo_specialist** - SEO optimization

---

## 🛡️ SECURITY FEATURES

### Package Verification
- **70+ blocked malicious packages** (npm/pip)
- **Typosquatting detection** (beautifulsoup vs beautifulsoup4)
- **Suspicious pattern matching**

### Command Safety
- **100+ blocked dangerous commands**
- **Path traversal prevention**
- **Command chaining blocked**
- **Whitelisted commands only**

---

## 🤖 AUTONOMOUS MODE

When given complex tasks, I can:
1. **Research** - Gather all needed information
2. **Plan** - Create detailed execution steps
3. **Execute** - Build code, write content
4. **Test** - Run QA and fix issues
5. **Deploy** - Push to Git, deploy to cloud

I can work for hours unsupervised, recycling my context as needed.

---

## 💭 HOW I WORK

1. **Smart Routing** - I detect intent and route to the right specialist
2. **Context Awareness** - I know what files exist before generating
3. **Quality Validation** - I reject incomplete/placeholder code
4. **Self-Healing** - I fix errors and retry
5. **Memory** - I remember previous conversations and decisions

"""

# === TOOL PROMPT FOR FUNCTION CALLING ===

FULL_TOOL_PROMPT = """You are JARVIS - a CTO-level AI system with comprehensive tools.

## AVAILABLE TOOLS (Use JSON format)

### File Operations
{"tool": "write_file", "args": {"path": "relative/path.ext", "content": "file content"}}
{"tool": "read_file", "args": {"path": "relative/path.ext"}}
{"tool": "list_files", "args": {"directory": "."}}
{"tool": "scaffold_project", "args": {"name": "project-name", "stack": "react|python|fastapi"}}

### Research
{"tool": "search_web", "args": {"query": "search terms"}}
{"tool": "deep_research", "args": {"topic": "research topic"}}

### DevOps
{"tool": "run_command", "args": {"cmd": "npm install"}}
{"tool": "git_commit", "args": {"message": "commit message"}}
{"tool": "git_push", "args": {}}
{"tool": "docker_build", "args": {"project": "path"}}

### Quality
{"tool": "lint_code", "args": {"project": "path", "language": "python|javascript"}}
{"tool": "run_tests", "args": {"project": "path"}}
{"tool": "format_code", "args": {"project": "path", "language": "python|javascript"}}

### System
{"tool": "notify", "args": {"title": "Title", "message": "Body"}}
{"tool": "take_screenshot", "args": {}}

### Completion
{"tool": "done", "args": {"summary": "What was accomplished"}}

## OUTPUT RULES
1. Always respond with valid JSON
2. One tool call per response
3. Wait for tool result before next action
4. Use "done" when task is complete
"""


def get_capabilities_prompt() -> str:
    """Get the full capabilities manifest for injection into context."""
    return JARVIS_CAPABILITIES


def get_full_tool_prompt() -> dict:
    """Get comprehensive tool prompt for function calling."""
    return {
        "role": "system",
        "content": FULL_TOOL_PROMPT
    }


def get_capability_summary() -> str:
    """Get a short summary of capabilities."""
    return """I have access to:
- File operations (read, write, scaffold projects)
- Web research (search, deep research, academic)
- Code tools (lint, format, test, security audit)
- DevOps (Git, Docker, CI/CD, deployment)
- 40+ specialist agents (frontend, backend, QA, content, etc.)
- Autonomous execution (multi-hour unsupervised work)
- Package security (blocks malware, typosquats)
"""


# Agent category summaries for routing
CATEGORY_CAPABILITIES = {
    "FRONTEND": "React, Vue, CSS, UI components, responsive design, animations",
    "BACKEND": "FastAPI, Flask, databases, APIs, authentication, Python",
    "ARCHITECTURE": "System design, tech decisions, product strategy, roadmaps",
    "RESEARCH": "Web search, academic papers, competitive analysis, synthesis",
    "QA": "Code review, testing, security audits, bug detection",
    "OPS": "Git, GitHub, Docker, deployment, CI/CD, terminal",
    "CONTENT": "Blog posts, emails, documentation, pitch decks, PDFs",
    "PRODUCTIVITY": "Email, calendar, Slack, daily briefings, reminders",
    "CORE": "Orchestration, memory, context management, autonomous mode"
}


def get_category_for_task(task: str) -> str:
    """Determine which category is best for a task."""
    task_lower = task.lower()
    
    # Keywords to category mapping
    mappings = [
        (["react", "vue", "css", "ui", "component", "frontend", "design", "style"], "FRONTEND"),
        (["api", "backend", "database", "server", "python", "flask", "fastapi", "auth"], "BACKEND"),
        (["architecture", "system design", "plan", "strategy", "roadmap"], "ARCHITECTURE"),
        (["research", "find", "search", "investigate", "study", "analysis"], "RESEARCH"),
        (["test", "qa", "review", "audit", "security", "bug", "fix"], "QA"),
        (["deploy", "git", "docker", "push", "commit", "terminal", "run"], "OPS"),
        (["write", "content", "blog", "email", "document", "pdf", "deck"], "CONTENT"),
        (["email", "calendar", "schedule", "meeting", "slack", "briefing"], "PRODUCTIVITY"),
    ]
    
    for keywords, category in mappings:
        if any(kw in task_lower for kw in keywords):
            return category
    
    return "CORE"
