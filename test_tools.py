"""
Test Tools functionality
"""

import asyncio
from zero_agent.core.tool_executor import ToolExecutor

async def test_tools():
    """Test tools functionality"""
    
    print("Testing Tools...")
    print("="*50)
    
    # Initialize tool executor
    try:
        executor = ToolExecutor()
        print("[OK] ToolExecutor initialized")
    except Exception as e:
        print(f"[FAIL] ToolExecutor failed: {e}")
        return
    
    # Test 1: List available tools
    print("\n1. Available tools:")
    tools = executor.list_tools()
    for tool in tools:
        print(f"   - {tool}")
    
    # Test 2: Test system monitoring tools
    print("\n2. Testing system monitoring tools:")
    
    system_tools = [
        ("cpu_usage", {}),
        ("memory_usage", {}),
        ("disk_usage", {}),
        ("system_info", {}),
    ]
    
    for tool_name, params in system_tools:
        try:
            result = await executor.execute(tool_name, **params)
            print(f"   [OK] {tool_name}: {str(result)[:50]}...")
        except Exception as e:
            print(f"   [FAIL] {tool_name}: {e}")
    
    # Test 3: Test screenshot tool
    print("\n3. Testing screenshot tool:")
    try:
        result = await executor.execute("screenshot")
        print(f"   [OK] Screenshot: {str(result)[:50]}...")
    except Exception as e:
        print(f"   [FAIL] Screenshot: {e}")
    
    print("\n" + "="*50)
    print("Tools test complete!")

if __name__ == "__main__":
    asyncio.run(test_tools())







