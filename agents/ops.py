"""
Ops Agent for Jarvis v2
Handles GitHub operations, deployments, and CI/CD.
"""
import os
import subprocess
from datetime import datetime
from .base_agent import BaseAgent
from .context_manager import context
from .config import WORKSPACE_DIR


class OpsAgent(BaseAgent):
    """Handles deployment and infrastructure operations."""
    
    def __init__(self):
        super().__init__("ops")
        self.github_available = self._check_git()
    
    def _get_system_prompt(self) -> str:
        return """You are a DevOps Engineer. You handle deployments and infrastructure.

When asked to deploy, output JSON:
{
    "action": "create_repo" | "push" | "deploy_vercel" | "status",
    "repo_name": "repo-name",
    "commit_message": "descriptive commit message",
    "branch": "main"
}

For deployment recommendations, provide:
{
    "action": "recommend",
    "platform": "vercel" | "github-pages" | "netlify",
    "reason": "why this platform",
    "steps": ["step 1", "step 2"]
}"""

    def _check_git(self) -> bool:
        """Check if git is available."""
        try:
            subprocess.run(["git", "--version"], capture_output=True, check=True)
            return True
        except:
            return False
    
    def _run_git(self, args: list, cwd: str = None) -> tuple:
        """Run a git command."""
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=cwd or WORKSPACE_DIR,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)
    
    def init_repo(self, project_path: str) -> dict:
        """Initialize a git repository."""
        full_path = os.path.join(WORKSPACE_DIR, project_path)
        
        if not os.path.exists(full_path):
            return {"success": False, "error": "Project path not found"}
        
        success, output = self._run_git(["init"], cwd=full_path)
        if success:
            # Create .gitignore
            gitignore = """node_modules/
.env
.env.local
dist/
build/
__pycache__/
*.pyc
.DS_Store
"""
            with open(os.path.join(full_path, ".gitignore"), "w") as f:
                f.write(gitignore)
            
            context.append("deployment_log", f"Initialized git repo: {project_path}")
        
        return {"success": success, "output": output}
    
    def commit(self, project_path: str, message: str) -> dict:
        """Stage all and commit."""
        full_path = os.path.join(WORKSPACE_DIR, project_path)
        
        # Stage all
        success, output = self._run_git(["add", "-A"], cwd=full_path)
        if not success:
            return {"success": False, "error": f"Stage failed: {output}"}
        
        # Commit
        success, output = self._run_git(["commit", "-m", message], cwd=full_path)
        
        if success:
            context.append("deployment_log", f"Commit: {message}")
        
        return {"success": success, "output": output}
    
    def get_deployment_plan(self, project_path: str) -> dict:
        """Analyze project and recommend deployment strategy."""
        full_path = os.path.join(WORKSPACE_DIR, project_path)
        
        # Detect project type
        has_package_json = os.path.exists(os.path.join(full_path, "package.json"))
        has_requirements = os.path.exists(os.path.join(full_path, "requirements.txt"))
        has_index_html = os.path.exists(os.path.join(full_path, "index.html"))
        
        if has_package_json:
            return {
                "platform": "vercel",
                "type": "node",
                "steps": [
                    "npm install",
                    "npm run build",
                    "vercel deploy (or connect GitHub repo to Vercel)"
                ],
                "free_tier": True
            }
        elif has_index_html:
            return {
                "platform": "github-pages",
                "type": "static",
                "steps": [
                    "Push to GitHub",
                    "Enable GitHub Pages in repo settings",
                    "Select branch to deploy"
                ],
                "free_tier": True
            }
        elif has_requirements:
            return {
                "platform": "vercel",
                "type": "python",
                "steps": [
                    "Add vercel.json with python runtime",
                    "vercel deploy"
                ],
                "free_tier": True
            }
        else:
            return {
                "platform": "unknown",
                "type": "unknown",
                "steps": ["Could not detect project type"],
                "free_tier": None
            }
    
    def run(self, task: str) -> str:
        """Execute ops task."""
        result = self.call_llm_json(task)
        
        if "error" in result:
            return f"Ops analysis failed: {result.get('raw', '')}"
        
        action = result.get("action", "")
        
        if action == "recommend":
            return f"""## Deployment Recommendation

**Platform**: {result.get('platform', 'N/A')}
**Reason**: {result.get('reason', 'N/A')}

**Steps**:
{chr(10).join(f"1. {s}" for s in result.get('steps', []))}
"""
        
        return str(result)


# Singleton
ops = OpsAgent()
