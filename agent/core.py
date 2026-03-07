import asyncio
import json
from typing import List, Dict, Any, Optional, AsyncIterator
from dataclasses import dataclass
from enum import Enum

from skills.registry import SkillRegistry
from agent.prompt import PromptManager
from agent.tools import ToolConverter
from memory.conversation import ConversationManager

# LLM 导入是可选的，用于运行时
try:
    from llm.base import LLMProvider
    from llm.response import ChatResponse, StreamChunk
except ImportError:
    LLMProvider = None
    ChatResponse = None
    StreamChunk = None

class AgentEventType(Enum):
    """Agent 事件类型"""
    THINKING = "thinking"
    TOOL_START = "tool_start"
    TOOL_RESULT = "tool_result"
    REPLY = "reply"
    ERROR = "error"

@dataclass
class AgentEvent:
    """Agent 事件"""
    type: AgentEventType
    data: Any
    reasoning: Optional[str] = None

class AgentCore:
    """Agent Loop 主循环"""
    
    def __init__(self, 
                 llm: LLMProvider,
                 registry: SkillRegistry,
                 conversation: Optional[ConversationManager] = None,
                 prompt_template: str = "default",
                 max_iterations: int = 10):
        self.llm = llm
        self.registry = registry
        self.conversation = conversation
        self.prompt_manager = PromptManager()
        self.prompt_template = prompt_template
        self.max_iterations = max_iterations
    
    async def run(self, 
                  user_input: str,
                  images: Optional[List[str]] = None) -> AsyncIterator[AgentEvent]:
        """
        Agent Loop 主循环
        
        流程：
        1. 构建消息（包含记忆、工具描述）
        2. LLM 推理
        3. 如果是 tool_call → 执行工具 → 结果回传 → 继续循环
        4. 如果是文本回复 → 返回最终结果
        5. 保存到记忆
        """
        
        # 1. 构建初始消息
        messages = self._build_initial_messages(user_input, images)
        tools = ToolConverter.registry_to_functions(self.registry)
        
        # 2. Agent Loop
        for i in range(self.max_iterations):
            yield AgentEvent(
                type=AgentEventType.THINKING,
                data=f"第 {i+1} 次思考中..."
            )
            
            try:
                # 3. LLM 调用
                response: ChatResponse = await self.llm.chat(
                    messages,
                    tools=tools if tools else None,
                    include_reasoning=True
                )
                
                # 发送 reasoning（如果有）
                if response.reasoning:
                    yield AgentEvent(
                        type=AgentEventType.THINKING,
                        data=response.reasoning,
                        reasoning=response.reasoning
                    )
                
                # 4. 检查是否有工具调用
                if response.tool_calls:
                    for tool_call in response.tool_calls:
                        # 解析工具调用
                        tool_name, tool_params = ToolConverter.parse_tool_call(tool_call)
                        
                        yield AgentEvent(
                            type=AgentEventType.TOOL_START,
                            data={
                                "name": tool_name,
                                "params": tool_params
                            }
                        )
                        
                        # 执行工具
                        skill = self.registry.get(tool_name)
                        if skill:
                            tool_result = skill.execute(tool_params)
                        else:
                            tool_result = f"未找到工具: {tool_name}"
                        
                        yield AgentEvent(
                            type=AgentEventType.TOOL_RESULT,
                            data=tool_result
                        )
                        
                        # 将工具结果添加到消息
                        messages.append({
                            "role": "assistant",
                            "content": response.content or "",
                            "tool_calls": [tool_call]
                        })
                        messages.append({
                            "role": "tool",
                            "content": str(tool_result),
                            "tool_call_id": tool_call.get("id", "")
                        })
                    
                    # 继续循环
                    continue
                
                # 5. 文本回复，结束循环
                yield AgentEvent(
                    type=AgentEventType.REPLY,
                    data=response.content
                )
                
                # 保存到记忆
                if self.conversation:
                    self.conversation.add_conversation(
                        user_input,
                        response.content
                    )
                
                return
                
            except Exception as e:
                yield AgentEvent(
                    type=AgentEventType.ERROR,
                    data=str(e)
                )
                return
        
        # 超过最大迭代次数
        yield AgentEvent(
            type=AgentEventType.ERROR,
            data=f"超过最大迭代次数 {self.max_iterations}"
        )
    
    def _build_initial_messages(self, user_input: str, 
                                images: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """构建初始消息"""
        messages = []
        
        # System prompt
        system_prompt = self.prompt_manager.get_template(self.prompt_template)
        
        # 如果有对话管理器，注入记忆
        if self.conversation and self.prompt_template == "with_memory":
            memory_context = self.conversation.get_memory_context()
            system_prompt = self.prompt_manager.render(
                "with_memory",
                memory_context=memory_context
            )
        
        messages.append({
            "role": "system",
            "content": system_prompt
        })
        
        # 添加滑动窗口历史
        if self.conversation:
            for msg in self.conversation.get_sliding_window():
                messages.append(msg)
        
        # 添加当前用户输入
        user_message = {"role": "user", "content": user_input}
        
        # 如果有图片，添加到消息（简化实现）
        if images:
            user_message["images"] = images
        
        messages.append(user_message)
        
        return messages
