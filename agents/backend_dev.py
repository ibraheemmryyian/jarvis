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
    
    def run(self, task: str, project_context: str = "") -> str:
        """Execute backend development task with proper file naming."""
        task_lower = task.lower()
        
        # Detect file type from task
        if any(kw in task_lower for kw in ["auth", "login", "password", "jwt", "token"]):
            file_hint = "backend/auth.py"
        elif any(kw in task_lower for kw in ["database", "model", "schema", "sqlalchemy"]):
            file_hint = "backend/models.py"
        elif any(kw in task_lower for kw in ["crud", "repository"]):
            file_hint = "backend/crud.py"
        elif any(kw in task_lower for kw in ["admin", "dashboard"]):
            file_hint = "backend/admin.py"
        elif any(kw in task_lower for kw in ["payment", "stripe", "billing"]):
            file_hint = "backend/payments.py"
        elif any(kw in task_lower for kw in ["email", "notification", "smtp"]):
            file_hint = "backend/email_service.py"
        elif any(kw in task_lower for kw in ["test", "pytest"]):
            file_hint = "tests/test_api.py"
        else:
            file_hint = "backend/api.py"
        
        # Include existing project context if available
        context_section = ""
        if project_context:
            context_section = f"""
EXISTING PROJECT FILES (integrate with these, don't duplicate):
{project_context[:1500]}

IMPORTANT: Import from existing modules where appropriate. Build ON the existing codebase.
"""
        
        # Build comprehensive prompt
        prompt = f"""You are building a COMPLETE, PRODUCTION-READY backend module.

TASK: {task}
{context_section}
CRITICAL REQUIREMENTS:
1. Output COMPLETE code - no placeholders, no "..." or "# add more here"
2. Start your code block with the FILENAME comment, like: # {file_hint}
3. Include ALL imports at the top
4. Include FULL implementation with at least 100+ lines
5. Use FastAPI with Pydantic models
6. Include proper error handling with HTTPException
7. Add type hints for all functions
8. Include docstrings
9. Add input validation

SUGGESTED FILE: {file_hint}

STRUCTURE YOUR OUTPUT AS:
```python
# {file_hint}
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
# ... more imports

# Models
class YourModel(BaseModel):
    ...

# Routes/Logic
@app.get("/...")
async def your_endpoint():
    ...
```

Output the COMPLETE module code now."""

        return self._call_llm(prompt)


# Singleton
backend_dev = BackendDeveloper()
