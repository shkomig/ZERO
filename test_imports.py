"""
Test all critical imports
"""
import sys

def test_import(module_name, package=None):
    try:
        if package:
            exec(f"from {package} import {module_name}")
        else:
            exec(f"import {module_name}")
        print(f"[OK] {package or module_name}.{module_name if package else ''}")
        return True
    except ImportError as e:
        print(f"[FAIL] {package or module_name}.{module_name if package else ''}")
        print(f"   Error: {e}")
        return False
    except Exception as e:
        print(f"[WARN] {package or module_name}.{module_name if package else ''}")
        print(f"   Error: {e}")
        return False

print("Testing Critical Imports:\n")

# Core dependencies
test_import("langgraph")
test_import("langchain")
test_import("langchain_anthropic")
test_import("anthropic")
test_import("ollama")

# Tools
test_import("playwright")
test_import("playwright.async_api", "playwright")
test_import("docker")
test_import("gitpython")

# Data
test_import("chromadb")
test_import("redis")
test_import("sentence_transformers")

# System
test_import("psutil")
test_import("pydantic")
test_import("fastapi")

print("\n" + "="*50)
print("Import Test Complete")
