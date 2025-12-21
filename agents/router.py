"""
Router Agent for Jarvis v2
Classifies user intent and dispatches to the appropriate specialist agent.
Uses registry for context-aware routing.
"""
from .base_agent import BaseAgent
from .context_manager import context
from .registry import registry, AGENT_CATEGORIES


class RouterAgent(BaseAgent):
    """Routes tasks to the appropriate specialist agent with context segregation."""
    
    def __init__(self):
        super().__init__("router")
    
    def _get_system_prompt(self) -> str:
        return """Classify the request into ONE category. Reply with ONLY a JSON object.

Categories:
- FRONTEND: UI, website, page, component, CSS, styling, React, animations
- BACKEND: API, database, server, endpoint, authentication, backend logic
- ARCHITECTURE: system design, architecture, product, strategy, planning
- RESEARCH: search, find, analyze, market, competitors, data, learn about
- QA: test, review, check, security, audit, validate, fix bug
- OPS: deploy, github, push, hosting, server, docker, kubernetes
- CONTENT: write, document, blog, pitch deck, SEO, content
- AUTONOMOUS: full build, create app, build system, from scratch, entire project
- CHAT: hello, question, explain, help, general conversation

IMPORTANT: 
- "build a website/app" → AUTONOMOUS (full project)
- "create a component" → FRONTEND (single piece)
- "build an API" → BACKEND (focused work)

Reply format: {"category": "CATEGORY", "specialists": [], "context_domains": [], "complexity": "low|medium|high"}

Only output the JSON. No explanation."""
    
    def classify(self, user_input: str) -> dict:
        """Classify the user's intent with context awareness."""
        input_lower = user_input.lower()
        
        # === Keyword-based fast classification ===
        
        # AUTONOMOUS - Full projects
        autonomous_keywords = ["build a", "create a full", "from scratch", "make me a", 
                              "entire", "complete project", "full app", "saas", "os", 
                              "startup", "business", "system with"]
        for kw in autonomous_keywords:
            if kw in input_lower:
                return self._build_routing("AUTONOMOUS", "high")
        
        # FRONTEND
        frontend_keywords = ["component", "ui", "page layout", "css", "style", "react", 
                            "animation", "responsive", "dark mode", "frontend"]
        for kw in frontend_keywords:
            if kw in input_lower:
                return self._build_routing("FRONTEND", "medium")
        
        # BACKEND  
        backend_keywords = ["api", "endpoint", "database", "auth", "backend", "server-side",
                          "crud", "rest", "graphql", "fastapi", "express"]
        for kw in backend_keywords:
            if kw in input_lower:
                return self._build_routing("BACKEND", "medium")
        
        # ARCHITECTURE
        arch_keywords = ["architecture", "system design", "product", "strategy", "roadmap",
                        "plan", "design doc", "adr", "technical spec"]
        for kw in arch_keywords:
            if kw in input_lower:
                return self._build_routing("ARCHITECTURE", "medium")
        
        # RESEARCH
        research_keywords = ["research", "find out", "analyze", "market", "competitor",
                           "learn about", "statistics", "data on", "search for"]
        for kw in research_keywords:
            if kw in input_lower:
                return self._build_routing("RESEARCH", "low")
        
        # QA
        qa_keywords = ["test", "review", "check", "security", "audit", "validate",
                      "fix bug", "debug", "error in"]
        for kw in qa_keywords:
            if kw in input_lower:
                return self._build_routing("QA", "medium")
        
        # OPS
        ops_keywords = ["deploy", "github", "push", "host", "docker", "kubernetes",
                       "production", "ci/cd", "vercel", "aws"]
        for kw in ops_keywords:
            if kw in input_lower:
                return self._build_routing("OPS", "medium")
        
        # CONTENT
        content_keywords = ["write", "document", "blog", "pitch deck", "seo",
                          "content", "copy", "readme", "docs"]
        for kw in content_keywords:
            if kw in input_lower:
                return self._build_routing("CONTENT", "low")
        
        # === Fallback to LLM for ambiguous cases ===
        prompt = f'User request: "{user_input}"\n\nOutput ONLY the JSON object:'
        result = self.call_llm_json(prompt)
        
        if "error" in result:
            return self._build_routing("CHAT", "low")
        
        category = result.get("category", "CHAT").upper()
        if category not in AGENT_CATEGORIES:
            category = "CHAT"
        
        complexity = result.get("complexity", "low")
        return self._build_routing(category, complexity)
    
    def _build_routing(self, category: str, complexity: str) -> dict:
        """Build routing info with context domains."""
        config = AGENT_CATEGORIES.get(category, AGENT_CATEGORIES.get("CORE", {}))
        
        return {
            "category": category,
            "specialists": config.get("agents", []),
            "context_domains": config.get("context_domains", ["task_state"]),
            "complexity": complexity,
            "requires_planning": complexity == "high" or category == "AUTONOMOUS"
        }
    
    def get_context_for_request(self, user_input: str) -> str:
        """Get only relevant context based on classified intent."""
        routing = self.classify(user_input)
        
        # Get primary specialist (first in list)
        specialists = routing.get("specialists", [])
        if specialists:
            return registry.get_context_for_agent(specialists[0])
        
        return ""
    
    def run(self, task: str) -> dict:
        """Route and return routing info."""
        routing = self.classify(task)
        
        # Log the decision
        context.log_decision(
            f"Route to {routing['category']}",
            f"Specialists: {routing['specialists']}, Complexity: {routing['complexity']}"
        )
        
        # Set up the active task
        context.set_active_task(task, [])
        
        return routing


# Singleton
router = RouterAgent()
