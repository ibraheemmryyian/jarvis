"""
Email Agent for Jarvis v2
Gmail/Outlook integration for reading and sending emails.
"""
import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from .config import WORKSPACE_DIR, LM_STUDIO_URL
import requests

# Optional: Gmail API (requires google-auth-oauthlib, google-api-python-client)
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    import base64
    from email.mime.text import MIMEText
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False


class EmailAgent:
    """
    Email management agent.
    
    Features:
    - Gmail OAuth integration
    - Read inbox/unread
    - Send emails
    - Email summarization
    - Auto-categorization
    - Draft assistant
    """
    
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
    
    def __init__(self):
        self.creds = None
        self.service = None
        self.credentials_path = os.path.join(WORKSPACE_DIR, "credentials")
        os.makedirs(self.credentials_path, exist_ok=True)
        
        # Try to load existing credentials
        self._load_credentials()
    
    def _load_credentials(self):
        """Load Gmail credentials if available."""
        if not GMAIL_AVAILABLE:
            print("[EmailAgent] Google API libraries not installed")
            return
        
        token_path = os.path.join(self.credentials_path, "gmail_token.json")
        
        if os.path.exists(token_path):
            self.creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
        
        # Refresh if expired
        if self.creds and self.creds.expired and self.creds.refresh_token:
            try:
                self.creds.refresh(Request())
                self._save_credentials()
            except Exception as e:
                print(f"[EmailAgent] Token refresh failed: {e}")
                self.creds = None
        
        # Build service if we have valid credentials
        if self.creds and self.creds.valid:
            try:
                self.service = build('gmail', 'v1', credentials=self.creds)
                print("[EmailAgent] Gmail connected")
            except Exception as e:
                print(f"[EmailAgent] Service build failed: {e}")
    
    def _save_credentials(self):
        """Save credentials to file."""
        token_path = os.path.join(self.credentials_path, "gmail_token.json")
        with open(token_path, 'w') as f:
            f.write(self.creds.to_json())
    
    def authenticate(self, credentials_file: str = None) -> Dict:
        """
        Authenticate with Gmail OAuth.
        
        Args:
            credentials_file: Path to OAuth client credentials JSON
        """
        if not GMAIL_AVAILABLE:
            return {"success": False, "error": "Google API libraries not installed"}
        
        creds_file = credentials_file or os.path.join(
            self.credentials_path, "gmail_credentials.json"
        )
        
        if not os.path.exists(creds_file):
            return {
                "success": False, 
                "error": f"Credentials file not found: {creds_file}",
                "instructions": "Download OAuth credentials from Google Cloud Console"
            }
        
        try:
            flow = InstalledAppFlow.from_client_secrets_file(creds_file, self.SCOPES)
            self.creds = flow.run_local_server(port=0)
            self._save_credentials()
            self.service = build('gmail', 'v1', credentials=self.creds)
            
            return {"success": True, "message": "Gmail authenticated successfully"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def is_connected(self) -> bool:
        """Check if Gmail is connected."""
        return self.service is not None
    
    def get_unread(self, max_results: int = 10) -> List[Dict]:
        """Get unread emails."""
        if not self.is_connected():
            return [{"error": "Gmail not connected. Call authenticate() first."}]
        
        try:
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for msg in messages:
                email_data = self._get_email_details(msg['id'])
                if email_data:
                    emails.append(email_data)
            
            return emails
        except Exception as e:
            return [{"error": str(e)}]
    
    def get_inbox(self, max_results: int = 20) -> List[Dict]:
        """Get recent inbox emails."""
        if not self.is_connected():
            return [{"error": "Gmail not connected"}]
        
        try:
            results = self.service.users().messages().list(
                userId='me',
                labelIds=['INBOX'],
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for msg in messages:
                email_data = self._get_email_details(msg['id'])
                if email_data:
                    emails.append(email_data)
            
            return emails
        except Exception as e:
            return [{"error": str(e)}]
    
    def _get_email_details(self, msg_id: str) -> Optional[Dict]:
        """Get details of a specific email."""
        try:
            msg = self.service.users().messages().get(
                userId='me', id=msg_id, format='full'
            ).execute()
            
            headers = msg.get('payload', {}).get('headers', [])
            
            def get_header(name):
                for h in headers:
                    if h['name'].lower() == name.lower():
                        return h['value']
                return ""
            
            # Get body
            body = ""
            payload = msg.get('payload', {})
            
            if 'body' in payload and payload['body'].get('data'):
                body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
            elif 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain' and part['body'].get('data'):
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
            
            return {
                "id": msg_id,
                "thread_id": msg.get('threadId'),
                "from": get_header('From'),
                "to": get_header('To'),
                "subject": get_header('Subject'),
                "date": get_header('Date'),
                "snippet": msg.get('snippet', ''),
                "body": body[:2000],  # Limit body size
                "labels": msg.get('labelIds', [])
            }
        except Exception as e:
            print(f"[EmailAgent] Error getting email {msg_id}: {e}")
            return None
    
    def send(self, to: str, subject: str, body: str) -> Dict:
        """Send an email."""
        if not self.is_connected():
            return {"success": False, "error": "Gmail not connected"}
        
        try:
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            result = self.service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()
            
            return {
                "success": True,
                "message_id": result.get('id'),
                "thread_id": result.get('threadId')
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def summarize_inbox(self, count: int = 5) -> str:
        """Get a summary of recent inbox emails."""
        emails = self.get_inbox(count)
        
        if not emails or (len(emails) == 1 and "error" in emails[0]):
            return "Unable to fetch emails. Gmail may not be connected."
        
        summary = f"## Inbox Summary ({len(emails)} emails)\n\n"
        
        for i, email in enumerate(emails, 1):
            summary += f"**{i}. {email.get('subject', 'No subject')}**\n"
            summary += f"   From: {email.get('from', 'Unknown')}\n"
            summary += f"   {email.get('snippet', '')[:100]}...\n\n"
        
        return summary
    
    def mock_inbox(self) -> List[Dict]:
        """Return mock emails for testing without Gmail connection."""
        return [
            {
                "id": "mock_1",
                "from": "investor@vc.com",
                "subject": "Re: Jarvis AI - Investment Opportunity",
                "snippet": "Thanks for sending over the deck. We'd love to schedule a call...",
                "date": datetime.now().isoformat()
            },
            {
                "id": "mock_2",
                "from": "support@github.com",
                "subject": "Your pull request was merged",
                "snippet": "Your changes have been merged into main...",
                "date": datetime.now().isoformat()
            },
            {
                "id": "mock_3",
                "from": "newsletter@producthunt.com",
                "subject": "Top Products This Week",
                "snippet": "Check out the trending products...",
                "date": datetime.now().isoformat()
            }
        ]


# Singleton
email_agent = EmailAgent()
