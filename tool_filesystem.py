"""
FileSystem Tool
===============
Tool for file operations: create, read, list, delete
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
import json


class FileSystemTool:
    """
    Tool for interacting with the file system
    Safe operations within workspace only
    """
    
    def __init__(self, workspace: Path):
        self.workspace = Path(workspace)
        self.workspace.mkdir(exist_ok=True)
        
    def get_safe_path(self, path: str) -> Path:
        """
        Ensure path is within workspace (security)
        """
        target = (self.workspace / path).resolve()
        
        # Check if path is within workspace
        try:
            target.relative_to(self.workspace.resolve())
            return target
        except ValueError:
            raise ValueError(f"Path {path} is outside workspace")
    
    def create_file(self, path: str, content: str) -> Dict[str, Any]:
        """
        Create a new file with content
        
        Args:
            path: Relative path within workspace
            content: File content
            
        Returns:
            Result dictionary with success status
        """
        try:
            safe_path = self.get_safe_path(path)
            
            # Create parent directories if needed
            safe_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            safe_path.write_text(content, encoding='utf-8')
            
            return {
                "success": True,
                "message": f"Created file: {path}",
                "path": str(safe_path),
                "size": len(content)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def read_file(self, path: str) -> Dict[str, Any]:
        """
        Read file content
        
        Args:
            path: Relative path within workspace
            
        Returns:
            Result dictionary with file content
        """
        try:
            safe_path = self.get_safe_path(path)
            
            if not safe_path.exists():
                return {
                    "success": False,
                    "error": f"File not found: {path}"
                }
            
            content = safe_path.read_text(encoding='utf-8')
            
            return {
                "success": True,
                "content": content,
                "path": str(safe_path),
                "size": len(content),
                "lines": len(content.split('\n'))
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_files(self, directory: str = ".") -> Dict[str, Any]:
        """
        List files in directory
        
        Args:
            directory: Relative path to directory
            
        Returns:
            List of files and directories
        """
        try:
            safe_path = self.get_safe_path(directory)
            
            if not safe_path.exists():
                return {
                    "success": False,
                    "error": f"Directory not found: {directory}"
                }
            
            if not safe_path.is_dir():
                return {
                    "success": False,
                    "error": f"Not a directory: {directory}"
                }
            
            items = []
            for item in safe_path.iterdir():
                items.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else 0
                })
            
            return {
                "success": True,
                "directory": str(safe_path),
                "items": items,
                "count": len(items)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_file(self, path: str) -> Dict[str, Any]:
        """
        Delete a file
        
        Args:
            path: Relative path within workspace
            
        Returns:
            Result dictionary
        """
        try:
            safe_path = self.get_safe_path(path)
            
            if not safe_path.exists():
                return {
                    "success": False,
                    "error": f"File not found: {path}"
                }
            
            if safe_path.is_dir():
                return {
                    "success": False,
                    "error": f"Cannot delete directory with this method: {path}"
                }
            
            safe_path.unlink()
            
            return {
                "success": True,
                "message": f"Deleted file: {path}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def file_exists(self, path: str) -> Dict[str, Any]:
        """
        Check if file exists
        
        Args:
            path: Relative path within workspace
            
        Returns:
            Result with existence status
        """
        try:
            safe_path = self.get_safe_path(path)
            
            return {
                "success": True,
                "exists": safe_path.exists(),
                "is_file": safe_path.is_file() if safe_path.exists() else False,
                "is_directory": safe_path.is_dir() if safe_path.exists() else False
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_info(self) -> str:
        """
        Get tool information for LLM
        """
        return """FileSystem Tool - Available operations:
        
1. create_file(path, content) - Create a new file
   Example: create_file("test.txt", "Hello World")
   
2. read_file(path) - Read file content
   Example: read_file("test.txt")
   
3. list_files(directory) - List files in directory
   Example: list_files(".")
   
4. delete_file(path) - Delete a file
   Example: delete_file("test.txt")
   
5. file_exists(path) - Check if file exists
   Example: file_exists("test.txt")

All paths are relative to workspace directory."""


# Test the tool
if __name__ == "__main__":
    print("FileSystem Tool Test")
    print("="*60)
    
    # Create tool
    workspace = Path("workspace")
    fs = FileSystemTool(workspace)
    
    print("\n1. Creating a test file...")
    result = fs.create_file("test.txt", "Hello, World!\nThis is a test.")
    print(f"   Result: {result}")
    
    print("\n2. Reading the file...")
    result = fs.read_file("test.txt")
    print(f"   Content: {result.get('content', 'N/A')}")
    
    print("\n3. Listing files...")
    result = fs.list_files(".")
    print(f"   Files: {result.get('items', [])}")
    
    print("\n4. Checking if file exists...")
    result = fs.file_exists("test.txt")
    print(f"   Exists: {result.get('exists', False)}")
    
    print("\n5. Deleting the file...")
    result = fs.delete_file("test.txt")
    print(f"   Result: {result}")
    
    print("\n" + "="*60)
    print("✅ FileSystem Tool is ready!")
