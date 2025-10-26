"""
Safety Layer - שכבת אבטחה לפעולות
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class Action:
    """פעולה לביצוע"""
    type: str
    parameters: Dict[str, Any]
    source: str = "user"  # user, agent, system


class SafetyLayer:
    """
    שכבת אבטחה לפעולות
    
    תפקידים:
    1. וולידציה של פעולות
    2. חתימת whitelist/blacklist
    3. בדיקת פרמטרים מסוכנים
    4. אישור לפעולות בעייתיות
    """
    
    # פעולות בטוחות - לא דורשות אישור
    SAFE_ACTIONS = [
        'read_file',
        'list_files',
        'web_search',
        'search',
        'query_database'
    ]
    
    # פעולות מסוכנות - דורשות אישור
    DANGEROUS_ACTIONS = [
        'delete_file',
        'delete_folder',
        'execute_code',
        'run_command',
        'install_package',
        'modify_system',
        'send_email',
        'access_network'
    ]
    
    # נתיבים אסורים - לא נוגעים בהם
    RESTRICTED_PATHS = [
        '/', 'C:\\Windows', 'C:\\Program Files',
        '/System', '/Library', '/etc', '/usr'
    ]
    
    def __init__(self):
        """Initialize safety layer"""
        self.allowed_paths: List[str] = []
        self.blocked_paths: List[str] = []
        self.confirmation_required: bool = True
        
    def validate(self, action: Action) -> tuple[bool, str]:
        """
        וולידציה של פעולה
        
        Args:
            action: הפעולה
            
        Returns:
            (is_valid, message)
        """
        logger.info(f"🔒 Validating action: {action.type}")
        
        # בדוק type
        if not self._is_valid_action_type(action.type):
            return False, f"Unknown action type: {action.type}"
        
        # בדוק parameters
        params_check = self._validate_parameters(action)
        if not params_check[0]:
            return params_check
        
        # בדוק paths
        paths_check = self._validate_paths(action)
        if not paths_check[0]:
            return paths_check
        
        # בדוק אם פעולה מסוכנת
        if action.type in self.DANGEROUS_ACTIONS:
            if self.confirmation_required:
                return False, f"Dangerous action requires confirmation: {action.type}"
        
        return True, "Action validated"
    
    def _is_valid_action_type(self, action_type: str) -> bool:
        """בדוק אם סוג הפעולה תקף"""
        all_actions = self.SAFE_ACTIONS + self.DANGEROUS_ACTIONS
        return action_type in all_actions or action_type.startswith('custom_')
    
    def _validate_parameters(self, action: Action) -> tuple[bool, str]:
        """וולידציה של פרמטרים"""
        params = action.parameters
        
        # בדוק path parameters
        if 'path' in params:
            path_str = params['path']
            if not isinstance(path_str, str):
                return False, "Path must be a string"
            
            # בדוק restricted paths
            path_obj = Path(path_str)
            for restricted in self.RESTRICTED_PATHS:
                if str(path_obj).startswith(restricted):
                    return False, f"Access denied to restricted path: {restricted}"
            
            # בדוק blocked paths
            for blocked in self.blocked_paths:
                if blocked in str(path_obj):
                    return False, f"Path is blocked: {blocked}"
        
        # בדוק command execution
        if 'command' in params:
            cmd = params['command']
            dangerous_keywords = ['rm -rf', 'del /f', 'format', 'fdisk']
            if any(keyword in cmd.lower() for keyword in dangerous_keywords):
                return False, f"Dangerous command detected: {cmd}"
        
        return True, "Parameters validated"
    
    def _validate_paths(self, action: Action) -> tuple[bool, str]:
        """וולידציה של נתיבים"""
        params = action.parameters
        
        # בדוק path arguments
        path_params = ['path', 'directory', 'file', 'source', 'target']
        
        for param_name in path_params:
            if param_name in params:
                path_value = params[param_name]
                
                if isinstance(path_value, str):
                    if self._is_restricted_path(path_value):
                        return False, f"Restricted path: {path_value}"
        
        return True, "Paths validated"
    
    def _is_restricted_path(self, path_str: str) -> bool:
        """בדוק אם נתיב מוגבל"""
        path_obj = Path(path_str)
        path_normalized = str(path_obj).lower()
        
        for restricted in self.RESTRICTED_PATHS:
            if path_normalized.startswith(restricted.lower()):
                return True
        
        return False
    
    def require_confirmation(self, action: Action) -> bool:
        """
        בדוק אם פעולה דורשת אישור
        
        Args:
            action: הפעולה
            
        Returns:
            True אם דורש אישור
        """
        return action.type in self.DANGEROUS_ACTIONS
    
    def add_allowed_path(self, path: str):
        """הוסף נתיב מותר"""
        self.allowed_paths.append(path)
        logger.info(f"Added allowed path: {path}")
    
    def add_blocked_path(self, path: str):
        """הוסף נתיב חסום"""
        self.blocked_paths.append(path)
        logger.info(f"Added blocked path: {path}")
    
    def check_resource_usage(self, action: Action) -> tuple[bool, str]:
        """
        בדוק שימוש במשאבים
        
        Args:
            action: הפעולה
            
        Returns:
            (is_safe, message)
        """
        # בדוק גודל קבצים
        if 'size' in action.parameters:
            max_size = 100 * 1024 * 1024  # 100MB
            if action.parameters['size'] > max_size:
                return False, f"File too large: {action.parameters['size']}"
        
        # בדוק זמן ביצוע
        if 'timeout' in action.parameters:
            max_timeout = 300  # 5 minutes
            if action.parameters['timeout'] > max_timeout:
                return False, f"Timeout too long: {action.parameters['timeout']}"
        
        return True, "Resource usage OK"
