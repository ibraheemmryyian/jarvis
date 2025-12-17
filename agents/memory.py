"""
Persistent Memory Layer for Jarvis v2
Supabase-powered cross-session memory with embeddings and semantic search.

Tables (auto-created):
- conversations: Message history
- agent_memory: Persistent agent state
- embeddings: Vector search (optional)
"""
import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from .config import WORKSPACE_DIR

# Try to import Supabase, fall back to SQLite if not available
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

import sqlite3


class Memory:
    """
    Persistent memory layer for Jarvis agents.
    
    Features:
    - Cross-session conversation history
    - Agent state persistence
    - Semantic search (with embeddings)
    - Fallback to SQLite if Supabase unavailable
    """
    
    def __init__(self):
        self.supabase: Optional[Client] = None
        self.sqlite_conn: Optional[sqlite3.Connection] = None
        self.use_supabase = False
        
        # Try Supabase first
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")
        
        if SUPABASE_AVAILABLE and supabase_url and supabase_key:
            try:
                self.supabase = create_client(supabase_url, supabase_key)
                self.use_supabase = True
                print("[Memory] Connected to Supabase")
            except Exception as e:
                print(f"[Memory] Supabase failed: {e}, falling back to SQLite")
        
        if not self.use_supabase:
            self._init_sqlite()
    
    def _init_sqlite(self):
        """Initialize SQLite database as fallback."""
        db_path = os.path.join(WORKSPACE_DIR, "jarvis_memory.db")
        self.sqlite_conn = sqlite3.connect(db_path, check_same_thread=False)
        self.sqlite_conn.row_factory = sqlite3.Row
        
        # Create tables
        cursor = self.sqlite_conn.cursor()
        
        # Conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT,
                content TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """)
        
        # Agent memory table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT,
                key TEXT,
                value TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(agent_name, key)
            )
        """)
        
        # Facts/Knowledge table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                content TEXT,
                source TEXT,
                confidence REAL DEFAULT 1.0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Daily briefing data
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS briefing_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_type TEXT,
                title TEXT,
                content TEXT,
                priority INTEGER DEFAULT 0,
                due_date DATE,
                completed BOOLEAN DEFAULT FALSE,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.sqlite_conn.commit()
        print(f"[Memory] SQLite initialized: {db_path}")
    
    # === Conversation Memory ===
    
    def save_message(self, role: str, content: str, session_id: str = "default", 
                     metadata: Dict = None) -> bool:
        """Save a message to conversation history."""
        try:
            if self.use_supabase:
                self.supabase.table("conversations").insert({
                    "session_id": session_id,
                    "role": role,
                    "content": content,
                    "metadata": json.dumps(metadata or {})
                }).execute()
            else:
                cursor = self.sqlite_conn.cursor()
                cursor.execute(
                    "INSERT INTO conversations (session_id, role, content, metadata) VALUES (?, ?, ?, ?)",
                    (session_id, role, content, json.dumps(metadata or {}))
                )
                self.sqlite_conn.commit()
            return True
        except Exception as e:
            print(f"[Memory] Error saving message: {e}")
            return False
    
    def get_conversation(self, session_id: str = "default", limit: int = 50) -> List[Dict]:
        """Get recent conversation history."""
        try:
            if self.use_supabase:
                result = self.supabase.table("conversations")\
                    .select("*")\
                    .eq("session_id", session_id)\
                    .order("timestamp", desc=True)\
                    .limit(limit)\
                    .execute()
                return list(reversed(result.data))
            else:
                cursor = self.sqlite_conn.cursor()
                cursor.execute(
                    """SELECT * FROM conversations 
                       WHERE session_id = ? 
                       ORDER BY timestamp DESC LIMIT ?""",
                    (session_id, limit)
                )
                rows = cursor.fetchall()
                return list(reversed([dict(row) for row in rows]))
        except Exception as e:
            print(f"[Memory] Error getting conversation: {e}")
            return []
    
    def clear_conversation(self, session_id: str = "default") -> bool:
        """Clear conversation history for a session."""
        try:
            if self.use_supabase:
                self.supabase.table("conversations")\
                    .delete()\
                    .eq("session_id", session_id)\
                    .execute()
            else:
                cursor = self.sqlite_conn.cursor()
                cursor.execute(
                    "DELETE FROM conversations WHERE session_id = ?",
                    (session_id,)
                )
                self.sqlite_conn.commit()
            return True
        except Exception as e:
            print(f"[Memory] Error clearing conversation: {e}")
            return False
    
    # === Agent State Memory ===
    
    def save_agent_state(self, agent_name: str, key: str, value: Any) -> bool:
        """Save persistent state for an agent."""
        try:
            value_json = json.dumps(value)
            
            if self.use_supabase:
                self.supabase.table("agent_memory").upsert({
                    "agent_name": agent_name,
                    "key": key,
                    "value": value_json
                }).execute()
            else:
                cursor = self.sqlite_conn.cursor()
                cursor.execute(
                    """INSERT OR REPLACE INTO agent_memory (agent_name, key, value) 
                       VALUES (?, ?, ?)""",
                    (agent_name, key, value_json)
                )
                self.sqlite_conn.commit()
            return True
        except Exception as e:
            print(f"[Memory] Error saving agent state: {e}")
            return False
    
    def get_agent_state(self, agent_name: str, key: str, default: Any = None) -> Any:
        """Get persistent state for an agent."""
        try:
            if self.use_supabase:
                result = self.supabase.table("agent_memory")\
                    .select("value")\
                    .eq("agent_name", agent_name)\
                    .eq("key", key)\
                    .single()\
                    .execute()
                if result.data:
                    return json.loads(result.data["value"])
            else:
                cursor = self.sqlite_conn.cursor()
                cursor.execute(
                    "SELECT value FROM agent_memory WHERE agent_name = ? AND key = ?",
                    (agent_name, key)
                )
                row = cursor.fetchone()
                if row:
                    return json.loads(row["value"])
            return default
        except Exception as e:
            print(f"[Memory] Error getting agent state: {e}")
            return default
    
    def get_all_agent_state(self, agent_name: str) -> Dict:
        """Get all persistent state for an agent."""
        try:
            if self.use_supabase:
                result = self.supabase.table("agent_memory")\
                    .select("key, value")\
                    .eq("agent_name", agent_name)\
                    .execute()
                return {row["key"]: json.loads(row["value"]) for row in result.data}
            else:
                cursor = self.sqlite_conn.cursor()
                cursor.execute(
                    "SELECT key, value FROM agent_memory WHERE agent_name = ?",
                    (agent_name,)
                )
                return {row["key"]: json.loads(row["value"]) for row in cursor.fetchall()}
        except Exception as e:
            print(f"[Memory] Error getting all agent state: {e}")
            return {}
    
    # === Facts/Knowledge Base ===
    
    def save_fact(self, content: str, category: str = "general", 
                  source: str = None, confidence: float = 1.0) -> bool:
        """Save a fact to the knowledge base."""
        try:
            if self.use_supabase:
                self.supabase.table("facts").insert({
                    "category": category,
                    "content": content,
                    "source": source,
                    "confidence": confidence
                }).execute()
            else:
                cursor = self.sqlite_conn.cursor()
                cursor.execute(
                    "INSERT INTO facts (category, content, source, confidence) VALUES (?, ?, ?, ?)",
                    (category, content, source, confidence)
                )
                self.sqlite_conn.commit()
            return True
        except Exception as e:
            print(f"[Memory] Error saving fact: {e}")
            return False
    
    def search_facts(self, query: str, category: str = None, limit: int = 10) -> List[Dict]:
        """Search facts by keyword."""
        try:
            if self.use_supabase:
                q = self.supabase.table("facts").select("*")
                if category:
                    q = q.eq("category", category)
                q = q.ilike("content", f"%{query}%").limit(limit)
                return q.execute().data
            else:
                cursor = self.sqlite_conn.cursor()
                if category:
                    cursor.execute(
                        """SELECT * FROM facts 
                           WHERE content LIKE ? AND category = ?
                           ORDER BY confidence DESC LIMIT ?""",
                        (f"%{query}%", category, limit)
                    )
                else:
                    cursor.execute(
                        """SELECT * FROM facts 
                           WHERE content LIKE ?
                           ORDER BY confidence DESC LIMIT ?""",
                        (f"%{query}%", limit)
                    )
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"[Memory] Error searching facts: {e}")
            return []
    
    # === Daily Briefing Items ===
    
    def add_briefing_item(self, title: str, content: str, 
                          item_type: str = "task", priority: int = 0,
                          due_date: str = None) -> bool:
        """Add an item for daily briefing."""
        try:
            if self.use_supabase:
                self.supabase.table("briefing_items").insert({
                    "item_type": item_type,
                    "title": title,
                    "content": content,
                    "priority": priority,
                    "due_date": due_date
                }).execute()
            else:
                cursor = self.sqlite_conn.cursor()
                cursor.execute(
                    """INSERT INTO briefing_items 
                       (item_type, title, content, priority, due_date) 
                       VALUES (?, ?, ?, ?, ?)""",
                    (item_type, title, content, priority, due_date)
                )
                self.sqlite_conn.commit()
            return True
        except Exception as e:
            print(f"[Memory] Error adding briefing item: {e}")
            return False
    
    def get_briefing_items(self, item_type: str = None, 
                           include_completed: bool = False) -> List[Dict]:
        """Get items for daily briefing."""
        try:
            if self.use_supabase:
                q = self.supabase.table("briefing_items").select("*")
                if item_type:
                    q = q.eq("item_type", item_type)
                if not include_completed:
                    q = q.eq("completed", False)
                q = q.order("priority", desc=True).order("due_date")
                return q.execute().data
            else:
                cursor = self.sqlite_conn.cursor()
                sql = "SELECT * FROM briefing_items WHERE 1=1"
                params = []
                
                if item_type:
                    sql += " AND item_type = ?"
                    params.append(item_type)
                if not include_completed:
                    sql += " AND completed = FALSE"
                
                sql += " ORDER BY priority DESC, due_date"
                cursor.execute(sql, params)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"[Memory] Error getting briefing items: {e}")
            return []
    
    def complete_briefing_item(self, item_id: int) -> bool:
        """Mark a briefing item as complete."""
        try:
            if self.use_supabase:
                self.supabase.table("briefing_items")\
                    .update({"completed": True})\
                    .eq("id", item_id)\
                    .execute()
            else:
                cursor = self.sqlite_conn.cursor()
                cursor.execute(
                    "UPDATE briefing_items SET completed = TRUE WHERE id = ?",
                    (item_id,)
                )
                self.sqlite_conn.commit()
            return True
        except Exception as e:
            print(f"[Memory] Error completing briefing item: {e}")
            return False
    
    # === Utility ===
    
    def get_stats(self) -> Dict:
        """Get memory usage stats."""
        try:
            if self.use_supabase:
                # Supabase doesn't have easy count, skip for now
                return {"backend": "supabase", "status": "connected"}
            else:
                cursor = self.sqlite_conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM conversations")
                conv_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM agent_memory")
                state_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM facts")
                facts_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM briefing_items WHERE completed = FALSE")
                pending_items = cursor.fetchone()[0]
                
                return {
                    "backend": "sqlite",
                    "conversations": conv_count,
                    "agent_states": state_count,
                    "facts": facts_count,
                    "pending_briefing_items": pending_items
                }
        except Exception as e:
            return {"error": str(e)}
    
    def recall(self, query: str, limit: int = 5) -> str:
        """
        Smart recall - search across all memory types.
        Returns formatted string for LLM context.
        """
        results = []
        
        # Search facts
        facts = self.search_facts(query, limit=limit)
        if facts:
            results.append("## Relevant Facts:")
            for f in facts:
                results.append(f"- {f['content']}")
        
        # Get recent conversation context
        conv = self.get_conversation(limit=limit)
        if conv:
            results.append("\n## Recent Conversation:")
            for msg in conv[-limit:]:
                results.append(f"- {msg['role']}: {msg['content'][:200]}...")
        
        return "\n".join(results) if results else "No relevant memories found."


# Singleton
memory = Memory()
