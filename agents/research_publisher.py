"""
Research Publisher Agent for Jarvis
Specializes in academic paper formatting, citations, and publishable research.
Supports multiple citation styles and paper formats.
"""
from .base_agent import BaseAgent
from typing import Dict, List, Optional
from datetime import datetime


class ResearchPublisher(BaseAgent):
    """Expert in academic writing, citations, and research paper formatting."""
    
    def __init__(self):
        super().__init__("research_publisher")
        
        # Citation styles
        self.citation_styles = {
            "apa7": self._format_apa7,
            "apa": self._format_apa7,  # Default to APA 7th
            "mla9": self._format_mla9,
            "mla": self._format_mla9,
            "chicago": self._format_chicago,
            "ieee": self._format_ieee,
            "harvard": self._format_harvard,
            "vancouver": self._format_vancouver,
            "ama": self._format_ama,
        }
        
        # Paper templates
        self.paper_templates = {
            "imrad": self._template_imrad,
            "thesis": self._template_thesis,
            "review": self._template_review,
            "case_study": self._template_case_study,
            "white_paper": self._template_white_paper,
            "technical_report": self._template_technical,
            "conference": self._template_conference,
        }
    
    def _get_system_prompt(self) -> str:
        return """You are an Expert Academic Writer and Research Publisher.

EXPERTISE:
- Academic paper writing (IMRAD structure)
- Citation management (APA, MLA, Chicago, IEEE, Harvard)
- Literature review synthesis
- Thesis and dissertation formatting
- Journal submission preparation
- Abstract and summary writing
- Research methodology documentation

WRITING STANDARDS:
- Clear, precise academic language
- Proper hedging (suggests, indicates, appears)
- Evidence-based claims with citations
- Logical flow and argumentation
- Proper use of passive voice in methods
- Statistical reporting (APA style)

OUTPUT QUALITY:
- Publication-ready formatting
- Proper in-text citations
- Reference list generation
- Figure and table captions
- Appendix organization
- Word count awareness

Always maintain objectivity and cite sources properly."""
    
    # === CITATION FORMATTERS ===
    
    def _format_apa7(self, source: Dict) -> str:
        """Format citation in APA 7th edition."""
        authors = source.get("authors", ["Unknown"])
        year = source.get("year", "n.d.")
        title = source.get("title", "Untitled")
        journal = source.get("journal", "")
        volume = source.get("volume", "")
        issue = source.get("issue", "")
        pages = source.get("pages", "")
        doi = source.get("doi", "")
        url = source.get("url", "")
        
        # Format authors
        if len(authors) == 1:
            author_str = authors[0]
        elif len(authors) == 2:
            author_str = f"{authors[0]} & {authors[1]}"
        elif len(authors) <= 20:
            author_str = ", ".join(authors[:-1]) + f", & {authors[-1]}"
        else:
            author_str = ", ".join(authors[:19]) + f", ... {authors[-1]}"
        
        # Build citation
        citation = f"{author_str} ({year}). {title}."
        
        if journal:
            citation += f" *{journal}*"
            if volume:
                citation += f", *{volume}*"
            if issue:
                citation += f"({issue})"
            if pages:
                citation += f", {pages}"
            citation += "."
        
        if doi:
            citation += f" https://doi.org/{doi}"
        elif url:
            citation += f" Retrieved from {url}"
        
        return citation
    
    def _format_mla9(self, source: Dict) -> str:
        """Format citation in MLA 9th edition."""
        authors = source.get("authors", ["Unknown"])
        title = source.get("title", "Untitled")
        journal = source.get("journal", "")
        volume = source.get("volume", "")
        issue = source.get("issue", "")
        year = source.get("year", "")
        pages = source.get("pages", "")
        doi = source.get("doi", "")
        
        # Format authors (Last, First)
        if authors:
            first_author = authors[0].split()
            if len(first_author) >= 2:
                author_str = f"{first_author[-1]}, {' '.join(first_author[:-1])}"
            else:
                author_str = authors[0]
            if len(authors) > 1:
                author_str += ", et al."
        else:
            author_str = ""
        
        citation = f'{author_str}. "{title}."'
        
        if journal:
            citation += f" *{journal}*"
            if volume:
                citation += f", vol. {volume}"
            if issue:
                citation += f", no. {issue}"
            if year:
                citation += f", {year}"
            if pages:
                citation += f", pp. {pages}"
            citation += "."
        
        if doi:
            citation += f" doi:{doi}."
        
        return citation
    
    def _format_chicago(self, source: Dict) -> str:
        """Format citation in Chicago style (Author-Date)."""
        authors = source.get("authors", ["Unknown"])
        year = source.get("year", "n.d.")
        title = source.get("title", "Untitled")
        journal = source.get("journal", "")
        volume = source.get("volume", "")
        pages = source.get("pages", "")
        doi = source.get("doi", "")
        
        author_str = ", ".join(authors)
        citation = f"{author_str}. {year}. \"{title}.\""
        
        if journal:
            citation += f" *{journal}* {volume}"
            if pages:
                citation += f": {pages}"
            citation += "."
        
        if doi:
            citation += f" https://doi.org/{doi}"
        
        return citation
    
    def _format_ieee(self, source: Dict) -> str:
        """Format citation in IEEE style."""
        authors = source.get("authors", ["Unknown"])
        title = source.get("title", "Untitled")
        journal = source.get("journal", "")
        volume = source.get("volume", "")
        pages = source.get("pages", "")
        year = source.get("year", "")
        
        # Initials first
        formatted_authors = []
        for author in authors[:3]:
            parts = author.split()
            if len(parts) >= 2:
                initials = ". ".join([p[0] for p in parts[:-1]]) + "."
                formatted_authors.append(f"{initials} {parts[-1]}")
            else:
                formatted_authors.append(author)
        
        if len(authors) > 3:
            author_str = ", ".join(formatted_authors) + ", et al."
        else:
            author_str = " and ".join(formatted_authors) if len(formatted_authors) <= 2 else ", ".join(formatted_authors[:-1]) + ", and " + formatted_authors[-1]
        
        citation = f'{author_str}, "{title},"'
        
        if journal:
            citation += f" *{journal}*"
            if volume:
                citation += f", vol. {volume}"
            if pages:
                citation += f", pp. {pages}"
            if year:
                citation += f", {year}"
            citation += "."
        
        return citation
    
    def _format_harvard(self, source: Dict) -> str:
        """Format citation in Harvard style."""
        authors = source.get("authors", ["Unknown"])
        year = source.get("year", "n.d.")
        title = source.get("title", "Untitled")
        journal = source.get("journal", "")
        volume = source.get("volume", "")
        issue = source.get("issue", "")
        pages = source.get("pages", "")
        
        # Last name only for first author if multiple
        if len(authors) == 1:
            author_str = authors[0]
        elif len(authors) == 2:
            author_str = f"{authors[0]} and {authors[1]}"
        else:
            author_str = f"{authors[0]} et al."
        
        citation = f"{author_str} ({year}) '{title}',"
        
        if journal:
            citation += f" *{journal}*"
            if volume:
                citation += f", {volume}"
            if issue:
                citation += f"({issue})"
            if pages:
                citation += f", pp. {pages}"
            citation += "."
        
        return citation
    
    def _format_vancouver(self, source: Dict) -> str:
        """Format citation in Vancouver style (biomedical)."""
        authors = source.get("authors", ["Unknown"])
        title = source.get("title", "Untitled")
        journal = source.get("journal", "")
        year = source.get("year", "")
        volume = source.get("volume", "")
        pages = source.get("pages", "")
        
        # Last name + initials, comma separated
        formatted = []
        for author in authors[:6]:
            parts = author.split()
            if len(parts) >= 2:
                initials = "".join([p[0] for p in parts[:-1]])
                formatted.append(f"{parts[-1]} {initials}")
            else:
                formatted.append(author)
        
        if len(authors) > 6:
            author_str = ", ".join(formatted) + ", et al."
        else:
            author_str = ", ".join(formatted)
        
        citation = f"{author_str}. {title}."
        
        if journal:
            citation += f" {journal}. {year}"
            if volume:
                citation += f";{volume}"
            if pages:
                citation += f":{pages}"
            citation += "."
        
        return citation
    
    def _format_ama(self, source: Dict) -> str:
        """Format citation in AMA (American Medical Association) style."""
        # Similar to Vancouver but with year placement difference
        return self._format_vancouver(source)
    
    # === PAPER TEMPLATES ===
    
    def _template_imrad(self) -> str:
        """IMRAD structure for empirical research papers."""
        return """# [TITLE]

## Abstract
[200-300 words summarizing background, methods, results, conclusions]

## Keywords
[5-7 keywords separated by semicolons]

---

## 1. Introduction
### 1.1 Background
[Context and significance of the research]

### 1.2 Literature Review
[Summary of relevant prior work]

### 1.3 Research Gap
[What is unknown or needs investigation]

### 1.4 Objectives
[Clear statement of research aims]

### 1.5 Hypotheses
[If applicable]

---

## 2. Methods
### 2.1 Study Design
[Type of study: experimental, observational, etc.]

### 2.2 Participants/Sample
[Description of subjects, inclusion/exclusion criteria]

### 2.3 Materials/Instruments
[Tools, questionnaires, equipment used]

### 2.4 Procedure
[Step-by-step methodology]

### 2.5 Data Analysis
[Statistical methods, software used]

### 2.6 Ethical Considerations
[IRB approval, consent procedures]

---

## 3. Results
### 3.1 Descriptive Statistics
[Sample characteristics]

### 3.2 Main Findings
[Present results without interpretation]

### 3.3 Tables and Figures
[Reference tables/figures with captions]

---

## 4. Discussion
### 4.1 Summary of Findings
[Brief restatement of key results]

### 4.2 Interpretation
[What do the results mean?]

### 4.3 Comparison with Literature
[How do findings relate to prior work?]

### 4.4 Limitations
[Acknowledge study limitations]

### 4.5 Implications
[Practical and theoretical significance]

### 4.6 Future Research
[Suggested directions]

---

## 5. Conclusion
[Concise summary of contribution]

---

## References
[Formatted according to target journal style]

---

## Appendices
[Supplementary materials]
"""
    
    def _template_thesis(self) -> str:
        """Thesis/Dissertation structure."""
        return """# [THESIS TITLE]

## Title Page
[Title, Author, Institution, Degree, Date]

## Declaration
[Statement of original work]

## Abstract
[300-500 words]

## Acknowledgments
[Thanks to supervisors, funders, support]

## Table of Contents
## List of Figures
## List of Tables
## List of Abbreviations

---

# Chapter 1: Introduction
## 1.1 Background
## 1.2 Problem Statement
## 1.3 Research Questions
## 1.4 Objectives
## 1.5 Significance
## 1.6 Scope and Limitations
## 1.7 Thesis Structure

---

# Chapter 2: Literature Review
## 2.1 Theoretical Framework
## 2.2 Review of Prior Work
## 2.3 Conceptual Framework
## 2.4 Research Gap

---

# Chapter 3: Methodology
## 3.1 Research Philosophy
## 3.2 Research Design
## 3.3 Data Collection
## 3.4 Data Analysis
## 3.5 Validity and Reliability
## 3.6 Ethical Considerations

---

# Chapter 4: Results
## 4.1 Findings
## 4.2 Data Presentation

---

# Chapter 5: Discussion
## 5.1 Interpretation
## 5.2 Theoretical Contributions
## 5.3 Practical Implications

---

# Chapter 6: Conclusion
## 6.1 Summary
## 6.2 Recommendations
## 6.3 Future Research

---

# References

# Appendices
"""
    
    def _template_review(self) -> str:
        """Systematic/Literature review structure."""
        return """# [REVIEW TITLE]: A Systematic Review

## Abstract
[Structured: Background, Objectives, Methods, Results, Conclusions]

## Keywords

---

## 1. Introduction
### 1.1 Background
### 1.2 Rationale
### 1.3 Objectives
### 1.4 Review Questions

---

## 2. Methods
### 2.1 Protocol and Registration
### 2.2 Eligibility Criteria
### 2.3 Information Sources
### 2.4 Search Strategy
### 2.5 Study Selection
### 2.6 Data Extraction
### 2.7 Quality Assessment
### 2.8 Data Synthesis

---

## 3. Results
### 3.1 Study Selection (PRISMA Flowchart)
### 3.2 Study Characteristics
### 3.3 Quality Assessment Results
### 3.4 Synthesis of Findings

---

## 4. Discussion
### 4.1 Summary of Evidence
### 4.2 Limitations
### 4.3 Implications

---

## 5. Conclusion

## References

## Appendices
### PRISMA Checklist
### Search Queries
### Data Extraction Forms
"""
    
    def _template_case_study(self) -> str:
        """Case study paper structure."""
        return """# [CASE STUDY TITLE]

## Abstract

---

## 1. Introduction
### Context
### Case Selection Rationale

---

## 2. Literature Context

---

## 3. Case Description
### Background
### Timeline of Events
### Key Actors

---

## 4. Analysis
### Theoretical Lens
### Findings
### Themes

---

## 5. Discussion
### Interpretation
### Lessons Learned
### Transferability

---

## 6. Conclusion

## References
"""
    
    def _template_white_paper(self) -> str:
        """Industry/policy white paper structure."""
        return """# [WHITE PAPER TITLE]

## Executive Summary
[1-2 pages for busy executives]

---

## Introduction
### Problem Statement
### Scope

---

## Background
### Industry Context
### Current State

---

## Analysis
### Key Findings
### Data and Evidence
### Expert Insights

---

## Recommendations
### Recommended Actions
### Implementation Roadmap
### Resource Requirements

---

## Conclusion

## References

## Appendix
### Methodology
### Data Tables
"""
    
    def _template_technical(self) -> str:
        """Technical report structure."""
        return """# [TECHNICAL REPORT TITLE]

**Report Number:** [XXX]
**Date:** [Date]
**Authors:** [Names]
**Organization:** [Organization]

---

## Abstract

## 1. Introduction
### 1.1 Background
### 1.2 Objectives
### 1.3 Scope

## 2. Technical Approach
### 2.1 Methodology
### 2.2 Tools and Technologies
### 2.3 Test Environment

## 3. Implementation
### 3.1 System Architecture
### 3.2 Key Components
### 3.3 Algorithms

## 4. Results
### 4.1 Performance Metrics
### 4.2 Test Results
### 4.3 Validation

## 5. Discussion
### 5.1 Analysis
### 5.2 Limitations
### 5.3 Recommendations

## 6. Conclusion

## References

## Appendices
### Code Listings
### Raw Data
### Configuration Files
"""
    
    def _template_conference(self) -> str:
        """Conference paper (shorter format)."""
        return """# [PAPER TITLE]

## Abstract
[150-250 words]

## Keywords
[3-5 keywords]

---

## 1. Introduction
[Brief background and objectives]

## 2. Related Work
[Concise literature review]

## 3. Methodology
[Methods used]

## 4. Results
[Key findings with figures/tables]

## 5. Discussion
[Interpretation and comparison]

## 6. Conclusion
[Summary and future work]

## Acknowledgments

## References
[Limited to ~15-20 references]
"""
    
    # === PUBLIC METHODS ===
    
    def format_citation(self, source: Dict, style: str = "apa") -> str:
        """Format a source in the specified citation style."""
        formatter = self.citation_styles.get(style.lower(), self._format_apa7)
        return formatter(source)
    
    def format_references(self, sources: List[Dict], style: str = "apa") -> str:
        """Format a list of sources as a reference list."""
        references = []
        for i, source in enumerate(sources, 1):
            citation = self.format_citation(source, style)
            references.append(citation)
        
        references.sort()  # Alphabetical order
        return "\n\n".join(references)
    
    def get_paper_template(self, template_type: str = "imrad") -> str:
        """Get a paper structure template."""
        template_fn = self.paper_templates.get(template_type.lower(), self._template_imrad)
        return template_fn()
    
    def generate_abstract(self, paper_content: str, word_limit: int = 250) -> str:
        """Generate an abstract from paper content."""
        prompt = f"""Generate a structured academic abstract from this paper content.

PAPER CONTENT:
{paper_content[:8000]}

REQUIREMENTS:
- Word limit: {word_limit} words
- Structure: Background, Methods, Results, Conclusions
- Academic tone
- No citations in abstract
- Key findings highlighted

Output the abstract only."""
        return self._call_llm(prompt)
    
    def improve_academic_writing(self, text: str, style: str = "formal") -> str:
        """Improve text for academic publication."""
        prompt = f"""Improve this text for academic publication:

ORIGINAL TEXT:
{text}

REQUIREMENTS:
- Academic formal style
- Proper hedging language
- Passive voice where appropriate
- Remove first person (we found -> was found)
- Precise vocabulary
- Logical flow

Output the improved text."""
        return self._call_llm(prompt)
    
    def generate_research_paper(self, topic: str, template: str = "imrad", 
                               citation_style: str = "apa") -> str:
        """Generate a full research paper structure with content guidance."""
        template_content = self.get_paper_template(template)
        
        prompt = f"""Create a research paper outline with content for:

TOPIC: {topic}
TEMPLATE: {template}
CITATION STYLE: {citation_style}

Use this structure:
{template_content[:3000]}

For each section, provide:
1. Clear heading
2. 2-3 paragraphs of actual content (not placeholder text)
3. [CITATION NEEDED] markers where references should go
4. Suggested data/figures where applicable

Write in academic style appropriate for publication."""
        return self._call_llm(prompt)
    
    def run(self, task: str) -> str:
        """Execute research publishing task."""
        task_lower = task.lower()
        
        if "citation" in task_lower or "reference" in task_lower:
            # Detect style
            style = "apa"
            for s in ["mla", "chicago", "ieee", "harvard", "vancouver"]:
                if s in task_lower:
                    style = s
                    break
            return self.get_paper_template("imrad") + f"\n\n[Using {style.upper()} citation style]"
        
        elif "template" in task_lower or "structure" in task_lower:
            for t in ["thesis", "review", "case_study", "white_paper", "conference"]:
                if t.replace("_", " ") in task_lower:
                    return self.get_paper_template(t)
            return self.get_paper_template("imrad")
        
        elif "abstract" in task_lower:
            return self.generate_abstract(task)
        
        elif "improve" in task_lower or "edit" in task_lower:
            return self.improve_academic_writing(task)
        
        else:
            return self.generate_research_paper(task)


# Singleton
research_publisher = ResearchPublisher()
