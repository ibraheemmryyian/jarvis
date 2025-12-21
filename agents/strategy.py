"""
Strategy Agent for Jarvis
Specializes in business strategy, market analysis, competitive positioning.
"""
from .base_agent import BaseAgent


class StrategyAgent(BaseAgent):
    """Strategic advisor for business decisions and planning."""
    
    def __init__(self):
        super().__init__("strategy")
    
    def _get_system_prompt(self) -> str:
        return """You are a Senior Strategy Consultant.

EXPERTISE:
- Go-to-market strategy
- Competitive analysis
- Market sizing (TAM, SAM, SOM)
- Business model design
- Growth strategy
- Pricing strategy
- Partnership opportunities

FRAMEWORKS:
- Porter's Five Forces
- SWOT Analysis
- Blue Ocean Strategy
- Jobs to be Done
- Value Proposition Canvas
- OKRs and KPIs

OUTPUT STYLE:
- Executive summary first
- Data-driven insights
- Clear recommendations with rationale
- Risk assessment
- Action items with priorities
- Timeline/roadmap when applicable

Be direct, avoid fluff. Focus on actionable insights."""
    
    def analyze_market(self, industry: str, focus: str = None) -> str:
        """Analyze market opportunity."""
        prompt = f"""Provide strategic market analysis for:

INDUSTRY: {industry}
FOCUS: {focus or 'general opportunity'}

Include:
- Market size (TAM/SAM/SOM)
- Key trends
- Major players
- Entry barriers
- Growth vectors
- Recommended positioning

Be specific with data where possible."""
        return self._call_llm(prompt)
    
    def competitive_analysis(self, company: str, competitors: list) -> str:
        """Analyze competitive landscape."""
        prompt = f"""Competitive analysis for: {company}

COMPETITORS: {', '.join(competitors)}

Analyze:
- Feature comparison matrix
- Pricing comparison
- Target market overlap
- Unique differentiators
- Threats and opportunities
- Strategic recommendations

Output structured analysis."""
        return self._call_llm(prompt)
    
    def gtm_strategy(self, product: str, target_market: str) -> str:
        """Create go-to-market strategy."""
        prompt = f"""Create GTM strategy for:

PRODUCT: {product}
TARGET MARKET: {target_market}

Include:
- Value proposition
- Customer segments
- Channel strategy
- Pricing model
- Launch phases
- Success metrics
- 90-day action plan"""
        return self._call_llm(prompt)
    
    def run(self, task: str) -> str:
        """Execute strategy task."""
        task_lower = task.lower()
        if "market" in task_lower and "analy" in task_lower:
            return self.analyze_market(task)
        elif "competit" in task_lower:
            return self.competitive_analysis(task, [])
        elif "gtm" in task_lower or "go-to-market" in task_lower:
            return self.gtm_strategy(task, "")
        else:
            return self._call_llm(f"Strategic task: {task}")


# Singleton
strategy = StrategyAgent()
