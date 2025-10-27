"""
Natural Language Processing Parser for Computer Control Commands
Converts natural language commands to structured actions
"""

import re
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class Action:
    """Structured action for computer control"""
    type: str  # click, type, drag, scroll, wait, screenshot, etc.
    target: Optional[str] = None  # Element description or coordinates
    parameters: Dict[str, Any] = None
    confidence: float = 0.0
    reasoning: str = ""


class NLPCommandParser:
    """
    Natural Language Command Parser
    
    Converts natural language commands to structured actions
    Supports Hebrew and English commands
    """
    
    def __init__(self, llm=None):
        self.llm = llm
        
        # Command patterns for different languages
        self.hebrew_patterns = {
            "open": [
                r"פתח (.+)",
                r"תפתח (.+)",
                r"הפעל (.+)",
                r"תפעיל (.+)",
                r"הרץ (.+)",
                r"תריץ (.+)"
            ],
            "click": [
                r"לחץ על (.+)",
                r"לחץ (.+)",
                r"תלחץ על (.+)",
                r"תלחץ (.+)",
                r"לחץ כאן",
                r"לחץ שם"
            ],
            "type": [
                r"הקלד (.+)",
                r"תקליד (.+)",
                r"כתוב (.+)",
                r"תכתוב (.+)",
                r"הכנס (.+)",
                r"תכניס (.+)"
            ],
            "drag": [
                r"גרור מ(.+) ל(.+)",
                r"תגרור מ(.+) ל(.+)",
                r"גרור (.+) ל(.+)",
                r"תגרור (.+) ל(.+)"
            ],
            "scroll": [
                r"גלול (.+)",
                r"תגלול (.+)",
                r"גלול למטה",
                r"גלול למעלה",
                r"גלול שמאלה",
                r"גלול ימינה"
            ],
            "screenshot": [
                r"צלם מסך",
                r"תצלם מסך",
                r"קח צילום",
                r"תקח צילום"
            ],
            "wait": [
                r"חכה (.+)",
                r"תחכה (.+)",
                r"המתן (.+)",
                r"תהמתן (.+)"
            ],
            "hotkey": [
                r"לחץ (.+\+.+)",
                r"תלחץ (.+\+.+)",
                r"הקש (.+\+.+)",
                r"תקיש (.+\+.+)",
                r"שלב מקשים (.+)"
            ],
            "generate_image": [
                r"צור תמונה של (.+)",
                r"צור תמונה (.+)",
                r"תצור תמונה של (.+)",
                r"צייר (.+)",
                r"תצייר (.+)",
                r"הפק תמונה של (.+)"
            ],
            "generate_video": [
                r"צור סרטון של (.+)",
                r"צור סרטון (.+)",
                r"תצור סרטון של (.+)",
                r"הפק סרטון של (.+)",
                r"צור וידאו של (.+)",
                r"צור וידאו (.+)"
            ],
            "speak": [
                r"הקרא בקול (.+)",
                r"תקרא בקול (.+)",
                r"דבר (.+)",
                r"תדבר (.+)",
                r"הגה (.+)",
                r"תהגה (.+)"
            ]
        }
        
        self.english_patterns = {
            "open": [
                r"open (.+)",
                r"launch (.+)",
                r"start (.+)",
                r"run (.+)"
            ],
            "click": [
                r"click on (.+)",
                r"click (.+)",
                r"press (.+)",
                r"tap (.+)"
            ],
            "type": [
                r"type (.+)",
                r"enter (.+)",
                r"write (.+)",
                r"input (.+)"
            ],
            "drag": [
                r"drag from (.+) to (.+)",
                r"drag (.+) to (.+)",
                r"move (.+) to (.+)"
            ],
            "scroll": [
                r"scroll (.+)",
                r"scroll down",
                r"scroll up",
                r"scroll left",
                r"scroll right"
            ],
            "screenshot": [
                r"take screenshot",
                r"screenshot",
                r"capture screen",
                r"snap screen"
            ],
            "wait": [
                r"wait (.+)",
                r"pause (.+)",
                r"delay (.+)"
            ],
            "hotkey": [
                r"press (.+\+.+)",
                r"hit (.+\+.+)",
                r"keyboard (.+)",
                r"shortcut (.+)"
            ],
            "generate_image": [
                r"generate image of (.+)",
                r"generate image (.+)",
                r"create image of (.+)",
                r"create image (.+)",
                r"draw (.+)",
                r"make image of (.+)"
            ],
            "generate_video": [
                r"generate video of (.+)",
                r"generate video (.+)",
                r"create video of (.+)",
                r"create video (.+)",
                r"make video of (.+)",
                r"render video (.+)"
            ],
            "speak": [
                r"speak (.+)",
                r"say (.+)",
                r"read out (.+)",
                r"read aloud (.+)",
                r"voice (.+)"
            ]
        }
        
        # Coordinate patterns
        self.coordinate_patterns = [
            r"\((\d+),\s*(\d+)\)",  # (x, y)
            r"(\d+),\s*(\d+)",      # x, y
            r"מיקום (\d+),\s*(\d+)",  # Hebrew: מיקום x, y
            r"position (\d+),\s*(\d+)"  # English: position x, y
        ]
        
        # Time patterns
        self.time_patterns = [
            r"(\d+)\s*שניות",  # Hebrew: X seconds
            r"(\d+)\s*seconds",  # English: X seconds
            r"(\d+)\s*דקות",    # Hebrew: X minutes
            r"(\d+)\s*minutes",  # English: X minutes
            r"(\d+)\s*שעה",     # Hebrew: X hours
            r"(\d+)\s*hours"    # English: X hours
        ]
        
        logger.info("NLP Command Parser initialized")
    
    def parse_command(self, command: str, screen_context: Dict = None) -> Action:
        """
        Parse natural language command to structured action
        
        Args:
            command: Natural language command
            screen_context: Current screen analysis context
            
        Returns:
            Structured Action object
        """
        try:
            command = command.strip()
            if not command:
                return Action("unknown", confidence=0.0, reasoning="Empty command")
            
            # Detect language
            is_hebrew = self._detect_hebrew(command)
            patterns = self.hebrew_patterns if is_hebrew else self.english_patterns
            
            # Try pattern matching first
            action = self._pattern_match(command, patterns, is_hebrew)
            if action and action.confidence > 0.7:
                return action
            
            # Fallback to LLM if available
            if self.llm:
                action = self._llm_parse(command, screen_context, is_hebrew)
                if action:
                    return action
            
            # Final fallback - basic parsing
            return self._basic_parse(command, is_hebrew)
            
        except Exception as e:
            logger.error(f"Command parsing failed: {e}")
            return Action("error", confidence=0.0, reasoning=f"Parsing error: {e}")
    
    def _detect_hebrew(self, text: str) -> bool:
        """Detect if text contains Hebrew characters"""
        hebrew_chars = sum(1 for char in text if '\u0590' <= char <= '\u05FF')
        total_chars = len([char for char in text if char.isalpha()])
        
        if total_chars == 0:
            return False
        
        return hebrew_chars / total_chars > 0.3
    
    def _pattern_match(self, command: str, patterns: Dict, is_hebrew: bool) -> Optional[Action]:
        """Match command against predefined patterns"""
        try:
            command_lower = command.lower()
            
            for action_type, pattern_list in patterns.items():
                for pattern in pattern_list:
                    match = re.search(pattern, command_lower)
                    if match:
                        groups = match.groups()
                        
                        if action_type == "open":
                            return self._parse_open_action(command, groups, is_hebrew)
                        elif action_type == "click":
                            return self._parse_click_action(command, groups, is_hebrew)
                        elif action_type == "type":
                            return self._parse_type_action(command, groups, is_hebrew)
                        elif action_type == "drag":
                            return self._parse_drag_action(command, groups, is_hebrew)
                        elif action_type == "scroll":
                            return self._parse_scroll_action(command, groups, is_hebrew)
                        elif action_type == "screenshot":
                            return self._parse_screenshot_action(command, is_hebrew)
                        elif action_type == "wait":
                            return self._parse_wait_action(command, groups, is_hebrew)
                        elif action_type == "hotkey":
                            return self._parse_hotkey_action(command, groups, is_hebrew)
                        elif action_type == "generate_image":
                            return self._parse_generate_image_action(command, groups, is_hebrew)
                        elif action_type == "generate_video":
                            return self._parse_generate_video_action(command, groups, is_hebrew)
                        elif action_type == "speak":
                            return self._parse_speak_action(command, groups, is_hebrew)
            
            return None
            
        except Exception as e:
            logger.warning(f"Pattern matching failed: {e}")
            return None
    
    def _parse_open_action(self, command: str, groups: Tuple, is_hebrew: bool) -> Action:
        """Parse open/launch application action"""
        app_name = groups[0] if groups else "unknown"
        app_name = app_name.strip()
        
        return Action(
            type="open",
            target=app_name,
            parameters={"app": app_name},
            confidence=0.95,
            reasoning=f"Open application: {app_name}"
        )
    
    def _parse_click_action(self, command: str, groups: Tuple, is_hebrew: bool) -> Action:
        """Parse click action"""
        target = groups[0] if groups else "unknown"
        
        # Check for coordinates
        coords = self._extract_coordinates(target)
        if coords:
            return Action(
                type="click",
                target=f"coordinates_{coords[0]}_{coords[1]}",
                parameters={"x": coords[0], "y": coords[1]},
                confidence=0.9,
                reasoning="Click at coordinates"
            )
        
        # Check for element description
        return Action(
            type="click",
            target=target,
            parameters={"description": target},
            confidence=0.8,
            reasoning="Click on element"
        )
    
    def _parse_type_action(self, command: str, groups: Tuple, is_hebrew: bool) -> Action:
        """Parse type action"""
        text = groups[0] if groups else ""
        
        # Clean up text
        text = text.strip('"\'')
        
        return Action(
            type="type",
            target="text_input",
            parameters={"text": text},
            confidence=0.9,
            reasoning="Type text"
        )
    
    def _parse_drag_action(self, command: str, groups: Tuple, is_hebrew: bool) -> Action:
        """Parse drag action"""
        if len(groups) >= 2:
            start_target = groups[0]
            end_target = groups[1]
            
            # Check for coordinates
            start_coords = self._extract_coordinates(start_target)
            end_coords = self._extract_coordinates(end_target)
            
            if start_coords and end_coords:
                return Action(
                    type="drag",
                    target="coordinates",
                    parameters={
                        "start_x": start_coords[0],
                        "start_y": start_coords[1],
                        "end_x": end_coords[0],
                        "end_y": end_coords[1]
                    },
                    confidence=0.9,
                    reasoning="Drag between coordinates"
                )
            else:
                return Action(
                    type="drag",
                    target="elements",
                    parameters={
                        "start_description": start_target,
                        "end_description": end_target
                    },
                    confidence=0.7,
                    reasoning="Drag between elements"
                )
        
        return Action(
            type="drag",
            target="unknown",
            parameters={},
            confidence=0.3,
            reasoning="Incomplete drag command"
        )
    
    def _parse_scroll_action(self, command: str, groups: Tuple, is_hebrew: bool) -> Action:
        """Parse scroll action"""
        direction = groups[0] if groups else "down"
        
        # Map directions
        direction_map = {
            "down": {"x": 0, "y": 100},
            "up": {"x": 0, "y": -100},
            "left": {"x": -100, "y": 0},
            "right": {"x": 100, "y": 0},
            "למטה": {"x": 0, "y": 100},
            "למעלה": {"x": 0, "y": -100},
            "שמאלה": {"x": -100, "y": 0},
            "ימינה": {"x": 100, "y": 0}
        }
        
        scroll_params = direction_map.get(direction.lower(), {"x": 0, "y": 100})
        
        return Action(
            type="scroll",
            target="screen",
            parameters=scroll_params,
            confidence=0.8,
            reasoning=f"Scroll {direction}"
        )
    
    def _parse_screenshot_action(self, command: str, is_hebrew: bool) -> Action:
        """Parse screenshot action"""
        return Action(
            type="screenshot",
            target="screen",
            parameters={},
            confidence=0.9,
            reasoning="Take screenshot"
        )
    
    def _parse_wait_action(self, command: str, groups: Tuple, is_hebrew: bool) -> Action:
        """Parse wait action"""
        time_text = groups[0] if groups else "1"
        
        # Extract time value
        time_seconds = self._extract_time(time_text)
        
        return Action(
            type="wait",
            target="time",
            parameters={"seconds": time_seconds},
            confidence=0.8,
            reasoning=f"Wait {time_seconds} seconds"
        )
    
    def _parse_hotkey_action(self, command: str, groups: Tuple, is_hebrew: bool) -> Action:
        """Parse keyboard shortcut action"""
        keys = groups[0] if groups else "ctrl+c"
        
        # Clean up keys
        keys = keys.strip().lower()
        
        # Map Hebrew keys to English
        key_map = {
            "קונטרול": "ctrl",
            "קונטרל": "ctrl",
            "קטרל": "ctrl",
            "אלט": "alt",
            "שיפט": "shift",
            "וין": "win",
            "ווינדוס": "win"
        }
        
        for heb_key, eng_key in key_map.items():
            keys = keys.replace(heb_key, eng_key)
        
        return Action(
            type="hotkey",
            target="keyboard",
            parameters={"keys": keys},
            confidence=0.9,
            reasoning=f"Press keyboard shortcut: {keys}"
        )
    
    def _parse_generate_image_action(self, command: str, groups: Tuple, is_hebrew: bool) -> Action:
        """Parse image generation action"""
        prompt = groups[0] if groups else command
        prompt = prompt.strip()
        
        return Action(
            type="generate_image",
            target="image",
            parameters={"prompt": prompt},
            confidence=0.95,
            reasoning=f"Generate image: {prompt[:50]}"
        )
    
    def _parse_generate_video_action(self, command: str, groups: Tuple, is_hebrew: bool) -> Action:
        """Parse video generation action"""
        prompt = groups[0] if groups else command
        prompt = prompt.strip()
        
        return Action(
            type="generate_video",
            target="video",
            parameters={"prompt": prompt},
            confidence=0.95,
            reasoning=f"Generate video: {prompt[:50]}"
        )
    
    def _parse_speak_action(self, command: str, groups: Tuple, is_hebrew: bool) -> Action:
        """Parse text-to-speech action"""
        text = groups[0] if groups else command
        text = text.strip()
        
        return Action(
            type="speak",
            target="audio",
            parameters={"text": text},
            confidence=0.95,
            reasoning=f"Speak: {text[:50]}"
        )
    
    def _extract_coordinates(self, text: str) -> Optional[Tuple[int, int]]:
        """Extract coordinates from text"""
        for pattern in self.coordinate_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    x = int(match.group(1))
                    y = int(match.group(2))
                    return (x, y)
                except (ValueError, IndexError):
                    continue
        return None
    
    def _extract_time(self, text: str) -> float:
        """Extract time value in seconds"""
        for pattern in self.time_patterns:
            match = re.search(pattern, text.lower())
            if match:
                try:
                    value = float(match.group(1))
                    
                    if "minute" in pattern or "דקה" in pattern:
                        return value * 60
                    elif "hour" in pattern or "שעה" in pattern:
                        return value * 3600
                    else:  # seconds
                        return value
                except ValueError:
                    continue
        
        # Default to 1 second
        return 1.0
    
    def _llm_parse(self, command: str, screen_context: Dict, is_hebrew: bool) -> Optional[Action]:
        """Use LLM to parse complex commands"""
        try:
            language = "Hebrew" if is_hebrew else "English"
            
            prompt = f"""
            Parse this {language} command: "{command}"
            
            Screen context:
            {json.dumps(screen_context, indent=2) if screen_context else "No context available"}
            
            Return a JSON object with this structure:
            {{
                "type": "click|type|drag|scroll|screenshot|wait",
                "target": "element description or coordinates",
                "parameters": {{}},
                "confidence": 0.0-1.0,
                "reasoning": "explanation"
            }}
            
            For coordinates, use format: "x,y"
            For element descriptions, be specific about what to click/type on.
            """
            
            result = self.llm.generate(prompt)
            
            # Parse JSON response
            try:
                action_data = json.loads(result)
                
                # Validate required fields
                if "type" in action_data and "confidence" in action_data:
                    return Action(
                        type=action_data["type"],
                        target=action_data.get("target"),
                        parameters=action_data.get("parameters", {}),
                        confidence=float(action_data["confidence"]),
                        reasoning=action_data.get("reasoning", "LLM parsing")
                    )
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                logger.warning(f"Failed to parse LLM response: {e}")
            
            return None
            
        except Exception as e:
            logger.warning(f"LLM parsing failed: {e}")
            return None
    
    def _basic_parse(self, command: str, is_hebrew: bool) -> Action:
        """Basic parsing fallback"""
        command_lower = command.lower()
        
        # Simple keyword detection
        if any(word in command_lower for word in ["click", "לחץ", "press"]):
            return Action("click", confidence=0.5, reasoning="Basic keyword detection")
        elif any(word in command_lower for word in ["type", "הקלד", "write", "כתוב"]):
            return Action("type", confidence=0.5, reasoning="Basic keyword detection")
        elif any(word in command_lower for word in ["scroll", "גלול"]):
            return Action("scroll", confidence=0.5, reasoning="Basic keyword detection")
        elif any(word in command_lower for word in ["screenshot", "צילום", "capture"]):
            return Action("screenshot", confidence=0.5, reasoning="Basic keyword detection")
        else:
            return Action("unknown", confidence=0.1, reasoning="No recognizable keywords")
    
    def get_supported_commands(self, language: str = "both") -> Dict[str, List[str]]:
        """Get list of supported commands"""
        if language == "hebrew":
            return self.hebrew_patterns
        elif language == "english":
            return self.english_patterns
        else:  # both
            return {
                "hebrew": self.hebrew_patterns,
                "english": self.english_patterns
            }
    
    def validate_action(self, action: Action) -> Tuple[bool, str]:
        """Validate parsed action"""
        if not action.type:
            return False, "Missing action type"
        
        if action.confidence < 0.1:
            return False, "Very low confidence"
        
        # Type-specific validation
        if action.type == "click":
            if not action.target and not action.parameters.get("x"):
                return False, "Click action missing target or coordinates"
        
        elif action.type == "type":
            if not action.parameters.get("text"):
                return False, "Type action missing text"
        
        elif action.type == "drag":
            required_params = ["start_x", "start_y", "end_x", "end_y"]
            if not all(param in action.parameters for param in required_params):
                return False, "Drag action missing coordinates"
        
        return True, "Action is valid"


# Example usage and testing
if __name__ == "__main__":
    parser = NLPCommandParser()
    
    # Test commands
    test_commands = [
        "לחץ על הכפתור הכחול",
        "click on the red button",
        "הקלד 'שלום עולם'",
        "type 'hello world'",
        "גרור מ(100,100) ל(200,200)",
        "scroll down",
        "צלם מסך",
        "wait 5 seconds"
    ]
    
    print("Testing NLP Command Parser:")
    print("=" * 50)
    
    for cmd in test_commands:
        action = parser.parse_command(cmd)
        print(f"Command: {cmd}")
        print(f"Action: {action.type}")
        print(f"Target: {action.target}")
        print(f"Parameters: {action.parameters}")
        print(f"Confidence: {action.confidence}")
        print(f"Reasoning: {action.reasoning}")
        print("-" * 30)


