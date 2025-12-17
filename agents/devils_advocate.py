"""
Devil's Advocate Agent for Jarvis v2
Pessimistic reviewer that challenges plans, code, and decisions.

NOT just for code - works on:
- Business plans
- Architecture decisions
- Feature specs
- Research conclusions
- Any output that needs scrutiny
"""
import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
from .config import LM_STUDIO_URL, WORKSPACE_DIR
from .memory import memory


class RiskLevel(Enum):
    """Risk categorization to avoid false loops."""
    CRITICAL = "critical"   # Must fix NOW before continuing
    MAJOR = "major"         # Should fix, but can proceed with warning
    MINOR = "minor"         # Note for later, don't block
    INFO = "info"           # Just FYI, no action needed


class DevilsAdvocate:
    """
    Pessimistic agent that finds flaws in everything.
    
    Features:
    - Challenges plans, code, business logic
    - Risk categorization (critical/major/minor/info)
    - Doesn't create infinite loops - knows when to stop
    - Works on ANY domain, not just code
    """
    
    # Max critiques before stopping (prevents loops)
    MAX_CRITIQUE_ROUNDS = 2
    
    # Risk thresholds
    RISK_THRESHOLDS = {
        RiskLevel.CRITICAL: 0.8,  # >80% = critical
        RiskLevel.MAJOR: 0.5,     # 50-80% = major
        RiskLevel.MINOR: 0.2,     # 20-50% = minor
    }
    
    def __init__(self):
        self.critique_count = {}  # Track per-item critique rounds
        self.deferred_issues = []  # Issues to address later
    
    def _call_llm(self, prompt: str, temperature: float = 0.4) -> str:
        """Call LLM for critique."""
        try:
            response = requests.post(
                LM_STUDIO_URL,
                json={
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature,
                    "max_tokens": 2000
                },
                timeout=90
            )
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"[DevilsAdvocate] LLM Error: {e}")
        return ""
    
    def critique(self, content: str, content_type: str = "general",
                 context: str = "") -> Dict:
        """
        Critique any content and categorize risks.
        
        Args:
            content: The content to critique (code, plan, document)
            content_type: "code", "plan", "business", "research", "general"
            context: Additional context
        
        Returns:
            {
                "issues": [...],
                "risk_summary": {"critical": 0, "major": 1, ...},
                "should_block": True/False,
                "deferred": [...],  # Issues for later
                "verdict": "PASS" | "FIX_REQUIRED" | "REVIEW_LATER"
            }
        """
        # Check if we've already critiqued this too many times
        content_hash = hash(content[:500])
        self.critique_count[content_hash] = self.critique_count.get(content_hash, 0) + 1
        
        if self.critique_count[content_hash] > self.MAX_CRITIQUE_ROUNDS:
            return {
                "issues": [],
                "risk_summary": {},
                "should_block": False,
                "deferred": [],
                "verdict": "PASS",
                "note": "Max critique rounds reached - proceeding"
            }
        
        # Build critique prompt based on type
        domain_prompts = {
            "code": self._code_critique_prompt(content, context),
            "plan": self._plan_critique_prompt(content, context),
            "business": self._business_critique_prompt(content, context),
            "research": self._research_critique_prompt(content, context),
            "general": self._general_critique_prompt(content, context)
        }
        
        prompt = domain_prompts.get(content_type, domain_prompts["general"])
        
        response = self._call_llm(prompt)
        
        # Parse response into structured issues
        issues = self._parse_issues(response)
        
        # Categorize by risk
        risk_summary = self._categorize_risks(issues)
        
        # Determine action
        should_block = risk_summary.get("critical", 0) > 0
        deferred = [i for i in issues if i["risk"] in ["minor", "info"]]
        
        # Store deferred issues
        if deferred:
            self.deferred_issues.extend(deferred)
            for issue in deferred:
                memory.add_briefing_item(
                    title=f"[Deferred] {issue['title'][:50]}",
                    content=issue.get("description", ""),
                    item_type="issue",
                    priority=1 if issue["risk"] == "minor" else 0
                )
        
        # Determine verdict
        if risk_summary.get("critical", 0) > 0:
            verdict = "FIX_REQUIRED"
        elif risk_summary.get("major", 0) > 0:
            verdict = "REVIEW_REQUIRED"
        else:
            verdict = "PASS"
        
        return {
            "issues": issues,
            "risk_summary": risk_summary,
            "should_block": should_block,
            "deferred": deferred,
            "verdict": verdict,
            "critique_round": self.critique_count[content_hash]
        }
    
    def _code_critique_prompt(self, code: str, context: str) -> str:
        return f"""You are a pessimistic code reviewer. Find REAL problems, not nitpicks.

CODE:
```
{code[:4000]}
```

CONTEXT: {context}

Find issues in these categories:
1. CRITICAL (must fix): Bugs, security holes, data loss risks
2. MAJOR (should fix): Performance issues, bad patterns, maintainability
3. MINOR (nice to have): Style, naming, minor improvements
4. INFO (just FYI): Observations, suggestions

For each issue, output:
RISK: [critical/major/minor/info]
TITLE: [short title]
DESCRIPTION: [what's wrong]
FIX: [how to fix]
---

Be harsh but practical. Only flag real issues, not style preferences.
If the code is actually good, say so - don't invent problems."""

    def _plan_critique_prompt(self, plan: str, context: str) -> str:
        return f"""You are a pessimistic project critic. Challenge this plan.

PLAN:
{plan[:4000]}

CONTEXT: {context}

Find issues:
1. CRITICAL: Impossible tasks, missing critical steps, circular dependencies
2. MAJOR: Underestimated complexity, missing requirements, risky assumptions
3. MINOR: Could be better organized, some redundancy
4. INFO: General observations

For each issue:
RISK: [critical/major/minor/info]
TITLE: [short title]
DESCRIPTION: [what's wrong]
FIX: [how to fix]
---

Be realistic. Plans are always imperfect - flag what actually matters."""

    def _business_critique_prompt(self, content: str, context: str) -> str:
        return f"""You are a skeptical business advisor. Poke holes in this.

CONTENT:
{content[:4000]}

CONTEXT: {context}

Find issues:
1. CRITICAL: Fatal flaws, unrealistic assumptions, legal risks
2. MAJOR: Weak market fit, competition concerns, scalability issues
3. MINOR: Messaging improvements, minor gaps
4. INFO: Market observations

For each issue:
RISK: [critical/major/minor/info]
TITLE: [short title]
DESCRIPTION: [what's wrong]
FIX: [how to fix]
---

Be honest. If the idea is good, say so. If it has real problems, call them out."""

    def _research_critique_prompt(self, research: str, context: str) -> str:
        return f"""You are a skeptical researcher. Challenge these conclusions.

RESEARCH:
{research[:4000]}

CONTEXT: {context}

Find issues:
1. CRITICAL: Wrong conclusions, misinterpreted data, missing key sources
2. MAJOR: Weak evidence, biased sampling, outdated sources
3. MINOR: Could use more depth, some gaps
4. INFO: Additional angles to explore

For each issue:
RISK: [critical/major/minor/info]
TITLE: [short title]
DESCRIPTION: [what's wrong]
FIX: [how to fix]
---"""

    def _general_critique_prompt(self, content: str, context: str) -> str:
        return f"""You are a pessimistic reviewer. Find problems with this.

CONTENT:
{content[:4000]}

CONTEXT: {context}

Categorize issues:
1. CRITICAL: Must fix before proceeding
2. MAJOR: Should address soon
3. MINOR: Nice to have
4. INFO: Just observations

For each issue:
RISK: [critical/major/minor/info]
TITLE: [short title]
DESCRIPTION: [what's wrong]
FIX: [how to fix]
---"""

    def _parse_issues(self, response: str) -> List[Dict]:
        """Parse LLM response into structured issues."""
        issues = []
        
        # Split by separator
        blocks = response.split("---")
        
        for block in blocks:
            if not block.strip():
                continue
            
            issue = {
                "risk": "info",
                "title": "",
                "description": "",
                "fix": ""
            }
            
            lines = block.strip().split("\n")
            for line in lines:
                line = line.strip()
                if line.startswith("RISK:"):
                    risk = line[5:].strip().lower()
                    if risk in ["critical", "major", "minor", "info"]:
                        issue["risk"] = risk
                elif line.startswith("TITLE:"):
                    issue["title"] = line[6:].strip()
                elif line.startswith("DESCRIPTION:"):
                    issue["description"] = line[12:].strip()
                elif line.startswith("FIX:"):
                    issue["fix"] = line[4:].strip()
            
            if issue["title"]:
                issues.append(issue)
        
        return issues
    
    def _categorize_risks(self, issues: List[Dict]) -> Dict[str, int]:
        """Count issues by risk level."""
        counts = {"critical": 0, "major": 0, "minor": 0, "info": 0}
        for issue in issues:
            risk = issue.get("risk", "info")
            counts[risk] = counts.get(risk, 0) + 1
        return counts
    
    def get_deferred_issues(self) -> List[Dict]:
        """Get all deferred issues for later review."""
        return self.deferred_issues
    
    def clear_deferred(self):
        """Clear deferred issues after they've been addressed."""
        self.deferred_issues = []
    
    def quick_check(self, content: str, content_type: str = "general") -> str:
        """Quick pass/fail check without full analysis."""
        result = self.critique(content, content_type)
        
        if result["verdict"] == "PASS":
            return "✅ PASS - No critical issues"
        elif result["verdict"] == "REVIEW_REQUIRED":
            return f"⚠️ REVIEW - {result['risk_summary'].get('major', 0)} major issues"
        else:
            return f"🚨 FIX REQUIRED - {result['risk_summary'].get('critical', 0)} critical issues"


# Singleton
devils_advocate = DevilsAdvocate()
