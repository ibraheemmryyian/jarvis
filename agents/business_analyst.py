"""
Business Analyst Agent for Jarvis v2
Competitive analysis, market sizing, financial projections, and strategic frameworks.
"""
import os
import re
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional
from .config import WORKSPACE_DIR, LM_STUDIO_URL


class BusinessAnalyst:
    """
    Business analysis and strategy assistant.
    
    Features:
    - Competitor analysis
    - Market sizing (TAM/SAM/SOM)
    - SWOT analysis
    - Business Model Canvas
    - Financial projections
    - Industry benchmarks
    - Porter's Five Forces
    """
    
    def __init__(self):
        self.results_dir = os.path.join(WORKSPACE_DIR, "business")
        os.makedirs(self.results_dir, exist_ok=True)
    
    def competitor_analysis(self, company: str, industry: str, competitors: List[str] = None) -> Dict:
        """
        Perform comprehensive competitor analysis.
        
        Args:
            company: Your company/product name
            industry: Industry sector
            competitors: Optional list of known competitors
            
        Returns:
            Dict with competitive landscape analysis
        """
        print(f"[Business] Analyzing competitors for {company} in {industry}")
        
        prompt = f"""Perform a comprehensive competitor analysis for:

COMPANY: {company}
INDUSTRY: {industry}
KNOWN COMPETITORS: {', '.join(competitors) if competitors else 'Find the top 5 competitors'}

Provide analysis in JSON format:
{{
    "top_competitors": [
        {{
            "name": "Competitor name",
            "description": "Brief description",
            "strengths": ["list of strengths"],
            "weaknesses": ["list of weaknesses"],
            "pricing_model": "How they charge",
            "target_market": "Who they serve",
            "estimated_market_share": "X%",
            "key_differentiator": "What makes them unique"
        }}
    ],
    "competitive_landscape": {{
        "market_leaders": ["names"],
        "emerging_players": ["names"],
        "market_consolidation": "high/medium/low",
        "entry_barriers": ["list"]
    }},
    "your_positioning": {{
        "unique_advantages": ["what you could do better"],
        "threats": ["what competitors do better"],
        "opportunities": ["gaps in the market"],
        "recommended_strategy": "Brief strategic recommendation"
    }}
}}

Be specific with real companies where possible. Output only JSON."""
        
        result = self._call_llm(prompt)
        
        # Save to file
        self._save_analysis("competitor", company, result)
        
        return result
    
    def market_sizing(self, product: str, target_market: str, geography: str = "Global") -> Dict:
        """
        Calculate TAM, SAM, SOM for a product/service.
        
        Args:
            product: Product or service description
            target_market: Target customer segment
            geography: Geographic scope
            
        Returns:
            Dict with market sizing calculations
        """
        print(f"[Business] Calculating market size for {product}")
        
        prompt = f"""Calculate market sizing (TAM/SAM/SOM) for:

PRODUCT/SERVICE: {product}
TARGET MARKET: {target_market}
GEOGRAPHY: {geography}

Provide analysis in JSON format:
{{
    "tam": {{
        "value_usd": "Total Addressable Market in USD (e.g., '$50B')",
        "description": "How this was calculated",
        "growth_rate": "Annual growth rate %",
        "data_sources": ["Assumed data sources"]
    }},
    "sam": {{
        "value_usd": "Serviceable Addressable Market in USD",
        "description": "Segment of TAM you can realistically serve",
        "percentage_of_tam": "X%",
        "key_constraints": ["What limits your SAM"]
    }},
    "som": {{
        "value_usd": "Serviceable Obtainable Market in USD",
        "description": "Realistic market share in 3-5 years",
        "percentage_of_sam": "X%",
        "assumptions": ["Key assumptions for this estimate"]
    }},
    "market_dynamics": {{
        "key_trends": ["Major industry trends"],
        "disruption_risks": ["Potential disruptors"],
        "regulatory_factors": ["Relevant regulations"],
        "timing": "Why now is the right time"
    }},
    "bottom_up_validation": {{
        "potential_customers": "Estimated number",
        "average_deal_size": "$X",
        "calculated_som": "Customers × Deal Size"
    }}
}}

Use realistic numbers based on industry knowledge. Output only JSON."""
        
        result = self._call_llm(prompt)
        self._save_analysis("market_size", product, result)
        
        return result
    
    def swot_analysis(self, company: str, context: str = "") -> Dict:
        """
        Generate SWOT analysis.
        
        Args:
            company: Company or product name
            context: Additional context about the business
            
        Returns:
            Dict with SWOT matrix
        """
        print(f"[Business] SWOT analysis for {company}")
        
        prompt = f"""Create a comprehensive SWOT analysis for:

COMPANY/PRODUCT: {company}
CONTEXT: {context if context else 'General startup analysis'}

Provide analysis in JSON format:
{{
    "strengths": [
        {{"item": "Strength description", "impact": "high/medium/low", "leverage_strategy": "How to capitalize"}}
    ],
    "weaknesses": [
        {{"item": "Weakness description", "impact": "high/medium/low", "mitigation_strategy": "How to address"}}
    ],
    "opportunities": [
        {{"item": "Opportunity description", "timeframe": "short/medium/long term", "action_required": "What to do"}}
    ],
    "threats": [
        {{"item": "Threat description", "probability": "high/medium/low", "contingency_plan": "How to prepare"}}
    ],
    "strategic_recommendations": [
        "Top 3 actionable recommendations based on this analysis"
    ]
}}

Provide 4-6 items per category. Output only JSON."""
        
        result = self._call_llm(prompt)
        self._save_analysis("swot", company, result)
        
        return result
    
    def business_model_canvas(self, company: str, description: str) -> Dict:
        """
        Generate Business Model Canvas.
        
        Args:
            company: Company name
            description: Business description
            
        Returns:
            Dict with all 9 BMC sections
        """
        print(f"[Business] Business Model Canvas for {company}")
        
        prompt = f"""Create a Business Model Canvas for:

COMPANY: {company}
DESCRIPTION: {description}

Provide the canvas in JSON format:
{{
    "customer_segments": {{
        "primary": ["Main customer segments"],
        "secondary": ["Secondary segments"],
        "characteristics": ["Key characteristics of ideal customers"]
    }},
    "value_propositions": {{
        "core_value": "The main value you provide",
        "features": ["Key features"],
        "pain_relievers": ["Problems you solve"],
        "gain_creators": ["Benefits you provide"]
    }},
    "channels": {{
        "awareness": ["How customers find you"],
        "evaluation": ["How customers evaluate you"],
        "purchase": ["How customers buy"],
        "delivery": ["How you deliver value"],
        "after_sales": ["Post-purchase support"]
    }},
    "customer_relationships": {{
        "type": "self-serve/personal/automated/community",
        "acquisition": "How you acquire customers",
        "retention": "How you keep customers",
        "growth": "How you grow customer value"
    }},
    "revenue_streams": {{
        "primary": ["Main revenue sources"],
        "pricing_model": "subscription/transaction/freemium/etc",
        "pricing_strategy": "premium/competitive/penetration"
    }},
    "key_resources": {{
        "physical": ["Physical assets"],
        "intellectual": ["IP, patents, data"],
        "human": ["Key team/skills"],
        "financial": ["Capital requirements"]
    }},
    "key_activities": {{
        "production": ["Building activities"],
        "problem_solving": ["Service activities"],
        "platform": ["Platform/network activities"]
    }},
    "key_partnerships": {{
        "strategic_alliances": ["Non-competitor partners"],
        "suppliers": ["Key suppliers"],
        "joint_ventures": ["Potential JVs"]
    }},
    "cost_structure": {{
        "fixed_costs": ["Ongoing fixed costs"],
        "variable_costs": ["Costs that scale"],
        "economies_of_scale": ["Scale advantages"],
        "cost_drivers": ["Main cost drivers"]
    }}
}}

Be specific and actionable. Output only JSON."""
        
        result = self._call_llm(prompt)
        self._save_analysis("bmc", company, result)
        
        return result
    
    def financial_projections(self, company: str, model_type: str = "SaaS", 
                             initial_mrr: float = 0, growth_rate: float = 0.15,
                             years: int = 5) -> Dict:
        """
        Generate financial projections.
        
        Args:
            company: Company name
            model_type: Business model (SaaS, Marketplace, E-commerce)
            initial_mrr: Starting MRR in USD
            growth_rate: Monthly growth rate (0.15 = 15%)
            years: Number of years to project
            
        Returns:
            Dict with financial projections
        """
        print(f"[Business] Financial projections for {company}")
        
        prompt = f"""Create realistic financial projections for:

COMPANY: {company}
BUSINESS MODEL: {model_type}
INITIAL MRR: ${initial_mrr if initial_mrr > 0 else 'Estimate a reasonable starting point'}
MONTHLY GROWTH RATE: {growth_rate * 100}%
PROJECTION PERIOD: {years} years

Provide projections in JSON format:
{{
    "assumptions": {{
        "starting_mrr": "$X",
        "growth_rate_year1": "X%",
        "growth_rate_year2_3": "X%",
        "growth_rate_year4_5": "X%",
        "churn_rate": "X%",
        "gross_margin": "X%",
        "cac_payback_months": X,
        "ltv_cac_ratio": X
    }},
    "yearly_projections": [
        {{
            "year": 1,
            "arr": "$X",
            "mrr_end": "$X",
            "customers": X,
            "revenue": "$X",
            "gross_profit": "$X",
            "operating_expenses": "$X",
            "ebitda": "$X",
            "burn_rate": "$X/month",
            "runway_months": X
        }}
    ],
    "key_metrics": {{
        "break_even_month": X,
        "arr_at_year_5": "$X",
        "cumulative_revenue": "$X",
        "total_funding_needed": "$X"
    }},
    "sensitivity_analysis": {{
        "optimistic_scenario": {{"arr_year_5": "$X", "assumptions": "What changes"}},
        "pessimistic_scenario": {{"arr_year_5": "$X", "assumptions": "What changes"}}
    }},
    "benchmarks": {{
        "industry_median_growth": "X%",
        "top_quartile_growth": "X%",
        "your_positioning": "Below/At/Above median"
    }}
}}

Use realistic {model_type} benchmarks. Output only JSON."""
        
        result = self._call_llm(prompt)
        self._save_analysis("financials", company, result)
        
        return result
    
    def porters_five_forces(self, industry: str) -> Dict:
        """
        Analyze industry using Porter's Five Forces.
        
        Args:
            industry: Industry to analyze
            
        Returns:
            Dict with five forces analysis
        """
        print(f"[Business] Porter's Five Forces for {industry}")
        
        prompt = f"""Analyze the {industry} industry using Porter's Five Forces:

Provide analysis in JSON format:
{{
    "competitive_rivalry": {{
        "intensity": "high/medium/low",
        "factors": ["Key factors driving rivalry"],
        "key_players": ["Major competitors"],
        "impact": "How this affects profitability"
    }},
    "threat_of_new_entrants": {{
        "threat_level": "high/medium/low",
        "entry_barriers": ["Barriers to entry"],
        "capital_requirements": "high/medium/low",
        "impact": "How this affects existing players"
    }},
    "bargaining_power_suppliers": {{
        "power_level": "high/medium/low",
        "key_suppliers": ["Types of suppliers"],
        "switching_costs": "high/medium/low",
        "impact": "How this affects margins"
    }},
    "bargaining_power_buyers": {{
        "power_level": "high/medium/low",
        "buyer_concentration": "high/medium/low",
        "price_sensitivity": "high/medium/low",
        "impact": "How this affects pricing power"
    }},
    "threat_of_substitutes": {{
        "threat_level": "high/medium/low",
        "substitute_products": ["Alternative solutions"],
        "switching_costs": "high/medium/low",
        "impact": "How this limits growth"
    }},
    "overall_assessment": {{
        "industry_attractiveness": "high/medium/low",
        "profit_potential": "above/at/below average",
        "strategic_recommendations": ["How to position given these forces"]
    }}
}}

Be specific to the {industry} industry. Output only JSON."""
        
        result = self._call_llm(prompt)
        self._save_analysis("five_forces", industry, result)
        
        return result
    
    def full_analysis(self, company: str, description: str, industry: str) -> Dict:
        """
        Run complete business analysis suite.
        
        Args:
            company: Company name
            description: Business description
            industry: Industry sector
            
        Returns:
            Dict with all analyses combined
        """
        print(f"[Business] Running full analysis for {company}")
        
        results = {
            "company": company,
            "timestamp": datetime.now().isoformat(),
            "analyses": {}
        }
        
        # Run all analyses
        print("  → SWOT Analysis")
        results["analyses"]["swot"] = self.swot_analysis(company, description)
        
        print("  → Business Model Canvas")
        results["analyses"]["bmc"] = self.business_model_canvas(company, description)
        
        print("  → Competitor Analysis")
        results["analyses"]["competitors"] = self.competitor_analysis(company, industry)
        
        print("  → Market Sizing")
        results["analyses"]["market_size"] = self.market_sizing(description, industry)
        
        print("  → Porter's Five Forces")
        results["analyses"]["five_forces"] = self.porters_five_forces(industry)
        
        print("  → Financial Projections")
        results["analyses"]["financials"] = self.financial_projections(company)
        
        # Generate executive summary
        results["executive_summary"] = self._generate_executive_summary(results)
        
        # Save complete analysis
        self._save_full_report(company, results)
        
        return results
    
    def _generate_executive_summary(self, results: Dict) -> str:
        """Generate executive summary from all analyses."""
        
        prompt = f"""Based on this business analysis data, write a concise executive summary (200-300 words):

{json.dumps(results['analyses'], indent=2)[:5000]}

The summary should:
1. State the key opportunity
2. Highlight main strengths and risks
3. Provide 3 strategic recommendations
4. Give an overall assessment

Write in professional business language."""
        
        try:
            response = requests.post(
                LM_STUDIO_URL,
                json={
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 600
                },
                timeout=90
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
                
        except Exception as e:
            return f"Error generating summary: {e}"
        
        return "Summary generation failed."
    
    def _call_llm(self, prompt: str) -> Dict:
        """Call LLM and parse JSON response."""
        try:
            response = requests.post(
                LM_STUDIO_URL,
                json={
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 2500
                },
                timeout=120
            )
            
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                
                # Parse JSON from response
                json_match = re.search(r'\{[\s\S]*\}', content)
                if json_match:
                    return json.loads(json_match.group())
                else:
                    return {"raw_response": content}
                    
        except json.JSONDecodeError as e:
            return {"error": f"JSON parse error: {e}", "raw": content[:500]}
        except Exception as e:
            return {"error": str(e)}
        
        return {"error": "LLM call failed"}
    
    def _save_analysis(self, analysis_type: str, subject: str, data: Dict):
        """Save analysis to file."""
        safe_name = re.sub(r'[^a-zA-Z0-9]', '_', subject)[:30]
        filename = f"{analysis_type}_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.results_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print(f"[Business] Saved: {filename}")
    
    def _save_full_report(self, company: str, results: Dict):
        """Save full business report as Markdown."""
        safe_name = re.sub(r'[^a-zA-Z0-9]', '_', company)[:30]
        filename = f"full_report_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = os.path.join(self.results_dir, filename)
        
        content = f"""# Business Analysis Report: {company}

Generated: {results['timestamp']}

---

## Executive Summary

{results.get('executive_summary', 'N/A')}

---

## SWOT Analysis

{json.dumps(results['analyses'].get('swot', {}), indent=2)}

---

## Business Model Canvas

{json.dumps(results['analyses'].get('bmc', {}), indent=2)}

---

## Competitive Landscape

{json.dumps(results['analyses'].get('competitors', {}), indent=2)}

---

## Market Sizing

{json.dumps(results['analyses'].get('market_size', {}), indent=2)}

---

## Porter's Five Forces

{json.dumps(results['analyses'].get('five_forces', {}), indent=2)}

---

## Financial Projections

{json.dumps(results['analyses'].get('financials', {}), indent=2)}

"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"[Business] Full report saved: {filepath}")
        results["report_path"] = filepath


# Singleton instance
business_analyst = BusinessAnalyst()
