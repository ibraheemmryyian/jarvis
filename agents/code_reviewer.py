"""
Code Review Agent for Jarvis v2
Strict code reviewer that analyzes variables, finds errors, detects unused code.
Writes detailed summaries about what each component does.
"""
import os
import re
import ast
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from .config import WORKSPACE_DIR


class CodeReviewer:
    """
    Strict code reviewer that analyzes code like a senior engineer.
    
    Features:
    - Variable usage analysis (what each variable does)
    - Function/class documentation
    - Syntax error detection
    - Unused variable/import detection
    - Missing reference detection (called but not defined)
    - Code quality scoring
    - Generates detailed review report
    """
    
    def __init__(self):
        self.current_review: Dict = {}
    
    def review_project(self, project_path: str) -> Dict:
        """
        Run full code review on a project.
        Returns detailed analysis with issues and suggestions.
        """
        review = {
            "project": project_path,
            "timestamp": datetime.now().isoformat(),
            "files_reviewed": [],
            "total_issues": 0,
            "total_warnings": 0,
            "code_quality_score": 100,
            "summary": ""
        }
        
        # Find all code files
        for root, dirs, files in os.walk(project_path):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
            
            for file in files:
                if self._is_code_file(file):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, project_path)
                    
                    file_review = self._review_file(full_path, rel_path)
                    review["files_reviewed"].append(file_review)
                    
                    review["total_issues"] += len(file_review.get("errors", []))
                    review["total_warnings"] += len(file_review.get("warnings", []))
        
        # Calculate quality score
        review["code_quality_score"] = self._calculate_quality_score(review)
        review["summary"] = self._generate_summary(review)
        
        # Save review to project
        self._save_review(project_path, review)
        
        return review
    
    def _review_file(self, full_path: str, rel_path: str) -> Dict:
        """Review a single file."""
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            return {"file": rel_path, "error": str(e)}
        
        file_type = self._detect_type(rel_path)
        lines = content.split('\n')
        
        review = {
            "file": rel_path,
            "type": file_type,
            "lines": len(lines),
            "errors": [],
            "warnings": [],
            "variables": [],
            "functions": [],
            "classes": [],
            "imports": [],
            "unused": [],
            "missing_refs": [],
            "documentation": ""
        }
        
        # Language-specific analysis
        if file_type == "python":
            self._review_python(content, review)
        elif file_type in ["javascript", "typescript"]:
            self._review_javascript(content, review)
        elif file_type == "html":
            self._review_html(content, review)
        elif file_type == "css":
            self._review_css(content, review)
        
        # Generate documentation
        review["documentation"] = self._document_file(review)
        
        return review
    
    def _review_python(self, content: str, review: Dict):
        """Deep review of Python code."""
        # Try to parse AST for accurate analysis
        try:
            tree = ast.parse(content)
            
            # Extract all definitions and usages
            defined = set()
            used = set()
            imports = set()
            
            for node in ast.walk(tree):
                # Track imports
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                        defined.add(alias.asname or alias.name)
                elif isinstance(node, ast.ImportFrom):
                    imports.add(node.module or "")
                    for alias in node.names:
                        defined.add(alias.asname or alias.name)
                
                # Track function definitions
                elif isinstance(node, ast.FunctionDef):
                    defined.add(node.name)
                    review["functions"].append({
                        "name": node.name,
                        "args": [a.arg for a in node.args.args],
                        "line": node.lineno,
                        "docstring": ast.get_docstring(node),
                        "summary": f"Function '{node.name}' with {len(node.args.args)} parameters"
                    })
                
                # Track class definitions
                elif isinstance(node, ast.ClassDef):
                    defined.add(node.name)
                    methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    review["classes"].append({
                        "name": node.name,
                        "line": node.lineno,
                        "methods": methods,
                        "docstring": ast.get_docstring(node),
                        "summary": f"Class '{node.name}' with methods: {', '.join(methods[:5])}"
                    })
                
                # Track variable assignments
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            defined.add(target.id)
                            review["variables"].append({
                                "name": target.id,
                                "line": node.lineno,
                                "summary": f"Variable '{target.id}' assigned at line {node.lineno}"
                            })
                
                # Track name usages
                elif isinstance(node, ast.Name):
                    used.add(node.id)
            
            # Find unused definitions
            unused = defined - used - {'__name__', '__main__', '__file__'}
            for name in unused:
                review["unused"].append({
                    "name": name,
                    "severity": "warning",
                    "message": f"'{name}' is defined but never used"
                })
            
            # Find missing references (used but not defined)
            # Exclude builtins
            builtins = {'print', 'len', 'range', 'str', 'int', 'float', 'list', 'dict', 
                       'True', 'False', 'None', 'self', 'cls', 'open', 'type', 'super',
                       'Exception', 'isinstance', 'hasattr', 'getattr', 'setattr'}
            missing = used - defined - builtins - imports
            for name in missing:
                review["missing_refs"].append({
                    "name": name,
                    "severity": "error",
                    "message": f"'{name}' is used but not defined"
                })
            
            review["imports"] = list(imports)
            
        except SyntaxError as e:
            review["errors"].append({
                "severity": "error",
                "line": e.lineno,
                "message": f"Syntax error: {e.msg}"
            })
    
    def _review_javascript(self, content: str, review: Dict):
        """Review JavaScript/TypeScript code."""
        # Extract function definitions
        func_pattern = r'(?:function|const|let|var)\s+(\w+)\s*(?:=\s*(?:async\s*)?\([^)]*\)\s*=>|=\s*function|\([^)]*\))'
        for match in re.finditer(func_pattern, content):
            review["functions"].append({
                "name": match.group(1),
                "summary": f"Function '{match.group(1)}'"
            })
        
        # Extract class definitions
        class_pattern = r'class\s+(\w+)'
        for match in re.finditer(class_pattern, content):
            review["classes"].append({
                "name": match.group(1),
                "summary": f"Class '{match.group(1)}'"
            })
        
        # Extract variable declarations
        var_pattern = r'(?:const|let|var)\s+(\w+)\s*='
        declared = set()
        for match in re.finditer(var_pattern, content):
            declared.add(match.group(1))
            review["variables"].append({
                "name": match.group(1),
                "summary": f"Variable '{match.group(1)}'"
            })
        
        # Check for common JS errors
        # Unused variables (simple check)
        for var in declared:
            # Count occurrences (excluding declaration)
            occurrences = len(re.findall(r'\b' + var + r'\b', content))
            if occurrences <= 1:
                review["unused"].append({
                    "name": var,
                    "severity": "warning",
                    "message": f"'{var}' may be unused"
                })
        
        # Check for console.log (should remove in production)
        if 'console.log' in content:
            review["warnings"].append({
                "severity": "warning",
                "message": "console.log statements found (remove for production)"
            })
        
        # Check for missing semicolons (common in JS)
        lines = content.split('\n')
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped and not stripped.endswith((';', '{', '}', ':', ',', '(', ')', '[', ']', '/')) \
               and not stripped.startswith(('if', 'else', 'for', 'while', '//', '/*', '*')):
                if len(stripped) > 10 and '=' in stripped:
                    review["warnings"].append({
                        "severity": "info",
                        "line": i + 1,
                        "message": "Possible missing semicolon"
                    })
    
    def _review_html(self, content: str, review: Dict):
        """Review HTML code."""
        # Check tag balance
        open_tags = len(re.findall(r'<[a-zA-Z][^/>]*(?<!/)>', content))
        close_tags = len(re.findall(r'</[a-zA-Z]+>', content))
        self_closing = len(re.findall(r'<[a-zA-Z][^>]*/>', content))
        
        if open_tags != close_tags:
            review["warnings"].append({
                "severity": "warning",
                "message": f"Tag imbalance: {open_tags} opening, {close_tags} closing tags"
            })
        
        # Check for missing alt on images
        img_without_alt = len(re.findall(r'<img(?![^>]*alt=)[^>]*>', content))
        if img_without_alt > 0:
            review["warnings"].append({
                "severity": "warning",
                "message": f"{img_without_alt} image(s) missing alt attribute (accessibility)"
            })
        
        # Check for missing meta tags
        if '<meta charset' not in content.lower():
            review["warnings"].append({
                "severity": "warning",
                "message": "Missing charset meta tag"
            })
        
        if '<meta name="viewport"' not in content.lower():
            review["warnings"].append({
                "severity": "warning",
                "message": "Missing viewport meta tag (mobile responsiveness)"
            })
        
        # Extract IDs for documentation
        ids = re.findall(r'id=["\']([^"\']+)["\']', content)
        for id_name in ids:
            review["variables"].append({
                "name": id_name,
                "type": "HTML id",
                "summary": f"Element with id='{id_name}'"
            })
        
        # Extract classes
        classes = set(re.findall(r'class=["\']([^"\']+)["\']', content))
        for class_list in classes:
            for cls in class_list.split():
                review["classes"].append({
                    "name": cls,
                    "type": "CSS class",
                    "summary": f"CSS class '{cls}'"
                })
    
    def _review_css(self, content: str, review: Dict):
        """Review CSS code."""
        # Extract selectors
        selector_pattern = r'([.#]?\w[\w-]*)\s*{'
        selectors = set()
        for match in re.finditer(selector_pattern, content):
            selectors.add(match.group(1))
            review["classes"].append({
                "name": match.group(1),
                "summary": f"CSS selector '{match.group(1)}'"
            })
        
        # Check for !important overuse
        important_count = len(re.findall(r'!important', content))
        if important_count > 5:
            review["warnings"].append({
                "severity": "warning",
                "message": f"Excessive use of !important ({important_count} times)"
            })
        
        # Check for vendor prefixes without standard
        prefixed = re.findall(r'-(?:webkit|moz|ms|o)-(\w+)', content)
        for prop in prefixed:
            if prop not in content:
                review["warnings"].append({
                    "severity": "info",
                    "message": f"Vendor-prefixed '{prop}' without standard property"
                })
    
    def _document_file(self, review: Dict) -> str:
        """Generate documentation summary for a file."""
        doc = f"## {review['file']}\n\n"
        doc += f"**Type**: {review['type']} | **Lines**: {review['lines']}\n\n"
        
        if review["functions"]:
            doc += "### Functions\n"
            for func in review["functions"][:10]:
                doc += f"- `{func['name']}`: {func.get('summary', 'No description')}\n"
            doc += "\n"
        
        if review["classes"]:
            doc += "### Classes\n"
            for cls in review["classes"][:10]:
                doc += f"- `{cls['name']}`: {cls.get('summary', 'No description')}\n"
            doc += "\n"
        
        if review["variables"]:
            doc += "### Variables\n"
            for var in review["variables"][:10]:
                doc += f"- `{var['name']}`: {var.get('summary', 'Defined')}\n"
            doc += "\n"
        
        if review["unused"]:
            doc += "### ⚠️ Unused\n"
            for item in review["unused"]:
                doc += f"- `{item['name']}`: {item['message']}\n"
            doc += "\n"
        
        if review["missing_refs"]:
            doc += "### ❌ Missing References\n"
            for item in review["missing_refs"]:
                doc += f"- `{item['name']}`: {item['message']}\n"
            doc += "\n"
        
        return doc
    
    def _calculate_quality_score(self, review: Dict) -> int:
        """Calculate overall code quality score (0-100)."""
        score = 100
        
        # Deduct for errors
        score -= review["total_issues"] * 10
        
        # Deduct for warnings
        score -= review["total_warnings"] * 2
        
        # Deduct for unused code
        for file_review in review["files_reviewed"]:
            score -= len(file_review.get("unused", [])) * 3
            score -= len(file_review.get("missing_refs", [])) * 15
        
        return max(0, min(100, score))
    
    def _generate_summary(self, review: Dict) -> str:
        """Generate human-readable summary."""
        score = review["code_quality_score"]
        
        if score >= 90:
            grade = "A - Excellent"
        elif score >= 80:
            grade = "B - Good"
        elif score >= 70:
            grade = "C - Acceptable"
        elif score >= 60:
            grade = "D - Needs Improvement"
        else:
            grade = "F - Critical Issues"
        
        return f"""## Code Review Summary

**Quality Score**: {score}/100 ({grade})
**Files Reviewed**: {len(review['files_reviewed'])}
**Issues Found**: {review['total_issues']} errors, {review['total_warnings']} warnings

### Recommendations:
{"- Fix all syntax errors before deployment" if review['total_issues'] > 0 else "- No critical syntax errors found"}
{"- Address unused code to reduce bundle size" if any(f.get('unused') for f in review['files_reviewed']) else ""}
{"- Verify all referenced variables are defined" if any(f.get('missing_refs') for f in review['files_reviewed']) else ""}
"""
    
    def _save_review(self, project_path: str, review: Dict):
        """Save review to project's .jarvis directory."""
        import json
        
        jarvis_dir = os.path.join(project_path, ".jarvis")
        os.makedirs(jarvis_dir, exist_ok=True)
        
        # Save full review
        review_path = os.path.join(jarvis_dir, "code_review.json")
        with open(review_path, 'w', encoding='utf-8') as f:
            json.dump(review, f, indent=2)
        
        # Save documentation
        doc_path = os.path.join(jarvis_dir, "CODE_DOCUMENTATION.md")
        with open(doc_path, 'w', encoding='utf-8') as f:
            f.write("# Code Documentation\n\n")
            f.write(f"*Generated: {review['timestamp']}*\n\n")
            f.write(review["summary"])
            f.write("\n---\n\n")
            for file_review in review["files_reviewed"]:
                f.write(file_review.get("documentation", ""))
    
    def _is_code_file(self, filename: str) -> bool:
        """Check if file should be reviewed."""
        extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.scss']
        return any(filename.endswith(ext) for ext in extensions)
    
    def _detect_type(self, path: str) -> str:
        """Detect file type."""
        ext = os.path.splitext(path)[1].lower()
        types = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'react',
            '.tsx': 'react-ts',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss'
        }
        return types.get(ext, 'unknown')


# Singleton
code_reviewer = CodeReviewer()
