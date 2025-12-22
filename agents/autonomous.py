"""
Autonomous Executor for Jarvis v2
Self-healing, self-orchestrating execution loop.

"Can't outsmart the AI, but we can out-work it, out-tool it"
"""
import os
import re
import time
from datetime import datetime
from typing import Callable, Dict, List, Optional, Any
from .recycler import recycler
from .router import router
from .coder import coder
from .research import researcher
from .context_manager import context
from .config import WORKSPACE_DIR
from .qa import qa_agent
from .project_manager import project_manager
from .terminal import terminal
from .code_indexer import code_indexer
from .design_creativity import design_creativity
from .visual_qa import visual_qa
from .prompt_refiner import prompt_refiner

# Additional specialist agents for routing
from .code_reviewer import code_reviewer
from .security_auditor import security_auditor
from .brute_research import brute_researcher
from .synthesis import synthesizer

# New specialized development agents
from .frontend_dev import frontend_dev
from .backend_dev import backend_dev
from .ai_ops import ai_ops
from .strategy import strategy
from .architect import architect
from .product_manager import product_manager
from .uiux import uiux
from .seo import seo_specialist

# Context-segregated registry
from .registry import registry, get_context_for_agent, save_context

# NEW: On-demand context retrieval (RAG-style)
from .context_retriever import context_retriever, get_context

# NEW: Autonomy utilities
from .utils.checkpoint import checkpoint_manager
from .utils.escalation import escalation_manager, should_escalate
from .utils.error_journal import error_journal, log_error, get_avoid_instructions
from .utils.hierarchical_planner import hierarchical_planner

# NEW: Project builder for cohesive file generation
from .project_builder import project_builder

# NEW: Live logging for real-time visibility
from .utils.live_logger import live_logger


