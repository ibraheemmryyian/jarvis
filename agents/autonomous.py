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
        self.iteration = 0
        self.max_iterations = 50  # Safety limit
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
        print(entry)
        if self.progress_callback:
            self.progress_callback(msg)
    
    def _call_llm(self, prompt: str) -> str:
        """Make LLM call through base agent."""
        from .base_agent import BaseAgent
        
        class TempAgent(BaseAgent):
            def __init__(self):
                super().__init__("autonomous")
            def _get_system_prompt(self):
                return "You are Jarvis, an autonomous AI assistant completing a multi-step task."
            def run(self, task: str) -> str:
                return self.call_llm(task)
        
        agent = TempAgent()
        return agent.call_llm(prompt)
    
    def _check_completion(self, response: str) -> bool:
        """Check if task is complete based on response."""
        completion_signals = [
            "task complete",
            "all steps done",
            "finished building",
            "project complete",
            "done",
            "completed successfully"
        ]
        response_lower = response.lower()
        return any(signal in response_lower for signal in completion_signals)
    
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
    
    def _extract_and_save_code(self, result: str, project_name: str) -> List[str]:
        """Extract code blocks from LLM output and save as files using ProjectManager."""
        import re
        
        saved_files = []
        
        # Create project if doesn't exist
        project_path = os.path.join(WORKSPACE_DIR, "projects", project_name)
        if not os.path.exists(project_path):
            project_manager.create_project(project_name, stack="vanilla", category="frontend")
        
        # Pattern to match code blocks with optional filename hints
        # Matches: ```html, ```css, ```javascript, ```python, etc.
        code_pattern = r'```(\w+)\n([\s\S]*?)```'
        matches = re.findall(code_pattern, result)
        
        # File mapping with proper subdirectories
        file_map = {
            'html': 'src/index.html',
            'css': 'src/css/style.css', 
            'javascript': 'src/js/script.js',
            'js': 'src/js/script.js',
            'python': 'src/main.py',
            'py': 'src/main.py',
            'json': 'data.json',
            'typescript': 'src/index.ts',
            'ts': 'src/index.ts',
            'jsx': 'src/App.jsx',
            'tsx': 'src/App.tsx',
        }
        
        # Track file counts for uniqueness
        file_counts = {}
        current_step = recycler.get_progress().get("pending_steps", ["unknown"])[0] if recycler else "unknown"
        
        for lang, code in matches:
            lang = lang.lower()
            if lang in file_map:
                relative_path = file_map[lang]
                
                # Handle multiple files of same type
                if relative_path in file_counts:
                    file_counts[relative_path] += 1
                    name, ext = os.path.splitext(relative_path)
                    relative_path = f"{name}_{file_counts[relative_path]}{ext}"
                else:
                    file_counts[relative_path] = 1
                
                # Use ProjectManager to add file (handles indexing)
                try:
                    file_entry = project_manager.add_file(
                        project_path, 
                        relative_path, 
                        code.strip(), 
                        step=current_step
                    )
                    saved_files.append(file_entry["path"])
                    self._log(f"  -> Saved: {relative_path}")
                except Exception as e:
                    self._log(f"  -> Error saving {relative_path}: {e}")
        
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
            # Check if this is a website/UI task that needs creativity
            ui_keywords = ["website", "landing", "page", "ui", "frontend", "dashboard", "app"]
            needs_creativity = any(kw in original_objective.lower() for kw in ui_keywords)
            
            if needs_creativity:
                # Inject unique design direction to avoid cookie-cutter templates
                prompt += design_creativity.get_creative_prompt(original_objective)
            else:
                prompt += f"""
- You are building: {original_objective}
"""
            
            prompt += """
- When writing code, include the COMPLETE file content
- Use proper code blocks (```html, ```css, ```javascript, ```python)
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
            prompt += """
- Provide data-driven analysis
- Include metrics and comparisons where relevant
- Summarize key findings
- Make recommendations based on analysis
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
- At the end, state what was accomplished for this step."""
        
        result = self._call_llm(prompt)
        
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
        """Ask LLM to break down objective into steps."""
        self._log("Planning steps...")
        
        prompt = f"""Break down this objective into concrete steps:

OBJECTIVE: {objective}

Output a numbered list of 5-10 specific, actionable steps.
Each step should be one clear action (e.g., "Create React component for login form").
Format: Just the numbered list, nothing else."""
        
        response = self._call_llm(prompt)
        
        # Parse steps from response
        steps = []
        for line in response.split("\n"):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith("-")):
                # Remove numbering
                step = line.lstrip("0123456789.-) ").strip()
                if step:
                    steps.append(step)
        
        self._log(f"Planned {len(steps)} steps")
        return steps[:10]  # Limit to 10 steps
    
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
        self._log(f"Objective: {objective}")
        
        try:
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
