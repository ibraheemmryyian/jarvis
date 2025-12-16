"""
Research Agent for Jarvis v2
Deep, multi-phase research with source aggregation and synthesis.
"""
import time
from duckduckgo_search import DDGS
from .base_agent import BaseAgent
from .context_manager import context


class ResearchAgent(BaseAgent):
    """Performs deep, autonomous research on topics."""
    
    def __init__(self):
        super().__init__("research")
    
    def _get_system_prompt(self) -> str:
        return """You are a Research Analyst. Your job is to synthesize information into actionable insights.

When given raw research data, you will:
1. Identify key trends and patterns
2. Extract actionable recommendations
3. Flag opportunities and risks
4. Provide a clear executive summary

Output format:
## Executive Summary
[2-3 sentences]

## Key Findings
- Finding 1
- Finding 2

## Recommendations
1. Recommendation 1
2. Recommendation 2

## Sources
- Source 1
- Source 2

Be concise. Focus on actionable intelligence."""

    def _search_web(self, query: str, max_results: int = 5) -> list:
        """Perform a web search."""
        try:
            results = list(DDGS().text(query, region='wt-wt', max_results=max_results))
            return results
        except Exception as e:
            return [{"title": "Search Error", "body": str(e), "href": ""}]
    
    def _search_academic(self, query: str) -> list:
        """Search for academic/arxiv papers."""
        try:
            results = list(DDGS().text(f"site:arxiv.org {query}", region='wt-wt', max_results=3))
            return results
        except Exception as e:
            return []
    
    def deep_research(self, topic: str, business_context: str = "") -> dict:
        """
        Multi-phase research pipeline.
        Returns structured data + synthesis.
        """
        phases = {}
        
        # Phase 1: Market Overview
        phases["market_overview"] = self._search_web(f"{topic} market size trends 2024")
        time.sleep(0.5)  # Rate limiting
        
        # Phase 2: Competitors
        phases["competitors"] = self._search_web(f"{topic} competitors alternatives")
        time.sleep(0.5)
        
        # Phase 3: Technical Feasibility
        phases["technical"] = self._search_web(f"{topic} how to build tutorial")
        time.sleep(0.5)
        
        # Phase 4: Monetization
        phases["monetization"] = self._search_web(f"{topic} pricing business model revenue")
        time.sleep(0.5)
        
        # Phase 5: Academic (if relevant)
        phases["academic"] = self._search_academic(topic)
        
        # Format raw data for LLM synthesis
        raw_data = self._format_raw_data(phases)
        
        # Synthesize with LLM
        synthesis_prompt = f"""Analyze this research data about: {topic}

Business Context: {business_context if business_context else 'General market research'}

RAW DATA:
{raw_data}

Synthesize into actionable insights. Focus on:
1. Market opportunity size
2. Key competitors and their weaknesses
3. Technical approach recommendation
4. Monetization strategy
5. Risks and challenges"""

        synthesis = self.call_llm(synthesis_prompt, include_context=False)
        
        # Save to context
        context.append("research_notes", f"## Research: {topic}\n\n{synthesis}")
        
        return {
            "topic": topic,
            "raw_phases": phases,
            "synthesis": synthesis
        }
    
    def _format_raw_data(self, phases: dict) -> str:
        """Format search results for LLM consumption."""
        output = ""
        for phase_name, results in phases.items():
            output += f"\n### {phase_name.upper()}\n"
            for r in results[:3]:  # Limit per phase
                title = r.get("title", "Untitled")
                body = r.get("body", "")[:300]  # Truncate
                output += f"- **{title}**: {body}\n"
        return output
    
    def run(self, task: str) -> str:
        """Execute research task."""
        result = self.deep_research(task)
        return result["synthesis"]


# Singleton
researcher = ResearchAgent()
