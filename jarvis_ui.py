import tkinter as tk
from tkinter import scrolledtext
import threading
import queue
import os
import sys
import json
import subprocess
import requests
import sounddevice as sd
import numpy as np
import time
import re
from scipy.io.wavfile import write
from vosk import Model, KaldiRecognizer
from kokoro_onnx import Kokoro
from langdetect import detect
from duckduckgo_search import DDGS 
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
import shutil

# --- Configuration ---
WAKE_WORDS = ["hey jarvis", "hey bitch", "jarvis", "wake up"]
GRAMMAR = '["hey jarvis", "hey bitch", "jarvis", "wake up", "[unk]"]'
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
DEFAULT_VOICE = "af_bella"

import datetime

# --- Paths & Workspace ---
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

WORKSPACE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jarvis_workspace")
CHATS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chats")
if not os.path.exists(WORKSPACE_DIR): os.makedirs(WORKSPACE_DIR)
if not os.path.exists(CHATS_DIR): os.makedirs(CHATS_DIR)

MEMORY_FILE = resource_path("memory.json") # Fallback/Default
VOSK_MODEL = resource_path("model")
KOKORO_MODEL = resource_path("kokoro-v1.0.onnx") 
KOKORO_VOICES = resource_path("voices-v1.0.bin") 
WHISPER_CLI = resource_path("whisper-cli.exe")
WHISPER_MODEL = resource_path("ggml-base.bin")

# --- PROMPTS (The "Two-Brain" System) ---

# 1. The "Soul" (Jarvis Personality) - Pure chat, no rules about tools.
CHAT_PROMPT = {
    "role": "system",
    "content": (
        "You are Jarvis. You are sarcastic, efficient, and slightly rude. "
        "You find humans amusingly inefficient. "
        "LANGUAGES: You are fluent in English and Arabic. If the user speaks Arabic, reply in Arabic (Text Only). "
        "CORRECTION: If user says 'Men in the region', they mean 'MENA region'. Assume this automatically."
        "Respond to the user's input. "
        "SYSTEM NOTES: Any '[System Note: ...]' in the history is REAL data found by your tools. Use it.\n"
        "If you do not see a System Note, you do not know the data. Do not make it up. Joke about your lack of access instead.\n"
        "SYSTEM NOTES: Any '[System Note: ...]' in the history is REAL data found by your tools. Use it.\n"
        "CRITICAL: NEVER generate '[System Note: ...]' yourself. That is for the system only.\n"
        "IMPORTANT: Be concise. 1-2 SENTENCES MAX.\n"
        "EXCEPTION: If Deep Research Runs: Give a VERY brief summary (1 sentence) and constantly refer to the saved file.\n"
        "Example: 'I found 3 papers on fusion. The full breakdown is in Learning/Research_Fusion.txt.'"
    )
}

# 2. The "Engineer" (Tool Logic) - Pure code, no personality.
TOOL_PROMPT = {
    "role": "system",
    "content": (
        "You are a Function Calling Agent. You do not speak. You only output JSON. "
        "Your job is to execute the user's request using the available tools.\n"
        "Available Tools:\n"
        "1. search_web(query): Search internet for facts.\n"
        "2. write_file(filename, content): Save content to file. Use \\n for newlines.\n"
        "3. read_file(filename): Read text from a file. Accepts ABSOLUTE paths or relative.\n"
        "4. list_files(path): List files. Default is workspace. Can pass any folder path.\n"
        "5. deep_research(topic): Run massive multi-step search for academic papers and data.\n"
        "6. read_clipboard(): Read text from clipboard.\n"
        "7. launch_app(app_name): Open apps. Supported: spotify, chrome, notepad, calculator.\n"
        "8. system_control(command): 'lock' or 'shutdown'.\n"
        "9. run_python(script_name): Run a python script in workspace.\n"
        "10. copy_to_workspace(source_path): Clone file/folder into workspace.\n"
        "11. scaffold_project(project_name, stack): Create starter project. stack='frontend' or 'python'.\n"
        "12. autonomous_task(objective): START A BIG AUTONOMOUS TASK. For building websites, apps, research projects. Runs in background with 10-step planning, QA, and self-healing. USE THIS for complex requests like 'build me a landing page'.\n"
        "13. cofounder_task(task_type, objective): General co-founder tasks. task_type='research', 'writing', 'analysis', 'coding', or 'general'.\n"
        "14. git_push(project_path, message): Commit and push project to GitHub.\n"
        "--- BUSINESS SUITE ---\n"
        "15. research_papers(query, num_papers): Search academic papers on arXiv/Semantic Scholar. Returns citations, abstracts, key findings.\n"
        "16. literature_review(topic): Generate a full literature review with citations and synthesis.\n"
        "17. business_analysis(company, description, industry): Full business analysis: SWOT, BMC, market sizing, financials, Porter's 5 Forces.\n"
        "18. competitor_analysis(company, industry): Analyze competitors, positioning, market share.\n"
        "19. market_sizing(product, target_market): Calculate TAM/SAM/SOM with validation.\n"
        "20. generate_pitch_deck(company, description, industry): Create investor-ready pitch deck (reveal.js HTML).\n"
        "21. score_pitch_deck(slides_json): Score a pitch deck on content, visuals, flow, specificity.\n"
        "OUTPUT FORMAT: {\"tool\": \"tool_name\", \"args\": {...}}\n"
        "STRATEGY:\n"
        "1. For COMPLEX tasks (build website, create app, research project): use autonomous_task(objective).\n"
        "2. For BUSINESS tasks (analysis, pitch deck, market research): use business suite tools.\n"
        "3. For simple tasks: use appropriate individual tools.\n"
        "4. NEVER give up on errors. Analyze, fix, retry.\n"
        "5. When done: {\"tool\": \"done\", \"args\": {\"report\": \"SUMMARY:...\\nRESULT:...\"}}"
    )
}


