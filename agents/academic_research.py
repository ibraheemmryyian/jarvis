"""
Academic Research Agent for Jarvis v2
Multi-source academic paper search, citation generation, and literature synthesis.
"""
import os
import re
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional
from .config import WORKSPACE_DIR, LM_STUDIO_URL


class AcademicResearch:
    """
    Academic research assistant for papers, citations, and literature reviews.
    
    Features:
    - Multi-source search (arXiv, Semantic Scholar, CrossRef)
    - Citation generation (APA, MLA, IEEE, Chicago)
    - Literature review synthesis
    - Key findings extraction
    - Research gap identification
    """
    
    # API endpoints
    ARXIV_API = "http://export.arxiv.org/api/query"
    SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1/paper/search"
    CROSSREF_API = "https://api.crossref.org/works"
    
    def __init__(self):
        self.results_dir = os.path.join(WORKSPACE_DIR, "research")
        os.makedirs(self.results_dir, exist_ok=True)
        self.cache = {}
    
    def search(self, query: str, sources: List[str] = None, max_results: int = 10) -> Dict:
        """
        Search for academic papers across multiple sources.
        
        Args:
            query: Search query
            sources: List of sources to search ('arxiv', 'semantic_scholar', 'crossref')
            max_results: Maximum results per source
            
        Returns:
            Dict with papers organized by source
        """
        if sources is None:
            sources = ['arxiv', 'semantic_scholar']
        
        results = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "total_papers": 0,
            "papers": []
        }
        
        for source in sources:
            if source == 'arxiv':
                papers = self._search_arxiv(query, max_results)
            elif source == 'semantic_scholar':
                papers = self._search_semantic_scholar(query, max_results)
            elif source == 'crossref':
                papers = self._search_crossref(query, max_results)
            else:
                continue
            
            results["papers"].extend(papers)
            results["total_papers"] += len(papers)
        
        # Remove duplicates by title similarity
        results["papers"] = self._deduplicate(results["papers"])
        results["total_papers"] = len(results["papers"])
        
        return results
    
    def _search_arxiv(self, query: str, max_results: int) -> List[Dict]:
        """Search arXiv for papers."""
        papers = []
        
        try:
            params = {
                "search_query": f"all:{query}",
                "start": 0,
                "max_results": max_results,
                "sortBy": "relevance"
            }
            
            response = requests.get(self.ARXIV_API, params=params, timeout=30)
            
            if response.status_code == 200:
                # Parse XML response
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.content)
                
                ns = {'atom': 'http://www.w3.org/2005/Atom'}
                
                for entry in root.findall('atom:entry', ns):
                    paper = {
                        "source": "arxiv",
                        "title": entry.find('atom:title', ns).text.strip().replace('\n', ' '),
                        "authors": [a.find('atom:name', ns).text for a in entry.findall('atom:author', ns)],
                        "abstract": entry.find('atom:summary', ns).text.strip()[:500],
                        "published": entry.find('atom:published', ns).text[:10],
                        "url": entry.find('atom:id', ns).text,
                        "pdf_url": None
                    }
                    
                    # Get PDF link
                    for link in entry.findall('atom:link', ns):
                        if link.get('title') == 'pdf':
                            paper["pdf_url"] = link.get('href')
                    
                    papers.append(paper)
                    
        except Exception as e:
            print(f"[Research] arXiv error: {e}")
        
        return papers
    
    def _search_semantic_scholar(self, query: str, max_results: int) -> List[Dict]:
        """Search Semantic Scholar for papers."""
        papers = []
        
        try:
            params = {
                "query": query,
                "limit": max_results,
                "fields": "title,authors,abstract,year,citationCount,url,externalIds"
            }
            
            response = requests.get(self.SEMANTIC_SCHOLAR_API, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                for item in data.get("data", []):
                    paper = {
                        "source": "semantic_scholar",
                        "title": item.get("title", ""),
                        "authors": [a.get("name", "") for a in item.get("authors", [])],
                        "abstract": (item.get("abstract") or "")[:500],
                        "published": str(item.get("year", "")),
                        "url": item.get("url", ""),
                        "citations": item.get("citationCount", 0),
                        "doi": item.get("externalIds", {}).get("DOI")
                    }
                    papers.append(paper)
                    
        except Exception as e:
            print(f"[Research] Semantic Scholar error: {e}")
        
        return papers
    
    def _search_crossref(self, query: str, max_results: int) -> List[Dict]:
        """Search CrossRef for papers."""
        papers = []
        
        try:
            params = {
                "query": query,
                "rows": max_results,
                "sort": "relevance"
            }
            
            response = requests.get(self.CROSSREF_API, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                for item in data.get("message", {}).get("items", []):
                    paper = {
                        "source": "crossref",
                        "title": item.get("title", [""])[0],
                        "authors": [f"{a.get('given', '')} {a.get('family', '')}" 
                                   for a in item.get("author", [])],
                        "abstract": "",  # CrossRef often doesn't have abstracts
                        "published": str(item.get("published-print", {}).get("date-parts", [[""]])[0][0]),
                        "url": item.get("URL", ""),
                        "doi": item.get("DOI"),
                        "journal": item.get("container-title", [""])[0]
                    }
                    papers.append(paper)
                    
        except Exception as e:
            print(f"[Research] CrossRef error: {e}")
        
        return papers
    
    def _deduplicate(self, papers: List[Dict]) -> List[Dict]:
        """Remove duplicate papers by title similarity."""
        unique = []
        seen_titles = set()
        
        for paper in papers:
            # Normalize title for comparison
            title_normalized = paper["title"].lower().strip()
            title_key = re.sub(r'[^a-z0-9]', '', title_normalized)[:50]
            
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique.append(paper)
        
        return unique
    
    def generate_citation(self, paper: Dict, style: str = "APA") -> str:
        """
        Generate a formatted citation.
        
        Args:
            paper: Paper dict from search results
            style: Citation style ('APA', 'MLA', 'IEEE', 'Chicago')
            
        Returns:
            Formatted citation string
        """
        authors = paper.get("authors", [])
        title = paper.get("title", "")
        year = paper.get("published", "")[:4]
        url = paper.get("url", "")
        doi = paper.get("doi", "")
        journal = paper.get("journal", "")
        
        if style.upper() == "APA":
            # APA 7th edition
            if len(authors) == 1:
                author_str = authors[0]
            elif len(authors) == 2:
                author_str = f"{authors[0]} & {authors[1]}"
            elif len(authors) > 2:
                author_str = f"{authors[0]} et al."
            else:
                author_str = "Unknown"
            
            citation = f"{author_str} ({year}). {title}."
            if journal:
                citation += f" {journal}."
            if doi:
                citation += f" https://doi.org/{doi}"
            elif url:
                citation += f" {url}"
            
        elif style.upper() == "MLA":
            # MLA 9th edition
            author_str = ", ".join(authors[:3])
            if len(authors) > 3:
                author_str += ", et al"
            
            citation = f'{author_str}. "{title}."'
            if journal:
                citation += f" {journal},"
            citation += f" {year}."
            if url:
                citation += f" {url}"
                
        elif style.upper() == "IEEE":
            # IEEE style
            author_abbrev = []
            for author in authors[:6]:
                parts = author.split()
                if len(parts) >= 2:
                    author_abbrev.append(f"{parts[0][0]}. {parts[-1]}")
                else:
                    author_abbrev.append(author)
            
            author_str = ", ".join(author_abbrev)
            if len(authors) > 6:
                author_str += ", et al."
            
            citation = f'{author_str}, "{title},"'
            if journal:
                citation += f" {journal},"
            citation += f" {year}."
            if doi:
                citation += f" doi: {doi}"
                
        elif style.upper() == "CHICAGO":
            # Chicago style
            author_str = ", ".join(authors[:3])
            if len(authors) > 3:
                author_str += ", et al"
            
            citation = f'{author_str}. "{title}."'
            if journal:
                citation += f" {journal}"
            citation += f" ({year})."
            if url:
                citation += f" {url}"
        
        else:
            citation = f"{', '.join(authors)}. {title}. {year}."
        
        return citation
    
    def summarize_paper(self, paper: Dict) -> Dict:
        """
        Use LLM to summarize a paper's key findings.
        
        Args:
            paper: Paper dict with abstract
            
        Returns:
            Dict with summary, key findings, methodology
        """
        abstract = paper.get("abstract", "")
        title = paper.get("title", "")
        
        if not abstract:
            return {"error": "No abstract available for summarization"}
        
        prompt = f"""Analyze this academic paper and extract key information:

TITLE: {title}

ABSTRACT: {abstract}

Provide a structured summary in JSON format:
{{
    "main_finding": "One sentence describing the primary finding",
    "methodology": "Brief description of the research method",
    "key_contributions": ["list", "of", "contributions"],
    "limitations": "Any mentioned limitations",
    "relevance": "Why this paper matters"
}}

Output only the JSON, no other text."""
        
        try:
            response = requests.post(
                LM_STUDIO_URL,
                json={
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 500
                },
                timeout=60
            )
            
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                # Try to parse JSON
                try:
                    # Find JSON in response
                    json_match = re.search(r'\{[\s\S]*\}', content)
                    if json_match:
                        return json.loads(json_match.group())
                except:
                    return {"summary": content}
                    
        except Exception as e:
            return {"error": str(e)}
        
        return {"error": "Failed to summarize"}
    
    def generate_literature_review(self, query: str, num_papers: int = 10) -> Dict:
        """
        Generate a comprehensive literature review.
        
        Args:
            query: Research topic
            num_papers: Number of papers to include
            
        Returns:
            Dict with literature review content
        """
        print(f"[Research] Generating literature review for: {query}")
        
        # Search for papers
        search_results = self.search(query, max_results=num_papers)
        papers = search_results["papers"]
        
        if not papers:
            return {"error": "No papers found for this query"}
        
        # Generate citations for all papers
        citations = []
        paper_summaries = []
        
        for i, paper in enumerate(papers[:num_papers]):
            citation = self.generate_citation(paper, "APA")
            citations.append(f"[{i+1}] {citation}")
            
            # Get summary if abstract available
            if paper.get("abstract"):
                summary = self.summarize_paper(paper)
                paper_summaries.append({
                    "title": paper["title"],
                    "citation_num": i + 1,
                    "summary": summary
                })
        
        # Use LLM to synthesize the literature review
        synthesis_prompt = f"""You are writing a literature review on: "{query}"

Here are summaries of {len(paper_summaries)} relevant papers:

{json.dumps(paper_summaries, indent=2)}

Write a cohesive literature review that:
1. Introduces the topic and its importance
2. Groups papers by themes/approaches
3. Identifies agreements and disagreements in the literature
4. Highlights research gaps
5. Concludes with future directions

Use citation numbers like [1], [2] to reference papers.
Format in Markdown with clear sections.
Keep it concise but comprehensive (500-800 words)."""
        
        try:
            response = requests.post(
                LM_STUDIO_URL,
                json={
                    "messages": [{"role": "user", "content": synthesis_prompt}],
                    "temperature": 0.3,
                    "max_tokens": 2000
                },
                timeout=120
            )
            
            if response.status_code == 200:
                review_content = response.json()["choices"][0]["message"]["content"]
            else:
                review_content = "Failed to generate synthesis."
                
        except Exception as e:
            review_content = f"Error generating review: {e}"
        
        # Compile the final output
        result = {
            "topic": query,
            "timestamp": datetime.now().isoformat(),
            "num_papers": len(papers),
            "literature_review": review_content,
            "references": citations,
            "papers": papers
        }
        
        # Save to file
        self._save_review(query, result)
        
        return result
    
    def _save_review(self, query: str, result: Dict):
        """Save literature review to file."""
        # Create safe filename
        safe_name = re.sub(r'[^a-zA-Z0-9]', '_', query)[:50]
        filename = f"lit_review_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = os.path.join(self.results_dir, filename)
        
        # Format as Markdown
        content = f"""# Literature Review: {query}

Generated: {result['timestamp']}
Papers Analyzed: {result['num_papers']}

---

{result['literature_review']}

---

## References

"""
        for ref in result.get("references", []):
            content += f"{ref}\n\n"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"[Research] Saved to: {filepath}")
        result["saved_to"] = filepath
    
    def find_research_gaps(self, query: str) -> Dict:
        """
        Identify research gaps in a field.
        
        Args:
            query: Research topic
            
        Returns:
            Dict with identified gaps and future directions
        """
        # Get recent papers
        results = self.search(query, max_results=15)
        
        if not results["papers"]:
            return {"error": "No papers found"}
        
        # Compile abstracts
        abstracts = "\n\n".join([
            f"Paper: {p['title']}\nAbstract: {p.get('abstract', 'N/A')}"
            for p in results["papers"][:10]
        ])
        
        prompt = f"""Analyze these academic papers on "{query}" and identify research gaps:

{abstracts}

Provide analysis in JSON format:
{{
    "well_studied_areas": ["areas with lots of research"],
    "research_gaps": [
        {{"gap": "description", "importance": "high/medium/low", "potential_approach": "how to address"}}
    ],
    "emerging_trends": ["new directions appearing"],
    "recommended_research_questions": ["specific questions worth investigating"]
}}

Output only JSON."""
        
        try:
            response = requests.post(
                LM_STUDIO_URL,
                json={
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 1000
                },
                timeout=90
            )
            
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                json_match = re.search(r'\{[\s\S]*\}', content)
                if json_match:
                    return json.loads(json_match.group())
                    
        except Exception as e:
            return {"error": str(e)}
        
        return {"error": "Failed to analyze"}


# Singleton instance
academic_research = AcademicResearch()
