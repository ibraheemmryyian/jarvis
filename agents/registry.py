"""
Agent Registry for Jarvis
Central registry of all 52 agents with context routing.
Each agent gets ONLY the context it needs - no pollution.

AUTO-REGISTRATION: All agents are registered on import.
"""
import os
from typing import Dict, List, Optional, Any
from .config import CONTEXT_DIR


# Agent categories with their context domains
AGENT_CATEGORIES = {
    "FRONTEND": {
        "agents": ["frontend_dev", "uiux", "seo"],
        "context_domains": ["frontend", "decisions"],
        "description": "Frontend development specialists"
    },
    "BACKEND": {
        "agents": ["backend_dev", "coder", "ai_ops", "ai_infra"],
        "context_domains": ["backend", "database", "decisions"],
        "description": "Backend and API development"
    },
    "ARCHITECTURE": {
        "agents": ["architect", "product_manager", "strategy", "business_analyst"],
        "context_domains": ["architecture", "decisions", "research"],
        "description": "System design and product strategy"
    },
    "RESEARCH": {
        "agents": ["researcher", "brute_researcher", "academic_research", "synthesizer", "research_publisher"],
        "context_domains": ["research"],
        "description": "Research and academic writing"
    },
    "QA": {
        "agents": ["qa_agent", "code_reviewer", "security_auditor", "visual_qa", "devils_advocate"],
        "context_domains": ["qa", "codebase"],
        "description": "Testing, review, and security"
    },
    "OPS": {
        "agents": ["ops", "git_agent", "github_agent", "terminal"],
        "context_domains": ["deployment", "decisions"],
        "description": "DevOps and deployment"
    },
    "CONTENT": {
        "agents": ["content_writer", "pitch_deck", "document_engine", "seo_specialist"],
        "context_domains": ["content", "research"],
        "description": "Content creation and documentation"
    },
    "PRODUCTIVITY": {
        "agents": ["email_agent", "calendar_agent", "slack_agent", "daily_briefing", "notifications"],
        "context_domains": ["productivity"],
        "description": "Personal productivity tools"
    },
    "CORE": {
        "agents": ["router", "autonomous", "orchestrator", "recycler", "memory"],
        "context_domains": ["task_state", "decisions"],
        "description": "Core orchestration agents"
    }
}


# Context domain definitions with max sizes
CONTEXT_DOMAINS = {
    "frontend": {"file": "frontend_context.md", "max_tokens": 4000},
    "backend": {"file": "backend_context.md", "max_tokens": 4000},
    "database": {"file": "database_context.md", "max_tokens": 2000},
    "research": {"file": "research_context.md", "max_tokens": 6000},
    "decisions": {"file": "decisions_context.md", "max_tokens": 3000},
    "architecture": {"file": "architecture_context.md", "max_tokens": 4000},
    "qa": {"file": "qa_context.md", "max_tokens": 3000},
    "codebase": {"file": "codebase_context.md", "max_tokens": 5000},
    "deployment": {"file": "deployment_context.md", "max_tokens": 2000},
    "content": {"file": "content_context.md", "max_tokens": 4000},
    "productivity": {"file": "productivity_context.md", "max_tokens": 2000},
    "task_state": {"file": "task_state.md", "max_tokens": 3000}
}


