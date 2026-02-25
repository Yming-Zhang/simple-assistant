#!/usr/bin/env python3
"""
电脑助手主程序
整合所有组件：唤醒系统、音频处理、STT、TTS、Skill 系统
"""

import time
import logging
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
from matcher.keyword import KeywordMatcher

# 导入内置 Skills
from skills.builtin.screen import ScreenSkill
from skills.builtin.camera import CameraSkill
from skills.builtin.system_cmd import SystemCmdSkill
from skills.builtin.notification import NotificationSkill


class Assistant:
    """
    电脑助手主类
    整合所有功能模块
    """
    
    def __init__(self):
        logger.info("初始化电脑助手...")
        
        # 初始化 Skill 注册中心
        self.registry = get_registry()
        self._register_skills()
        
        # 初始化关键词匹配器
        self.matcher = KeywordMatcher(self.registry)
        
        # 初始化唤醒系统
        self.wake_system = get_wake_system()
        
        logger.info("电脑助手初始化完成！")
    
    def _register_skills(self):
        """
        注册所有 Skills
        """
        skills = [
            ScreenSkill(),
            CameraSkill(),
            SystemCmdSkill(),
            NotificationSkill(),
        ]
        
        for skill in skills:
            self.registry.register(skill)
            logger.info(f"注册 Skill: {skill.name}")
    
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
            
            # 4. 关键词匹配
            logger.info("正在匹配关键词...")
            skill, params = self.matcher.match(text)
            
            if skill:
                logger.info(f"匹配到 Skill: {skill.name}")
                # 5. 执行 Skill
                result = skill.execute(params)
                logger.info(f"执行结果: {result}")
                # 6. TTS 播放结果
                self._speak(result)
            else:
                logger.warning(f"未匹配到任何 Skill: {text}")
                self._speak("抱歉，我还不支持这个功能")
                
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
