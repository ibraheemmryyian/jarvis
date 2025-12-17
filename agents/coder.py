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
    
    # === SMART FILE EDITING (No Full Rewrites!) ===
    
    def edit_lines(self, relative_path: str, start_line: int, end_line: int, 
                   new_content: str) -> str:
        """
        Edit specific lines in a file (surgical edit).
        
        Args:
            relative_path: Path to file
            start_line: First line to replace (1-indexed)
            end_line: Last line to replace (inclusive)
            new_content: New content for those lines
        """
        content = self.read_file(relative_path)
        if content.startswith("Error:"):
            return content
        
        lines = content.split('\n')
        
        # Validate line numbers
        if start_line < 1 or end_line > len(lines) or start_line > end_line:
            return f"Error: Invalid line range {start_line}-{end_line} (file has {len(lines)} lines)"
        
        # Replace lines (convert to 0-indexed)
        new_lines = new_content.split('\n')
        lines[start_line-1:end_line] = new_lines
        
        # Write back
        return self.write_file(relative_path, '\n'.join(lines))
    
    def insert_at_line(self, relative_path: str, line_number: int, 
                       content: str) -> str:
        """
        Insert content at a specific line (pushes existing content down).
        
        Args:
            relative_path: Path to file
            line_number: Line to insert at (1-indexed)
            content: Content to insert
        """
        file_content = self.read_file(relative_path)
        if file_content.startswith("Error:"):
            return file_content
        
        lines = file_content.split('\n')
        new_lines = content.split('\n')
        
        # Insert at position (convert to 0-indexed)
        insert_pos = max(0, min(line_number - 1, len(lines)))
        lines[insert_pos:insert_pos] = new_lines
        
        return self.write_file(relative_path, '\n'.join(lines))
    
    def append_to_file(self, relative_path: str, content: str) -> str:
        """Append content to end of file."""
        existing = self.read_file(relative_path)
        if existing.startswith("Error:"):
            # File doesn't exist, create it
            return self.write_file(relative_path, content)
        
        new_content = existing + '\n' + content if existing else content
        return self.write_file(relative_path, new_content)
    
    def search_replace(self, relative_path: str, search: str, 
                       replace: str, count: int = -1) -> str:
        """
        Search and replace text in a file.
        
        Args:
            relative_path: Path to file
            search: Text to find
            replace: Replacement text
            count: Max replacements (-1 for all)
        """
        content = self.read_file(relative_path)
        if content.startswith("Error:"):
            return content
        
        if search not in content:
            return f"Error: '{search[:50]}...' not found in {relative_path}"
        
        if count == -1:
            new_content = content.replace(search, replace)
        else:
            new_content = content.replace(search, replace, count)
        
        return self.write_file(relative_path, new_content)
    
    def patch_file(self, relative_path: str, patches: list) -> str:
        """
        Apply multiple patches to a file.
        
        Args:
            relative_path: Path to file
            patches: List of patch operations:
                [
                    {"action": "replace", "search": "old", "replace": "new"},
                    {"action": "insert", "line": 10, "content": "new line"},
                    {"action": "delete", "start": 5, "end": 10},
                    {"action": "append", "content": "new stuff"}
                ]
        """
        results = []
        
        for patch in patches:
            action = patch.get("action", "")
            
            if action == "replace":
                result = self.search_replace(
                    relative_path,
                    patch.get("search", ""),
                    patch.get("replace", "")
                )
            elif action == "insert":
                result = self.insert_at_line(
                    relative_path,
                    patch.get("line", 1),
                    patch.get("content", "")
                )
            elif action == "delete":
                result = self.edit_lines(
                    relative_path,
                    patch.get("start", 1),
                    patch.get("end", 1),
                    ""  # Empty = delete
                )
            elif action == "append":
                result = self.append_to_file(
                    relative_path,
                    patch.get("content", "")
                )
            elif action == "edit_lines":
                result = self.edit_lines(
                    relative_path,
                    patch.get("start", 1),
                    patch.get("end", 1),
                    patch.get("content", "")
                )
            else:
                result = f"Unknown action: {action}"
            
            results.append(result)
        
        return f"Applied {len(patches)} patches: " + ", ".join(results)
    
    def smart_edit(self, relative_path: str, instruction: str) -> str:
        """
        Smart edit using LLM to understand what to change.
        
        Args:
            relative_path: Path to file
            instruction: Natural language instruction like "add a dark mode toggle"
        """
        current_content = self.read_file(relative_path)
        if current_content.startswith("Error:"):
            return current_content
        
        prompt = f"""You are editing an existing file. DO NOT rewrite the whole file.
Output ONLY the specific patches needed as JSON.

CURRENT FILE ({relative_path}):
```
{current_content[:8000]}
```

INSTRUCTION: {instruction}

Output JSON with patches:
{{
    "patches": [
        {{"action": "replace", "search": "exact text to find", "replace": "new text"}},
        {{"action": "insert", "line": 15, "content": "new code to insert"}},
        {{"action": "append", "content": "code to add at end"}}
    ],
    "notes": "what was changed"
}}

IMPORTANT: 
- Use "replace" for modifying existing code (search must be EXACT match)
- Use "insert" for adding new code at a specific line
- Use "append" for adding at the end
- Keep patches minimal and surgical"""

        result = self.call_llm_json(prompt)
        
        if "error" in result:
            return f"Smart edit failed: {result.get('error')}"
        
        patches = result.get("patches", [])
        if not patches:
            return "No patches generated"
        
        return self.patch_file(relative_path, patches)
    
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
