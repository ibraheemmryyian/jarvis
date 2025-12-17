"""
Security Auditor Agent for Jarvis v2
Specialized security-focused pessimistic reviewer.

Scans for:
- Code vulnerabilities (injection, XSS, auth issues)
- Infrastructure risks (exposed secrets, misconfigs)
- Business logic exploits
- API security issues
"""
import os
import re
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from .config import LM_STUDIO_URL, WORKSPACE_DIR
from .memory import memory


class SecurityAuditor:
    """
    Security-focused auditor agent.
    
    Features:
    - Vulnerability scanning (OWASP Top 10)
    - Secret detection
    - Dependency risk check
    - Risk categorization (critical/major/minor)
    - Auto-generates security report
    """
    
    # Patterns that indicate security issues
    DANGEROUS_PATTERNS = {
        "hardcoded_secrets": [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
            r'AWS_SECRET_ACCESS_KEY\s*=',
            r'PRIVATE_KEY\s*=',
        ],
        "sql_injection": [
            r'execute\([^)]*\+',
            r'f".*SELECT.*{',
            r'query\s*=\s*["\'].*\+',
            r'cursor\.execute\(.*%s.*%',
        ],
        "xss_vuln": [
            r'innerHTML\s*=',
            r'document\.write\(',
            r'eval\(',
            r'dangerouslySetInnerHTML',
        ],
        "command_injection": [
            r'os\.system\(',
            r'subprocess\.call\([^)]*shell=True',
            r'exec\(',
            r'eval\(',
        ],
        "insecure_random": [
            r'random\.(random|randint|choice)\(',
            r'Math\.random\(',
        ],
        "weak_crypto": [
            r'md5\(',
            r'sha1\(',
            r'DES\.',
            r'RC4\.',
        ]
    }
    
    # Files to always check
    SENSITIVE_FILES = [
        '.env', 'config.py', 'settings.py', 'secrets.py',
        'credentials.json', 'private_key.pem'
    ]
    
    def __init__(self):
        self.findings = []
        self.scan_count = 0
    
    def _call_llm(self, prompt: str) -> str:
        """Call LLM for security analysis."""
        try:
            response = requests.post(
                LM_STUDIO_URL,
                json={
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 2000
                },
                timeout=90
            )
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"[SecurityAuditor] LLM Error: {e}")
        return ""
    
    def audit_code(self, code: str, language: str = "python",
                   filename: str = "unknown") -> Dict:
        """
        Audit code for security vulnerabilities.
        
        Returns:
            {
                "vulnerabilities": [...],
                "risk_level": "critical" | "major" | "minor" | "clean",
                "should_block": True/False,
                "recommendations": [...]
            }
        """
        self.scan_count += 1
        vulnerabilities = []
        
        # Step 1: Pattern-based scanning (fast)
        pattern_findings = self._pattern_scan(code)
        vulnerabilities.extend(pattern_findings)
        
        # Step 2: LLM-based deep analysis (thorough)
        llm_findings = self._llm_security_scan(code, language)
        vulnerabilities.extend(llm_findings)
        
        # Deduplicate
        seen = set()
        unique_vulns = []
        for v in vulnerabilities:
            key = f"{v.get('type', '')}:{v.get('title', '')}"
            if key not in seen:
                seen.add(key)
                unique_vulns.append(v)
        
        # Calculate risk level
        has_critical = any(v.get("risk") == "critical" for v in unique_vulns)
        has_major = any(v.get("risk") == "major" for v in unique_vulns)
        
        if has_critical:
            risk_level = "critical"
            should_block = True
        elif has_major:
            risk_level = "major"
            should_block = False  # Don't block on major, just warn
        elif unique_vulns:
            risk_level = "minor"
            should_block = False
        else:
            risk_level = "clean"
            should_block = False
        
        # Generate recommendations
        recommendations = self._generate_recommendations(unique_vulns)
        
        # Save findings
        self.findings.extend(unique_vulns)
        
        # Log to memory
        if unique_vulns:
            memory.save_fact(
                f"Security scan of {filename}: {len(unique_vulns)} issues ({risk_level})",
                category="security",
                source="security_auditor"
            )
        
        return {
            "filename": filename,
            "vulnerabilities": unique_vulns,
            "risk_level": risk_level,
            "should_block": should_block,
            "recommendations": recommendations,
            "scan_id": self.scan_count
        }
    
    def _pattern_scan(self, code: str) -> List[Dict]:
        """Fast regex-based vulnerability detection."""
        findings = []
        
        for vuln_type, patterns in self.DANGEROUS_PATTERNS.items():
            for pattern in patterns:
                matches = re.finditer(pattern, code, re.IGNORECASE)
                for match in matches:
                    # Get line number
                    line_num = code[:match.start()].count('\n') + 1
                    
                    findings.append({
                        "type": vuln_type,
                        "title": f"Potential {vuln_type.replace('_', ' ')}",
                        "risk": self._get_vuln_risk(vuln_type),
                        "line": line_num,
                        "snippet": match.group()[:100],
                        "description": self._get_vuln_description(vuln_type)
                    })
        
        return findings
    
    def _llm_security_scan(self, code: str, language: str) -> List[Dict]:
        """Deep LLM-based security analysis."""
        prompt = f"""You are a security expert. Analyze this {language} code for vulnerabilities.

CODE:
```{language}
{code[:5000]}
```

Check for:
1. OWASP Top 10 vulnerabilities
2. Authentication/authorization flaws
3. Input validation issues
4. Sensitive data exposure
5. Security misconfigurations

For each vulnerability found, output:
RISK: [critical/major/minor]
TYPE: [vulnerability type]
TITLE: [short title]
LINE: [approximate line number or "unknown"]
DESCRIPTION: [what's wrong]
FIX: [how to fix]
---

If the code is secure, output: NO_VULNERABILITIES_FOUND

Be thorough but avoid false positives. Only report real security issues."""

        response = self._call_llm(prompt)
        
        if "NO_VULNERABILITIES_FOUND" in response:
            return []
        
        return self._parse_llm_findings(response)
    
    def _parse_llm_findings(self, response: str) -> List[Dict]:
        """Parse LLM security findings."""
        findings = []
        blocks = response.split("---")
        
        for block in blocks:
            if not block.strip():
                continue
            
            finding = {
                "risk": "minor",
                "type": "unknown",
                "title": "",
                "line": "unknown",
                "description": "",
                "fix": ""
            }
            
            for line in block.strip().split("\n"):
                line = line.strip()
                if line.startswith("RISK:"):
                    risk = line[5:].strip().lower()
                    if risk in ["critical", "major", "minor"]:
                        finding["risk"] = risk
                elif line.startswith("TYPE:"):
                    finding["type"] = line[5:].strip()
                elif line.startswith("TITLE:"):
                    finding["title"] = line[6:].strip()
                elif line.startswith("LINE:"):
                    finding["line"] = line[5:].strip()
                elif line.startswith("DESCRIPTION:"):
                    finding["description"] = line[12:].strip()
                elif line.startswith("FIX:"):
                    finding["fix"] = line[4:].strip()
            
            if finding["title"]:
                findings.append(finding)
        
        return findings
    
    def _get_vuln_risk(self, vuln_type: str) -> str:
        """Get risk level for vulnerability type."""
        critical = ["hardcoded_secrets", "sql_injection", "command_injection"]
        major = ["xss_vuln", "weak_crypto"]
        
        if vuln_type in critical:
            return "critical"
        elif vuln_type in major:
            return "major"
        return "minor"
    
    def _get_vuln_description(self, vuln_type: str) -> str:
        """Get description for vulnerability type."""
        descriptions = {
            "hardcoded_secrets": "Sensitive credentials found in code. Use environment variables instead.",
            "sql_injection": "Potential SQL injection vulnerability. Use parameterized queries.",
            "xss_vuln": "Potential cross-site scripting vulnerability. Sanitize user input.",
            "command_injection": "Potential command injection. Avoid shell execution with user input.",
            "insecure_random": "Insecure random number generation. Use secrets module for security-sensitive values.",
            "weak_crypto": "Weak cryptographic algorithm. Use SHA-256 or stronger."
        }
        return descriptions.get(vuln_type, "Potential security issue detected.")
    
    def _generate_recommendations(self, vulnerabilities: List[Dict]) -> List[str]:
        """Generate security recommendations."""
        recommendations = []
        
        vuln_types = set(v.get("type", "") for v in vulnerabilities)
        
        if "hardcoded_secrets" in vuln_types:
            recommendations.append("Move all secrets to environment variables or a secrets manager")
        if "sql_injection" in vuln_types:
            recommendations.append("Use parameterized queries or an ORM for all database operations")
        if "xss_vuln" in vuln_types:
            recommendations.append("Implement proper output encoding and use a templating engine")
        if "command_injection" in vuln_types:
            recommendations.append("Avoid os.system/subprocess with user input, use allowlists")
        if any(v.get("risk") == "critical" for v in vulnerabilities):
            recommendations.append("🚨 Address critical vulnerabilities before deployment")
        
        return recommendations
    
    def audit_project(self, project_path: str) -> Dict:
        """Audit an entire project directory."""
        all_findings = []
        files_scanned = 0
        
        for root, dirs, files in os.walk(project_path):
            # Skip common non-code directories
            dirs[:] = [d for d in dirs if d not in [
                'node_modules', '__pycache__', '.git', 'venv', '.venv',
                'dist', 'build', '.next'
            ]]
            
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.jsx', '.tsx', '.php')):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            code = f.read()
                        
                        ext = os.path.splitext(file)[1]
                        lang = {'.py': 'python', '.js': 'javascript', 
                               '.ts': 'typescript', '.php': 'php'}.get(ext, 'code')
                        
                        result = self.audit_code(code, lang, file)
                        if result["vulnerabilities"]:
                            all_findings.extend(result["vulnerabilities"])
                        files_scanned += 1
                    except Exception as e:
                        print(f"[SecurityAuditor] Error scanning {file}: {e}")
        
        # Overall risk
        has_critical = any(f.get("risk") == "critical" for f in all_findings)
        has_major = any(f.get("risk") == "major" for f in all_findings)
        
        return {
            "project_path": project_path,
            "files_scanned": files_scanned,
            "total_vulnerabilities": len(all_findings),
            "critical": len([f for f in all_findings if f.get("risk") == "critical"]),
            "major": len([f for f in all_findings if f.get("risk") == "major"]),
            "minor": len([f for f in all_findings if f.get("risk") == "minor"]),
            "overall_risk": "critical" if has_critical else "major" if has_major else "minor" if all_findings else "clean",
            "findings": all_findings,
            "recommendations": self._generate_recommendations(all_findings)
        }
    
    def generate_report(self, findings: List[Dict] = None) -> str:
        """Generate security audit report."""
        findings = findings or self.findings
        
        report = "# Security Audit Report\n\n"
        report += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        report += f"**Total Findings:** {len(findings)}\n\n"
        
        # Summary
        critical = len([f for f in findings if f.get("risk") == "critical"])
        major = len([f for f in findings if f.get("risk") == "major"])
        minor = len([f for f in findings if f.get("risk") == "minor"])
        
        report += "## Summary\n\n"
        report += f"- 🚨 Critical: {critical}\n"
        report += f"- ⚠️ Major: {major}\n"
        report += f"- ℹ️ Minor: {minor}\n\n"
        
        # Critical findings
        if critical > 0:
            report += "## 🚨 Critical Findings\n\n"
            for f in findings:
                if f.get("risk") == "critical":
                    report += f"### {f.get('title', 'Unknown')}\n"
                    report += f"**Type:** {f.get('type', 'Unknown')}\n"
                    report += f"**Line:** {f.get('line', 'Unknown')}\n"
                    report += f"{f.get('description', '')}\n"
                    if f.get('fix'):
                        report += f"**Fix:** {f.get('fix')}\n"
                    report += "\n"
        
        # Major findings
        if major > 0:
            report += "## ⚠️ Major Findings\n\n"
            for f in findings:
                if f.get("risk") == "major":
                    report += f"- **{f.get('title', 'Unknown')}**: {f.get('description', '')}\n"
        
        return report
    
    def quick_scan(self, code: str) -> str:
        """Quick pass/fail security check."""
        result = self.audit_code(code)
        
        if result["risk_level"] == "clean":
            return "✅ SECURE - No vulnerabilities found"
        elif result["risk_level"] == "critical":
            return f"🚨 CRITICAL - {result['vulnerabilities'][0]['title']}"
        elif result["risk_level"] == "major":
            return f"⚠️ MAJOR - {len(result['vulnerabilities'])} issues found"
        else:
            return f"ℹ️ MINOR - {len(result['vulnerabilities'])} low-risk issues"


# Singleton
security_auditor = SecurityAuditor()
