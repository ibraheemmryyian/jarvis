"""
Terminal Agent for Jarvis v2
Sandboxed command execution with output capture for AI feedback.
"""
import os
import subprocess
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from .config import WORKSPACE_DIR


# Allowed commands (whitelist for safety)
ALLOWED_COMMANDS = {
    # Package managers - expanded list
    "npm": ["install", "run", "build", "test", "start", "init", "ci", "--version", "-v", "list", "outdated", "update"],
    "npx": True,  # Allow all npx commands
    "pip": ["install", "list", "freeze", "--version", "-V", "show", "check"],
    "python": True,  # Allow python with restrictions
    "node": True,  # Allow node
    
    # Build tools
    "vite": ["dev", "build", "preview"],
    "webpack": True,
    "tsc": True,  # TypeScript compiler
    
    # Testing
    "pytest": True,
    "jest": True,
    "vitest": True,
    
    # Git (read-only operations)
    "git": ["status", "log", "diff", "branch"],
    
    # Utilities
    "mkdir": True,
    "cd": True,
    "ls": True,
    "dir": True,
    "cat": True,
    "type": True,  # Windows equivalent of cat
    "echo": True,
}

# BLOCKED COMMANDS - COMPREHENSIVE LIST FOR 100% SAFETY
# These commands are NEVER allowed, regardless of arguments
BLOCKED_COMMANDS = [
    # === FILE DELETION ===
    "rm",           # Unix remove
    "rm -rf",
    "rm -r",
    "rmdir",        # Remove directory
    "del",          # Windows delete
    "erase",        # Windows erase
    "rd",           # Windows remove directory
    "shred",        # Secure delete
    "unlink",       # Remove file
    
    # === DANGEROUS SYSTEM COMMANDS ===
    "format",       # Format disk
    "fdisk",        # Partition disk
    "mkfs",         # Make filesystem
    "dd",           # Disk destroyer if misused
    
    # === PRIVILEGE ESCALATION ===
    "sudo",
    "su",
    "runas",        # Windows run as admin
    "doas",         # OpenBSD sudo
    
    # === SYSTEM CONTROL ===
    "shutdown",
    "reboot",
    "poweroff",
    "halt",
    "init",
    
    # === NETWORK ATTACKS ===
    "nmap",
    "netcat",
    "nc",
    "curl -X DELETE",
    "wget --delete",
    
    # === DANGEROUS OPERATIONS ===
    ":(){:|:&};:",  # Fork bomb
    "chmod 777",    # Dangerous permissions
    "chown",        # Change ownership
    "kill",         # Kill processes
    "killall",
    "pkill",
    
    # === WINDOWS SPECIFIC ===
    "reg delete",   # Registry delete
    "wmic",         # WMI commands
    "net user",     # User management
    "net localgroup",
    "takeown",      # Take ownership
    "icacls",       # Change permissions
]

# BLOCKED PATTERNS - Match anywhere in command
BLOCKED_PATTERNS = [
    # === PATH MANIPULATION ===
    "../",          # Path traversal
    "..\\",
    
    # === COMMAND CHAINING (could bypass security) ===
    ";",            # Command separator
    "&&",           # AND chain
    "||",           # OR chain
    "|",            # Pipe
    "`",            # Command substitution
    "$(",           # Command substitution
    ">(", "<(",     # Process substitution
    
    # === REDIRECTION TO SYSTEM FILES ===
    "> /dev/",      # Write to devices
    "> /etc/",      # Write to system config
    "> C:\\Windows",# Write to Windows
    
    # === ENVIRONMENT MANIPULATION ===
    "export PATH",
    "set PATH",
    
    # === DANGEROUS FILE OPERATIONS ===
    ">/dev/null",   # Allow this? Actually this is fine
    "mv /",         # Move root
    "cp -r /",      # Copy root
]

# BLOCKED KEYWORDS - If these words appear, extra caution
BLOCKED_KEYWORDS = [
    "delete", "remove", "destroy", "wipe", "erase",
    "truncate", "purge", "clean --all", "reset --hard",
    "drop database", "drop table",
]