class AgentRegistry:
    """Central registry for all Jarvis agents with context segregation."""
    
    _instance = None  # Singleton
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._agents = {}
        self._ensure_context_files()
        self._initialized = True
    
    def _ensure_context_files(self):
        """Create all context domain files."""
        os.makedirs(CONTEXT_DIR, exist_ok=True)
        for domain, config in CONTEXT_DOMAINS.items():
            filepath = os.path.join(CONTEXT_DIR, config["file"])
            if not os.path.exists(filepath):
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(f"# {domain.upper()} Context\n\n")
    
    def register(self, name: str, agent: Any, category: str = None):
        """Register an agent with its category."""
        self._agents[name] = {
            "agent": agent,
            "category": category or self._detect_category(name)
        }
    
    def _detect_category(self, agent_name: str) -> str:
        """Detect category from agent name."""
        for category, config in AGENT_CATEGORIES.items():
            if agent_name in config["agents"]:
                return category
        return "CORE"
    
    def get_agent(self, name: str) -> Optional[Any]:
        """Get agent by name."""
        entry = self._agents.get(name)
        return entry["agent"] if entry else None
    
    def get_category(self, agent_name: str) -> str:
        """Get category for an agent."""
        entry = self._agents.get(agent_name)
        if entry:
            return entry["category"]
        return self._detect_category(agent_name)
    
    def get_context_domains(self, agent_name: str) -> List[str]:
        """Get context domains an agent should receive."""
        category = self.get_category(agent_name)
        config = AGENT_CATEGORIES.get(category, {})
        return config.get("context_domains", ["task_state"])
    
    def get_context_for_agent(self, agent_name: str) -> str:
        """
        Get aggregated context for a specific agent.
        Only loads domains relevant to that agent - prevents pollution!
        """
        domains = self.get_context_domains(agent_name)
        
        context_parts = []
        total_tokens = 0
        max_total = 15000  # Max context to inject
        
        for domain in domains:
            if domain not in CONTEXT_DOMAINS:
                continue
                
            config = CONTEXT_DOMAINS[domain]
            filepath = os.path.join(CONTEXT_DIR, config["file"])
            
            if os.path.exists(filepath):
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                    
                    if content and len(content) > 50:
                        domain_tokens = len(content) // 4
                        
                        if total_tokens + domain_tokens < max_total:
                            context_parts.append(f"## {domain.upper()}\n{content}")
                            total_tokens += domain_tokens
                except:
                    pass
        
        if context_parts:
            return "\n\n---\n\n".join(context_parts)
        return ""
    
    def save_to_domain(self, domain: str, content: str, agent_name: str = None):
        """Save content to a domain with timestamping and size management."""
        if domain not in CONTEXT_DOMAINS:
            domain = "decisions"
        
        config = CONTEXT_DOMAINS[domain]
        filepath = os.path.join(CONTEXT_DIR, config["file"])
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M")
        source = f" ({agent_name})" if agent_name else ""
        
        entry = f"\n### [{timestamp}]{source}\n{content}\n"
        
        existing = ""
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                existing = f.read()
        
        combined = existing + entry
        
        # Enforce max size (keep newest)
        max_chars = config["max_tokens"] * 4
        if len(combined) > max_chars:
            combined = combined[-max_chars:]
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(combined)
    
    def clear_domain(self, domain: str):
        """Clear a domain's context."""
        if domain in CONTEXT_DOMAINS:
            config = CONTEXT_DOMAINS[domain]
            filepath = os.path.join(CONTEXT_DIR, config["file"])
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# {domain.upper()} Context\n\n")
    
    def clear_all_domains(self):
        """Clear all domains for a fresh start."""
        for domain in CONTEXT_DOMAINS:
            self.clear_domain(domain)
    
    def get_agents_by_category(self, category: str) -> List[str]:
        """Get all agent names in a category."""
        config = AGENT_CATEGORIES.get(category.upper(), {})
        return config.get("agents", [])
    
    def get_all_categories(self) -> List[str]:
        """Get all category names."""
        return list(AGENT_CATEGORIES.keys())
    
    def get_status(self) -> Dict:
        """Get registry status."""
        return {
            "registered_agents": len(self._agents),
            "total_defined": sum(len(c["agents"]) for c in AGENT_CATEGORIES.values()),
            "categories": len(AGENT_CATEGORIES),
            "context_domains": len(CONTEXT_DOMAINS)
        }


# Singleton instance
registry = AgentRegistry()


# === AUTO-REGISTRATION ===
# Import and register all agents

