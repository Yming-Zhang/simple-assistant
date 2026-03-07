import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_mvp1():
    """测试 MVP1: LLM Provider 抽象基类 + 响应数据模型"""
    print("\n" + "=" * 60)
    print("测试 MVP1: LLM Provider 抽象基类 + 响应数据模型")
    print("=" * 60)
    
    from llm.base import LLMProvider
    from llm.response import ChatResponse, StreamChunk
    
    assert LLMProvider is not None
    assert ChatResponse is not None
    assert StreamChunk is not None
    
    # 测试 ChatResponse
    response = ChatResponse(
        content="你好！",
        reasoning="思考过程",
        tool_calls=[{"name": "test"}],
        raw_response={"test": "data"}
    )
    assert response.content == "你好！"
    assert response.reasoning == "思考过程"
    
    print("✓ MVP1 测试通过！")


def test_mvp2():
    """测试 MVP2: Ollama 适配器"""
    print("\n" + "=" * 60)
    print("测试 MVP2: Ollama 适配器")
    print("=" * 60)
    
    from llm.ollama import OllamaProvider
    
    provider = OllamaProvider(
        base_url="http://localhost:11434",
        model="qwen3.5:4b"
    )
    
    assert provider.model == "qwen3.5:4b"
    assert hasattr(provider, "chat")
    assert hasattr(provider, "embed")
    
    print("✓ MVP2 测试通过！")
    print("  注意：完整功能测试需要 Ollama 服务运行")


def test_mvp3():
    """测试 MVP3: Azure OpenAI 适配器"""
    print("\n" + "=" * 60)
    print("测试 MVP3: Azure OpenAI 适配器")
    print("=" * 60)
    
    from llm.azure_openai import AzureOpenAIProvider
    
    # 只测试导入和初始化（不需要实际凭据）
    assert AzureOpenAIProvider is not None
    print("✓ MVP3 测试通过！")
    print("  注意：完整功能测试需要 Azure OpenAI 凭据")


def test_mvp4():
    """测试 MVP4: Provider 工厂"""
    print("\n" + "=" * 60)
    print("测试 MVP4: Provider 工厂")
    print("=" * 60)
    
    from llm.factory import LLMProviderFactory
    from llm.ollama import OllamaProvider
    
    config = {
        "base_url": "http://localhost:11434",
        "model": "qwen3.5:4b"
    }
    
    provider = LLMProviderFactory.create("ollama", config)
    assert isinstance(provider, OllamaProvider)
    assert provider.model == "qwen3.5:4b"
    
    print("✓ MVP4 测试通过！")


def test_mvp5():
    """测试 MVP5: 配置扩展"""
    print("\n" + "=" * 60)
    print("测试 MVP5: 配置扩展")
    print("=" * 60)
    
    from config import config
    
    assert hasattr(config, "llm")
    assert config.llm.provider == "ollama"
    assert config.llm.ollama_model == "qwen3.5:4b"
    
    provider_config = config.llm.get_provider_config()
    assert "model" in provider_config
    assert provider_config["model"] == "qwen3.5:4b"
    
    print("✓ MVP5 测试通过！")


def test_mvp6():
    """测试 MVP6: Skills 增强系统"""
    print("\n" + "=" * 60)
    print("测试 MVP6: Skills 增强系统")
    print("=" * 60)
    
    from skills.types import SkillMetadata
    from skills.loader import KnowledgeSkill, SkillLoader
    from skills.registry import SkillRegistry
    
    # 测试 SkillMetadata
    metadata = SkillMetadata(
        name="测试",
        description="测试描述",
        is_knowledge=True
    )
    assert metadata.name == "测试"
    assert metadata.is_knowledge is True
    
    # 测试 KnowledgeSkill
    knowledge_skill = KnowledgeSkill(
        name="天气助手",
        description="天气查询",
        prompt="你是天气助手"
    )
    assert knowledge_skill.name == "天气助手"
    assert knowledge_skill.is_knowledge is True
    assert knowledge_skill.execute() == "你是天气助手"
    
    # 测试 SkillRegistry
    registry = SkillRegistry()
    registry.register(knowledge_skill)
    assert registry.get("天气助手") is not None
    
    print("✓ MVP6 测试通过！")


def test_mvp7():
    """测试 MVP7: LLM 匹配引擎"""
    print("\n" + "=" * 60)
    print("测试 MVP7: LLM 匹配引擎")
    print("=" * 60)
    
    from matcher.llm import LLMMatcher
    from skills.registry import SkillRegistry
    
    # 测试导入和基本结构
    assert LLMMatcher is not None
    
    # 创建匹配器（不会实际连接 Ollama）
    registry = SkillRegistry()
    matcher = LLMMatcher(registry)
    
    assert hasattr(matcher, "match")
    assert hasattr(matcher, "get_last_reasoning")
    
    print("✓ MVP7 测试通过！")
    print("  注意：完整功能测试需要 Ollama 服务运行")


if __name__ == "__main__":
    print("=" * 60)
    print("Phase 9 - 所有 MVP 测试")
    print("=" * 60)
    
    try:
        test_mvp1()
        test_mvp2()
        test_mvp3()
        test_mvp4()
        test_mvp5()
        test_mvp6()
        test_mvp7()
        
        print("\n" + "=" * 60)
        print("🎉 Phase 9 所有 MVP 核心功能测试通过！")
        print("=" * 60)
        print("\n下一步：")
        print("1. 确保 Ollama 服务运行")
        print("2. 拉取 qwen3.5:4b 和 nomic-embed-text 模型")
        print("3. 更新 assistant.py 集成 LLMMatcher")
        print("4. 运行完整验收测试")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
