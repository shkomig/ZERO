"""
Quick fix for memory import
Run this in C:\AI-ALL-PRO\ZERO
"""

import sys
from pathlib import Path

# Check if memory folder exists
memory_dir = Path("memory")

if memory_dir.exists():
    print("✓ memory/ folder found")
    
    # Check files
    required_files = [
        "__init__.py",
        "short_term_memory.py", 
        "rag_connector.py",
        "memory_manager.py"
    ]
    
    for file in required_files:
        filepath = memory_dir / file
        if filepath.exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} MISSING!")
    
    # Try importing
    print("\nTrying to import...")
    try:
        sys.path.insert(0, str(Path.cwd()))
        from memory import MemoryManager
        print("✓ Import successful!")
    except Exception as e:
        print(f"✗ Import failed: {e}")
        
else:
    print("✗ memory/ folder NOT FOUND")
    print("\nPlease create it:")
    print("  mkdir memory")
