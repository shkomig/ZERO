"""
Proactive Assistant for Zero Agent
Coordinates predictive actions and provides intelligent assistance
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging

from .predictive_engine import PredictiveActionEngine, ProactiveSuggestion
from .behavior_learner import BehaviorLearner, UserAction
from .vision_agent import VisionAgent
from .nlp_parser import NLPCommandParser, Action

logger = logging.getLogger(__name__)


@dataclass
class AssistantState:
    """Current state of the proactive assistant"""
    is_active: bool
    last_activity: datetime
    suggestion_count: int
    executed_actions: int
    user_feedback: Dict[str, Any]
    current_context: Dict[str, Any]


class ProactiveAssistant:
    """
    Proactive Assistant
    
    Coordinates all predictive systems and provides intelligent assistance
    Features:
    - Proactive action suggestions
    - Learning from user feedback
    - Context-aware recommendations
    - Smart timing of suggestions
    """
    
    def __init__(self, orchestrator=None, llm=None, data_dir: str = "workspace/assistant_data"):
        self.orchestrator = orchestrator
        self.llm = llm
        self.data_dir = data_dir
        
        # Initialize components
        self.behavior_learner = BehaviorLearner()
        self.predictive_engine = PredictiveActionEngine(self.behavior_learner, llm)
        self.vision_agent = VisionAgent(llm)
        self.nlp_parser = NLPCommandParser(llm)
        
        # Assistant state
        self.state = AssistantState(
            is_active=True,
            last_activity=datetime.now(),
            suggestion_count=0,
            executed_actions=0,
            user_feedback={},
            current_context={}
        )
        
        # Configuration
        self.suggestion_interval = 30  # seconds between suggestions
        self.max_suggestions_per_cycle = 3
        self.learning_enabled = True
        self.proactive_threshold = 0.6
        
        # Suggestion history
        self.suggestion_history: List[ProactiveSuggestion] = []
        self.user_responses: Dict[str, str] = {}  # suggestion_id -> response
        
        logger.info("Proactive Assistant initialized")
    
    def process_context_update(self, context: Dict[str, Any]) -> List[ProactiveSuggestion]:
        """
        Process context update and generate proactive suggestions
        
        Args:
            context: Updated system/application context
            
        Returns:
            List of proactive suggestions
        """
        try:
            # Update current context
            self.state.current_context.update(context)
            self.state.last_activity = datetime.now()
            
            # Check if we should generate suggestions
            if not self._should_generate_suggestions():
                return []
            
            # Generate predictions
            suggestions = self.predictive_engine.generate_predictions(
                self.state.current_context,
                max_predictions=self.max_suggestions_per_cycle
            )
            
            # Filter suggestions based on user preferences and history
            filtered_suggestions = self._filter_suggestions(suggestions)
            
            # Update suggestion history
            self.suggestion_history.extend(filtered_suggestions)
            self.state.suggestion_count += len(filtered_suggestions)
            
            # Learn from context if enabled
            if self.learning_enabled:
                self._learn_from_context(context)
            
            logger.info(f"Generated {len(filtered_suggestions)} proactive suggestions")
            return filtered_suggestions
            
        except Exception as e:
            logger.error(f"Context processing failed: {e}")
            return []
    
    def execute_suggestion(self, suggestion: ProactiveSuggestion, user_confirmation: bool = False) -> Dict[str, Any]:
        """
        Execute a proactive suggestion
        
        Args:
            suggestion: Suggestion to execute
            user_confirmation: Whether user confirmed the action
            
        Returns:
            Execution result
        """
        try:
            # Check if execution is allowed
            if not self._can_execute_suggestion(suggestion, user_confirmation):
                return {
                    "success": False,
                    "error": "Execution not allowed",
                    "reason": "User confirmation required or suggestion not suitable"
                }
            
            # Execute via orchestrator if available
            if self.orchestrator:
                result = self._execute_via_orchestrator(suggestion)
            else:
                result = self._execute_directly(suggestion)
            
            # Record execution
            self.state.executed_actions += 1
            
            # Learn from execution
            if self.learning_enabled:
                self._learn_from_execution(suggestion, result)
            
            # Update suggestion status
            suggestion_id = f"{suggestion.action.type}_{suggestion.action.target}_{datetime.now().timestamp()}"
            self.user_responses[suggestion_id] = "executed" if result.get("success") else "failed"
            
            logger.info(f"Executed suggestion: {suggestion.action.type} -> {suggestion.action.target}")
            return result
            
        except Exception as e:
            logger.error(f"Suggestion execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "reason": "Execution error"
            }
    
    def process_user_feedback(self, suggestion_id: str, feedback: str, details: Dict[str, Any] = None):
        """
        Process user feedback on suggestions
        
        Args:
            suggestion_id: ID of the suggestion
            feedback: User feedback (positive, negative, neutral)
            details: Additional feedback details
        """
        try:
            # Store feedback
            self.user_responses[suggestion_id] = feedback
            self.state.user_feedback[suggestion_id] = {
                "feedback": feedback,
                "details": details or {},
                "timestamp": datetime.now().isoformat()
            }
            
            # Learn from feedback
            if self.learning_enabled:
                self._learn_from_feedback(suggestion_id, feedback, details)
            
            logger.info(f"Processed feedback for {suggestion_id}: {feedback}")
            
        except Exception as e:
            logger.warning(f"Feedback processing failed: {e}")
    
    def get_suggestions_summary(self) -> Dict[str, Any]:
        """Get summary of current suggestions and assistant state"""
        try:
            recent_suggestions = self.suggestion_history[-10:]  # Last 10 suggestions
            
            # Calculate statistics
            total_suggestions = len(self.suggestion_history)
            executed_suggestions = sum(1 for resp in self.user_responses.values() if resp == "executed")
            positive_feedback = sum(1 for resp in self.user_responses.values() if resp == "positive")
            
            # Categorize suggestions
            categories = {}
            for suggestion in recent_suggestions:
                cat = suggestion.category
                categories[cat] = categories.get(cat, 0) + 1
            
            return {
                "assistant_state": {
                    "is_active": self.state.is_active,
                    "last_activity": self.state.last_activity.isoformat(),
                    "total_suggestions": total_suggestions,
                    "executed_actions": self.state.executed_actions,
                    "execution_rate": executed_suggestions / max(1, total_suggestions),
                    "positive_feedback_rate": positive_feedback / max(1, len(self.user_responses))
                },
                "recent_suggestions": [
                    {
                        "action": s.action.type,
                        "target": s.action.target,
                        "confidence": s.confidence,
                        "reasoning": s.reasoning,
                        "category": s.category,
                        "urgency": s.urgency
                    } for s in recent_suggestions
                ],
                "category_breakdown": categories,
                "learning_enabled": self.learning_enabled,
                "proactive_threshold": self.proactive_threshold
            }
            
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return {"error": str(e)}
    
    def _should_generate_suggestions(self) -> bool:
        """Check if we should generate new suggestions"""
        try:
            # Check if assistant is active
            if not self.state.is_active:
                return False
            
            # Check time since last activity
            time_since_activity = datetime.now() - self.state.last_activity
            if time_since_activity.total_seconds() < self.suggestion_interval:
                return False
            
            # Check if we have too many pending suggestions
            pending_count = len([s for s in self.suggestion_history if s not in self.user_responses])
            if pending_count >= self.max_suggestions_per_cycle:
                return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Suggestion timing check failed: {e}")
            return False
    
    def _filter_suggestions(self, suggestions: List[ProactiveSuggestion]) -> List[ProactiveSuggestion]:
        """Filter suggestions based on user preferences and history"""
        try:
            filtered = []
            
            for suggestion in suggestions:
                # Skip if confidence too low
                if suggestion.confidence < self.proactive_threshold:
                    continue
                
                # Skip if we've suggested this recently
                if self._was_recently_suggested(suggestion):
                    continue
                
                # Skip if user previously rejected similar suggestion
                if self._was_previously_rejected(suggestion):
                    continue
                
                # Apply user preferences
                if self._matches_user_preferences(suggestion):
                    filtered.append(suggestion)
            
            return filtered
            
        except Exception as e:
            logger.warning(f"Suggestion filtering failed: {e}")
            return suggestions
    
    def _was_recently_suggested(self, suggestion: ProactiveSuggestion) -> bool:
        """Check if similar suggestion was made recently"""
        try:
            recent_time = datetime.now() - timedelta(minutes=5)
            
            for prev_suggestion in self.suggestion_history:
                if prev_suggestion.action.type == suggestion.action.type and \
                   prev_suggestion.action.target == suggestion.action.target:
                    # Check if it was recent
                    if hasattr(prev_suggestion, 'timestamp') and \
                       prev_suggestion.timestamp > recent_time:
                        return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Recent suggestion check failed: {e}")
            return False
    
    def _was_previously_rejected(self, suggestion: ProactiveSuggestion) -> bool:
        """Check if user previously rejected similar suggestion"""
        try:
            for suggestion_id, response in self.user_responses.items():
                if response in ["negative", "rejected", "no"]:
                    # Check if it's similar to current suggestion
                    if self._are_suggestions_similar(suggestion_id, suggestion):
                        return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Rejection check failed: {e}")
            return False
    
    def _are_suggestions_similar(self, suggestion_id: str, suggestion: ProactiveSuggestion) -> bool:
        """Check if two suggestions are similar"""
        try:
            # Simple similarity check based on action type and target
            # In a real implementation, this would be more sophisticated
            return suggestion_id.startswith(f"{suggestion.action.type}_{suggestion.action.target}")
            
        except Exception as e:
            logger.warning(f"Similarity check failed: {e}")
            return False
    
    def _matches_user_preferences(self, suggestion: ProactiveSuggestion) -> bool:
        """Check if suggestion matches user preferences"""
        try:
            # Get user preferences from state
            preferences = self.state.user_feedback.get("preferences", {})
            
            # Check category preferences
            preferred_categories = preferences.get("categories", [])
            if preferred_categories and suggestion.category not in preferred_categories:
                return False
            
            # Check urgency preferences
            max_urgency = preferences.get("max_urgency", "high")
            urgency_levels = {"low": 1, "medium": 2, "high": 3}
            if urgency_levels.get(suggestion.urgency, 0) > urgency_levels.get(max_urgency, 3):
                return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Preference matching failed: {e}")
            return True  # Default to allowing suggestion
    
    def _can_execute_suggestion(self, suggestion: ProactiveSuggestion, user_confirmation: bool) -> bool:
        """Check if suggestion can be executed"""
        try:
            # High confidence suggestions can be executed automatically
            if suggestion.confidence >= 0.8 and suggestion.urgency == "high":
                return True
            
            # Medium confidence requires user confirmation
            if suggestion.confidence >= 0.6 and user_confirmation:
                return True
            
            # Low confidence always requires confirmation
            if suggestion.confidence < 0.6 and user_confirmation:
                return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Execution permission check failed: {e}")
            return False
    
    def _execute_via_orchestrator(self, suggestion: ProactiveSuggestion) -> Dict[str, Any]:
        """Execute suggestion via orchestrator"""
        try:
            if not self.orchestrator:
                return {"success": False, "error": "No orchestrator available"}
            
            # Convert suggestion to orchestrator format
            command = self._suggestion_to_command(suggestion)
            
            # Execute via orchestrator
            result = self.orchestrator.execute_goal(command)
            
            return {
                "success": result.get("success", False),
                "result": result.get("output", ""),
                "error": result.get("error"),
                "method": "orchestrator"
            }
            
        except Exception as e:
            logger.error(f"Orchestrator execution failed: {e}")
            return {"success": False, "error": str(e), "method": "orchestrator"}
    
    def _execute_directly(self, suggestion: ProactiveSuggestion) -> Dict[str, Any]:
        """Execute suggestion directly"""
        try:
            # Direct execution based on action type
            action = suggestion.action
            
            if action.type == "screenshot":
                # Take screenshot
                return {"success": True, "result": "Screenshot taken", "method": "direct"}
            
            elif action.type == "click":
                # Simulate click (would need actual implementation)
                return {"success": True, "result": f"Clicked {action.target}", "method": "direct"}
            
            elif action.type == "type":
                # Simulate typing
                text = action.parameters.get("text", "")
                return {"success": True, "result": f"Typed: {text}", "method": "direct"}
            
            else:
                return {"success": False, "error": f"Unknown action type: {action.type}", "method": "direct"}
            
        except Exception as e:
            logger.error(f"Direct execution failed: {e}")
            return {"success": False, "error": str(e), "method": "direct"}
    
    def _suggestion_to_command(self, suggestion: ProactiveSuggestion) -> str:
        """Convert suggestion to natural language command"""
        try:
            action = suggestion.action
            
            if action.type == "click":
                return f"Click on {action.target}"
            elif action.type == "type":
                text = action.parameters.get("text", "")
                return f"Type '{text}'"
            elif action.type == "scroll":
                return f"Scroll {action.parameters.get('x', 0)}, {action.parameters.get('y', 100)}"
            elif action.type == "screenshot":
                return "Take screenshot"
            else:
                return f"Execute {action.type} on {action.target}"
                
        except Exception as e:
            logger.warning(f"Command conversion failed: {e}")
            return f"Execute {suggestion.action.type}"
    
    def _learn_from_context(self, context: Dict[str, Any]):
        """Learn from context update"""
        try:
            if not self.learning_enabled:
                return
            
            # Create context action for learning
            context_action = UserAction(
                timestamp=datetime.now(),
                action_type="context_update",
                target="system",
                parameters=context,
                success=True,
                context=context
            )
            
            # Learn from context
            self.behavior_learner.learn_from_action(context_action)
            
        except Exception as e:
            logger.warning(f"Context learning failed: {e}")
    
    def _learn_from_execution(self, suggestion: ProactiveSuggestion, result: Dict[str, Any]):
        """Learn from suggestion execution"""
        try:
            if not self.learning_enabled:
                return
            
            # Create execution action for learning
            execution_action = UserAction(
                timestamp=datetime.now(),
                action_type=suggestion.action.type,
                target=suggestion.action.target,
                parameters=suggestion.action.parameters,
                success=result.get("success", False),
                context=self.state.current_context,
                duration=suggestion.time_to_execute
            )
            
            # Learn from execution
            self.behavior_learner.learn_from_action(execution_action)
            
        except Exception as e:
            logger.warning(f"Execution learning failed: {e}")
    
    def _learn_from_feedback(self, suggestion_id: str, feedback: str, details: Dict[str, Any]):
        """Learn from user feedback"""
        try:
            if not self.learning_enabled:
                return
            
            # Update learning based on feedback
            if feedback in ["positive", "good", "yes"]:
                # Positive feedback - increase confidence for similar suggestions
                self._adjust_confidence_for_feedback(suggestion_id, 0.1)
            elif feedback in ["negative", "bad", "no"]:
                # Negative feedback - decrease confidence for similar suggestions
                self._adjust_confidence_for_feedback(suggestion_id, -0.1)
            
        except Exception as e:
            logger.warning(f"Feedback learning failed: {e}")
    
    def _adjust_confidence_for_feedback(self, suggestion_id: str, adjustment: float):
        """Adjust confidence for similar suggestions based on feedback"""
        try:
            # This is a simplified implementation
            # In a real system, this would be more sophisticated
            for suggestion in self.suggestion_history:
                if suggestion_id.startswith(f"{suggestion.action.type}_{suggestion.action.target}"):
                    suggestion.confidence = max(0.0, min(1.0, suggestion.confidence + adjustment))
            
        except Exception as e:
            logger.warning(f"Confidence adjustment failed: {e}")


# Example usage and testing
if __name__ == "__main__":
    async def test_proactive_assistant():
        assistant = ProactiveAssistant()
        
        # Test context update
        context = {
            "app_name": "chrome",
            "ui_elements": [{"type": "button", "text": "Search"}],
            "system_load": 0.5
        }
        
        suggestions = assistant.process_context_update(context)
        print(f"Generated {len(suggestions)} suggestions")
        
        for suggestion in suggestions:
            print(f"- {suggestion.action.type}: {suggestion.reasoning}")
        
        # Test execution
        if suggestions:
            result = assistant.execute_suggestion(suggestions[0], user_confirmation=True)
            print(f"Execution result: {result}")
        
        # Get summary
        summary = assistant.get_suggestions_summary()
        print(f"Assistant summary: {summary}")
    
    # Run test
    asyncio.run(test_proactive_assistant())
