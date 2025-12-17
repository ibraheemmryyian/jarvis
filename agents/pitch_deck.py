"""
Pitch Deck Generator for Jarvis v2
Creates investor-ready pitch decks with minimal text, visual appeal, and proper structure.
"""
import os
import re
import json
from datetime import datetime
from typing import Dict, List, Optional
from .config import WORKSPACE_DIR, LM_STUDIO_URL
import requests


class PitchDeckGenerator:
    """
    Generates investor-ready pitch decks.
    
    Features:
    - 10-12 slide structure (investor standard)
    - Word count enforcement (max 6 words per bullet)
    - reveal.js HTML output
    - Multiple templates (SaaS, DeepTech, Consumer)
    - Visual QA integration
    """
    
    # Standard pitch deck structure
    SLIDE_STRUCTURE = [
        {"id": "cover", "title": "Cover", "purpose": "Company name, tagline, logo"},
        {"id": "problem", "title": "Problem", "purpose": "The pain point you solve"},
        {"id": "solution", "title": "Solution", "purpose": "Your product/service"},
        {"id": "market", "title": "Market Size", "purpose": "TAM, SAM, SOM"},
        {"id": "product", "title": "Product", "purpose": "How it works, screenshots"},
        {"id": "business_model", "title": "Business Model", "purpose": "How you make money"},
        {"id": "traction", "title": "Traction", "purpose": "Key metrics, growth"},
        {"id": "competition", "title": "Competition", "purpose": "Competitive landscape"},
        {"id": "team", "title": "Team", "purpose": "Founders and key hires"},
        {"id": "financials", "title": "Financials", "purpose": "Revenue projections"},
        {"id": "ask", "title": "The Ask", "purpose": "Funding amount, use of funds"},
        {"id": "contact", "title": "Contact", "purpose": "Contact info, next steps"}
    ]
    
    # Color themes
    THEMES = {
        "tech": {
            "primary": "#6366f1",      # Indigo
            "secondary": "#8b5cf6",    # Purple
            "accent": "#22d3ee",       # Cyan
            "background": "#0f172a",   # Dark slate
            "text": "#f8fafc"          # Light
        },
        "saas": {
            "primary": "#3b82f6",      # Blue
            "secondary": "#06b6d4",    # Cyan
            "accent": "#10b981",       # Emerald
            "background": "#1e293b",   # Slate
            "text": "#f1f5f9"
        },
        "fintech": {
            "primary": "#14b8a6",      # Teal
            "secondary": "#0ea5e9",    # Sky
            "accent": "#f59e0b",       # Amber
            "background": "#0c1222",   # Dark
            "text": "#e2e8f0"
        },
        "sustainability": {
            "primary": "#22c55e",      # Green
            "secondary": "#84cc16",    # Lime
            "accent": "#06b6d4",       # Cyan
            "background": "#052e16",   # Dark green
            "text": "#f0fdf4"
        },
        "healthcare": {
            "primary": "#0891b2",      # Cyan
            "secondary": "#6366f1",    # Indigo
            "accent": "#ec4899",       # Pink
            "background": "#0f172a",   # Dark
            "text": "#f8fafc"
        }
    }
    
    def __init__(self):
        self.decks_dir = os.path.join(WORKSPACE_DIR, "pitch_decks")
        os.makedirs(self.decks_dir, exist_ok=True)
    
    def generate(self, company: str, description: str, 
                 industry: str = "tech",
                 additional_info: Dict = None) -> Dict:
        """
        Generate a complete pitch deck.
        
        Args:
            company: Company name
            description: Business description
            industry: Industry for theme selection
            additional_info: Optional dict with traction, team, financials
            
        Returns:
            Dict with deck content and file paths
        """
        print(f"[PitchDeck] Generating deck for {company}")
        
        # Select theme
        theme = self.THEMES.get(industry, self.THEMES["tech"])
        
        # Generate content for each slide
        slides = self._generate_slide_content(company, description, additional_info)
        
        # Generate HTML
        html_content = self._generate_reveal_html(company, slides, theme)
        
        # Save files
        safe_name = re.sub(r'[^a-zA-Z0-9]', '_', company)[:30]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        deck_dir = os.path.join(self.decks_dir, f"{safe_name}_{timestamp}")
        os.makedirs(deck_dir, exist_ok=True)
        
        html_path = os.path.join(deck_dir, "index.html")
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Save slide content as JSON
        json_path = os.path.join(deck_dir, "slides.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(slides, f, indent=2)
        
        print(f"[PitchDeck] Saved to: {deck_dir}")
        
        return {
            "company": company,
            "deck_path": deck_dir,
            "html_file": html_path,
            "slides": slides,
            "theme": industry,
            "slide_count": len(slides)
        }
    
    def _generate_slide_content(self, company: str, description: str, 
                                additional_info: Dict = None) -> List[Dict]:
        """Generate content for each slide using LLM."""
        
        info = additional_info or {}
        
        prompt = f"""Create pitch deck content for an investor presentation.

COMPANY: {company}
DESCRIPTION: {description}

ADDITIONAL INFO:
- Traction: {info.get('traction', 'Early stage, building MVP')}
- Team: {info.get('team', 'Founding team')}
- Funding Ask: {info.get('ask', '$500K pre-seed')}
- Revenue: {info.get('revenue', 'Pre-revenue')}

Generate content for each slide. CRITICAL RULES:
1. MAX 6 words per bullet point
2. MAX 4 bullet points per slide
3. Include ONE specific number per slide where possible
4. No complete sentences - just impactful phrases
5. Every word must earn its place

Output JSON array with exactly 12 slides:
[
    {{
        "id": "cover",
        "title": "{company}",
        "subtitle": "One-line tagline (max 8 words)",
        "content": []
    }},
    {{
        "id": "problem",
        "title": "The Problem",
        "subtitle": "One line",
        "content": ["Bullet 1 (max 6 words)", "Bullet 2", "Bullet 3"],
        "stat": "Key statistic about the problem"
    }},
    {{
        "id": "solution",
        "title": "Our Solution",
        "subtitle": "One line",
        "content": ["What you do in 6 words max"],
        "key_benefit": "Main value prop"
    }},
    {{
        "id": "market",
        "title": "Market Opportunity",
        "subtitle": null,
        "tam": "$XB",
        "sam": "$XB",
        "som": "$XM",
        "content": ["Key market insight"]
    }},
    {{
        "id": "product",
        "title": "Product",
        "subtitle": "How it works",
        "content": ["Feature 1", "Feature 2", "Feature 3"],
        "note": "Screenshot/demo would go here"
    }},
    {{
        "id": "business_model",
        "title": "Business Model",
        "subtitle": null,
        "pricing": "Pricing model in 4 words",
        "content": ["Revenue stream 1", "Revenue stream 2"],
        "unit_economics": "Key metric"
    }},
    {{
        "id": "traction",
        "title": "Traction",
        "subtitle": null,
        "metrics": [
            {{"label": "Metric name", "value": "X", "growth": "+Y%"}}
        ],
        "milestones": ["Milestone 1", "Milestone 2"]
    }},
    {{
        "id": "competition",
        "title": "Competitive Landscape",
        "subtitle": null,
        "differentiator": "Why we win in 6 words",
        "competitors": ["Competitor 1", "Competitor 2", "Competitor 3"],
        "our_advantage": "Key advantage"
    }},
    {{
        "id": "team",
        "title": "Team",
        "subtitle": null,
        "members": [
            {{"name": "Name", "role": "Role", "credential": "Key credential"}}
        ]
    }},
    {{
        "id": "financials",
        "title": "Financials",
        "subtitle": "Projections",
        "projections": [
            {{"year": "Year 1", "revenue": "$X"}},
            {{"year": "Year 3", "revenue": "$X"}},
            {{"year": "Year 5", "revenue": "$X"}}
        ],
        "path_to_profitability": "When and how"
    }},
    {{
        "id": "ask",
        "title": "The Ask",
        "subtitle": null,
        "amount": "$X",
        "use_of_funds": [
            {{"category": "Product", "percentage": "X%"}},
            {{"category": "Growth", "percentage": "X%"}},
            {{"category": "Team", "percentage": "X%"}}
        ],
        "milestones_with_funding": ["What you'll achieve"]
    }},
    {{
        "id": "contact",
        "title": "Let's Build Together",
        "subtitle": null,
        "cta": "Call to action",
        "contact": "email@company.com"
    }}
]

Be specific to {company}. Use realistic numbers. Output only JSON array."""
        
        try:
            response = requests.post(
                LM_STUDIO_URL,
                json={
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.4,
                    "max_tokens": 3000
                },
                timeout=180
            )
            
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                
                # Extract JSON array
                json_match = re.search(r'\[[\s\S]*\]', content)
                if json_match:
                    slides = json.loads(json_match.group())
                    return self._enforce_word_limits(slides)
                    
        except Exception as e:
            print(f"[PitchDeck] Error: {e}")
        
        # Return minimal deck if generation fails
        return self._get_fallback_slides(company, description)
    
    def _enforce_word_limits(self, slides: List[Dict]) -> List[Dict]:
        """Enforce word count limits on all slides."""
        
        for slide in slides:
            # Limit subtitle
            if slide.get("subtitle"):
                words = slide["subtitle"].split()
                if len(words) > 10:
                    slide["subtitle"] = " ".join(words[:10]) + "..."
            
            # Limit content bullets
            if slide.get("content"):
                limited = []
                for bullet in slide["content"][:4]:  # Max 4 bullets
                    words = bullet.split()
                    if len(words) > 6:
                        limited.append(" ".join(words[:6]))
                    else:
                        limited.append(bullet)
                slide["content"] = limited
        
        return slides
    
    def _get_fallback_slides(self, company: str, description: str) -> List[Dict]:
        """Fallback slides if LLM fails."""
        return [
            {"id": "cover", "title": company, "subtitle": description[:50]},
            {"id": "problem", "title": "The Problem", "content": ["Problem description needed"]},
            {"id": "solution", "title": "Our Solution", "content": ["Solution description needed"]},
            {"id": "market", "title": "Market", "tam": "TBD", "sam": "TBD", "som": "TBD"},
            {"id": "product", "title": "Product", "content": ["Features TBD"]},
            {"id": "business_model", "title": "Business Model", "content": ["Model TBD"]},
            {"id": "traction", "title": "Traction", "content": ["Metrics TBD"]},
            {"id": "competition", "title": "Competition", "content": ["Analysis TBD"]},
            {"id": "team", "title": "Team", "content": ["Team info TBD"]},
            {"id": "financials", "title": "Financials", "content": ["Projections TBD"]},
            {"id": "ask", "title": "The Ask", "amount": "TBD"},
            {"id": "contact", "title": "Contact", "content": ["Contact TBD"]}
        ]
    
    def _generate_reveal_html(self, company: str, slides: List[Dict], theme: Dict) -> str:
        """Generate reveal.js HTML presentation."""
        
        slides_html = ""
        
        for slide in slides:
            slides_html += self._render_slide(slide, theme)
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{company} - Investor Presentation</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.5.0/reveal.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.5.0/theme/black.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: {theme["primary"]};
            --secondary: {theme["secondary"]};
            --accent: {theme["accent"]};
            --bg: {theme["background"]};
            --text: {theme["text"]};
        }}
        
        .reveal {{
            font-family: 'Inter', sans-serif;
        }}
        
        .reveal .slides {{
            text-align: left;
        }}
        
        .reveal .slides section {{
            background: var(--bg);
            color: var(--text);
            padding: 40px 60px;
        }}
        
        .reveal h1 {{
            font-size: 3.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5em;
        }}
        
        .reveal h2 {{
            font-size: 2.8rem;
            font-weight: 600;
            color: var(--text);
            margin-bottom: 0.8em;
        }}
        
        .reveal h3 {{
            font-size: 1.4rem;
            font-weight: 400;
            color: var(--secondary);
            margin-bottom: 1.5em;
            opacity: 0.9;
        }}
        
        .reveal ul {{
            list-style: none;
            padding: 0;
        }}
        
        .reveal li {{
            font-size: 1.8rem;
            margin: 0.6em 0;
            padding-left: 1.5em;
            position: relative;
        }}
        
        .reveal li::before {{
            content: "→";
            position: absolute;
            left: 0;
            color: var(--accent);
        }}
        
        .stat-box {{
            display: inline-block;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            padding: 20px 40px;
            border-radius: 12px;
            margin: 10px;
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 3rem;
            font-weight: 700;
            color: white;
        }}
        
        .stat-label {{
            font-size: 1rem;
            color: rgba(255,255,255,0.8);
            text-transform: uppercase;
            letter-spacing: 2px;
        }}
        
        .market-sizes {{
            display: flex;
            justify-content: space-around;
            margin-top: 2em;
        }}
        
        .market-circle {{
            text-align: center;
        }}
        
        .market-circle .value {{
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--accent);
        }}
        
        .market-circle .label {{
            font-size: 1.2rem;
            color: var(--secondary);
            text-transform: uppercase;
        }}
        
        .team-grid {{
            display: flex;
            flex-wrap: wrap;
            gap: 30px;
            margin-top: 1em;
        }}
        
        .team-member {{
            flex: 1;
            min-width: 200px;
            background: rgba(255,255,255,0.05);
            padding: 20px;
            border-radius: 12px;
            border-left: 4px solid var(--primary);
        }}
        
        .team-member .name {{
            font-size: 1.4rem;
            font-weight: 600;
            margin-bottom: 5px;
        }}
        
        .team-member .role {{
            color: var(--accent);
            font-size: 1rem;
        }}
        
        .team-member .credential {{
            color: rgba(255,255,255,0.6);
            font-size: 0.9rem;
            margin-top: 10px;
        }}
        
        .funds-chart {{
            display: flex;
            gap: 20px;
            margin-top: 1.5em;
        }}
        
        .fund-item {{
            flex: 1;
            background: rgba(255,255,255,0.05);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
        }}
        
        .fund-item .percentage {{
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--accent);
        }}
        
        .fund-item .category {{
            font-size: 1rem;
            color: var(--secondary);
            text-transform: uppercase;
        }}
        
        .cover-slide {{
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            height: 100%;
        }}
        
        .cover-slide h1 {{
            font-size: 5rem;
        }}
        
        .cta-button {{
            display: inline-block;
            background: linear-gradient(135deg, var(--primary), var(--accent));
            color: white;
            padding: 15px 40px;
            border-radius: 50px;
            font-weight: 600;
            font-size: 1.2rem;
            margin-top: 2em;
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <div class="reveal">
        <div class="slides">
            {slides_html}
        </div>
    </div>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.5.0/reveal.min.js"></script>
    <script>
        Reveal.initialize({{
            hash: true,
            transition: 'slide',
            backgroundTransition: 'fade',
            center: false,
            width: 1920,
            height: 1080
        }});
    </script>
</body>
</html>'''
        
        return html
    
    def _render_slide(self, slide: Dict, theme: Dict) -> str:
        """Render a single slide to HTML."""
        
        slide_id = slide.get("id", "")
        
        if slide_id == "cover":
            return f'''
            <section class="cover-slide">
                <h1>{slide.get("title", "")}</h1>
                <h3>{slide.get("subtitle", "")}</h3>
            </section>
            '''
        
        elif slide_id == "market":
            return f'''
            <section>
                <h2>{slide.get("title", "Market Opportunity")}</h2>
                <div class="market-sizes">
                    <div class="market-circle">
                        <div class="value">{slide.get("tam", "TBD")}</div>
                        <div class="label">TAM</div>
                    </div>
                    <div class="market-circle">
                        <div class="value">{slide.get("sam", "TBD")}</div>
                        <div class="label">SAM</div>
                    </div>
                    <div class="market-circle">
                        <div class="value">{slide.get("som", "TBD")}</div>
                        <div class="label">SOM</div>
                    </div>
                </div>
                {self._render_bullets(slide.get("content", []))}
            </section>
            '''
        
        elif slide_id == "traction":
            metrics_html = ""
            for metric in slide.get("metrics", []):
                metrics_html += f'''
                <div class="stat-box">
                    <div class="stat-value">{metric.get("value", "")}</div>
                    <div class="stat-label">{metric.get("label", "")}</div>
                </div>
                '''
            
            return f'''
            <section>
                <h2>{slide.get("title", "Traction")}</h2>
                <div style="display: flex; gap: 20px; flex-wrap: wrap;">
                    {metrics_html}
                </div>
                {self._render_bullets(slide.get("milestones", []))}
            </section>
            '''
        
        elif slide_id == "team":
            team_html = ""
            for member in slide.get("members", []):
                team_html += f'''
                <div class="team-member">
                    <div class="name">{member.get("name", "")}</div>
                    <div class="role">{member.get("role", "")}</div>
                    <div class="credential">{member.get("credential", "")}</div>
                </div>
                '''
            
            return f'''
            <section>
                <h2>{slide.get("title", "Team")}</h2>
                <div class="team-grid">
                    {team_html}
                </div>
            </section>
            '''
        
        elif slide_id == "ask":
            funds_html = ""
            for fund in slide.get("use_of_funds", []):
                funds_html += f'''
                <div class="fund-item">
                    <div class="percentage">{fund.get("percentage", "")}</div>
                    <div class="category">{fund.get("category", "")}</div>
                </div>
                '''
            
            return f'''
            <section>
                <h2>{slide.get("title", "The Ask")}</h2>
                <div class="stat-box" style="margin-bottom: 30px;">
                    <div class="stat-value">{slide.get("amount", "TBD")}</div>
                    <div class="stat-label">Raising</div>
                </div>
                <h3>Use of Funds</h3>
                <div class="funds-chart">
                    {funds_html}
                </div>
                {self._render_bullets(slide.get("milestones_with_funding", []))}
            </section>
            '''
        
        elif slide_id == "contact":
            return f'''
            <section class="cover-slide">
                <h2>{slide.get("title", "Let's Talk")}</h2>
                <h3>{slide.get("cta", "")}</h3>
                <a href="mailto:{slide.get('contact', '')}" class="cta-button">
                    {slide.get("contact", "Contact Us")}
                </a>
            </section>
            '''
        
        elif slide_id == "financials":
            projections_html = ""
            for proj in slide.get("projections", []):
                projections_html += f'''
                <div class="stat-box">
                    <div class="stat-value">{proj.get("revenue", "")}</div>
                    <div class="stat-label">{proj.get("year", "")}</div>
                </div>
                '''
            
            return f'''
            <section>
                <h2>{slide.get("title", "Financials")}</h2>
                <div style="display: flex; gap: 20px; flex-wrap: wrap;">
                    {projections_html}
                </div>
                <p style="margin-top: 2em; font-size: 1.4rem; color: var(--secondary);">
                    {slide.get("path_to_profitability", "")}
                </p>
            </section>
            '''
        
        else:
            # Generic slide
            subtitle = f'<h3>{slide.get("subtitle", "")}</h3>' if slide.get("subtitle") else ""
            stat = ""
            if slide.get("stat"):
                stat = f'''
                <div class="stat-box" style="margin-top: 1em;">
                    <div class="stat-value" style="font-size: 2rem;">{slide.get("stat")}</div>
                </div>
                '''
            
            return f'''
            <section>
                <h2>{slide.get("title", "")}</h2>
                {subtitle}
                {self._render_bullets(slide.get("content", []))}
                {stat}
            </section>
            '''
    
    def _render_bullets(self, items: List[str]) -> str:
        """Render bullet list."""
        if not items:
            return ""
        
        bullets = "".join([f"<li>{item}</li>" for item in items])
        return f"<ul>{bullets}</ul>"


# Singleton instance
pitch_deck = PitchDeckGenerator()
