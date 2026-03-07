import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from llm.ollama import OllamaProvider


def test_imports():
    """测试导入是否成功"""
    print("✓ 测试导入...")
    assert OllamaProvider is not None
    print("✓ OllamaProvider 导入成功！")


def test_initialization():
    """测试初始化"""
    print("\n✓ 测试初始化...")
    
    provider = OllamaProvider(
        base_url="http://localhost:11434",
        model="qwen3.5:4b",
        embed_model="nomic-embed-text",
        timeout=120
    )
    
    assert provider.model == "qwen3.5:4b"
    assert provider.embed_model == "nomic-embed-text"
    assert provider.base_url == "http://localhost:11434"
    
    print("✓ 初始化测试通过！")


def test_abstract_methods():
    """测试是否实现了所有抽象方法"""
    print("\n✓ 测试抽象方法实现...")
    
    provider = OllamaProvider()
    
    assert hasattr(provider, "chat")
    assert hasattr(provider, "stream_chat")
    assert hasattr(provider, "embed")
    assert hasattr(provider, "close")
    
    print("✓ 抽象方法实现测试通过！")


if __name__ == "__main__":
    print("=" * 50)
    print("Phase 9 - MVP2 测试")
    print("=" * 50)
    
    test_imports()
    test_initialization()
    test_abstract_methods()
    
    print("\n" + "=" * 50)
    print("✓ MVP2 所有测试通过！")
    print("=" * 50)
    print("\n注意：完整功能测试需要 Ollama 服务运行")
