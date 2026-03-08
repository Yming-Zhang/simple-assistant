#!/usr/bin/env python3
"""
电脑助手主程序
整合所有组件：唤醒系统、音频处理、STT、TTS、Skill 系统、LLM 系统
"""

import time
import logging
import asyncio
from typing import Optional, Dict, Any
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 导入核心组件
from audio.microphone import record_audio
from audio.player import play_audio
from audio.stt import transcribe
from audio.tts import speak
from wake.wake_system import get_wake_system
from skills.registry import get_registry
from matcher.llm import LLMMatcher
from skills.loader import SkillLoader
from llm.base import LLMProvider
from llm.response import ChatResponse
from llm.factory import LLMProviderFactory
from config import config

# 记忆系统
from memory.store import MemoryStore
from memory.db import MemoryDB
from memory.conversation import ConversationManager

# 导入内置 Skills
from skills.builtin.screen import ScreenSkill
from skills.builtin.camera import CameraSkill
from skills.builtin.system_cmd import SystemCmdSkill
from skills.builtin.notification import NotificationSkill
from skills.builtin.memory import MemorySearchSkill, MemoryGetSkill
from skills.builtin.terminal import TerminalSkill
from skills.builtin.browser import BrowserSkill
from skills.builtin.app_control import AppControlSkill
from skills.builtin.feishu import FeishuSkill


