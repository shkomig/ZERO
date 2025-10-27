"""
Debug model selection
"""

from zero_agent.models.model_router import router
from zero_agent.core.config import config

print("Debug Model Selection")
print("="*50)

# Check what models are available
print("Available models:")
for model_name in router.list_available_models():
    info = router.get_model_info(model_name)
    print(f"  - {model_name}: {info.provider} (speed: {info.speed}, quality: {info.quality})")

print(f"\nDefault model: {config.settings.default_model}")
print(f"Fallback model: {config.settings.fallback_model}")

# Test model selection
print("\nModel selection tests:")
test_cases = [
    ("understanding task requirements", "medium", "quality"),
    ("planning", "high", "quality"),
]

for task, complexity, priority in test_cases:
    selected = router.select_model(task, complexity, priority)
    print(f"  {task} -> {selected}")

# Test actual model invocation
print("\nTesting model invocation:")
try:
    messages = [{"role": "user", "content": "Say hello"}]
    response = router.invoke_model("llama-3.1-8b", messages)
    print(f"  Response: {response[:50]}...")
except Exception as e:
    print(f"  Error: {e}")











