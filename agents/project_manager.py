"""
Project Manager for Jarvis v2
Handles project structure, tech stacks, file organization, and library awareness.
"""
import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
from .config import WORKSPACE_DIR


# Modern library/framework templates for different stacks
STACK_TEMPLATES = {
    "frontend": {
        "react": {
            "structure": ["src/", "src/components/", "src/hooks/", "src/styles/", "public/"],
            "files": {
                "package.json": {
                    "dependencies": {
                        "react": "^18.2.0",
                        "react-dom": "^18.2.0"
                    },
                    "devDependencies": {
                        "vite": "^5.0.0",
                        "@types/react": "^18.2.0"
                    }
                },
                "index.html": "public/index.html",
                "entry": "src/main.jsx"
            },
            "test_framework": "vitest"
        },
        "nextjs": {
            "structure": ["app/", "components/", "lib/", "public/", "styles/"],
            "files": {
                "package.json": {
                    "dependencies": {
                        "next": "^14.0.0",
                        "react": "^18.2.0",
                        "react-dom": "^18.2.0"
                    }
                },
                "entry": "app/page.tsx"
            },
            "test_framework": "jest"
        },
        "vanilla": {
            "structure": ["src/", "src/css/", "src/js/", "assets/"],
            "files": {
                "index.html": "src/index.html",
                "style.css": "src/css/style.css",
                "script.js": "src/js/script.js"
            },
            "test_framework": None
        }
    },
    "backend": {
        "python_fastapi": {
            "structure": ["app/", "app/routes/", "app/models/", "app/services/", "tests/"],
            "files": {
                "requirements.txt": ["fastapi", "uvicorn", "pydantic", "python-dotenv"],
                "main.py": "app/main.py",
                "entry": "app/main.py"
            },
            "test_framework": "pytest"
        },
        "python_flask": {
            "structure": ["app/", "app/routes/", "app/models/", "tests/"],
            "files": {
                "requirements.txt": ["flask", "python-dotenv", "gunicorn"],
                "main.py": "app/__init__.py",
                "entry": "app/__init__.py"
            },
            "test_framework": "pytest"
        },
        "nodejs_express": {
            "structure": ["src/", "src/routes/", "src/controllers/", "src/models/", "tests/"],
            "files": {
                "package.json": {
                    "dependencies": {
                        "express": "^4.18.0",
                        "dotenv": "^16.0.0",
                        "cors": "^2.8.5"
                    }
                },
                "entry": "src/index.js"
            },
            "test_framework": "jest"
        },
        "typescript_express": {
            "structure": ["src/", "src/routes/", "src/controllers/", "src/models/", "tests/"],
            "files": {
                "package.json": {
                    "dependencies": {
                        "express": "^4.18.0",
                        "dotenv": "^16.0.0"
                    },
                    "devDependencies": {
                        "typescript": "^5.0.0",
                        "@types/express": "^4.17.0",
                        "ts-node": "^10.9.0"
                    }
                },
                "tsconfig.json": True,
                "entry": "src/index.ts"
            },
            "test_framework": "jest"
        },
        "java_spring": {
            "structure": ["src/main/java/", "src/main/resources/", "src/test/java/"],
            "files": {
                "pom.xml": True,
                "entry": "src/main/java/Application.java"
            },
            "test_framework": "junit"
        }
    },
    "fullstack": {
        "nextjs_fullstack": {
            "structure": ["app/", "app/api/", "components/", "lib/", "prisma/"],
            "files": {
                "package.json": {
                    "dependencies": {
                        "next": "^14.0.0",
                        "react": "^18.2.0",
                        "@prisma/client": "^5.0.0"
                    }
                },
                "prisma/schema.prisma": True
            },
            "test_framework": "jest"
        },
        "python_react": {
            "structure": ["backend/", "frontend/", "backend/app/", "frontend/src/"],
            "separate_projects": True
        }
    },
    "database": {
        "postgresql": {"driver": "psycopg2", "orm": "sqlalchemy"},
        "mongodb": {"driver": "pymongo", "orm": "mongoengine"},
        "supabase": {"driver": "@supabase/supabase-js", "orm": None}
    }
}


