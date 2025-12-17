"""
Jarvis API Layer
FastAPI-based REST API for Jarvis agent platform.

Endpoints:
- /agents - Agent management
- /tasks - Task queue management
- /memory - Memory operations
- /content - Content generation
- /briefing - Daily briefing
"""
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.memory import memory
from agents.content_writer import content_writer
from agents.daily_briefing import daily_briefing
from agents.pitch_deck import pitch_deck, pitch_deck_scorer
from agents.business_analyst import business_analyst
from agents.academic_research import academic_research

app = FastAPI(
    title="Jarvis API",
    description="AI Agent Platform API",
    version="2.0.0"
)

# CORS for web dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple API key auth
API_KEY = os.environ.get("JARVIS_API_KEY", "dev-key-change-me")

def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


# === Models ===

class TaskCreate(BaseModel):
    title: str
    priority: int = 0
    due_date: Optional[str] = None

class ContentRequest(BaseModel):
    topic: str
    content_type: str = "blog"
    tone: str = "professional"
    keywords: Optional[List[str]] = None

class EmailRequest(BaseModel):
    purpose: str
    context: str = ""
    recipient_type: str = "prospect"
    email_type: str = "cold_outreach"
    tone: str = "professional"

class SocialRequest(BaseModel):
    platform: str
    topic: str
    context: str = ""
    tone: str = "casual"

class MessageSave(BaseModel):
    role: str
    content: str
    session_id: str = "default"

class FactSave(BaseModel):
    content: str
    category: str = "general"
    source: Optional[str] = None

class PitchDeckRequest(BaseModel):
    company: str
    description: str
    industry: str = "tech"
    additional_info: Optional[Dict] = None

class BusinessAnalysisRequest(BaseModel):
    company: str
    description: str
    industry: str

class ResearchRequest(BaseModel):
    query: str
    max_results: int = 10


# === Health ===

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "2.0.0"}


# === Memory Endpoints ===

@app.post("/memory/message")
def save_message(msg: MessageSave, api_key: str = Depends(verify_api_key)):
    success = memory.save_message(msg.role, msg.content, msg.session_id)
    return {"success": success}

@app.get("/memory/conversation/{session_id}")
def get_conversation(session_id: str, limit: int = 50, 
                     api_key: str = Depends(verify_api_key)):
    return memory.get_conversation(session_id, limit)

@app.delete("/memory/conversation/{session_id}")
def clear_conversation(session_id: str, api_key: str = Depends(verify_api_key)):
    success = memory.clear_conversation(session_id)
    return {"success": success}

@app.post("/memory/fact")
def save_fact(fact: FactSave, api_key: str = Depends(verify_api_key)):
    success = memory.save_fact(fact.content, fact.category, fact.source)
    return {"success": success}

@app.get("/memory/search")
def search_memory(query: str, category: str = None, limit: int = 10,
                  api_key: str = Depends(verify_api_key)):
    return memory.search_facts(query, category, limit)

@app.get("/memory/stats")
def get_memory_stats(api_key: str = Depends(verify_api_key)):
    return memory.get_stats()

@app.get("/memory/recall")
def recall_memory(query: str, limit: int = 5,
                  api_key: str = Depends(verify_api_key)):
    return {"recall": memory.recall(query, limit)}


# === Task Endpoints ===

@app.post("/tasks")
def create_task(task: TaskCreate, api_key: str = Depends(verify_api_key)):
    success = daily_briefing.add_task(task.title, task.priority, task.due_date)
    return {"success": success}

@app.get("/tasks")
def get_tasks(include_completed: bool = False, 
              api_key: str = Depends(verify_api_key)):
    return memory.get_briefing_items(include_completed=include_completed)

@app.post("/tasks/{task_id}/complete")
def complete_task(task_id: int, api_key: str = Depends(verify_api_key)):
    success = daily_briefing.complete_task(task_id)
    return {"success": success}

@app.get("/tasks/status")
def get_task_status(api_key: str = Depends(verify_api_key)):
    return {"status": daily_briefing.get_quick_status()}


