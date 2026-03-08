import time
import threading
import asyncio
from typing import Optional, List, Any, Dict


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
            self._stream_llm_with_assistant(text)
            
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
                    # 流式调用 LLM
                    self._stream_llm_with_assistant(text, images)
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
    
    def _stream_llm_with_assistant(self, text: str, images: Optional[List[str]] = None):
        """
        使用真实的 Assistant 进行完整处理：先匹配工具 → 执行工具 → LLM对话
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
                self._evaluate_js("onAgentComplete")
            except Exception as e:
                print(f"流式调用失败: {e}")
                import traceback
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
    
    def get_history(self):
        return [
            {"id": "1", "date": "2026-03-07", "title": "今天的天气怎么样"},
            {"id": "2", "date": "2026-03-07", "title": "打开 Chrome 浏览器"},
            {"id": "3", "date": "2026-03-06", "title": "设置提醒"},
            {"id": "4", "date": "2026-03-06", "title": "创建文档"},
            {"id": "5", "date": "2026-03-05", "title": "音乐播放"}
        ]
    
    def get_settings(self):
        return {
            "showThinkingChain": True,
            "model": "qwen3.5",
            "temperature": 0.7
        }
    
    def update_settings(self, settings: dict):
        print(f"更新设置: {settings}")
