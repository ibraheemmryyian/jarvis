"""
GitHub Integration for Jarvis v2
Read-only by default. Write mode requires explicit enable.
"""
import os
import json
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class GitHubConfig:
    """GitHub API configuration."""
    token: str
    base_url: str = "https://api.github.com"
    write_enabled: bool = False  # READ-ONLY BY DEFAULT
    allowed_repo_prefix: str = "jarvis-"  # Only touch repos with this prefix


class GitHubAgent:
    """
    Safe GitHub integration for Jarvis.
    
    SAFETY:
    - Read-only by default
    - Write mode must be explicitly enabled
    - Even with write mode, only touches repos with allowed prefix
    """
    
    def __init__(self, token: str = None):
        # Try to get token from environment or config
        self.token = token or os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN", "")
        self.config = GitHubConfig(token=self.token)
        self._headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
    
    def _request(self, method: str, endpoint: str, data: dict = None) -> dict:
        """Make API request."""
        url = f"{self.config.base_url}{endpoint}"
        try:
            if method == "GET":
                resp = requests.get(url, headers=self._headers, timeout=30)
            elif method == "POST":
                resp = requests.post(url, headers=self._headers, json=data, timeout=30)
            elif method == "PUT":
                resp = requests.put(url, headers=self._headers, json=data, timeout=30)
            else:
                return {"error": f"Unknown method: {method}"}
            
            if resp.status_code >= 400:
                return {"error": f"HTTP {resp.status_code}: {resp.text[:200]}"}
            
            return resp.json() if resp.text else {"success": True}
        except Exception as e:
            return {"error": str(e)}
    
    # === READ OPERATIONS (Always allowed) ===
    
    def get_user(self) -> dict:
        """Get authenticated user info."""
        return self._request("GET", "/user")
    
    def list_repos(self, username: str = None, limit: int = 30) -> List[dict]:
        """List repositories for a user."""
        endpoint = f"/users/{username}/repos" if username else "/user/repos"
        result = self._request("GET", f"{endpoint}?per_page={limit}&sort=updated")
        if isinstance(result, list):
            return result
        return []
    
    def get_repo(self, owner: str, repo: str) -> dict:
        """Get repository details."""
        return self._request("GET", f"/repos/{owner}/{repo}")
    
    def list_files(self, owner: str, repo: str, path: str = "") -> List[dict]:
        """List files in a repository."""
        result = self._request("GET", f"/repos/{owner}/{repo}/contents/{path}")
        if isinstance(result, list):
            return result
        return [result] if isinstance(result, dict) and "name" in result else []
    
    def get_file_content(self, owner: str, repo: str, path: str) -> str:
        """Get file content (decoded)."""
        result = self._request("GET", f"/repos/{owner}/{repo}/contents/{path}")
        if "content" in result:
            import base64
            return base64.b64decode(result["content"]).decode("utf-8")
        return result.get("error", "File not found")
    
    def search_repos(self, query: str, limit: int = 10) -> List[dict]:
        """Search public repositories."""
        result = self._request("GET", f"/search/repositories?q={query}&per_page={limit}")
        return result.get("items", [])
    
    def search_code(self, query: str, limit: int = 10) -> List[dict]:
        """Search code across GitHub."""
        result = self._request("GET", f"/search/code?q={query}&per_page={limit}")
        return result.get("items", [])
    
    # === WRITE OPERATIONS (Require explicit enable) ===
    
    def _check_write_permission(self, repo_name: str) -> tuple:
        """Check if write is allowed for this repo."""
        if not self.config.write_enabled:
            return False, "Write mode is DISABLED. Enable with github.enable_write_mode() first."
        
        if not repo_name.startswith(self.config.allowed_repo_prefix):
            return False, f"Repo must start with '{self.config.allowed_repo_prefix}'. Got: {repo_name}"
        
        return True, "OK"
    
    def enable_write_mode(self, confirm: bool = False) -> str:
        """
        Enable write operations.
        Requires explicit confirmation.
        """
        if not confirm:
            return "⚠️ Write mode allows Jarvis to create repos and push code. Call enable_write_mode(confirm=True) to enable."
        
        self.config.write_enabled = True
        return f"✅ Write mode ENABLED. Jarvis can now create/modify repos with prefix '{self.config.allowed_repo_prefix}'"
    
    def disable_write_mode(self) -> str:
        """Disable write operations."""
        self.config.write_enabled = False
        return "🔒 Write mode DISABLED. Jarvis is now read-only."
    
    def create_repo(self, name: str, description: str = "", private: bool = False) -> dict:
        """Create a new repository (requires write mode + prefix)."""
        allowed, msg = self._check_write_permission(name)
        if not allowed:
            return {"error": msg}
        
        return self._request("POST", "/user/repos", {
            "name": name,
            "description": description,
            "private": private,
            "auto_init": True
        })
    
    def push_file(self, owner: str, repo: str, path: str, content: str, message: str) -> dict:
        """Push a file to a repository (requires write mode + prefix)."""
        allowed, msg = self._check_write_permission(repo)
        if not allowed:
            return {"error": msg}
        
        import base64
        encoded = base64.b64encode(content.encode()).decode()
        
        # Check if file exists (need SHA for update)
        existing = self._request("GET", f"/repos/{owner}/{repo}/contents/{path}")
        sha = existing.get("sha") if "sha" in existing else None
        
        data = {
            "message": message,
            "content": encoded
        }
        if sha:
            data["sha"] = sha
        
        return self._request("PUT", f"/repos/{owner}/{repo}/contents/{path}", data)
    
    # === STATUS ===
    
    def status(self) -> dict:
        """Get current GitHub integration status."""
        user = self.get_user()
        return {
            "authenticated": "login" in user,
            "username": user.get("login", "unknown"),
            "write_enabled": self.config.write_enabled,
            "allowed_prefix": self.config.allowed_repo_prefix,
            "mode": "READ-WRITE" if self.config.write_enabled else "READ-ONLY"
        }


# Singleton
github = GitHubAgent()
