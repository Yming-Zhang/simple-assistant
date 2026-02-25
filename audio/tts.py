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

    async def _synthesize(self, text: str, output_path: str) -> None:
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(output_path)

    def speak(self, text: str) -> None:
        if not text:
            print("没有文字需要播放")
            return
        
        print(f"播放语音: {text}")
        
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            asyncio.run(self._synthesize(text, temp_path))
            play_audio(temp_path)
            print("播放完成")
        finally:
            Path(temp_path).unlink(missing_ok=True)

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


def speak(text: str) -> None:
    get_tts().speak(text)


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
