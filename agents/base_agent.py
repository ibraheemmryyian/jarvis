"""
Base Agent for Jarvis v2
Abstract class that all specialist agents inherit from.
"""
import requests
import json
import re
from abc import ABC, abstractmethod
from .config import LM_STUDIO_URL, AGENT_TEMPS, MAX_OUTPUT_TOKENS
from .context_manager import context


class BaseAgent(ABC):
    """Base class for all Jarvis agents."""
    
    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        self.temperature = AGENT_TEMPS.get(agent_type, 0.3)
        self.system_prompt = self._get_system_prompt()
    
    @abstractmethod
    def _get_system_prompt(self) -> str:
        """Each agent defines its own personality/instructions."""
        pass
    
    def _build_messages(self, user_input: str, include_context: bool = True) -> list:
        """Build the message array for LLM call."""
        messages = [{"role": "system", "content": self.system_prompt}]
        
        if include_context:
            ctx = context.read_for_agent(self.agent_type)
            if ctx.strip():
                messages.append({
                    "role": "system", 
                    "content": f"[CONTEXT FILES]\n{ctx}"
                })
        
        messages.append({"role": "user", "content": user_input})
        return messages
    
    def call_llm(self, user_input: str, include_context: bool = True, json_mode: bool = False) -> str:
        """Make a call to the local LLM server."""
        messages = self._build_messages(user_input, include_context)
        
        payload = {
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": MAX_OUTPUT_TOKENS,
        }
        
        # Some models support response_format for structured output
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        
        try:
            # 30 minute timeout for full autonomous operations
            response = requests.post(LM_STUDIO_URL, json=payload, timeout=1800)
            if response.status_code != 200:
                return f"[LLM Error: {response.status_code}]"
            
            content = response.json()["choices"][0]["message"]["content"]
            return content
        except requests.exceptions.ConnectionError:
            return "[Error: LM Studio not running. Start it and load a model.]"
        except Exception as e:
            return f"[LLM Exception: {e}]"
    
    def call_llm_json(self, user_input: str) -> dict:
        """Make LLM call expecting JSON output."""
        # Don't use json_mode - not all models support it
        response = self.call_llm(user_input)
        
        # Strip Qwen <think> tags if present (native thinking mode)
        if "<think>" in response:
            # Extract content after </think>
            parts = response.split("</think>")
            if len(parts) > 1:
                response = parts[-1].strip()
        
        # Clean response - remove reasoning text before/after JSON
        cleaned = response.strip()
        
        # Extract JSON from response
        try:
            # Try direct parse first
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Try to find JSON in markdown code block
            match = re.search(r'```(?:json)?\\s*([\\s\\S]*?)\\s*```', response)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    pass
            
            # Try to find raw JSON object (first occurrence)
            match = re.search(r'\\{[^{}]*(?:\\{[^{}]*\\}[^{}]*)*\\}', response)
            if match:
                try:
                    return json.loads(match.group(0))
                except json.JSONDecodeError:
                    pass
            
            # Last resort: find anything between first { and last }
            start = response.find('{')
            end = response.rfind('}')
            if start != -1 and end != -1 and end > start:
                try:
                    return json.loads(response[start:end+1])
                except json.JSONDecodeError:
                    pass
        
        return {"error": "Failed to parse JSON", "raw": response[:200]}
    
    @abstractmethod
    def run(self, task: str) -> str:
        """Execute the agent's main function."""
        pass
