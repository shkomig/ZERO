"""
Test Agent System
=================
Tests for Agent Orchestrator and Safety Layer
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from zero_agent.agent_orchestrator import AgentOrchestrator, Task, ExecutionResult
from zero_agent.safety_layer import SafetyLayer, Action
from streaming_llm import StreamingMultiModelLLM


def test_safety_layer():
    """Test Safety Layer validation"""
    print("\n=== Testing Safety Layer ===")
    
    safety = SafetyLayer()
    
    # Test safe action
    safe_action = Action(
        type='read_file',
        parameters={'path': './test.txt'},
        source='user'
    )
    
    is_valid, message = safety.validate(safe_action)
    print(f"Safe action validation: {is_valid} - {message}")
    assert is_valid, "Safe action should be valid"
    
    # Test dangerous action
    dangerous_action = Action(
        type='delete_file',
        parameters={'path': './test.txt'},
        source='user'
    )
    
    is_valid, message = safety.validate(dangerous_action)
    print(f"Dangerous action validation: {is_valid} - {message}")
    assert not is_valid, "Dangerous action should require confirmation"
    
    # Test restricted path
    restricted_action = Action(
        type='read_file',
        parameters={'path': 'C:/Windows/test.txt'},
        source='user'
    )
    
    is_valid, message = safety.validate(restricted_action)
    print(f"Restricted path validation: {is_valid} - {message}")
    assert not is_valid, "Restricted path should be blocked"
    
    print("OK: Safety Layer tests passed!")


def test_agent_orchestrator():
    """Test Agent Orchestrator basic functionality"""
    print("\n=== Testing Agent Orchestrator ===")
    
    # Mock LLM
    llm = StreamingMultiModelLLM(default_model="fast")
    
    # Mock tools
    tools = {}
    
    # Create orchestrator
    orchestrator = AgentOrchestrator(llm=llm, tools=tools)
    
    # Test status
    status = orchestrator.get_status()
    print(f"Initial status: {status}")
    assert status['total_tasks'] == 0, "Should start with no tasks"
    
    print("OK: Agent Orchestrator basic tests passed!")


def test_task_execution():
    """Test task execution flow"""
    print("\n=== Testing Task Execution ===")
    
    # Mock LLM
    llm = StreamingMultiModelLLM(default_model="fast")
    
    # Mock tools
    tools = {}
    
    # Create orchestrator
    orchestrator = AgentOrchestrator(llm=llm, tools=tools)
    
    # Test goal execution
    goal = "חפש ברשת מידע על Python"
    result = orchestrator.execute_goal(goal, max_iterations=3)
    
    print(f"Goal: {goal}")
    print(f"Result success: {result.success}")
    print(f"Result output: {result.output}")
    
    status = orchestrator.get_status()
    print(f"Final status: {status}")
    
    assert isinstance(result, ExecutionResult), "Should return ExecutionResult"
    
    print("OK: Task execution tests passed!")


def main():
    """Run all tests"""
    print("\nStarting Agent System Tests...\n")
    
    try:
        test_safety_layer()
        test_agent_orchestrator()
        test_task_execution()
        
        print("\n" + "="*50)
        print("OK: All tests passed!")
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"\nERROR: Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
