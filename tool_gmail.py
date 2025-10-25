"""
Gmail Tool for Zero Agent
==========================
Read, search, and send emails via Gmail API

Requires:
    pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
"""

import os
import pickle
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import base64
from email.mime.text import MIMEText

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False
    print("⚠️  Gmail libraries not installed. Run: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")


class GmailTool:
    """
    Gmail integration for Zero Agent
    """
    
    # Gmail API scopes
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.modify'
    ]
    
    def __init__(self, credentials_path: Path = Path("credentials.json")):
        """
        Initialize Gmail tool
        
        Args:
            credentials_path: Path to Google OAuth credentials JSON
        """
        if not GMAIL_AVAILABLE:
            raise ImportError("Gmail libraries not installed")
        
        self.credentials_path = credentials_path
        self.token_path = Path("token.pickle")
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """
        Authenticate with Gmail API
        """
        creds = None
        
        # Load existing token
        if self.token_path.exists():
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # Refresh or get new token
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not self.credentials_path.exists():
                    raise FileNotFoundError(
                        f"credentials.json not found at {self.credentials_path}\n"
                        "Download from: https://console.cloud.google.com/apis/credentials"
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), 
                    self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save token
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('gmail', 'v1', credentials=creds)
    
    def search_emails(self, 
                     query: str,
                     max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search emails
        
        Args:
            query: Gmail search query (e.g., "from:john@example.com")
            max_results: Maximum number of results
            
        Returns:
            List of email summaries
        """
        try:
            results = self.service.users().messages().list(
                userId='me',
                q=query,
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
            print(f"Error searching emails: {str(e)}")
            return []
    
    def get_recent_emails(self, 
                         count: int = 10,
                         unread_only: bool = False) -> List[Dict[str, Any]]:
        """
        Get recent emails
        
        Args:
            count: Number of emails to retrieve
            unread_only: Only unread emails
            
        Returns:
            List of email summaries
        """
        query = "is:unread" if unread_only else ""
        return self.search_emails(query, max_results=count)
    
    def _get_email_details(self, message_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed email information
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            headers = message['payload']['headers']
            
            # Extract headers
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
            
            # Extract body
            body = self._get_email_body(message['payload'])
            
            # Check if unread
            labels = message.get('labelIds', [])
            is_unread = 'UNREAD' in labels
            
            return {
                'id': message_id,
                'subject': subject,
                'from': sender,
                'date': date,
                'body': body[:500] + '...' if len(body) > 500 else body,
                'snippet': message.get('snippet', ''),
                'unread': is_unread,
                'labels': labels
            }
            
        except Exception as e:
            print(f"Error getting email details: {str(e)}")
            return None
    
    def _get_email_body(self, payload: Dict) -> str:
        """
        Extract email body from payload
        """
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8')
                        break
        elif 'body' in payload and 'data' in payload['body']:
            body = base64.urlsafe_b64decode(
                payload['body']['data']
            ).decode('utf-8')
        
        return body
    
    def send_email(self,
                   to: str,
                   subject: str,
                   body: str,
                   cc: Optional[str] = None,
                   bcc: Optional[str] = None) -> bool:
        """
        Send email
        
        Args:
            to: Recipient email
            subject: Email subject
            body: Email body
            cc: CC recipients (comma-separated)
            bcc: BCC recipients (comma-separated)
            
        Returns:
            Success status
        """
        try:
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            
            if cc:
                message['cc'] = cc
            if bcc:
                message['bcc'] = bcc
            
            raw_message = base64.urlsafe_b64encode(
                message.as_bytes()
            ).decode('utf-8')
            
            self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            return True
            
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False
    
    def mark_as_read(self, message_id: str) -> bool:
        """
        Mark email as read
        """
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True
        except Exception as e:
            print(f"Error marking as read: {str(e)}")
            return False
    
    def mark_as_unread(self, message_id: str) -> bool:
        """
        Mark email as unread
        """
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'addLabelIds': ['UNREAD']}
            ).execute()
            return True
        except Exception as e:
            print(f"Error marking as unread: {str(e)}")
            return False
    
    def delete_email(self, message_id: str) -> bool:
        """
        Delete email (move to trash)
        """
        try:
            self.service.users().messages().trash(
                userId='me',
                id=message_id
            ).execute()
            return True
        except Exception as e:
            print(f"Error deleting email: {str(e)}")
            return False
    
    def get_email_stats(self) -> Dict[str, int]:
        """
        Get email statistics
        """
        try:
            profile = self.service.users().getProfile(userId='me').execute()
            
            # Count unread
            unread = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=1
            ).execute()
            
            return {
                'total_messages': profile.get('messagesTotal', 0),
                'total_threads': profile.get('threadsTotal', 0),
                'unread_estimate': unread.get('resultSizeEstimate', 0),
                'email_address': profile.get('emailAddress', 'Unknown')
            }
            
        except Exception as e:
            print(f"Error getting stats: {str(e)}")
            return {}


# Convenience functions for Zero Agent

def gmail_search(query: str, max_results: int = 10) -> str:
    """
    Search emails (for Zero Agent)
    """
    try:
        tool = GmailTool()
        emails = tool.search_emails(query, max_results)
        
        if not emails:
            return "No emails found"
        
        result = f"Found {len(emails)} emails:\n\n"
        for i, email in enumerate(emails, 1):
            result += f"{i}. From: {email['from']}\n"
            result += f"   Subject: {email['subject']}\n"
            result += f"   Date: {email['date']}\n"
            result += f"   Snippet: {email['snippet']}\n"
            result += f"   Unread: {'Yes' if email['unread'] else 'No'}\n\n"
        
        return result
        
    except Exception as e:
        return f"Error: {str(e)}"


def gmail_recent(count: int = 10, unread_only: bool = False) -> str:
    """
    Get recent emails (for Zero Agent)
    """
    try:
        tool = GmailTool()
        emails = tool.get_recent_emails(count, unread_only)
        
        if not emails:
            return "No emails found"
        
        result = f"Recent {'unread ' if unread_only else ''}emails:\n\n"
        for i, email in enumerate(emails, 1):
            result += f"{i}. From: {email['from']}\n"
            result += f"   Subject: {email['subject']}\n"
            result += f"   Date: {email['date']}\n\n"
        
        return result
        
    except Exception as e:
        return f"Error: {str(e)}"


def gmail_send(to: str, subject: str, body: str) -> str:
    """
    Send email (for Zero Agent)
    """
    try:
        tool = GmailTool()
        success = tool.send_email(to, subject, body)
        return "✓ Email sent successfully!" if success else "✗ Failed to send email"
    except Exception as e:
        return f"Error: {str(e)}"


# Test
if __name__ == "__main__":
    if not GMAIL_AVAILABLE:
        print("Install required libraries first:")
        print("pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    else:
        print("Gmail Tool Test")
        print("="*70)
        
        try:
            tool = GmailTool()
            print("✓ Authenticated with Gmail")
            
            # Get stats
            stats = tool.get_email_stats()
            print(f"\n📊 Stats:")
            print(f"   Email: {stats.get('email_address')}")
            print(f"   Total messages: {stats.get('total_messages')}")
            print(f"   Unread: {stats.get('unread_estimate')}")
            
            # Get recent emails
            print("\n📧 Recent emails:")
            emails = tool.get_recent_emails(count=5)
            for i, email in enumerate(emails, 1):
                print(f"\n{i}. {email['subject']}")
                print(f"   From: {email['from']}")
                print(f"   Unread: {'Yes' if email['unread'] else 'No'}")
            
        except Exception as e:
            print(f"Error: {str(e)}")
