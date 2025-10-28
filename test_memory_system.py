"""
Test Memory System - בדיקת מערכת הזיכרון
"""

import sys
from pathlib import Path

print("="*70)
print("Zero Memory System - System Check")
print("="*70)

# Test 1: Short-Term Memory
print("\n[1] Testing Short-Term Memory...")
try:
    from memory.short_term_memory import ShortTermMemory
    
    memory = ShortTermMemory(memory_dir=Path("workspace/memory"))
    
    # Check if conversations exist
    stats = memory.get_statistics()
    print(f"   [OK] Short-Term Memory loaded")
    print(f"   [DATA] Total conversations: {stats['total_conversations']}")
    print(f"   [DATA] Last 24h: {stats['conversations_24h']}")
    print(f"   [DATA] Preferences: {stats['total_preferences']}")
    print(f"   [DATA] Facts: {stats['total_facts']}")
    
    # Test encoding
    print("\n   [TEST] Testing UTF-8 encoding...")
    test_conv = memory.add_conversation(
        user_message="בדיקת עברית - שלום עולם",
        assistant_message="תשובה בעברית - היי!",
        model_used="test",
        topic="encoding_test"
    )
    
    # Reload and check
    last_conv = memory.conversations[-1]
    if "שלום" in last_conv['user_message']:
        print("   [OK] UTF-8 encoding works correctly!")
    else:
        print("   [FAIL] UTF-8 encoding BROKEN:", last_conv['user_message'])
    
except Exception as e:
    print(f"   [FAIL] Short-Term Memory failed: {e}")
    import traceback
    traceback.print_exc()

# Test 2: RAG System
print("\n[2] Testing RAG System...")
try:
    from zero_agent.rag.memory import RAGMemorySystem
    
    rag = RAGMemorySystem()
    print("   [OK] RAG System initialized")
    
    # Try to store
    rag.store_conversation(
        task="בדיקת RAG",
        response="RAG עובד!",
        metadata={"test": True}
    )
    print("   [OK] RAG can store conversations")
    
    # Try to retrieve
    results = rag.retrieve("בדיקה", n_results=1)
    print(f"   [OK] RAG can retrieve: {len(results)} results")
    
except Exception as e:
    print(f"   [FAIL] RAG System failed: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Memory Manager
print("\n[3] Testing Memory Manager...")
try:
    from memory.memory_manager import MemoryManager
    
    manager = MemoryManager(
        memory_dir=Path("workspace/memory"),
        enable_rag=False  # Disable RAG for now
    )
    print("   [OK] Memory Manager initialized")
    
    # Test remember
    entry = manager.remember(
        user_message="בדיקת Memory Manager",
        assistant_message="עובד מצוין!",
        model_used="test"
    )
    print("   [OK] Memory Manager can remember")
    
    # Test recall
    results = manager.recall("בדיקה", hours=1, use_rag=False)
    print(f"   [OK] Memory Manager can recall")
    print(f"      - Recent conversations: {len(results['recent_conversations'])}")
    print(f"      - Preferences: {len(results['preferences'])}")
    
except Exception as e:
    print(f"   [FAIL] Memory Manager failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Check API Integration
print("\n[4] Testing API Integration...")
try:
    import api_server
    
    # Check if ZeroAgent has memory
    zero = api_server.ZeroAgent()
    zero.initialize()
    
    if hasattr(zero, 'memory') and zero.memory:
        print("   [OK] API has Memory Manager")
    else:
        print("   [WARN] API Memory Manager not initialized")
    
except Exception as e:
    print(f"   [FAIL] API Integration check failed: {e}")

print("\n" + "="*70)
print("Memory System Check Complete!")
print("="*70)

# Summary
print("\n[SUMMARY]:")
print("   [OK] = Working")
print("   [WARN] = Needs attention")
print("   [FAIL] = Not working")
print("\nCheck details above for issues.")
print("\n" + "="*70)