# === Briefing Endpoints ===

@app.get("/briefing")
def get_briefing(user_name: str = "Boss", voice_mode: bool = False,
                 api_key: str = Depends(verify_api_key)):
    return daily_briefing.generate(user_name, voice_mode=voice_mode)

@app.get("/briefing/voice")
def get_voice_briefing(api_key: str = Depends(verify_api_key)):
    return {"briefing": daily_briefing.get_voice_briefing()}


# === Content Endpoints ===

@app.post("/content/blog")
def create_blog(req: ContentRequest, api_key: str = Depends(verify_api_key)):
    return content_writer.write_blog(
        topic=req.topic,
        keywords=req.keywords,
        tone=req.tone
    )

@app.post("/content/email")
def create_email(req: EmailRequest, api_key: str = Depends(verify_api_key)):
    return content_writer.write_email(
        purpose=req.purpose,
        context=req.context,
        recipient_type=req.recipient_type,
        email_type=req.email_type,
        tone=req.tone
    )

@app.post("/content/social")
def create_social(req: SocialRequest, api_key: str = Depends(verify_api_key)):
    return content_writer.write_social(
        platform=req.platform,
        topic=req.topic,
        context=req.context,
        tone=req.tone
    )

@app.post("/content/ideas")
def generate_ideas(topic: str, content_type: str = "blog", count: int = 10,
                   api_key: str = Depends(verify_api_key)):
    return content_writer.generate_ideas(topic, content_type, count)


# === Business Suite Endpoints ===

@app.post("/business/pitch-deck")
def create_pitch_deck(req: PitchDeckRequest, 
                      api_key: str = Depends(verify_api_key)):
    result = pitch_deck.generate(
        req.company, req.description, req.industry, req.additional_info
    )
    # Add quality score
    score = pitch_deck_scorer.score(result["slides"])
    result["quality_score"] = score
    return result

@app.post("/business/analysis")
def run_business_analysis(req: BusinessAnalysisRequest,
                          api_key: str = Depends(verify_api_key)):
    return business_analyst.full_analysis(
        req.company, req.description, req.industry
    )

@app.post("/business/swot")
def run_swot(req: BusinessAnalysisRequest,
             api_key: str = Depends(verify_api_key)):
    return business_analyst.swot_analysis(req.company, req.description)

@app.post("/business/market-sizing")
def run_market_sizing(product: str, target_market: str,
                      api_key: str = Depends(verify_api_key)):
    return business_analyst.market_sizing(product, target_market)

@app.post("/business/competitors")
def run_competitor_analysis(company: str, industry: str,
                            api_key: str = Depends(verify_api_key)):
    return business_analyst.competitor_analysis(company, industry)


# === Research Endpoints ===

@app.post("/research/papers")
def search_papers(req: ResearchRequest, 
                  api_key: str = Depends(verify_api_key)):
    return academic_research.search(req.query, req.max_results)

@app.post("/research/literature-review")
def create_literature_review(topic: str,
                             api_key: str = Depends(verify_api_key)):
    return academic_research.generate_literature_review(topic)


# === Agent Endpoints ===

@app.get("/agents")
def list_agents(api_key: str = Depends(verify_api_key)):
    """List all available agents."""
    return {
        "agents": [
            {"name": "memory", "status": "active", "type": "infrastructure"},
            {"name": "content_writer", "status": "active", "type": "content"},
            {"name": "daily_briefing", "status": "active", "type": "productivity"},
            {"name": "pitch_deck", "status": "active", "type": "business"},
            {"name": "business_analyst", "status": "active", "type": "business"},
            {"name": "academic_research", "status": "active", "type": "research"},
            {"name": "coder", "status": "active", "type": "development"},
            {"name": "autonomous", "status": "active", "type": "orchestration"},
            {"name": "terminal", "status": "active", "type": "infrastructure"},
            {"name": "git_agent", "status": "active", "type": "development"},
        ],
        "total": 30
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
