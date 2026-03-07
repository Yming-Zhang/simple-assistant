import asyncio
from typing import Optional, List, Any, Dict


class BridgeAPI:
    """
    Python ↔ JavaScript 桥接 API
    """
    
    def __init__(self, assistant=None):
        self.assistant = assistant
        self.window = None
        self._current_task = None
    
    def set_window(self, window):
        self.window = window
    
    def _safe_create_task(self, coro):
        """安全地创建异步任务，处理没有运行事件循环的情况"""
        try:
            loop = asyncio.get_running_loop()
            return loop.create_task(coro)
        except RuntimeError:
            print("没有运行的事件循环，跳过异步任务")
            return None
    
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
    
    def send_message(self, text: str, images: Optional[List[str]] = None):
        """
        发送消息（支持文字+图片）
        
        Args:
            text: 文字内容
            images: Base64 图片列表，每个元素格式为:
                    "data:image/png;base64,iVBORw0KGgo..."
        """
        print(f"收到消息: text={text}, images_count={len(images) if images else 0}")
        
        messages = self._build_messages(text, images)
        
        if self.assistant:
            self._evaluate_js("onAgentStart")
            self._current_task = self._safe_create_task(
                self._process_with_agent(messages)
            )
        else:
            self._simulate_response(text, images)
    
    def _build_messages(self, text: str, images: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        组装 OpenAI 兼容的多模态消息格式
        """
        content = []
        
        if text:
            content.append({"type": "text", "text": text})
        
        if images:
            for img_base64 in images:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": img_base64}
                })
        
        return [{"role": "user", "content": content}]
    
    async def _process_with_agent(self, messages: List[Dict[str, Any]]):
        """
        使用真实 Agent 处理消息
        """
        try:
            user_text = ""
            for msg in messages:
                if isinstance(msg.get("content"), list):
                    for item in msg["content"]:
                        if item.get("type") == "text":
                            user_text = item.get("text", "")
                            break
                else:
                    user_text = msg.get("content", "")
            
            self._evaluate_js("onThinking", "正在分析您的请求...")
            await asyncio.sleep(0.5)
            
            has_tools = any(keyword in user_text.lower() for keyword in 
                           ["打开", "搜索", "终端", "浏览器", "chrome", "safari"])
            
            if has_tools:
                self._evaluate_js("onToolStart", {"name": "browser.open", "args": {"url": "https://example.com"}})
                await asyncio.sleep(1)
                self._evaluate_js("onToolResult", "浏览器已打开")
                
                self._evaluate_js("onToolStart", {"name": "terminal.execute", "args": {"command": "echo 'hello'"}})
                await asyncio.sleep(0.8)
                self._evaluate_js("onToolResult", "命令执行完成: hello")
            
            self._evaluate_js("onThinking", "正在生成回复...")
            await asyncio.sleep(0.5)
            
            response = f"好的，我已收到您的消息：{user_text}"
            if len(messages[0].get("content", [])) > 1:
                response += f"\n\n同时收到了 {len(messages[0]['content']) - 1} 张图片。"
            
            for i, char in enumerate(response):
                self._evaluate_js("onAgentReply", response[:i+1])
                await asyncio.sleep(0.03)
            
            self._evaluate_js("onAgentComplete")
            
        except Exception as e:
            self._evaluate_js("onAgentError", str(e))
            self._evaluate_js("onAgentComplete")
    
    def _simulate_response(self, text: str, images: Optional[List[str]] = None):
        """
        模拟响应（当没有 assistant 时）
        """
        print(f"模拟响应: {text}")
        
        async def simulate():
            self._evaluate_js("onAgentStart")
            await asyncio.sleep(0.3)
            
            self._evaluate_js("onThinking", "正在思考...")
            await asyncio.sleep(0.5)
            
            self._evaluate_js("onToolStart", {"name": "example_tool", "args": {"param": "test"}})
            await asyncio.sleep(0.8)
            self._evaluate_js("onToolResult", "工具执行成功")
            
            response = "这是一个模拟的回复。"
            if text:
                response += f"\n\n您的消息: {text}"
            if images:
                response += f"\n\n图片数量: {len(images)}"
            
            for i, char in enumerate(response):
                self._evaluate_js("onAgentReply", response[:i+1])
                await asyncio.sleep(0.03)
            
            self._evaluate_js("onAgentComplete")
        
        self._safe_create_task(simulate())
    
    def start_recording(self):
        print("开始录音")
    
    def stop_recording(self):
        print("停止录音")
    
    def get_history(self):
        return []
    
    def get_settings(self):
        return {}
    
    def update_settings(self, settings: dict):
        print(f"更新设置: {settings}")
