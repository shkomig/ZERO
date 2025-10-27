"""
Computer Control Agent - Main integration class
Combines all computer control capabilities into a unified interface
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from .vision_agent import VisionAgent
from .nlp_parser import NLPCommandParser, Action
from .behavior_learner import BehaviorLearner, UserAction
from .predictive_engine import PredictiveActionEngine
from .proactive_assistant import ProactiveAssistant

logger = logging.getLogger(__name__)


class ComputerControlAgent:
    """
    Main Computer Control Agent
    
    Integrates all computer control capabilities:
    - Computer Vision
    - Natural Language Processing
    - Behavior Learning
    - Predictive Actions
    - Proactive Assistance
    """
    
    def __init__(self, llm=None, orchestrator=None):
        self.llm = llm
        self.orchestrator = orchestrator
        
        # Initialize components
        self.vision_agent = VisionAgent(llm)
        self.nlp_parser = NLPCommandParser(llm)
        self.behavior_learner = BehaviorLearner()
        self.predictive_engine = PredictiveActionEngine(self.behavior_learner, llm)
        self.proactive_assistant = ProactiveAssistant(orchestrator, llm)
        
        # Agent state
        self.is_active = True
        self.current_context = {}
        self.last_screenshot_path = None
        
        logger.info("Computer Control Agent initialized")
    
    def process_command(self, command: str, context: Dict = None) -> Dict[str, Any]:
        """
        Process natural language command
        
        Args:
            command: Natural language command
            context: Optional context information
            
        Returns:
            Execution result
        """
        try:
            # Take screenshot for context
            screenshot_path = self._take_screenshot()
            self.last_screenshot_path = screenshot_path
            
            # Analyze screen
            screen_analysis = self.vision_agent.analyze_screen(screenshot_path)
            
            # Combine contexts
            full_context = {
                **(context or {}),
                "screen_analysis": screen_analysis,
                "screenshot_path": screenshot_path
            }
            
            # Parse command
            action = self.nlp_parser.parse_command(command, full_context)
            
            # Execute action
            result = self._execute_action(action, full_context)
            
            # Learn from execution
            self._learn_from_execution(action, result, full_context)
            
            return {
                "success": result.get("success", False),
                "action": action.type,
                "target": action.target,
                "result": result.get("result", ""),
                "error": result.get("error"),
                "confidence": action.confidence,
                "reasoning": action.reasoning
            }
            
        except Exception as e:
            logger.error(f"Command processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "action": "error"
            }
    
    def get_proactive_suggestions(self, context: Dict = None) -> List[Dict[str, Any]]:
        """
        Get proactive action suggestions
        
        Args:
            context: Optional context information
            
        Returns:
            List of proactive suggestions
        """
        try:
            # Update context
            if context:
                self.current_context.update(context)
            
            # Get suggestions from proactive assistant
            suggestions = self.proactive_assistant.process_context_update(
                self.current_context
            )
            
            # Convert to simple format
            result = []
            for suggestion in suggestions:
                result.append({
                    "action_type": suggestion.action.type,
                    "target": suggestion.action.target,
                    "parameters": suggestion.action.parameters,
                    "confidence": suggestion.confidence,
                    "reasoning": suggestion.reasoning,
                    "urgency": suggestion.urgency,
                    "category": suggestion.category,
                    "estimated_benefit": suggestion.estimated_benefit,
                    "time_to_execute": suggestion.time_to_execute
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Proactive suggestions failed: {e}")
            return []
    
    def execute_suggestion(self, suggestion: Dict[str, Any], 
                                user_confirmation: bool = False) -> Dict[str, Any]:
        """
        Execute a proactive suggestion
        
        Args:
            suggestion: Suggestion to execute
            user_confirmation: Whether user confirmed
            
        Returns:
            Execution result
        """
        try:
            # Convert suggestion to ProactiveSuggestion object
            from .proactive_assistant import ProactiveSuggestion
            from .nlp_parser import Action
            
            action = Action(
                type=suggestion["action_type"],
                target=suggestion["target"],
                parameters=suggestion["parameters"]
            )
            
            proactive_suggestion = ProactiveSuggestion(
                action=action,
                confidence=suggestion["confidence"],
                reasoning=suggestion["reasoning"],
                urgency=suggestion["urgency"],
                category=suggestion["category"],
                estimated_benefit=suggestion["estimated_benefit"],
                time_to_execute=suggestion["time_to_execute"]
            )
            
            # Execute via proactive assistant
            result = self.proactive_assistant.execute_suggestion(
                proactive_suggestion, user_confirmation
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Suggestion execution failed: {e}")
            return {"success": False, "error": str(e)}
    
    def analyze_screen(self, screenshot_path: str = None) -> Dict[str, Any]:
        """
        Analyze current screen
        
        Args:
            screenshot_path: Optional path to screenshot
            
        Returns:
            Screen analysis results
        """
        try:
            if not screenshot_path:
                screenshot_path = self._take_screenshot()
            
            analysis = self.vision_agent.analyze_screen(screenshot_path)
            return analysis
            
        except Exception as e:
            logger.error(f"Screen analysis failed: {e}")
            return {"success": False, "error": str(e)}
    
    def find_element(self, description: str, screenshot_path: str = None) -> Dict[str, Any]:
        """
        Find UI element by description
        
        Args:
            description: Element description
            screenshot_path: Optional path to screenshot
            
        Returns:
            Element information
        """
        try:
            if not screenshot_path:
                screenshot_path = self._take_screenshot()
            
            result = self.vision_agent.find_element(description, screenshot_path)
            return result
            
        except Exception as e:
            logger.error(f"Element finding failed: {e}")
            return {"success": False, "error": str(e)}
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get learning statistics"""
        try:
            behavior_stats = self.behavior_learner.get_learning_stats()
            assistant_summary = self.proactive_assistant.get_suggestions_summary()
            
            return {
                "behavior_learning": behavior_stats,
                "proactive_assistant": assistant_summary,
                "agent_status": {
                    "is_active": self.is_active,
                    "last_activity": datetime.now().isoformat(),
                    "current_context": self.current_context
                }
            }
            
        except Exception as e:
            logger.error(f"Stats generation failed: {e}")
            return {"error": str(e)}
    
    def _take_screenshot(self) -> str:
        """Take screenshot and return path"""
        try:
            from .screen_capture import ScreenCapture
            
            # Create screenshots directory
            screenshots_dir = Path("workspace/screenshots")
            screenshots_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = screenshots_dir / f"screenshot_{timestamp}.png"
            
            # Take screenshot
            screen_capture = ScreenCapture()
            img_array = screen_capture.capture_screen(save_path=screenshot_path)
            
            if img_array is not None:
                return str(screenshot_path)
            else:
                raise Exception("Failed to capture screenshot")
                
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            # Return a default path for testing
            return "workspace/screenshots/default.png"
    
    def _execute_action(self, action: Action, context: Dict) -> Dict[str, Any]:
        """Execute parsed action - ALWAYS execute directly for computer control"""
        try:
            # Direct execution - this actually performs the action
            return self._execute_directly(action, context)
                
        except Exception as e:
            logger.error(f"Action execution failed: {e}")
            # Fallback to orchestrator only if direct execution fails
            if self.orchestrator:
                try:
                    command = self._action_to_command(action)
                    result = self.orchestrator.execute_goal(command)
                    return {
                        "success": result.success,
                        "result": result.output,
                        "error": result.error
                    }
                except Exception as orch_error:
                    logger.error(f"Orchestrator fallback failed: {orch_error}")
            return {"success": False, "error": str(e)}
    
    def _execute_directly(self, action: Action, context: Dict) -> Dict[str, Any]:
        """Execute action directly"""
        try:
            if action.type == "open":
                # Open application
                import subprocess
                import platform
                
                app_name = action.target.lower() if action.target else ""
                
                # Map common names to executables (Windows)
                app_map = {
                    # Hebrew
                    "דפדפן": "start msedge",
                    "דפדפן גוגל": "start chrome",
                    "פנקס רשימות": "notepad",
                    "מחשבון": "calc",
                    "סייר": "explorer",
                    "לוח בקרה": "control",
                    # English
                    "notepad": "notepad",
                    "calculator": "calc",
                    "calc": "calc",
                    "chrome": "start chrome",
                    "google chrome": "start chrome",
                    "edge": "start msedge",
                    "microsoft edge": "start msedge",
                    "explorer": "explorer",
                    "file explorer": "explorer",
                    "cmd": "cmd",
                    "command prompt": "cmd",
                    "powershell": "powershell",
                    "control panel": "control",
                    "settings": "start ms-settings:",
                    "paint": "mspaint",
                    "wordpad": "write"
                }
                
                # Get executable name
                exe = app_map.get(app_name, app_name)
                
                try:
                    if platform.system() == "Windows":
                        result = subprocess.run(exe, shell=True, capture_output=True, timeout=3)
                        # Check if command was recognized
                        if result.returncode == 0 or "is not recognized" not in str(result.stderr):
                            return {"success": True, "result": f"Opened {action.target}"}
                        else:
                            return {"success": False, "error": f"Application '{action.target}' not found"}
                    else:
                        subprocess.Popen(exe)
                        return {"success": True, "result": f"Opened {action.target}"}
                except subprocess.TimeoutExpired:
                    # Timeout means the app is probably running (good!)
                    return {"success": True, "result": f"Opened {action.target}"}
                except Exception as e:
                    logger.error(f"Failed to open {action.target}: {e}")
                    return {"success": False, "error": f"Could not open {action.target}: {str(e)}"}
            
            elif action.type == "screenshot":
                # Real screenshot with analysis
                try:
                    from .screen_capture import ScreenCapture
                    from pathlib import Path
                    from datetime import datetime
                    
                    # Create screenshots directory
                    screenshots_dir = Path("ZERO/screenshots")
                    screenshots_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Generate filename
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    screenshot_path = screenshots_dir / f"screenshot_{timestamp}.png"
                    
                    # Capture screen
                    capturer = ScreenCapture()
                    img_array = capturer.capture_screen(save_path=screenshot_path)
                    
                    if img_array is None:
                        return {"success": False, "error": "Screenshot failed"}
                    
                    # Optional: Analyze with Vision Agent if available
                    analysis = {}
                    if self.vision_agent:
                        analysis = self.vision_agent.analyze_screen(str(screenshot_path))
                    
                    result_text = f"Screenshot saved to {screenshot_path}"
                    if analysis.get("success"):
                        # Add summary
                        summary = self.vision_agent.get_screen_summary(str(screenshot_path))
                        result_text += f"\n\nScreen Analysis:\n{summary}"
                    
                    return {
                        "success": True, 
                        "result": result_text,
                        "screenshot_path": str(screenshot_path),
                        "analysis": analysis
                    }
                except ImportError as e:
                    return {"success": False, "error": f"Screenshot dependencies missing: {e}"}
                except Exception as e:
                    return {"success": False, "error": f"Screenshot failed: {str(e)}"}
            
            elif action.type == "click":
                # Real mouse click using pyautogui
                try:
                    import pyautogui
                    params = action.parameters or {}
                    
                    # Check if coordinates provided
                    if "x" in params and "y" in params:
                        x, y = params["x"], params["y"]
                        pyautogui.click(x, y)
                        return {"success": True, "result": f"Clicked at ({x}, {y})"}
                    else:
                        return {"success": False, "error": "Coordinates required for click"}
                except ImportError:
                    return {"success": False, "error": "pyautogui not installed"}
                except Exception as e:
                    return {"success": False, "error": f"Click failed: {str(e)}"}
            
            elif action.type == "type":
                # Real keyboard typing using pyautogui
                try:
                    import pyautogui
                    import time
                    text = action.parameters.get("text", "")
                    if text:
                        time.sleep(0.5)  # Small delay before typing
                        # Use write() instead of typewrite() for Unicode support (Hebrew, etc.)
                        pyautogui.write(text, interval=0.05)
                        return {"success": True, "result": f"Typed: {text}"}
                    else:
                        return {"success": False, "error": "No text provided"}
                except ImportError:
                    return {"success": False, "error": "pyautogui not installed"}
                except Exception as e:
                    return {"success": False, "error": f"Type failed: {str(e)}"}
            
            elif action.type == "scroll":
                # Real mouse scroll using pyautogui
                try:
                    import pyautogui
                    x = action.parameters.get("x", 0)
                    y = action.parameters.get("y", 100)
                    
                    # pyautogui.scroll() takes positive for up, negative for down
                    # We convert y to scroll amount (divide by 10 for smoothness)
                    scroll_amount = int(y / 10)
                    pyautogui.scroll(scroll_amount)
                    
                    direction = "down" if y > 0 else "up" if y < 0 else "right" if x > 0 else "left"
                    return {"success": True, "result": f"Scrolled {direction}"}
                except ImportError:
                    return {"success": False, "error": "pyautogui not installed"}
                except Exception as e:
                    return {"success": False, "error": f"Scroll failed: {str(e)}"}
            
            elif action.type == "hotkey":
                # Real keyboard shortcuts using pyautogui
                try:
                    import pyautogui
                    keys = action.parameters.get("keys", "")
                    if keys:
                        # Split by + and press the combination
                        key_parts = [k.strip() for k in keys.split("+")]
                        pyautogui.hotkey(*key_parts)
                        return {"success": True, "result": f"Pressed {keys}"}
                    else:
                        return {"success": False, "error": "No keys provided"}
                except ImportError:
                    return {"success": False, "error": "pyautogui not installed"}
                except Exception as e:
                    return {"success": False, "error": f"Hotkey failed: {str(e)}"}
            
            elif action.type == "generate_image":
                # Generate image using FLUX
                try:
                    from .tool_image_generation import image_tool
                    prompt = action.parameters.get("prompt", "")
                    if prompt:
                        result = image_tool.generate_simple(prompt)
                        if result.get("success"):
                            return {"success": True, "result": f"Image generation started: {result.get('message', '')}", "data": result}
                        else:
                            return {"success": False, "error": result.get("error", "Unknown error")}
                    else:
                        return {"success": False, "error": "No prompt provided"}
                except Exception as e:
                    return {"success": False, "error": f"Image generation failed: {str(e)}"}
            
            elif action.type == "generate_video":
                # Generate video using CogVideoX or HunyuanVideo
                try:
                    from .tool_video_generation import video_tool
                    prompt = action.parameters.get("prompt", "")
                    if prompt:
                        result = video_tool.generate_simple(prompt, service="cogvideo")
                        if result.get("success"):
                            return {"success": True, "result": f"Video generation started: {result.get('message', '')}", "data": result}
                        else:
                            return {"success": False, "error": result.get("error", "Unknown error")}
                    else:
                        return {"success": False, "error": "No prompt provided"}
                except Exception as e:
                    return {"success": False, "error": f"Video generation failed: {str(e)}"}
            
            elif action.type == "speak":
                # Text-to-Speech using Hebrew TTS
                try:
                    from .tool_tts_hebrew import tts_tool
                    import subprocess
                    import platform
                    
                    text = action.parameters.get("text", "")
                    if text:
                        result = tts_tool.speak_simple(text)
                        if result.get("success"):
                            # Auto-play the audio file
                            filepath = result.get("filepath")
                            if filepath:
                                try:
                                    if platform.system() == "Windows":
                                        subprocess.Popen(['powershell', 'Invoke-Item', filepath])
                                    elif platform.system() == "Darwin":  # macOS
                                        subprocess.Popen(['open', filepath])
                                    else:  # Linux
                                        subprocess.Popen(['xdg-open', filepath])
                                    logger.info(f"🔊 Playing audio: {filepath}")
                                except Exception as play_error:
                                    logger.warning(f"Could not auto-play audio: {play_error}")
                            
                            return {"success": True, "result": f"🔊 מדבר: {text[:50]}...", "data": result}
                        else:
                            return {"success": False, "error": result.get("error", "Unknown error")}
                    else:
                        return {"success": False, "error": "No text provided"}
                except Exception as e:
                    return {"success": False, "error": f"TTS failed: {str(e)}"}
            
            else:
                return {"success": False, "error": f"Unknown action: {action.type}"}
                
        except Exception as e:
            logger.error(f"Direct execution failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _action_to_command(self, action: Action) -> str:
        """Convert action to natural language command"""
        try:
            if action.type == "open":
                return f"Open {action.target}"
            elif action.type == "click":
                return f"Click on {action.target}"
            elif action.type == "type":
                text = action.parameters.get("text", "")
                return f"Type '{text}'"
            elif action.type == "scroll":
                x = action.parameters.get("x", 0)
                y = action.parameters.get("y", 100)
                return f"Scroll {x}, {y}"
            elif action.type == "screenshot":
                return "Take screenshot"
            else:
                return f"Execute {action.type} on {action.target}"
                
        except Exception as e:
            logger.warning(f"Command conversion failed: {e}")
            return f"Execute {action.type}"
    
    def _learn_from_execution(self, action: Action, result: Dict, context: Dict):
        """Learn from action execution"""
        try:
            # Create user action for learning
            user_action = UserAction(
                timestamp=datetime.now(),
                action_type=action.type,
                target=action.target,
                parameters=action.parameters,
                success=result.get("success", False),
                context=context
            )
            
            # Learn from action
            self.behavior_learner.learn_from_action(user_action)
            
        except Exception as e:
            logger.warning(f"Learning from execution failed: {e}")


# Example usage and testing
if __name__ == "__main__":
    async def test_computer_control_agent():
        agent = ComputerControlAgent()
        
        # Test command processing
        result = agent.process_command("לחץ על הכפתור הכחול")
        print(f"Command result: {result}")
        
        # Test proactive suggestions
        suggestions = agent.get_proactive_suggestions()
        print(f"Proactive suggestions: {len(suggestions)}")
        
        # Test screen analysis
        analysis = agent.analyze_screen()
        print(f"Screen analysis: {analysis.get('success', False)}")
        
        # Get learning stats
        stats = agent.get_learning_stats()
        print(f"Learning stats: {stats}")
    
    # Run test
    asyncio.run(test_computer_control_agent())