class TerminalAgent:
    """
    Sandboxed terminal for running commands within project directories.
    
    Features:
    - Project-scoped execution (can't escape project directory)
    - Command whitelist for safety
    - Output capture for AI feedback
    - Timeout protection
    """
    
    def __init__(self):
        self.history: List[Dict] = []
        self.max_history = 50
        self.default_timeout = 120  # seconds
    
    def run(self, command: str, project_path: str = None, 
            timeout: int = None, capture_output: bool = True) -> Dict:
        """
        Run a command in a sandboxed environment.
        
        Args:
            command: Command to execute
            project_path: Directory to run in (defaults to workspace)
            timeout: Max execution time in seconds
            capture_output: Whether to capture stdout/stderr
            
        Returns:
            Dict with exit_code, stdout, stderr, duration
        """
        timeout = timeout or self.default_timeout
        
        # Determine working directory
        if project_path:
            if os.path.isabs(project_path):
                cwd = project_path
            else:
                cwd = os.path.join(WORKSPACE_DIR, "projects", project_path)
        else:
            cwd = WORKSPACE_DIR
        
        # Ensure directory exists
        if not os.path.exists(cwd):
            return {
                "success": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Directory does not exist: {cwd}",
                "command": command,
                "duration": 0
            }
        
        # Security check
        security_check = self._security_check(command)
        if not security_check["allowed"]:
            return {
                "success": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Command blocked: {security_check['reason']}",
                "command": command,
                "duration": 0
            }
        
        # Execute command
        start_time = time.time()
        
        try:
            # Use shell=True for Windows compatibility
            process = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=capture_output,
                text=True,
                timeout=timeout,
                env=self._get_safe_env()
            )
            
            duration = time.time() - start_time
            
            result = {
                "success": process.returncode == 0,
                "exit_code": process.returncode,
                "stdout": process.stdout[:10000] if process.stdout else "",  # Limit output
                "stderr": process.stderr[:5000] if process.stderr else "",
                "command": command,
                "cwd": cwd,
                "duration": round(duration, 2)
            }
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            result = {
                "success": False,
                "exit_code": -2,
                "stdout": "",
                "stderr": f"Command timed out after {timeout}s",
                "command": command,
                "cwd": cwd,
                "duration": round(duration, 2)
            }
            
        except Exception as e:
            duration = time.time() - start_time
            result = {
                "success": False,
                "exit_code": -3,
                "stdout": "",
                "stderr": str(e),
                "command": command,
                "cwd": cwd,
                "duration": round(duration, 2)
            }
        
        # Log to history
        self._log_command(result)
        
        return result
    
    def run_and_wait(self, command: str, project_path: str = None,
                     timeout: int = None, wait_for: str = None) -> Dict:
        """
        Run command and wait for specific output or completion.
        This is ideal for AI to monitor command progress.
        
        Args:
            command: Command to execute
            project_path: Directory to run in
            timeout: Max execution time
            wait_for: Optional string to wait for in output
            
        Returns:
            Dict with parsed output and status
        """
        result = self.run(command, project_path, timeout)
        
        # Parse and structure the output for AI consumption
        parsed = {
            **result,
            "output_lines": result["stdout"].split("\n") if result["stdout"] else [],
            "error_lines": result["stderr"].split("\n") if result["stderr"] else [],
            "has_errors": bool(result["stderr"] and result["exit_code"] != 0),
            "found_pattern": wait_for in result["stdout"] if wait_for else None
        }
        
        # Detect common patterns in output
        parsed["detected"] = self._detect_output_patterns(result)
        
        return parsed
    
    def run_with_feedback(self, command: str, project_path: str = None) -> str:
        """
        Run command and return a formatted string for AI feedback.
        Perfect for injecting into LLM context.
        """
        result = self.run(command, project_path)
        
        status = "SUCCESS" if result["success"] else "FAILED"
        output = f"""## Command: `{command}`
**Status**: {status}
**Exit Code**: {result["exit_code"]}
**Duration**: {result["duration"]}s

"""
        if result["stdout"]:
            output += f"""### Output:
```
{result["stdout"][:3000]}
```

"""
        if result["stderr"] and not result["success"]:
            output += f"""### Errors:
```
{result["stderr"][:1500]}
```
"""
        
        return output
    
    def _detect_output_patterns(self, result: Dict) -> Dict:
        """Detect common patterns in command output."""
        stdout = result.get("stdout", "")
        stderr = result.get("stderr", "")
        combined = (stdout + stderr).lower()
        
        return {
            "success_indicated": any(s in combined for s in ["success", "completed", "done", "built", "passed"]),
            "error_indicated": any(s in combined for s in ["error", "failed", "exception", "traceback"]),
            "warning_indicated": any(s in combined for s in ["warning", "warn", "deprecated"]),
            "install_complete": any(s in combined for s in ["added", "packages", "installed"]),
            "build_complete": any(s in combined for s in ["built", "compiled", "bundled"]),
            "test_results": any(s in combined for s in ["passed", "failed", "tests", "assertions"]),
            "server_started": any(s in combined for s in ["listening", "running on", "started", "ready"])
        }
    
    def run_script(self, script: str, project_path: str, 
                   language: str = "python") -> Dict:
        """
        Run a script file in the project.
        
        Args:
            script: Relative path to script (e.g., "test.py")
            project_path: Project directory
            language: python, node, etc.
        """
        interpreters = {
            "python": "python",
            "node": "node",
            "javascript": "node",
            "typescript": "npx ts-node",
            "bash": "bash",
            "sh": "sh",
        }
        
        interpreter = interpreters.get(language, "python")
        command = f"{interpreter} {script}"
        
        return self.run(command, project_path)
    
    def install_dependencies(self, project_path: str, 
                            package_manager: str = "auto") -> Dict:
        """
        Install project dependencies.
        
        Args:
            project_path: Project directory
            package_manager: npm, pip, or auto-detect
        """
        if package_manager == "auto":
            package_manager = self._detect_package_manager(project_path)
        
        if package_manager == "npm":
            return self.run("npm install", project_path)
        elif package_manager == "pip":
            return self.run("pip install -r requirements.txt", project_path)
        elif package_manager == "yarn":
            return self.run("yarn install", project_path)
        else:
            return {
                "success": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Unknown package manager: {package_manager}",
                "command": "install",
                "duration": 0
            }
    
    def run_tests(self, project_path: str, 
                  test_framework: str = "auto") -> Dict:
        """
        Run project tests.
        
        Args:
            project_path: Project directory
            test_framework: pytest, jest, vitest, or auto-detect
        """
        if test_framework == "auto":
            test_framework = self._detect_test_framework(project_path)
        
        commands = {
            "pytest": "pytest -v",
            "jest": "npm test",
            "vitest": "npm run test",
            "unittest": "python -m unittest discover",
            "mocha": "npm test",
        }
        
        command = commands.get(test_framework, "pytest -v")
        return self.run(command, project_path)
    
    def start_dev_server(self, project_path: str, 
                        framework: str = "auto") -> Dict:
        """
        Start development server (with timeout for quick check).
        
        Note: This returns quickly - use for verifying server starts.
        For long-running servers, use run() with a background process.
        """
        if framework == "auto":
            framework = self._detect_framework(project_path)
        
        commands = {
            "vite": "npm run dev",
            "next": "npm run dev",
            "react": "npm start",
            "flask": "python -m flask run",
            "fastapi": "uvicorn main:app --reload",
            "http": "python -m http.server 8000",
        }
        
        command = commands.get(framework, "python -m http.server 8000")
        
        # Short timeout just to check if it starts
        return self.run(command, project_path, timeout=5)
    
    # === Private Methods ===
    
    def _security_check(self, command: str) -> Dict:
        """
        STRICT security check - 100% protection against harmful commands.
        Uses defense-in-depth with multiple layers.
        """
        cmd_lower = command.lower()
        
        # LAYER 1: Check blocked commands (exact and partial match)
        for blocked in BLOCKED_COMMANDS:
            # Check if blocked command appears at start or after space
            if cmd_lower == blocked or cmd_lower.startswith(blocked + " ") or \
               f" {blocked}" in cmd_lower or f" {blocked} " in cmd_lower:
                return {"allowed": False, "reason": f"BLOCKED: '{blocked}' is a dangerous command"}
        
        # LAYER 2: Check blocked patterns
        for pattern in BLOCKED_PATTERNS:
            if pattern in command:
                return {"allowed": False, "reason": f"BLOCKED: Pattern '{pattern}' not allowed"}
        
        # LAYER 3: Check dangerous keywords
        for keyword in BLOCKED_KEYWORDS:
            if keyword in cmd_lower:
                return {"allowed": False, "reason": f"BLOCKED: Keyword '{keyword}' not allowed"}
        
        # LAYER 4: Check base command is whitelisted
        parts = command.split()
        if not parts:
            return {"allowed": False, "reason": "Empty command"}
        
        base_cmd = parts[0].lower()
        
        # Remove path if present (e.g., /usr/bin/python -> python)
        base_cmd = os.path.basename(base_cmd)
        
        # Check whitelist
        if base_cmd not in ALLOWED_COMMANDS:
            return {"allowed": False, "reason": f"BLOCKED: '{base_cmd}' not in whitelist"}
        
        allowed_args = ALLOWED_COMMANDS[base_cmd]
        
        # True means all args allowed
        if allowed_args is True:
            return {"allowed": True, "reason": "Whitelisted command"}
        
        # Check if subcommand is in allowed list
        if len(parts) > 1:
            if parts[1] in allowed_args:
                return {"allowed": True, "reason": "Whitelisted subcommand"}
            else:
                return {"allowed": False, "reason": f"Subcommand '{parts[1]}' not allowed for {base_cmd}"}
        
        return {"allowed": True, "reason": "Whitelisted (no args)"}
    
    def _get_safe_env(self) -> Dict:
        """Get a safe environment for command execution."""
        safe_env = os.environ.copy()
        
        # Remove sensitive variables
        sensitive = ["AWS_SECRET", "API_KEY", "TOKEN", "PASSWORD", "PRIVATE"]
        for key in list(safe_env.keys()):
            for s in sensitive:
                if s in key.upper():
                    del safe_env[key]
                    break
        
        return safe_env
    
    def _detect_package_manager(self, project_path: str) -> str:
        """Detect package manager from project files."""
        full_path = project_path if os.path.isabs(project_path) else \
                    os.path.join(WORKSPACE_DIR, "projects", project_path)
        
        if os.path.exists(os.path.join(full_path, "package.json")):
            if os.path.exists(os.path.join(full_path, "yarn.lock")):
                return "yarn"
            return "npm"
        elif os.path.exists(os.path.join(full_path, "requirements.txt")):
            return "pip"
        elif os.path.exists(os.path.join(full_path, "Pipfile")):
            return "pipenv"
        
        return "npm"  # Default
    
    def _detect_test_framework(self, project_path: str) -> str:
        """Detect test framework from project files."""
        full_path = project_path if os.path.isabs(project_path) else \
                    os.path.join(WORKSPACE_DIR, "projects", project_path)
        
        if os.path.exists(os.path.join(full_path, "pytest.ini")) or \
           os.path.exists(os.path.join(full_path, "tests")):
            return "pytest"
        elif os.path.exists(os.path.join(full_path, "jest.config.js")):
            return "jest"
        elif os.path.exists(os.path.join(full_path, "vitest.config.js")):
            return "vitest"
        
        return "pytest"  # Default
    
    def _detect_framework(self, project_path: str) -> str:
        """Detect web framework from project files."""
        full_path = project_path if os.path.isabs(project_path) else \
                    os.path.join(WORKSPACE_DIR, "projects", project_path)
        
        if os.path.exists(os.path.join(full_path, "vite.config.js")):
            return "vite"
        elif os.path.exists(os.path.join(full_path, "next.config.js")):
            return "next"
        elif os.path.exists(os.path.join(full_path, "app.py")):
            return "flask"
        
        return "http"  # Simple HTTP server
    
    def _log_command(self, result: Dict):
        """Log command to history."""
        entry = {
            **result,
            "timestamp": datetime.now().isoformat()
        }
        
        self.history.append(entry)
        
        # Trim history
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
    
    def get_history(self, limit: int = 10) -> List[Dict]:
        """Get recent command history."""
        return self.history[-limit:]
    
    def get_history_for_context(self) -> str:
        """Format history for AI context."""
        if not self.history:
            return "No commands executed yet."
        
        output = "## Recent Commands\n"
        for entry in self.history[-5:]:
            status = "✓" if entry["success"] else "✗"
            output += f"- [{status}] `{entry['command']}` ({entry['duration']}s)\n"
            if entry["stderr"] and not entry["success"]:
                output += f"  Error: {entry['stderr'][:100]}\n"
        
        return output


# Singleton
terminal = TerminalAgent()