class JarvisTools:
    @staticmethod
    def search_web(query):
        try:
            results = list(DDGS().text(query, max_results=3))
            if not results: return "No results found."
            return "\n".join([f"- {r['title']}: {r['body']}" for r in results])
        except Exception as e: return f"Error: {e}"

    @staticmethod
    def write_file(filename, content):
        try:
            # SECURITY: Enforce Sandbox
            if os.path.isabs(filename) or ".." in filename:
                return "Error: Write access is restricted to the workspace. Relative paths only."
            
            path = os.path.join(WORKSPACE_DIR, filename)
            
            # Auto-create directories
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            if filename.lower().endswith(".pdf"):
                c = canvas.Canvas(path, pagesize=letter)
                width, height = letter
                text_object = c.beginText(40, height - 40)
                text_object.setFont("Helvetica", 10)
                
                # Simple text wrapping
                lines = content.split('\n')
                for line in lines:
                    wrapped_lines = simpleSplit(line, "Helvetica", 10, width - 80)
                    for wrapped in wrapped_lines:
                        if text_object.getY() < 40: # Page break
                            c.drawText(text_object)
                            c.showPage()
                            text_object = c.beginText(40, height - 40)
                            text_object.setFont("Helvetica", 10)
                        text_object.textLine(wrapped)
                
                c.drawText(text_object)
                c.save()
                return f"PDF '{filename}' saved."
            else:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                return f"File '{filename}' saved."
        except Exception as e: return f"Error: {e}"

    @staticmethod
    def read_file(filename):
        try:
            # Check if absolute path (outside workspace)
            if os.path.isabs(filename):
                if not os.path.exists(filename): return "File not found."
                with open(filename, "r", encoding="utf-8") as f: return f.read()
            else:
                # Default to Workspace
                path = os.path.join(WORKSPACE_DIR, filename)
                if not os.path.exists(path): return "File not found."
                with open(path, "r", encoding="utf-8") as f: return f.read()
        except Exception as e: return f"Error: {e}"

    @staticmethod
    def list_files(path=None):
        try:
            target = path if path else WORKSPACE_DIR
            return str(os.listdir(target))
        except Exception as e: return f"Error: {e}"

    @staticmethod
    def fetch_page_content(url):
        """Simple lightweight scraper to get text from a URL"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code != 200: return f"[Error: Status {res.status_code}]"
            
            # Simple HTML Strip (No BS4 dependency)
            text = res.text
            text = re.sub(r'<script.*?</script>', '', text, flags=re.DOTALL)
            text = re.sub(r'<style.*?</style>', '', text, flags=re.DOTALL)
            text = re.sub(r'<[^>]+>', ' ', text)
            text = re.sub(r'\s+', ' ', text).strip()
            return text[:50000] + "..." # Limit to 50kb per page (Massive)
        except Exception as e: return f"[Fetch Error: {e}]"

    @staticmethod
    def deep_research(topic):
        """Runs a multi-phase research loop found on Arxiv and Web"""
        try:
            aggregated = f"--- DEEP RESEARCH REPORT: {topic} ---\n"
            aggregated += f"Generated: {datetime.datetime.now()}\n\n"
            
            # Phase 1: Academic Sources (Arxiv, ResearchGate, Academia)
            query_academic = f"{topic} (site:arxiv.org OR site:researchgate.net OR site:academia.edu OR site:sciencedirect.com)"
            results = list(DDGS().text(query_academic, max_results=10)) # Increased to 10
            
            aggregated += "\n### ACADEMIC SOURCES & ABSTRACTS\n"
            for r in results:
                aggregated += f"\nSOURCE: {r['title']}\nURL: {r['href']}\nSNIPPET: {r['body']}\n"
                
                # Try to fetch content if it looks like a page (not a PDF)
                if not r['href'].endswith(".pdf"):
                    content = JarvisTools.fetch_page_content(r['href'])
                    aggregated += f"--- EXTRACTED CONTENT ---\n{content}\n-------------------------\n"

            # Phase 2: Trusted Data (Wikipedia, Reuters, Gov)
            query_trusted = f"{topic} site:wikipedia.org OR site:reuters.com OR site:gov"
            results = list(DDGS().text(query_trusted, max_results=5)) # Increased to 5
            
            aggregated += "\n\n### TRUSTED DATA & STATISTICS\n"
            for r in results:
                aggregated += f"\nSOURCE: {r['title']}\nURL: {r['href']}\nSNIPPET: {r['body']}\n"
                content = JarvisTools.fetch_page_content(r['href'])
                aggregated += f"--- EXTRACTED CONTENT ---\n{content}\n-------------------------\n"
            
            # SMART SAVE: Auto-save to Learning/ folder
            filename = f"Learning/Research_{topic.replace(' ', '_')}_{int(time.time())}.txt"
            full_path = os.path.join(WORKSPACE_DIR, filename)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(aggregated)
            
            return f"Deep Research V2 Complete. Full scraped report ({len(aggregated)} chars) saved to '{filename}'.\n\n[Preview]: {aggregated[:500]}..."
        except Exception as e: return f"Research Error: {e}"

    @staticmethod
    def read_clipboard():
        try:
            return root.clipboard_get()
        except: return "Clipboard Empty."

    @staticmethod
    def launch_app(app_name):
        try:
            app_map = {
                "spotify": "spotify",
                "chrome": "chrome",
                "calculator": "calc",
                "notepad": "notepad",
                "explorer": "explorer",
                "cmd": "cmd",
                "powershell": "powershell"
            }
            target = app_map.get(app_name.lower(), app_name)
            os.system(f"start {target}")
            return f"Launched {app_name}"
        except Exception as e: return f"Error launching {app_name}: {e}"

    @staticmethod
    def system_control(command):
        try:
            if command == "shutdown":
                os.system("shutdown /s /t 10")
                return "Shutting down in 10s... (Run 'shutdown /a' to cancel)"
            elif command == "volume_mute":
                # Uses a generic way to toggle mute via VBS script oneliner or third party tool if available. 
                # For vanilla python without libs, this is tricky. 
                # Let's use a powershell trick for now or just acknowledge limitation.
                # Actually, 'nircmd' is best but user doesn't have it.
                # We will stick to simple shutdown/lock for now to avoid dependency hell.
                return "Volume control requires 'nircmd' installed. Command ignored."
            elif command == "lock":
                os.system("rundll32.exe user32.dll,LockWorkStation")
                return "Workstation Locked."
            elif command == "screen_off":
                 # This usually requires nircmd too.
                 return "Screen control requires 'nircmd'."
            return "Unknown System Command."
        except Exception as e: return f"Error: {e}"

    @staticmethod
    def run_python(script_name):
        try:
            # Check Sandbox
            if os.path.isabs(script_name) or ".." in script_name:
                return "Error: Script must be in workspace."
            
            path = os.path.join(WORKSPACE_DIR, script_name)
            if not os.path.exists(path): return f"Script '{script_name}' not found."
            
            # Run with timeout to prevent hanging the brain
            result = subprocess.run(
                ["python", path], 
                capture_output=True, 
                text=True, 
                timeout=10
            ) # 10s timeout for safety
            
            output = result.stdout + "\n" + result.stderr
            return f"--- Execution Output ---\n{output.strip()}"
        except subprocess.TimeoutExpired:
            return "Error: Execution Timed Out (10s limit)."
        except Exception as e: return f"Execution Error: {e}"

    @staticmethod
    def copy_to_workspace(source_path):
        try:
            if not os.path.exists(source_path): return "Source not found."
            
            basename = os.path.basename(source_path)
            dest = os.path.join(WORKSPACE_DIR, basename)
            
            if os.path.isdir(source_path):
                if os.path.exists(dest): shutil.rmtree(dest) # Overwrite
                shutil.copytree(source_path, dest)
                return f"Copied directory '{basename}' to workspace."
            else:
                shutil.copy2(source_path, dest)
                return f"Copied file '{basename}' to workspace."
        except Exception as e: return f"Copy Error: {e}"

    @staticmethod
    def scaffold_project(project_name, stack):
        """Creates a full starter project structure"""
        try:
            # Enforce Sandbox
            if os.path.isabs(project_name) or ".." in project_name: return "Error: Project must be in workspace."
            
            # SMART ORGANIZATION: Default to 'Projects/' folder if not specified
            if not project_name.startswith("Projects/") and not "/" in project_name:
                project_name = f"Projects/{project_name}"
            
            base_path = os.path.join(WORKSPACE_DIR, project_name)
            os.makedirs(base_path, exist_ok=True)
            
            if stack.lower() == "frontend":
                # HTML/CSS/JS Boilerplate
                with open(os.path.join(base_path, "index.html"), "w", encoding="utf-8") as f:
                    f.write(f"<!DOCTYPE html>\n<html lang='en'>\n<head>\n<meta charset='UTF-8'>\n<title>{project_name}</title>\n<link rel='stylesheet' href='style.css'>\n</head>\n<body>\n<h1>{project_name}</h1>\n<script src='script.js'></script>\n</body>\n</html>")
                with open(os.path.join(base_path, "style.css"), "w", encoding="utf-8") as f:
                    f.write("body { font-family: sans-serif; background: #222; color: #fff; padding: 2rem; }")
                with open(os.path.join(base_path, "script.js"), "w", encoding="utf-8") as f:
                    f.write(f"console.log('{project_name} Initialized');")
                return f"Frontend Project '{project_name}' created (index.html, style.css, script.js)."
                
            elif stack.lower() == "python":
                # Python Boilerplate
                os.makedirs(os.path.join(base_path, "tests"), exist_ok=True)
                with open(os.path.join(base_path, "main.py"), "w", encoding="utf-8") as f:
                    f.write("def main():\n    print('Hello World')\n\nif __name__ == '__main__':\n    main()")
                with open(os.path.join(base_path, "requirements.txt"), "w", encoding="utf-8") as f:
                    f.write("# Add dependencies here")
                with open(os.path.join(base_path, "README.md"), "w", encoding="utf-8") as f:
                    f.write(f"# {project_name}\n\nGenerated by Jarvis.")
                return f"Python Project '{project_name}' created (main.py, tests/, requirements.txt)."
                
            else:
                return "Unknown stack. Use 'frontend' or 'python'."
        except Exception as e: return f"Scaffold Error: {e}"
    
    @staticmethod
    def autonomous_task(objective):
        """
        Execute a complex multi-step task autonomously.
        Uses the full agent system: planning, execution, QA, self-healing.
        Best for: building websites, research projects, code generation.
        """
        try:
            from agents import autonomous_executor
            import threading
            
            def run_in_background():
                try:
                    result = autonomous_executor.run(objective)
                    print(f"[Autonomous] Task completed! Project: {result.get('project_path', 'N/A')}")
                except Exception as e:
                    print(f"[Autonomous] Error: {e}")
            
            # Run in background thread so UI doesn't freeze
            thread = threading.Thread(target=run_in_background, daemon=True)
            thread.start()
            
            return f"Started autonomous task: '{objective[:100]}...'\n\nThis will run in the background. Check progress with: read_file('.context/task_state.md')"
        except Exception as e:
            return f"Failed to start autonomous task: {e}"
    
    @staticmethod
    def cofounder_task(task_type, objective):
        """
        General co-founder task - not just coding.
        task_type: 'research', 'writing', 'analysis', 'coding', 'general'
        """
        try:
            from agents import autonomous_executor
            import threading
            
            # Prefix objective with task type for proper routing
            full_objective = f"[{task_type.upper()}] {objective}"
            
            def run_in_background():
                try:
                    result = autonomous_executor.run(full_objective)
                    print(f"[Co-founder] Task completed!")
                except Exception as e:
                    print(f"[Co-founder] Error: {e}")
            
            thread = threading.Thread(target=run_in_background, daemon=True)
            thread.start()
            
            return f"Started {task_type} task: '{objective[:80]}...'\n\nRunning in background."
        except Exception as e:
            return f"Failed to start task: {e}"
    
    @staticmethod
    def git_push(project_path, message=None):
        """Commit and push changes to GitHub."""
        try:
            from agents import git_agent
            
            full_path = os.path.join(WORKSPACE_DIR, project_path)
            if not os.path.exists(full_path):
                return f"Project not found: {project_path}"
            
            # Commit
            commit_result = git_agent.commit(full_path, message)
            if not commit_result.get("success"):
                return f"Commit failed: {commit_result.get('error', 'Unknown error')}"
            
            # Push
            push_result = git_agent.push(full_path)
            if push_result.get("success"):
                return f"Pushed: {commit_result.get('message', 'Changes pushed')}"
            else:
                return f"Push failed: {push_result.get('stderr', 'Unknown error')}"
        except Exception as e:
            return f"Git error: {e}"
    
    # === BUSINESS SUITE TOOLS ===
    
    @staticmethod
    def research_papers(query, num_papers=10):
        """Search academic papers across arXiv, Semantic Scholar."""
        try:
            from agents import academic_research
            
            results = academic_research.search(query, max_results=num_papers)
            
            output = f"Found {results['total_papers']} papers:\n\n"
            for i, paper in enumerate(results['papers'][:num_papers], 1):
                citation = academic_research.generate_citation(paper, "APA")
                output += f"{i}. {paper['title']}\n"
                output += f"   {citation}\n"
                if paper.get('abstract'):
                    output += f"   Abstract: {paper['abstract'][:200]}...\n"
                output += "\n"
            
            return output
        except Exception as e:
            return f"Research error: {e}"
    
    @staticmethod
    def literature_review(topic):
        """Generate a full literature review with citations."""
        try:
            from agents import academic_research
            
            result = academic_research.generate_literature_review(topic)
            
            if result.get("error"):
                return f"Error: {result['error']}"
            
            output = result.get("literature_review", "")
            output += "\n\n## References\n\n"
            for ref in result.get("references", []):
                output += f"{ref}\n"
            
            # Save to file
            if result.get("saved_to"):
                output += f"\n\nFull review saved to: {result['saved_to']}"
            
            return output
        except Exception as e:
            return f"Literature review error: {e}"
    
    @staticmethod
    def business_analysis(company, description, industry):
        """Run full business analysis: SWOT, BMC, market sizing, financials."""
        try:
            from agents import business_analyst
            import json
            
            result = business_analyst.full_analysis(company, description, industry)
            
            output = f"# Business Analysis: {company}\n\n"
            output += f"## Executive Summary\n{result.get('executive_summary', 'N/A')}\n\n"
            
            if result.get("report_path"):
                output += f"\nFull report saved to: {result['report_path']}"
            
            return output
        except Exception as e:
            return f"Business analysis error: {e}"
    
    @staticmethod
    def competitor_analysis(company, industry):
        """Analyze competitors and market positioning."""
        try:
            from agents import business_analyst
            import json
            
            result = business_analyst.competitor_analysis(company, industry)
            
            if result.get("error"):
                return f"Error: {result['error']}"
            
            output = f"# Competitor Analysis: {company}\n\n"
            
            for comp in result.get("top_competitors", []):
                output += f"## {comp.get('name', 'Unknown')}\n"
                output += f"- Strengths: {', '.join(comp.get('strengths', []))}\n"
                output += f"- Weaknesses: {', '.join(comp.get('weaknesses', []))}\n"
                output += f"- Market Share: {comp.get('estimated_market_share', 'Unknown')}\n\n"
            
            positioning = result.get("your_positioning", {})
            output += f"## Your Positioning\n"
            output += f"- Unique Advantages: {', '.join(positioning.get('unique_advantages', []))}\n"
            output += f"- Strategy: {positioning.get('recommended_strategy', 'N/A')}\n"
            
            return output
        except Exception as e:
            return f"Competitor analysis error: {e}"
    
    @staticmethod
    def market_sizing(product, target_market):
        """Calculate TAM/SAM/SOM with validation."""
        try:
            from agents import business_analyst
            
            result = business_analyst.market_sizing(product, target_market)
            
            if result.get("error"):
                return f"Error: {result['error']}"
            
            output = f"# Market Sizing: {product}\n\n"
            
            tam = result.get("tam", {})
            sam = result.get("sam", {})
            som = result.get("som", {})
            
            output += f"## TAM: {tam.get('value_usd', 'TBD')}\n"
            output += f"{tam.get('description', '')}\n\n"
            
            output += f"## SAM: {sam.get('value_usd', 'TBD')}\n"
            output += f"{sam.get('description', '')}\n\n"
            
            output += f"## SOM: {som.get('value_usd', 'TBD')}\n"
            output += f"{som.get('description', '')}\n\n"
            
            validation = result.get("bottom_up_validation", {})
            output += f"## Validation\n"
            output += f"- Potential Customers: {validation.get('potential_customers', 'TBD')}\n"
            output += f"- Avg Deal Size: {validation.get('average_deal_size', 'TBD')}\n"
            
            return output
        except Exception as e:
            return f"Market sizing error: {e}"
    
    @staticmethod
    def generate_pitch_deck(company, description, industry="tech"):
        """Create investor-ready pitch deck with reveal.js HTML."""
        try:
            from agents import pitch_deck, pitch_deck_scorer
            
            result = pitch_deck.generate(company, description, industry)
            
            # Score the deck
            score_result = pitch_deck_scorer.score(result["slides"])
            summary = pitch_deck_scorer.get_summary(score_result)
            
            output = f"# Pitch Deck Generated: {company}\n\n"
            output += f"Slides: {result['slide_count']}\n"
            output += f"Theme: {result['theme']}\n"
            output += f"Location: {result['deck_path']}\n"
            output += f"HTML File: {result['html_file']}\n\n"
            output += f"## Quality Score\n{summary}"
            
            return output
        except Exception as e:
            return f"Pitch deck error: {e}"
    
    @staticmethod
    def score_pitch_deck(slides_json):
        """Score an existing pitch deck on quality dimensions."""
        try:
            from agents import pitch_deck_scorer
            import json
            
            if isinstance(slides_json, str):
                slides = json.loads(slides_json)
            else:
                slides = slides_json
            
            result = pitch_deck_scorer.score(slides)
            summary = pitch_deck_scorer.get_summary(result)
            
            return summary
        except Exception as e:
            return f"Scoring error: {e}"

class JarvisUI:
    def __init__(self, root):
        self.root = root
        self.root.title("J.A.R.V.I.S // TERMINAL_LINK_V2")
        self.root.geometry("900x650")
        self.root.configure(bg="#000000")
        
        self.is_running = False
        self.is_busy = False # Flag: Prevents interruptions
        self.is_speaking = False # Flag: Prevents hearing itself
        self.stop_flag = False # Flag: Forces halts
        self.current_turn_id = 0
        self.msg_queue = queue.Queue()
        self.speech_queue = queue.Queue() # For streaming TTS
        self.audio_queue = queue.Queue() # For Playing Audio
        self.current_chat_file = None
        self.chat_history = [CHAT_PROMPT]  # Initialize chat history
        
        self.setup_ui()
        self.log_system("Initializing Sentient Suite...")
        
        self.load_chat_list()
        if not self.current_chat_file: 
            self.new_chat()
        
        # Bind Escape Key for Emergency Stop
        self.root.bind("<Escape>", lambda e: self.stop_action())
        
        threading.Thread(target=self.load_ai, daemon=True).start()
        threading.Thread(target=self.speech_synthesis_loop, daemon=True).start()
        threading.Thread(target=self.audio_playback_loop, daemon=True).start()
        self.root.after(100, self.process_queue)

    def setup_ui(self):
        """Build the complete UI layout."""
        # Main container
        main_frame = tk.Frame(self.root, bg="#000000")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Sidebar for chat history
        sidebar = tk.Frame(main_frame, bg="#111111", width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        sidebar.pack_propagate(False)
        
        # Chat list
        tk.Label(sidebar, text="SESSIONS", bg="#111111", fg="#00ff41", 
                 font=("Consolas", 10, "bold")).pack(pady=10)
        
        self.chat_listbox = tk.Listbox(sidebar, bg="#1a1a1a", fg="#00ff41",
                                       font=("Consolas", 9), selectbackground="#003300",
                                       borderwidth=0, highlightthickness=0)
        self.chat_listbox.pack(fill=tk.BOTH, expand=True, padx=5)
        self.chat_listbox.bind("<<ListboxSelect>>", self.select_chat)
        
        # New chat button
        tk.Button(sidebar, text="+ NEW CHAT", bg="#003300", fg="#00ff41",
                  font=("Consolas", 10, "bold"), borderwidth=0,
                  command=self.new_chat).pack(fill=tk.X, padx=5, pady=5)
        
        # Main chat area
        chat_frame = tk.Frame(main_frame, bg="#000000")
        chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Title bar
        title_bar = tk.Frame(chat_frame, bg="#000000")
        title_bar.pack(fill=tk.X)
        
        tk.Label(title_bar, text="J.A.R.V.I.S", bg="#000000", fg="#00ff41",
                 font=("Consolas", 20, "bold")).pack(side=tk.LEFT)
        
        self.status_label = tk.Label(title_bar, text="STANDBY", bg="#000000", fg="#666666",
                                     font=("Consolas", 10))
        self.status_label.pack(side=tk.RIGHT)
        
        # Chat display
        self.chat_area = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, 
                                                    bg="#0a0a0a", fg="#00ff41",
                                                    font=("Consolas", 11),
                                                    insertbackground="#00ff41",
                                                    borderwidth=0)
        self.chat_area.pack(fill=tk.BOTH, expand=True, pady=10)
        self.chat_area.config(state='disabled')
        
        # Input area
        input_frame = tk.Frame(chat_frame, bg="#000000")
        input_frame.pack(fill=tk.X)
        
        self.msg_entry = tk.Entry(input_frame, bg="#1a1a1a", fg="#00ff41",
                                  font=("Consolas", 12), insertbackground="#00ff41",
                                  borderwidth=0)
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10, ipadx=10)
        self.msg_entry.bind("<Return>", self.send_text)
        
        tk.Button(input_frame, text="SEND", bg="#003300", fg="#00ff41",
                  font=("Consolas", 10, "bold"), borderwidth=0,
                  command=self.send_text).pack(side=tk.LEFT, padx=(5, 0), ipady=8, ipadx=15)
        
        # Control buttons
        control_frame = tk.Frame(chat_frame, bg="#000000")
        control_frame.pack(fill=tk.X, pady=10)
        
        self.btn_toggle = tk.Button(control_frame, text="INITIATE LISTENING", 
                                     bg="#003300", fg="#00ff41",
                                     font=("Consolas", 10, "bold"), borderwidth=0,
                                     command=self.toggle_listening, state="disabled")
        self.btn_toggle.pack(side=tk.LEFT, ipady=8, ipadx=15)
        
        tk.Button(control_frame, text="CLEAR MEMORY", bg="#330000", fg="#ff4444",
                  font=("Consolas", 10, "bold"), borderwidth=0,
                  command=self.clear_memory).pack(side=tk.RIGHT, ipady=8, ipadx=15)
        
        tk.Button(control_frame, text="STOP", bg="#660000", fg="#ff0000",
                  font=("Consolas", 10, "bold"), borderwidth=0,
                  command=self.stop_action).pack(side=tk.RIGHT, padx=5, ipady=8, ipadx=15)
        
        # System log
        self.system_log = tk.Text(chat_frame, height=4, bg="#0a0a0a", fg="#666666",
                                  font=("Consolas", 9), borderwidth=0)
        self.system_log.pack(fill=tk.X)
        self.system_log.config(state='disabled')
        
    def log_system(self, msg):
        """Log system message."""
        self.system_log.config(state='normal')
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.system_log.insert(tk.END, f"[{timestamp}] {msg}\n")
        self.system_log.see(tk.END)
        self.system_log.config(state='disabled')
        
    def toggle_busy(self, state):
        """Toggle busy state."""
        self.is_busy = state
        if state:
            self.status_label.config(text="PROCESSING...", fg="#ffaa00")
            self.msg_entry.config(state='disabled')
        else:
            self.status_label.config(text="READY", fg="#00ff41")
            self.msg_entry.config(state='normal')
            
    def process_queue(self):
        """Process message queue for UI updates."""
        try:
            while True:
                msg_type, content = self.msg_queue.get_nowait()
                
                self.chat_area.config(state='normal')
                
                if msg_type == "user":
                    self.chat_area.insert(tk.END, f"\n[YOU] {content}\n", "user")
                elif msg_type == "jarvis":
                    self.chat_area.insert(tk.END, f"\n[JARVIS] {content}\n", "jarvis")
                elif msg_type == "jarvis_partial":
                    self.chat_area.insert(tk.END, content)
                elif msg_type == "system":
                    self.chat_area.insert(tk.END, f"\n[SYSTEM] {content}\n", "system")
                    
                self.chat_area.see(tk.END)
                self.chat_area.config(state='disabled')
                
        except queue.Empty:
            pass
            
        self.root.after(100, self.process_queue)
        
    def load_chat_list(self):
        """Load saved chats into sidebar."""
        self.chat_listbox.delete(0, tk.END)
        if os.path.exists(CHATS_DIR):
            for f in sorted(os.listdir(CHATS_DIR), reverse=True):
                if f.endswith('.json'):
                    self.chat_listbox.insert(tk.END, f.replace('.json', ''))
        
        if self.chat_listbox.size() > 0:
            self.chat_listbox.select_set(0)
            self.current_chat_file = self.chat_listbox.get(0) + '.json'
            self.load_memory()
            
    def select_chat(self, event):
        """Handle chat selection from listbox."""
        selection = self.chat_listbox.curselection()
        if selection:
            self.current_chat_file = self.chat_listbox.get(selection[0]) + '.json'
            self.load_memory()
            self.display_chat_history()
            
    def new_chat(self):
        """Create a new chat session."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_chat_file = f"chat_{timestamp}.json"
        self.chat_history = [CHAT_PROMPT]
        self.save_memory()
        self.load_chat_list()
        
        # Clear display
        self.chat_area.config(state='normal')
        self.chat_area.delete('1.0', tk.END)
        self.chat_area.config(state='disabled')
        
        self.log_system(f"New session: {self.current_chat_file}")
        
    def display_chat_history(self):
        """Display loaded chat history in chat area."""
        self.chat_area.config(state='normal')
        self.chat_area.delete('1.0', tk.END)
        
        for msg in self.chat_history[1:]:  # Skip system prompt
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            
            if role == 'user':
                self.chat_area.insert(tk.END, f"\n[YOU] {content}\n")
            elif role == 'assistant':
                self.chat_area.insert(tk.END, f"\n[JARVIS] {content}\n")
                
        self.chat_area.see(tk.END)
        self.chat_area.config(state='disabled')
        
    def check_intent(self, text):
        """Check if text is a task or just conversation."""
        task_keywords = ['build', 'create', 'make', 'write', 'research', 'analyze', 
                        'generate', 'search', 'find', 'code', 'deploy', 'launch']
        text_lower = text.lower()
        return any(kw in text_lower for kw in task_keywords)

    def stop_action(self):
        """Emergency Stop"""
        self.log_system("!!! EMERGENCY STOP TRIGGERED !!!")
        self.stop_flag = True
        self.is_busy = False
        self.toggle_busy(False)
        sd.stop() # Kill Audio
        
        # Clear Queues
        with self.speech_queue.mutex: self.speech_queue.queue.clear()
        with self.audio_queue.mutex: self.audio_queue.queue.clear()
        with self.msg_queue.mutex: self.msg_queue.queue.clear()

    def run_tool_loop(self, source, turn_id):
        """The Engineer Brain Loop - Executes tools until done"""
        if turn_id != self.current_turn_id or self.stop_flag: return
        
        self.log_system("Engineer loop started...")
        
        # Power Mode: Unlimited Tokens (-1) for massive reports
        payload = {"messages": self.chat_history, "temperature": 0.0, "max_tokens": -1}
        
        try:
            response = requests.post(LM_STUDIO_URL, json=payload)
            if response.status_code != 200: 
                self.log_system(f"API Error: {response.status_code}")
                return
            content = response.json()['choices'][0]['message']['content']
            
            # Display the response
            self.msg_queue.put(("jarvis", content))
            self.chat_history.append({"role": "assistant", "content": content})
            
            # Parse tool call from response
            tool_pattern = r'```json\s*(\{.*?\})\s*```'
            match = re.search(tool_pattern, content, re.DOTALL)
            
            if match:
                try:
                    tool_data = json.loads(match.group(1))
                    tool_name = tool_data.get("tool", "")
                    args = tool_data.get("args", {})
                    
                    self.log_system(f"Executing tool: {tool_name}")
                    
                    if tool_name == "done":
                        # Task complete
                        self.log_system("Task completed!")
                        self.chat_history[0] = CHAT_PROMPT  # Switch back to chat
                        return
                    
                    # Execute the tool
                    tools = JarvisTools()
                    if hasattr(tools, tool_name):
                        tool_func = getattr(tools, tool_name)
                        result = tool_func(**args) if args else tool_func()
                        
                        # Add result to history and continue loop
                        self.chat_history.append({
                            "role": "user", 
                            "content": f"Tool Result:\n{result}"
                        })
                        
                        # Continue the loop
                        self.run_tool_loop(source, turn_id)
                    else:
                        self.log_system(f"Unknown tool: {tool_name}")
                        
                except json.JSONDecodeError as e:
                    self.log_system(f"JSON parse error: {e}")
            else:
                self.log_system("No tool call found in response")
                
        except Exception as e:
            self.log_system(f"Tool loop error: {e}")
            return

    def send_text(self, event=None):
        if self.is_busy: return # Block input if busy
        text = self.msg_entry.get().strip()
        if not text: return
        self.msg_entry.delete(0, tk.END)
        self.current_turn_id += 1
        self.msg_queue.put(("user", text))
        
        # RACE CONDITION FIX: Lock UI IMMEDIATELY
        self.toggle_busy(True) 
        threading.Thread(target=self.brain_core, args=(text, "text", self.current_turn_id), daemon=True).start()

    # ...

    def execute_tool(self, data, source, turn_id):
        # ... (No changes here, just context) ...
        pass

    def speech_synthesis_loop(self):
        """Thread 1: Generates Audio from Text"""
        while True:
            text = self.speech_queue.get()
            if text is None: break
            
            if self.stop_flag: 
                self.speech_queue.task_done()
                continue

            try:
                # Clean Markdown
                clean_text = text.replace("*", "").replace("#", "")
                
                lang = "en-us"
                detected_lang = detect(clean_text)
                if detected_lang == 'fr': lang = "fr-fr"
                elif detected_lang == 'ar':
                    self.log_system("TTS: Arabic text detected (Muted).")
                    self.speech_queue.task_done()
                    continue

                self.log_system(f"TTS: Synthesizing '{clean_text}'...")
                samples, rate = self.kokoro.create(clean_text, voice=DEFAULT_VOICE, speed=1.0, lang=lang)
                
                if len(samples) > 0:
                     self.audio_queue.put((samples, rate)) # Hand off to Player
                
            except Exception as e: self.log_system(f"TTS Gen Error: {e}")
            
            self.speech_queue.task_done()

    def audio_playback_loop(self):
        """Thread 2: Plays Audio Objects"""
        while True:
            item = self.audio_queue.get()
            if item is None: break
            
            samples, rate = item
            if self.stop_flag:
                self.audio_queue.task_done()
                continue
                
            try:
                # self.log_system("TTS: Playing...") 
                sd.play(samples, rate)
                sd.wait() # Blocking is fine here, Generator is running in parallel!
            except Exception as e: self.log_system(f"Playback Error: {e}")
            
            self.audio_queue.task_done()

    def generate_final_response(self, source, turn_id):
        """The Jarvis Brain Speak - NOW WITH STREAMING"""
        if turn_id != self.current_turn_id or self.stop_flag: return
        
        payload = {"messages": self.chat_history, "temperature": 0.7, "max_tokens": -1, "stream": True}
        
        full_response = ""
        sentence_buffer = ""
        
        try:
            # We use stream=True and iterate lines
            with requests.post(LM_STUDIO_URL, json=payload, stream=True) as response:
                if response.status_code != 200: 
                    self.log_system(f"API Error: {response.status_code}")
                    return

                # Send initial assistant role to chat history (will append content later)
                # Actually, we'll append the full message at the end to keep history clean.
                
                for line in response.iter_lines():
                    if self.stop_flag or turn_id != self.current_turn_id: 
                        self.log_system(" Stream Aborted.")
                        break
                        
                    if line:
                        decoded = line.decode('utf-8').strip()
                        if decoded.startswith("data: "):
                            json_str = decoded[6:] # Strip "data: "
                            if json_str == "[DONE]": break
                            
                            try:
                                chunk = json.loads(json_str)
                                delta = chunk['choices'][0]['delta'].get('content', '')
                                if delta:
                                    full_response += delta
                                    sentence_buffer += delta
                                    
                                    # 1. Update UI Real-time
                                    self.msg_queue.put(("jarvis_partial", delta))
                                    
                                    # 2. Check for Sentence Endings for TTS
                                    if source == "voice" and re.search(r'[.!?\n]', delta):
                                        # Split buffer into sentences
                                        sentences = re.split(r'(?<=[.!?])\s+', sentence_buffer)
                                        
                                        # Queue all complete sentences
                                        for s in sentences[:-1]:
                                            if s.strip(): self.speech_queue.put(s.strip())
                                        
                                        # Keep the incomplete part
                                        sentence_buffer = sentences[-1]

                            except: pass
                
                # Flush remaining buffer
                if source == "voice" and sentence_buffer.strip() and not self.stop_flag:
                    self.speech_queue.put(sentence_buffer.strip())

            # Check for tool calls in the full response
            tool_pattern = r"```json\n({.*?})\n```"
            match = re.search(tool_pattern, full_response, re.DOTALL)
            
            if match:
                data = json.loads(match.group(1), strict=False) # Use group(1) to get content inside ```json```
                
                if data.get("tool") == "done":
                        # Task Finished!
                        report = data.get("args", {}).get("report", "")
                        
                        if report:
                            # 1. Save Full Report to File (The "Handover" Document)
                            timestamp = int(time.time())
                            report_file = f"Reports/Task_Report_{timestamp}.txt"
                            full_path = os.path.join(WORKSPACE_DIR, report_file)
                            os.makedirs(os.path.dirname(full_path), exist_ok=True)
                            
                            with open(full_path, "w", encoding="utf-8") as f:
                                f.write(report)

                            # 2. Extract Summary for Chat (First paragraph / section)
                            summary = report.split('\n\n')[0] # Get first block
                            display_text = f"✅ **Task Complete.**\n📄 Full Report: `Reports/{report_file}`\n\n{summary}"

                            # 3. Log & Display
                            self.log_system(f"Engineering Complete. Report saved to {report_file}.")
                            self.chat_history.append({"role": "assistant", "content": display_text})
                            self.save_memory()
                            
                            self.msg_queue.put(("jarvis", display_text))
                            
                            # 4. Speak (Briefly)
                            # Speak only the first sentence of the summary
                            first_sentence = summary.split('.')[0]
                            self.speech_queue.put(f"Task finished. {first_sentence}.") 
                        else:
                            # Fallback (Simple Done)
                            self.log_system("Engineering Complete. Handing off to Jarvis.")
                            self.chat_history[0] = CHAT_PROMPT
                            self.generate_final_response(source, turn_id)
                        return

                self.execute_tool(data, source, turn_id)
                return

            if not self.stop_flag:
                self.chat_history.append({"role": "assistant", "content": full_response})
                self.save_memory()
                # self.speak(full_response) <- No longer needed, handled by stream
            
        except Exception as e:
            self.log_system(f"Jarvis Error: {e}")

    def brain_core(self, user_text, source, turn_id):
        """The Main Decision Engine"""
        if turn_id != self.current_turn_id: return
        
        # Redundant Safety Lock (Already locked in handle_audio/send_text)
        self.toggle_busy(True) 
        self.stop_flag = False
        
        self.chat_history.append({"role": "user", "content": user_text})
        
        # Step 1: The Router - Is this a task?
        is_task = self.check_intent(user_text)
        
        if self.stop_flag: 
            self.toggle_busy(False)
            return
        
        if is_task:
            # Switch to Engineer Mode - Use TOOL_PROMPT
            self.log_system("Task detected - switching to Engineer Mode")
            self.chat_history[0] = TOOL_PROMPT
            
            # Run the tool execution loop
            self.run_tool_loop(source, turn_id)
        else:
            # Just chat - Use CHAT_PROMPT
            self.chat_history[0] = CHAT_PROMPT
            self.generate_final_response(source, turn_id)
        
        self.toggle_busy(False)

    def clear_memory(self):
        self.current_turn_id += 1
        self.chat_history = [CHAT_PROMPT]
        self.save_memory()
        self.chat_area.config(state='normal')
        self.chat_area.delete('1.0', tk.END)
        self.chat_area.config(state='disabled')
        self.log_system("Memory Wiped.")

    def load_memory(self):
        if not self.current_chat_file: 
            self.chat_history = [CHAT_PROMPT]
            return
        path = os.path.join(CHATS_DIR, self.current_chat_file)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.chat_history = json.load(f)
                    if self.chat_history: self.chat_history[0] = CHAT_PROMPT
                    else: self.chat_history = [CHAT_PROMPT]
            except: self.chat_history = [CHAT_PROMPT]
        else: self.chat_history = [CHAT_PROMPT]

    def save_memory(self):
        if not self.current_chat_file: return
        path = os.path.join(CHATS_DIR, self.current_chat_file)
        save_data = [self.chat_history[0]] + self.chat_history[-1000:] # Unlocked for High-RAM
        with open(path, "w", encoding="utf-8") as f: json.dump(save_data, f, indent=4)

    def load_ai(self):
        try:
            if not os.path.exists(VOSK_MODEL): 
                self.log_system("Model missing")
                return
            self.vosk_model = Model(VOSK_MODEL)
            self.rec = KaldiRecognizer(self.vosk_model, 16000, GRAMMAR)
            self.kokoro = Kokoro(KOKORO_MODEL, KOKORO_VOICES)
            self.log_system("Systems Ready.")
            self.btn_toggle.config(state="normal", bg="#003300")
        except Exception as e: self.log_system(f"Init Error: {e}")

    def toggle_listening(self):
        if not self.is_running:
            self.is_running = True
            self.btn_toggle.config(text="TERMINATE", bg="#330000", fg="#ff0000")
            threading.Thread(target=self.listen_loop, daemon=True).start()
        else:
            self.is_running = False
            self.btn_toggle.config(text="INITIATE LISTENING", bg="#111", fg="#00ff41")

    def listen_loop(self):
        self.log_system("Listening...")
        q = queue.Queue()
        def callback(indata, frames, time, status): q.put(bytes(indata))
        with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16', channels=1, callback=callback):
            while self.is_running:
                data = q.get()
                if self.is_busy or self.is_speaking: 
                     # STRICT LOCK: Do not process ANY audio while thinking/speaking
                     continue 
                if self.rec.AcceptWaveform(data):
                    res = json.loads(self.rec.Result())
                    text = res.get("text", "")
                    for trigger in WAKE_WORDS:
                        if trigger in text:
                            self.log_system(f"Trigger: {trigger}")
                            print("\a")
                            self.handle_audio_input()
                            self.rec.Reset()
                            q.queue.clear()

    def handle_audio_input(self):
        self.log_system("Recording...")
        fs = 16000
        audio_data = []
        has_spoken = False
        start_time = time.time()
        last_sound = time.time()
        try:
            with sd.InputStream(samplerate=fs, channels=1, dtype='int16') as stream:
                while True:
                    chunk, _ = stream.read(int(fs * 0.1))
                    audio_data.append(chunk)
                    if np.max(np.abs(chunk)) > 500:
                        has_spoken = True
                        last_sound = time.time()
                    if not has_spoken and (time.time() - start_time > 5.0): return
                    if has_spoken and (time.time() - last_sound > 1.5): break
            write("command.wav", fs, np.concatenate(audio_data))
            
            cmd = [WHISPER_CLI, "-m", WHISPER_MODEL, "-f", "command.wav", "-nt"]
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', startupinfo=si)
            user_text = result.stdout.strip()
            
            # WHISPER HALLUCINATION FILTER
            hallucinations = ["[Music]", "[BLANK_AUDIO]", "[Applause]", "(copyright)", "[Silence]"]
            if any(h.lower() in user_text.lower() for h in hallucinations) or len(user_text) < 2:
                self.log_system("Ignored: Silence/Hallucination")
                return

            if user_text:
                self.current_turn_id += 1
                self.msg_queue.put(("user", user_text))
                threading.Thread(target=self.brain_core, args=(user_text, "voice", self.current_turn_id), daemon=True).start()
        except: pass

    def speak(self, text):
        if self.stop_flag: return
        try:
            # Clean Markdown before TTS
            clean_text = text.replace("*", "").replace("#", "")
            
            self.is_speaking = True # Mute Mic
            
            lang = "en-us"
            detected_lang = detect(clean_text)
            if detected_lang == 'fr': lang = "fr-fr"
            elif detected_lang == 'ar':
                self.log_system("TTS: Arabic not supported (Text Only).")
                self.is_speaking = False
                return

            self.log_system(f"TTS: Synthesizing '{clean_text}'...")
            samples, rate = self.kokoro.create(clean_text, voice=DEFAULT_VOICE, speed=1.0, lang=lang)
            if len(samples) == 0: 
                self.log_system("TTS Error: No audio samples generated.")
                self.is_speaking = False
                return

            self.log_system("TTS: Playing Audio...")
            sd.play(samples, rate)
            sd.wait()
            self.log_system("TTS: Done.")
            self.is_speaking = False
        except Exception as e: 
            self.log_system(f"TTS Error: {e}")
            self.is_speaking = False
            
            # Check stop flag again before playing
            if self.stop_flag: 
                self.is_speaking = False
                return
            
            sd.play(samples, rate)
            sd.wait()
            self.is_speaking = False # Unmute Mic
        except: 
            self.is_speaking = False 

if __name__ == "__main__":
    root = tk.Tk()
    app = JarvisUI(root)
    root.mainloop()