class ProjectManager:
    """
    Manages project structure, files, and tech stack awareness.
    """
    
    def __init__(self):
        self.projects_dir = os.path.join(WORKSPACE_DIR, "projects")
        os.makedirs(self.projects_dir, exist_ok=True)
    
    def create_project(self, name: str, stack: str = "vanilla", 
                       category: str = "frontend") -> Dict:
        """
        Create a new project with proper structure.
        
        Args:
            name: Project name (will be slugified)
            stack: Tech stack (react, fastapi, express, etc.)
            category: frontend, backend, or fullstack
        """
        # Slugify name
        project_slug = name.lower().replace(" ", "-").replace("_", "-")[:30]
        project_path = os.path.join(self.projects_dir, project_slug)
        
        # Get stack template
        template = STACK_TEMPLATES.get(category, {}).get(stack, 
                   STACK_TEMPLATES["frontend"]["vanilla"])
        
        # Create project directory
        os.makedirs(project_path, exist_ok=True)
        
        # Create .jarvis metadata folder
        jarvis_path = os.path.join(project_path, ".jarvis")
        os.makedirs(jarvis_path, exist_ok=True)
        
        # Create structure from template
        for folder in template.get("structure", []):
            os.makedirs(os.path.join(project_path, folder), exist_ok=True)
        
        # Create manifest
        manifest = {
            "name": name,
            "slug": project_slug,
            "stack": stack,
            "category": category,
            "created": datetime.now().isoformat(),
            "test_framework": template.get("test_framework"),
            "entry_point": template.get("files", {}).get("entry"),
            "status": "initialized"
        }
        
        self._save_manifest(project_path, manifest)
        
        # Initialize file index
        self._init_file_index(project_path)
        
        # Initialize task log
        self._init_task_log(project_path)
        
        return {
            "path": project_path,
            "manifest": manifest,
            "template": template
        }
    
    def get_project(self, name_or_path: str) -> Optional[Dict]:
        """Get project info by name or path."""
        if os.path.isabs(name_or_path):
            project_path = name_or_path
        else:
            project_path = os.path.join(self.projects_dir, name_or_path)
        
        manifest_path = os.path.join(project_path, ".jarvis", "manifest.json")
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r') as f:
                return {"path": project_path, "manifest": json.load(f)}
        return None
    
    def list_projects(self) -> List[Dict]:
        """List all projects."""
        projects = []
        if os.path.exists(self.projects_dir):
            for name in os.listdir(self.projects_dir):
                project = self.get_project(name)
                if project:
                    projects.append(project)
        return projects
    
    # === File Management ===
    
    def add_file(self, project_path: str, relative_path: str, 
                 content: str, step: str = "") -> Dict:
        """
        Add a file to the project with proper indexing.
        """
        full_path = os.path.join(project_path, relative_path)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # Write file
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Calculate checksum
        checksum = hashlib.md5(content.encode()).hexdigest()
        
        # Update file index
        file_entry = {
            "path": relative_path,
            "type": self._detect_file_type(relative_path),
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "step": step,
            "size_bytes": len(content.encode()),
            "checksum": checksum
        }
        
        self._add_to_file_index(project_path, file_entry)
        
        return file_entry
    
    def get_file_index(self, project_path: str) -> Dict:
        """Get the file index for a project."""
        index_path = os.path.join(project_path, ".jarvis", "files.json")
        if os.path.exists(index_path):
            with open(index_path, 'r') as f:
                return json.load(f)
        return {"files": []}
    
    def get_project_context(self, project_path: str) -> str:
        """
        Get a summary of the project for AI context.
        """
        manifest = self.get_project(project_path)
        if not manifest:
            return ""
        
        file_index = self.get_file_index(project_path)
        
        context = f"""## Project: {manifest['manifest']['name']}
Stack: {manifest['manifest']['category']}/{manifest['manifest']['stack']}
Status: {manifest['manifest']['status']}
Test Framework: {manifest['manifest'].get('test_framework', 'None')}

### Files ({len(file_index.get('files', []))}):
"""
        for f in file_index.get("files", [])[:20]:  # Limit to 20 files
            context += f"- {f['path']} ({f['type']}, {f['size_bytes']}b)\n"
        
        return context
    
    # === Task Logging ===
    
    def log_task(self, project_path: str, task_type: str, 
                 description: str, result: str = ""):
        """Log a task to the project."""
        task_log_path = os.path.join(project_path, ".jarvis", "tasks.json")
        
        tasks = []
        if os.path.exists(task_log_path):
            with open(task_log_path, 'r') as f:
                tasks = json.load(f)
        
        tasks.append({
            "type": task_type,
            "description": description,
            "result": result[:500],
            "timestamp": datetime.now().isoformat()
        })
        
        with open(task_log_path, 'w') as f:
            json.dump(tasks, f, indent=2)
    
    # === Private Methods ===
    
    def _save_manifest(self, project_path: str, manifest: Dict):
        manifest_path = os.path.join(project_path, ".jarvis", "manifest.json")
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
    
    def _init_file_index(self, project_path: str):
        index_path = os.path.join(project_path, ".jarvis", "files.json")
        with open(index_path, 'w') as f:
            json.dump({"files": [], "last_updated": datetime.now().isoformat()}, f)
    
    def _init_task_log(self, project_path: str):
        task_path = os.path.join(project_path, ".jarvis", "tasks.json")
        with open(task_path, 'w') as f:
            json.dump([], f)
    
    def _add_to_file_index(self, project_path: str, file_entry: Dict):
        index_path = os.path.join(project_path, ".jarvis", "files.json")
        
        index = {"files": [], "last_updated": ""}
        if os.path.exists(index_path):
            with open(index_path, 'r') as f:
                index = json.load(f)
        
        # Update or add file
        updated = False
        for i, f in enumerate(index["files"]):
            if f["path"] == file_entry["path"]:
                index["files"][i] = file_entry
                updated = True
                break
        
        if not updated:
            index["files"].append(file_entry)
        
        index["last_updated"] = datetime.now().isoformat()
        
        with open(index_path, 'w') as f:
            json.dump(index, f, indent=2)
    
    def _detect_file_type(self, path: str) -> str:
        ext = os.path.splitext(path)[1].lower()
        type_map = {
            ".html": "html", ".htm": "html",
            ".css": "css", ".scss": "scss", ".sass": "sass",
            ".js": "javascript", ".jsx": "react",
            ".ts": "typescript", ".tsx": "react-ts",
            ".py": "python",
            ".java": "java",
            ".json": "json",
            ".md": "markdown",
            ".sql": "sql",
            ".yml": "yaml", ".yaml": "yaml"
        }
        return type_map.get(ext, "unknown")


# Singleton
project_manager = ProjectManager()
