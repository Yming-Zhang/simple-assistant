import time
import threading
import asyncio
import traceback
from typing import Optional, List, Any, Dict

from config import settings_manager


class BridgeAPI:
    """
    Python ↔ JavaScript 桥接 API
    整合 Assistant 主控制器
    """
    
    def __init__(self, assistant=None):
        self.assistant = assistant
        self.window = None
        self._is_recording = False
        self._audio_file = None
        
        # 创建异步事件循环用于流式调用
        self._stream_loop = asyncio.new_event_loop()
        self._stream_thread = None
        self._stream_running = False
        
        # 注入 SettingsManager 的 DB
        if self.assistant and hasattr(self.assistant, 'memory_db'):
            settings_manager.set_db(self.assistant.memory_db)
    
    def set_window(self, window):
        self.window = window
    
    def _evaluate_js(self, func_name: str, *args):
        """
        调用 JavaScript 函数
        """
        if self.window:
            try:
                args_str = ", ".join(repr(arg) for arg in args)
                self.window.evaluate_js(f"{func_name}({args_str})")
            except Exception as e:
                print(f"JS 调用失败: {e}")
    
    # ======== 会话管理 API ========
    
    def get_history_list(self):
        """获取会话列表（真实数据）"""
        try:
            if self.assistant and hasattr(self.assistant, 'conversation_manager'):
                convs = self.assistant.conversation_manager.list_conversations()
                # 转为前端友好格式
                result = []
                for c in convs:
                    result.append({
                        "id": c["id"],
                        "title": c.get("title", "新对话"),
                        "preview": c.get("preview") or "",
                        "created_at": c.get("created_at", ""),
                        "updated_at": c.get("updated_at", ""),
                        "message_count": c.get("message_count", 0)
                    })
                return result
            return []
        except Exception as e:
            print(f"获取会话列表失败: {e}")
            traceback.print_exc()
            return []
    
    def get_conversation(self, conv_id: str):
        """获取指定会话的完整内容，同时激活该会话为当前会话"""
        try:
            if self.assistant and hasattr(self.assistant, 'conversation_manager'):
                # 切换后端当前活跃会话
                self.assistant.conversation_manager.set_current_conversation(conv_id)
                conv = self.assistant.conversation_manager.get_conversation(conv_id)
                if conv:
                    # 转换消息格式
                    messages = []
                    for m in conv.get("messages", []):
                        messages.append({
                            "id": str(m.get("id", "")),
                            "role": m["role"],
                            "content": m["content"],
                            "timestamp": m.get("timestamp", ""),
                            "images": m.get("images", [])
                        })
                    return {
                        "id": conv["id"],
                        "title": conv.get("title", "新对话"),
                        "created_at": conv.get("created_at", ""),
                        "updated_at": conv.get("updated_at", ""),
                        "messages": messages
                    }
            return None
        except Exception as e:
            print(f"获取会话详情失败: {e}")
            traceback.print_exc()
            return None
    
    def create_conversation(self):
        """创建新会话，返回 conversation id（同时激活为当前会话）"""
        try:
            if self.assistant and hasattr(self.assistant, 'conversation_manager'):
                conv_id = self.assistant.conversation_manager.create_conversation()
                # create_conversation 内部已经 set _current_conversation_id
                return conv_id
            return None
        except Exception as e:
            print(f"创建会话失败: {e}")
            traceback.print_exc()
            return None
    
    def rename_conversation(self, conv_id: str, title: str):
        """重命名会话"""
        try:
            if self.assistant and hasattr(self.assistant, 'conversation_manager'):
                return self.assistant.conversation_manager.rename_conversation(conv_id, title)
            return False
        except Exception as e:
            print(f"重命名会话失败: {e}")
            traceback.print_exc()
            return False
    
    def delete_conversation(self, conv_id: str):
        """删除会话"""
        try:
            if self.assistant and hasattr(self.assistant, 'conversation_manager'):
                return self.assistant.conversation_manager.delete_conversation(conv_id)
            return False
        except Exception as e:
            print(f"删除会话失败: {e}")
            traceback.print_exc()
            return False
    
    # ======== 设置 API ========
    
    def get_settings(self):
        """获取所有设置（真实持久化数据）"""
        try:
            return settings_manager.get_all()
        except Exception as e:
            print(f"获取设置失败: {e}")
            traceback.print_exc()
            return settings_manager.UI_DEFAULTS
    
    def update_settings(self, settings: dict):
        """更新设置（写入 DB + 同步 Python config）"""
        try:
            print(f"更新设置: {settings}")
            settings_manager.update(settings)
            return True
        except Exception as e:
            print(f"更新设置失败: {e}")
            traceback.print_exc()
            return False
    
    def validate_whisper_path(self, path: str):
        """校验 Whisper 路径"""
        try:
            return settings_manager.validate_whisper_path(path)
        except Exception as e:
            return {"valid": False, "message": str(e)}
    
    # ======== 录音 API ========
    
    def start_recording(self):
        """
        开始录音（前端调用）
        """
        print("开始录音")
        self._is_recording = True
        self._evaluate_js("onAgentStart")
        
        try:
            from audio.microphone import start_recording as mic_start
            mic_start()
        except Exception as e:
            print(f"启动录音失败: {e}")
            self._evaluate_js("onAgentError", f"启动录音失败: {e}")
            self._evaluate_js("onAgentComplete")
            self._is_recording = False
    
    def stop_recording(self):
        """
        停止录音并处理（前端调用）
        完整流程：停止录音 → STT → 发送给 Agent → 推送到前端
        """
        print("停止录音")
        self._is_recording = False
        
        def process():
            try:
                if self.assistant:
                    # 有真实 Assistant 的情况
                    self._process_with_assistant()
                else:
                    # 没有 Assistant，模拟
                    self._simulate_process()
            except Exception as e:
                print(f"处理失败: {e}")
                self._evaluate_js("onAgentError", str(e))
                self._evaluate_js("onAgentComplete")
        
        thread = threading.Thread(target=process)
        thread.daemon = True
        thread.start()
    
    def _process_with_assistant(self):
        """
        使用真实的 Assistant 处理录音
        """
        try:
            from audio.microphone import stop_recording as mic_stop
            from audio.stt import transcribe
            
            # 1. 停止录音并保存
            self._evaluate_js("onThinking", "正在处理录音...")
            audio_file = mic_stop("output.wav")
            
            if not audio_file:
                self._evaluate_js("onAgentError", "录音失败")
                self._evaluate_js("onAgentComplete")
                return
            
            # 2. STT 转文字
            self._evaluate_js("onThinking", "正在识别语音...")
            text = transcribe(audio_file)
            
            if not text:
                self._evaluate_js("onAgentError", "语音识别失败")
                self._evaluate_js("onAgentComplete")
                return
            
            print(f"识别到: {text}")
            
            # 3. 添加用户消息到前端
            self._evaluate_js("onUserMessage", text)
            
            # 4. 完整处理流程：匹配工具 → 执行工具 → LLM对话
            # 标记唤醒来源为语音
            self._stream_llm_with_assistant(text, wake_source="voice")
            
        except Exception as e:
            print(f"处理失败: {e}")
            self._evaluate_js("onAgentError", str(e))
            self._evaluate_js("onAgentComplete")
    
    def send_message(self, text: str, images: Optional[List[str]] = None):
        """
        发送文字消息（用户直接输入文字时调用）
        """
        print(f"收到文字消息: text={text}, images_count={len(images) if images else 0}")
        
        def process():
            try:
                # 添加用户消息到前端
                self._evaluate_js("onUserMessage", text)
                
                if self.assistant:
                    # 流式调用 LLM，标记唤醒来源为手动
                    self._stream_llm_with_assistant(text, images, wake_source="manual")
                else:
                    # 模拟响应
                    self._simulate_response(text, images)
                    
            except Exception as e:
                print(f"处理失败: {e}")
                self._evaluate_js("onAgentError", str(e))
                self._evaluate_js("onAgentComplete")
        
        thread = threading.Thread(target=process)
        thread.daemon = True
        thread.start()
    
    def _stream_llm_with_assistant(self, text: str, images: Optional[List[str]] = None,
                                    wake_source: str = "manual"):
        """
        使用真实的 Assistant 进行完整处理：先匹配工具 → 执行工具 → LLM对话
        wake_source: 'voice' | 'key' | 'manual'
        """
        self._evaluate_js("onAgentStart")
        self._evaluate_js("onThinking", "正在分析任务...")
        
        # 预处理文本，避免闭包问题
        processed_text = text
        if images:
            processed_text += f"\n\n（收到了 {len(images)} 张图片）"
        
        async def on_chunk(chunk_type, content):
            """
            流式回调：接收思考过程和内容，实时推送到前端
            """
            if chunk_type == "reasoning":
                self._evaluate_js("onThinking", content)
            elif chunk_type == "content":
                self._evaluate_js("onAgentReply", content)
            elif chunk_type == "tool_start":
                self._evaluate_js("onToolStart", content)
            elif chunk_type == "tool_result":
                self._evaluate_js("onToolResult", content)
        
        async def stream_task():
            """
            异步流式调用任务
            """
            try:
                await self.assistant._stream_process(processed_text, on_chunk)
                
                # 处理完成后，判断是否需要 TTS 播报
                self._maybe_tts_reply(wake_source)
                
                self._evaluate_js("onAgentComplete")
            except Exception as e:
                print(f"流式调用失败: {e}")
                traceback.print_exc()
                self._evaluate_js("onAgentError", str(e))
                self._evaluate_js("onAgentComplete")
        
        # 在独立线程的事件循环中运行异步任务
        def run_stream():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(stream_task())
            finally:
                loop.close()
        
        stream_thread = threading.Thread(target=run_stream)
        stream_thread.daemon = True
        stream_thread.start()
    
    def _maybe_tts_reply(self, wake_source: str):
        """根据设置和唤醒来源决定是否 TTS 播报"""
        try:
            from config import config
            
            if not config.tts.enabled:
                return
            
            if config.tts.only_when_wake_by_voice and wake_source != "voice":
                return
            
            # 获取最后一条 assistant 消息
            if self.assistant and hasattr(self.assistant, 'conversation_manager'):
                session = self.assistant.conversation_manager.current_session
                if session:
                    last = session[-1]
                    if last.get("role") == "assistant" and last.get("content"):
                        content = last["content"]
                        # 截取前 200 字播报
                        if len(content) > 200:
                            content = content[:200] + "..."
                        from audio.tts import get_tts
                        tts = get_tts()
                        tts.speak(content)
        except Exception as e:
            print(f"TTS 播报失败: {e}")
    
    # ======== 模拟方法（无 assistant 时） ========
    
    def _simulate_process(self):
        """
        模拟处理录音流程（没有 assistant 时）
        """
        self._evaluate_js("onThinking", "正在录音...")
        time.sleep(1)
        
        self._evaluate_js("onThinking", "正在识别语音...")
        time.sleep(1)
        
        text = "你是谁"
        self._evaluate_js("onUserMessage", text)
        self._simulate_response(text, None)
    
    def _simulate_response(self, text: str, images: Optional[List[str]] = None):
        """
        模拟响应（没有 assistant 时）
        """
        self._evaluate_js("onAgentStart")
        time.sleep(0.3)
        
        self._evaluate_js("onThinking", "正在思考...")
        time.sleep(0.5)
        
        has_tools = any(keyword in text.lower() for keyword in 
                       ["打开", "搜索", "终端", "浏览器", "chrome", "safari"])
        
        if has_tools:
            self._evaluate_js("onToolStart", {"name": "browser.open", "args": {"url": "https://example.com"}})
            time.sleep(1)
            self._evaluate_js("onToolResult", "浏览器已打开")
            
            self._evaluate_js("onToolStart", {"name": "terminal.execute", "args": {"command": "echo 'hello'"}})
            time.sleep(0.8)
            self._evaluate_js("onToolResult", "命令执行完成: hello")
        
        self._evaluate_js("onThinking", "正在生成回复...")
        time.sleep(0.5)
        
        response = "这是一个模拟的回复。"
        if text:
            response += f"\n\n您的消息: {text}"
        if images:
            response += f"\n\n图片数量: {len(images)}"
        
        for i in range(len(response)):
            self._evaluate_js("onAgentReply", response[:i+1])
            time.sleep(0.03)
        
        self._evaluate_js("onAgentComplete")
    
    # ======== 旧兼容 API（重定向到新方法） ========
    
    def get_history(self):
        """兼容旧前端调用"""
        return self.get_history_list()
    
    # ======== Skills API ========
    
    def get_skills(self):
        """获取所有已加载的技能列表"""
        if not self.assistant:
            return []
        
        skills = []
        for skill in self.assistant.registry.get_all():
            skill_info = {
                "name": skill.name,
                "description": skill.description,
                "keywords": getattr(skill, "keywords", []),
                "is_knowledge": getattr(skill, "is_knowledge", False),
                "enabled": True
            }
            skills.append(skill_info)
        
        return skills
    
    def reload_skills(self):
        """重新加载所有技能"""
        from pathlib import Path
        
        if not self.assistant:
            return False
        
        try:
            self.assistant.registry.clear()
            
            builtin_dir = Path(__file__).parent.parent / "skills" / "builtin"
            if builtin_dir.exists():
                self.assistant.skill_loader.load_from_directory(str(builtin_dir))
                
                memory_search = self.assistant.registry.get("memory_search")
                if memory_search and hasattr(memory_search, "set_conversation_manager"):
                    memory_search.set_conversation_manager(self.assistant.conversation_manager)
                
                memory_get = self.assistant.registry.get("memory_get")
                if memory_get and hasattr(memory_get, "set_conversation_manager"):
                    memory_get.set_conversation_manager(self.assistant.conversation_manager)
            
            knowledge_dir = Path(__file__).parent.parent / "skills" / "knowledge"
            if knowledge_dir.exists():
                self.assistant.skill_loader.load_from_directory(str(knowledge_dir))
            
            external_dir = Path(__file__).parent.parent / "skills" / "external"
            if external_dir.exists():
                self.assistant.skill_loader.load_from_directory(str(external_dir))
            
            self.assistant.matcher = type(self.assistant.matcher)(
                self.assistant.registry, 
                self.assistant.loop
            )
            
            print("技能重新加载成功")
            return True
        except Exception as e:
            print(f"重新加载技能失败: {e}")
            traceback.print_exc()
            return False
