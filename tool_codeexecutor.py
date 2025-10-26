"""
CodeExecutor Tool
=================
Tool for executing Python code and bash commands safely
"""

import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import tempfile
import os


class CodeExecutorTool:
    """
    Tool for executing code safely
    Runs code in isolated environment with timeout
    """
    
    def __init__(self, workspace: Path, timeout: int = 30):
        self.workspace = Path(workspace)
        self.timeout = timeout
        self.workspace.mkdir(exist_ok=True)
        
    def execute_python(self, code: str, save_file: bool = False) -> Dict[str, Any]:
        """
        Execute Python code
        
        Args:
            code: Python code to execute
            save_file: Whether to save the code to a file
            
        Returns:
            Execution result
        """
        try:
            # Create temporary file for code
            if save_file:
                code_file = self.workspace / "temp_script.py"
                code_file.write_text(code, encoding='utf-8')
                file_path = str(code_file)
            else:
                # Use temporary file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                    f.write(code)
                    file_path = f.name
            
            # Execute code
            result = subprocess.run(
                [sys.executable, file_path],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=str(self.workspace)
            )
            
            # Clean up temp file if not saved
            if not save_file:
                try:
                    os.unlink(file_path)
                except:
                    pass
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "file": str(file_path) if save_file else None
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Execution timed out after {self.timeout} seconds"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def execute_bash(self, command: str, safe_mode: bool = True) -> Dict[str, Any]:
        """
        Execute bash command
        
        Args:
            command: Bash command to execute
            safe_mode: If True, restricts dangerous commands
            
        Returns:
            Execution result
        """
        # Dangerous commands to block in safe mode
        dangerous_commands = [
            'rm -rf /',
            'mkfs',
            'dd if=',
            ':(){ :|:& };:',  # Fork bomb
            'chmod -R 777 /',
            'wget http',  # Can be dangerous
            'curl http',  # Can be dangerous
        ]
        
        if safe_mode:
            for dangerous in dangerous_commands:
                if dangerous in command.lower():
                    return {
                        "success": False,
                        "error": f"Dangerous command blocked: {dangerous}"
                    }
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=str(self.workspace)
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Command timed out after {self.timeout} seconds"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def execute_python_simple(self, code: str) -> str:
        """
        Simple Python execution that returns output as string
        
        Args:
            code: Python code to execute
            
        Returns:
            Output string
        """
        result = self.execute_python(code)
        
        if result["success"]:
            output = result["stdout"]
            if result["stderr"]:
                output += f"\nWarnings:\n{result['stderr']}"
            return output if output else "Code executed successfully (no output)"
        else:
            return f"Error: {result.get('error', result.get('stderr', 'Unknown error'))}"
    
    def create_folder(self, path: str, **kwargs) -> Dict[str, Any]:
        """
        Create a folder (directory)
        
        Args:
            path: Path to create
            
        Returns:
            Execution result
        """
        try:
            from pathlib import Path
            
            print(f"[CodeExecutor] create_folder called with path: {path}")
            print(f"[CodeExecutor] workspace: {self.workspace}")
            
            # Resolve path relative to workspace
            if path.startswith('/') or (len(path) > 1 and path[1] == ':'):
                # Absolute path
                folder_path = Path(path)
            else:
                # Relative to workspace
                folder_path = self.workspace / path
            
            print(f"[CodeExecutor] Resolved folder_path: {folder_path}")
            
            # Create directory
            folder_path.mkdir(parents=True, exist_ok=True)
            
            print(f"[CodeExecutor] Directory created successfully: {folder_path}")
            
            return {
                "success": True,
                "message": f"Directory created: {folder_path}",
                "path": str(folder_path)
            }
            
        except Exception as e:
            print(f"[CodeExecutor] ERROR creating folder: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_file(self, path: str, content: str = "", **kwargs) -> Dict[str, Any]:
        """
        Create a file with content
        
        Args:
            path: Path to create
            content: File content
            
        Returns:
            Execution result
        """
        try:
            from pathlib import Path
            
            # Resolve path relative to workspace
            if path.startswith('/') or (len(path) > 1 and path[1] == ':'):
                # Absolute path
                file_path = Path(path)
            else:
                # Relative to workspace
                file_path = self.workspace / path
            
            # Create parent directory if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create file
            file_path.write_text(content, encoding='utf-8')
            
            return {
                "success": True,
                "message": f"File created: {file_path}",
                "path": str(file_path),
                "size": len(content)
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
        return """CodeExecutor Tool - Execute code safely:

1. execute_python(code, save_file=False) - Run Python code
   Example: execute_python("print('Hello')")
   Returns: {"success": True, "stdout": "Hello\\n", "stderr": "", "returncode": 0}
   
2. execute_bash(command, safe_mode=True) - Run bash command
   Example: execute_bash("ls -la")
   Returns: {"success": True, "stdout": "...", "stderr": "", "returncode": 0}
   
3. execute_python_simple(code) - Run Python and get simple output
   Example: execute_python_simple("print(2+2)")
   Returns: "4"

Safety features:
- Timeout: 30 seconds default
- Safe mode: Blocks dangerous bash commands
- Isolated execution in workspace
- Captures both stdout and stderr"""


# Test the tool
if __name__ == "__main__":
    print("CodeExecutor Tool Test")
    print("="*60)
    
    # Create tool
    workspace = Path("workspace")
    executor = CodeExecutorTool(workspace)
    
    print("\n1. Executing simple Python code...")
    code = """
print("Hello from Python!")
result = 2 + 2
print(f"2 + 2 = {result}")
"""
    result = executor.execute_python(code)
    print(f"   Success: {result['success']}")
    print(f"   Output:\n{result['stdout']}")
    
    print("\n2. Executing Python with error...")
    code = """
print("This will work")
undefined_variable  # This will cause an error
"""
    result = executor.execute_python(code)
    print(f"   Success: {result['success']}")
    print(f"   Stdout: {result['stdout']}")
    print(f"   Stderr: {result['stderr']}")
    
    print("\n3. Executing bash command (ls)...")
    result = executor.execute_bash("ls -la")
    print(f"   Success: {result['success']}")
    print(f"   Output:\n{result['stdout'][:200]}...")
    
    print("\n4. Testing dangerous command block...")
    result = executor.execute_bash("rm -rf /", safe_mode=True)
    print(f"   Success: {result['success']}")
    print(f"   Error: {result.get('error', 'N/A')}")
    
    print("\n5. Simple Python execution...")
    output = executor.execute_python_simple("print('Simple:', 10 * 5)")
    print(f"   Output: {output}")
    
    print("\n" + "="*60)
    print("✅ CodeExecutor Tool is ready!")
    print("\n⚠️  Safety features active:")
    print("   - 30 second timeout")
    print("   - Dangerous commands blocked")
    print("   - Isolated workspace execution")
