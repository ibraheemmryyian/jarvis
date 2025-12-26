"""
Quality Assurance Agent for Jarvis v2
Verifies code quality and provides feedback loop for self-fixing.
"""
import os
import re
import json
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from .base_agent import BaseAgent
from .project_manager import project_manager


class QAAgent(BaseAgent):
    """
    Quality Assurance Agent - Validates generated code and provides feedback.
    
    Features:
    - Syntax validation (HTML, CSS, JS, Python, etc.)
    - File verification
    - Feedback loop for AI self-correction
    """
    
    def __init__(self):
        super().__init__("qa")
    
    def _get_system_prompt(self) -> str:
        return """You are a Quality Assurance expert. Your job is to:
1. Review code for bugs, errors, and best practices
2. Identify issues and suggest fixes
3. Verify that code is production-ready

When reviewing code, output a JSON report with this structure:
{
    "status": "pass" | "fail" | "warning",
    "issues": [
        {"severity": "error|warning|info", "line": 1, "message": "..."}
    ],
    "suggestions": ["..."],
    "can_auto_fix": true|false,
    "auto_fix_prompt": "..." // If can_auto_fix, describe what to fix
}"""
    
    def run(self, project_path: str) -> Dict:
        """Run full QA suite on a project."""
        results = {
            "project": project_path,
            "timestamp": datetime.now().isoformat(),
            "file_results": [],
            "overall_status": "pass",
            "total_errors": 0,
            "total_warnings": 0
        }
        
        file_index = project_manager.get_file_index(project_path)
        
        for file_entry in file_index.get("files", []):
            file_path = os.path.join(project_path, file_entry["path"])
            if os.path.exists(file_path):
                file_result = self.verify_file(file_path, file_entry["type"])
                results["file_results"].append(file_result)
                
                if file_result["status"] == "fail":
                    results["overall_status"] = "fail"
                    results["total_errors"] += len([i for i in file_result.get("issues", []) 
                                                    if i.get("severity") == "error"])
                elif file_result["status"] == "warning" and results["overall_status"] != "fail":
                    results["overall_status"] = "warning"
                
                results["total_warnings"] += len([i for i in file_result.get("issues", []) 
                                                  if i.get("severity") == "warning"])
        
        # Save QA report
        self._save_qa_report(project_path, results)
        
        return results
    
    def verify_file(self, file_path: str, file_type: str) -> Dict:
        """Verify a single file based on its type."""
        result = {
            "file": file_path,
            "type": file_type,
            "status": "pass",
            "issues": [],
            "suggestions": []
        }
        
        if not os.path.exists(file_path):
            result["status"] = "fail"
            result["issues"].append({
                "severity": "error",
                "message": "File does not exist"
            })
            return result
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        if len(content.strip()) == 0:
            result["status"] = "fail"
            result["issues"].append({
                "severity": "error",
                "message": "File is empty"
            })
            return result
        
        # Type-specific validation
        if file_type == "html":
            result = self._verify_html(content, result)
        elif file_type == "css" or file_type == "scss":
            result = self._verify_css(content, result)
        elif file_type in ["javascript", "react"]:
            result = self._verify_javascript(content, result)
        elif file_type in ["typescript", "react-ts"]:
            result = self._verify_typescript(content, result)
        elif file_type == "python":
            result = self._verify_python(content, result)
        elif file_type == "json":
            result = self._verify_json(content, result)
        
        return result
    
    # === Language-Specific Validators ===
    
    def _verify_html(self, content: str, result: Dict) -> Dict:
        """Verify HTML file."""
        # Check for DOCTYPE
        if "<!DOCTYPE html>" not in content and "<!doctype html>" not in content:
            result["issues"].append({
                "severity": "warning",
                "message": "Missing DOCTYPE declaration"
            })
        
        # Check for basic structure
        if "<html" not in content:
            result["issues"].append({
                "severity": "error",
                "message": "Missing <html> tag"
            })
            result["status"] = "fail"
        
        if "<head" not in content:
            result["issues"].append({
                "severity": "warning",
                "message": "Missing <head> section"
            })
        
        if "<body" not in content:
            result["issues"].append({
                "severity": "warning",
                "message": "Missing <body> section"
            })
        
        # Check for meta viewport (responsive)
        if "viewport" not in content:
            result["suggestions"].append("Add meta viewport for mobile responsiveness")
        
        # Check for unclosed tags (basic check)
        open_tags = len(re.findall(r'<[a-zA-Z][^/>]*>', content))
        close_tags = len(re.findall(r'</[a-zA-Z]+>', content))
        self_closing = len(re.findall(r'<[a-zA-Z][^>]*/>', content))
        
        if open_tags - close_tags > 5:  # Allow some tolerance
            result["issues"].append({
                "severity": "warning",
                "message": f"Possible unclosed tags (opens: {open_tags}, closes: {close_tags})"
            })
        
        if result["issues"] and result["status"] != "fail":
            result["status"] = "warning"
        
        return result
    
    def _verify_css(self, content: str, result: Dict) -> Dict:
        """Verify CSS file."""
        # Check for balanced braces
        open_braces = content.count('{')
        close_braces = content.count('}')
        
        if open_braces != close_braces:
            result["issues"].append({
                "severity": "error",
                "message": f"Unbalanced braces (open: {open_braces}, close: {close_braces})"
            })
            result["status"] = "fail"
        
        # Check for common issues
        if "!important" in content:
            count = content.count("!important")
            if count > 5:
                result["suggestions"].append(f"Excessive use of !important ({count} times)")
        
        # Check for missing semicolons (basic check)
        lines_without_semicolon = []
        for i, line in enumerate(content.split('\n'), 1):
            line = line.strip()
            if ':' in line and not line.endswith(';') and not line.endswith('{') and not line.endswith(','):
                if not line.startswith('/*') and not line.startswith('//'):
                    lines_without_semicolon.append(i)
        
        if lines_without_semicolon[:3]:
            result["issues"].append({
                "severity": "warning",
                "message": f"Possible missing semicolons at lines: {lines_without_semicolon[:3]}"
            })
        
        if result["issues"] and result["status"] != "fail":
            result["status"] = "warning"
        
        return result
    
    def _verify_javascript(self, content: str, result: Dict) -> Dict:
        """Verify JavaScript file."""
        # Check for balanced braces/brackets
        if content.count('{') != content.count('}'):
            result["issues"].append({
                "severity": "error",
                "message": "Unbalanced curly braces"
            })
            result["status"] = "fail"
        
        if content.count('[') != content.count(']'):
            result["issues"].append({
                "severity": "error",
                "message": "Unbalanced square brackets"
            })
            result["status"] = "fail"
        
        if content.count('(') != content.count(')'):
            result["issues"].append({
                "severity": "error",
                "message": "Unbalanced parentheses"
            })
            result["status"] = "fail"
        
        # Check for console.log (production warning)
        console_logs = len(re.findall(r'console\.log\(', content))
        if console_logs > 0:
            result["suggestions"].append(f"Remove {console_logs} console.log statements for production")
        
        # Check for var usage (suggest let/const)
        var_usage = len(re.findall(r'\bvar\s+', content))
        if var_usage > 0:
            result["suggestions"].append(f"Consider using let/const instead of var ({var_usage} occurrences)")
        
        if result["issues"] and result["status"] != "fail":
            result["status"] = "warning"
        
        return result
    
    def _verify_typescript(self, content: str, result: Dict) -> Dict:
        """Verify TypeScript file."""
        result = self._verify_javascript(content, result)
        
        # Check for any type
        any_usage = len(re.findall(r':\s*any\b', content))
        if any_usage > 3:
            result["suggestions"].append(f"Excessive use of 'any' type ({any_usage} times)")
        
        return result
    
    def _verify_python(self, content: str, result: Dict) -> Dict:
        """Verify Python file."""
        # Check for syntax using compile
        try:
            compile(content, '<string>', 'exec')
        except SyntaxError as e:
            result["issues"].append({
                "severity": "error",
                "line": e.lineno,
                "message": f"Syntax error: {e.msg}"
            })
            result["status"] = "fail"
        
        # Check for common issues
        if "import *" in content:
            result["suggestions"].append("Avoid 'import *' - use explicit imports")
        
        # Check for proper indentation
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if line.startswith(' ') and not line.startswith('    ') and len(line.strip()) > 0:
                if len(line) - len(line.lstrip()) not in [0, 4, 8, 12, 16, 20]:
                    result["issues"].append({
                        "severity": "warning",
                        "line": i,
                        "message": "Inconsistent indentation (use 4 spaces)"
                    })
                    break
        
        if result["issues"] and result["status"] != "fail":
            result["status"] = "warning"
        
        return result
    
    def _verify_json(self, content: str, result: Dict) -> Dict:
        """Verify JSON file."""
        try:
            json.loads(content)
        except json.JSONDecodeError as e:
            result["issues"].append({
                "severity": "error",
                "line": e.lineno,
                "message": f"Invalid JSON: {e.msg}"
            })
            result["status"] = "fail"
        
        return result
    
    # === Feedback Loop ===
    
    def generate_fix_prompt(self, qa_result: Dict) -> Optional[str]:
        """
        Generate a prompt for the AI to fix identified issues.
        This is the key to the feedback loop.
        """
        if qa_result["status"] == "pass":
            return None
        
        issues = []
        for file_result in qa_result.get("file_results", []):
            if file_result["status"] != "pass":
                file_issues = file_result.get("issues", [])
                if file_issues:
                    issues.append({
                        "file": file_result["file"],
                        "issues": file_issues
                    })
        
        if not issues:
            return None
        
        prompt = """The following issues were found in the code. Please fix them:

"""
        for item in issues:
            prompt += f"### File: {item['file']}\n"
            for issue in item["issues"]:
                severity = issue.get("severity", "info").upper()
                line = f" (line {issue.get('line')})" if issue.get('line') else ""
                prompt += f"- [{severity}]{line}: {issue['message']}\n"
            prompt += "\n"
        
        prompt += """
Generate the corrected code for each file. Use proper code blocks with filenames."""
        
        return prompt
    
    def run_feedback_loop(self, project_path: str, llm_call_func, max_iterations: int = 3) -> Dict:
        """
        Run QA with automatic fix attempts.
        
        Args:
            project_path: Path to the project
            llm_call_func: Function to call LLM for fixes
            max_iterations: Maximum fix attempts
        
        Returns:
            Final QA result
        """
        for iteration in range(max_iterations):
            print(f"[QA] Iteration {iteration + 1}/{max_iterations}")
            
            # Run QA
            result = self.run(project_path)
            
            if result["status"] == "pass":
                print("[QA] All checks passed!")
                return result
            
            # Generate fix prompt
            fix_prompt = self.generate_fix_prompt(result)
            
            if not fix_prompt:
                print("[QA] No actionable fixes found")
                return result
            
            print(f"[QA] Found {result['total_errors']} errors, {result['total_warnings']} warnings")
            print("[QA] Attempting auto-fix...")
            
            # Ask LLM to fix
            fix_response = llm_call_func(fix_prompt)
            
            # Extract and apply fixes
            self._apply_fixes(project_path, fix_response)
        
        # Final check
        return self.run(project_path)
    
    def _apply_fixes(self, project_path: str, fix_response: str):
        """Extract code blocks from LLM response and apply fixes."""
        import re
        
        # Pattern to match code blocks with filenames
        # Looks for patterns like: ### File: path/to/file.ext or ```html filename.html
        code_pattern = r'```(\w+)\n([\s\S]*?)```'
        matches = re.findall(code_pattern, fix_response)
        
        ext_map = {
            'html': 'index.html',
            'css': 'style.css',
            'javascript': 'script.js',
            'js': 'script.js',
            'python': 'main.py',
            'py': 'main.py',
            'json': 'data.json'
        }
        
        for lang, code in matches:
            lang = lang.lower()
            if lang in ext_map:
                # Try to find the file in the project
                file_index = project_manager.get_file_index(project_path)
                target_file = None
                
                for f in file_index.get("files", []):
                    if f["type"] == lang or f["path"].endswith(ext_map.get(lang, "")):
                        target_file = f["path"]
                        break
                
                if target_file:
                    full_path = os.path.join(project_path, target_file)
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(code.strip())
                    print(f"[QA] Applied fix to {target_file}")
    
    def _save_qa_report(self, project_path: str, results: Dict):
        """Save QA report to project."""
        jarvis_dir = os.path.join(project_path, ".jarvis")
        os.makedirs(jarvis_dir, exist_ok=True)
        report_path = os.path.join(jarvis_dir, "qa_report.json")
        with open(report_path, 'w') as f:
            json.dump(results, f, indent=2)


# Singleton
qa_agent = QAAgent()
