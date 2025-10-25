"""
Git operations tool for Zero Agent
Provides safe Git operations with error handling
"""

from git import Repo, GitCommandError
from pathlib import Path
from typing import Optional, List, Dict


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
    
    def add_files(self, patterns: Optional[List[str]] = None) -> Dict:
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

