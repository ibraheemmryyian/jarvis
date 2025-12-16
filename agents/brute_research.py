"""
Brute Force Research Engine for Jarvis v2
"If you can't outsmart them, outwork them"

Exhaustive multi-source research with parallel execution.
"""
import os
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from .config import CONTEXT_DIR
from .context_manager import context

# Third-party (installed)
try:
    from duckduckgo_search import DDGS
    DDG_AVAILABLE = True
except ImportError:
    DDG_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


@dataclass
class ResearchResult:
    """Container for research findings."""
    source: str
    category: str
    query: str
    data: Any
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    error: Optional[str] = None


class BruteForceResearcher:
    """
    Exhaustive research engine that hits every source, 
    aggregates everything, then synthesizes.
    
    Now with LLM-generated queries for intelligent, topic-specific searches.
    """
    
    def __init__(self, max_workers: int = 15):
        self.max_workers = max_workers
        self.results: List[ResearchResult] = []
        self.progress_callback = None
        
    def _log(self, msg: str):
        """Log progress."""
        print(f"[Research] {msg}")
        if self.progress_callback:
            self.progress_callback(msg)
    
    def _generate_queries_with_llm(self, topic: str) -> List[str]:
        """
        Use LLM to generate intelligent, topic-specific search queries.
        This is the 'smart' part - understanding what to search for.
        """
        from .base_agent import BaseAgent
        
        class QueryGenerator(BaseAgent):
            def __init__(self):
                super().__init__("research")
            
            def _get_system_prompt(self):
                return """You generate search queries for market research. Output a JSON array of 50 search queries.

For the given topic, generate queries covering:
- Direct competitors and alternatives
- Pricing and business models  
- User reviews and complaints
- Technical implementations
- Market size and trends
- Recent news and launches
- Tutorial and how-to content
- Academic research
- Open source alternatives

Make queries SPECIFIC and ACTIONABLE - not generic templates.

Output format: ["query1", "query2", ...]
Output ONLY the JSON array, nothing else."""
            
            def run(self, topic):
                prompt = f'Generate 50 specific search queries for researching: "{topic}"'
                response = self.call_llm(prompt)
                
                # Parse JSON array
                import json
                import re
                try:
                    return json.loads(response)
                except:
                    # Try to extract array from response
                    match = re.search(r'\[.*\]', response, re.DOTALL)
                    if match:
                        try:
                            return json.loads(match.group(0))
                        except:
                            pass
                return []
        
        generator = QueryGenerator()
        queries = generator.run(topic)
        
        if not queries or len(queries) < 10:
            self._log("LLM query generation failed, using fallback templates")
            return self._get_fallback_queries(topic)
        
        self._log(f"LLM generated {len(queries)} intelligent queries")
        return queries
    
    def _get_fallback_queries(self, topic: str) -> List[str]:
        """Fallback template queries if LLM fails."""
        return [
            topic,
            f"{topic} tools",
            f"best {topic} 2024",
            f"{topic} alternatives",
            f"{topic} pricing",
            f"{topic} reviews",
            f"{topic} tutorial",
            f"{topic} open source",
            f"{topic} market size",
            f"{topic} competitors",
        ]
        
    def _log(self, msg: str):
        """Log progress."""
        print(f"[Research] {msg}")
        if self.progress_callback:
            self.progress_callback(msg)
    
    # === SOURCE SCRAPERS ===
    
    def _search_ddg(self, query: str, max_results: int = 10) -> List[Dict]:
        """DuckDuckGo text search."""
        if not DDG_AVAILABLE:
            return []
        try:
            with DDGS() as ddg:
                results = list(ddg.text(query, max_results=max_results))
                return results
        except Exception as e:
            return [{"error": str(e)}]
    
    def _search_ddg_news(self, query: str, max_results: int = 10) -> List[Dict]:
        """DuckDuckGo news search."""
        if not DDG_AVAILABLE:
            return []
        try:
            with DDGS() as ddg:
                results = list(ddg.news(query, max_results=max_results))
                return results
        except Exception as e:
            return [{"error": str(e)}]
    
    def _search_reddit(self, query: str) -> List[Dict]:
        """Search Reddit via DuckDuckGo site search."""
        if not DDG_AVAILABLE:
            return []
        try:
            with DDGS() as ddg:
                results = list(ddg.text(f"site:reddit.com {query}", max_results=15))
                return results
        except Exception as e:
            return [{"error": str(e)}]
    
    def _search_hackernews(self, query: str) -> List[Dict]:
        """Search HackerNews via Algolia API."""
        if not REQUESTS_AVAILABLE:
            return []
        try:
            url = f"https://hn.algolia.com/api/v1/search?query={query}&tags=story&hitsPerPage=15"
            resp = requests.get(url, timeout=10)
            data = resp.json()
            return data.get("hits", [])
        except Exception as e:
            return [{"error": str(e)}]
    
    def _search_arxiv(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search Arxiv for academic papers."""
        if not REQUESTS_AVAILABLE:
            return []
        try:
            import urllib.parse
            encoded = urllib.parse.quote(query)
            url = f"http://export.arxiv.org/api/query?search_query=all:{encoded}&max_results={max_results}"
            resp = requests.get(url, timeout=15)
            
            # Simple XML parsing for titles and summaries
            import re
            entries = re.findall(r'<entry>(.*?)</entry>', resp.text, re.DOTALL)
            results = []
            for entry in entries:
                title = re.search(r'<title>(.*?)</title>', entry, re.DOTALL)
                summary = re.search(r'<summary>(.*?)</summary>', entry, re.DOTALL)
                link = re.search(r'<id>(.*?)</id>', entry)
                results.append({
                    "title": title.group(1).strip() if title else "",
                    "summary": summary.group(1).strip()[:500] if summary else "",
                    "url": link.group(1) if link else ""
                })
            return results
        except Exception as e:
            return [{"error": str(e)}]
    
    def _search_youtube(self, query: str) -> List[Dict]:
        """Search YouTube via DuckDuckGo."""
        if not DDG_AVAILABLE:
            return []
        try:
            with DDGS() as ddg:
                results = list(ddg.text(f"site:youtube.com {query}", max_results=10))
                return results
        except Exception as e:
            return [{"error": str(e)}]
    
    def _search_producthunt(self, query: str) -> List[Dict]:
        """Search ProductHunt via DuckDuckGo."""
        if not DDG_AVAILABLE:
            return []
        try:
            with DDGS() as ddg:
                results = list(ddg.text(f"site:producthunt.com {query}", max_results=10))
                return results
        except Exception as e:
            return [{"error": str(e)}]
    
    def _search_quora(self, query: str) -> List[Dict]:
        """Search Quora via DuckDuckGo."""
        if not DDG_AVAILABLE:
            return []
        try:
            with DDGS() as ddg:
                results = list(ddg.text(f"site:quora.com {query}", max_results=10))
                return results
        except Exception as e:
            return [{"error": str(e)}]
    
    # === PARALLEL EXECUTION ===
    
    def _generate_query_variants(self, topic: str) -> List[Dict]:
        """
        Generate 50+ search queries for exhaustive coverage.
        ~500+ individual results when each returns 10 items.
        """
        queries = []
        
        # === WEB SEARCHES (15 variations) ===
        web_queries = [
            topic,
            f"{topic} tools",
            f"{topic} software",
            f"{topic} apps",
            f"{topic} platforms",
            f"best {topic} 2024",
            f"best {topic} 2025",
            f"top {topic}",
            f"{topic} alternatives",
            f"{topic} comparison",
            f"{topic} guide",
            f"how to {topic}",
            f"{topic} for beginners",
            f"{topic} free",
            f"{topic} open source",
        ]
        for q in web_queries:
            queries.append({"category": "web", "source": "ddg", "query": q, "func": self._search_ddg})
        
        # === NEWS (5 variations) ===
        news_queries = [
            topic,
            f"{topic} startup",
            f"{topic} funding",
            f"{topic} launch",
            f"{topic} announcement",
        ]
        for q in news_queries:
            queries.append({"category": "news", "source": "ddg_news", "query": q, "func": self._search_ddg_news})
        
        # === REDDIT (5 variations) ===
        reddit_queries = [
            topic,
            f"{topic} problems",
            f"{topic} recommendations",
            f"best {topic}",
            f"{topic} advice",
        ]
        for q in reddit_queries:
            queries.append({"category": "reddit", "source": "reddit", "query": q, "func": self._search_reddit})
        
        # === HACKER NEWS (3 variations) ===
        hn_queries = [topic, f"{topic} Show HN", f"{topic} Ask HN"]
        for q in hn_queries:
            queries.append({"category": "hackernews", "source": "hn", "query": q, "func": self._search_hackernews})
        
        # === QUORA (3 variations) ===
        quora_queries = [f"how to {topic}", f"what is {topic}", f"best {topic}"]
        for q in quora_queries:
            queries.append({"category": "quora", "source": "quora", "query": q, "func": self._search_quora})
        
        # === ACADEMIC (3 variations) ===
        arxiv_queries = [topic, f"{topic} algorithms", f"{topic} research"]
        for q in arxiv_queries:
            queries.append({"category": "academic", "source": "arxiv", "query": q, "func": self._search_arxiv})
        
        # === YOUTUBE (5 variations) ===
        youtube_queries = [
            f"{topic} tutorial",
            f"{topic} review",
            f"{topic} how to",
            f"{topic} demo",
            f"{topic} comparison",
        ]
        for q in youtube_queries:
            queries.append({"category": "youtube", "source": "youtube", "query": q, "func": self._search_youtube})
        
        # === COMPETITORS/PRODUCTS (5 variations) ===
        competitor_queries = [
            topic,
            f"{topic} pricing",
            f"{topic} vs",
            f"{topic} reviews",
            f"{topic} features",
        ]
        for q in competitor_queries:
            queries.append({"category": "competitors", "source": "producthunt", "query": q, "func": self._search_producthunt})
        
        # === MARKET DATA (6 variations) ===
        market_queries = [
            f"{topic} market size",
            f"{topic} industry trends",
            f"{topic} statistics 2024",
            f"{topic} growth rate",
            f"{topic} revenue",
            f"{topic} market analysis",
        ]
        for q in market_queries:
            queries.append({"category": "market", "source": "ddg", "query": q, "func": self._search_ddg})
        
        return queries
    
    def _execute_search(self, search_config: Dict) -> ResearchResult:
        """Execute a single search and return result."""
        try:
            data = search_config["func"](search_config["query"])
            return ResearchResult(
                source=search_config["source"],
                category=search_config["category"],
                query=search_config["query"],
                data=data
            )
        except Exception as e:
            return ResearchResult(
                source=search_config["source"],
                category=search_config["category"],
                query=search_config["query"],
                data=[],
                error=str(e)
            )
    
    def gather(self, topic: str, progress_callback=None, use_llm_queries: bool = True) -> List[ResearchResult]:
        """
        Execute all searches in parallel.
        
        Args:
            topic: What to research
            progress_callback: Function to call with updates
            use_llm_queries: If True, use LLM to generate intelligent queries (recommended)
        """
        self.progress_callback = progress_callback
        self.results = []
        
        # Step 1: Generate queries (LLM or template)
        if use_llm_queries:
            self._log("Phase 1: Generating intelligent queries with LLM...")
            llm_queries = self._generate_queries_with_llm(topic)
            
            # Convert LLM queries to search configs with smart source routing
            searches = []
            for q in llm_queries:
                q_lower = q.lower()
                
                # Route to appropriate source based on query content
                if "reddit" in q_lower or "problems" in q_lower or "complaints" in q_lower:
                    searches.append({"category": "reddit", "source": "reddit", "query": q, "func": self._search_reddit})
                elif "youtube" in q_lower or "tutorial" in q_lower or "video" in q_lower:
                    searches.append({"category": "youtube", "source": "youtube", "query": q, "func": self._search_youtube})
                elif "news" in q_lower or "launch" in q_lower or "funding" in q_lower or "announcement" in q_lower:
                    searches.append({"category": "news", "source": "ddg_news", "query": q, "func": self._search_ddg_news})
                elif "research" in q_lower or "paper" in q_lower or "academic" in q_lower or "study" in q_lower:
                    searches.append({"category": "academic", "source": "arxiv", "query": q, "func": self._search_arxiv})
                elif "producthunt" in q_lower or "hacker news" in q_lower:
                    searches.append({"category": "hackernews", "source": "hn", "query": q, "func": self._search_hackernews})
                elif "quora" in q_lower or "how do" in q_lower or "what is" in q_lower:
                    searches.append({"category": "quora", "source": "quora", "query": q, "func": self._search_quora})
                else:
                    # Default to DuckDuckGo web search
                    searches.append({"category": "web", "source": "ddg", "query": q, "func": self._search_ddg})
        else:
            searches = self._generate_query_variants(topic)
        
        # Step 2: Execute all searches in parallel
        self._log(f"Phase 2: Executing {len(searches)} parallel searches...")
        
        completed = 0
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self._execute_search, s): s for s in searches}
            
            for future in as_completed(futures):
                result = future.result()
                self.results.append(result)
                completed += 1
                if completed % 10 == 0:  # Log every 10 to reduce noise
                    self._log(f"[{completed}/{len(searches)}] searches complete...")
        
        # Count actual results
        total_items = sum(len(r.data) if isinstance(r.data, list) else 0 for r in self.results)
        self._log(f"Phase 2 complete: {len(self.results)} queries → {total_items} total results")
        
        return self.results
    
    def aggregate_by_category(self) -> Dict[str, List[Dict]]:
        """Group all results by category."""
        aggregated = {}
        for result in self.results:
            if result.category not in aggregated:
                aggregated[result.category] = []
            if isinstance(result.data, list):
                aggregated[result.category].extend(result.data)
        return aggregated
    
    def to_context_string(self) -> str:
        """Convert all results to a string for LLM context."""
        aggregated = self.aggregate_by_category()
        
        sections = []
        for category, items in aggregated.items():
            section = f"\n## {category.upper()}\n"
            for item in items[:20]:  # Limit per category
                if isinstance(item, dict):
                    title = item.get("title") or item.get("headline") or item.get("body", "")[:100]
                    url = item.get("href") or item.get("url") or item.get("link", "")
                    section += f"- {title[:100]}\n"
            sections.append(section)
        
        return "\n".join(sections)
    
    def save_raw(self, topic: str):
        """Save raw results to context directory."""
        filepath = os.path.join(CONTEXT_DIR, "research_raw.json")
        data = {
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
            "total_results": len(self.results),
            "results": [
                {
                    "source": r.source,
                    "category": r.category,
                    "query": r.query,
                    "count": len(r.data) if isinstance(r.data, list) else 1,
                    "error": r.error
                }
                for r in self.results
            ]
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        self._log(f"Raw results saved to {filepath}")


# Singleton
brute_researcher = BruteForceResearcher()
