"""
Orchestrator v3 for Jarvis
Full 54-agent coordination with intelligent routing, context segregation, and critique phases.

Routes to 9 categories:
- FRONTEND: frontend_dev, uiux, seo
- BACKEND: backend_dev, coder, ai_ops, ai_infra
- ARCHITECTURE: architect, product_manager, strategy, business_analyst
- RESEARCH: researcher, brute_research, academic_research, academic_workflow
- QA: qa_agent, code_reviewer, security_auditor, visual_qa, devils_advocate
- OPS: ops, git_agent, github_agent, terminal
- CONTENT: content_writer, pitch_deck, document_engine, seo_specialist
- PRODUCTIVITY: email_agent, calendar_agent, slack_agent, daily_briefing
- CORE: router, autonomous, recycler, memory
"""
import time
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any

# Core routing and context
from .router import router
from .context_manager import context
from .registry import registry, AGENT_CATEGORIES, get_context_for_agent, save_context

# === FRONTEND ===
from .frontend_dev import frontend_dev
from .uiux import uiux
from .seo import seo_specialist

# === BACKEND ===
from .backend_dev import backend_dev
from .coder import coder
from .ai_ops import ai_ops
from .ai_infra import ai_infra

# === ARCHITECTURE ===
from .architect import architect
from .product_manager import product_manager
from .strategy import strategy
from .business_analyst import business_analyst

# === RESEARCH ===
from .research import researcher
from .brute_research import brute_researcher
from .academic_research import academic_research
from .synthesis import deep_research_v2
from .academic_workflow import academic_workflow
from .research_publisher import research_publisher

# === QA ===
from .qa import qa_agent
from .code_reviewer import code_reviewer
from .security_auditor import security_auditor
from .visual_qa import visual_qa
from .devils_advocate import devils_advocate

# === OPS ===
from .ops import ops
from .git_agent import git_agent
from .terminal import terminal

# === CONTENT ===
from .content_writer import content_writer
from .pitch_deck import pitch_deck, pitch_deck_scorer
from .document_engine import document_engine

# === PRODUCTIVITY ===
from .email_agent import email_agent
from .calendar_agent import calendar_agent
from .slack_agent import slack_agent
from .daily_briefing import daily_briefing

# === CORE ===
from .autonomous import AutonomousExecutor
from .recycler import recycler
from .memory import memory
from .prompt_refiner import prompt_refiner
from .project_manager import project_manager
from .design_creativity import design_creativity
from .code_indexer import code_indexer


class Orchestrator:
    """
    The master brain that coordinates all 54 agents.
    Uses registry.py for categories and context routing.
    
    Features:
    - Intelligent routing via registry categories
    - Auto-prompt refinement
    - Critique phases (devil's advocate, security)
    - Multi-step pipelines with context segregation
    - Progress tracking
    """
    
    def __init__(self):
        self.execution_log = []
        self.autonomous = AutonomousExecutor()
        
        # Direct agent references - ALL 42 AGENTS
        self.agents = {
            # === FRONTEND (3) ===
            "frontend_dev": frontend_dev,
            "uiux": uiux,
            "seo": seo_specialist,
            
            # === BACKEND (4) ===
            "backend_dev": backend_dev,
            "coder": coder,
            "ai_ops": ai_ops,
            "ai_infra": ai_infra,
            
            # === ARCHITECTURE (4) ===
            "architect": architect,
            "product_manager": product_manager,
            "project_manager": project_manager,
            "strategy": strategy,
            "business_analyst": business_analyst,
            
            # === RESEARCH (6) ===
            "researcher": researcher,
            "brute_research": brute_researcher,
            "academic_research": academic_research,
            "deep_research": deep_research_v2,
            "academic_workflow": academic_workflow,
            "research_publisher": research_publisher,
            
            # === QA (5) ===
            "code_reviewer": code_reviewer,
            "qa": qa_agent,
            "devils_advocate": devils_advocate,
            "security_auditor": security_auditor,
            "visual_qa": visual_qa,
            
            # === OPS (4) ===
            "ops": ops,
            "git_agent": git_agent,
            "terminal": terminal,
            "code_indexer": code_indexer,
            
            # === CONTENT (4) ===
            "content_writer": content_writer,
            "pitch_deck": pitch_deck,
            "document_engine": document_engine,
            "design_creativity": design_creativity,
            
            # === PRODUCTIVITY (4) ===
            "email_agent": email_agent,
            "calendar_agent": calendar_agent,
            "slack_agent": slack_agent,
            "daily_briefing": daily_briefing,
            
            # === CORE (6) ===
            "router": router,
            "recycler": recycler,
            "memory": memory,
            "prompt_refiner": prompt_refiner,
            "autonomous": self.autonomous,
        }
        
        # Multi-agent discussion mode
        self.team_mode = False
        self.discussion_log = []
    
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
