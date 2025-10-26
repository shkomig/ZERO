# 🛠️ ZERO AGENT - קוד מוכן לשימוש

## 📋 תוכן עניינים
1. [Git Operations](#git-operations)
2. [Docker Control](#docker-control)
3. [Email Management](#email-management)
4. [System Monitoring](#system-monitoring)
5. [File Operations](#file-operations)
6. [Web Automation](#web-automation)

---

## 🔄 Git Operations

### tools/git_ops.py

```python
"""
Git operations tool for Zero Agent
Provides safe Git operations with error handling
"""

from git import Repo, GitCommandError
from pathlib import Path
from typing import Optional, List, Dict
import os

class GitOperations:
    """Git operations handler"""
    
    def __init__(self, workspace_dir: Path = Path("./workspace")):
        self.workspace_dir = workspace_dir
        self.workspace_dir.mkdir(exist_ok=True)
        self.current_repo: Optional[Repo] = None
    
    def init_repo(self, name: str) -> Dict:
        """
        Initialize new Git repository
        
        Example:
            git_ops.init_repo("my-project")
        """
        try:
            repo_path = self.workspace_dir / name
            
            if repo_path.exists():
                return {
                    "success": False,
                    "error": f"Directory {name} already exists"
                }
            
            repo_path.mkdir(parents=True)
            repo = Repo.init(repo_path)
            self.current_repo = repo
            
            # Create initial .gitignore
            gitignore = repo_path / ".gitignore"
            gitignore.write_text("""
__pycache__/
*.pyc
.env
.venv/
venv/
node_modules/
.DS_Store
*.log
            """.strip())
            
            return {
                "success": True,
                "path": str(repo_path),
                "message": f"Initialized repository: {name}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def clone_repo(self, url: str, name: Optional[str] = None) -> Dict:
        """
        Clone repository from URL
        
        Example:
            git_ops.clone_repo("https://github.com/user/repo.git")
        """
        try:
            if name is None:
                name = url.split('/')[-1].replace('.git', '')
            
            repo_path = self.workspace_dir / name
            
            if repo_path.exists():
                return {
                    "success": False,
                    "error": f"Directory {name} already exists"
                }
            
            repo = Repo.clone_from(url, repo_path)
            self.current_repo = repo
            
            return {
                "success": True,
                "path": str(repo_path),
                "message": f"Cloned: {url}",
                "branch": repo.active_branch.name
            }
            
        except GitCommandError as e:
            return {
                "success": False,
                "error": f"Git error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def add_files(self, patterns: List[str] = None) -> Dict:
        """
        Add files to staging area
        
        Example:
            git_ops.add_files(['*.py', 'README.md'])
            git_ops.add_files()  # Add all
        """
        if not self.current_repo:
            return {"success": False, "error": "No active repository"}
        
        try:
            if patterns is None or '.' in patterns or '*' in patterns:
                # Add all
                self.current_repo.git.add(A=True)
                added_files = "all files"
            else:
                # Add specific patterns
                for pattern in patterns:
                    self.current_repo.index.add([pattern])
                added_files = ", ".join(patterns)
            
            # Get status
            status = self._get_status()
            
            return {
                "success": True,
                "added": added_files,
                "staged_files": len(status['staged']),
                "status": status
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def commit(self, message: str, author: Optional[Dict] = None) -> Dict:
        """
        Commit staged changes
        
        Example:
            git_ops.commit("Initial commit")
            git_ops.commit("Add feature", author={'name': 'Zero', 'email': 'zero@ai.com'})
        """
        if not self.current_repo:
            return {"success": False, "error": "No active repository"}
        
        try:
            # Check if there are changes to commit
            if not self.current_repo.index.diff("HEAD"):
                return {
                    "success": False,
                    "error": "No changes to commit"
                }
            
            # Set author if provided
            if author:
                commit = self.current_repo.index.commit(
                    message,
                    author=f"{author['name']} <{author['email']}>"
                )
            else:
                commit = self.current_repo.index.commit(message)
            
            return {
                "success": True,
                "commit_hash": commit.hexsha[:7],
                "message": message,
                "files_changed": len(commit.stats.files),
                "insertions": commit.stats.total['insertions'],
                "deletions": commit.stats.total['deletions']
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def push(
        self,
        remote: str = "origin",
        branch: Optional[str] = None
    ) -> Dict:
        """
        Push commits to remote
        
        Example:
            git_ops.push()
            git_ops.push("origin", "main")
        """
        if not self.current_repo:
            return {"success": False, "error": "No active repository"}
        
        try:
            if branch is None:
                branch = self.current_repo.active_branch.name
            
            # Push
            push_info = self.current_repo.remotes[remote].push(branch)
            
            return {
                "success": True,
                "remote": remote,
                "branch": branch,
                "message": f"Pushed to {remote}/{branch}"
            }
            
        except GitCommandError as e:
            return {
                "success": False,
                "error": f"Push failed: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_branch(self, name: str, checkout: bool = True) -> Dict:
        """
        Create new branch
        
        Example:
            git_ops.create_branch("feature/new-tool")
        """
        if not self.current_repo:
            return {"success": False, "error": "No active repository"}
        
        try:
            # Create branch
            new_branch = self.current_repo.create_head(name)
            
            if checkout:
                new_branch.checkout()
            
            return {
                "success": True,
                "branch": name,
                "checked_out": checkout,
                "message": f"Created branch: {name}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def checkout(self, branch: str) -> Dict:
        """
        Switch to branch
        
        Example:
            git_ops.checkout("main")
        """
        if not self.current_repo:
            return {"success": False, "error": "No active repository"}
        
        try:
            self.current_repo.git.checkout(branch)
            
            return {
                "success": True,
                "branch": branch,
                "message": f"Switched to: {branch}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_status(self) -> Dict:
        """Get repository status"""
        if not self.current_repo:
            return {}
        
        return {
            "staged": [item.a_path for item in self.current_repo.index.diff("HEAD")],
            "unstaged": [item.a_path for item in self.current_repo.index.diff(None)],
            "untracked": self.current_repo.untracked_files,
            "branch": self.current_repo.active_branch.name
        }
    
    def status(self) -> Dict:
        """
        Get repository status
        
        Example:
            status = git_ops.status()
        """
        if not self.current_repo:
            return {"success": False, "error": "No active repository"}
        
        try:
            status = self._get_status()
            
            return {
                "success": True,
                **status,
                "clean": (
                    len(status['staged']) == 0 and
                    len(status['unstaged']) == 0 and
                    len(status['untracked']) == 0
                )
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# Usage Example
if __name__ == "__main__":
    git = GitOperations()
    
    # Initialize repo
    result = git.init_repo("test-project")
    print(result)
    
    # Create file
    (Path(result['path']) / "README.md").write_text("# Test Project")
    
    # Add and commit
    git.add_files()
    git.commit("Initial commit")
    
    # Check status
    status = git.status()
    print(status)
```

---

## 🐳 Docker Control

### tools/docker_ops.py

```python
"""
Docker operations for Zero Agent
Safe Docker container and image management
"""

import docker
from docker.errors import DockerException, ImageNotFound, APIError
from typing import List, Dict, Optional
import json

class DockerOperations:
    """Docker operations handler"""
    
    def __init__(self):
        try:
            self.client = docker.from_env()
            # Test connection
            self.client.ping()
            self.connected = True
        except DockerException as e:
            self.connected = False
            self.error = str(e)
    
    def list_containers(self, all: bool = False) -> Dict:
        """
        List Docker containers
        
        Example:
            docker_ops.list_containers()
            docker_ops.list_containers(all=True)  # Include stopped
        """
        if not self.connected:
            return {"success": False, "error": self.error}
        
        try:
            containers = self.client.containers.list(all=all)
            
            result = []
            for container in containers:
                result.append({
                    "id": container.short_id,
                    "name": container.name,
                    "image": container.image.tags[0] if container.image.tags else "unknown",
                    "status": container.status,
                    "ports": container.ports
                })
            
            return {
                "success": True,
                "count": len(result),
                "containers": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def run_container(
        self,
        image: str,
        name: Optional[str] = None,
        ports: Optional[Dict[str, int]] = None,
        environment: Optional[Dict[str, str]] = None,
        detach: bool = True,
        remove: bool = False
    ) -> Dict:
        """
        Run Docker container
        
        Example:
            docker_ops.run_container(
                image="nginx:latest",
                name="my-nginx",
                ports={"80/tcp": 8080}
            )
        """
        if not self.connected:
            return {"success": False, "error": self.error}
        
        try:
            container = self.client.containers.run(
                image=image,
                name=name,
                ports=ports,
                environment=environment,
                detach=detach,
                remove=remove
            )
            
            return {
                "success": True,
                "container_id": container.short_id,
                "name": container.name,
                "image": image,
                "status": container.status,
                "message": f"Started container: {name or container.short_id}"
            }
            
        except ImageNotFound:
            # Try to pull image first
            try:
                print(f"Pulling image: {image}")
                self.client.images.pull(image)
                
                # Retry running
                container = self.client.containers.run(
                    image=image,
                    name=name,
                    ports=ports,
                    environment=environment,
                    detach=detach,
                    remove=remove
                )
                
                return {
                    "success": True,
                    "container_id": container.short_id,
                    "name": container.name,
                    "pulled_image": True,
                    "message": f"Pulled and started: {image}"
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to pull image: {str(e)}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def stop_container(self, container_id: str) -> Dict:
        """
        Stop Docker container
        
        Example:
            docker_ops.stop_container("abc123")
        """
        if not self.connected:
            return {"success": False, "error": self.error}
        
        try:
            container = self.client.containers.get(container_id)
            container.stop()
            
            return {
                "success": True,
                "container_id": container_id,
                "message": f"Stopped: {container_id}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def remove_container(self, container_id: str, force: bool = False) -> Dict:
        """
        Remove Docker container
        
        Example:
            docker_ops.remove_container("abc123", force=True)
        """
        if not self.connected:
            return {"success": False, "error": self.error}
        
        try:
            container = self.client.containers.get(container_id)
            container.remove(force=force)
            
            return {
                "success": True,
                "container_id": container_id,
                "message": f"Removed: {container_id}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def container_logs(
        self,
        container_id: str,
        tail: int = 100
    ) -> Dict:
        """
        Get container logs
        
        Example:
            logs = docker_ops.container_logs("abc123", tail=50)
        """
        if not self.connected:
            return {"success": False, "error": self.error}
        
        try:
            container = self.client.containers.get(container_id)
            logs = container.logs(tail=tail).decode('utf-8')
            
            return {
                "success": True,
                "container_id": container_id,
                "logs": logs
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def exec_command(
        self,
        container_id: str,
        command: str
    ) -> Dict:
        """
        Execute command in container
        
        Example:
            result = docker_ops.exec_command("abc123", "ls -la")
        """
        if not self.connected:
            return {"success": False, "error": self.error}
        
        try:
            container = self.client.containers.get(container_id)
            exec_result = container.exec_run(command)
            
            return {
                "success": True,
                "container_id": container_id,
                "command": command,
                "exit_code": exec_result.exit_code,
                "output": exec_result.output.decode('utf-8')
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# Usage Example
if __name__ == "__main__":
    docker = DockerOperations()
    
    # Run nginx
    result = docker.run_container(
        image="nginx:latest",
        name="test-nginx",
        ports={"80/tcp": 8080}
    )
    print(result)
    
    # List containers
    containers = docker.list_containers()
    print(containers)
    
    # Stop and remove
    if result['success']:
        docker.stop_container(result['container_id'])
        docker.remove_container(result['container_id'])
```

---

## 📧 Email Management

### tools/email.py

```python
"""
Email management for Zero Agent
Gmail API integration for reading, sending, and organizing emails
"""

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64
import os
import pickle
from typing import List, Dict, Optional
from datetime import datetime, timedelta

class EmailOperations:
    """Gmail operations handler"""
    
    # Gmail API scopes
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.modify'
    ]
    
    def __init__(self, credentials_file: str = 'credentials.json'):
        self.credentials_file = credentials_file
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Gmail API"""
        creds = None
        
        # Token file stores user's access and refresh tokens
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, let user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('gmail', 'v1', credentials=creds)
    
    def list_emails(
        self,
        query: Optional[str] = None,
        max_results: int = 10,
        after_date: Optional[datetime] = None
    ) -> Dict:
        """
        List emails with optional filters
        
        Example:
            emails = email_ops.list_emails(query="from:example@gmail.com", max_results=5)
            emails = email_ops.list_emails(after_date=datetime.now() - timedelta(days=7))
        """
        try:
            # Build query
            if after_date:
                date_str = after_date.strftime('%Y/%m/%d')
                query = f"{query or ''} after:{date_str}".strip()
            
            # Get message list
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            # Get full message details
            emails = []
            for msg in messages:
                email = self._get_email_details(msg['id'])
                emails.append(email)
            
            return {
                "success": True,
                "count": len(emails),
                "emails": emails
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_email_details(self, msg_id: str) -> Dict:
        """Get email details"""
        msg = self.service.users().messages().get(
            userId='me',
            id=msg_id,
            format='full'
        ).execute()
        
        headers = msg['payload']['headers']
        
        # Extract headers
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
        
        # Get body
        body = self._get_email_body(msg['payload'])
        
        return {
            "id": msg_id,
            "subject": subject,
            "from": from_email,
            "date": date,
            "snippet": msg.get('snippet', ''),
            "body": body,
            "labels": msg.get('labelIds', [])
        }
    
    def _get_email_body(self, payload: Dict) -> str:
        """Extract email body"""
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        return base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8')
        
        if 'body' in payload and 'data' in payload['body']:
            return base64.urlsafe_b64decode(
                payload['body']['data']
            ).decode('utf-8')
        
        return ""
    
    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[List[str]] = None
    ) -> Dict:
        """
        Send email
        
        Example:
            email_ops.send_email(
                to="recipient@example.com",
                subject="Hello from Zero",
                body="This is a test email"
            )
        """
        try:
            message = MIMEMultipart()
            message['to'] = to
            message['subject'] = subject
            
            if cc:
                message['cc'] = ', '.join(cc)
            
            message.attach(MIMEText(body, 'plain'))
            
            # Encode
            raw = base64.urlsafe_b64encode(
                message.as_bytes()
            ).decode('utf-8')
            
            # Send
            sent = self.service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()
            
            return {
                "success": True,
                "message_id": sent['id'],
                "to": to,
                "subject": subject
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_emails(self, email_ids: List[str]) -> Dict:
        """
        Delete emails
        
        Example:
            email_ops.delete_emails(["msg_123", "msg_456"])
        """
        try:
            deleted = 0
            errors = []
            
            for email_id in email_ids:
                try:
                    self.service.users().messages().trash(
                        userId='me',
                        id=email_id
                    ).execute()
                    deleted += 1
                except Exception as e:
                    errors.append({"id": email_id, "error": str(e)})
            
            return {
                "success": True,
                "deleted": deleted,
                "failed": len(errors),
                "errors": errors
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def filter_spam(self, keywords: List[str]) -> Dict:
        """
        Find and filter emails containing spam keywords
        
        Example:
            result = email_ops.filter_spam(["unsubscribe", "click here", "free gift"])
        """
        try:
            # Build query
            query = " OR ".join([f'subject:"{keyword}"' for keyword in keywords])
            
            # Get emails
            emails_result = self.list_emails(query=query, max_results=50)
            
            if not emails_result['success']:
                return emails_result
            
            spam_emails = emails_result['emails']
            
            return {
                "success": True,
                "found": len(spam_emails),
                "emails": spam_emails,
                "message": f"Found {len(spam_emails)} potential spam emails"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# Usage Example
if __name__ == "__main__":
    email = EmailOperations()
    
    # List recent emails
    emails = email.list_emails(max_results=5)
    print(f"Found {emails['count']} emails")
    
    # Find spam
    spam = email.filter_spam(["unsubscribe", "promotion"])
    print(f"Found {spam['found']} spam emails")
    
    # Send email
    email.send_email(
        to="test@example.com",
        subject="Test from Zero",
        body="This is a test email sent by Zero Agent"
    )
```

---

## 📊 System Monitoring

### tools/system_monitor.py

```python
"""
System monitoring for Zero Agent
CPU, memory, disk, and process monitoring
"""

import psutil
import platform
from typing import Dict, List, Optional
from datetime import datetime

class SystemMonitor:
    """System monitoring operations"""
    
    @staticmethod
    def get_cpu_usage(interval: float = 1.0) -> Dict:
        """
        Get CPU usage
        
        Example:
            cpu = monitor.get_cpu_usage()
        """
        try:
            # Overall CPU
            cpu_percent = psutil.cpu_percent(interval=interval)
            
            # Per core
            cpu_per_core = psutil.cpu_percent(interval=interval, percpu=True)
            
            # CPU frequency
            cpu_freq = psutil.cpu_freq()
            
            # CPU count
            cpu_count_logical = psutil.cpu_count(logical=True)
            cpu_count_physical = psutil.cpu_count(logical=False)
            
            return {
                "success": True,
                "overall": cpu_percent,
                "per_core": cpu_per_core,
                "frequency": {
                    "current": cpu_freq.current,
                    "min": cpu_freq.min,
                    "max": cpu_freq.max
                },
                "cores": {
                    "logical": cpu_count_logical,
                    "physical": cpu_count_physical
                },
                "status": "high" if cpu_percent > 80 else "normal"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def get_memory_usage() -> Dict:
        """
        Get memory usage
        
        Example:
            memory = monitor.get_memory_usage()
        """
        try:
            # RAM
            virtual_mem = psutil.virtual_memory()
            
            # Swap
            swap_mem = psutil.swap_memory()
            
            return {
                "success": True,
                "ram": {
                    "total": virtual_mem.total,
                    "available": virtual_mem.available,
                    "used": virtual_mem.used,
                    "percent": virtual_mem.percent,
                    "total_gb": round(virtual_mem.total / (1024**3), 2),
                    "available_gb": round(virtual_mem.available / (1024**3), 2),
                    "used_gb": round(virtual_mem.used / (1024**3), 2)
                },
                "swap": {
                    "total": swap_mem.total,
                    "used": swap_mem.used,
                    "percent": swap_mem.percent,
                    "total_gb": round(swap_mem.total / (1024**3), 2),
                    "used_gb": round(swap_mem.used / (1024**3), 2)
                },
                "status": "high" if virtual_mem.percent > 85 else "normal"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def get_disk_usage(path: str = "/") -> Dict:
        """
        Get disk usage
        
        Example:
            disk = monitor.get_disk_usage("C:\\")
        """
        try:
            disk = psutil.disk_usage(path)
            
            # All partitions
            partitions = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    partitions.append({
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total_gb": round(usage.total / (1024**3), 2),
                        "used_gb": round(usage.used / (1024**3), 2),
                        "free_gb": round(usage.free / (1024**3), 2),
                        "percent": usage.percent
                    })
                except PermissionError:
                    continue
            
            return {
                "success": True,
                "main_disk": {
                    "path": path,
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": disk.percent,
                    "total_gb": round(disk.total / (1024**3), 2),
                    "used_gb": round(disk.used / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2)
                },
                "partitions": partitions,
                "status": "low" if disk.percent > 90 else "normal"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def get_process_list(sort_by: str = "memory") -> Dict:
        """
        Get running processes
        
        Example:
            processes = monitor.get_process_list(sort_by="cpu")
        """
        try:
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_percent', 'cpu_percent']):
                try:
                    pinfo = proc.info
                    processes.append({
                        "pid": pinfo['pid'],
                        "name": pinfo['name'],
                        "user": pinfo['username'],
                        "memory_percent": round(pinfo['memory_percent'], 2),
                        "cpu_percent": round(pinfo['cpu_percent'], 2)
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort
            if sort_by == "memory":
                processes.sort(key=lambda x: x['memory_percent'], reverse=True)
            elif sort_by == "cpu":
                processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            
            # Top 10
            top_processes = processes[:10]
            
            return {
                "success": True,
                "total_processes": len(processes),
                "top_processes": top_processes,
                "sorted_by": sort_by
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def get_system_info() -> Dict:
        """
        Get general system information
        
        Example:
            info = monitor.get_system_info()
        """
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            
            return {
                "success": True,
                "platform": platform.system(),
                "platform_release": platform.release(),
                "platform_version": platform.version(),
                "architecture": platform.machine(),
                "processor": platform.processor(),
                "hostname": platform.node(),
                "boot_time": boot_time.isoformat(),
                "uptime_seconds": (datetime.now() - boot_time).total_seconds()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @classmethod
    def get_full_report(cls) -> Dict:
        """
        Get complete system report
        
        Example:
            report = SystemMonitor.get_full_report()
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "system": cls.get_system_info(),
            "cpu": cls.get_cpu_usage(),
            "memory": cls.get_memory_usage(),
            "disk": cls.get_disk_usage(),
            "processes": cls.get_process_list()
        }

# Usage Example
if __name__ == "__main__":
    monitor = SystemMonitor()
    
    # Get full report
    report = monitor.get_full_report()
    
    # Print summary
    print(f"CPU: {report['cpu']['overall']}%")
    print(f"Memory: {report['memory']['ram']['percent']}%")
    print(f"Disk: {report['disk']['main_disk']['percent']}%")
    print(f"\nTop Processes:")
    for proc in report['processes']['top_processes'][:5]:
        print(f"  {proc['name']}: {proc['memory_percent']}% RAM")
```

---

## 📁 קבצים מוכנים להעתקה

כל הקבצים האלה מוכנים לשימוש מיידי:
1. העתק לתיקייה `tools/`
2. התקן dependencies הנדרשים
3. הוסף auth credentials כנדרש (Gmail, Docker)
4. התחל להשתמש!

### Dependencies נוספים

```bash
# Git
pip install gitpython

# Docker
pip install docker

# Email (Gmail)
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

# System monitoring
pip install psutil
```

---

בהצלחה! 🎉
