"""
Content Writer Agent for Jarvis v2
Generates blog posts, emails, social media, and marketing content.
"""
import os
import re
import json
from datetime import datetime
from typing import Dict, List, Optional
from .config import WORKSPACE_DIR, LM_STUDIO_URL
import requests


class ContentWriter:
    """
    AI-powered content generation for marketing and communication.
    
    Features:
    - Blog posts with SEO optimization
    - Email templates (cold outreach, follow-up, newsletter)
    - Social media (Twitter/X, LinkedIn, Instagram captions)
    - Tone control (professional, casual, persuasive, technical)
    - Content repurposing (blog → social threads)
    """
    
    TONES = {
        "professional": "formal, polished, authoritative",
        "casual": "friendly, conversational, approachable",
        "persuasive": "compelling, action-oriented, benefit-focused",
        "technical": "precise, detailed, expert-level",
        "witty": "clever, engaging, slightly humorous",
        "empathetic": "understanding, supportive, warm"
    }
    
    CONTENT_TYPES = {
        "blog": {"min_words": 500, "max_words": 2000},
        "email": {"min_words": 50, "max_words": 300},
        "twitter": {"max_chars": 280},
        "linkedin": {"min_words": 50, "max_words": 500},
        "instagram": {"max_chars": 2200},
        "newsletter": {"min_words": 200, "max_words": 800}
    }
    
    def __init__(self):
        self.content_dir = os.path.join(WORKSPACE_DIR, "content")
        os.makedirs(self.content_dir, exist_ok=True)
    
    def _call_llm(self, prompt: str, temperature: float = 0.7) -> str:
        """Call LLM for content generation."""
        try:
            response = requests.post(
                LM_STUDIO_URL,
                json={
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature,
                    "max_tokens": 2000
                },
                timeout=120
            )
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"[ContentWriter] LLM Error: {e}")
        return ""
    
    # === Blog Posts ===
    
    def write_blog(self, topic: str, keywords: List[str] = None,
                   tone: str = "professional", word_count: int = 1000,
                   include_outline: bool = True) -> Dict:
        """
        Generate a full blog post with SEO optimization.
        
        Args:
            topic: Main topic/title
            keywords: SEO keywords to include
            tone: Writing tone
            word_count: Target word count
            include_outline: Whether to generate outline first
        """
        print(f"[ContentWriter] Writing blog: {topic}")
        
        tone_desc = self.TONES.get(tone, self.TONES["professional"])
        keywords_str = ", ".join(keywords) if keywords else "none specified"
        
        # Generate outline first if requested
        outline = ""
        if include_outline:
            outline_prompt = f"""Create a detailed outline for a blog post about: {topic}

Include:
- Compelling headline options (3)
- Introduction hook
- 4-6 main sections with subpoints
- Conclusion with CTA

Keywords to include: {keywords_str}
"""
            outline = self._call_llm(outline_prompt, temperature=0.5)
        
        # Generate full blog
        prompt = f"""Write a comprehensive blog post about: {topic}

REQUIREMENTS:
- Tone: {tone_desc}
- Target word count: {word_count} words
- SEO keywords to include naturally: {keywords_str}
- Include a compelling headline
- Start with a hook
- Use subheadings (##)
- Include actionable takeaways
- End with a call-to-action

{f"OUTLINE TO FOLLOW:{chr(10)}{outline}" if outline else ""}

Write the full blog post in Markdown format."""

        content = self._call_llm(prompt, temperature=0.7)
        
        # Extract headline
        headline = topic
        headline_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if headline_match:
            headline = headline_match.group(1)
        
        # Save to file
        safe_topic = re.sub(r'[^a-zA-Z0-9]', '_', topic)[:40]
        timestamp = datetime.now().strftime('%Y%m%d')
        filename = f"blog_{safe_topic}_{timestamp}.md"
        filepath = os.path.join(self.content_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        word_count_actual = len(content.split())
        
        return {
            "type": "blog",
            "headline": headline,
            "content": content,
            "word_count": word_count_actual,
            "keywords": keywords,
            "tone": tone,
            "outline": outline,
            "saved_to": filepath
        }
    
    # === Email Generation ===
    
    def write_email(self, purpose: str, context: str = "",
                    recipient_type: str = "prospect", 
                    tone: str = "professional",
                    email_type: str = "cold_outreach") -> Dict:
        """
        Generate email content.
        
        Args:
            purpose: What the email should achieve
            context: Additional context (company, product, etc)
            recipient_type: prospect, customer, investor, partner
            tone: Writing tone
            email_type: cold_outreach, follow_up, newsletter, thank_you
        """
        print(f"[ContentWriter] Writing {email_type} email")
        
        tone_desc = self.TONES.get(tone, self.TONES["professional"])
        
        type_guidelines = {
            "cold_outreach": "Short (under 150 words), personalized hook, clear value prop, soft CTA",
            "follow_up": "Brief, reference previous contact, provide new value, clear next step",
            "newsletter": "Engaging subject, scannable format, multiple value points, single CTA",
            "thank_you": "Genuine appreciation, specific mention of what you're thankful for, future-focused"
        }
        
        guidelines = type_guidelines.get(email_type, type_guidelines["cold_outreach"])
        
        prompt = f"""Write a {email_type} email.

PURPOSE: {purpose}
RECIPIENT TYPE: {recipient_type}
ADDITIONAL CONTEXT: {context}

TONE: {tone_desc}
GUIDELINES: {guidelines}

Format:
SUBJECT: [compelling subject line]
---
[email body]
---
SIGNATURE SUGGESTION: [brief signature]

Write the email now."""

        result = self._call_llm(prompt, temperature=0.6)
        
        # Parse subject
        subject = ""
        subject_match = re.search(r'SUBJECT:\s*(.+?)(?:\n|---)', result)
        if subject_match:
            subject = subject_match.group(1).strip()
        
        # Parse body
        body = result
        body_match = re.search(r'---\n([\s\S]+?)(?:\n---|\Z)', result)
        if body_match:
            body = body_match.group(1).strip()
        
        return {
            "type": "email",
            "email_type": email_type,
            "subject": subject,
            "body": body,
            "full_content": result,
            "tone": tone
        }
    
    # === Social Media ===
    
    def write_social(self, platform: str, topic: str, 
                     context: str = "", tone: str = "casual",
                     include_hashtags: bool = True,
                     thread_length: int = 1) -> Dict:
        """
        Generate social media content.
        
        Args:
            platform: twitter, linkedin, instagram
            topic: What to post about
            context: Additional context
            tone: Writing tone
            include_hashtags: Whether to add hashtags
            thread_length: For Twitter threads (1 = single tweet)
        """
        print(f"[ContentWriter] Writing {platform} post")
        
        tone_desc = self.TONES.get(tone, self.TONES["casual"])
        
        platform_guidelines = {
            "twitter": f"Max 280 chars per tweet. {'Create a thread of ' + str(thread_length) + ' tweets.' if thread_length > 1 else 'Single tweet.'} Engaging, punchy, hook at start.",
            "linkedin": "Professional but personable. 50-150 words ideal. Line breaks for readability. End with question or CTA.",
            "instagram": "Engaging caption up to 2200 chars. Storytelling approach. Emoji-friendly. CTA at end."
        }
        
        guidelines = platform_guidelines.get(platform, platform_guidelines["twitter"])
        
        prompt = f"""Write a {platform} post about: {topic}

CONTEXT: {context}
TONE: {tone_desc}
GUIDELINES: {guidelines}
{"Include 3-5 relevant hashtags at the end." if include_hashtags else "No hashtags."}

{"Format as numbered tweets (1/, 2/, etc) for the thread." if platform == "twitter" and thread_length > 1 else ""}

Write the post now."""

        content = self._call_llm(prompt, temperature=0.8)
        
        # Extract hashtags
        hashtags = re.findall(r'#\w+', content)
        
        return {
            "type": "social",
            "platform": platform,
            "content": content,
            "hashtags": hashtags,
            "char_count": len(content),
            "tone": tone
        }
    
    # === Content Repurposing ===
    
    def repurpose(self, original_content: str, 
                  from_type: str, to_types: List[str]) -> Dict:
        """
        Repurpose content from one format to others.
        
        Args:
            original_content: Source content
            from_type: blog, email, social
            to_types: List of target formats
        """
        print(f"[ContentWriter] Repurposing from {from_type} to {to_types}")
        
        results = {}
        
        for target in to_types:
            prompt = f"""Repurpose this {from_type} content into a {target} format.

ORIGINAL CONTENT:
{original_content[:3000]}

TARGET FORMAT: {target}
REQUIREMENTS:
- Maintain the core message
- Adapt tone and length for the platform
- Make it feel native to {target}

Write the repurposed content."""

            results[target] = {
                "content": self._call_llm(prompt, temperature=0.7),
                "source": from_type
            }
        
        return {
            "type": "repurposed",
            "original_type": from_type,
            "results": results
        }
    
    # === Content Ideas ===
    
    def generate_ideas(self, topic: str, content_type: str = "blog",
                       count: int = 10) -> Dict:
        """Generate content ideas for a topic."""
        print(f"[ContentWriter] Generating {count} {content_type} ideas for: {topic}")
        
        prompt = f"""Generate {count} compelling {content_type} content ideas about: {topic}

For each idea provide:
1. Title/Headline
2. Hook (1 sentence)
3. Key angle/unique perspective

Make ideas varied - some educational, some controversial, some personal, some data-driven.

Format as numbered list."""

        ideas = self._call_llm(prompt, temperature=0.9)
        
        return {
            "type": "ideas",
            "topic": topic,
            "content_type": content_type,
            "ideas": ideas,
            "count": count
        }
    def run(self, task: str) -> str:
        """
        Execute a content writing task.
        This is the main entry point expected by the autonomous executor.
        
        Args:
            task: Description of content to write
            
        Returns:
            Generated content as a string
        """
        task_lower = task.lower()
        
        # Detect content type from task
        if "blog" in task_lower or "article" in task_lower or "post" in task_lower:
            result = self.write_blog(task)
            return result.get("content", "")
        
        elif "email" in task_lower:
            email_type = "cold_outreach"
            if "follow" in task_lower:
                email_type = "follow_up"
            elif "newsletter" in task_lower:
                email_type = "newsletter"
            elif "thank" in task_lower:
                email_type = "thank_you"
            result = self.write_email(task, email_type=email_type)
            return result.get("full_content", "")
        
        elif any(p in task_lower for p in ["twitter", "linkedin", "instagram", "social"]):
            platform = "linkedin"  # default
            if "twitter" in task_lower or "tweet" in task_lower:
                platform = "twitter"
            elif "instagram" in task_lower:
                platform = "instagram"
            result = self.write_social(platform, task)
            return result.get("content", "")
        
        elif "idea" in task_lower:
            result = self.generate_ideas(task)
            return result.get("ideas", "")
        
        else:
            # Default to blog-style content
            result = self.write_blog(task)
            return result.get("content", "")


# Singleton
content_writer = ContentWriter()
