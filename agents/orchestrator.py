"""
Orchestrator for Jarvis v2
Coordinates all agents to execute complex, multi-step tasks.
"""
import time
from datetime import datetime
from .router import router
from .research import researcher
from .coder import coder
from .ops import ops
from .context_manager import context
from .synthesis import deep_research_v2


class Orchestrator:
    """
    The brain that coordinates all agents.
    Handles research-first workflows and multi-step execution.
    """
    
    def __init__(self):
        self.agents = {
            "RESEARCH": researcher,
            "CODER": coder,
            "OPS": ops,
        }
        self.execution_log = []
    
    def _log(self, message: str):
        """Log execution step."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {message}"
        self.execution_log.append(entry)
        print(entry)  # Console output for monitoring
    
    def execute(self, user_request: str, callback=None) -> dict:
        """
        Main execution pipeline.
        
        Args:
            user_request: The user's natural language request
            callback: Optional function to call with progress updates
        
        Returns:
            dict with execution results
        """
        self.execution_log = []
        self._log(f"Received: {user_request[:100]}...")
        
        # Step 1: Route the request
        self._log("Routing request...")
        routing = router.run(user_request)
        
        if callback:
            callback(f"Routed to: {routing['agent']}")
        
        self._log(f"Agent: {routing['agent']}, Complexity: {routing['estimated_complexity']}")
        
        # Step 2: Research first if needed
        if routing.get("requires_research_first", False):
            self._log("Research phase required...")
            if callback:
                callback("Starting research phase...")
            
            research_result = researcher.deep_research(
                user_request,
                business_context="User wants to build a product/tool"
            )
            
            self._log("Research complete. Updating context.")
            # Research results are automatically saved to context by the agent
        
        # Step 3: Execute with appropriate agent
        agent_name = routing["agent"]
        
        if agent_name == "CHAT":
            # Simple chat response with JARVIS personality
            self._log("Chat mode - activating personality...")
            from .personality import get_chat_prompt, clean_response
            from .base_agent import BaseAgent
            
            class ChatAgent(BaseAgent):
                def __init__(self, voice_mode=False):
                    self.voice_mode = voice_mode
                    super().__init__("router")
                
                def _get_system_prompt(self):
                    return get_chat_prompt(self.voice_mode)["content"]
                
                def run(self, task):
                    response = self.call_llm(task)
                    # Always clean the response
                    response = clean_response(response)
                    if self.voice_mode:
                        from .personality import format_for_voice
                        response = format_for_voice(response)
                    return response
            
            chat = ChatAgent(voice_mode=False)
            result = chat.run(user_request)
        
        elif agent_name in self.agents:
            self._log(f"Executing with {agent_name} agent...")
            if callback:
                callback(f"Executing with {agent_name}...")
            
            agent = self.agents[agent_name]
            result = agent.run(user_request)
        
        elif agent_name == "AUTONOMOUS":
            # Full autonomous pipeline - triggered by natural language
            self._log("AUTONOMOUS mode detected from speech. Running full pipeline...")
            if callback:
                callback("🚀 AUTONOMOUS MODE: Research → Build → Deploy")
            
            autonomous_result = self.execute_autonomous(user_request, progress_callback=callback)
            result = autonomous_result.get("research", {}).get("synthesis", "Autonomous run complete. Check workspace.")
        
        else:
            result = f"Unknown agent: {agent_name}"
        
        # Step 4: Clean the response (remove <think> tags, artifacts)
        from .personality import clean_response
        if isinstance(result, str):
            result = clean_response(result)
        
        # Step 5: Update task status
        context.mark_task_complete(f"Completed with {agent_name} agent")
        
        self._log("Execution complete.")
        
        return {
            "routing": routing,
            "result": result,
            "execution_log": self.execution_log
        }
    
    def execute_autonomous(self, business_idea: str, progress_callback=None) -> dict:
        """
        Full autonomous execution: Research → Build → Deploy.
        This is the "come back in 2 hours" mode.
        
        Args:
            business_idea: High-level business/product idea
            progress_callback: Function to call with status updates
        """
        results = {
            "research": None,
            "code": None,
            "deployment": None,
            "errors": []
        }
        
        def update(msg):
            if progress_callback:
                progress_callback(msg)
            self._log(msg)
        
        # Phase 1: BRUTE FORCE Deep Research
        update("🔍 Phase 1/3: BRUTE FORCE Research (20+ sources)...")
        try:
            results["research"] = deep_research_v2(
                business_idea,
                progress_callback=update
            )
            update("✅ Research complete.")
        except Exception as e:
            results["errors"].append(f"Research failed: {e}")
            update(f"❌ Research error: {e}")
        
        # Phase 2: Code Generation
        update("💻 Phase 2/3: Code Generation...")
        try:
            # Build code generation prompt using research
            research_summary = results.get("research", {}).get("synthesis", "")
            code_prompt = f"""Based on this research:
{research_summary[:2000]}

Create a complete, deployable web application for: {business_idea}

Requirements:
- Use React + Vite
- Modern, professional UI
- Include placeholder for ads
- Add a simple paywall/premium feature section
"""
            results["code"] = coder.run(code_prompt)
            update("✅ Code generated.")
        except Exception as e:
            results["errors"].append(f"Code generation failed: {e}")
            update(f"❌ Code error: {e}")
        
        # Phase 3: Deployment Planning
        update("🚀 Phase 3/3: Deployment Planning...")
        try:
            results["deployment"] = ops.run(
                "Recommend deployment for a React web app with Vite"
            )
            update("✅ Deployment plan ready.")
        except Exception as e:
            results["errors"].append(f"Deployment planning failed: {e}")
            update(f"❌ Deployment error: {e}")
        
        # Summary
        update("🎉 Autonomous execution complete!")
        
        return results


# Singleton
orchestrator = Orchestrator()
