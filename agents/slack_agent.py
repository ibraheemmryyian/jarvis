"""
Slack Agent for Jarvis v2
Slack integration for team communication and notifications.
"""
import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from .config import WORKSPACE_DIR

# Optional: Slack SDK
try:
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError
    SLACK_SDK_AVAILABLE = True
except ImportError:
    SLACK_SDK_AVAILABLE = False


class SlackAgent:
    """
    Slack integration agent.
    
    Features:
    - Send messages to channels
    - Send DMs to users
    - Read channel history
    - Post rich messages (blocks)
    - Webhook notifications
    - Bot commands handling
    """
    
    def __init__(self):
        self.client = None
        self.webhook_url = None
        self.bot_token = os.environ.get("SLACK_BOT_TOKEN")
        self.webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
        
        # Initialize SDK client if available
        if SLACK_SDK_AVAILABLE and self.bot_token:
            try:
                self.client = WebClient(token=self.bot_token)
                print("[SlackAgent] Connected with Bot Token")
            except Exception as e:
                print(f"[SlackAgent] SDK init failed: {e}")
        elif self.webhook_url:
            print("[SlackAgent] Webhook mode only")
        else:
            print("[SlackAgent] Not configured (set SLACK_BOT_TOKEN or SLACK_WEBHOOK_URL)")
    
    def is_connected(self) -> bool:
        """Check if Slack is connected."""
        return self.client is not None or self.webhook_url is not None
    
    # === Sending Messages ===
    
    def send_message(self, channel: str, text: str, 
                     thread_ts: str = None) -> Dict:
        """
        Send a message to a channel.
        
        Args:
            channel: Channel name (with #) or ID
            text: Message text
            thread_ts: Thread timestamp for replies
        """
        if self.client:
            try:
                result = self.client.chat_postMessage(
                    channel=channel,
                    text=text,
                    thread_ts=thread_ts
                )
                return {
                    "success": True,
                    "ts": result["ts"],
                    "channel": result["channel"]
                }
            except SlackApiError as e:
                return {"success": False, "error": str(e)}
        elif self.webhook_url:
            return self._send_webhook(text)
        else:
            return {"success": False, "error": "Slack not configured"}
    
    def send_dm(self, user_id: str, text: str) -> Dict:
        """Send a direct message to a user."""
        if not self.client:
            return {"success": False, "error": "Bot token required for DMs"}
        
        try:
            # Open DM channel
            result = self.client.conversations_open(users=[user_id])
            channel = result["channel"]["id"]
            
            # Send message
            msg_result = self.client.chat_postMessage(
                channel=channel,
                text=text
            )
            return {
                "success": True,
                "ts": msg_result["ts"],
                "channel": channel
            }
        except SlackApiError as e:
            return {"success": False, "error": str(e)}
    
    def send_rich_message(self, channel: str, blocks: List[Dict],
                          text: str = "Message from Jarvis") -> Dict:
        """
        Send a rich message with blocks.
        
        Args:
            channel: Channel name or ID
            blocks: Slack Block Kit blocks
            text: Fallback text
        """
        if not self.client:
            return self._send_webhook(text)
        
        try:
            result = self.client.chat_postMessage(
                channel=channel,
                text=text,
                blocks=blocks
            )
            return {
                "success": True,
                "ts": result["ts"],
                "channel": result["channel"]
            }
        except SlackApiError as e:
            return {"success": False, "error": str(e)}
    
    def _send_webhook(self, text: str, blocks: List[Dict] = None) -> Dict:
        """Send message via webhook (fallback)."""
        if not self.webhook_url:
            return {"success": False, "error": "No webhook URL configured"}
        
        try:
            payload = {"text": text}
            if blocks:
                payload["blocks"] = blocks
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                return {"success": True, "method": "webhook"}
            else:
                return {"success": False, "error": f"Status {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # === Reading Messages ===
    
    def get_channel_history(self, channel: str, limit: int = 20) -> List[Dict]:
        """Get recent messages from a channel."""
        if not self.client:
            return [{"error": "Bot token required to read messages"}]
        
        try:
            result = self.client.conversations_history(
                channel=channel,
                limit=limit
            )
            
            messages = []
            for msg in result.get("messages", []):
                messages.append({
                    "user": msg.get("user"),
                    "text": msg.get("text", ""),
                    "ts": msg.get("ts"),
                    "timestamp": datetime.fromtimestamp(
                        float(msg.get("ts", 0))
                    ).isoformat()
                })
            
            return messages
        except SlackApiError as e:
            return [{"error": str(e)}]
    
    def search_messages(self, query: str, count: int = 10) -> List[Dict]:
        """Search messages across channels."""
        if not self.client:
            return [{"error": "Bot token required for search"}]
        
        try:
            result = self.client.search_messages(
                query=query,
                count=count
            )
            
            matches = []
            for match in result.get("messages", {}).get("matches", []):
                matches.append({
                    "channel": match.get("channel", {}).get("name"),
                    "user": match.get("username"),
                    "text": match.get("text", ""),
                    "ts": match.get("ts")
                })
            
            return matches
        except SlackApiError as e:
            return [{"error": str(e)}]
    
    # === Channel Management ===
    
    def list_channels(self, limit: int = 100) -> List[Dict]:
        """List all public channels."""
        if not self.client:
            return [{"error": "Bot token required"}]
        
        try:
            result = self.client.conversations_list(
                types="public_channel",
                limit=limit
            )
            
            channels = []
            for ch in result.get("channels", []):
                channels.append({
                    "id": ch.get("id"),
                    "name": ch.get("name"),
                    "topic": ch.get("topic", {}).get("value", ""),
                    "member_count": ch.get("num_members", 0)
                })
            
            return channels
        except SlackApiError as e:
            return [{"error": str(e)}]
    
    def get_channel_info(self, channel: str) -> Dict:
        """Get info about a channel."""
        if not self.client:
            return {"error": "Bot token required"}
        
        try:
            result = self.client.conversations_info(channel=channel)
            ch = result.get("channel", {})
            
            return {
                "id": ch.get("id"),
                "name": ch.get("name"),
                "topic": ch.get("topic", {}).get("value", ""),
                "purpose": ch.get("purpose", {}).get("value", ""),
                "created": ch.get("created"),
                "member_count": ch.get("num_members", 0)
            }
        except SlackApiError as e:
            return {"error": str(e)}
    
    # === User Management ===
    
    def list_users(self, limit: int = 100) -> List[Dict]:
        """List workspace users."""
        if not self.client:
            return [{"error": "Bot token required"}]
        
        try:
            result = self.client.users_list(limit=limit)
            
            users = []
            for user in result.get("members", []):
                if not user.get("is_bot") and not user.get("deleted"):
                    users.append({
                        "id": user.get("id"),
                        "name": user.get("name"),
                        "real_name": user.get("real_name"),
                        "email": user.get("profile", {}).get("email"),
                        "title": user.get("profile", {}).get("title")
                    })
            
            return users
        except SlackApiError as e:
            return [{"error": str(e)}]
    
    def get_user_info(self, user_id: str) -> Dict:
        """Get info about a user."""
        if not self.client:
            return {"error": "Bot token required"}
        
        try:
            result = self.client.users_info(user=user_id)
            user = result.get("user", {})
            
            return {
                "id": user.get("id"),
                "name": user.get("name"),
                "real_name": user.get("real_name"),
                "email": user.get("profile", {}).get("email"),
                "title": user.get("profile", {}).get("title"),
                "status": user.get("profile", {}).get("status_text")
            }
        except SlackApiError as e:
            return {"error": str(e)}
    
    # === Reactions ===
    
    def add_reaction(self, channel: str, timestamp: str, emoji: str) -> Dict:
        """Add a reaction to a message."""
        if not self.client:
            return {"success": False, "error": "Bot token required"}
        
        try:
            self.client.reactions_add(
                channel=channel,
                timestamp=timestamp,
                name=emoji
            )
            return {"success": True}
        except SlackApiError as e:
            return {"success": False, "error": str(e)}
    
    # === Notifications (Pre-built templates) ===
    
    def notify_task_complete(self, channel: str, task_name: str, 
                             result: str = "Success") -> Dict:
        """Send a task completion notification."""
        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "✅ Task Complete"}
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Task:*\n{task_name}"},
                    {"type": "mrkdwn", "text": f"*Result:*\n{result}"}
                ]
            },
            {
                "type": "context",
                "elements": [
                    {"type": "mrkdwn", "text": f"Completed by Jarvis at {datetime.now().strftime('%H:%M')}"}
                ]
            }
        ]
        
        return self.send_rich_message(
            channel, blocks, f"Task Complete: {task_name}")
    
    def notify_error(self, channel: str, error_type: str, 
                     details: str) -> Dict:
        """Send an error notification."""
        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "🚨 Error Alert"}
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*{error_type}*\n```{details[:500]}```"}
            }
        ]
        
        return self.send_rich_message(
            channel, blocks, f"Error: {error_type}")
    
    def notify_daily_summary(self, channel: str, summary: str) -> Dict:
        """Send daily summary notification."""
        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "📊 Daily Summary"}
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": summary}
            },
            {
                "type": "divider"
            },
            {
                "type": "context",
                "elements": [
                    {"type": "mrkdwn", "text": f"Generated by Jarvis | {datetime.now().strftime('%B %d, %Y')}"}
                ]
            }
        ]
        
        return self.send_rich_message(
            channel, blocks, "Daily Summary from Jarvis")
    
    # === Mock Data (for testing without connection) ===
    
    def mock_channels(self) -> List[Dict]:
        """Return mock channels for testing."""
        return [
            {"id": "C001", "name": "general", "topic": "Company announcements", "member_count": 50},
            {"id": "C002", "name": "engineering", "topic": "Tech discussions", "member_count": 20},
            {"id": "C003", "name": "jarvis-alerts", "topic": "AI notifications", "member_count": 10}
        ]
    
    def mock_messages(self) -> List[Dict]:
        """Return mock messages for testing."""
        return [
            {"user": "U001", "text": "Hey team, the new feature is ready!", "ts": "1702800000.000100"},
            {"user": "U002", "text": "Great work! Let's deploy.", "ts": "1702800100.000200"},
            {"user": "jarvis", "text": "Deployment complete. ✅", "ts": "1702800200.000300"}
        ]


# Singleton
slack_agent = SlackAgent()
