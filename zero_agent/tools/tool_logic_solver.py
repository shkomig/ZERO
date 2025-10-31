"""
Logic Solver Tool for Zero Agent
Helps with logical reasoning and pattern recognition
"""

from typing import Dict, Any, List, Optional
import re


class LogicSolverTool:
    """Tool for solving logical and pattern-based problems"""
    
    def __init__(self):
        self.name = "logic_solver"
        self.description = "Solves logical reasoning problems, identifies patterns, and helps with mathematical logic"
    
    def solve_pattern(self, sequence: List[Any]) -> Dict[str, Any]:
        """
        Identify pattern in a sequence and predict next value
        
        Args:
            sequence: List of numbers or values
            
        Returns:
            Dictionary with pattern type, rule, and prediction
        """
        try:
            if not sequence or len(sequence) < 2:
                return {"error": "Sequence too short to identify pattern"}
            
            # Try arithmetic progression
            if len(sequence) >= 3:
                diff1 = sequence[1] - sequence[0]
                diff2 = sequence[2] - sequence[1]
                if diff1 == diff2:
                    next_val = sequence[-1] + diff1
                    return {
                        "pattern_type": "arithmetic",
                        "rule": f"Add {diff1}",
                        "next_value": next_val,
                        "confidence": 0.9
                    }
            
            # Try geometric progression
            if len(sequence) >= 3 and all(x != 0 for x in sequence):
                ratio1 = sequence[1] / sequence[0]
                ratio2 = sequence[2] / sequence[1]
                if abs(ratio1 - ratio2) < 0.001:  # Floating point tolerance
                    next_val = sequence[-1] * ratio1
                    return {
                        "pattern_type": "geometric",
                        "rule": f"Multiply by {ratio1}",
                        "next_value": int(next_val) if next_val.is_integer() else next_val,
                        "confidence": 0.9
                    }
            
            # Try doubling pattern (common: 2, 4, 8, 16, ...)
            if len(sequence) >= 2:
                if all(sequence[i+1] == sequence[i] * 2 for i in range(len(sequence)-1)):
                    next_val = sequence[-1] * 2
                    return {
                        "pattern_type": "doubling",
                        "rule": "Multiply by 2",
                        "next_value": next_val,
                        "confidence": 0.95
                    }
            
            # Try Fibonacci-like patterns
            if len(sequence) >= 4:
                if all(sequence[i+2] == sequence[i] + sequence[i+1] for i in range(len(sequence)-2)):
                    next_val = sequence[-1] + sequence[-2]
                    return {
                        "pattern_type": "fibonacci",
                        "rule": "Add previous two numbers",
                        "next_value": next_val,
                        "confidence": 0.85
                    }
            
            return {"error": "Could not identify clear pattern"}
            
        except Exception as e:
            return {"error": f"Error analyzing pattern: {str(e)}"}
    
    def solve_logic_implication(self, premises: List[str]) -> Dict[str, Any]:
        """
        Solve logical implication problems
        
        Args:
            premises: List of logical statements like ["A implies B", "B implies C"]
            
        Returns:
            Dictionary with conclusion
        """
        try:
            # Extract implications
            implications = []
            for premise in premises:
                if "implies" in premise.lower() or "→" in premise or "->" in premise:
                    # Extract A and B from "A implies B"
                    parts = re.split(r'[→->]|implies', premise, flags=re.IGNORECASE)
                    if len(parts) >= 2:
                        a = parts[0].strip()
                        b = parts[1].strip()
                        implications.append((a, b))
            
            if not implications:
                return {"error": "No valid implications found"}
            
            # Build chain
            chain = [implications[0]]
            for imp in implications[1:]:
                # Check if it continues the chain
                if chain[-1][1] == imp[0]:
                    chain.append(imp)
            
            # Final conclusion
            if len(chain) >= 2:
                first = chain[0][0]
                last = chain[-1][1]
                return {
                    "conclusion": f"{first} implies {last}",
                    "reasoning": "Transitive property of implication",
                    "confidence": 0.9
                }
            
            return {"error": "Could not build implication chain"}
            
        except Exception as e:
            return {"error": f"Error solving logic: {str(e)}"}
    
    def solve_word_problem(self, problem: str) -> Dict[str, Any]:
        """
        Solve word problems with logic
        
        Args:
            problem: Natural language problem description
            
        Returns:
            Dictionary with answer and reasoning
        """
        try:
            problem_lower = problem.lower()
            
            # "All but X" pattern
            if "all but" in problem_lower:
                numbers = re.findall(r'\d+', problem)
                if len(numbers) >= 2:
                    total = int(numbers[0])
                    all_but = int(numbers[1])
                    remaining = all_but  # "all but X" means X remain
                    return {
                        "answer": remaining,
                        "reasoning": f"'All but {all_but}' means {all_but} remain out of {total}",
                        "confidence": 0.9
                    }
            
            # Machine/rate problems
            if "machine" in problem_lower and "minutes" in problem_lower:
                numbers = re.findall(r'\d+', problem)
                if len(numbers) >= 4:
                    machines1 = int(numbers[0])
                    widgets1 = int(numbers[1])
                    time1 = int(numbers[2])
                    machines2 = int(numbers[3])
                    widgets2 = int(numbers[4]) if len(numbers) > 4 else widgets1
                    
                    # Each machine takes same time per widget
                    time_per_widget = time1 / widgets1  # Time per widget per machine
                    time2 = time_per_widget * widgets2
                    
                    return {
                        "answer": time2,
                        "reasoning": f"Each machine takes {time1} minutes for {widgets1} widgets. So {machines2} machines take same time ({time2} minutes) for {widgets2} widgets.",
                        "confidence": 0.85
                    }
            
            return {"error": "Could not parse word problem"}
            
        except Exception as e:
            return {"error": f"Error solving word problem: {str(e)}"}
    
    def __call__(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Main entry point for logic solver
        
        Args:
            task: The task description
            context: Optional context
            
        Returns:
            Solution dictionary
        """
        try:
            # Detect task type
            task_lower = task.lower()
            
            # Pattern detection
            if "pattern" in task_lower or "sequence" in task_lower or "דפוס" in task_lower:
                # Extract numbers from task
                numbers = [int(x) for x in re.findall(r'\d+', task)]
                if len(numbers) >= 2:
                    return self.solve_pattern(numbers)
            
            # Logic implication
            if "implies" in task_lower or "→" in task or "->" in task:
                # Extract premises
                sentences = task.split('.')
                return self.solve_logic_implication(sentences)
            
            # Word problems
            if any(kw in task_lower for kw in ["how many", "כמה", "remain", "נשאר", "machine", "מכונה"]):
                return self.solve_word_problem(task)
            
            return {"error": "Could not determine problem type"}
            
        except Exception as e:
            return {"error": f"Error in logic solver: {str(e)}"}


# Example usage
if __name__ == "__main__":
    solver = LogicSolverTool()
    
    # Test pattern
    result = solver.solve_pattern([2, 4, 8, 16])
    print(f"Pattern result: {result}")
    
    # Test logic
    result = solver.solve_logic_implication(["A implies B", "B implies C"])
    print(f"Logic result: {result}")
    
    # Test word problem
    result = solver.solve_word_problem("A farmer has 17 sheep, all but 9 run away. How many remain?")
    print(f"Word problem result: {result}")

