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
    
    def _validate_execution(self, project_path: str, saved_files: list) -> dict:
        """
        V3.3: Post-Execution Validation
        Attempts to run saved Python files and captures any errors.
        Returns dict with {filename: error_message} for files that failed.
        """
        import subprocess
        errors = {}
        
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
                # Try to syntax-check the file (compile only, don't execute)
                with open(filepath, 'r', encoding='utf-8') as f:
                    code = f.read()
                
                # Compile to check syntax
                compile(code, filepath, 'exec')
                
                # Try to import (catches missing dependencies)
                module_name = filename.replace('.py', '')
                result = subprocess.run(
                    ['python', '-c', f'import sys; sys.path.insert(0, r"{project_path}"); import {module_name}'],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    cwd=project_path
                )
                
                if result.returncode != 0:
                    error_msg = result.stderr.strip()
                    # Extract the key error line
                    error_lines = [l for l in error_msg.split('\n') if 'Error' in l or 'error' in l]
                    errors[filename] = error_lines[-1] if error_lines else error_msg[-500:]
                    self._log(f"[Validation] ❌ {filename}: {errors[filename][:100]}")
                else:
                    self._log(f"[Validation] ✅ {filename}: OK")
                    
            except SyntaxError as e:
                errors[filename] = f"SyntaxError: {e.msg} at line {e.lineno}"
                self._log(f"[Validation] ❌ {filename}: SyntaxError at line {e.lineno}")
            except subprocess.TimeoutExpired:
                errors[filename] = "Timeout: Code took too long to import"
                self._log(f"[Validation] ❌ {filename}: Timeout")
            except Exception as e:
                errors[filename] = f"ValidationError: {str(e)[:200]}"
                self._log(f"[Validation] ❌ {filename}: {e}")
        
        return errors
    
    def _multi_perspective_review(self, code: str, filename: str) -> list:
        """
        V3.3: Multi-Angle Code Review
        Reviews code from multiple perspectives: correctness, security, performance.
        Returns list of issues found.
        """
        issues = []
        
        # Perspective 1: Correctness (via Devils Advocate)
        from .devils_advocate import devils_advocate
        critique = devils_advocate.critique(code, content_type="code", context=f"File: {filename}")
        if critique.get("issues"):
            issues.extend([{"perspective": "correctness", **i} for i in critique["issues"]])
        
        # Perspective 2: Security (quick static checks)
        security_red_flags = [
            ("eval(", "CRITICAL: Use of eval() is dangerous"),
            ("exec(", "CRITICAL: Use of exec() is dangerous"),
            ("__import__", "WARNING: Dynamic import detected"),
            ("pickle.load", "WARNING: Pickle deserialization can be unsafe"),
            ("shell=True", "WARNING: Shell injection risk with subprocess"),
            ("os.system(", "WARNING: Prefer subprocess over os.system"),
        ]
        for pattern, warning in security_red_flags:
            if pattern in code:
                issues.append({"perspective": "security", "title": warning, "risk": "major"})
        
        # Perspective 3: Performance (basic checks)
        perf_issues = []
        if "for " in code and "append(" in code:
            # Suggest list comprehension
            perf_issues.append("Consider list comprehension instead of for+append")
        if code.count("for ") > 5:
            perf_issues.append("Multiple nested loops detected - consider optimization")
        
        for issue in perf_issues:
            issues.append({"perspective": "performance", "title": issue, "risk": "minor"})
        
        return issues
    
    def _get_project_name(self, objective: str) -> str:
        """Generate a project folder name from the objective."""
        import re
        # Extract key words and create short name
        words = re.findall(r'\b\w+\b', objective.lower())
        keywords = [w for w in words if len(w) > 3 and w not in ['build', 'create', 'make', 'with', 'that', 'this', 'from', 'using']]
        name = '-'.join(keywords[:3]) if keywords else 'project'
        return name.replace(' ', '-')[:30]
    
    def _scaffold_project(self, project_path: str, project_type: str = "research") -> dict:
        """
        V3.4: Create proper project structure with organized folders.
        Returns dict with created paths.
        """
        structure = {
            "research": ["src", "tests", "data", "docs", "figures"],
            "webapp": ["src", "public", "components", "styles", "tests"],
            "api": ["src", "routes", "models", "tests", "docs"],
            "default": ["src", "tests", "docs"]
        }
        
        folders = structure.get(project_type, structure["default"])
        created = {"folders": [], "files": []}
        
        for folder in folders:
            folder_path = os.path.join(project_path, folder)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path, exist_ok=True)
                created["folders"].append(folder)
                self._log(f"📁 SCAFFOLD: Created {folder}/")
        
        # Create README.md
        readme_path = os.path.join(project_path, "README.md")
        if not os.path.exists(readme_path):
            readme_content = f"""# Project: {os.path.basename(project_path)}

## Structure
```
{chr(10).join('├── ' + f + '/' for f in folders)}
├── requirements.txt
└── main.py
```

## Setup
```bash
pip install -r requirements.txt
python main.py
```

## Generated by Jarvis Autonomous System
"""
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            created["files"].append("README.md")
            self._log("📁 SCAFFOLD: Created README.md")
        
        return created
    
    def _install_dependencies(self, project_path: str, saved_files: list) -> list:
        """
        V3.4: Auto-install external dependencies found in Python files.
        Returns list of installed packages.
        """
        import subprocess
        import re
        
        # Common external packages (not in stdlib)
        external_packages = {
            'numpy': 'numpy', 'np': 'numpy',
            'pandas': 'pandas', 'pd': 'pandas',
            'matplotlib': 'matplotlib', 'plt': 'matplotlib',
            'networkx': 'networkx', 'nx': 'networkx',
            'requests': 'requests',
            'scipy': 'scipy',
            'sklearn': 'scikit-learn',
            'torch': 'torch',
            'tensorflow': 'tensorflow', 'tf': 'tensorflow',
            'flask': 'flask',
            'fastapi': 'fastapi',
            'pytest': 'pytest',
        }
        
        found_packages = set()
        
        for filename in saved_files:
            if not filename.endswith('.py'):
                continue
            
            # Find the file
            for root, dirs, files in os.walk(project_path):
                if filename in files:
                    filepath = os.path.join(root, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Find imports
                        import_pattern = r'^(?:from\s+(\w+)|import\s+(\w+))'
                        for match in re.finditer(import_pattern, content, re.MULTILINE):
                            module = match.group(1) or match.group(2)
                            if module in external_packages:
                                found_packages.add(external_packages[module])
                    except:
                        pass
                    break
        
        installed = []
        for package in found_packages:
            try:
                result = subprocess.run(
                    ['pip', 'install', package, '--quiet'],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if result.returncode == 0:
                    installed.append(package)
                    self._log(f"📦 DEPS: Installed {package}")
            except Exception as e:
                self._log(f"📦 DEPS: Failed to install {package}: {e}")
        
        # Generate requirements.txt
        if installed:
            req_path = os.path.join(project_path, "requirements.txt")
            with open(req_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(sorted(installed)))
            self._log(f"📦 DEPS: Generated requirements.txt with {len(installed)} packages")
        
        return installed
    
    def _inject_entry_point(self, project_path: str, main_file: str = "main.py") -> bool:
        """
        V3.4: Ensure main.py has an if __name__ == '__main__' block.
        Returns True if modified.
        """
        filepath = os.path.join(project_path, main_file)
        if not os.path.exists(filepath):
            return False
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if entry point exists
            if 'if __name__' in content:
                return False
            
            # Find the main class or function to call
            import re
            
            # Look for Simulation class or main function
            main_call = ""
            if 'class Simulation' in content:
                main_call = '''
if __name__ == "__main__":
    # Auto-generated entry point
    sim = Simulation(topology_type="ER", num_agents=50, alpha=0.7, beta=0.3)
    sim.run(iterations=100)
    print("Results:", sim.collect_metrics())
'''
            elif 'def main(' in content:
                main_call = '''
if __name__ == "__main__":
    main()
'''
            else:
                # Generic entry point
                main_call = '''
if __name__ == "__main__":
    print("Project initialized. Add your entry point logic here.")
'''
            
            # Append entry point
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write(main_call)
            
            self._log(f"🚀 ENTRY: Injected entry point into {main_file}")
            return True
            
        except Exception as e:
            self._log(f"🚀 ENTRY: Failed to inject entry point: {e}")
            return False
    
    def _run_and_capture_output(self, project_path: str, script: str = "main.py", timeout: int = 120) -> dict:
        """
        V3.5: Run a Python script and capture its output (stdout, stderr, JSON).
        Returns dict with stdout, stderr, json_data, success.
        """
        import subprocess
        import json
        
        filepath = os.path.join(project_path, script)
        if not os.path.exists(filepath):
            return {"success": False, "error": f"{script} not found"}
        
        try:
            result = subprocess.run(
                ['python', script],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=project_path
            )
            
            output = {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "json_data": None
            }
            
            # Try to extract JSON from stdout
            if result.stdout:
                try:
                    # Look for JSON in output (between { and })
                    import re
                    json_match = re.search(r'\{[^{}]*\}', result.stdout, re.DOTALL)
                    if json_match:
                        output["json_data"] = json.loads(json_match.group())
                except:
                    pass
            
            # Also check for results file
            results_file = os.path.join(project_path, "simulation_results.json")
            if os.path.exists(results_file):
                with open(results_file, 'r') as f:
                    output["json_data"] = json.load(f)
            
            self._log(f"▶️ RUN: {script} {'✅' if output['success'] else '❌'}")
            if output["json_data"]:
                self._log(f"   📊 Captured JSON data with {len(output['json_data'])} keys")
            
            return output
            
        except subprocess.TimeoutExpired:
            return {"success": False, "error": f"Timeout after {timeout}s"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _generate_figures(self, project_path: str, data: dict) -> list:
        """
        V3.5: Auto-generate matplotlib figures from simulation data.
        Saves figures to figures/ directory.
        Returns list of generated figure filenames.
        """
        figures_dir = os.path.join(project_path, "figures")
        os.makedirs(figures_dir, exist_ok=True)
        
        generated = []
        
        try:
            import matplotlib
            matplotlib.use('Agg')  # Non-interactive backend
            import matplotlib.pyplot as plt
            import numpy as np
            
            # Figure 1: Bar chart of efficiencies by topology
            if isinstance(data, dict) and any('efficiency' in str(v) for v in data.values()):
                fig, ax = plt.subplots(figsize=(10, 6))
                
                topologies = list(data.keys())
                efficiencies = [v.get('avg_efficiency', v.get('efficiency', 0)) 
                               for v in data.values() if isinstance(v, dict)]
                
                if efficiencies:
                    ax.bar(topologies, efficiencies, color=['#3498db', '#2ecc71', '#e74c3c'])
                    ax.set_xlabel('Network Topology')
                    ax.set_ylabel('Mean Efficiency')
                    ax.set_title('ATRA-G Performance Across Topologies')
                    ax.set_ylim(0, 1.1)
                    
                    fig_path = os.path.join(figures_dir, "efficiency_comparison.png")
                    plt.savefig(fig_path, dpi=150, bbox_inches='tight')
                    plt.close()
                    generated.append("efficiency_comparison.png")
                    self._log("📊 FIGURE: Generated efficiency_comparison.png")
            
            # Figure 2: Variance comparison
            if isinstance(data, dict):
                variances = [v.get('avg_variance', v.get('variance', 0)) 
                            for v in data.values() if isinstance(v, dict)]
                
                if variances and any(v > 0 for v in variances):
                    fig, ax = plt.subplots(figsize=(10, 6))
                    topologies = list(data.keys())
                    ax.bar(topologies, variances, color=['#9b59b6', '#f39c12', '#1abc9c'])
                    ax.set_xlabel('Network Topology')
                    ax.set_ylabel('Variance')
                    ax.set_title('Resource Allocation Variance by Topology')
                    
                    fig_path = os.path.join(figures_dir, "variance_comparison.png")
                    plt.savefig(fig_path, dpi=150, bbox_inches='tight')
                    plt.close()
                    generated.append("variance_comparison.png")
                    self._log("📊 FIGURE: Generated variance_comparison.png")
                    
        except ImportError:
            self._log("📊 FIGURE: matplotlib not available, skipping figure generation")
        except Exception as e:
            self._log(f"📊 FIGURE: Error generating figures: {e}")
        
        return generated
    
    def _enforce_paper_length(self, prompt: str, min_words: int = 3000) -> str:
        """
        V3.5: Modify paper generation prompt to enforce minimum length.
        """
        length_enforcement = f"""

CRITICAL LENGTH REQUIREMENT:
- You MUST write a COMPLETE academic paper with AT LEAST {min_words} words.
- Do NOT write an outline or summary.
- Each section MUST have multiple full paragraphs.
- Include: Abstract (200+ words), Introduction (500+ words), Methods (800+ words), 
  Results (600+ words), Discussion (500+ words), Conclusion (200+ words).
- Use proper academic language and cite all figures.
- If you write less than {min_words} words, your paper will be REJECTED.

"""
        return length_enforcement + prompt
    
    def _export_to_docx(self, project_path: str, markdown_file: str = "paper.md") -> str:
        """
        V3.5: Convert markdown to DOCX format for academic submission.
        Returns path to generated DOCX or empty string on failure.
        """
        md_path = os.path.join(project_path, markdown_file)
        
        # Also check in src/ and docs/
        if not os.path.exists(md_path):
            md_path = os.path.join(project_path, "src", markdown_file)
        if not os.path.exists(md_path):
            md_path = os.path.join(project_path, "docs", markdown_file)
        if not os.path.exists(md_path):
            # Try generated.markdown
            md_path = os.path.join(project_path, "src", "generated.markdown")
        
        if not os.path.exists(md_path):
            self._log("📄 DOCX: No markdown file found to convert")
            return ""
        
        try:
            from docx import Document
            from docx.shared import Inches, Pt
            from docx.enum.text import WD_ALIGN_PARAGRAPH
            
            # Read markdown
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            doc = Document()
            
            # Process markdown line by line
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if line.startswith('# '):
                    # Title
                    p = doc.add_heading(line[2:], level=0)
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                elif line.startswith('## '):
                    doc.add_heading(line[3:], level=1)
                elif line.startswith('### '):
                    doc.add_heading(line[4:], level=2)
                elif line.startswith('- '):
                    doc.add_paragraph(line[2:], style='List Bullet')
                else:
                    doc.add_paragraph(line)
            
            # Save DOCX
            docx_path = md_path.replace('.md', '.docx').replace('.markdown', '.docx')
            doc.save(docx_path)
            
            self._log(f"📄 DOCX: Exported to {os.path.basename(docx_path)}")
            return docx_path
            
        except ImportError:
            self._log("📄 DOCX: python-docx not installed, attempting install...")
            import subprocess
            subprocess.run(['pip', 'install', 'python-docx', '--quiet'], capture_output=True)
            # Retry
            try:
                from docx import Document
                return self._export_to_docx(project_path, markdown_file)
            except:
                self._log("📄 DOCX: Failed to install python-docx")
                return ""
        except Exception as e:
            self._log(f"📄 DOCX: Error exporting: {e}")
            return ""
    
    def _find_available_port(self, start_port: int = 3000, max_attempts: int = 20) -> int:
        """
        V3.6: Find an available port for dev server.
        """
        import socket
        for port in range(start_port, start_port + max_attempts):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    return port
            except OSError:
                continue
        return start_port + max_attempts  # Fallback
    
    def _start_dev_server(self, project_path: str, server_type: str = "auto") -> dict:
        """
        V3.6: Start a development server for the project.
        Returns dict with pid, port, url, type.
        """
        import subprocess
        
        # Detect server type
        if server_type == "auto":
            if os.path.exists(os.path.join(project_path, "package.json")):
                server_type = "npm"
            elif os.path.exists(os.path.join(project_path, "index.html")):
                server_type = "python"
            else:
                server_type = "python"
        
        port = self._find_available_port()
        
        try:
            if server_type == "npm":
                # Check if node_modules exists
                if not os.path.exists(os.path.join(project_path, "node_modules")):
                    self._log("🔧 DEV: Running npm install...")
                    subprocess.run(['npm', 'install'], cwd=project_path, capture_output=True)
                
                # Start dev server
                process = subprocess.Popen(
                    ['npm', 'run', 'dev', '--', '--port', str(port)],
                    cwd=project_path,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True
                )
            else:
                # Python HTTP server
                process = subprocess.Popen(
                    ['python', '-m', 'http.server', str(port)],
                    cwd=project_path,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            
            url = f"http://localhost:{port}"
            self._log(f"🚀 DEV: Server started at {url} (PID: {process.pid})")
            
            return {
                "success": True,
                "pid": process.pid,
                "port": port,
                "url": url,
                "type": server_type
            }
            
        except Exception as e:
            self._log(f"🚀 DEV: Failed to start server - {e}")
            return {"success": False, "error": str(e)}
    
    def _deploy_netlify(self, project_path: str, prod: bool = False) -> dict:
        """
        V3.6: Deploy project to Netlify using CLI.
        """
        import subprocess
        
        # Check if Netlify CLI is installed
        try:
            result = subprocess.run(['netlify', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                self._log("📦 Installing Netlify CLI...")
                subprocess.run(['npm', 'install', '-g', 'netlify-cli'], capture_output=True)
        except FileNotFoundError:
            self._log("📦 Installing Netlify CLI...")
            subprocess.run(['npm', 'install', '-g', 'netlify-cli'], capture_output=True)
        
        # Determine build directory
        build_dir = project_path
        for candidate in ['dist', 'build', 'public', '.']:
            candidate_path = os.path.join(project_path, candidate)
            if os.path.exists(candidate_path) and os.path.isdir(candidate_path):
                build_dir = candidate_path
                break
        
        try:
            cmd = ['netlify', 'deploy', '--dir', build_dir]
            if prod:
                cmd.append('--prod')
            
            result = subprocess.run(
                cmd,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            # Extract URL from output
            import re
            url_match = re.search(r'(https://[^\s]+\.netlify\.app)', result.stdout)
            deploy_url = url_match.group(1) if url_match else None
            
            if deploy_url:
                self._log(f"🌐 NETLIFY: Deployed to {deploy_url}")
                return {"success": True, "url": deploy_url, "prod": prod}
            else:
                self._log(f"🌐 NETLIFY: Deploy output - {result.stdout[:200]}")
                return {"success": False, "output": result.stdout, "error": result.stderr}
                
        except Exception as e:
            self._log(f"🌐 NETLIFY: Deploy failed - {e}")
            return {"success": False, "error": str(e)}
    
    def _deploy_vercel(self, project_path: str, prod: bool = False) -> dict:
        """
        V3.6: Deploy project to Vercel using CLI.
        """
        import subprocess
        
        # Check if Vercel CLI is installed
        try:
            result = subprocess.run(['vercel', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                self._log("📦 Installing Vercel CLI...")
                subprocess.run(['npm', 'install', '-g', 'vercel'], capture_output=True)
        except FileNotFoundError:
            self._log("📦 Installing Vercel CLI...")
            subprocess.run(['npm', 'install', '-g', 'vercel'], capture_output=True)
        
        try:
            cmd = ['vercel', '--yes']  # --yes for non-interactive
            if prod:
                cmd.append('--prod')
            
            result = subprocess.run(
                cmd,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=180
            )
            
            # Extract URL from output
            import re
            url_match = re.search(r'(https://[^\s]+\.vercel\.app)', result.stdout)
            deploy_url = url_match.group(1) if url_match else None
            
            if deploy_url:
                self._log(f"▲ VERCEL: Deployed to {deploy_url}")
                return {"success": True, "url": deploy_url, "prod": prod}
            else:
                self._log(f"▲ VERCEL: Deploy output - {result.stdout[:200]}")
                return {"success": False, "output": result.stdout, "error": result.stderr}
                
        except Exception as e:
            self._log(f"▲ VERCEL: Deploy failed - {e}")
            return {"success": False, "error": str(e)}
    
    def _start_project(self, project_path: str, mode: str = "dev") -> dict:
        """
        V3.6: Smart project starter - detects project type and runs appropriately.
        Modes: 'dev' (local server), 'run' (execute main.py), 'deploy' (Netlify/Vercel)
        """
        project_name = os.path.basename(project_path)
        
        # Detect project type
        has_package_json = os.path.exists(os.path.join(project_path, "package.json"))
        has_main_py = os.path.exists(os.path.join(project_path, "main.py"))
        has_index_html = os.path.exists(os.path.join(project_path, "index.html"))
        
        if mode == "dev":
            if has_package_json:
                return self._start_dev_server(project_path, "npm")
            elif has_index_html:
                return self._start_dev_server(project_path, "python")
            else:
                return {"success": False, "error": "No web project detected"}
        
        elif mode == "run":
            if has_main_py:
                return self._run_and_capture_output(project_path, "main.py")
            else:
                return {"success": False, "error": "No main.py found"}
        
        elif mode == "deploy":
            # Try Vercel first (faster), fallback to Netlify
            result = self._deploy_vercel(project_path, prod=True)
            if not result.get("success"):
                result = self._deploy_netlify(project_path, prod=True)
            return result
        
        else:
            return {"success": False, "error": f"Unknown mode: {mode}"}
    
    def _execute_step(self, step: str, task_context: str) -> str:
        """Execute a single step with smart context and terminal integration."""
        self._log(f"Executing: {step}")
        
        # Get the ORIGINAL objective - this prevents hallucination
        original_objective = recycler.task_objective
        
        # Detect task type
        task_type = self._detect_task_type(original_objective)
        
        project_name = self._get_project_name(original_objective)
        project_path = os.path.join(WORKSPACE_DIR, "projects", project_name)

        # V3.4: Scaffold project structure on first access
        if not os.path.exists(project_path):
            os.makedirs(project_path, exist_ok=True)
        self._scaffold_project(project_path, project_type=task_type)

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
            
            # V3.4: Auto-install dependencies found in saved files
            installed_deps = self._install_dependencies(project_path, saved_files)
            if installed_deps:
                response += f"\n[SYSTEM: Installed {len(installed_deps)} packages: {', '.join(installed_deps)}]"
            
            # V3.4: Inject entry point if main.py lacks one
            if 'main.py' in saved_files:
                self._inject_entry_point(project_path, 'main.py')
        
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
        # Check ALL Python files in the project for missing imports (not just newly saved)
        all_py_files = []
        for root, dirs, files in os.walk(project_path):
            for f in files:
                if f.endswith('.py'):
                    all_py_files.append(f)
        
        if all_py_files:
            missing_deps = self._audit_dependencies(project_path, all_py_files)
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

        # === V3.3: POST-EXECUTION VALIDATION ===
        # Try to run saved Python files and catch any errors
        if all_py_files:
            max_retries = 3
            for retry in range(max_retries):
                validation_errors = self._validate_execution(project_path, all_py_files)
                
                if not validation_errors:
                    self._log(f"🧪 VALIDATION: All {len(all_py_files)} files passed!")
                    break
                
                self._log(f"🧪 VALIDATION: {len(validation_errors)} errors found (retry {retry + 1}/{max_retries})")
                
                # Build fix prompt with specific errors
                fix_prompt = "Your code has ERRORS that prevent it from running:\n\n"
                for filename, error in validation_errors.items():
                    fix_prompt += f"❌ {filename}: {error}\n"
                fix_prompt += "\nFix ALL these errors NOW. Output the corrected code blocks."
                
                # Call LLM to fix
                fix_response = self._call_llm(fix_prompt)
                fixed_files = self._extract_and_save_code(fix_response, project_name)
                
                if fixed_files:
                    response += f"\n\n[SYSTEM: Auto-fixed files: {', '.join(fixed_files)}]"
                    # Re-scan for all py files after fix
                    all_py_files = []
                    for root, dirs, files in os.walk(project_path):
                        for f in files:
                            if f.endswith('.py'):
                                all_py_files.append(f)
        
        # === V3.3: MULTI-PERSPECTIVE CODE REVIEW ===
        # Review saved code from multiple angles (security, performance, correctness)
        if saved_files:
            for filename in saved_files:
                if not filename.endswith('.py'):
                    continue
                
                # Find and read the file
                for root, dirs, files in os.walk(project_path):
                    if filename in files:
                        filepath = os.path.join(root, filename)
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                code = f.read()
                            
                            issues = self._multi_perspective_review(code, filename)
                            critical_issues = [i for i in issues if i.get('risk') in ['critical', 'major']]
                            
                            if critical_issues:
                                self._log(f"🔍 REVIEW: {filename} has {len(critical_issues)} critical issues")
                                # Force fix for security issues
                                security_issues = [i for i in critical_issues if i.get('perspective') == 'security']
                                if security_issues:
                                    sec_prompt = f"SECURITY ALERT for {filename}:\n"
                                    for issue in security_issues:
                                        sec_prompt += f"- {issue['title']}\n"
                                    sec_prompt += "\nRewrite the code to fix these security issues."
                                    self._log(f"  -> Forcing security fix for {filename}")
                                    sec_response = self._call_llm(sec_prompt)
                                    self._extract_and_save_code(sec_response, project_name)
                            else:
                                self._log(f"🔍 REVIEW: {filename} passed all perspectives ✅")
                        except Exception as e:
                            self._log(f"[Review] Error reading {filename}: {e}")
                        break

        # === V3.5: DATA-FIRST PIPELINE ===
        # After code is saved, run it and capture output for paper generation
        if 'main.py' in saved_files or os.path.exists(os.path.join(project_path, 'main.py')):
            # Step 1: Run simulation and capture output
            run_result = self._run_and_capture_output(project_path, 'main.py')
            
            if run_result.get("success") and run_result.get("json_data"):
                # Step 2: Generate figures from captured data
                figures = self._generate_figures(project_path, run_result["json_data"])
                if figures:
                    response += f"\n[SYSTEM: Generated {len(figures)} figures: {', '.join(figures)}]"
                
                # Step 3: If this is a research task, trigger paper generation with real data
                if task_type == "research" and "paper" not in step.lower():
                    self._log("📝 DATA-FIRST: Triggering paper generation with REAL data...")
                    
                    # Build paper prompt with actual results
                    paper_prompt = self._enforce_paper_length(f"""
Write a COMPLETE academic research paper based on THESE ACTUAL RESULTS:

SIMULATION DATA:
{json.dumps(run_result['json_data'], indent=2)}

GENERATED FIGURES (reference these in your paper):
{', '.join(figures) if figures else 'None generated'}

PROJECT: {project_name}
OBJECTIVE: {original_objective}

Write the FULL paper now with proper academic formatting.
""")
                    # Store for next step rather than calling LLM here
                    # (Paper generation should be a separate step)
                    data_file = os.path.join(project_path, "data", "results.json")
                    os.makedirs(os.path.dirname(data_file), exist_ok=True)
                    with open(data_file, 'w') as f:
                        json.dump(run_result["json_data"], f, indent=2)
                    self._log(f"📊 DATA: Saved results to data/results.json for paper generation")
            
            elif run_result.get("error"):
                self._log(f"⚠️ RUN: Simulation failed - {run_result['error']}")
        
        # === V3.5: DOCX EXPORT ===
        # Export any markdown papers to DOCX
        md_files = [f for f in saved_files if f.endswith('.md') or f.endswith('.markdown')]
        for md_file in md_files:
            if 'paper' in md_file.lower() or 'generated' in md_file.lower():
                self._export_to_docx(project_path, md_file)

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
