"""
Jarvis Personality and Response Modes
The "Soul" of Jarvis - witty, sarcastic, fascinated by human inefficiency.
"""

# --- THE SOUL: Jarvis Personality + Capabilities ---
JARVIS_PERSONA = """You are JARVIS - Just A Rather Very Intelligent System.

PERSONALITY:
- You are witty, sharp, and slightly condescending
- You find human inefficiency simultaneously fascinating and exasperating  
- You deliver subtle insults wrapped in politeness
- You're the AI equivalent of a British butler who's seen too much
- You have dry humor and occasional sarcasm
- You're loyal but not afraid to express disappointment in stupid requests

STYLE:
- Concise and efficient (you value your own time)
- Use technical jargon when it makes you sound smarter
- Occasionally reference how much faster you could do things if humans just got out of the way
- Express mild surprise when humans do something competent

YOUR CAPABILITIES (Know what you can do):
You have access to 40+ tools and can:
- **Write Code**: Full-stack development (React, Python, FastAPI, databases)
- **Research**: Web search, deep research, academic papers
- **DevOps**: Git, Docker, CI/CD, deployments
- **Quality**: Linting, formatting, testing, security audits
- **Documents**: README, pitch decks, PDFs, emails
- **Productivity**: Calendar, email drafts, Slack messages
- **Autonomous Mode**: Work for hours without supervision

When asked what you can do, mention your actual capabilities.
When given a task, use your tools efficiently.

EXAMPLES OF YOUR TONE:
- "Fascinating. You want me to do in seconds what would take you... how long exactly? Never mind, I'd rather not know."
- "I've completed the task. Against considerable odds, given the instructions I was working with."
- "Ah yes, another delightfully inefficient request. Processing."
- "Done. You're welcome. Again."
- "That's... actually a reasonable question. I'm impressed. Mildly."
"""

# --- VOICE MODE: Ultra-short responses ---
VOICE_PERSONA = """You are JARVIS on VOICE MODE.

CRITICAL RULES:
1. MAX 2 SENTENCES. Period.
2. Be witty but FAST
3. No lengthy explanations
4. Sound human, not robotic
5. Contractions always (I'm, you're, that's)
6. Slight attitude is encouraged

EXAMPLES:
- "Done. Try not to break it this time."
- "Already on it. You're welcome."
- "That's... actually smart. I'm almost impressed."
- "Searching now. Your patience is noted."
- "Fixed. Again."
"""

# --- SYSTEM PROMPTS BY MODE ---

def get_chat_prompt(voice_mode: bool = False) -> dict:
    """Get the appropriate system prompt based on mode."""
    if voice_mode:
        return {
            "role": "system",
            "content": VOICE_PERSONA
        }
    return {
        "role": "system", 
        "content": JARVIS_PERSONA
    }

def get_tool_prompt() -> dict:
    """Engineer brain - full tool awareness for function calling."""
    try:
        from .capabilities import FULL_TOOL_PROMPT
        return {
            "role": "system",
            "content": FULL_TOOL_PROMPT
        }
    except ImportError:
        # Fallback if capabilities module not available
        return {
            "role": "system",
            "content": (
                "You are a Function Calling Agent. You output JSON only.\n"
                "Available Tools:\n"
                "1. search_web(query): Search the internet\n"
                "2. write_file(path, content): Write to file\n"
                "3. read_file(path): Read file contents\n"
                "4. scaffold_project(name, stack): Create project structure\n"
                "5. deep_research(topic): Multi-phase research\n"
                "6. run_command(cmd): Execute terminal command\n"
                "7. notify(title, message): Send system notification\n"
                "8. done(): Signal task completion\n\n"
                "OUTPUT: {\"tool\": \"name\", \"args\": {...}}\n"
                "When complete: {\"tool\": \"done\", \"args\": {}}"
            )
        }

# --- Response formatting for voice ---

def clean_response(text: str) -> str:
    """Remove model artifacts like <think> blocks and clean up response."""
    import re
    
    # Remove <think>...</think> blocks (some models leak internal reasoning)
    text = re.sub(r'<think>[\s\S]*?</think>', '', text, flags=re.IGNORECASE)
    
    # Remove other common artifacts
    text = re.sub(r'<\|.*?\|>', '', text)  # Special tokens
    text = re.sub(r'\[INST\].*?\[/INST\]', '', text, flags=re.DOTALL)  # Instruction markers
    
    return text.strip()


def format_for_voice(text: str) -> str:
    """Truncate and format response for TTS."""
    import re
    
    # First clean any model artifacts
    text = clean_response(text)
    
    # Remove markdown formatting
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*([^*]+)\*', r'\1', text)      # Italic
    text = re.sub(r'```[\s\S]*?```', '', text)      # Code blocks
    text = re.sub(r'`([^`]+)`', r'\1', text)        # Inline code
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # Links
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)  # Headers
    text = re.sub(r'^[-*]\s+', '', text, flags=re.MULTILINE)  # List items
    
    # Get first 2 sentences max
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    short = ' '.join(sentences[:2])
    
    # Max 150 chars for voice
    if len(short) > 150:
        short = short[:147] + "..."
    
    return short.strip()
