"""
Predictive Action Engine for Zero Agent
Combines multiple prediction sources to suggest proactive actions
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging

from .behavior_learner import BehaviorLearner, Prediction
from .nlp_parser import Action

logger = logging.getLogger(__name__)


@dataclass
class ProactiveSuggestion:
    """Proactive action suggestion"""
    action: Action
    confidence: float
    reasoning: str
    urgency: str  # low, medium, high
    category: str  # routine, context, time, pattern
    estimated_benefit: float  # 0.0-1.0
    time_to_execute: float  # seconds


class PredictiveActionEngine:
    """
    Advanced Predictive Action Engine
    
    Combines multiple prediction sources:
    - Behavior learning patterns
    - Time-based patterns
    - Context analysis
    - User preferences
    - System state
    """
    
    def __init__(self, behavior_learner: BehaviorLearner, llm=None):
        self.behavior_learner = behavior_learner
        self.llm = llm
        
        # Prediction weights
        self.weights = {
            "behavior_pattern": 0.4,
            "time_pattern": 0.3,
            "context_analysis": 0.2,
            "user_preference": 0.1
        }
        
        # Urgency thresholds
        self.urgency_thresholds = {
            "high": 0.8,
            "medium": 0.6,
            "low": 0.4
        }
        
        # Category definitions
        self.categories = {
            "routine": "Regular user routine",
            "context": "Based on current context",
            "time": "Time-based pattern",
            "pattern": "Behavior pattern",
            "proactive": "Proactive system action"
        }
        
        logger.info("Predictive Action Engine initialized")
    
    def generate_predictions(self, current_context: Dict, max_predictions: int = 10) -> List[ProactiveSuggestion]:
        """
        Generate comprehensive predictions
        
        Args:
            current_context: Current system/application context
            max_predictions: Maximum number of predictions
            
        Returns:
            List of proactive suggestions sorted by confidence
        """
        try:
            all_predictions = []
            
            # 1. Behavior-based predictions
            behavior_predictions = self._get_behavior_predictions(current_context)
            all_predictions.extend(behavior_predictions)
            
            # 2. Time-based predictions
            time_predictions = self._get_time_predictions(current_context)
            all_predictions.extend(time_predictions)
            
            # 3. Context-based predictions
            context_predictions = self._get_context_predictions(current_context)
            all_predictions.extend(context_predictions)
            
            # 4. Proactive system predictions
            proactive_predictions = self._get_proactive_predictions(current_context)
            all_predictions.extend(proactive_predictions)
            
            # 5. Combine and rank predictions
            combined_predictions = self._combine_predictions(all_predictions)
            
            # 6. Filter and sort
            filtered_predictions = self._filter_predictions(combined_predictions, current_context)
            sorted_predictions = sorted(filtered_predictions, key=lambda x: x.confidence, reverse=True)
            
            return sorted_predictions[:max_predictions]
            
        except Exception as e:
            logger.error(f"Prediction generation failed: {e}")
            return []
    
    def _get_behavior_predictions(self, context: Dict) -> List[ProactiveSuggestion]:
        """Get predictions from behavior learning"""
        try:
            predictions = self.behavior_learner.predict_next_actions(context, max_predictions=5)
            
            suggestions = []
            for pred in predictions:
                action = Action(
                    type=pred.action_type,
                    target=pred.target,
                    parameters=pred.parameters,
                    confidence=pred.confidence
                )
                
                suggestion = ProactiveSuggestion(
                    action=action,
                    confidence=pred.confidence * self.weights["behavior_pattern"],
                    reasoning=f"Behavior pattern: {pred.reasoning}",
                    urgency=self._calculate_urgency(pred.confidence),
                    category="pattern",
                    estimated_benefit=self._estimate_benefit(action, context),
                    time_to_execute=self._estimate_execution_time(action)
                )
                
                suggestions.append(suggestion)
            
            return suggestions
            
        except Exception as e:
            logger.warning(f"Behavior prediction failed: {e}")
            return []
    
    def _get_time_predictions(self, context: Dict) -> List[ProactiveSuggestion]:
        """Get time-based predictions"""
        try:
            current_time = datetime.now()
            hour = current_time.hour
            day_of_week = current_time.weekday()
            
            suggestions = []
            
            # Morning routine (7-9 AM)
            if 7 <= hour <= 9:
                suggestions.append(self._create_time_suggestion(
                    Action(type="screenshot", target="screen", parameters={}),
                    confidence=0.7,
                    reasoning="Morning routine - take daily screenshot",
                    category="routine"
                ))
            
            # Work hours (9-17)
            elif 9 <= hour <= 17:
                suggestions.append(self._create_time_suggestion(
                    Action(type="scroll", target="page", parameters={"x": 0, "y": 100}),
                    confidence=0.5,
                    reasoning="Work hours - likely to scroll content",
                    category="time"
                ))
            
            # Evening routine (18-20)
            elif 18 <= hour <= 20:
                suggestions.append(self._create_time_suggestion(
                    Action(type="click", target="close_button", parameters={}),
                    confidence=0.6,
                    reasoning="Evening routine - likely to close applications",
                    category="routine"
                ))
            
            # Weekend patterns
            if day_of_week in [5, 6]:  # Saturday, Sunday
                suggestions.append(self._create_time_suggestion(
                    Action(type="type", target="search", parameters={"text": "news"}),
                    confidence=0.4,
                    reasoning="Weekend - likely to search for news",
                    category="time"
                ))
            
            return suggestions
            
        except Exception as e:
            logger.warning(f"Time prediction failed: {e}")
            return []
    
    def _get_context_predictions(self, context: Dict) -> List[ProactiveSuggestion]:
        """Get context-based predictions"""
        try:
            suggestions = []
            
            app_name = context.get("app_name", "").lower()
            screen_elements = context.get("ui_elements", [])
            
            # Browser-specific predictions
            if any(browser in app_name for browser in ["chrome", "firefox", "edge", "browser"]):
                suggestions.append(self._create_context_suggestion(
                    Action(type="scroll", target="page", parameters={"x": 0, "y": 200}),
                    confidence=0.6,
                    reasoning="Browser context - likely to scroll down",
                    category="context"
                ))
                
                # Check for search elements
                if any("search" in str(elem).lower() for elem in screen_elements):
                    suggestions.append(self._create_context_suggestion(
                        Action(type="click", target="search_box", parameters={}),
                        confidence=0.7,
                        reasoning="Search box detected - likely to search",
                        category="context"
                    ))
            
            # Text editor predictions
            elif any(editor in app_name for editor in ["notepad", "text", "editor", "word"]):
                suggestions.append(self._create_context_suggestion(
                    Action(type="type", target="text_area", parameters={"text": ""}),
                    confidence=0.8,
                    reasoning="Text editor context - likely to type",
                    category="context"
                ))
            
            # File manager predictions
            elif any(fm in app_name for fm in ["explorer", "finder", "files"]):
                suggestions.append(self._create_context_suggestion(
                    Action(type="click", target="file", parameters={}),
                    confidence=0.5,
                    reasoning="File manager context - likely to open file",
                    category="context"
                ))
            
            return suggestions
            
        except Exception as e:
            logger.warning(f"Context prediction failed: {e}")
            return []
    
    def _get_proactive_predictions(self, context: Dict) -> List[ProactiveSuggestion]:
        """Get proactive system predictions"""
        try:
            suggestions = []
            
            # System maintenance suggestions
            suggestions.append(self._create_proactive_suggestion(
                Action(type="screenshot", target="screen", parameters={}),
                confidence=0.3,
                reasoning="Proactive: Regular system monitoring",
                category="proactive"
            ))
            
            # Performance monitoring
            if context.get("system_load", 0) > 0.8:
                suggestions.append(self._create_proactive_suggestion(
                    Action(type="click", target="task_manager", parameters={}),
                    confidence=0.6,
                    reasoning="High system load detected - check task manager",
                    category="proactive"
                ))
            
            # Memory usage monitoring
            if context.get("memory_usage", 0) > 0.9:
                suggestions.append(self._create_proactive_suggestion(
                    Action(type="click", target="close_app", parameters={}),
                    confidence=0.7,
                    reasoning="High memory usage - close unnecessary apps",
                    category="proactive"
                ))
            
            return suggestions
            
        except Exception as e:
            logger.warning(f"Proactive prediction failed: {e}")
            return []
    
    def _create_time_suggestion(self, action: Action, confidence: float, reasoning: str, category: str) -> ProactiveSuggestion:
        """Create time-based suggestion"""
        return ProactiveSuggestion(
            action=action,
            confidence=confidence * self.weights["time_pattern"],
            reasoning=reasoning,
            urgency=self._calculate_urgency(confidence),
            category=category,
            estimated_benefit=self._estimate_benefit(action, {}),
            time_to_execute=self._estimate_execution_time(action)
        )
    
    def _create_context_suggestion(self, action: Action, confidence: float, reasoning: str, category: str) -> ProactiveSuggestion:
        """Create context-based suggestion"""
        return ProactiveSuggestion(
            action=action,
            confidence=confidence * self.weights["context_analysis"],
            reasoning=reasoning,
            urgency=self._calculate_urgency(confidence),
            category=category,
            estimated_benefit=self._estimate_benefit(action, {}),
            time_to_execute=self._estimate_execution_time(action)
        )
    
    def _create_proactive_suggestion(self, action: Action, confidence: float, reasoning: str, category: str) -> ProactiveSuggestion:
        """Create proactive suggestion"""
        return ProactiveSuggestion(
            action=action,
            confidence=confidence,
            reasoning=reasoning,
            urgency=self._calculate_urgency(confidence),
            category=category,
            estimated_benefit=self._estimate_benefit(action, {}),
            time_to_execute=self._estimate_execution_time(action)
        )
    
    def _calculate_urgency(self, confidence: float) -> str:
        """Calculate urgency level based on confidence"""
        if confidence >= self.urgency_thresholds["high"]:
            return "high"
        elif confidence >= self.urgency_thresholds["medium"]:
            return "medium"
        else:
            return "low"
    
    def _estimate_benefit(self, action: Action, context: Dict) -> float:
        """Estimate benefit of executing action"""
        try:
            # Base benefit on action type and context
            base_benefits = {
                "screenshot": 0.3,  # Documentation
                "click": 0.7,       # Interaction
                "type": 0.8,        # Input
                "scroll": 0.5,      # Navigation
                "drag": 0.6,        # Manipulation
                "wait": 0.2         # Pause
            }
            
            base_benefit = base_benefits.get(action.type, 0.5)
            
            # Adjust based on context
            if action.type == "screenshot" and context.get("important_moment"):
                base_benefit += 0.3
            
            if action.type == "click" and context.get("frequent_target"):
                base_benefit += 0.2
            
            return min(1.0, base_benefit)
            
        except Exception as e:
            logger.warning(f"Benefit estimation failed: {e}")
            return 0.5
    
    def _estimate_execution_time(self, action: Action) -> float:
        """Estimate time to execute action in seconds"""
        time_estimates = {
            "screenshot": 0.5,
            "click": 0.2,
            "type": 1.0,
            "scroll": 0.3,
            "drag": 1.5,
            "wait": 1.0
        }
        
        base_time = time_estimates.get(action.type, 0.5)
        
        # Adjust for text length
        if action.type == "type" and action.parameters.get("text"):
            text_length = len(action.parameters["text"])
            base_time += text_length * 0.1
        
        return base_time
    
    def _combine_predictions(self, predictions: List[ProactiveSuggestion]) -> List[ProactiveSuggestion]:
        """Combine and deduplicate predictions"""
        try:
            # Group by action type and target
            grouped = {}
            
            for suggestion in predictions:
                key = (suggestion.action.type, suggestion.action.target)
                
                if key in grouped:
                    # Combine with existing suggestion
                    existing = grouped[key]
                    combined_confidence = max(existing.confidence, suggestion.confidence)
                    combined_reasoning = f"{existing.reasoning}; {suggestion.reasoning}"
                    
                    grouped[key] = ProactiveSuggestion(
                        action=suggestion.action,
                        confidence=combined_confidence,
                        reasoning=combined_reasoning,
                        urgency=self._calculate_urgency(combined_confidence),
                        category=suggestion.category,
                        estimated_benefit=max(existing.estimated_benefit, suggestion.estimated_benefit),
                        time_to_execute=min(existing.time_to_execute, suggestion.time_to_execute)
                    )
                else:
                    grouped[key] = suggestion
            
            return list(grouped.values())
            
        except Exception as e:
            logger.warning(f"Prediction combination failed: {e}")
            return predictions
    
    def _filter_predictions(self, predictions: List[ProactiveSuggestion], context: Dict) -> List[ProactiveSuggestion]:
        """Filter predictions based on context and constraints"""
        try:
            filtered = []
            
            for suggestion in predictions:
                # Skip if confidence too low
                if suggestion.confidence < 0.3:
                    continue
                
                # Skip if estimated benefit too low
                if suggestion.estimated_benefit < 0.2:
                    continue
                
                # Skip if execution time too long
                if suggestion.time_to_execute > 10.0:
                    continue
                
                # Context-specific filtering
                if self._is_relevant_to_context(suggestion, context):
                    filtered.append(suggestion)
            
            return filtered
            
        except Exception as e:
            logger.warning(f"Prediction filtering failed: {e}")
            return predictions
    
    def _is_relevant_to_context(self, suggestion: ProactiveSuggestion, context: Dict) -> bool:
        """Check if suggestion is relevant to current context"""
        try:
            app_name = context.get("app_name", "").lower()
            action_type = suggestion.action.type
            
            # Context-specific relevance checks
            if action_type == "screenshot":
                return True  # Always relevant
            
            if action_type == "click" and "button" in suggestion.action.target:
                return True  # Buttons are generally relevant
            
            if action_type == "type" and any(editor in app_name for editor in ["text", "notepad", "word"]):
                return True  # Typing in text editors
            
            if action_type == "scroll" and any(browser in app_name for browser in ["chrome", "firefox", "browser"]):
                return True  # Scrolling in browsers
            
            return True  # Default to relevant
            
        except Exception as e:
            logger.warning(f"Context relevance check failed: {e}")
            return True
    
    def get_prediction_summary(self, predictions: List[ProactiveSuggestion]) -> Dict[str, Any]:
        """Get summary of predictions"""
        try:
            if not predictions:
                return {"message": "No predictions available"}
            
            # Count by category
            category_counts = {}
            urgency_counts = {}
            total_confidence = 0
            
            for pred in predictions:
                category_counts[pred.category] = category_counts.get(pred.category, 0) + 1
                urgency_counts[pred.urgency] = urgency_counts.get(pred.urgency, 0) + 1
                total_confidence += pred.confidence
            
            avg_confidence = total_confidence / len(predictions)
            
            return {
                "total_predictions": len(predictions),
                "average_confidence": round(avg_confidence, 3),
                "category_breakdown": category_counts,
                "urgency_breakdown": urgency_counts,
                "top_prediction": {
                    "action": pred.action.type,
                    "reasoning": pred.reasoning,
                    "confidence": pred.confidence
                } if predictions else None
            }
            
        except Exception as e:
            logger.error(f"Prediction summary failed: {e}")
            return {"error": str(e)}


# Example usage and testing
if __name__ == "__main__":
    from .behavior_learner import BehaviorLearner
    
    # Initialize components
    behavior_learner = BehaviorLearner()
    engine = PredictiveActionEngine(behavior_learner)
    
    # Test context
    test_context = {
        "app_name": "chrome",
        "ui_elements": [{"type": "button", "text": "Search"}],
        "system_load": 0.5,
        "memory_usage": 0.7
    }
    
    # Generate predictions
    predictions = engine.generate_predictions(test_context)
    
    print("Predictive Action Engine Test:")
    print("=" * 50)
    print(f"Generated {len(predictions)} predictions")
    
    for i, pred in enumerate(predictions[:3]):  # Show top 3
        print(f"\n{i+1}. {pred.action.type} -> {pred.action.target}")
        print(f"   Confidence: {pred.confidence:.2f}")
        print(f"   Reasoning: {pred.reasoning}")
        print(f"   Urgency: {pred.urgency}")
        print(f"   Category: {pred.category}")
    
    # Get summary
    summary = engine.get_prediction_summary(predictions)
    print(f"\nSummary: {summary}")









