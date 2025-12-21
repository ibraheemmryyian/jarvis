"""
Project Builder for Jarvis
Handles cohesive project generation instead of fragmented files.
Creates proper project structure and manages file integration.
"""
import os
import re
from typing import Dict, List, Optional
from datetime import datetime


class ProjectBuilder:
    """
    Manages project file creation with proper structure.
    Prevents fragmentation by integrating code into existing files.
    """
    
    TEMPLATES = {
        "vanilla": {
            "structure": {
                "index.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name}</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <!-- JARVIS: Insert sections here -->
    <script src="script.js"></script>
</body>
</html>""",
                "styles.css": """/* {project_name} Styles */
:root {
    --primary: #6366f1;
    --secondary: #8b5cf6;
    --bg-dark: #0f0f23;
    --bg-card: #1a1a2e;
    --text: #e2e8f0;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', -apple-system, sans-serif;
    background: var(--bg-dark);
    color: var(--text);
    line-height: 1.6;
}

/* JARVIS: Insert component styles here */
""",
                "script.js": """// {project_name} JavaScript

document.addEventListener('DOMContentLoaded', () => {{
    console.log('{project_name} loaded');
    
    // JARVIS: Insert component scripts here
}});
"""
            }
        },
        "react": {
            "structure": {
                "package.json": """{
  "name": "{project_name_slug}",
  "version": "0.1.0",
  "private": true,
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
    "@vitejs/plugin-react": "^4.0.0",
    "vite": "^5.0.0"
  }
}""",
                "vite.config.js": """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
})""",
                "index.html": """<!DOCTYPE html>
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
                "src/App.jsx": """import React from 'react'

function App() {
  return (
    <div className="app">
      {/* JARVIS: Insert components here */}
      <h1>{project_name}</h1>
    </div>
  )
}

export default App""",
                "src/index.css": """/* {project_name} Styles */
:root {
  --primary: #6366f1;
  --secondary: #8b5cf6;
  --bg-dark: #0f0f23;
  --text: #e2e8f0;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, sans-serif;
  background: var(--bg-dark);
  color: var(--text);
}

/* JARVIS: Insert component styles here */
"""
            }
        }
    }
    
    def __init__(self, workspace_dir: str):
        self.workspace_dir = workspace_dir
        self.projects_dir = os.path.join(workspace_dir, "projects")
        os.makedirs(self.projects_dir, exist_ok=True)
        
        self.current_project: Optional[str] = None
        self.project_path: Optional[str] = None
        self.project_files: Dict[str, str] = {}
    
    def create_project(self, name: str, template: str = "vanilla") -> str:
        """
        Create a new project with proper structure.
        Returns the project path.
        """
        # Slugify name
        slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
        timestamp = datetime.now().strftime("%Y%m%d")
        project_name = f"{slug}-{timestamp}"
        
        self.project_path = os.path.join(self.projects_dir, project_name)
        self.current_project = name
        
        # Create directory
        os.makedirs(self.project_path, exist_ok=True)
        
        # Create .jarvis metadata
        jarvis_dir = os.path.join(self.project_path, ".jarvis")
        os.makedirs(jarvis_dir, exist_ok=True)
        
        # Write project info
        with open(os.path.join(jarvis_dir, "project.json"), "w") as f:
            import json
            json.dump({
                "name": name,
                "slug": project_name,
                "template": template,
                "created": datetime.now().isoformat(),
                "files": []
            }, f, indent=2)
        
        # Apply template
        if template in self.TEMPLATES:
            self._apply_template(template, name)
        
        print(f"[ProjectBuilder] Created: {project_name}")
        return self.project_path
    
    def _apply_template(self, template: str, project_name: str):
        """Apply a project template."""
        template_data = self.TEMPLATES[template]
        slug = re.sub(r'[^a-z0-9]+', '-', project_name.lower()).strip('-')
        
        for rel_path, content in template_data["structure"].items():
            # Replace placeholders
            content = content.replace("{project_name}", project_name)
            content = content.replace("{project_name_slug}", slug)
            
            # Create file
            full_path = os.path.join(self.project_path, rel_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            self.project_files[rel_path] = content
            print(f"  Created: {rel_path}")
    
    def inject_code(self, file_path: str, code: str, marker: str = "JARVIS") -> bool:
        """
        Inject code into an existing file at a marker location.
        Looks for <!-- JARVIS: ... --> or /* JARVIS: ... */ or // JARVIS: ...
        """
        full_path = os.path.join(self.project_path, file_path)
        
        if not os.path.exists(full_path):
            # Create the file if it doesn't exist
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(code)
            return True
        
        # Read existing content
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Find marker patterns
        patterns = [
            (r'(<!--\s*' + marker + r':[^>]*-->)', 'html'),
            (r'(/\*\s*' + marker + r':[^*]*\*/)', 'css'),
            (r'(//\s*' + marker + r':[^\n]*\n)', 'js'),
        ]
        
        injected = False
        for pattern, lang in patterns:
            if re.search(pattern, content):
                # Replace marker with code + marker (so we can inject more later)
                new_content = re.sub(
                    pattern,
                    code + "\n\n\\1",
                    content,
                    count=1
                )
                if new_content != content:
                    content = new_content
                    injected = True
                    break
        
        if injected:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        
        # Fallback: append to file
        with open(full_path, "a", encoding="utf-8") as f:
            f.write("\n\n" + code)
        return True
    
    def merge_files(self, source_files: List[str], target_file: str) -> bool:
        """
        Merge multiple generated files into a single cohesive file.
        Used to fix fragmentation.
        """
        combined_content = []
        
        for src in source_files:
            src_path = os.path.join(self.project_path, src)
            if os.path.exists(src_path):
                with open(src_path, "r", encoding="utf-8") as f:
                    combined_content.append(f"<!-- Section: {src} -->\n{f.read()}")
        
        if combined_content:
            target_path = os.path.join(self.project_path, target_file)
            with open(target_path, "w", encoding="utf-8") as f:
                f.write("\n\n".join(combined_content))
            return True
        
        return False
    
    def get_file(self, file_path: str) -> Optional[str]:
        """Get the contents of a file in the project."""
        full_path = os.path.join(self.project_path, file_path)
        if os.path.exists(full_path):
            with open(full_path, "r", encoding="utf-8") as f:
                return f.read()
        return None
    
    def update_file(self, file_path: str, content: str):
        """Update or create a file in the project."""
        full_path = os.path.join(self.project_path, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        self.project_files[file_path] = content
    
    def list_files(self) -> List[str]:
        """List all files in the current project."""
        files = []
        if self.project_path:
            for root, _, filenames in os.walk(self.project_path):
                for filename in filenames:
                    rel_path = os.path.relpath(
                        os.path.join(root, filename),
                        self.project_path
                    )
                    if not rel_path.startswith(".jarvis"):
                        files.append(rel_path)
        return files
    
    def get_project_context(self) -> str:
        """
        Get the current project state as context for the next step.
        This is the key to preventing fragmentation!
        """
        if not self.project_path:
            return ""
        
        files = self.list_files()
        context_parts = [f"## Current Project: {self.current_project}\n"]
        context_parts.append(f"Files: {', '.join(files)}\n")
        
        # Include main files content
        main_files = ["index.html", "src/App.jsx", "styles.css", "src/index.css"]
        for f in main_files:
            content = self.get_file(f)
            if content:
                # Truncate if too long
                if len(content) > 2000:
                    content = content[:2000] + "\n... (truncated)"
                context_parts.append(f"\n### {f}:\n```\n{content}\n```\n")
        
        return "\n".join(context_parts)


# Singleton
from .config import WORKSPACE_DIR
project_builder = ProjectBuilder(WORKSPACE_DIR)
