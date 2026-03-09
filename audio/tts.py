import asyncio
import tempfile
from pathlib import Path
from typing import Optional
import edge_tts
from config import config
from audio.player import play_audio


class TTS:
    def __init__(self):
        self.voice = config.tts.voice
        self.rate = config.tts.rate
        self.volume = config.tts.volume

    def update_from_config(self):
        """从最新 config 刷新运行时参数"""
        self.voice = config.tts.voice
        self.rate = config.tts.rate
        self.volume = config.tts.volume

    async def _synthesize(self, text: str, output_path: str,
                           volume: Optional[float] = None,
                           rate: Optional[float] = None) -> None:
        """合成语音到文件
        
        Args:
            text: 要合成的文本
            output_path: 输出文件路径
            volume: 可选音量覆盖 (0.0-1.0)
            rate: 可选语速覆盖
        """
        effective_rate = rate if rate is not None else self.rate
        effective_volume = volume if volume is not None else self.volume
        
        # edge-tts 的 rate 参数格式: "+0%", "-20%", "+50%" 等
        rate_str = f"{int((effective_rate - 1.0) * 100):+d}%"
        # edge-tts 的 volume 参数格式: "+0%", "-50%", "+100%" 等
        volume_str = f"{int((effective_volume - 1.0) * 100):+d}%"
        
        communicate = edge_tts.Communicate(
            text, 
            self.voice,
            rate=rate_str,
            volume=volume_str
        )
        await communicate.save(output_path)

    def speak(self, text: str, volume: Optional[float] = None,
              rate: Optional[float] = None) -> None:
        """播放语音
        
        Args:
            text: 要播报的文本
            volume: 可选音量覆盖 (0.0-1.0)，None 则使用 config 值
            rate: 可选语速覆盖，None 则使用 config 值
        """
        if not text:
            print("没有文字需要播放")
            return
        
        # 检查 TTS 是否启用
        if not config.tts.enabled:
            print("TTS 已禁用，跳过播报")
            return
        
        print(f"播放语音: {text[:50]}...")
        
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            asyncio.run(self._synthesize(text, temp_path, volume=volume, rate=rate))
            play_audio(temp_path)
            print("播放完成")
        except Exception as e:
            print(f"播放语音失败: {e}")
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def should_speak(self, wake_source: str = "manual") -> bool:
        """根据配置和唤醒来源判断是否应该播报
        
        Args:
            wake_source: 唤醒来源 'voice' | 'key' | 'manual'
            
        Returns:
            True 表示应该播报
        """
        if not config.tts.enabled:
            return False
        if config.tts.only_when_wake_by_voice and wake_source != "voice":
            return False
        return True

    def save_to_file(self, text: str, output_path: str) -> None:
        if not text:
            print("没有文字需要转换")
            return
        
        print(f"生成语音文件: {output_path}")
        
        try:
            asyncio.run(self._synthesize(text, output_path))
            print(f"语音文件已保存到: {output_path}")
        except Exception as e:
            print(f"生成语音文件失败: {e}")


_tts_instance: Optional[TTS] = None


def get_tts() -> TTS:
    global _tts_instance
    if _tts_instance is None:
        _tts_instance = TTS()
    return _tts_instance


def speak(text: str, wake_source: str = "manual") -> None:
    """智能播报：根据唤醒来源和配置决定是否播报"""
    tts = get_tts()
    if tts.should_speak(wake_source):
        tts.speak(text)
    else:
        print(f"跳过 TTS (wake_source={wake_source}, enabled={config.tts.enabled}, only_voice={config.tts.only_when_wake_by_voice})")


def save_to_file(text: str, output_path: str) -> None:
    get_tts().save_to_file(text, output_path)


async def list_voices_async() -> None:
    voices = await edge_tts.list_voices()
    print("可用中文语音:")
    for voice in voices:
        if voice["Locale"].startswith("zh"):
            print(f"  {voice['ShortName']:30} {voice['Locale']:10} {voice['FriendlyName']}")


def list_voices() -> None:
    asyncio.run(list_voices_async())


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "--list":
            list_voices()
        elif sys.argv[1] == "--save" and len(sys.argv) > 3:
            save_to_file(sys.argv[2], sys.argv[3])
        else:
            speak(" ".join(sys.argv[1:]))
    else:
        print("用法:")
        print("  python tts.py <文字>          # 播放语音")
        print("  python tts.py --list           # 列出所有中文语音")
        print("  python tts.py --save <文字> <输出文件>  # 保存到文件")
