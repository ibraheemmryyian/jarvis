"""
Prompt Refiner Agent for Jarvis v2
Automatically refines vague prompts into detailed execution plans.

"Build a CRM" → Detailed spec without user needing to specify everything
"""
import os
import json
import requests
from typing import Dict, List, Optional, Tuple
from .config import LM_STUDIO_URL, WORKSPACE_DIR
from .memory import memory


class PromptRefiner:
    """
    Intelligent prompt refinement that understands intent.
    
    Features:
    - Takes vague input, produces detailed spec
    - Learns from past projects
    - Asks minimal clarifying questions (0-2)
    - Infers missing details from context
    """
    
    # V4.3: REMOVED PROJECT_TEMPLATES
    # These were injecting generic features (auth, CRUD) that polluted user intent
    # Jarvis should understand intent, not assume features
    PROJECT_TEMPLATES = {}  # Empty - preserve original intent
    
    # Keywords that trigger specific inferences
    KEYWORDS = {
        "premium": {"style": "premium, high-end, polished"},
        "simple": {"complexity": "minimal, focused"},
        "fast": {"priority": "performance, speed"},
        "modern": {"style": "contemporary, 2024 design trends"},
        "startup": {"style": "bold, innovative, growth-focused"},
        "enterprise": {"style": "professional, secure, scalable"},
        "minimal": {"complexity": "minimal features", "style": "clean, whitespace"},
    }
    
    # Keywords that trigger resume/continue behavior
    CONTINUE_KEYWORDS = [
        "continue", "resume", "keep going", "carry on", "finish", 
        "complete the", "what's next", "next step", "pending",
        "where were we", "pick up", "done yet"
    ]
    
    def __init__(self):
        self.context_history = []
        self.founder_profile = self._load_founder_profile()
    
    def _load_founder_profile(self) -> str:
        """
        V4.3: Load founder profile for cofounder mode.
        Jarvis needs to know the businesses, vision, working style.
        """
        profile_path = os.path.join(WORKSPACE_DIR, ".context", "founder_profile.md")
        if os.path.exists(profile_path):
            try:
                with open(profile_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Limit to essential info (first 1500 chars)
                    return content[:1500]
            except:
                pass
        return ""
    
    def _detect_resume_intent(self, user_input: str) -> bool:
        """
        Check if user wants to resume a previous task.
        Only triggers if:
        1. Input is SHORT (< 30 chars) - meaning it's just a continue command
        2. Input STARTS with a continue keyword - meaning it's the main intent
        """
        input_lower = user_input.lower().strip()
        
        # Only trigger on short inputs (pure continue commands)
        if len(input_lower) > 50:
            return False  # If they wrote a lot, they have a new request
        
        # Check if it STARTS with a continue keyword 
        for kw in self.CONTINUE_KEYWORDS:
            if input_lower.startswith(kw):
                return True
        
        # Also match if the ENTIRE input is just the keyword
        if input_lower in self.CONTINUE_KEYWORDS:
            return True
            
        return False
    
    def _get_pending_tasks(self) -> str:
        """Read pending tasks from tasks.md and active_task.md."""
        pending = []
        
        # Check tasks.md
        tasks_file = os.path.join(WORKSPACE_DIR, "tasks.md")
        if os.path.exists(tasks_file):
            try:
                with open(tasks_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Find unchecked items
                    import re
                    unchecked = re.findall(r'- \[ \] (.+)', content)
                    pending.extend(unchecked)
            except:
                pass
        
        # Check active_task.md
        active_file = os.path.join(WORKSPACE_DIR, ".context", "active_task.md")
        if os.path.exists(active_file):
            try:
                with open(active_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Extract objective
                    obj_match = re.search(r'## Objective\s*\n(.+)', content)
                    if obj_match and "[Waiting" not in obj_match.group(1):
                        pending.insert(0, f"ACTIVE: {obj_match.group(1).strip()}")
                    # Find remaining items
                    remaining = re.findall(r'- \[ \] (.+)', content)
                    pending.extend(remaining)
            except:
                pass
        
        return pending
    
    def _call_llm(self, prompt: str, temperature: float = 0.3) -> str:
        """Call LLM for refinement."""
        try:
            response = requests.post(
                LM_STUDIO_URL,
                json={
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature,
                    "max_tokens": 1500
                },
                timeout=60
            )
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"[PromptRefiner] LLM Error: {e}")
        return ""
    
    def refine(self, user_input: str, ask_questions: bool = False) -> Dict:
        """
        Refine a vague prompt into a detailed specification.
        
        Args:
            user_input: Raw user input like "build a crm"
            ask_questions: If True, may return clarifying questions
        
        Returns:
            {
                "original": "build a crm",
                "needs_clarification": False,
                "questions": [],
                "refined_prompt": "...",
                "spec": {...},
                "confidence": 0.85
            }
        """
        input_lower = user_input.lower()
        
        # Step 0: Check for resume/continue intent
        if self._detect_resume_intent(user_input):
            pending = self._get_pending_tasks()
            if pending:
                # Build an expanded prompt from pending tasks
                task_list = "\n".join(f"- {t}" for t in pending[:5])  # Limit to 5
                expanded = f"Complete these pending tasks:\n{task_list}"
                print(f"[PromptRefiner] Detected resume intent. Expanding to:\n{expanded}")
                
                return {
                    "original": user_input,
                    "needs_clarification": False,
                    "questions": [],
                    "refined_prompt": expanded,
                    "spec": {"type": "resume", "pending_tasks": pending},
                    "confidence": 0.95
                }
        
        # Step 1: Detect project type
        project_type = self._detect_project_type(input_lower)
        
        # Step 2: Extract keywords and inferences
        inferences = self._extract_inferences(input_lower)
        
        # Step 3: Get template defaults
        template = self.PROJECT_TEMPLATES.get(project_type, {})
        
        # Step 4: Merge with inferences
        spec = {**template, **inferences}
        spec["project_type"] = project_type
        spec["original_request"] = user_input
        
        # Step 5: Check if we need clarification
        needs_clarification = False
        questions = []
        
        if ask_questions and not spec.get("features"):
            needs_clarification = True
            questions.append("What are the main features you need?")
        
        if ask_questions and project_type == "unknown":
            needs_clarification = True
            questions.append("What kind of project is this? (website, app, API, etc.)")
        
        # Step 6: Generate refined prompt
        refined_prompt = self._generate_refined_prompt(spec)
        
        # Step 7: Calculate confidence
        confidence = self._calculate_confidence(spec, user_input)
        
        # Save to memory for learning
        memory.save_fact(
            f"User requested: {user_input} → Refined to: {project_type}",
            category="prompt_patterns"
        )
        
        return {
            "original": user_input,
            "needs_clarification": needs_clarification,
            "questions": questions,
            "refined_prompt": refined_prompt,
            "spec": spec,
            "confidence": confidence
        }
    
    def _detect_project_type(self, input_lower: str) -> str:
        """Detect the type of project from input. Requires strong signals."""
        
        # Strong keywords that immediately identify project type (standalone)
        strong_keywords = {
            "crm": ["crm", "customer relationship management"],
            "landing": ["landing page"],
            "dashboard": ["dashboard", "admin panel"],
            "api": ["api", "backend", "rest api"],
            "blog": ["blog"],
            "ecommerce": ["ecommerce", "e-commerce", "online store"],
            "portfolio": ["portfolio"],
        }
        
        # First check for strong keywords
        for proj_type, keywords in strong_keywords.items():
            for kw in keywords:
                if kw in input_lower:
                    return proj_type
        
        # Weak keywords need 2+ matches to trigger
        weak_keywords = {
            "crm": ["sales", "pipeline", "deals", "customer"],
            "landing": ["homepage", "marketing", "signup"],
            "dashboard": ["analytics", "metrics", "stats", "charts"],
            "ecommerce": ["products", "cart", "checkout"],
        }
        
        for proj_type, keywords in weak_keywords.items():
            matches = sum(1 for kw in keywords if kw in input_lower)
            if matches >= 2:
                return proj_type
        
        # Default: don't assume project type, preserve original
        return "custom"
    
    def _extract_inferences(self, input_lower: str) -> Dict:
        """Extract inferences from keywords."""
        inferences = {}
        
        for keyword, values in self.KEYWORDS.items():
            if keyword in input_lower:
                inferences.update(values)
        
        # Extract specific mentions
        if "react" in input_lower:
            inferences["stack"] = "React"
        if "python" in input_lower:
            inferences["backend"] = "Python"
        if "dark" in input_lower:
            inferences["theme"] = "dark"
        if "light" in input_lower:
            inferences["theme"] = "light"
        
        return inferences
    
    def _generate_refined_prompt(self, spec: Dict) -> str:
        """Generate a detailed prompt from spec, preserving original intent."""
        original = spec.get("original_request", "")
        project_type = spec.get("project_type", "project")
        
        # If project type is known (matched a template), use template-based prompt
        if project_type in self.PROJECT_TEMPLATES:
            prompt = f"Build a {project_type}"
            
            if spec.get("style"):
                prompt += f" with a {spec['style']} design"
            
            if spec.get("features"):
                features = spec["features"]
                if isinstance(features, list):
                    prompt += f". Include: {', '.join(features)}"
                else:
                    prompt += f". Include: {features}"
            
            if spec.get("stack"):
                prompt += f". Use {spec['stack']}"
            
            if spec.get("theme"):
                prompt += f". {spec['theme'].title()} theme"
            
            prompt += ". Make it production-ready with clean code and modern best practices."
            return prompt
        
        # For unknown project types, PRESERVE the original request
        # Only add enhancements, don't replace the user's intent
        prompt = original
        
        # Add inferred details
        if spec.get("theme") and spec["theme"].lower() not in original.lower():
            prompt += f" {spec['theme'].title()} theme."
        
        if spec.get("stack") and spec["stack"].lower() not in original.lower():
            prompt += f" Use {spec['stack']}."
        
        if spec.get("style") and spec["style"] not in original.lower():
            prompt += f" Design: {spec['style']}."
        
        return prompt
    
    def _calculate_confidence(self, spec: Dict, original: str) -> float:
        """Calculate confidence in the refinement."""
        score = 0.5  # Base
        
        if spec.get("project_type") != "unknown":
            score += 0.2
        if spec.get("features"):
            score += 0.1
        if spec.get("style"):
            score += 0.1
        if len(original.split()) > 5:
            score += 0.1  # More words = more context
        
        return min(score, 1.0)
    
    def refine_with_llm(self, user_input: str) -> Dict:
        """
        V4.3: COFOUNDER MODE - Understand intent, don't add features.
        Uses low temperature for deterministic understanding.
        """
        # V4.3: Include founder profile if available
        founder_context = ""
        if self.founder_profile:
            founder_context = f"""
## FOUNDER CONTEXT (reference this for understanding):
{self.founder_profile[:800]}

"""
        
        prompt = f"""You are a technical cofounder reading a founder's quick message.
Your job is to UNDERSTAND their intent, not add features they didn't ask for.
{founder_context}
FOUNDER SAYS: "{user_input}"

CRITICAL RULES:
1. DO NOT add features not explicitly mentioned
2. DO NOT assume they want auth/login unless they said so
3. DO NOT assume they want a database unless they said so
4. FOCUS on exactly what they asked for
5. If they want a voice app, focus on VOICE - not generic web app features
6. If they mention a business (SymbioFlow, etc), reference the founder context

Output a JSON with:
{{
  "understood_intent": "What you think they actually want in 1-2 sentences",
  "project_type": "web_app | mobile | api | landing | research | tool",
  "core_features": ["Only what they explicitly mentioned or directly implied"],
  "tech_stack": "Your recommendation based on what they asked for",
  "refined_prompt": "A clear, focused prompt that preserves their original intent"
}}

Remember: They're busy. They gave you jackshit. Your job is to CATCH UP to their thinking, not add your own ideas.

Output JSON only:"""

        # V4.3: Use very low temperature for deterministic understanding
        response = self._call_llm(prompt, temperature=0.2)
        
        try:
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                spec = json.loads(json_match.group())
                return {
                    "original": user_input,
                    "needs_clarification": False,
                    "questions": [],
                    "refined_prompt": spec.get("refined_prompt", user_input),
                    "spec": spec,
                    "confidence": 0.9
                }
        except:
            pass
        
        # Fallback: Just return the original - don't corrupt intent
        return {
            "original": user_input,
            "needs_clarification": False,
            "questions": [],
            "refined_prompt": user_input,  # PRESERVE ORIGINAL
            "spec": {"original_request": user_input},
            "confidence": 0.5
        }
    
    def quick_refine(self, user_input: str) -> str:
        """
        Quick refinement - just return the refined prompt string.
        Use this when you just need the enhanced prompt.
        """
        result = self.refine(user_input)
        return result["refined_prompt"]


# Singleton
prompt_refiner = PromptRefiner()
