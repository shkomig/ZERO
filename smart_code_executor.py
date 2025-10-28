"""
Smart Code Executor for Zero Agent
===================================
Automatically executes code generation requests and creates files
"""

import re
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import json


class SmartCodeExecutor:
    """
    Intelligent code executor that:
    1. Detects code in LLM responses
    2. Extracts files and their content
    3. Creates project structure automatically
    4. Executes if requested
    """
    
    def __init__(self, workspace_root: str = "workspace/projects"):
        self.workspace = Path(workspace_root)
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.last_project = None
    
    def extract_code_blocks(self, response: str) -> List[Dict[str, str]]:
        """
        Extract code blocks from markdown response
        
        Returns:
            List of dicts with 'language', 'filename', 'code'
        """
        # Pattern: ```language:filename or ```language
        pattern = r'```(\w+)(?::([^\n]+))?\n(.*?)```'
        matches = re.findall(pattern, response, re.DOTALL)
        
        code_blocks = []
        for i, (lang, filename, code) in enumerate(matches):
            if not filename:
                # Auto-generate filename based on language
                ext_map = {
                    'python': 'py', 'javascript': 'js', 'typescript': 'ts',
                    'html': 'html', 'css': 'css', 'bash': 'sh', 'sql': 'sql',
                    'json': 'json', 'yaml': 'yaml', 'dockerfile': 'Dockerfile'
                }
                ext = ext_map.get(lang.lower(), 'txt')
                filename = f"file_{i+1}.{ext}"
            
            code_blocks.append({
                'language': lang,
                'filename': filename.strip(),
                'code': code.strip()
            })
        
        return code_blocks
    
    def create_project(self, 
                      project_name: str,
                      files: List[Dict[str, str]],
                      description: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a project with multiple files
        
        Args:
            project_name: Name of the project folder
            files: List of file dicts
            description: Optional project description
        
        Returns:
            Result dict with paths and status
        """
        # Sanitize project name
        safe_name = re.sub(r'[^\w\-]', '_', project_name.lower())
        project_path = self.workspace / safe_name
        
        # Create project directory
        project_path.mkdir(parents=True, exist_ok=True)
        
        created_files = []
        errors = []
        
        # Create each file
        for file_info in files:
            try:
                filename = file_info['filename']
                code = file_info['code']
                
                # Handle subdirectories
                file_path = project_path / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Write file
                file_path.write_text(code, encoding='utf-8')
                created_files.append(str(file_path.relative_to(self.workspace)))
                
            except Exception as e:
                errors.append(f"Failed to create {filename}: {str(e)}")
        
        # Create README if description provided
        if description:
            readme_path = project_path / "README.md"
            readme_path.write_text(f"# {project_name}\n\n{description}\n", 
                                  encoding='utf-8')
            created_files.append(str(readme_path.relative_to(self.workspace)))
        
        self.last_project = str(project_path)
        
        return {
            'success': len(errors) == 0,
            'project_path': str(project_path),
            'created_files': created_files,
            'errors': errors,
            'file_count': len(created_files)
        }
    
    def auto_execute_from_response(self, 
                                   response: str,
                                   project_name: Optional[str] = None
                                   ) -> Optional[Dict[str, Any]]:
        """
        Automatically detect and execute code generation from LLM response
        
        Args:
            response: LLM response text
            project_name: Optional project name (auto-generated if None)
        
        Returns:
            Execution result or None if no code detected
        """
        # Extract code blocks
        code_blocks = self.extract_code_blocks(response)
        
        if not code_blocks:
            return None  # No code to execute
        
        # Auto-generate project name if not provided
        if not project_name:
            # Try to extract from response
            name_patterns = [
                r'(?:create|build|make)\s+(?:a|an)?\s*(\w+)\s+(?:app|application|project)',
                r'(?:flask|django|react|vue)\s+(\w+)',
                r'project\s+name[:\s]+(\w+)'
            ]
            for pattern in name_patterns:
                match = re.search(pattern, response, re.IGNORECASE)
                if match:
                    project_name = match.group(1)
                    break
            
            if not project_name:
                # Default name based on language
                main_lang = code_blocks[0]['language']
                project_name = f"{main_lang}_project"
        
        # Create project
        result = self.create_project(
            project_name=project_name,
            files=code_blocks,
            description=f"Auto-generated {project_name} project"
        )
        
        return result
    
    def list_projects(self) -> List[str]:
        """List all projects in workspace"""
        if not self.workspace.exists():
            return []
        return [d.name for d in self.workspace.iterdir() if d.is_dir()]
    
    def get_project_files(self, project_name: str) -> List[str]:
        """Get all files in a project"""
        project_path = self.workspace / project_name
        if not project_path.exists():
            return []
        
        files = []
        for file_path in project_path.rglob('*'):
            if file_path.is_file():
                files.append(str(file_path.relative_to(project_path)))
        return files


# Singleton instance
_executor_instance = None


def get_executor() -> SmartCodeExecutor:
    """Get global executor instance"""
    global _executor_instance
    if _executor_instance is None:
        _executor_instance = SmartCodeExecutor()
    return _executor_instance


if __name__ == "__main__":
    # Test
    executor = SmartCodeExecutor()
    
    # Test with sample response
    sample_response = """
    Here's a Flask application:
    
    ```python:app.py
    from flask import Flask
    
    app = Flask(__name__)
    
    @app.route('/')
    def hello():
        return 'Hello, World!'
    
    if __name__ == '__main__':
        app.run(debug=True)
    ```
    
    ```python:config.py
    class Config:
        DEBUG = True
        SECRET_KEY = 'dev'
    ```
    """
    
    result = executor.auto_execute_from_response(sample_response, "flask_demo")
    print(json.dumps(result, indent=2))




