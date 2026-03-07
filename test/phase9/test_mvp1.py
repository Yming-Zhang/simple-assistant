import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from llm.base import LLMProvider
from llm.response import ChatResponse, StreamChunk


def test_imports():
    """测试导入是否成功"""
    print("✓ 测试导入...")
    
    assert LLMProvider is not None
    assert ChatResponse is not None
    assert StreamChunk is not None
    
    print("✓ 所有导入成功！")


def test_chat_response():
    """测试 ChatResponse 数据模型"""
    print("\n✓ 测试 ChatResponse...")
    
    response = ChatResponse(
        content="你好！",
        reasoning="我需要先理解用户的问题",
        tool_calls=[{"name": "test_tool"}],
        raw_response={"test": "data"}
    )
    
    assert response.content == "你好！"
    assert response.reasoning == "我需要先理解用户的问题"
    assert response.tool_calls == [{"name": "test_tool"}]
    assert response.raw_response == {"test": "data"}
    
    print("✓ ChatResponse 测试通过！")


def test_stream_chunk():
    """测试 StreamChunk 数据模型"""
    print("\n✓ 测试 StreamChunk...")
    
    chunk = StreamChunk(
        content="你",
        reasoning="思考中...",
        is_finished=False
    )
    
    assert chunk.content == "你"
    assert chunk.reasoning == "思考中..."
    assert chunk.is_finished is False
    
    finish_chunk = StreamChunk(is_finished=True)
    assert finish_chunk.is_finished is True
    
    print("✓ StreamChunk 测试通过！")


if __name__ == "__main__":
    print("=" * 50)
    print("Phase 9 - MVP1 测试")
    print("=" * 50)
    
    test_imports()
    test_chat_response()
    test_stream_chunk()
    
    print("\n" + "=" * 50)
    print("✓ MVP1 所有测试通过！")
    print("=" * 50)