class AutonomousExecutor:
    """
    Self-healing autonomous execution loop.
    
    Features:
    - Automatic context recycling at 75%
    - Domain-segregated memory
    - Self-generated continuation prompts
    - Progress tracking across recycles
    - PAUSE/RESUME capability
    - Mid-flow plan modification
    """
    
    def __init__(self):
        self.is_running = False
        self.is_paused = False  # NEW: Pause state
        self.current_task = None
        self.current_objective = ""  # Store the objective for reference
        self.iteration = 0
        self.max_iterations = 200  # Increased for overnight work
        self.log = []
        self.progress_callback = None
        
        # Pause/Resume state
        self.pause_requested = False
        self.resume_event = None  # Will be threading.Event()
        self.pause_reason = ""
        self.pending_modifications = []  # Plan changes during pause
        self.saved_state = {}  # State snapshot on pause
    
    def pause(self, reason: str = "User requested pause") -> Dict:
        """
        Pause execution at the next safe point.
        Returns current state.
        """
        if not self.is_running:
            return {"success": False, "error": "Not currently running"}
        
        self.pause_requested = True
        self.pause_reason = reason
        self._log(f"⏸️ Pause requested: {reason}")
        
        return {
            "success": True,
            "message": "Will pause after current step completes",
            "current_step": self.iteration,
            "reason": reason
        }
    
    def resume(self, modifications: List[str] = None) -> Dict:
        """
        Resume paused execution, optionally with plan modifications.
        
        Args:
            modifications: List of changes to apply to the plan
        """
        if not self.is_paused:
            return {"success": False, "error": "Not currently paused"}
        
        if modifications:
            self.pending_modifications.extend(modifications)
            self._log(f"📝 {len(modifications)} modifications queued")
        
        self.is_paused = False
        self.pause_requested = False
        
        # Signal resume if using threading
        if self.resume_event:
            self.resume_event.set()
        
        self._log("▶️ Resuming execution")
        
        return {
            "success": True,
            "message": "Execution resumed",
            "modifications_applied": len(modifications) if modifications else 0
        }
    
    def get_state(self) -> Dict:
        """Get current execution state (useful when paused)."""
        from .recycler import recycler
        progress = recycler.get_progress()
        
        return {
            "is_running": self.is_running,
            "is_paused": self.is_paused,
            "pause_reason": self.pause_reason if self.is_paused else None,
            "current_iteration": self.iteration,
            "max_iterations": self.max_iterations,
            "objective": progress.get("objective", ""),
            "completed_steps": progress.get("completed_steps", []),
            "pending_steps": progress.get("pending_steps", []),
            "percent_complete": progress.get("percent", 0),
            "pending_modifications": self.pending_modifications,
            "log_tail": self.log[-10:] if self.log else []
        }
    
    def modify_plan(self, action: str, step: str = None, position: int = None) -> Dict:
        """
        Modify the execution plan mid-flow.
        
        Args:
            action: "add", "remove", "insert", "replace"
            step: The step text
            position: For insert, where to insert
        """
        from .recycler import recycler
        
        if action == "add":
            recycler.pending_steps.append(step)
            self._log(f"📌 Added step: {step}")
        elif action == "remove" and step:
            if step in recycler.pending_steps:
                recycler.pending_steps.remove(step)
                self._log(f"❌ Removed step: {step}")
        elif action == "insert" and position is not None:
            recycler.pending_steps.insert(position, step)
            self._log(f"📍 Inserted step at {position}: {step}")
        elif action == "replace" and position is not None:
            if position < len(recycler.pending_steps):
                old = recycler.pending_steps[position]
                recycler.pending_steps[position] = step
                self._log(f"🔄 Replaced step {position}: {old} → {step}")
        
        return {"success": True, "pending_steps": recycler.pending_steps}
    
    def add_note(self, note: str) -> Dict:
        """Add a note to the execution log (useful during pause)."""
        self._log(f"📝 Note: {note}")
        
        # Also save to memory
        from .memory import memory
        memory.save_fact(note, category="execution_notes")
        
        return {"success": True}
    
    def _check_pause(self) -> bool:
        """
        Check if we should pause. Called between steps.
        Returns True if paused, False to continue.
        """
        if self.pause_requested:
            self.is_paused = True
            self.pause_requested = False
            
            # Save state
            from .recycler import recycler
            self.saved_state = {
                "iteration": self.iteration,
                "progress": recycler.get_progress(),
                "timestamp": datetime.now().isoformat()
            }
            
            self._log(f"⏸️ PAUSED at step {self.iteration}")
            self._log(f"   Reason: {self.pause_reason}")
            self._log("   Use executor.resume() to continue")
            self._log("   Use executor.modify_plan() to change steps")
            
            # If using threading, wait for resume
            if self.resume_event:
                import threading
                self.resume_event = threading.Event()
                self.resume_event.wait()  # Block until resumed
            
            return True
        
        return False
    
    def _apply_pending_modifications(self):
        """Apply any modifications queued during pause."""
        if self.pending_modifications:
            self._log(f"📝 Applying {len(self.pending_modifications)} modifications")
            for mod in self.pending_modifications:
                # Parse modification string
                if mod.startswith("add:"):
                    self.modify_plan("add", mod[4:].strip())
                elif mod.startswith("remove:"):
                    self.modify_plan("remove", mod[7:].strip())
            self.pending_modifications = []
    
    def _log(self, msg: str):
        """Log with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {msg}"
        self.log.append(entry)
        
        # Safe printing for Windows consoles
        try:
            print(entry, flush=True)
        except UnicodeEncodeError:
            # Fallback: remove non-ascii chars if console can't handle them
            safe_msg = msg.encode('ascii', 'ignore').decode('ascii')
            safe_entry = f"[{timestamp}] {safe_msg}"
            print(safe_entry, flush=True)
            
        if self.progress_callback:
            self.progress_callback(msg)
    
    def _call_llm(self, prompt: str, max_tokens: int = None) -> str:
        """Make LLM call through base agent with optional token limit."""
        from .base_agent import BaseAgent
        from .config import TOKEN_LIMITS
        
        # Default to standard limit if not specified
        tokens = max_tokens or TOKEN_LIMITS["standard"]
        
        class TempAgent(BaseAgent):
            def __init__(self):
                super().__init__("autonomous")
            def _get_system_prompt(self):
                return "You are Jarvis, an autonomous AI assistant completing a multi-step task."
            def run(self, task: str) -> str:
                return self.call_llm(task)
        
        agent = TempAgent()
        return agent.call_llm(prompt, max_tokens=tokens)
    
    def _check_completion(self, response: str) -> bool:
        """Check if task is complete based on EXPLICIT completion signal in response."""
        # VERY SPECIFIC signals that the LLM must explicitly output
        # Generic terms like "done" trigger false positives
        completion_signals = [
            "[task complete]",
            "[all steps complete]",
            "[project finished]",
            "jarvis: task complete",
            "=== task complete ===",
            "[completion]",
        ]
        response_lower = response.lower()
        
        # Only trigger if signal appears at start of a line or is bracketed
        for signal in completion_signals:
            if signal in response_lower:
                return True
        
        return False
    
    def _validate_output(self, content: str, task_type: str) -> dict:
        """Validate output quality - reject placeholder-filled content."""
        issues = []
        
        # Check for common placeholders that indicate template output
        placeholders = [
            "[Company Name]", "[Your Name]", "[Your Company]",
            "[specific initiative", "[TODO", "[PLACEHOLDER",
            "[Company]", "[Name]", "[Contact]"
        ]
        
        for p in placeholders:
            if p in content:
                issues.append(f"Contains placeholder: {p}")
        
        # For analysis tasks, require actual data usage
        if task_type == "analysis":
            if content.count("[") > 10:  # Too many brackets suggests templates
                issues.append("Too many bracket placeholders for analysis output")
        
        if issues:
            self._log(f"  ⚠️ OUTPUT QUALITY ISSUES: {', '.join(issues)}")
            return {"valid": False, "issues": issues}
        
        return {"valid": True, "issues": []}
    
    def _detect_domain(self, content: str) -> str:
        """Detect which domain the content belongs to."""
        content_lower = content.lower()
        
        if any(kw in content_lower for kw in ["react", "component", "jsx", "css", "html", "ui", "frontend", "page"]):
            return "frontend"
        elif any(kw in content_lower for kw in ["api", "route", "server", "endpoint", "express", "backend"]):
            return "backend"
        elif any(kw in content_lower for kw in ["database", "schema", "table", "sql", "supabase", "migration"]):
            return "database"
        elif any(kw in content_lower for kw in ["market", "competitor", "research", "trend", "analysis"]):
            return "research"
        else:
            return "decisions"
    
    def _detect_task_type(self, objective: str) -> str:
        """
        Detect what type of task this is for appropriate handling.
        Supports coding, research, writing, analysis, and general tasks.
        """
        obj_lower = objective.lower()
        
        # Coding tasks
        coding_keywords = [
            "build", "create", "develop", "code", "implement", "website", "app",
            "frontend", "backend", "api", "component", "page", "feature",
            "react", "python", "javascript", "html", "css", "database",
            "deploy", "fix bug", "refactor", "landing page", "saas"
        ]
        if any(kw in obj_lower for kw in coding_keywords):
            return "coding"
        
        # Research tasks
        research_keywords = [
            "research", "investigate", "find out", "look into", "analyze market",
            "competitor analysis", "industry trends", "gather information",
            "what is", "how does", "why do", "explore options"
        ]
        if any(kw in obj_lower for kw in research_keywords):
            return "research"
        
        # Writing tasks
        writing_keywords = [
            "write", "draft", "compose", "create content", "blog post",
            "article", "email", "pitch", "proposal", "documentation",
            "copy", "script", "outline", "summary"
        ]
        if any(kw in obj_lower for kw in writing_keywords):
            return "writing"
        
        # Analysis tasks
        analysis_keywords = [
            "analyze", "evaluate", "assess", "compare", "review",
            "audit", "measure", "calculate", "forecast", "model",
            "data analysis", "metrics", "performance"
        ]
        if any(kw in obj_lower for kw in analysis_keywords):
            return "analysis"
        
        # Default to general
        return "general"
    
    def _extract_component_name(self, step: str) -> str:
        """Extract a clean component name from a step description for file naming."""
        if not step or step == "unknown":
            return "component"
        
        # Look for [COMPONENT: Name] pattern
        import re
        component_match = re.search(r'\[COMPONENT[:\s]+([^\]]+)\]', step, re.IGNORECASE)
        if component_match:
            name = component_match.group(1).strip()
        else:
            # Extract key words from step
            name = step
        
        # Clean up the name for filesystem
        # Take first few meaningful words
        words = re.findall(r'[a-zA-Z]+', name)
        if words:
            # Take up to 3 words, make lowercase, join with hyphen
            clean_words = [w.lower() for w in words[:3] if len(w) > 2]
            return "-".join(clean_words) if clean_words else "component"
        
        return "component"
    
    def _route_to_specialist(self, step: str, task_type: str, project_path: str) -> Dict:
        """
        Route a step to the appropriate specialist agent.
        NOW USES: On-demand context retrieval (RAG-style) instead of pre-loading domains.
        """
        step_lower = step.lower()
        step_upper = step.upper()
        
        # Get context on-demand using the new retriever
        # This asks the LLM which files are needed instead of pre-loading everything
        context = get_context(step, agent=task_type, project=project_path)
        
        # === COMPONENT STEPS: Direct LLM for complete modules ===
        if "[COMPONENT" in step_upper or "complete module" in step_lower:
            return {
                "agent": "component_builder", 
                "category": "FRONTEND",
                "use_specialist": False,
                "context": context  # On-demand context instead of domains
            }
        
        # === ARCHITECTURE STEPS: Direct LLM for design docs ===
        if "[ARCHITECTURE" in step_upper or "system design" in step_lower:
            return {
                "agent": "architect",
                "category": "ARCHITECTURE", 
                "use_specialist": True,
                "context": context
            }
        
        # === INTEGRATION STEPS: Direct LLM for connecting modules ===
        if "[INTEGRATION" in step_upper:
            return {
                "agent": "integrator",
                "category": "FRONTEND",
                "use_specialist": False,
                "context": context
            }
        
        # === Route by keywords to categories ===
        routing_rules = {
            "FRONTEND": {
                "keywords": ["ui", "component", "page", "css", "style", "react", "animation", "frontend", "responsive"],
                "default_agent": "frontend_dev"
            },
            "BACKEND": {
                "keywords": ["api", "endpoint", "database", "auth", "backend", "server", "crud", "rest", "graphql"],
                "default_agent": "backend_dev"
            },
            "RESEARCH": {
                "keywords": ["research", "investigate", "find", "search", "analyze", "paper", "academic", "cite"],
                "default_agent": "brute_researcher"
            },
            "QA": {
                "keywords": ["test", "qa", "quality", "debug", "fix bug", "error", "lint", "review"],
                "default_agent": "qa_agent"
            },
            "OPS": {
                "keywords": ["deploy", "docker", "kubernetes", "ci/cd", "production", "github", "push"],
                "default_agent": "ops"
            },
            "CONTENT": {
                "keywords": ["write", "document", "blog", "content", "seo", "readme"],
                "default_agent": "content_writer"
            }
        }
        
        # Match category
        for category, config in routing_rules.items():
            if any(kw in step_lower for kw in config["keywords"]):
                return {
                    "agent": config["default_agent"],
                    "category": category,
                    "use_specialist": True,
                    "context": context  # On-demand context
                }
        
        # Default: use LLM directly with minimal context
        return {
            "agent": "general",
            "category": "CORE", 
            "use_specialist": False,
            "context": context
        }
    
    def _call_specialist(self, agent_name: str, step: str, project_path: str, context: str) -> str:
        """Call a specialist agent with the step and context."""
        self._log(f"  -> Routing to: {agent_name}")
        
        try:
            if agent_name == "coder":
                # Use coder agent
                result = coder.run(step, project_path if os.path.exists(project_path) else None)
                return result
                
            elif agent_name == "code_reviewer":
                # Use code reviewer
                result = code_reviewer.run(project_path)
                return str(result)
                
            elif agent_name == "qa":
                # Use QA agent
                result = qa_agent.run(project_path)
                return str(result)
                
            elif agent_name == "security":
                # Use security auditor
                result = security_auditor.run(project_path)
                return str(result)
                
            elif agent_name == "research":
                # Use brute researcher
                result = brute_researcher.run(step)
                return str(result)
                
            else:
                # Fallback to LLM
                return self._call_llm(f"Execute this step: {step}\n\nContext: {context[:2000]}")
                
        except Exception as e:
            self._log(f"  Specialist error: {e}")
            # Fallback to LLM on error
            return self._call_llm(f"Execute this step: {step}\n\nContext: {context[:2000]}")
    
    def _extract_and_save_code(self, result: str, project_name: str) -> List[str]:
        """
        Extract code blocks from LLM output and save to proper files.
        Handles both:
        1. Code blocks with explicit filenames: ```jsx filename="App.jsx"
        2. Concatenated code with comment markers: // src/components/Sidebar.tsx
        """
        import re
        import os
        
        saved_files = []
        
        # Get or create project using project_builder
        if not project_builder.project_path or project_name not in str(project_builder.project_path or ""):
            objective = recycler.task_objective or ""
            template = "react" if any(kw in objective.lower() for kw in ["react", "next", "jsx", "tsx"]) else "vanilla"
            project_builder.create_project(project_name, template=template)
        
        project_path = project_builder.project_path
        
        # FIRST: Try to split by comment markers (// src/filename.ext or # src/filename.ext)
        file_pattern = r'(?:\/\/|#)\s*(src\/[^\n]+\.(?:tsx?|jsx?|css|py|json|md))\s*\n'
        splits = re.split(file_pattern, result)
        
        if len(splits) > 2:
            # We have comment-based splits
            self._log(f"  -> Detected {len(splits)//2} embedded files")
            i = 1
            while i < len(splits) - 1:
                filename = splits[i].strip()
                content = splits[i + 1].strip()
                
                # Clean up content - remove trailing ```
                if content.endswith('```'):
                    content = content[:-3].strip()
                
                # Remove leading ``` with language
                if content.startswith('```'):
                    lines = content.split('\n', 1)
                    content = lines[1] if len(lines) > 1 else ""
                
                if content and filename:
                    full_path = os.path.join(project_path, filename)
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    saved_files.append(filename)
                    self._log(f"  -> Saved: {filename} ({len(content)} chars)")
                
                i += 2
            
            return saved_files
        
        # SECOND: Try explicit filename in code blocks
        code_pattern = r'```(\w+)(?:\s+filename=["\']([^"\']+)["\'])?\n([\s\S]*?)```'
        matches = re.findall(code_pattern, result)
        
        if matches:
            for lang, filename, code in matches:
                lang = lang.lower()
                code = code.strip()
                
                if not code:
                    continue
                
                # Determine target file
                if filename:
                    target_file = filename
                else:
                    ext_map = {
                        'jsx': 'src/App.jsx', 'tsx': 'src/App.tsx',
                        'css': 'src/index.css', 'html': 'index.html',
                        'javascript': 'src/main.js', 'js': 'src/main.js',
                        'python': 'main.py', 'py': 'main.py',
                        'json': 'data.json', 'typescript': 'src/main.ts', 'ts': 'src/main.ts'
                    }
                    target_file = ext_map.get(lang, f'src/generated.{lang}')
                
                full_path = os.path.join(project_path, target_file)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
                # FIXED: Always overwrite to prevent duplicate code fragments
                # Each step should produce COMPLETE code, not append fragments
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(code)
                
                saved_files.append(target_file)
                self._log(f"  -> Saved: {target_file} ({len(code)} chars)")
        
        return saved_files
    
    def _update_file_index(self, project_name: str, files: List[str]):
        """Track generated files in an index for the AI to reference."""
        from .config import WORKSPACE_DIR
        
        index_path = os.path.join(WORKSPACE_DIR, project_name, ".file_index.json")
        
        # Load existing index
        existing = []
        if os.path.exists(index_path):
            try:
                import json
                with open(index_path, 'r') as f:
                    existing = json.load(f)
            except:
                existing = []
        
        # Add new files
        for f in files:
            if f not in existing:
                existing.append(f)
        
        # Save updated index
        import json
        with open(index_path, 'w') as f:
            json.dump(existing, f, indent=2)
    
    def _auto_run_project(self, project_path: str) -> Dict:
        """
        Automatically install dependencies and start dev server.
        Returns: Dict with status, port, and any errors.
        """
        import subprocess
        import time
        
        result = {"success": False, "port": None, "error": None, "process": None}
        
        # Check if package.json exists
        package_json = os.path.join(project_path, "package.json")
        if not os.path.exists(package_json):
            result["error"] = "No package.json found"
            return result
        
        self._log("[AutoRun] Installing dependencies...")
        
        try:
            # Run npm install
            install_result = subprocess.run(
                ["npm", "install"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=300,  # 5 min timeout
                shell=True
            )
            
            if install_result.returncode != 0:
                result["error"] = f"npm install failed: {install_result.stderr[:500]}"
                self._log(f"[AutoRun] npm install failed: {install_result.stderr[:200]}")
                return result
            
            self._log("[AutoRun] Dependencies installed. Starting dev server...")
            
            # Start dev server in background
            dev_process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=project_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True
            )
            
            # Wait a bit for server to start
            time.sleep(5)
            
            # Check if process is still running
            if dev_process.poll() is None:
                result["success"] = True
                result["port"] = 5173  # Vite default
                result["process"] = dev_process
                self._log(f"[AutoRun] ✅ Dev server running on port {result['port']}")
            else:
                stdout, stderr = dev_process.communicate()
                result["error"] = f"Dev server crashed: {stderr.decode()[:500]}"
                self._log(f"[AutoRun] ❌ Dev server failed")
            
        except subprocess.TimeoutExpired:
            result["error"] = "npm install timed out"
        except Exception as e:
            result["error"] = str(e)
            self._log(f"[AutoRun] Error: {e}")
        
        return result
    
    def _execute_with_recovery(self, step: str, context: str, max_retries: int = 2) -> str:
        """
        Execute a step with automatic error recovery.
        If execution fails, retry with error context.
        """
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                # Add error context if this is a retry
                if last_error:
                    context += f"\n\n[PREVIOUS ERROR - PLEASE FIX]: {last_error}"
                    self._log(f"  Retry {attempt}/{max_retries} with error context")
                
                result = self._execute_step(step, context)
                
                # Check for obvious errors in response
                if "[Error:" in result or "[LLM Error" in result:
                    last_error = result
                    continue
                
                return result
                
            except Exception as e:
                last_error = str(e)
                self._log(f"  !!! ERROR: {e} !!!")
                
                if attempt == max_retries:
                    return f"[FAILED after {max_retries + 1} attempts: {last_error}]"
        
        return f"[FAILED: {last_error}]"
    
    def _capture_preview(self, port: int = 5173) -> str:
        """
        Capture a screenshot of the running dev server.
        Returns: Path to saved screenshot.
        """
        try:
            from playwright.sync_api import sync_playwright
            import time
            
            screenshot_path = os.path.join(WORKSPACE_DIR, "screenshots", f"preview_{int(time.time())}.png")
            os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(viewport={"width": 1280, "height": 720})
                page.goto(f"http://localhost:{port}", wait_until="networkidle", timeout=30000)
                page.screenshot(path=screenshot_path)
                browser.close()
            
            self._log(f"[Preview] Screenshot saved: {screenshot_path}")
            return screenshot_path
            
        except Exception as e:
            self._log(f"[Preview] Failed to capture: {e}")
            return None
    
    def _audit_dependencies(self, project_path: str, saved_files: list) -> list:
        """
        Scan saved Python files for local imports and verify they exist.
        Returns a list of missing module names.
        """
        import re
        missing = []
        standard_libs = {'os', 'sys', 'json', 'time', 'datetime', 're', 'random', 
                         'math', 'collections', 'itertools', 'functools', 'typing',
                         'pathlib', 'subprocess', 'threading', 'multiprocessing',
                         'requests', 'numpy', 'pandas', 'networkx', 'matplotlib'}
        
        for filename in saved_files:
            if not filename.endswith('.py'):
                continue
            
            # Find the file path
            filepath = None
            for root, dirs, files in os.walk(project_path):
                if filename in files:
                    filepath = os.path.join(root, filename)
                    break
            
            if not filepath or not os.path.exists(filepath):
                continue
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse import statements
                # Match: import X, from X import Y
                import_pattern = r'^(?:from\s+(\w+)|import\s+(\w+))'
                for match in re.finditer(import_pattern, content, re.MULTILINE):
                    module_name = match.group(1) or match.group(2)
                    
                    # Skip standard library and known packages
                    if module_name in standard_libs:
                        continue
                    
                    # Check if local module exists
                    potential_path = os.path.join(project_path, f"{module_name}.py")
                    src_path = os.path.join(project_path, "src", f"{module_name}.py")
                    
                    if not os.path.exists(potential_path) and not os.path.exists(src_path):
                        if module_name not in missing:
                            missing.append(module_name)
            except Exception as e:
                self._log(f"[DependencyAudit] Error parsing {filename}: {e}")
        
        return missing
    
    def _get_project_name(self, objective: str) -> str:
        """Generate a project folder name from the objective."""
        import re
        # Extract key words and create short name
        words = re.findall(r'\b\w+\b', objective.lower())
        keywords = [w for w in words if len(w) > 3 and w not in ['build', 'create', 'make', 'with', 'that', 'this', 'from', 'using']]
        name = '-'.join(keywords[:3]) if keywords else 'project'
        return name.replace(' ', '-')[:30]
    
    def _execute_step(self, step: str, task_context: str) -> str:
        """Execute a single step with smart context and terminal integration."""
        self._log(f"Executing: {step}")
        
        # Get the ORIGINAL objective - this prevents hallucination
        original_objective = recycler.task_objective
        
        # Detect task type
        task_type = self._detect_task_type(original_objective)
        
        project_name = self._get_project_name(original_objective)
        project_path = os.path.join(WORKSPACE_DIR, "projects", project_name)

        # Route to specialist
        routing = self._route_to_specialist(step, task_type, project_path)
        
        # Execute via specialist
        if routing["use_specialist"]:
            response = self._call_specialist(
                routing["agent"], 
                step, 
                project_path, 
                routing["context"]
            )
        else:
            # Direct LLM execution
            response = self._call_llm(
                f"Project: {project_path}\nObjective: {original_objective}\nStep: {step}\n\nContext: {routing['context'][:3000]}"
            )

        # CRITICAL: Auto-Save Supervisor (Fix for 'Lost in RAM' bug)
        # Capture artifacts immediately after generation
        saved_files = self._extract_and_save_code(response, project_name)
        if saved_files:
            response += f"\n\n[SYSTEM: Auto-saved {len(saved_files)} files: {', '.join(saved_files)}]"
        
        # === DEVILS ADVOCATE REVIEW (The "Integrity Check") ===
        # Mandatory audit for coding and research tasks
        if task_type in ["coding", "research"] and "critical" not in step.lower():
            from .devils_advocate import devils_advocate
            
            # Pass the list of ACTUAL saved files to the Devil so it can catch hallucinations
            reality_context = f"Project: {project_name}\nFiles Saved This Turn: {json.dumps(saved_files) if saved_files else 'NONE'}"
            
            critique = devils_advocate.critique(response, content_type=task_type, context=reality_context)
            
            if critique["verdict"] in ["FIX_REQUIRED", "REVIEW_REQUIRED"]:
                self._log(f"😈 DEVIL REJECTED: {len(critique['issues'])} issues found.")
                
                # Filter for just the serious ones
                blockers = [i for i in critique['issues'] if i['risk'] in ['critical', 'major']]
                
                if blockers:
                    feedback = "Your previous work was REJECTED by the Quality Assurance system.\n\n"
                    for i in blockers:
                        feedback += f"- [CRITICAL] {i['title']}: {i['description']}\n  Fix: {i['fix']}\n\n"
                    feedback += "You must RE-WRITE your response to fix these errors immediately.\nDo not apologize, just provide the corrected output."
                    
                    self._log("  -> Forcing retry with critique feedback...")
                    # Retry with feedback
                    response = self._call_llm(feedback)
                    
                    # Auto-save again for the fixed version
                    new_saved = self._extract_and_save_code(response, project_name)
                    if new_saved:
                        response += f"\n\n[SYSTEM: Auto-saved fixes: {', '.join(new_saved)}]"
            else:
                self._log("😇 DEVIL APPROVED: No critical issues.")
        
        # === DEPENDENCY AUDITOR (The "Lab Work" Enforcer) ===
        # Check if saved Python files import modules that don't exist
        if saved_files:
            missing_deps = self._audit_dependencies(project_path, saved_files)
            if missing_deps:
                self._log(f"🔬 DEPENDENCY AUDIT: {len(missing_deps)} missing modules detected: {missing_deps}")
                # Force the agent to write these modules NOW
                for missing_module in missing_deps:
                    dep_prompt = f"""CRITICAL: Your code imports '{missing_module}' but this file does not exist.
You MUST implement '{missing_module}.py' NOW with all the functions your code expects.
Project path: {project_path}

Output the full Python code block for '{missing_module}.py'. No explanations, just the code."""
                    self._log(f"  -> Forcing implementation of: {missing_module}.py")
                    dep_response = self._call_llm(dep_prompt)
                    new_saved = self._extract_and_save_code(dep_response, self._get_project_name(original_objective))
                    if new_saved:
                        response += f"\\n\\n[SYSTEM: Auto-generated dependency: {', '.join(new_saved)}]"

        return response
        # Ensure project exists
        if not os.path.exists(project_path):
            project_manager.create_project(project_name, stack="vanilla", category="frontend")
        
        # === SPECIALIST ROUTING: Route to the right agent ===
        routing = self._route_to_specialist(step, task_type, project_path)
        
        if routing["use_specialist"]:
            # Use specialist agent
            task_context_short = task_context[:1500] if task_context else ""
            result = self._call_specialist(routing["agent"], step, project_path, task_context_short)
            
            # Still extract and save any code from specialist output
            saved_files = self._extract_and_save_code(result, project_name)
            if saved_files:
                self._log(f"  Created {len(saved_files)} files in {project_name}/")
                code_indexer.index_project(project_path)
                
                # Auto-run project if we have multiple files (looks like a complete project)
                if len(saved_files) >= 3 and any(f.endswith(('.jsx', '.tsx', '.html')) for f in saved_files):
                    run_result = self._auto_run_project(project_path)
                    if run_result["success"]:
                        # Capture preview screenshot
                        screenshot = self._capture_preview(run_result.get("port", 5173))
                        if screenshot:
                            self._log(f"  📸 Preview captured: {screenshot}")
            
            # Save result to domain and mark complete
            domain = self._detect_domain(result)
            recycler.save_to_domain(domain, f"### {step}\n{result[:2000]}")
            recycler.mark_step_complete(step, result[:500])
            
            return result
        
        # === FALLBACK: Use LLM directly for planning/general steps ===
        
        # === SMART CONTEXT: Only relevant files, not everything ===
        code_context = ""
        if os.path.exists(project_path) and task_type == "coding":
            code_context = code_indexer.get_relevant_context(project_path, step, max_tokens=2000)
        
        # Build context section
        context_section = ""
        if code_context:
            context_section = f"### Relevant Project Files:\n{code_context}"
        
        # Build prompt with STRONG objective reinforcement to prevent hallucination
        prompt = f"""# YOUR MISSION
You are executing a task for your user. Stay STRICTLY focused on this objective.

## OBJECTIVE (NEVER DEVIATE FROM THIS):
{original_objective}

## CURRENT STEP:
{step}

## TASK CONTEXT:
{task_context[:2500]}

{context_section}

## INSTRUCTIONS:
"""
        
        # Add task-specific instructions
        if task_type == "coding":
            # Check if this is a component/module step
            is_component = "[COMPONENT" in step.upper() or "module" in step.lower() or "build" in step.lower()
            
            if is_component:
                # COMPONENT MODE: Create complete, polished module
                prompt += f"""
## COMPONENT BUILDING MODE

You are building a COMPLETE, POLISHED component. Think of the premium landing page quality:
- 686 lines of polished HTML+CSS+JS in ONE file
- Glassmorphism, gradients, animations
- Fully functional with all features
- Dark theme with CSS variables
- Responsive design

FOR THIS STEP: {step}

CREATE A SINGLE COMPLETE FILE that includes:
1. All HTML structure
2. All CSS (inline in <style> tags) with:
   - CSS variables for theme
   - glassmorphism effects
   - hover animations
   - responsive breakpoints
3. All JavaScript functionality
4. Mock data that looks realistic
5. Proper navigation

QUALITY CHECKLIST:
[ ] Dark theme with purple/cyan accents
[ ] Glassmorphism cards with backdrop-filter
[ ] Smooth hover transitions
[ ] Working CRUD operations (add/edit/delete)
[ ] Proper form handling
[ ] Loading states
[ ] Responsive layout

Output the COMPLETE file in a code block with proper filename.
Example: ```html filename="crm-contacts.html"
"""
            else:
                # Regular coding task
                prompt += f"""
- You are building: {original_objective}
- Create COMPLETE working code, not fragments
- Include inline styles for polished look
"""
            
            prompt += """
- Use proper code blocks: ```html filename="example.html"
- For commands, use: [COMMAND]: npm install, python test.py, etc.
- For file edits, use: [EDIT] filename: replace "old" with "new"
"""
        elif task_type == "research":
            prompt += """
- Provide comprehensive research findings
- Include sources and citations where possible
- Structure findings clearly with headers
- Highlight key insights and actionable items
"""
        elif task_type == "writing":
            prompt += """
- Write professional, engaging content
- Match the tone to the context
- Structure with clear sections
- Include any necessary formatting
"""
        elif task_type == "analysis":
            prompt += f"""
## ANALYSIS MODE - DATA REQUIRED

You are analyzing data for: {original_objective}

CRITICAL RULES:
1. You MUST read actual data files mentioned in the objective
2. For Excel files, use: [COMMAND]: python -c "import pandas as pd; df = pd.read_excel('path/to/file.xlsx'); print(df.head(50).to_string())"
3. Extract SPECIFIC names, numbers, and companies from the data
4. NEVER use placeholders like "[Company Name]" or "[Your Name]" - use REAL data
5. Personalize all output based on ACTUAL data read
6. Save outputs to the specified directory (create if needed)

QUALITY CHECKLIST:
[ ] Used actual company/contact names from data
[ ] No placeholder text anywhere
[ ] Actionable recommendations with specifics
[ ] Saved to correct output location

For file operations on Windows:
[COMMAND]: python -c "import os; os.makedirs('path', exist_ok=True)"
"""
        else:  # general
            prompt += """
- Complete this step thoroughly
- Be specific and actionable
- Include all relevant details
- State what was accomplished
"""
        
        prompt += f"""

## CRITICAL REMINDERS:
- You are working on: {original_objective}
- This is step: {step}
- Stay focused. Do NOT make up different product names or objectives.
- IMPORTANT: When updating a file, output the COMPLETE file including ALL previous content plus your additions.
- At the end, state what was accomplished for this step."""
        
        # === ADAPTIVE TOKEN LIMITS ===
        from .config import TOKEN_LIMITS
        
        # Choose token limit based on step and task type
        if "plan" in step.lower() or "analyze" in step.lower():
            token_limit = TOKEN_LIMITS["planning"]  # 4K - fast for planning
        elif "[COMPONENT" in step.upper() or "complete" in step.lower():
            token_limit = TOKEN_LIMITS["component"]  # 10K - for full components
        elif task_type == "analysis":
            token_limit = TOKEN_LIMITS["standard"]  # 6K - analysis needs detail
        else:
            token_limit = TOKEN_LIMITS["standard"]  # 6K default
        
        result = self._call_llm(prompt, max_tokens=token_limit)
        
        # === EXTRACT AND RUN COMMANDS ===
        commands = self._extract_commands(result)
        for cmd in commands:
            self._log(f"  Running: {cmd}")
            cmd_result = terminal.run(cmd, project_path)
            if cmd_result["success"]:
                self._log(f"  Command OK ({cmd_result['duration']}s)")
            else:
                self._log(f"  Command failed: {cmd_result['stderr'][:100]}")
        
        # === EXTRACT AND SAVE CODE ===
        saved_files = self._extract_and_save_code(result, project_name)
        
        if saved_files:
            self._log(f"  Created {len(saved_files)} files in {project_name}/")
            # Re-index the project after adding files
            code_indexer.index_project(project_path)
        
        # === HANDLE FILE EDITS ===
        edits = self._extract_file_edits(result)
        for edit in edits:
            edit_result = code_indexer.edit_file(
                project_path, 
                edit["file"], 
                edit["old"], 
                edit["new"]
            )
            if edit_result["success"]:
                self._log(f"  Edited: {edit['file']}")
            else:
                self._log(f"  Edit failed: {edit_result['error']}")
        
        # Save result to appropriate domain
        domain = self._detect_domain(result)
        recycler.save_to_domain(domain, f"### {step}\n{result[:2000]}")
        
        # Mark step complete
        recycler.mark_step_complete(step, result[:500])
        
        return result
    
    def _extract_commands(self, result: str) -> List[str]:
        """Extract commands from LLM output."""
        commands = []
        
        # Look for [COMMAND]: pattern
        cmd_pattern = r'\[COMMAND\]:\s*(.+?)(?:\n|$)'
        matches = re.findall(cmd_pattern, result, re.IGNORECASE)
        commands.extend(matches)
        
        # Also look for common command patterns in context
        # e.g., "Run `npm install`" or "Execute: npm run build"
        run_pattern = r'(?:run|execute)[:\s]+`?([^`\n]+)`?'
        matches = re.findall(run_pattern, result, re.IGNORECASE)
        for m in matches:
            cmd = m.strip()
            if cmd and len(cmd) < 100:  # Sanity check
                commands.append(cmd)
        
        return commands[:5]  # Limit to 5 commands per step
    
    def _extract_file_edits(self, result: str) -> List[Dict]:
        """Extract file edit instructions from LLM output."""
        edits = []
        
        # Look for edit patterns like:
        # [EDIT] file.py: replace "old" with "new"
        # Edit src/index.html: change "old content" to "new content"
        
        edit_pattern = r'\[EDIT\]\s*([^:]+):\s*(?:replace|change)\s*["\'](.+?)["\']\s*(?:with|to)\s*["\'](.+?)["\']'
        matches = re.findall(edit_pattern, result, re.IGNORECASE | re.DOTALL)
        
        for file_path, old_content, new_content in matches:
            edits.append({
                "file": file_path.strip(),
                "old": old_content,
                "new": new_content
            })
        
        return edits[:3]  # Limit to 3 edits per step
    
    
    def _run_qa_feedback(self, project_path: str, max_attempts: int = 2) -> Optional[Dict]:
        """
        Run QA on project and attempt auto-fix if issues found.
        This is the feedback loop that makes the AI self-correcting.
        """
        for attempt in range(max_attempts):
            # Run QA check
            qa_result = qa_agent.run(project_path)
            
            if qa_result["overall_status"] == "pass":
                if attempt > 0:
                    self._log(f"  [QA] Fixed after {attempt} attempt(s)")
                return qa_result
            
            # If errors found, try to fix them
            if qa_result["total_errors"] > 0:
                self._log(f"  [QA] Found {qa_result['total_errors']} errors - attempting fix...")
                
                # Generate fix prompt from QA results
                fix_prompt = qa_agent.generate_fix_prompt(qa_result)
                
                if fix_prompt:
                    # Ask LLM to fix the issues
                    fix_result = self._call_llm(fix_prompt)
                    
                    # Extract and apply fixed code
                    project_name = os.path.basename(project_path)
                    self._extract_and_save_code(fix_result, project_name)
                    
                    self._log(f"  [QA] Applied fixes, re-checking...")
            else:
                # Only warnings, no critical errors to fix
                self._log(f"  [QA] {qa_result['total_warnings']} warnings (not critical)")
                return qa_result
        
        self._log(f"  [QA] Max attempts reached")
        return qa_result
    
    def _plan_steps(self, objective: str) -> List[str]:
        """
        Plan steps using COMPONENT-FOCUSED approach.
        Each step produces a COMPLETE, POLISHED module - not shallow fragments.
        """
        self._log("Planning steps...")
        
        # Detect if this is a large/complex project
        complex_keywords = ["os", "system", "platform", "ecosystem", "full", "complete", 
                           "entire", "everything", "crm", "dashboard", "app", "application",
                           "business", "enterprise", "management"]
        is_complex = any(kw in objective.lower() for kw in complex_keywords)
        
        if is_complex:
            prompt = f"""You are an expert software architect planning a PRODUCTION system.

OBJECTIVE: {objective}

CRITICAL RULES:
1. Each step must produce a COMPLETE, WORKING module - not fragments
2. Think like building the premium-landing-page: One polished file with HTML+CSS+JS
3. Each component should work STANDALONE before integration
4. Quality > Quantity. 10 polished components beats 50 half-done files

PLANNING FORMAT:

PHASE 1: ARCHITECTURE (Steps 1-3)
Step 1: [ARCHITECTURE] Create complete system design document with data models, API specs, file structure
Step 2: [ARCHITECTURE] Define component boundaries and integration points
Step 3: [ARCHITECTURE] Create project skeleton with proper folder structure

PHASE 2: CORE MODULES (Steps 4-N, one per major feature)
Step 4: [COMPONENT: Feature Name] Build COMPLETE module with full HTML/CSS/JS, dark theme, all CRUD operations, polished UI
Step 5: [COMPONENT: Feature Name] Build COMPLETE module...
(Continue for each major feature requested)

PHASE 3: INTEGRATION (Final steps)
Step N-2: [INTEGRATION] Connect all modules with shared navigation and state
Step N-1: [TESTING] Test all features work together
Step N: [POLISH] Final UI polish, responsive design, accessibility

IMPORTANT:
- Each [COMPONENT] step should create ONE complete, polished module
- Use the SAME quality level as a premium landing page (glassmorphism, animations, dark theme)
- Include ALL functionality for that component in ONE step
- Do NOT split styling and logic into separate steps

Now plan for: {objective}

Output numbered steps with phase headers. Aim for 10-20 high-quality steps."""
            max_steps = 25
        else:
            prompt = f"""Break down this objective into concrete steps:

OBJECTIVE: {objective}

RULES:
- Each step should produce something COMPLETE and WORKING
- Don't split "Create component" and "Add styling" - combine them
- Quality over quantity

Output a numbered list of 5-10 specific steps.
Format: Just the numbered list."""
            max_steps = 10
        
        response = self._call_llm(prompt)
        
        # Debug: log raw response length
        self._log(f"  [Planner] Got {len(response)} chars response")
        
        # Parse steps from response - handle multiple formats
        steps = []
        import re
        
        for line in response.split("\n"):
            line = line.strip()
            if not line or len(line) < 10:
                continue
            
            # Match numbered lists: "1.", "1)", "Step 1:", etc.
            if line[0].isdigit() or line.startswith("-") or line.startswith("*"):
                step = re.sub(r'^[\d\.\)\-\*\s]+', '', line).strip()
                if step.startswith("Step"):
                    step = re.sub(r'^Step\s*\d*[:\.]?\s*', '', step).strip()
                if step and len(step) > 10:
                    steps.append(step)
            
            # Match markdown headers: "## Step 1: Create..."
            elif line.startswith("#"):
                step = re.sub(r'^#+\s*', '', line).strip()
                step = re.sub(r'^[\d\.\)\s]+', '', step).strip()
                step = re.sub(r'^Step\s*\d*[:\.]?\s*', '', step).strip()
                if step and len(step) > 10:
                    steps.append(step)
            
            # Match bold markers: "**Step 1:**" 
            elif line.startswith("**"):
                step = re.sub(r'^\*+\s*', '', line).strip()
                step = re.sub(r'\*+$', '', step).strip()
                step = re.sub(r'^Step\s*\d*[:\.]?\s*', '', step).strip()
                if step and len(step) > 10:
                    steps.append(step)
        
        # Fallback: if no steps found, split by sentences and take actionable ones
        if not steps:
            self._log(f"  [Planner] Fallback parsing...")
            sentences = re.split(r'[.!?]\s+', response)
            action_words = ['create', 'build', 'implement', 'add', 'design', 'develop', 'setup', 'configure']
            for sent in sentences:
                sent = sent.strip()
                if len(sent) > 20 and any(word in sent.lower() for word in action_words):
                    steps.append(sent[:200])
                    if len(steps) >= 10:
                        break
        
        self._log(f"Planned {len(steps)} component milestones")
        return steps[:max_steps]
    
    def run(self, objective: str, progress_callback: Callable = None) -> Dict:
        """
        Run the autonomous execution loop.
        
        Args:
            objective: What to accomplish
            progress_callback: Function to call with progress updates
        
        Returns:
            Final result with logs and artifacts
        """
        self.progress_callback = progress_callback
        self.is_running = True
        self.iteration = 0
        self.log = []
        
        self._log(f"=== AUTONOMOUS MODE STARTED ===")
        self._log(f"Original objective: {objective}")
        
        try:
            # Phase 0: Prompt Refinement (auto-expand vague prompts)
            self._log("Phase 0: Refining prompt...")
            try:
                refined = prompt_refiner.quick_refine(objective)
                if refined and refined != objective:
                    self._log(f"Refined to: {refined[:200]}...")
                    objective = refined
                else:
                    self._log("Using original prompt (already detailed)")
            except Exception as e:
                self._log(f"Prompt refinement skipped: {e}")
            
            # Phase 1: Research (if needed)
            self._log("Phase 1: Research")
            routing = router.classify(objective)
            
            if routing.get("requires_research_first", False):
                self._log("Conducting research...")
                research_result = researcher.run(objective)
                recycler.save_to_domain("research", research_result)
            
            # Phase 2: Plan steps
            self._log("Phase 2: Planning")
            steps = self._plan_steps(objective)
            recycler.set_task(objective, steps)
            
            # Phase 3: Execute loop
            self._log("Phase 3: Execution")
            
            while self.is_running and self.iteration < self.max_iterations:
                self.iteration += 1
                self._log(f"--- Iteration {self.iteration} ---")
                
                # Check for recycling
                if recycler.needs_recycling():
                    self._log("!!! CONTEXT RECYCLING !!!")
                    continuation_prompt = recycler.recycle(self._call_llm)
                    
                    # Re-plan remaining steps with fresh context
                    result = self._call_llm(continuation_prompt)
                    self._log("Recycled and continuing...")
                
                # Get progress
                progress = recycler.get_progress()
                
                # Check if done
                if not progress["pending_steps"]:
                    self._log("All steps completed!")
                    break
                
                # Execute next step
                next_step = progress["pending_steps"][0]
                task_context = recycler.get_all_domain_context()
                
                result = self._execute_step(next_step, task_context)
                
                # === QA FEEDBACK LOOP ===
                # After code is generated, verify and fix if needed
                project_name = self._get_project_name(recycler.task_objective)
                project_path = os.path.join(WORKSPACE_DIR, "projects", project_name)
                
                if os.path.exists(project_path):
                    self._run_qa_feedback(project_path)
                
                # Check for completion signal in result
                if self._check_completion(result):
                    self._log("Task signaled completion")
                    break
                
                # Update token count (for recycler tracking)
                recycler.current_tokens = recycler.get_total_context_tokens()
            
            # === FINAL QA CHECK ===
            project_name = self._get_project_name(objective)
            project_path = os.path.join(WORKSPACE_DIR, "projects", project_name)
            
            if os.path.exists(project_path):
                self._log("Phase 4: Final QA")
                final_qa = self._run_qa_feedback(project_path, max_attempts=3)
                qa_status = final_qa.get("overall_status", "unknown") if final_qa else "skipped"
                self._log(f"Final QA: {qa_status}")
                
                # === PHASE 5: VISUAL QA ===
                # Take headless screenshots and analyze with vision model
                task_type = self._detect_task_type(objective)
                if task_type == "coding" and ("web" in objective.lower() or "page" in objective.lower() or "site" in objective.lower() or "frontend" in objective.lower()):
                    self._log("Phase 5: Visual QA (Headless)")
                    try:
                        visual_result = visual_qa.analyze_project(project_path)
                        visual_score = visual_result.get("average_score", 0)
                        visual_issues = visual_result.get("total_issues", 0)
                        critical_issues = len(visual_result.get("critical_issues", []))
                        
                        if visual_score >= 70 and critical_issues == 0:
                            self._log(f"Visual QA: PASSED (score: {visual_score}/100)")
                        else:
                            self._log(f"Visual QA: {visual_issues} issues found ({critical_issues} critical)")
                            # Log recommendations
                            for page in visual_result.get("pages_analyzed", []):
                                for rec in page.get("analysis", {}).get("recommendations", [])[:2]:
                                    self._log(f"  → {rec}")
                    except Exception as e:
                        self._log(f"Visual QA skipped: {e}")
            
            # Final summary
            self._log("=== AUTONOMOUS MODE COMPLETE ===")
            final_progress = recycler.get_progress()
            
            return {
                "status": "complete",
                "objective": objective,
                "iterations": self.iteration,
                "progress": final_progress,
                "project_path": project_path if os.path.exists(project_path) else None,
                "log": self.log,
                "domain_files": {
                    domain: recycler.read_domain(domain)[-500:]
                    for domain in recycler.DOMAINS
                }
            }
            
        except Exception as e:
            self._log(f"!!! ERROR: {e} !!!")
            return {
                "status": "error",
                "error": str(e),
                "log": self.log
            }
        
        finally:
            self.is_running = False
    
    def stop(self):
        """Stop the autonomous loop."""
        self._log("Stop requested")
        self.is_running = False


# Singleton
autonomous_executor = AutonomousExecutor()
