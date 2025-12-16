"""
Coder Agent for Jarvis v2
Multi-file code generation with project awareness.
"""
import os
import json
from .base_agent import BaseAgent
from .context_manager import context
from .config import WORKSPACE_DIR


class CoderAgent(BaseAgent):
    """Generates and manages code files."""
    
    def __init__(self):
        super().__init__("coder")
    
    def _get_system_prompt(self) -> str:
        return """You are an Expert Software Engineer. You write clean, production-ready code.

When asked to create files, output JSON:
{
    "files": [
        {"path": "relative/path/file.ext", "content": "file content here"},
        ...
    ],
    "commands": ["npm install", "pip install -r requirements.txt"],
    "notes": "Any important information"
}

Rules:
1. Use relative paths (no leading slash)
2. Write COMPLETE files, not snippets
3. Include package.json/requirements.txt when needed
4. Use modern best practices (ES6+, Python 3.10+)
5. Add helpful comments
6. For React: use Vite, functional components, hooks
7. For Python: use type hints, docstrings"""

    def write_file(self, relative_path: str, content: str) -> str:
        """Write a file to the workspace."""
        # Security: prevent path traversal
        if ".." in relative_path or relative_path.startswith("/"):
            return f"Error: Invalid path '{relative_path}'"
        
        full_path = os.path.join(WORKSPACE_DIR, relative_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        return f"Created: {relative_path}"
    
    def read_file(self, relative_path: str) -> str:
        """Read a file from the workspace."""
        full_path = os.path.join(WORKSPACE_DIR, relative_path)
        if not os.path.exists(full_path):
            return f"Error: File not found '{relative_path}'"
        
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
    
    def scaffold_project(self, project_name: str, stack: str = "react") -> dict:
        """Create a new project structure."""
        project_path = os.path.join(WORKSPACE_DIR, project_name)
        
        if os.path.exists(project_path):
            return {"status": "exists", "path": project_path}
        
        os.makedirs(project_path, exist_ok=True)
        
        if stack.lower() in ["react", "vite"]:
            # Vite React project
            files = {
                "package.json": json.dumps({
                    "name": project_name,
                    "version": "1.0.0",
                    "type": "module",
                    "scripts": {
                        "dev": "vite",
                        "build": "vite build",
                        "preview": "vite preview"
                    },
                    "dependencies": {
                        "react": "^18.2.0",
                        "react-dom": "^18.2.0"
                    },
                    "devDependencies": {
                        "vite": "^5.0.0",
                        "@vitejs/plugin-react": "^4.0.0"
                    }
                }, indent=2),
                "vite.config.js": """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
})""",
                "index.html": f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{project_name}</title>
</head>
<body>
  <div id="root"></div>
  <script type="module" src="/src/main.jsx"></script>
</body>
</html>""",
                "src/main.jsx": """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)""",
                "src/App.jsx": f"""export default function App() {{
  return (
    <div>
      <h1>{project_name}</h1>
      <p>Edit src/App.jsx to start building.</p>
    </div>
  )
}}""",
                "src/index.css": """* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: system-ui, sans-serif;
  background: #0a0a0a;
  color: #fafafa;
  min-height: 100vh;
}"""
            }
        else:
            # Python project
            files = {
                "main.py": f'''"""
{project_name}
"""

def main():
    print("Hello from {project_name}")

if __name__ == "__main__":
    main()
''',
                "requirements.txt": "# Add dependencies here\n"
            }
        
        # Write files
        results = []
        for rel_path, content in files.items():
            full = os.path.join(project_path, rel_path)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "w", encoding="utf-8") as f:
                f.write(content)
            results.append(rel_path)
        
        # Update codebase map
        context.update_codebase_map(project_path)
        
        return {"status": "created", "path": project_path, "files": results}
    
    def generate_code(self, task: str) -> dict:
        """Use LLM to generate code for a task."""
        result = self.call_llm_json(task)
        
        if "error" in result:
            return result
        
        # Write generated files
        written = []
        for file_info in result.get("files", []):
            path = file_info.get("path", "")
            content = file_info.get("content", "")
            if path and content:
                status = self.write_file(path, content)
                written.append(status)
        
        return {
            "files_written": written,
            "commands": result.get("commands", []),
            "notes": result.get("notes", "")
        }
    
    def run(self, task: str) -> str:
        """Execute coding task."""
        result = self.generate_code(task)
        
        if "error" in result:
            return f"Code generation failed: {result.get('raw', 'Unknown error')}"
        
        output = "## Code Generated\n\n"
        for f in result.get("files_written", []):
            output += f"- {f}\n"
        
        if result.get("commands"):
            output += "\n## Run These Commands:\n"
            for cmd in result["commands"]:
                output += f"```\n{cmd}\n```\n"
        
        if result.get("notes"):
            output += f"\n## Notes\n{result['notes']}\n"
        
        return output


# Singleton
coder = CoderAgent()