def _auto_register_agents():
    """Auto-register all available agents."""
    agent_imports = {
        # === FRONTEND ===
        "frontend_dev": (".frontend_dev", "frontend_dev"),
        "uiux": (".uiux", "uiux"),
        "seo_specialist": (".seo", "seo_specialist"),
        
        # === BACKEND ===
        "backend_dev": (".backend_dev", "backend_dev"),
        "coder": (".coder", "coder"),
        "ai_ops": (".ai_ops", "ai_ops"),
        "ai_infra": (".ai_infra", "ai_infra"),
        
        # === ARCHITECTURE ===
        "architect": (".architect", "architect"),
        "product_manager": (".product_manager", "product_manager"),
        "strategy": (".strategy", "strategy"),
        "business_analyst": (".business_analyst", "business_analyst"),
        
        # === RESEARCH ===
        "researcher": (".research", "researcher"),
        "brute_researcher": (".brute_research", "brute_researcher"),
        "academic_research": (".academic_research", "academic_research"),
        "deep_research_v2": (".synthesis", "deep_research_v2"),
        "research_publisher": (".research_publisher", "research_publisher"),
        "academic_workflow": (".academic_workflow", "academic_workflow"),
        
        # === QA ===
        "qa_agent": (".qa", "qa_agent"),
        "code_reviewer": (".code_reviewer", "code_reviewer"),
        "security_auditor": (".security_auditor", "security_auditor"),
        "visual_qa": (".visual_qa", "visual_qa"),
        "devils_advocate": (".devils_advocate", "devils_advocate"),
        "browser_tester": (".browser_tester", "browser_tester"),
        
        # === OPS ===
        "ops": (".ops", "ops"),
        "git_agent": (".git_agent", "git_agent"),
        "github_agent": (".github_agent", "github_agent"),
        "terminal": (".terminal", "terminal"),
        
        # === CONTENT ===
        "content_writer": (".content_writer", "content_writer"),
        "pitch_deck": (".pitch_deck", "pitch_deck"),
        "pitch_deck_scorer": (".pitch_deck", "pitch_deck_scorer"),
        "document_engine": (".document_engine", "document_engine"),
        
        # === PRODUCTIVITY ===
        "email_agent": (".email_agent", "email_agent"),
        "calendar_agent": (".calendar_agent", "calendar_agent"),
        "slack_agent": (".slack_agent", "slack_agent"),
        "daily_briefing": (".daily_briefing", "daily_briefing"),
        "notifications": (".notifications", "notifications"),
        
        # === CORE ===
        "memory": (".memory", "memory"),
        "project_manager": (".project_manager", "project_manager"),
        "prompt_refiner": (".prompt_refiner", "prompt_refiner"),
        "design_creativity": (".design_creativity", "design_creativity"),
        "code_indexer": (".code_indexer", "code_indexer"),
        "jarvis_identity": (".jarvis_identity", "JarvisIdentity"),
        "autonomous": (".autonomous", "AutonomousExecutor"),
        "orchestrator": (".orchestrator", "Orchestrator"),
        
        # === SEARCH & RESEARCH ===
        "google_search": (".google_search", "GoogleSearch"),
        "synthesizer": (".synthesis", "deep_research_v2"),
        "personality": (".personality", "PersonalityEnhancer"),
        
        # === MISSING AGENTS (fixing export names) ===
        "researcher": (".research", "ResearchAgent"),
        "brute_researcher": (".brute_research", "BruteResearcher"),
        "github_agent": (".github_agent", "github_agent"),
        "notifications": (".notifications", "notifications"),
        "qa": (".qa", "qa_agent"),
        "seo": (".seo", "seo_specialist"),
        "synthesis": (".synthesis", "deep_research_v2"),
    }
    
    for name, (module_path, attr_name) in agent_imports.items():
        try:
            import importlib
            module = importlib.import_module(module_path, package="agents")
            agent = getattr(module, attr_name)
            registry.register(name, agent)
        except Exception as e:
            pass  # Agent not available, skip silently


# Run auto-registration
_auto_register_agents()


# Helper functions for easy access
def get_context_for_agent(agent_name: str) -> str:
    """Get segregated context for an agent."""
    return registry.get_context_for_agent(agent_name)


def save_context(domain: str, content: str, agent: str = None):
    """Save content to a domain."""
    registry.save_to_domain(domain, content, agent)


def get_agent(name: str):
    """Get agent by name."""
    return registry.get_agent(name)


def get_agents_for_category(category: str) -> List[str]:
    """Get agent names for a category."""
    return registry.get_agents_by_category(category)
