"""
Code Indexer for Jarvis v2
Smart indexing of code files with relevance-based context control.
Prevents filling LLM context with irrelevant code.
"""
import os
import re
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from .config import WORKSPACE_DIR


class CodeIndexer:
    """
    Smart code indexing with context control.
    
    Features:
    - Index code files with metadata (type, size, functions, classes)
    - Get ONLY relevant code based on current task
    - Summarize large files instead of loading full content
    - Track file dependencies
    """
    
    # Max tokens to inject into context per file
    MAX_TOKENS_PER_FILE = 500
    MAX_TOTAL_CONTEXT_TOKENS = 4000
    
    def __init__(self):
        self.indexes: Dict[str, Dict] = {}  # project_path -> index
    
    def index_project(self, project_path: str) -> Dict:
        """
        Index all code files in a project.
        Creates a lightweight index for fast lookups.
        """
        if not os.path.exists(project_path):
            return {"files": [], "error": "Project not found"}
        
        index = {
            "project_path": project_path,
            "indexed_at": datetime.now().isoformat(),
            "files": [],
            "by_type": {},
            "by_name": {},
            "total_lines": 0,
            "total_size": 0
        }
        
        for root, dirs, files in os.walk(project_path):
            # Skip hidden directories and node_modules
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
            
            for file in files:
                if self._is_code_file(file):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, project_path)
                    
                    file_info = self._index_file(full_path, rel_path)
                    index["files"].append(file_info)
                    
                    # Index by type
                    file_type = file_info["type"]
                    if file_type not in index["by_type"]:
                        index["by_type"][file_type] = []
                    index["by_type"][file_type].append(rel_path)
                    
                    # Index by name
                    index["by_name"][file] = rel_path
                    
                    index["total_lines"] += file_info["lines"]
                    index["total_size"] += file_info["size"]
        
        self.indexes[project_path] = index
        return index
    
    def _index_file(self, full_path: str, rel_path: str) -> Dict:
        """Index a single file with metadata."""
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except:
            return {
                "path": rel_path,
                "type": "unknown",
                "size": 0,
                "lines": 0,
                "error": "Could not read file"
            }
        
        lines = content.split('\n')
        file_type = self._detect_file_type(rel_path)
        
        # Extract structure (functions, classes)
        structure = self._extract_structure(content, file_type)
        
        return {
            "path": rel_path,
            "type": file_type,
            "size": len(content),
            "lines": len(lines),
            "checksum": hashlib.md5(content.encode()).hexdigest()[:8],
            "functions": structure.get("functions", []),
            "classes": structure.get("classes", []),
            "imports": structure.get("imports", []),
            "exports": structure.get("exports", [])
        }
    
    def _extract_structure(self, content: str, file_type: str) -> Dict:
        """Extract code structure (functions, classes, imports)."""
        structure = {"functions": [], "classes": [], "imports": [], "exports": []}
        
        if file_type in ["python", "py"]:
            # Python functions
            structure["functions"] = re.findall(r'def\s+(\w+)\s*\(', content)
            # Python classes
            structure["classes"] = re.findall(r'class\s+(\w+)', content)
            # Python imports
            structure["imports"] = re.findall(r'^(?:from|import)\s+([\w.]+)', content, re.MULTILINE)
            
        elif file_type in ["javascript", "typescript", "js", "ts", "jsx", "tsx"]:
            # JS functions
            structure["functions"] = re.findall(r'(?:function|const|let|var)\s+(\w+)\s*[=(]', content)
            # JS classes
            structure["classes"] = re.findall(r'class\s+(\w+)', content)
            # JS imports
            structure["imports"] = re.findall(r"import\s+.*?from\s+['\"]([^'\"]+)", content)
            # JS exports
            structure["exports"] = re.findall(r'export\s+(?:default\s+)?(?:function|class|const|let|var)?\s*(\w+)', content)
            
        elif file_type == "html":
            # HTML elements with IDs
            structure["exports"] = re.findall(r'id=["\']([^"\']+)["\']', content)
            # HTML scripts
            structure["imports"] = re.findall(r'<script\s+src=["\']([^"\']+)["\']', content)
        
        return structure
    
    def get_relevant_context(self, project_path: str, task: str, 
                             max_tokens: int = None) -> str:
        """
        Get ONLY relevant code context for a task.
        This is the key to smart context control.
        """
        max_tokens = max_tokens or self.MAX_TOTAL_CONTEXT_TOKENS
        
        # Get or create index
        if project_path not in self.indexes:
            self.index_project(project_path)
        
        index = self.indexes.get(project_path, {})
        
        if not index.get("files"):
            return "No code files found in project."
        
        # Determine relevant files based on task keywords
        relevant_files = self._find_relevant_files(index, task)
        
        # Build context with token budget
        context = f"## Project: {os.path.basename(project_path)}\n"
        context += f"Files: {len(index['files'])} | Lines: {index['total_lines']}\n\n"
        
        tokens_used = len(context.split())
        
        # Add relevant files
        for file_info in relevant_files[:5]:  # Max 5 files
            file_context = self._get_file_context(project_path, file_info, task)
            file_tokens = len(file_context.split())
            
            if tokens_used + file_tokens > max_tokens:
                # Add summary instead of full content
                context += self._get_file_summary(file_info)
            else:
                context += file_context
                tokens_used += file_tokens
        
        # Add overview of other files
        remaining = [f for f in index["files"] if f not in relevant_files][:10]
        if remaining:
            context += "\n### Other Files:\n"
            for f in remaining:
                context += f"- `{f['path']}` ({f['type']}, {f['lines']} lines)\n"
        
        return context
    
    def _find_relevant_files(self, index: Dict, task: str) -> List[Dict]:
        """Find files relevant to the current task."""
        task_lower = task.lower()
        scored_files = []
        
        for file_info in index.get("files", []):
            score = 0
            path_lower = file_info["path"].lower()
            
            # Score based on file type relevance
            if "html" in task_lower and file_info["type"] == "html":
                score += 10
            elif "css" in task_lower and file_info["type"] == "css":
                score += 10
            elif ("javascript" in task_lower or "js" in task_lower) and file_info["type"] in ["javascript", "js"]:
                score += 10
            elif "python" in task_lower and file_info["type"] == "python":
                score += 10
            elif "test" in task_lower and "test" in path_lower:
                score += 15
            elif "style" in task_lower and ("style" in path_lower or file_info["type"] == "css"):
                score += 10
            
            # Score based on keywords in path
            keywords = ["index", "main", "app", "component", "page", "route", "api"]
            for kw in keywords:
                if kw in path_lower:
                    score += 5
            
            # Score based on task keywords matching functions/classes
            for func in file_info.get("functions", []):
                if func.lower() in task_lower:
                    score += 15
            
            for cls in file_info.get("classes", []):
                if cls.lower() in task_lower:
                    score += 15
            
            if score > 0:
                scored_files.append((score, file_info))
        
        # Sort by score descending
        scored_files.sort(key=lambda x: -x[0])
        
        return [f for _, f in scored_files]
    
    def _get_file_context(self, project_path: str, file_info: Dict, task: str) -> str:
        """Get file content, possibly truncated based on relevance."""
        full_path = os.path.join(project_path, file_info["path"])
        
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except:
            return f"### {file_info['path']}\n*Could not read file*\n\n"
        
        # If file is small, include all of it
        if file_info["lines"] <= 50:
            return f"### {file_info['path']}\n```{file_info['type']}\n{content}\n```\n\n"
        
        # For larger files, include structure and key sections
        structure = file_info.get("functions", []) + file_info.get("classes", [])
        
        context = f"### {file_info['path']} ({file_info['lines']} lines)\n"
        context += f"**Structure**: {', '.join(structure[:10])}\n"
        
        # Include first 20 lines and last 10 lines
        lines = content.split('\n')
        preview = '\n'.join(lines[:20])
        if len(lines) > 30:
            preview += f"\n... ({len(lines) - 30} lines omitted) ...\n"
            preview += '\n'.join(lines[-10:])
        
        context += f"```{file_info['type']}\n{preview}\n```\n\n"
        
        return context
    
    def _get_file_summary(self, file_info: Dict) -> str:
        """Get a brief summary of a file (used when over token budget)."""
        functions = ', '.join(file_info.get("functions", [])[:5])
        classes = ', '.join(file_info.get("classes", [])[:3])
        
        summary = f"### {file_info['path']} (summary)\n"
        summary += f"- Type: {file_info['type']}, Lines: {file_info['lines']}\n"
        if functions:
            summary += f"- Functions: {functions}\n"
        if classes:
            summary += f"- Classes: {classes}\n"
        summary += "\n"
        
        return summary
    
    def _is_code_file(self, filename: str) -> bool:
        """Check if file is a code file we should index."""
        code_extensions = [
            '.py', '.js', '.ts', '.jsx', '.tsx',
            '.html', '.htm', '.css', '.scss', '.sass',
            '.json', '.yaml', '.yml', '.md',
            '.java', '.kt', '.go', '.rs', '.c', '.cpp', '.h'
        ]
        return any(filename.endswith(ext) for ext in code_extensions)
    
    def _detect_file_type(self, path: str) -> str:
        """Detect file type from extension."""
        ext = os.path.splitext(path)[1].lower()
        type_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'react',
            '.tsx': 'react-ts',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.json': 'json',
            '.md': 'markdown',
            '.yaml': 'yaml',
            '.yml': 'yaml'
        }
        return type_map.get(ext, 'unknown')
    
    # === File Editing ===
    
    def read_file(self, project_path: str, file_path: str) -> Optional[str]:
        """Read a file from the project."""
        if file_path.startswith(project_path):
            full_path = file_path
        else:
            full_path = os.path.join(project_path, file_path)
        
        if not os.path.exists(full_path):
            return None
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return None
    
    def edit_file(self, project_path: str, file_path: str, 
                  old_content: str, new_content: str) -> Dict:
        """
        Edit a file by replacing specific content.
        This is safer than full file replacement.
        """
        full_path = os.path.join(project_path, file_path) if not file_path.startswith(project_path) else file_path
        
        if not os.path.exists(full_path):
            return {"success": False, "error": "File not found"}
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                current = f.read()
            
            if old_content not in current:
                return {"success": False, "error": "Target content not found in file"}
            
            # Replace content
            updated = current.replace(old_content, new_content, 1)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(updated)
            
            # Re-index the file
            rel_path = os.path.relpath(full_path, project_path)
            if project_path in self.indexes:
                for i, file_info in enumerate(self.indexes[project_path]["files"]):
                    if file_info["path"] == rel_path:
                        self.indexes[project_path]["files"][i] = self._index_file(full_path, rel_path)
                        break
            
            return {"success": True, "path": file_path}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def append_to_file(self, project_path: str, file_path: str, 
                       content: str, position: str = "end") -> Dict:
        """Append content to a file."""
        full_path = os.path.join(project_path, file_path) if not file_path.startswith(project_path) else file_path
        
        if not os.path.exists(full_path):
            return {"success": False, "error": "File not found"}
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                current = f.read()
            
            if position == "start":
                updated = content + current
            else:  # end
                updated = current + content
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(updated)
            
            return {"success": True, "path": file_path}
            
        except Exception as e:
            return {"success": False, "error": str(e)}


# Singleton
code_indexer = CodeIndexer()
