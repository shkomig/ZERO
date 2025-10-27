"""
Behavior Learning System for Zero Agent
Learns from user actions and predicts future behavior
"""

import json
import pickle
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class UserAction:
    """Record of user action"""
    timestamp: datetime
    action_type: str
    target: str
    parameters: Dict[str, Any]
    success: bool
    context: Dict[str, Any]
    duration: float = 0.0


@dataclass
class ActionPattern:
    """Identified pattern in user behavior"""
    pattern_id: str
    sequence: List[str]  # Sequence of action types
    frequency: int
    success_rate: float
    avg_duration: float
    last_seen: datetime
    confidence: float


@dataclass
class Prediction:
    """Predicted next action"""
    action_type: str
    target: str
    parameters: Dict[str, Any]
    confidence: float
    reasoning: str
    based_on: str  # What pattern this is based on


class BehaviorLearner:
    """
    Advanced Behavior Learning System
    
    Learns from user actions and predicts future behavior
    Supports pattern recognition, success rate tracking, and proactive suggestions
    """
    
    def __init__(self, memory_system=None, data_dir: str = "workspace/behavior_data"):
        self.memory = memory_system
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Action storage
        self.action_history: deque = deque(maxlen=1000)  # Keep last 1000 actions
        self.action_patterns: Dict[str, ActionPattern] = {}
        self.success_rates: Dict[str, float] = defaultdict(float)
        self.action_frequencies: Dict[str, int] = defaultdict(int)
        
        # Learning parameters
        self.min_pattern_length = 2
        self.max_pattern_length = 5
        self.min_pattern_frequency = 3
        self.confidence_threshold = 0.6
        
        # Time-based learning
        self.time_patterns: Dict[str, List[UserAction]] = defaultdict(list)
        self.day_patterns: Dict[int, List[UserAction]] = defaultdict(list)  # Day of week
        
        # Load existing data
        self._load_learning_data()
        
        logger.info("Behavior Learning System initialized")
    
    def learn_from_action(self, action: UserAction):
        """
        Learn from a user action
        
        Args:
            action: UserAction object with action details
        """
        try:
            # Store action
            self.action_history.append(action)
            
            # Update frequencies
            action_key = f"{action.action_type}_{action.target}"
            self.action_frequencies[action_key] += 1
            
            # Update success rate
            if action.success:
                self.success_rates[action_key] = min(1.0, self.success_rates[action_key] + 0.1)
            else:
                self.success_rates[action_key] = max(0.0, self.success_rates[action_key] - 0.05)
            
            # Update time-based patterns
            self._update_time_patterns(action)
            
            # Identify new patterns
            self._identify_patterns()
            
            # Save learning data
            self._save_learning_data()
            
            logger.debug(f"Learned from action: {action.action_type} -> {action.target}")
            
        except Exception as e:
            logger.error(f"Learning from action failed: {e}")
    
    def predict_next_actions(self, current_context: Dict, max_predictions: int = 5) -> List[Prediction]:
        """
        Predict likely next actions based on learned patterns
        
        Args:
            current_context: Current screen/application context
            max_predictions: Maximum number of predictions to return
            
        Returns:
            List of predicted actions sorted by confidence
        """
        try:
            predictions = []
            
            # 1. Pattern-based predictions
            pattern_predictions = self._predict_from_patterns(current_context)
            predictions.extend(pattern_predictions)
            
            # 2. Time-based predictions
            time_predictions = self._predict_from_time_patterns(current_context)
            predictions.extend(time_predictions)
            
            # 3. Frequency-based predictions
            frequency_predictions = self._predict_from_frequency(current_context)
            predictions.extend(frequency_predictions)
            
            # 4. Context-based predictions
            context_predictions = self._predict_from_context(current_context)
            predictions.extend(context_predictions)
            
            # Remove duplicates and sort by confidence
            unique_predictions = self._deduplicate_predictions(predictions)
            sorted_predictions = sorted(unique_predictions, key=lambda x: x.confidence, reverse=True)
            
            return sorted_predictions[:max_predictions]
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return []
    
    def _update_time_patterns(self, action: UserAction):
        """Update time-based learning patterns"""
        try:
            # Hour-based patterns
            hour = action.timestamp.hour
            self.time_patterns[hour].append(action)
            
            # Keep only recent actions (last 30 days)
            cutoff = datetime.now() - timedelta(days=30)
            self.time_patterns[hour] = [
                a for a in self.time_patterns[hour] 
                if a.timestamp > cutoff
            ]
            
            # Day-of-week patterns
            day_of_week = action.timestamp.weekday()
            self.day_patterns[day_of_week].append(action)
            
            # Keep only recent actions
            self.day_patterns[day_of_week] = [
                a for a in self.day_patterns[day_of_week] 
                if a.timestamp > cutoff
            ]
            
        except Exception as e:
            logger.warning(f"Time pattern update failed: {e}")
    
    def _identify_patterns(self):
        """Identify recurring patterns in user behavior"""
        try:
            if len(self.action_history) < self.min_pattern_length:
                return
            
            # Get recent actions for pattern analysis
            recent_actions = list(self.action_history)[-50:]  # Last 50 actions
            
            # Find patterns of different lengths
            for pattern_length in range(self.min_pattern_length, self.max_pattern_length + 1):
                patterns = self._find_sequences(recent_actions, pattern_length)
                
                for pattern in patterns:
                    pattern_key = "_".join([a.action_type for a in pattern])
                    
                    if pattern_key in self.action_patterns:
                        # Update existing pattern
                        self._update_pattern(pattern_key, pattern)
                    else:
                        # Create new pattern
                        self._create_pattern(pattern_key, pattern)
            
        except Exception as e:
            logger.warning(f"Pattern identification failed: {e}")
    
    def _find_sequences(self, actions: List[UserAction], length: int) -> List[List[UserAction]]:
        """Find sequences of specific length"""
        sequences = []
        
        for i in range(len(actions) - length + 1):
            sequence = actions[i:i + length]
            sequences.append(sequence)
        
        return sequences
    
    def _create_pattern(self, pattern_key: str, sequence: List[UserAction]):
        """Create new action pattern"""
        try:
            action_types = [a.action_type for a in sequence]
            success_count = sum(1 for a in sequence if a.success)
            avg_duration = sum(a.duration for a in sequence) / len(sequence)
            
            pattern = ActionPattern(
                pattern_id=pattern_key,
                sequence=action_types,
                frequency=1,
                success_rate=success_count / len(sequence),
                avg_duration=avg_duration,
                last_seen=sequence[-1].timestamp,
                confidence=0.5  # Initial confidence
            )
            
            self.action_patterns[pattern_key] = pattern
            logger.debug(f"Created new pattern: {pattern_key}")
            
        except Exception as e:
            logger.warning(f"Pattern creation failed: {e}")
    
    def _update_pattern(self, pattern_key: str, sequence: List[UserAction]):
        """Update existing action pattern"""
        try:
            if pattern_key not in self.action_patterns:
                return
            
            pattern = self.action_patterns[pattern_key]
            
            # Update frequency
            pattern.frequency += 1
            
            # Update success rate (weighted average)
            success_count = sum(1 for a in sequence if a.success)
            new_success_rate = success_count / len(sequence)
            pattern.success_rate = (pattern.success_rate * (pattern.frequency - 1) + new_success_rate) / pattern.frequency
            
            # Update average duration
            new_avg_duration = sum(a.duration for a in sequence) / len(sequence)
            pattern.avg_duration = (pattern.avg_duration * (pattern.frequency - 1) + new_avg_duration) / pattern.frequency
            
            # Update last seen
            pattern.last_seen = sequence[-1].timestamp
            
            # Update confidence based on frequency and recency
            recency_factor = self._calculate_recency_factor(pattern.last_seen)
            frequency_factor = min(1.0, pattern.frequency / 10)  # Max confidence at 10 occurrences
            pattern.confidence = (recency_factor + frequency_factor) / 2
            
        except Exception as e:
            logger.warning(f"Pattern update failed: {e}")
    
    def _calculate_recency_factor(self, last_seen: datetime) -> float:
        """Calculate recency factor for pattern confidence"""
        hours_since = (datetime.now() - last_seen).total_seconds() / 3600
        
        if hours_since < 1:
            return 1.0
        elif hours_since < 24:
            return 0.8
        elif hours_since < 168:  # 1 week
            return 0.6
        elif hours_since < 720:  # 1 month
            return 0.4
        else:
            return 0.2
    
    def _predict_from_patterns(self, context: Dict) -> List[Prediction]:
        """Predict actions based on learned patterns"""
        predictions = []
        
        try:
            # Get recent action sequence
            recent_actions = list(self.action_history)[-5:]  # Last 5 actions
            if len(recent_actions) < 2:
                return predictions
            
            # Find matching patterns
            for pattern_id, pattern in self.action_patterns.items():
                if pattern.confidence < self.confidence_threshold:
                    continue
                
                # Check if recent actions match pattern start
                if self._matches_pattern_start(recent_actions, pattern.sequence):
                    # Predict next action in pattern
                    next_action_type = self._get_next_action_in_pattern(recent_actions, pattern)
                    if next_action_type:
                        prediction = Prediction(
                            action_type=next_action_type,
                            target="predicted",
                            parameters={},
                            confidence=pattern.confidence * 0.8,  # Slightly lower confidence
                            reasoning=f"Based on pattern: {pattern_id}",
                            based_on=f"pattern_{pattern_id}"
                        )
                        predictions.append(prediction)
            
        except Exception as e:
            logger.warning(f"Pattern-based prediction failed: {e}")
        
        return predictions
    
    def _matches_pattern_start(self, recent_actions: List[UserAction], pattern_sequence: List[str]) -> bool:
        """Check if recent actions match the start of a pattern"""
        if len(recent_actions) < len(pattern_sequence) - 1:
            return False
        
        # Check if the last N actions match the pattern start
        recent_types = [a.action_type for a in recent_actions]
        pattern_start = pattern_sequence[:-1]  # All but last action
        
        return recent_types[-len(pattern_start):] == pattern_start
    
    def _get_next_action_in_pattern(self, recent_actions: List[UserAction], pattern: ActionPattern) -> Optional[str]:
        """Get the next action type in a pattern"""
        if len(pattern.sequence) <= len(recent_actions):
            return None
        
        return pattern.sequence[len(recent_actions)]
    
    def _predict_from_time_patterns(self, context: Dict) -> List[Prediction]:
        """Predict actions based on time patterns"""
        predictions = []
        
        try:
            current_hour = datetime.now().hour
            current_day = datetime.now().weekday()
            
            # Hour-based predictions
            if current_hour in self.time_patterns:
                hour_actions = self.time_patterns[current_hour]
                if hour_actions:
                    most_common = self._get_most_common_action(hour_actions)
                    if most_common:
                        predictions.append(Prediction(
                            action_type=most_common.action_type,
                            target=most_common.target,
                            parameters=most_common.parameters,
                            confidence=0.6,
                            reasoning=f"Common action at {current_hour}:00",
                            based_on=f"time_{current_hour}"
                        ))
            
            # Day-based predictions
            if current_day in self.day_patterns:
                day_actions = self.day_patterns[current_day]
                if day_actions:
                    most_common = self._get_most_common_action(day_actions)
                    if most_common:
                        predictions.append(Prediction(
                            action_type=most_common.action_type,
                            target=most_common.target,
                            parameters=most_common.parameters,
                            confidence=0.5,
                            reasoning=f"Common action on {self._get_day_name(current_day)}",
                            based_on=f"day_{current_day}"
                        ))
            
        except Exception as e:
            logger.warning(f"Time-based prediction failed: {e}")
        
        return predictions
    
    def _predict_from_frequency(self, context: Dict) -> List[Prediction]:
        """Predict actions based on frequency"""
        predictions = []
        
        try:
            # Get most frequent actions
            sorted_frequencies = sorted(
                self.action_frequencies.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            for action_key, frequency in sorted_frequencies[:3]:  # Top 3
                action_type, target = action_key.split("_", 1)
                success_rate = self.success_rates.get(action_key, 0.5)
                
                predictions.append(Prediction(
                    action_type=action_type,
                    target=target,
                    parameters={},
                    confidence=min(0.7, frequency / 10) * success_rate,
                    reasoning=f"Frequent action (used {frequency} times)",
                    based_on="frequency"
                ))
            
        except Exception as e:
            logger.warning(f"Frequency-based prediction failed: {e}")
        
        return predictions
    
    def _predict_from_context(self, context: Dict) -> List[Prediction]:
        """Predict actions based on current context"""
        predictions = []
        
        try:
            # Context-based heuristics
            app_name = context.get("app_name", "").lower()
            
            if "browser" in app_name or "chrome" in app_name:
                predictions.append(Prediction(
                    action_type="scroll",
                    target="page",
                    parameters={"x": 0, "y": 100},
                    confidence=0.4,
                    reasoning="Common browser action",
                    based_on="context_browser"
                ))
            
            elif "notepad" in app_name or "text" in app_name:
                predictions.append(Prediction(
                    action_type="type",
                    target="text_area",
                    parameters={"text": ""},
                    confidence=0.4,
                    reasoning="Common text editor action",
                    based_on="context_text"
                ))
            
        except Exception as e:
            logger.warning(f"Context-based prediction failed: {e}")
        
        return predictions
    
    def _get_most_common_action(self, actions: List[UserAction]) -> Optional[UserAction]:
        """Get the most common action from a list"""
        if not actions:
            return None
        
        # Count action types
        action_counts = defaultdict(int)
        for action in actions:
            action_counts[action.action_type] += 1
        
        # Find most common
        most_common_type = max(action_counts.items(), key=lambda x: x[1])[0]
        
        # Return first action of most common type
        for action in actions:
            if action.action_type == most_common_type:
                return action
        
        return None
    
    def _get_day_name(self, day_of_week: int) -> str:
        """Get day name from day of week number"""
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return days[day_of_week]
    
    def _deduplicate_predictions(self, predictions: List[Prediction]) -> List[Prediction]:
        """Remove duplicate predictions"""
        seen = set()
        unique_predictions = []
        
        for prediction in predictions:
            key = (prediction.action_type, prediction.target)
            if key not in seen:
                seen.add(key)
                unique_predictions.append(prediction)
        
        return unique_predictions
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get learning statistics"""
        try:
            total_actions = len(self.action_history)
            unique_patterns = len(self.action_patterns)
            
            # Calculate average success rate
            avg_success_rate = 0.0
            if self.success_rates:
                avg_success_rate = sum(self.success_rates.values()) / len(self.success_rates)
            
            # Get most frequent actions
            top_actions = sorted(
                self.action_frequencies.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            return {
                "total_actions": total_actions,
                "unique_patterns": unique_patterns,
                "average_success_rate": round(avg_success_rate, 3),
                "top_actions": top_actions,
                "confidence_threshold": self.confidence_threshold,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get learning stats: {e}")
            return {"error": str(e)}
    
    def _save_learning_data(self):
        """Save learning data to disk"""
        try:
            # Convert patterns to serializable format
            serializable_patterns = {}
            for k, v in self.action_patterns.items():
                pattern_dict = asdict(v)
                # Convert datetime to ISO format
                pattern_dict["last_seen"] = pattern_dict["last_seen"].isoformat()
                serializable_patterns[k] = pattern_dict
            
            data = {
                "action_patterns": serializable_patterns,
                "success_rates": dict(self.success_rates),
                "action_frequencies": dict(self.action_frequencies),
                "last_saved": datetime.now().isoformat()
            }
            
            with open(self.data_dir / "behavior_data.json", "w") as f:
                json.dump(data, f, indent=2)
            
        except Exception as e:
            logger.warning(f"Failed to save learning data: {e}")
    
    def _load_learning_data(self):
        """Load learning data from disk"""
        try:
            data_file = self.data_dir / "behavior_data.json"
            if not data_file.exists():
                return
            
            with open(data_file, "r") as f:
                data = json.load(f)
            
            # Load patterns
            for pattern_id, pattern_data in data.get("action_patterns", {}).items():
                pattern_data["last_seen"] = datetime.fromisoformat(pattern_data["last_seen"])
                self.action_patterns[pattern_id] = ActionPattern(**pattern_data)
            
            # Load success rates and frequencies
            self.success_rates.update(data.get("success_rates", {}))
            self.action_frequencies.update(data.get("action_frequencies", {}))
            
            logger.info(f"Loaded learning data: {len(self.action_patterns)} patterns")
            
        except Exception as e:
            logger.warning(f"Failed to load learning data: {e}")


# Example usage and testing
if __name__ == "__main__":
    learner = BehaviorLearner()
    
    # Simulate some actions
    test_actions = [
        UserAction(
            timestamp=datetime.now(),
            action_type="click",
            target="button",
            parameters={"x": 100, "y": 200},
            success=True,
            context={"app": "browser"},
            duration=0.5
        ),
        UserAction(
            timestamp=datetime.now(),
            action_type="type",
            target="input",
            parameters={"text": "hello"},
            success=True,
            context={"app": "browser"},
            duration=1.0
        )
    ]
    
    # Learn from actions
    for action in test_actions:
        learner.learn_from_action(action)
    
    # Get predictions
    context = {"app_name": "browser"}
    predictions = learner.predict_next_actions(context)
    
    print("Behavior Learning System Test:")
    print("=" * 50)
    print(f"Predictions: {len(predictions)}")
    for pred in predictions:
        print(f"- {pred.action_type}: {pred.reasoning} (confidence: {pred.confidence})")
    
    stats = learner.get_learning_stats()
    print(f"\nLearning Stats: {stats}")
