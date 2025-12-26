"""
Git Agent for Jarvis v2
Handles repository creation, commits, and pushing to GitHub.
Enables auto-commit for continuous saving during autonomous tasks.
"""
import os
import subprocess
import json
from datetime import datetime
from typing import Dict, List, Optional
from .config import WORKSPACE_DIR


class GitAgent:
    """
    Manages Git operations for Jarvis projects.
    
    Features:
    - Initialize new repositories
    - Auto-commit on file changes
    - Push to GitHub
    - Branch management
    """
    
    def __init__(self, github_token: str = None):
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.github_username = os.getenv("GITHUB_USERNAME", "")
    
    def _run_git(self, args: List[str], cwd: str = None) -> Dict:
        """Run a git command and return result."""
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=cwd or WORKSPACE_DIR,
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip()
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def init_repo(self, project_path: str, repo_name: str = None) -> Dict:
        """
        Initialize a new Git repository.
        
        Args:
            project_path: Path to the project directory
            repo_name: Optional name for the repo (defaults to folder name)
            
        Returns:
            Dict with success status and details
        """
        if not os.path.exists(project_path):
            return {"success": False, "error": f"Path does not exist: {project_path}"}
        
        # Check if already a git repo
        if os.path.exists(os.path.join(project_path, ".git")):
            return {"success": True, "message": "Already a git repository"}
        
        # Initialize
        result = self._run_git(["init"], cwd=project_path)
        if not result["success"]:
            return result
        
        # Create .gitignore
        gitignore_content = """# Dependencies
node_modules/
__pycache__/
*.pyc
.env
.venv/
venv/

# Build outputs
dist/
build/
*.egg-info/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Jarvis internal
.jarvis/
"""
        gitignore_path = os.path.join(project_path, ".gitignore")
        if not os.path.exists(gitignore_path):
            with open(gitignore_path, "w") as f:
                f.write(gitignore_content)
        
        # Initial commit
        self._run_git(["add", "."], cwd=project_path)
        self._run_git(["commit", "-m", "Initial commit by Jarvis"], cwd=project_path)
        
        return {
            "success": True,
            "message": f"Initialized git repository at {project_path}",
            "repo_name": repo_name or os.path.basename(project_path)
        }
    
    def commit(self, project_path: str, message: str = None) -> Dict:
        """
        Commit all changes in the project.
        
        Args:
            project_path: Path to the project
            message: Commit message (auto-generated if not provided)
            
        Returns:
            Dict with commit details
        """
        if not message:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            message = f"Auto-save by Jarvis at {timestamp}"
        
        # Stage all changes
        self._run_git(["add", "."], cwd=project_path)
        
        # Check if there are changes to commit
        status = self._run_git(["status", "--porcelain"], cwd=project_path)
        if not status["stdout"]:
            return {"success": True, "message": "No changes to commit"}
        
        # Commit
        result = self._run_git(["commit", "-m", message], cwd=project_path)
        
        if result["success"]:
            # Get commit hash
            hash_result = self._run_git(["rev-parse", "--short", "HEAD"], cwd=project_path)
            return {
                "success": True,
                "message": f"Committed: {message}",
                "commit_hash": hash_result.get("stdout", "")
            }
        
        return result
    
    def create_github_repo(self, repo_name: str, private: bool = True, description: str = "") -> Dict:
        """
        Create a new GitHub repository.
        
        Args:
            repo_name: Name for the repository
            private: Whether repo should be private
            description: Repository description
            
        Returns:
            Dict with repo URL and details
        """
        if not self.github_token:
            return {"success": False, "error": "GitHub token not configured"}
        
        import requests
        
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        data = {
            "name": repo_name,
            "private": private,
            "description": description or f"Created by Jarvis AI Assistant",
            "auto_init": False
        }
        
        try:
            response = requests.post(
                "https://api.github.com/user/repos",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 201:
                repo_data = response.json()
                return {
                    "success": True,
                    "repo_url": repo_data["html_url"],
                    "clone_url": repo_data["clone_url"],
                    "ssh_url": repo_data["ssh_url"]
                }
            else:
                return {
                    "success": False,
                    "error": response.json().get("message", "Failed to create repo")
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def push(self, project_path: str, remote: str = "origin", branch: str = "main") -> Dict:
        """
        Push commits to remote repository.
        
        Args:
            project_path: Path to the project
            remote: Remote name (default: origin)
            branch: Branch name (default: main)
            
        Returns:
            Dict with push result
        """
        # Ensure we're on the right branch
        self._run_git(["branch", "-M", branch], cwd=project_path)
        
        # Try push with upstream tracking
        result = self._run_git(["push", "-u", remote, branch], cwd=project_path)
        
        if not result["success"]:
            # If push fails, try force push (for new repos)
            result = self._run_git(["push", "-u", "-f", remote, branch], cwd=project_path)
        
        return result
    
    def add_remote(self, project_path: str, repo_url: str, remote_name: str = "origin") -> Dict:
        """Add a remote to the repository."""
        return self._run_git(["remote", "add", remote_name, repo_url], cwd=project_path)
    
    def get_status(self, project_path: str) -> Dict:
        """Get git status for a project."""
        status = self._run_git(["status", "--short"], cwd=project_path)
        log = self._run_git(["log", "--oneline", "-5"], cwd=project_path)
        
        return {
            "changes": status.get("stdout", "").split("\n") if status.get("stdout") else [],
            "recent_commits": log.get("stdout", "").split("\n") if log.get("stdout") else []
        }
    
    def auto_save(self, project_path: str, step_name: str = "") -> Dict:
        """
        Auto-save current state (commit without push).
        Used during autonomous task execution.
        
        Args:
            project_path: Path to the project
            step_name: Name of the step being completed
            
        Returns:
            Dict with commit result
        """
        message = f"[Jarvis] {step_name}" if step_name else f"[Jarvis] Auto-save {datetime.now().strftime('%H:%M')}"
        return self.commit(project_path, message)
    
    def full_setup(self, project_path: str, repo_name: str = None, private: bool = True) -> Dict:
        """
        Full Git setup: init, create GitHub repo, add remote, initial push.
        
        Args:
            project_path: Path to the project
            repo_name: Name for the GitHub repo
            private: Whether repo should be private
            
        Returns:
            Dict with full setup result
        """
        results = {"steps": []}
        
        repo_name = repo_name or os.path.basename(project_path)
        
        # 1. Initialize
        init_result = self.init_repo(project_path, repo_name)
        results["steps"].append({"init": init_result})
        if not init_result["success"]:
            return results
        
        # 2. Create GitHub repo
        if self.github_token:
            github_result = self.create_github_repo(repo_name, private)
            results["steps"].append({"github": github_result})
            
            if github_result.get("success"):
                # 3. Add remote
                remote_url = github_result["clone_url"]
                if self.github_token:
                    # Use token in URL for auth
                    remote_url = remote_url.replace(
                        "https://",
                        f"https://{self.github_token}@"
                    )
                
                add_result = self.add_remote(project_path, remote_url)
                results["steps"].append({"add_remote": add_result})
                
                # 4. Push
                push_result = self.push(project_path)
                results["steps"].append({"push": push_result})
                
                results["repo_url"] = github_result["repo_url"]
        
        results["success"] = True
        return results


# Singleton
git_agent = GitAgent()
