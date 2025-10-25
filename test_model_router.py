"""
Test Model Router functionality
"""

import asyncio
from zero_agent.models.model_router import router
from zero_agent.core.config import config

async def test_model_router():
    """Test model router functionality"""
    
    print("Testing Model Router...")
    print("="*50)
    
    # Test 1: List available models
    print("\n1. Available models:")
    models = router.list_available_models()
    for model in models:
        info = router.get_model_info(model)
        print(f"   - {model}: {info.provider} (speed: {info.speed}, quality: {info.quality})")
    
    # Test 2: Model selection
    print("\n2. Model selection tests:")
    
    test_cases = [
        ("planning", "high", "quality"),
        ("coding", "medium", "speed"),
        ("quick_response", "low", "cost"),
        ("reasoning", "high", "quality"),
    ]
    
    for task, complexity, priority in test_cases:
        selected = router.select_model(task, complexity, priority)
        print(f"   {task} ({complexity}, {priority}) -> {selected}")
    
    # Test 3: Model invocation
    print("\n3. Model invocation test:")
    
    try:
        messages = [
            {"role": "user", "content": "Say 'Hello from Zero Agent' in Hebrew"}
        ]
        
        # Try to invoke a model
        response = router.invoke_model("llama-3.1-8b", messages)
        print(f"   Response: {response[:100]}...")
        print("   [OK] Model invocation successful!")
        
    except Exception as e:
        print(f"   [FAIL] Model invocation failed: {e}")
    
    print("\n" + "="*50)
    print("Model Router test complete!")

if __name__ == "__main__":
    asyncio.run(test_model_router())






