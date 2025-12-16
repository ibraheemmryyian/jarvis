"""
Research Synthesis Engine for Jarvis v2
Takes raw research data and synthesizes into actionable report.
"""
import json
from datetime import datetime
from typing import Dict, List, Any
from .base_agent import BaseAgent
from .brute_research import brute_researcher
from .context_manager import context
from .config import CONTEXT_DIR
import os


class SynthesisEngine(BaseAgent):
    """
    Takes aggregated research and synthesizes into structured report.
    Uses LLM for intelligent summarization.
    """
    
    def __init__(self):
        super().__init__("research")  # Uses research agent temperature
    
    def _get_system_prompt(self) -> str:
        return """You are a Research Analyst creating an EXHAUSTIVE business viability report.

Your job is to synthesize raw research data into an actionable founder report.

OUTPUT FORMAT (use exactly this structure):
```
# 📊 EXHAUSTIVE RESEARCH REPORT: [TOPIC]

## Executive Summary
[2-3 paragraph summary of key findings and recommendation]

## Market Analysis
### Market Size
[Estimated market size with sources]

### Growth Trends
[Industry growth patterns]

### Key Players
[Top 5-10 competitors with brief descriptions]

## Competitor Deep Dive
| Competitor | Strengths | Weaknesses | Pricing |
|------------|-----------|------------|---------|
[Table of top competitors]

## User Sentiment
### Pain Points (from Reddit/Quora)
- [Bullet points of real user complaints]

### What Users Want
- [Features users are asking for]

## Technical Landscape
### Common Tech Stacks
[What competitors are built with]

### Build vs Buy
[Recommendations on what to build vs use existing]

## SEO Opportunity
### Keyword Gaps
[Underserved search terms]

### Content Strategy
[What content to create]

## GO/NO-GO RECOMMENDATION
**Verdict**: [GO / CAUTION / NO-GO]
**Confidence**: [0-100%]
**Reasoning**: [Why this recommendation]

### If GO, Next Steps:
1. [Action item]
2. [Action item]
3. [Action item]
```

Be thorough but actionable. A founder should be able to make a decision after reading this."""

    def synthesize(self, topic: str, raw_context: str) -> str:
        """Synthesize raw research into final report."""
        prompt = f"""Analyze this research data and create an EXHAUSTIVE RESEARCH REPORT for:

TOPIC: {topic}

RAW RESEARCH DATA:
{raw_context[:12000]}

Create the full report following the exact format specified. Be thorough and actionable."""

        return self.call_llm(prompt)
    
    def run(self, topic: str) -> Dict[str, Any]:
        """Full research pipeline: gather → aggregate → synthesize."""
        
        # Step 1: Brute force gather from all sources
        results = brute_researcher.gather(topic)
        
        # Step 2: Aggregate by category
        aggregated = brute_researcher.aggregate_by_category()
        
        # Step 3: Save raw data
        brute_researcher.save_raw(topic)
        
        # Step 4: Convert to context string
        raw_context = brute_researcher.to_context_string()
        
        # Step 5: Synthesize with LLM
        report = self.synthesize(topic, raw_context)
        
        # Step 6: Save final report
        report_path = os.path.join(CONTEXT_DIR, "research_report.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)
        
        # Step 7: Also save to research_notes for context
        context.append_context("research_notes", f"\n\n---\n# Research: {topic}\n{datetime.now().isoformat()}\n\n{report}")
        
        return {
            "topic": topic,
            "total_sources_searched": len(results),
            "categories": list(aggregated.keys()),
            "report": report,
            "report_path": report_path
        }


# Singleton
synthesizer = SynthesisEngine()


def deep_research_v2(topic: str, progress_callback=None) -> Dict[str, Any]:
    """
    The main entry point for brute force research.
    Returns exhaustive report.
    """
    brute_researcher.progress_callback = progress_callback
    return synthesizer.run(topic)
