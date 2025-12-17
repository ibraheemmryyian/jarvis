"""
Orchestrator v2 for Jarvis
Full 40-agent coordination with intelligent routing and critique phases.

Routes to:
- Development: coder, code_reviewer, qa, terminal, git_agent
- Research: researcher, brute_research, academic_research, synthesis
- Business: business_analyst, pitch_deck, content_writer
- Productivity: daily_briefing, memory, calendar, email, slack
- QA: devils_advocate, security_auditor, visual_qa
- Infrastructure: autonomous, recycler, project_manager
"""
import time
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any

# Core routing
from .router import router
from .context_manager import context

# Development agents
from .coder import coder
from .code_reviewer import code_reviewer
from .qa import qa_agent
from .terminal import terminal
from .git_agent import git_agent
from .project_manager import project_manager
from .design_creativity import design_creativity
from .code_indexer import code_indexer

# Research agents
from .research import researcher
from .brute_research import brute_searcher
from .synthesis import deep_research_v2
from .academic_research import academic_research

# Business agents
from .business_analyst import business_analyst
from .pitch_deck import pitch_deck, pitch_deck_scorer
from .content_writer import content_writer

# Productivity agents
from .daily_briefing import daily_briefing
from .memory import memory
from .email_agent import email_agent
from .calendar_agent import calendar_agent
from .slack_agent import slack_agent

# QA / Review agents
from .devils_advocate import devils_advocate
from .security_auditor import security_auditor
from .visual_qa import visual_qa

# Infrastructure
from .autonomous import AutonomousExecutor
from .recycler import recycler
from .prompt_refiner import prompt_refiner
from .ops import ops

# Document generation
from .document_engine import document_engine


