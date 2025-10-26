#!/usr/bin/env python3
"""Check if Agent Orchestrator is actually loaded"""
import sys
sys.path.insert(0, '.')

from api_server import zero, AGENT_ORCHESTRATOR_AVAILABLE

print("=" * 70)
print("Agent Orchestrator Status Check")
print("=" * 70)
print(f"AGENT_ORCHESTRATOR_AVAILABLE: {AGENT_ORCHESTRATOR_AVAILABLE}")
print(f"zero.agent_orchestrator is not None: {zero.agent_orchestrator is not None}")
if zero.agent_orchestrator:
    print(f"Agent Orchestrator type: {type(zero.agent_orchestrator)}")
    print(f"Agent Orchestrator tools: {list(zero.agent_orchestrator.tools.keys()) if hasattr(zero.agent_orchestrator, 'tools') else 'N/A'}")
else:
    print("❌ Agent Orchestrator is NOT loaded!")
print("=" * 70)

