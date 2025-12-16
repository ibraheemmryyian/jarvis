"""
Router Agent for Jarvis v2
Classifies user intent and dispatches to the appropriate specialist agent.
"""
from .base_agent import BaseAgent
from .context_manager import context


class RouterAgent(BaseAgent):
    """Routes tasks to the appropriate specialist agent."""
    
    def __init__(self):
        super().__init__("router")
    
    def _get_system_prompt(self) -> str:
        return """Classify the request into ONE category. Reply with ONLY a JSON object.

Categories:
- CODER: build, create, make, write code, calculator, app, website, script, program, tool
- RESEARCH: search, find, analyze, market, competitors, data, statistics, trends
- OPS: deploy, github, push, hosting, server, vercel, production
- AUTONOMOUS: full business idea, startup, SaaS, product from scratch
- CHAT: hello, question, explain, help, general conversation

IMPORTANT: If user says "build", "create", "make", or mentions a specific app/tool → CODER

Reply format: {"agent": "CATEGORY", "subtasks": [], "requires_research_first": false, "estimated_complexity": "low"}

Only output the JSON. No explanation."""
    
    def classify(self, user_input: str) -> dict:
        """Classify the user's intent and return routing info."""
        input_lower = user_input.lower()
        
        # Keyword-based fast classification (reliable fallback)
        coder_keywords = ["build", "create", "make", "write", "code", "calculator", "app", "website", "script", "program", "tool", "implement"]
        research_keywords = ["research", "find", "search", "analyze", "market", "competitor", "trend", "data"]
        ops_keywords = ["deploy", "github", "push", "host", "server", "vercel", "production", "launch"]
        autonomous_keywords = ["saas", "startup", "business idea", "product from scratch", "full pipeline"]
        
        detected_agent = None
        
        # Check RESEARCH first (more specific intent)
        for kw in research_keywords:
            if kw in input_lower:
                detected_agent = "RESEARCH"
                break
        
        # Then CODER
        if not detected_agent:
            for kw in coder_keywords:
                if kw in input_lower:
                    detected_agent = "CODER"
                    break
        
        # OPS
        if not detected_agent:
            for kw in ops_keywords:
                if kw in input_lower:
                    detected_agent = "OPS"
                    break
        
        # AUTONOMOUS  
        if not detected_agent:
            for kw in autonomous_keywords:
                if kw in input_lower:
                    detected_agent = "AUTONOMOUS"
                    break
        
        # If keyword match found, return directly (faster + reliable)
        if detected_agent:
            return {
                "agent": detected_agent,
                "subtasks": [],
                "requires_research_first": detected_agent in ["CODER", "AUTONOMOUS"],
                "estimated_complexity": "medium"
            }
        
        # Fallback to LLM for ambiguous cases
        prompt = f"""User request: "{user_input}"

Output ONLY the JSON object, nothing else:"""
        
        result = self.call_llm_json(prompt)
        
        # Validate and set defaults
        if "error" in result:
            return {
                "agent": "CHAT",
                "subtasks": [],
                "requires_research_first": False,
                "estimated_complexity": "low",
                "raw_error": result.get("raw", "")
            }
        
        return {
            "agent": result.get("agent", "CHAT").upper(),
            "subtasks": result.get("subtasks", []),
            "requires_research_first": result.get("requires_research_first", False),
            "estimated_complexity": result.get("estimated_complexity", "low")
        }
    
    def run(self, task: str) -> str:
        """Route and execute the task."""
        # Classify intent
        routing = self.classify(task)
        
        # Log the decision
        context.log_decision(
            f"Route to {routing['agent']}",
            f"Complexity: {routing['estimated_complexity']}, Research first: {routing['requires_research_first']}"
        )
        
        # Set up the active task
        context.set_active_task(task, routing["subtasks"])
        
        # Return routing info (orchestrator will handle dispatch)
        return routing


# Singleton
router = RouterAgent()