class Orchestrator:
    """
    The master brain that coordinates all 40 agents.
    
    Features:
    - Intelligent routing based on intent
    - Auto-prompt refinement
    - Critique phases (devil's advocate, security)
    - Multi-step pipelines
    - Progress tracking
    """
    
    # Agent categories for routing
    AGENT_CATEGORIES = {
        "development": {
            "agents": ["coder", "code_reviewer", "qa", "terminal", "git_agent", "project_manager"],
            "keywords": ["build", "code", "create", "develop", "fix", "debug", "website", "app", "api", "script"]
        },
        "research": {
            "agents": ["researcher", "brute_research", "academic_research", "synthesis"],
            "keywords": ["research", "find", "search", "look up", "papers", "study", "investigate", "analyze data"]
        },
        "business": {
            "agents": ["business_analyst", "pitch_deck", "content_writer"],
            "keywords": ["pitch", "deck", "swot", "analysis", "market", "competitor", "business", "strategy", "content", "blog", "email", "social"]
        },
        "productivity": {
            "agents": ["daily_briefing", "memory", "calendar", "email", "slack"],
            "keywords": ["briefing", "schedule", "calendar", "email", "slack", "remind", "remember", "task"]
        },
        "ops": {
            "agents": ["ops", "git_agent", "terminal"],
            "keywords": ["deploy", "push", "commit", "run", "execute", "install", "server"]
        },
        "documents": {
            "agents": ["document_engine"],
            "keywords": ["document", "word", "excel", "pdf", "report", "proposal", "spreadsheet", "docx", "xlsx"]
        }
    }
    
    def __init__(self):
        self.execution_log = []
        self.autonomous = AutonomousExecutor()
        
        # Direct agent references
        self.agents = {
            # Development
            "coder": coder,
            "code_reviewer": code_reviewer,
            "qa": qa_agent,
            "terminal": terminal,
            "git_agent": git_agent,
            "project_manager": project_manager,
            "design_creativity": design_creativity,
            "code_indexer": code_indexer,
            
            # Research
            "researcher": researcher,
            "brute_research": brute_searcher,
            "academic_research": academic_research,
            
            # Business
            "business_analyst": business_analyst,
            "pitch_deck": pitch_deck,
            "content_writer": content_writer,
            
            # Productivity
            "daily_briefing": daily_briefing,
            "memory": memory,
            "email_agent": email_agent,
            "calendar_agent": calendar_agent,
            "slack_agent": slack_agent,
            
            # QA
            "devils_advocate": devils_advocate,
            "security_auditor": security_auditor,
            "visual_qa": visual_qa,
            
            # Infrastructure
            "ops": ops,
            "recycler": recycler,
            "prompt_refiner": prompt_refiner,
            
            # Documents
            "document_engine": document_engine,
        }
    
    def _log(self, message: str):
        """Log execution step."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {message}"
        self.execution_log.append(entry)
        print(entry)
    
    def execute(self, user_request: str, callback: Callable = None,
                auto_refine: bool = True, enable_critique: bool = True) -> Dict:
        """
        Main execution pipeline.
        
        Args:
            user_request: The user's natural language request
            callback: Progress callback function
            auto_refine: Auto-refine vague prompts
            enable_critique: Run devil's advocate on results
        """
        self.execution_log = []
        self._log(f"Received: {user_request[:100]}...")
        
        # Step 1: Auto-refine prompt if enabled
        if auto_refine:
            refined = prompt_refiner.refine(user_request)
            if refined["confidence"] > 0.6:
                self._log(f"Refined prompt (confidence: {refined['confidence']:.0%})")
                user_request = refined["refined_prompt"]
        
        # Step 2: Route the request
        self._log("Routing request...")
        routing = self._smart_route(user_request)
        
        if callback:
            callback(f"Routed to: {routing['category']} → {routing['primary_agent']}")
        
        self._log(f"Category: {routing['category']}, Agent: {routing['primary_agent']}")
        
        # Step 3: Execute based on category
        result = self._execute_by_category(
            routing, user_request, callback
        )
        
        # Step 4: Critique phase (if enabled and applicable)
        if enable_critique and routing["category"] in ["development", "business"]:
            self._log("Running critique phase...")
            critique = devils_advocate.critique(
                str(result)[:3000],
                content_type="code" if routing["category"] == "development" else "business"
            )
            
            if critique["should_block"]:
                self._log(f"⚠️ {critique['risk_summary'].get('critical', 0)} critical issues found")
                result = {
                    "result": result,
                    "critique": critique,
                    "needs_attention": True
                }
            else:
                self._log(f"✅ Critique passed ({critique['verdict']})")
        
        # Step 5: Security check for code
        if routing["category"] == "development" and isinstance(result, str):
            self._log("Running security scan...")
            security = security_auditor.quick_scan(result)
            self._log(security)
        
        self._log("Execution complete.")
        
        return {
            "routing": routing,
            "result": result,
            "execution_log": self.execution_log
        }
    
    def _smart_route(self, request: str) -> Dict:
        """Intelligent routing based on request content."""
        request_lower = request.lower()
        
        # Score each category
        scores = {}
        for category, info in self.AGENT_CATEGORIES.items():
            score = sum(1 for kw in info["keywords"] if kw in request_lower)
            scores[category] = score
        
        # Get best category
        best_category = max(scores, key=scores.get)
        
        # Special cases
        if "autonomous" in request_lower or "build me" in request_lower:
            return {
                "category": "autonomous",
                "primary_agent": "autonomous",
                "pipeline": ["research", "design", "code", "qa", "critique"]
            }
        
        if "pitch deck" in request_lower:
            return {
                "category": "business",
                "primary_agent": "pitch_deck",
                "pipeline": ["pitch_deck", "critique"]
            }
        
        if "briefing" in request_lower or "morning" in request_lower:
            return {
                "category": "productivity",
                "primary_agent": "daily_briefing",
                "pipeline": ["daily_briefing"]
            }
        
        if "email" in request_lower:
            return {
                "category": "productivity",
                "primary_agent": "email_agent",
                "pipeline": ["email_agent"]
            }
        
        if "calendar" in request_lower or "schedule" in request_lower:
            return {
                "category": "productivity",
                "primary_agent": "calendar_agent",
                "pipeline": ["calendar_agent"]
            }
        
        # Document generation
        if any(kw in request_lower for kw in ["word doc", "excel", "spreadsheet", "pdf report", "proposal", ".docx", ".xlsx", ".pdf"]):
            return {
                "category": "documents",
                "primary_agent": "document_engine",
                "pipeline": ["document_engine"]
            }
        
        if "blog" in request_lower or "write" in request_lower and "email" not in request_lower:
            return {
                "category": "business",
                "primary_agent": "content_writer",
                "pipeline": ["content_writer", "critique"]
            }
        
        if "swot" in request_lower or "competitor" in request_lower or "market" in request_lower:
            return {
                "category": "business",
                "primary_agent": "business_analyst",
                "pipeline": ["business_analyst"]
            }
        
        if "paper" in request_lower or "academic" in request_lower or "literature" in request_lower:
            return {
                "category": "research",
                "primary_agent": "academic_research",
                "pipeline": ["academic_research", "synthesis"]
            }
        
        if "research" in request_lower:
            return {
                "category": "research",
                "primary_agent": "brute_research",
                "pipeline": ["brute_research", "synthesis"]
            }
        
        if "git" in request_lower or "push" in request_lower or "commit" in request_lower:
            return {
                "category": "ops",
                "primary_agent": "git_agent",
                "pipeline": ["git_agent"]
            }
        
        # Default to development for build requests
        if scores.get("development", 0) > 0:
            return {
                "category": "development",
                "primary_agent": "coder",
                "pipeline": ["design", "code", "qa", "critique", "security"]
            }
        
        # Fallback to chat
        return {
            "category": "chat",
            "primary_agent": "chat",
            "pipeline": ["chat"]
        }
    
    def _execute_by_category(self, routing: Dict, request: str, 
                             callback: Callable = None) -> Any:
        """Execute based on routed category."""
        category = routing["category"]
        agent_name = routing["primary_agent"]
        
        def update(msg):
            self._log(msg)
            if callback:
                callback(msg)
        
        # === AUTONOMOUS ===
        if category == "autonomous":
            update("🚀 AUTONOMOUS MODE")
            return self.autonomous.run(request, progress_callback=callback)
        
        # === DEVELOPMENT ===
        if category == "development":
            update(f"💻 Development mode: {agent_name}")
            
            # Get creative direction first
            creativity = design_creativity.get_random_style()
            update(f"🎨 Style: {creativity.get('layout', 'default')}")
            
            # Generate code
            if agent_name == "coder":
                return coder.run(request)
            elif agent_name == "code_reviewer":
                return code_reviewer.run(request)
            
        # === RESEARCH ===
        if category == "research":
            update(f"🔬 Research mode: {agent_name}")
            
            if agent_name == "academic_research":
                return academic_research.search(request)
            elif agent_name == "brute_research":
                return deep_research_v2(request, progress_callback=update)
            else:
                return researcher.run(request)
        
        # === BUSINESS ===
        if category == "business":
            update(f"📊 Business mode: {agent_name}")
            
            if agent_name == "pitch_deck":
                # Extract company info from request
                result = pitch_deck.generate(
                    company_name="Company",  # Would be extracted
                    description=request,
                    industry="tech"
                )
                # Score it
                score = pitch_deck_scorer.score(result.get("slides", []))
                result["score"] = score
                return result
            
            elif agent_name == "content_writer":
                # Determine content type
                if "blog" in request.lower():
                    return content_writer.write_blog(request)
                elif "email" in request.lower():
                    return content_writer.write_email(request, request)
                elif "linkedin" in request.lower() or "twitter" in request.lower():
                    platform = "linkedin" if "linkedin" in request.lower() else "twitter"
                    return content_writer.write_social(platform, request)
                else:
                    return content_writer.write_blog(request)
            
            elif agent_name == "business_analyst":
                if "swot" in request.lower():
                    return business_analyst.swot_analysis("Company", request)
                elif "competitor" in request.lower():
                    return business_analyst.competitor_analysis("Company", "tech")
                else:
                    return business_analyst.full_analysis("Company", request, "tech")
        
        # === PRODUCTIVITY ===
        if category == "productivity":
            update(f"📅 Productivity mode: {agent_name}")
            
            if agent_name == "daily_briefing":
                return daily_briefing.generate()
            elif agent_name == "email_agent":
                return email_agent.summarize_inbox()
            elif agent_name == "calendar_agent":
                return calendar_agent.get_today_summary()
            elif agent_name == "slack_agent":
                return {"status": "Slack agent ready", "connected": slack_agent.is_connected()}
        
        # === OPS ===
        if category == "ops":
            update(f"⚙️ Ops mode: {agent_name}")
            
            if agent_name == "git_agent":
                return git_agent.run(request)
            elif agent_name == "terminal":
                return terminal.run(request)
            else:
                return ops.run(request)
        
        # === DOCUMENTS ===
        if category == "documents":
            update(f"📄 Document mode: {agent_name}")
            
            request_lower = request.lower()
            
            # Determine document type and generate
            if "excel" in request_lower or "spreadsheet" in request_lower:
                # Generate Excel
                return document_engine.create_excel(
                    filename="generated_spreadsheet",
                    sheets=[{
                        "name": "Sheet1",
                        "headers": ["Column A", "Column B", "Column C"],
                        "rows": [["Data will be populated by content"]],
                        "column_widths": [20, 20, 20]
                    }]
                )
            elif "proposal" in request_lower:
                return document_engine.create_business_proposal(
                    filename="proposal",
                    company="Your Company",
                    client="Client Name",
                    proposal={
                        "summary": "Generated proposal",
                        "problem": request,
                        "solution": "Solution description",
                        "deliverables": ["Deliverable 1", "Deliverable 2"],
                        "timeline": [["Phase 1", "2 weeks", "Initial setup"]],
                        "pricing": "Contact for pricing",
                        "next_steps": ["Schedule call", "Review proposal"]
                    }
                )
            elif "pdf" in request_lower:
                return document_engine.create_pdf(
                    filename="generated_document",
                    title="Generated Document",
                    content=[
                        {"type": "paragraph", "text": request}
                    ]
                )
            else:
                # Default to Word document
                return document_engine.create_word_doc(
                    filename="generated_document",
                    title="Generated Document",
                    sections=[
                        {"heading": "Content", "content": request}
                    ]
                )
        
        # === CHAT (fallback) ===
        update("💬 Chat mode")
        from .personality import get_chat_prompt, clean_response
        from .base_agent import BaseAgent
        
        class ChatAgent(BaseAgent):
            def __init__(self):
                super().__init__("router")
            
            def _get_system_prompt(self):
                return get_chat_prompt(False)["content"]
            
            def run(self, task):
                return clean_response(self.call_llm(task))
        
        return ChatAgent().run(request)
    
    # === Specialized Pipelines ===
    
    def run_full_build(self, request: str, callback: Callable = None) -> Dict:
        """
        Full build pipeline: Research → Design → Code → QA → Critique → Security
        """
        results = {}
        
        def update(msg):
            self._log(msg)
            if callback:
                callback(msg)
        
        # 1. Research
        update("🔍 Phase 1: Research")
        results["research"] = deep_research_v2(request, progress_callback=update)
        
        # 2. Design
        update("🎨 Phase 2: Design")
        results["design"] = design_creativity.get_random_style()
        
        # 3. Code
        update("💻 Phase 3: Code Generation")
        results["code"] = coder.run(request)
        
        # 4. QA
        update("✅ Phase 4: QA")
        results["qa"] = qa_agent.run_qa(results.get("code", ""))
        
        # 5. Critique
        update("🔍 Phase 5: Devil's Advocate")
        results["critique"] = devils_advocate.critique(
            str(results.get("code", ""))[:3000],
            content_type="code"
        )
        
        # 6. Security
        update("🔐 Phase 6: Security Audit")
        results["security"] = security_auditor.audit_code(
            str(results.get("code", ""))
        )
        
        update("🎉 Build complete!")
        return results
    
    def run_business_analysis(self, company: str, description: str, 
                              industry: str = "tech") -> Dict:
        """Full business analysis pipeline."""
        self._log(f"Running full business analysis for {company}")
        
        results = {
            "swot": business_analyst.swot_analysis(company, description),
            "competitors": business_analyst.competitor_analysis(company, industry),
            "market": business_analyst.market_sizing(description, industry),
        }
        
        # Critique the analysis
        results["critique"] = devils_advocate.critique(
            str(results)[:3000],
            content_type="business"
        )
        
        return results
    
    def run_content_campaign(self, topic: str, platforms: List[str] = None) -> Dict:
        """Generate content across multiple platforms."""
        platforms = platforms or ["blog", "twitter", "linkedin"]
        
        results = {}
        
        if "blog" in platforms:
            results["blog"] = content_writer.write_blog(topic)
        
        if "twitter" in platforms:
            results["twitter"] = content_writer.write_social("twitter", topic)
        
        if "linkedin" in platforms:
            results["linkedin"] = content_writer.write_social("linkedin", topic)
        
        if "email" in platforms:
            results["email"] = content_writer.write_email(
                f"Newsletter about {topic}",
                topic,
                email_type="newsletter"
            )
        
        return results
    
    def get_status(self) -> Dict:
        """Get orchestrator status and agent health."""
        return {
            "total_agents": 40,
            "categories": list(self.AGENT_CATEGORIES.keys()),
            "autonomous_state": self.autonomous.get_state(),
            "memory_stats": memory.get_stats(),
            "execution_log_size": len(self.execution_log)
        }


# Singleton
orchestrator = Orchestrator()
