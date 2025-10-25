"""
Quick test of model router
"""

from zero_agent.models.model_router import router

print("Quick Model Test")
print("="*30)

# Test model selection
selected = router.select_model("understanding task requirements", "medium", "quality")
print(f"Selected model: {selected}")

# Test model invocation
try:
    messages = [{"role": "user", "content": "Say hello in Hebrew"}]
    response = router.invoke_model(selected, messages)
    print(f"Response: {response[:50]}...")
    print("[OK] Model working!")
except Exception as e:
    print(f"[FAIL] Error: {e}")






