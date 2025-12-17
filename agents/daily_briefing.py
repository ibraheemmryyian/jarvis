"""
Daily Briefing System for Jarvis v2
Generates personalized morning summaries from memory, tasks, and context.
"""
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from .config import WORKSPACE_DIR, LM_STUDIO_URL
from .memory import memory
import requests


class DailyBriefing:
    """
    Generates daily briefing summaries.
    
    Features:
    - Task overview and priorities
    - Calendar integration (when available)
    - Recent activity summary
    - Key metrics/progress
    - Personalized voice delivery option
    """
    
    def __init__(self):
        self.briefing_dir = os.path.join(WORKSPACE_DIR, "briefings")
        os.makedirs(self.briefing_dir, exist_ok=True)
    
    def _call_llm(self, prompt: str) -> str:
        """Call LLM for briefing generation."""
        try:
            response = requests.post(
                LM_STUDIO_URL,
                json={
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.6,
                    "max_tokens": 1500
                },
                timeout=60
            )
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"[DailyBriefing] LLM Error: {e}")
        return ""
    
    def generate(self, user_name: str = "Boss", 
                 include_motivational: bool = True,
                 voice_mode: bool = False) -> Dict:
        """
        Generate the daily briefing.
        
        Args:
            user_name: Name to address user
            include_motivational: Include motivational closing
            voice_mode: Optimize for TTS delivery
        """
        print("[DailyBriefing] Generating morning briefing...")
        
        today = datetime.now().strftime("%A, %B %d, %Y")
        time_of_day = self._get_time_of_day()
        
        # Gather data sources
        data = self._gather_briefing_data()
        
        # Build briefing prompt
        prompt = f"""Generate a daily briefing for {user_name}.

DATE: {today}
TIME: {time_of_day}

DATA:
{json.dumps(data, indent=2)}

Create a briefing with these sections:
1. GREETING - Personalized {time_of_day} greeting
2. PRIORITY TASKS - Top 3 things to focus on today (from pending items)
3. PROGRESS UPDATE - What was accomplished recently
4. UPCOMING - Any due dates or deadlines approaching
{"5. MOTIVATION - Brief inspiring closing thought" if include_motivational else ""}

{"Make it VERY concise and punchy for voice delivery. Use short sentences." if voice_mode else "Use clear formatting with headers."}

Be specific about tasks and deadlines. Don't be generic.
If there's no data in a section, acknowledge it naturally ("No pending deadlines" etc)."""

        briefing_content = self._call_llm(prompt)
        
        # Create structured briefing
        briefing = {
            "date": today,
            "time": datetime.now().strftime("%H:%M"),
            "user": user_name,
            "content": briefing_content,
            "data": data,
            "voice_mode": voice_mode
        }
        
        # Save to file
        filename = f"briefing_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
        filepath = os.path.join(self.briefing_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# Daily Briefing - {today}\n\n")
            f.write(briefing_content)
        
        briefing["saved_to"] = filepath
        
        return briefing
    
    def _get_time_of_day(self) -> str:
        """Get time of day for appropriate greeting."""
        hour = datetime.now().hour
        if hour < 12:
            return "morning"
        elif hour < 17:
            return "afternoon"
        else:
            return "evening"
    
    def _gather_briefing_data(self) -> Dict:
        """Gather all data for the briefing."""
        data = {
            "pending_tasks": [],
            "completed_today": [],
            "upcoming_deadlines": [],
            "recent_activity": [],
            "memory_stats": {}
        }
        
        # Get briefing items from memory
        try:
            # Pending tasks
            pending = memory.get_briefing_items(include_completed=False)
            data["pending_tasks"] = [
                {"title": item.get("title", ""), 
                 "priority": item.get("priority", 0),
                 "due_date": item.get("due_date")}
                for item in pending[:10]
            ]
            
            # Sort by priority
            data["pending_tasks"].sort(key=lambda x: x["priority"], reverse=True)
            
            # Completed items (from last 24 hours)
            all_items = memory.get_briefing_items(include_completed=True)
            data["completed_today"] = [
                item.get("title", "")
                for item in all_items
                if item.get("completed")
            ][:5]
            
            # Get memory stats
            data["memory_stats"] = memory.get_stats()
            
            # Recent conversation summary
            recent_conv = memory.get_conversation(limit=5)
            if recent_conv:
                data["recent_activity"] = [
                    f"{msg.get('role', 'unknown')}: {msg.get('content', '')[:100]}..."
                    for msg in recent_conv[-3:]
                ]
        except Exception as e:
            print(f"[DailyBriefing] Error gathering data: {e}")
        
        return data
    
    def add_task(self, title: str, priority: int = 0, 
                 due_date: str = None) -> bool:
        """Add a task to the briefing queue."""
        return memory.add_briefing_item(
            title=title,
            content=title,
            item_type="task",
            priority=priority,
            due_date=due_date
        )
    
    def complete_task(self, task_id: int) -> bool:
        """Mark a task as complete."""
        return memory.complete_briefing_item(task_id)
    
    def get_quick_status(self) -> str:
        """Get a one-line status summary."""
        try:
            pending = memory.get_briefing_items(include_completed=False)
            completed = [i for i in memory.get_briefing_items(include_completed=True) 
                        if i.get("completed")]
            
            pending_count = len(pending)
            completed_count = len(completed)
            
            # Get highest priority task
            top_task = ""
            if pending:
                sorted_pending = sorted(pending, key=lambda x: x.get("priority", 0), reverse=True)
                top_task = sorted_pending[0].get("title", "Unknown")[:30]
            
            return f"{pending_count} pending, {completed_count} done. Top priority: {top_task or 'None'}"
        except Exception as e:
            return f"Status unavailable: {e}"
    
    def get_voice_briefing(self) -> str:
        """Get a concise briefing optimized for voice."""
        briefing = self.generate(voice_mode=True)
        
        # Clean for TTS
        content = briefing["content"]
        
        # Remove markdown
        content = content.replace("#", "")
        content = content.replace("*", "")
        content = content.replace("-", "")
        
        # Shorten sentences
        sentences = content.split(".")
        short_sentences = [s.strip() for s in sentences if len(s.strip()) > 10][:10]
        
        return ". ".join(short_sentences) + "."


# Singleton
daily_briefing = DailyBriefing()
