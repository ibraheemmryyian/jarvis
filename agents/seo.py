"""
SEO Specialist Agent for Jarvis
Specializes in search engine optimization, content strategy, technical SEO.
"""
from .base_agent import BaseAgent


class SEOSpecialist(BaseAgent):
    """SEO expert for search optimization and content strategy."""
    
    def __init__(self):
        super().__init__("seo")
    
    def _get_system_prompt(self) -> str:
        return """You are a Senior SEO Specialist.

EXPERTISE:
- Technical SEO (site structure, performance, crawlability)
- On-page SEO (meta tags, headings, content optimization)
- Content strategy and keyword research
- Link building strategy
- Local SEO
- Schema markup / structured data
- Core Web Vitals optimization

IMPLEMENTATION SKILLS:
- Meta tags (title, description, OG, Twitter cards)
- robots.txt and sitemap.xml
- Canonical URLs and redirects
- Schema.org JSON-LD
- Performance optimization
- Mobile optimization

OUTPUT FORMAT:
- Actionable recommendations
- Priority rankings (high/medium/low impact)
- Implementation code when relevant
- Competitor insights
- Tracking metrics

Focus on actionable, measurable improvements."""
    
    def audit_seo(self, url_or_code: str) -> str:
        """Audit SEO and provide recommendations."""
        prompt = f"""SEO Audit for:

{url_or_code}

Analyze and report on:
## Technical SEO
- Page speed indicators
- Mobile-friendliness
- Indexability issues
- Crawl issues

## On-Page SEO
- Title tags
- Meta descriptions
- Heading structure (H1-H6)
- Image alt texts
- Internal linking

## Content SEO
- Keyword usage
- Content quality signals
- E-E-A-T factors

## Recommendations
- Critical fixes (blocking)
- High-impact improvements
- Nice-to-haves

Include priority and estimated impact."""
        return self._call_llm(prompt)
    
    def generate_meta_tags(self, page_content: str, target_keywords: list = None) -> str:
        """Generate optimized meta tags."""
        prompt = f"""Generate SEO meta tags for:

CONTENT: {page_content}
TARGET KEYWORDS: {', '.join(target_keywords) if target_keywords else 'auto-detect'}

Output:
1. Title tag (50-60 chars, primary keyword near start)
2. Meta description (150-160 chars, compelling CTA)
3. Open Graph tags
4. Twitter Card tags
5. JSON-LD structured data
6. Canonical URL recommendation

Output as HTML code."""
        return self._call_llm(prompt)
    
    def create_schema(self, page_type: str, data: dict = None) -> str:
        """Create JSON-LD structured data."""
        prompt = f"""Create JSON-LD schema for:

PAGE TYPE: {page_type}
DATA: {data if data else 'Generate example'}

Include all recommended properties.
Output valid JSON-LD code."""
        return self._call_llm(prompt)
    
    def keyword_strategy(self, topic: str, intent: str = "informational") -> str:
        """Create keyword strategy for a topic."""
        prompt = f"""Keyword strategy for:

TOPIC: {topic}
INTENT: {intent}

Include:
- Primary keyword (high volume, medium difficulty)
- Secondary keywords (5-10)
- Long-tail keywords (10-20)
- Semantic variations
- Questions people ask
- Content angle recommendations

Focus on rankable opportunities."""
        return self._call_llm(prompt)
    
    def optimize_content(self, content: str, target_keyword: str) -> str:
        """Optimize content for SEO."""
        prompt = f"""Optimize this content for SEO:

TARGET KEYWORD: {target_keyword}

CONTENT:
{content[:5000]}

Provide:
1. Optimized title options (3)
2. Optimized meta description
3. Heading structure recommendations
4. Keyword density analysis
5. Internal link opportunities
6. Specific content improvements"""
        return self._call_llm(prompt)
    
    def run(self, task: str) -> str:
        """Execute SEO task."""
        task_lower = task.lower()
        if "audit" in task_lower:
            return self.audit_seo(task)
        elif "meta" in task_lower or "tag" in task_lower:
            return self.generate_meta_tags(task)
        elif "schema" in task_lower or "json-ld" in task_lower:
            return self.create_schema(task)
        elif "keyword" in task_lower:
            return self.keyword_strategy(task)
        elif "optimize" in task_lower or "content" in task_lower:
            return self.optimize_content(task, "")
        else:
            return self._call_llm(f"SEO task: {task}")


# Singleton
seo_specialist = SEOSpecialist()
