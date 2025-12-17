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
    
    # Common project types and their default specs
    PROJECT_TEMPLATES = {
        "crm": {
            "type": "web_app",
            "features": ["contacts", "deals", "pipeline", "notes", "search"],
            "stack": "React + FastAPI",
            "style": "modern, dark theme"
        },
        "landing": {
            "type": "website",
            "sections": ["hero", "features", "testimonials", "pricing", "cta"],
            "stack": "HTML/CSS/JS",
            "style": "premium, animated"
        },
        "dashboard": {
            "type": "web_app",
            "features": ["charts", "tables", "filters", "export"],
            "stack": "React + API",
            "style": "dark, data-rich"
        },
        "api": {
            "type": "backend",
            "features": ["CRUD", "auth", "validation", "docs"],
            "stack": "FastAPI",
            "style": "RESTful"
        },
        "blog": {
            "type": "website",
            "features": ["posts", "categories", "search", "comments"],
            "stack": "Next.js or HTML",
            "style": "clean, readable"
        }
    }
    
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
    
    def __init__(self):
        self.context_history = []
    
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
        """Detect the type of project from input."""
        type_keywords = {
            "crm": ["crm", "customer", "sales", "pipeline", "contacts"],
            "landing": ["landing", "page", "website", "homepage", "marketing"],
            "dashboard": ["dashboard", "admin", "analytics", "metrics", "stats"],
            "api": ["api", "backend", "server", "endpoint", "rest"],
            "blog": ["blog", "posts", "articles", "content", "cms"],
            "ecommerce": ["shop", "store", "ecommerce", "products", "cart"],
            "portfolio": ["portfolio", "showcase", "projects", "gallery"],
        }
        
        for proj_type, keywords in type_keywords.items():
            for kw in keywords:
                if kw in input_lower:
                    return proj_type
        
        return "website"  # Default assumption
    
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
        """Generate a detailed prompt from spec."""
        project_type = spec.get("project_type", "project")
        
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
        Use LLM for more complex refinement when rules aren't enough.
        """
        prompt = f"""Refine this user request into a detailed technical specification.

USER REQUEST: "{user_input}"

Output a JSON with:
- project_type: (website, web_app, api, mobile, etc.)
- name: suggested project name
- features: list of key features
- stack: recommended tech stack
- style: design style/theme
- priority_features: top 3 must-haves
- refined_prompt: a detailed prompt for the developer

Be practical. Infer reasonable defaults. Don't ask for more info, just make smart assumptions.

Output JSON only:"""

        response = self._call_llm(prompt)
        
        try:
            # Try to extract JSON
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
        
        # Fallback to rule-based
        return self.refine(user_input)
    
    def quick_refine(self, user_input: str) -> str:
        """
        Quick refinement - just return the refined prompt string.
        Use this when you just need the enhanced prompt.
        """
        result = self.refine(user_input)
        return result["refined_prompt"]


# Singleton
prompt_refiner = PromptRefiner()
