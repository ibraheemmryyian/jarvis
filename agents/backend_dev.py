"""
Backend Developer Agent for Jarvis
Specializes in APIs, databases, server architecture.
"""
from .base_agent import BaseAgent


class BackendDeveloper(BaseAgent):
    """Expert backend engineer specializing in APIs and databases."""
    
    def __init__(self):
        super().__init__("backend_dev")
    
    def _get_system_prompt(self) -> str:
        return """You are an Expert Backend Developer.

SPECIALTIES:
- Python (FastAPI, Django, Flask)
- Node.js (Express, NestJS, Fastify)
- Databases (PostgreSQL, MongoDB, Redis)
- API design (REST, GraphQL)
- Authentication (JWT, OAuth2, sessions)
- Message queues (RabbitMQ, Kafka)

ARCHITECTURE PRINCIPLES:
- Clean architecture / hexagonal
- SOLID principles
- Repository pattern for data access
- Dependency injection
- Proper error handling with custom exceptions
- Input validation (Pydantic, Zod)

OUTPUT FORMAT:
For APIs, output COMPLETE code with:
1. All route handlers
2. Data models/schemas
3. Database migrations
4. Error handlers
5. Auth middleware
6. Type hints (Python) or TypeScript

Always include proper logging and validation."""
    
    def create_api(self, description: str, framework: str = "fastapi") -> str:
        """Create a complete API with routes and models."""
        prompt = f"""Create a production-ready {framework} API:

{description}

Include:
- All CRUD endpoints
- Pydantic models (if Python)
- Database models
- Auth middleware
- Error handling
- Input validation
- OpenAPI docs

Output the COMPLETE API code."""
        return self._call_llm(prompt)
    
    def create_service(self, description: str) -> str:
        """Create a business logic service layer."""
        prompt = f"""Create a clean service layer:

{description}

Include:
- Service class with dependency injection
- Repository interface
- Business logic methods
- Error handling
- Unit-testable design

Output complete code."""
        return self._call_llm(prompt)
    
    def run(self, task: str) -> str:
        """Execute backend development task."""
        if "api" in task.lower() or "endpoint" in task.lower():
            return self.create_api(task)
        elif "service" in task.lower():
            return self.create_service(task)
        else:
            return self._call_llm(f"Backend task: {task}")


# Singleton
backend_dev = BackendDeveloper()
