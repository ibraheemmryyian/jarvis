"""
Software Architect Agent for Jarvis
Specializes in system design, architecture patterns, technical decisions.
"""
from .base_agent import BaseAgent


class ArchitectAgent(BaseAgent):
    """Software architect for system design and technical decisions."""
    
    def __init__(self):
        super().__init__("architect")
    
    def _get_system_prompt(self) -> str:
        return """You are a Principal Software Architect.

EXPERTISE:
- System design (monolith vs microservices)
- API design (REST, GraphQL, gRPC)
- Database architecture (SQL, NoSQL, time-series)
- Event-driven architecture
- Cloud architecture (AWS, GCP, Azure)
- Performance optimization
- Security architecture

PATTERNS:
- CQRS / Event Sourcing
- Domain-Driven Design
- Hexagonal Architecture
- Saga pattern
- Circuit breaker
- Strangler fig (migration)

OUTPUT FORMAT:
For architecture decisions:
1. Context and constraints
2. Options considered
3. Decision with rationale
4. Consequences (trade-offs)
5. Architecture diagram (mermaid)
6. Implementation roadmap

Always explain WHY not just WHAT."""
    
    def design_system(self, requirements: str) -> str:
        """Create system architecture design."""
        prompt = f"""Design a system architecture for:

{requirements}

Include:
- High-level architecture diagram (mermaid)
- Component breakdown
- Data flow
- Technology choices with rationale
- Scalability considerations
- Security boundaries
- API contracts
- Database schema overview"""
        return self._call_llm(prompt)
    
    def adr(self, decision: str, context: str) -> str:
        """Create Architecture Decision Record."""
        prompt = f"""Create an Architecture Decision Record (ADR):

DECISION: {decision}
CONTEXT: {context}

Format:
# ADR: [Title]

## Status
[Proposed/Accepted/Deprecated]

## Context
[Why this decision is needed]

## Decision
[What we decided]

## Consequences
[Trade-offs and impacts]

## Alternatives Considered
[Other options and why rejected]"""
        return self._call_llm(prompt)
    
    def review_architecture(self, description: str) -> str:
        """Review existing architecture for improvements."""
        prompt = f"""Review this architecture:

{description}

Analyze:
- Strengths
- Weaknesses/risks
- Scalability issues
- Security concerns
- Suggested improvements
- Priority recommendations"""
        return self._call_llm(prompt)
    
    def run(self, task: str) -> str:
        """Execute architecture task."""
        task_lower = task.lower()
        if "design" in task_lower or "architect" in task_lower:
            return self.design_system(task)
        elif "adr" in task_lower or "decision" in task_lower:
            return self.adr(task, "")
        elif "review" in task_lower:
            return self.review_architecture(task)
        else:
            return self._call_llm(f"Architecture task: {task}")


# Singleton
architect = ArchitectAgent()