class Assistant:
    """
    电脑助手主类
    整合所有功能模块
    """
    
    def __init__(self):
        logger.info("初始化电脑助手...")
        
        # 创建全局事件循环
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        # 初始化 Skill 注册中心
        self.registry = get_registry()
        
        # 加载 Skills（从目录动态加载）
        self.skill_loader = SkillLoader(self.registry)
        
        # 初始化记忆系统
        self.memory_store = MemoryStore(config.memory.data_dir)
        self.memory_db = MemoryDB(str(Path(config.memory.data_dir) / "memory.db"))
        self.conversation_manager = ConversationManager(
            self.memory_store,
            self.memory_db,
            max_sliding_window=config.memory.max_sliding_window
        )
        logger.info("记忆系统初始化成功")
        
        # 注册内置 Skills
        self._register_builtin_skills()
        
        # 从 knowledge 目录加载 Knowledge Skills
        knowledge_dir = Path(__file__).parent / "skills" / "knowledge"
        if knowledge_dir.exists():
            loaded_count = self.skill_loader.load_from_directory(str(knowledge_dir))
            logger.info(f"从 knowledge 目录加载了 {loaded_count} 个 Skills")
        
        # 初始化 LLM 匹配器（优先），传入全局事件循环
        self.matcher = LLMMatcher(self.registry, self.loop)
        
        # 初始化独立的 LLM Provider 用于纯对话
        try:
            self.llm_provider: Optional[LLMProvider] = LLMProviderFactory.create(
                config.llm.provider,
                config.llm.get_provider_config()
            )
            logger.info("LLM Provider 初始化成功")
        except Exception as e:
            logger.warning(f"LLM Provider 初始化失败: {e}")
            self.llm_provider = None
        
        # 初始化唤醒系统
        self.wake_system = get_wake_system()
        
        logger.info("电脑助手初始化完成！")
    
    def _register_builtin_skills(self):
        """注册内置 Skills"""
        skills = [
            ScreenSkill(),
            CameraSkill(),
            SystemCmdSkill(),
            NotificationSkill(),
            MemorySearchSkill(self.conversation_manager),
            MemoryGetSkill(self.conversation_manager),
            TerminalSkill(),
            BrowserSkill(),
            AppControlSkill(),
            FeishuSkill(),
        ]
        
        for skill in skills:
            self.registry.register(skill)
            logger.info(f"注册内置 Skill: {skill.name}")
    
    def _call_llm_directly(self, text: str) -> Optional[dict]:
        """
        直接调用 LLM 进行纯对话（同步）
        
        Args:
            text: 用户输入
            
        Returns:
            包含 content 和 reasoning 的字典
        """
        if not self.llm_provider:
            return None
        
        try:
            logger.info("直接调用 LLM 进行对话...")
            messages = [
                {"role": "system", "content": "你是一个友好的电脑助手，用简洁的中文回答用户的问题。"},
                {"role": "user", "content": text}
            ]
            
            response: ChatResponse = self.loop.run_until_complete(
                self.llm_provider.chat(messages, include_reasoning=True)
            )
            
            if response.reasoning:
                logger.info(f"LLM 推理: {response.reasoning}")
            
            return {
                "content": response.content,
                "reasoning": response.reasoning
            }
            
        except Exception as e:
            logger.error(f"LLM 调用失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    async def _stream_process(self, text: str, on_chunk):
        """
        完整的流式处理流程：先匹配工具 → 执行工具 → 没匹配到才 LLM 对话
        
        Args:
            text: 用户输入
            on_chunk: 回调函数，接收 (type, content)，type 可以是 'reasoning', 'content', 'tool_start', 'tool_result'
        """
        try:
            logger.info(f"处理用户输入: {text}")
            
            # 添加用户消息到记忆
            self.conversation_manager.add_message("user", text)
            
            # 1. 使用 LLM 匹配器匹配 Skill（流式）
            logger.info("正在使用 LLM 匹配...")
            
            # 定义匹配阶段的回调
            async def match_on_chunk(chunk_type, content):
                if chunk_type == "reasoning":
                    await on_chunk("reasoning", f"任务分析: {content}")
            
            skill, params = await self.matcher.stream_match(text, match_on_chunk)
            
            # 2. 如果匹配到 Skill，执行 Skill
            if skill:
                logger.info(f"匹配到 Skill: {skill.name}")
                
                # 推送工具开始事件
                await on_chunk("tool_start", {
                    "name": skill.name,
                    "args": params
                })
                
                # 执行 Skill（在单独线程中）
                def execute_sync():
                    return skill.execute(params)
                
                result = await asyncio.to_thread(execute_sync)
                logger.info(f"执行结果: {result}")
                
                # 推送工具结果
                await on_chunk("tool_result", str(result))
                
                # 推送最终内容
                await on_chunk("content", str(result))
                
                # 添加助手回复到记忆
                self.conversation_manager.add_message("assistant", str(result))
                
                return
            
            # 3. 没有匹配到 Skill，使用 LLM 纯对话
            logger.warning(f"未匹配到任何 Skill，使用 LLM 对话")
            
            if not self.llm_provider:
                await on_chunk("content", "抱歉，我还不支持这个功能")
                self.conversation_manager.add_message("assistant", "抱歉，我还不支持这个功能")
                return
            
            # 流式调用 LLM
            messages = [
                {"role": "system", "content": "你是一个友好的电脑助手，用简洁的中文回答用户的问题。"},
                {"role": "user", "content": text}
            ]
            
            full_reasoning = ""
            full_content = ""
            
            async for chunk in self.llm_provider.stream_chat(messages, include_reasoning=True):
                if chunk.reasoning:
                    full_reasoning += chunk.reasoning
                    await on_chunk("reasoning", f"LLM思考: {full_reasoning}")
                
                if chunk.content:
                    full_content += chunk.content
                    await on_chunk("content", full_content)
                
                if chunk.is_finished:
                    break
            
            if full_reasoning:
                logger.info(f"LLM 推理: {full_reasoning}")
            
            # 添加助手回复到记忆
            self.conversation_manager.add_message("assistant", full_content)
            
        except Exception as e:
            logger.error(f"处理失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            await on_chunk("content", f"处理出错: {e}")
    
    async def _stream_llm_directly(self, text: str, on_chunk):
        """
        流式调用 LLM 进行纯对话（保留兼容性）
        
        Args:
            text: 用户输入
            on_chunk: 回调函数，接收 (type, content)，type 可以是 'reasoning' 或 'content'
        """
        if not self.llm_provider:
            return
        
        try:
            logger.info("流式调用 LLM 进行对话...")
            messages = [
                {"role": "system", "content": "你是一个友好的电脑助手，用简洁的中文回答用户的问题。"},
                {"role": "user", "content": text}
            ]
            
            full_reasoning = ""
            full_content = ""
            
            async for chunk in self.llm_provider.stream_chat(messages, include_reasoning=True):
                if chunk.reasoning:
                    full_reasoning += chunk.reasoning
                    await on_chunk("reasoning", full_reasoning)
                
                if chunk.content:
                    full_content += chunk.content
                    await on_chunk("content", full_content)
                
                if chunk.is_finished:
                    break
            
            if full_reasoning:
                logger.info(f"LLM 推理: {full_reasoning}")
            
        except Exception as e:
            logger.error(f"流式 LLM 调用失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    def handle_wakeup(self):
        """
        处理唤醒事件
        完整流程：唤醒 → 录音 → STT → 匹配 → 执行 → TTS
        """
        logger.info("开始处理唤醒事件...")
        
        try:
            # 1. 提示用户可以开始说话
            logger.info("请说出您的命令...")
            
            # 2. 录音
            audio_file = record_audio(seconds=5)
            if not audio_file:
                logger.error("录音失败")
                self._speak("录音失败，请重试")
                return
            
            # 3. STT 语音转文字
            logger.info("正在识别语音...")
            text = transcribe(audio_file)
            if not text:
                logger.error("语音识别失败")
                self._speak("抱歉，我没有听清，请再说一遍")
                return
            
            logger.info(f"识别到: {text}")
            
            # 添加用户消息到记忆
            self.conversation_manager.add_message("user", text)
            
            # 4. LLM 匹配
            logger.info("正在使用 LLM 匹配...")
            skill, params = self.matcher.match(text)
            
            # 获取 reasoning 并打印
            reasoning = self.matcher.get_last_reasoning()
            if reasoning:
                logger.info(f"匹配推理: {reasoning}")
            
            if skill:
                logger.info(f"匹配到 Skill: {skill.name}")
                
                # 5. 执行 Skill
                result = skill.execute(params)
                logger.info(f"执行结果: {result}")
                
                # 添加助手回复到记忆
                self.conversation_manager.add_message("assistant", result)
                
                # 6. TTS 播放结果
                self._speak(result)
            else:
                logger.warning(f"未匹配到任何 Skill: {text}")
                
                # 尝试直接调用 LLM 进行对话
                llm_result = self._call_llm_directly(text)
                if llm_result:
                    llm_response = llm_result.get("content", "")
                    logger.info(f"LLM 响应: {llm_response}")
                    
                    # 添加助手回复到记忆
                    self.conversation_manager.add_message("assistant", llm_response)
                    
                    self._speak(llm_response)
                else:
                    response = "抱歉，我还不支持这个功能"
                    self.conversation_manager.add_message("assistant", response)
                    self._speak(response)
                
        except Exception as e:
            logger.error(f"处理唤醒事件时出错: {str(e)}")
            self._speak("处理命令时出错，请重试")
        finally:
            logger.info("唤醒事件处理完成")
    
    def _speak(self, text: str):
        """
        播放语音
        
        Args:
            text: 要播放的文本
        """
        try:
            speak(text)
        except Exception as e:
            logger.error(f"播放语音失败: {str(e)}")
    
    def start(self):
        """
        启动助手
        """
        logger.info("启动电脑助手...")
        logger.info("按 Cmd+Shift+Space 或说 'hey computer' 唤醒我")
        logger.info("按 Ctrl+C 退出")
        
        try:
            # 启动唤醒系统
            self.wake_system.start(
                callback=self.handle_wakeup,
                enable_voice=True,
                enable_key=True
            )
            
            # 保持运行
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("正在退出...")
        finally:
            # 停止唤醒系统
            self.wake_system.stop()
            logger.info("电脑助手已退出")


def main():
    """
    主函数
    """
    assistant = Assistant()
    assistant.start()


if __name__ == "__main__":
    main()
