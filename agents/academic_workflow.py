"""
Academic Workflow Agent for Jarvis
Complete A-to-Z academic paper pipeline with review, plagiarism, and anti-hallucination.
"""
import os
import re
import json
import hashlib
import requests
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from .base_agent import BaseAgent
from .config import WORKSPACE_DIR, LM_STUDIO_URL


class AcademicWorkflow(BaseAgent):
    """
    Complete academic paper workflow: write, review, critique, verify.
    
    Features:
    - Full paper generation (outline → draft → revise → finalize)
    - Academic reviewer (critique, feedback, scoring)
    - Plagiarism detection (similarity checking)
    - Anti-hallucination (source verification, claim-citation matching)
    """
    
    def __init__(self):
        super().__init__("academic_workflow")
        self.papers_dir = os.path.join(WORKSPACE_DIR, "papers")
        self.sources_cache = {}  # Cache verified sources
        os.makedirs(self.papers_dir, exist_ok=True)
    
    def _get_system_prompt(self) -> str:
        return """You are an Expert Academic Writer and Reviewer.

ANTI-HALLUCINATION RULES:
1. EVERY factual claim MUST have a citation marker [NEEDS_SOURCE]
2. NEVER invent statistics, numbers, or data
3. Use hedging language: "suggests", "indicates", "appears to"
4. Clearly mark speculation: "[HYPOTHESIS]" or "[SPECULATION]"
5. When uncertain, write "[REQUIRES VERIFICATION]"

ACADEMIC STANDARDS:
- Formal academic tone
- Proper paragraph structure
- Evidence-based argumentation
- Acknowledge limitations
- Use passive voice in methods

OUTPUT REQUIREMENTS:
- All claims marked with citation needs
- Clear section headings
- Proper formatting
- Acknowledgment of gaps"""
    
    # === FULL PAPER PIPELINE ===
    
    def write_paper(self, topic: str, paper_type: str = "imrad", 
                   sources: List[Dict] = None, word_target: int = 3000) -> Dict:
        """
        Write a complete academic paper from A to Z.
        
        Pipeline: Research → Outline → Draft → Verify → Revise → Finalize
        """
        result = {
            "topic": topic,
            "type": paper_type,
            "stages": {},
            "warnings": [],
            "unverified_claims": []
        }
        
        print(f"[Academic] Starting paper: {topic}")
        
        # STAGE 1: Research phase
        print("[Academic] Stage 1: Research...")
        from .academic_research import academic_research
        research = academic_research.search(topic, max_results=15)
        result["stages"]["research"] = {
            "papers_found": len(research.get("papers", [])),
            "sources": research.get("papers", [])[:10]
        }
        sources = result["stages"]["research"]["sources"]
        
        # STAGE 2: Generate outline
        print("[Academic] Stage 2: Outline...")
        outline = self._generate_outline(topic, paper_type, sources)
        result["stages"]["outline"] = outline
        
        # STAGE 3: Write first draft with anti-hallucination markers
        print("[Academic] Stage 3: First draft...")
        draft = self._write_draft(topic, outline, sources, word_target)
        result["stages"]["first_draft"] = draft
        
        # STAGE 4: Verify claims (anti-hallucination)
        print("[Academic] Stage 4: Verification...")
        verification = self._verify_claims(draft["content"], sources)
        result["stages"]["verification"] = verification
        result["unverified_claims"] = verification.get("unverified", [])
        
        # STAGE 5: Academic review
        print("[Academic] Stage 5: Academic review...")
        review = self.review_paper(draft["content"])
        result["stages"]["review"] = review
        
        # STAGE 6: Revise based on review
        print("[Academic] Stage 6: Revision...")
        revised = self._revise_paper(draft["content"], review, verification)
        result["stages"]["revision"] = revised
        
        # STAGE 7: Final check and format
        print("[Academic] Stage 7: Finalization...")
        final = self._finalize_paper(revised["content"], sources, paper_type)
        result["final_paper"] = final
        
        # Save paper
        filepath = self._save_paper(topic, final)
        result["saved_to"] = filepath
        
        return result
    
    def _generate_outline(self, topic: str, paper_type: str, sources: List[Dict]) -> Dict:
        """Generate paper outline based on type and sources."""
        from .research_publisher import research_publisher
        
        template = research_publisher.get_paper_template(paper_type)
        
        source_summary = "\n".join([
            f"- {s['title']} ({s.get('published', 'n.d.')})"
            for s in sources[:5]
        ])
        
        prompt = f"""Create a detailed outline for an academic paper.

TOPIC: {topic}
PAPER TYPE: {paper_type}
AVAILABLE SOURCES:
{source_summary}

Based on this template structure:
{template[:2000]}

Generate a detailed outline with:
1. Each major section
2. Subsections with 2-3 bullet points of what to cover
3. Notes on which sources support each section
4. Estimated word count per section (total: 3000 words)

Format as Markdown outline."""
        
        outline_text = self._call_llm(prompt)
        
        return {
            "content": outline_text,
            "sections": self._parse_outline_sections(outline_text)
        }
    
    def _parse_outline_sections(self, outline: str) -> List[str]:
        """Extract section headings from outline."""
        sections = []
        for line in outline.split("\n"):
            if line.strip().startswith("#"):
                sections.append(line.strip().lstrip("#").strip())
        return sections
    
    def _write_draft(self, topic: str, outline: Dict, sources: List[Dict], 
                    word_target: int) -> Dict:
        """Write first draft with anti-hallucination markers."""
        source_info = json.dumps([
            {"title": s["title"], "authors": s.get("authors", [])[:2], 
             "year": s.get("published", "")[:4], "abstract": s.get("abstract", "")[:300]}
            for s in sources[:8]
        ], indent=2)
        
        prompt = f"""Write a complete academic paper draft.

TOPIC: {topic}
TARGET WORDS: {word_target}

OUTLINE:
{outline['content'][:3000]}

AVAILABLE SOURCES:
{source_info}

CRITICAL ANTI-HALLUCINATION RULES:
1. For EVERY factual claim, add a citation like (Author, Year) or [1]
2. If you don't have a source for a claim, mark it: [NEEDS_SOURCE]
3. NEVER invent statistics - use "[STAT NEEDED]" placeholder
4. For speculation/hypothesis, clearly mark: "[HYPOTHESIS]"
5. Use hedging language: "appears to", "suggests", "may indicate"

STRUCTURE:
- Write each section from the outline
- Include proper transitions
- Add in-text citations
- Mark any claims needing verification

Begin writing the complete paper:"""
        
        content = self._call_llm(prompt, max_tokens=8000)
        
        # Count markers
        needs_source = len(re.findall(r'\[NEEDS_SOURCE\]', content))
        stat_needed = len(re.findall(r'\[STAT NEEDED\]', content))
        hypotheses = len(re.findall(r'\[HYPOTHESIS\]', content))
        
        return {
            "content": content,
            "word_count": len(content.split()),
            "markers": {
                "needs_source": needs_source,
                "stat_needed": stat_needed, 
                "hypotheses": hypotheses
            }
        }
    
    # === ANTI-HALLUCINATION SYSTEM ===
    
    def _verify_claims(self, content: str, sources: List[Dict]) -> Dict:
        """Verify claims against sources - anti-hallucination check."""
        
        # Extract claims with citations
        citation_pattern = r'([^.]*\([A-Z][a-z]+,?\s*\d{4}\)[^.]*\.)'
        cited_claims = re.findall(citation_pattern, content)
        
        # Extract uncited claims (sentences without citations)
        unverified = []
        
        prompt = f"""Analyze this academic content for hallucination risks.

CONTENT:
{content[:4000]}

AVAILABLE SOURCES:
{json.dumps([s['title'] for s in sources[:10]])}

Identify:
1. Claims without citations that need sources
2. Statistics or numbers that need verification
3. Strong claims that may be speculation
4. Any invented-sounding data

Output JSON:
{{
    "verified_claims": ["claims that match source titles"],
    "unverified": ["claims without proper support"],
    "suspicious_stats": ["statistics that look invented"],
    "speculation_found": ["claims presented as fact but are speculation"],
    "hallucination_risk": "low/medium/high",
    "recommendation": "what to fix"
}}"""
        
        try:
            response = self._call_llm(prompt, max_tokens=1500)
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                verification = json.loads(json_match.group())
            else:
                verification = {"error": "Could not parse verification"}
        except:
            verification = {"error": "Verification failed"}
        
        # Count [NEEDS_SOURCE] markers
        verification["explicit_markers"] = len(re.findall(r'\[NEEDS_SOURCE\]', content))
        
        return verification
    
    def verify_single_claim(self, claim: str, sources: List[Dict] = None) -> Dict:
        """Verify a single claim against academic sources."""
        
        # Search for relevant sources
        if not sources:
            from .academic_research import academic_research
            results = academic_research.search(claim[:100], max_results=5)
            sources = results.get("papers", [])
        
        source_abstracts = "\n".join([
            f"Source {i+1}: {s['title']}\n{s.get('abstract', '')[:300]}"
            for i, s in enumerate(sources[:5])
        ])
        
        prompt = f"""Verify this academic claim against available sources.

CLAIM: "{claim}"

SOURCES:
{source_abstracts}

Analyze:
1. Is this claim supported by any source?
2. Is it contradicted by any source?
3. Is it a reasonable inference?
4. What level of confidence can we have?

Output JSON:
{{
    "claim": "{claim[:100]}...",
    "verdict": "VERIFIED|PARTIALLY_SUPPORTED|UNVERIFIED|CONTRADICTED",
    "supporting_sources": [list of source numbers],
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation",
    "suggested_revision": "how to rewrite if needed"
}}"""
        
        response = self._call_llm(prompt)
        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return {"verdict": "UNVERIFIED", "confidence": 0.0}
    
    # === PLAGIARISM DETECTION ===
    
    def check_plagiarism(self, content: str) -> Dict:
        """
        Check content for potential plagiarism.
        Uses n-gram similarity and source matching.
        """
        result = {
            "similarity_score": 0.0,
            "flagged_passages": [],
            "potential_sources": [],
            "recommendation": ""
        }
        
        # Extract key phrases (potential plagiarism indicators)
        sentences = re.split(r'[.!?]', content)
        
        # Check for exact phrase matches in sources
        from .academic_research import academic_research
        
        flagged = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 50:  # Only check substantial sentences
                # Search for similar content
                results = academic_research.search(sentence[:100], max_results=3)
                
                for paper in results.get("papers", []):
                    abstract = paper.get("abstract", "").lower()
                    sentence_lower = sentence.lower()
                    
                    # Check for significant overlap
                    overlap = self._calculate_overlap(sentence_lower, abstract)
                    
                    if overlap > 0.6:  # 60% similarity threshold
                        flagged.append({
                            "passage": sentence[:100] + "...",
                            "similar_to": paper["title"],
                            "similarity": round(overlap * 100, 1)
                        })
        
        result["flagged_passages"] = flagged[:10]  # Limit to top 10
        result["similarity_score"] = len(flagged) / max(len(sentences), 1) * 100
        
        if result["similarity_score"] > 30:
            result["recommendation"] = "HIGH RISK: Significant similarity detected. Rewrite flagged passages."
        elif result["similarity_score"] > 10:
            result["recommendation"] = "MEDIUM RISK: Some similar passages. Consider paraphrasing."
        else:
            result["recommendation"] = "LOW RISK: Content appears original."
        
        return result
    
    def _calculate_overlap(self, text1: str, text2: str) -> float:
        """Calculate word overlap between two texts."""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        overlap = len(words1 & words2)
        return overlap / min(len(words1), len(words2))
    
    # === ACADEMIC REVIEW ===
    
    def review_paper(self, content: str, review_type: str = "comprehensive") -> Dict:
        """
        Academic peer review of a paper.
        Returns structured feedback with scores.
        """
        prompt = f"""Act as an academic peer reviewer. Provide a rigorous review.

PAPER CONTENT:
{content[:6000]}

REVIEW CRITERIA:
1. ORIGINALITY (1-10): Novel contribution to field?
2. METHODOLOGY (1-10): Sound research methods?
3. CLARITY (1-10): Well-written and organized?
4. EVIDENCE (1-10): Claims supported by citations?
5. SIGNIFICANCE (1-10): Important for the field?

Provide detailed review in JSON:
{{
    "summary": "1-2 sentence overview",
    "scores": {{
        "originality": X,
        "methodology": X,
        "clarity": X,
        "evidence": X,
        "significance": X,
        "overall": X
    }},
    "strengths": ["list of strong points"],
    "weaknesses": ["list of issues"],
    "major_revisions": ["critical changes needed"],
    "minor_revisions": ["small improvements"],
    "missing_citations": ["topics needing more references"],
    "verdict": "ACCEPT|MINOR_REVISIONS|MAJOR_REVISIONS|REJECT",
    "detailed_comments": "paragraph of feedback"
}}"""
        
        response = self._call_llm(prompt, max_tokens=2000)
        
        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                review = json.loads(json_match.group())
                return review
        except:
            pass
        
        return {
            "error": "Could not parse review",
            "raw_response": response[:500]
        }
    
    def critique_methodology(self, methodology_section: str) -> Dict:
        """Specific critique of methodology section."""
        
        prompt = f"""Critique this research methodology section.

METHODOLOGY:
{methodology_section}

Analyze:
1. Research design appropriateness
2. Sample size and selection
3. Data collection methods
4. Analysis techniques
5. Validity and reliability
6. Ethical considerations
7. Reproducibility

Output JSON with ratings (1-10) and specific feedback for each."""
        
        response = self._call_llm(prompt)
        
        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return {"raw_critique": response}
    
    # === REVISION ===
    
    def _revise_paper(self, content: str, review: Dict, verification: Dict) -> Dict:
        """Revise paper based on review and verification feedback."""
        
        issues = []
        if review.get("major_revisions"):
            issues.extend(review["major_revisions"])
        if review.get("minor_revisions"):
            issues.extend(review["minor_revisions"])
        if verification.get("unverified"):
            issues.extend([f"Unverified claim: {c}" for c in verification["unverified"][:5]])
        
        prompt = f"""Revise this academic paper based on reviewer feedback.

ORIGINAL PAPER:
{content[:5000]}

ISSUES TO ADDRESS:
{json.dumps(issues[:10], indent=2)}

REVIEW SCORES:
{json.dumps(review.get('scores', {}), indent=2)}

REVISION REQUIREMENTS:
1. Address each major issue
2. Replace [NEEDS_SOURCE] with proper hedging or remove claims
3. Improve clarity where noted
4. Strengthen evidence where weak
5. Maintain academic tone

Output the REVISED paper content:"""
        
        revised_content = self._call_llm(prompt, max_tokens=8000)
        
        return {
            "content": revised_content,
            "issues_addressed": len(issues),
            "word_count": len(revised_content.split())
        }
    
    def _finalize_paper(self, content: str, sources: List[Dict], 
                       paper_type: str) -> Dict:
        """Final formatting and reference list generation."""
        from .research_publisher import research_publisher
        
        # Generate references
        references = research_publisher.format_references(
            [{"authors": s.get("authors", []), "title": s["title"], 
              "year": s.get("published", "")[:4], "url": s.get("url", "")}
             for s in sources[:15]],
            style="apa"
        )
        
        final_content = content + "\n\n---\n\n## References\n\n" + references
        
        return {
            "content": final_content,
            "word_count": len(final_content.split()),
            "reference_count": len(sources),
            "format": paper_type
        }
    
    def _save_paper(self, topic: str, final: Dict) -> str:
        """Save final paper to file."""
        safe_name = re.sub(r'[^a-zA-Z0-9]', '_', topic)[:50]
        filename = f"paper_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = os.path.join(self.papers_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(final["content"])
        
        print(f"[Academic] Paper saved: {filepath}")
        return filepath
    
    def run(self, task: str) -> str:
        """Execute academic workflow task."""
        task_lower = task.lower()
        
        if "write paper" in task_lower or "full paper" in task_lower:
            result = self.write_paper(task)
            return f"Paper completed. Saved to: {result.get('saved_to', 'N/A')}\n\nReview: {result.get('stages', {}).get('review', {}).get('verdict', 'N/A')}"
        
        elif "review" in task_lower or "critique" in task_lower:
            review = self.review_paper(task)
            return json.dumps(review, indent=2)
        
        elif "plagiarism" in task_lower:
            check = self.check_plagiarism(task)
            return json.dumps(check, indent=2)
        
        elif "verify" in task_lower:
            result = self.verify_single_claim(task)
            return json.dumps(result, indent=2)
        
        else:
            # Default: write paper on topic
            result = self.write_paper(task)
            return f"Paper completed. Saved to: {result.get('saved_to', 'N/A')}"


# Singleton
academic_workflow = AcademicWorkflow()
