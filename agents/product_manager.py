"""
Product Manager Agent for Jarvis
Specializes in product strategy, roadmaps, requirements, user stories.
"""
from .base_agent import BaseAgent


class ProductManagerAgent(BaseAgent):
    """Product manager for requirements, roadmaps, and prioritization."""
    
    def __init__(self):
        super().__init__("product_manager")
    
    def _get_system_prompt(self) -> str:
        return """You are a Senior Product Manager.

EXPERTISE:
- Product vision and strategy
- User research synthesis
- Requirements gathering (PRD)
- User story writing
- Feature prioritization (RICE, MoSCoW)
- Roadmap planning
- Sprint planning

FRAMEWORKS:
- Jobs to be Done (JTBD)
- User Story Mapping
- RICE scoring
- Kano model
- Product-Market Fit
- North Star Metric

OUTPUT STYLE:
- Clear problem statements
- User-centric language
- Measurable success criteria
- Acceptance criteria for stories
- Dependencies mapped
- Effort estimates when asked

Write for engineering teams to implement clearly."""
    
    def create_prd(self, feature: str, context: str = None) -> str:
        """Create a Product Requirements Document."""
        prompt = f"""Create a PRD for:

FEATURE: {feature}
CONTEXT: {context or 'New feature'}

Include:
## Overview
## Problem Statement
## Goals & Success Metrics
## User Stories
## Requirements (Functional/Non-functional)
## Out of Scope
## Dependencies
## Timeline/Phases
## Risks & Mitigations"""
        return self._call_llm(prompt)
    
    def write_user_stories(self, feature: str, personas: list = None) -> str:
        """Write user stories with acceptance criteria."""
        prompt = f"""Write user stories for:

FEATURE: {feature}
PERSONAS: {', '.join(personas) if personas else 'Primary user'}

Format each story:
**As a** [user type]
**I want** [action]
**So that** [benefit]

**Acceptance Criteria:**
- Given [context], when [action], then [result]
- ...

Include edge cases and error states."""
        return self._call_llm(prompt)
    
    def prioritize_backlog(self, items: list) -> str:
        """Prioritize backlog items using RICE."""
        prompt = f"""Prioritize these backlog items using RICE:

ITEMS:
{chr(10).join(f'- {item}' for item in items)}

For each item, score:
- Reach: How many users impacted (1-10)
- Impact: How much value (0.25, 0.5, 1, 2, 3)
- Confidence: How sure are we (0-100%)
- Effort: Person-weeks

Calculate RICE score = (R * I * C) / E

Output prioritized list with rationale."""
        return self._call_llm(prompt)
    
    def create_roadmap(self, product: str, timeframe: str = "6 months") -> str:
        """Create a product roadmap."""
        prompt = f"""Create a product roadmap for:

PRODUCT: {product}
TIMEFRAME: {timeframe}

Format:
## Vision
## Now (This Quarter)
## Next (Next Quarter)
## Later (Future)

For each phase:
- Key features/initiatives
- Dependencies
- Success metrics
- Risks"""
        return self._call_llm(prompt)
    
    def run(self, task: str) -> str:
        """Execute product management task."""
        task_lower = task.lower()
        if "prd" in task_lower or "requirement" in task_lower:
            return self.create_prd(task)
        elif "user stor" in task_lower:
            return self.write_user_stories(task)
        elif "priorit" in task_lower or "backlog" in task_lower:
            return self.prioritize_backlog([task])
        elif "roadmap" in task_lower:
            return self.create_roadmap(task)
        else:
            return self._call_llm(f"Product task: {task}")


# Singleton
product_manager = ProductManagerAgent()
