"""
Basic tests for Zero Agent
"""

import pytest
from zero_agent.core.config import config, ConfigManager
from zero_agent.models.model_router import ModelRouter
from zero_agent.tools.system_monitor import SystemMonitor


def test_config_loads():
    """Test that configuration loads properly"""
    assert config is not None
    assert config.settings is not None
    assert config.settings.ollama_host is not None


def test_config_manager():
    """Test ConfigManager functionality"""
    cfg = ConfigManager()
    assert cfg.models_config is not None
    assert cfg.tools_config is not None
    
    # Test model config retrieval
    routing_rules = cfg.get_routing_rules()
    assert routing_rules is not None
    
    # Test tool config
    perms = cfg.get_permissions()
    assert isinstance(perms, dict)


def test_model_router_init():
    """Test that ModelRouter initializes"""
    router = ModelRouter()
    assert router is not None
    assert len(router.models) > 0
    
    # Test model listing
    models = router.list_available_models()
    assert isinstance(models, list)
    assert len(models) > 0


def test_model_selection():
    """Test model selection logic"""
    router = ModelRouter()
    
    # Test different task types
    model = router.select_model("coding task", complexity="high")
    assert model is not None
    
    model = router.select_model("quick question", complexity="low", priority="speed")
    assert model is not None


def test_system_monitor():
    """Test system monitoring tools"""
    # CPU
    cpu = SystemMonitor.get_cpu_usage(interval=0.1)
    assert cpu["success"] is True
    assert "overall" in cpu
    assert cpu["overall"] >= 0
    
    # Memory
    mem = SystemMonitor.get_memory_usage()
    assert mem["success"] is True
    assert "ram" in mem
    assert mem["ram"]["percent"] >= 0
    
    # System info
    info = SystemMonitor.get_system_info()
    assert info["success"] is True
    assert "platform" in info


def test_directories_exist():
    """Test that required directories are created"""
    import os
    from pathlib import Path
    
    base_dir = Path("zero_agent")
    assert base_dir.exists()
    
    # Check main directories
    assert (base_dir / "core").exists()
    assert (base_dir / "models").exists()
    assert (base_dir / "tools").exists()
    assert (base_dir / "rag").exists()
    assert (base_dir / "ui").exists()
    assert (base_dir / "config").exists()
    
    # Check data directories
    assert (base_dir / "data").exists()
    assert (base_dir / "logs").exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

