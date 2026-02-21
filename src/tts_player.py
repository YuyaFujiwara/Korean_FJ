import asyncio
import ctypes
import os
import tempfile
import threading
import uuid
from tkinter import messagebox

try:
    import edge_tts

    EDGE_TTS_AVAILABLE = True
except Exception:
    EDGE_TTS_AVAILABLE = False

_tts_lock = threading.Lock()


def speak_korean(text: str, voice: str = "ko-KR-SunHiNeural", rate: str = "-25%"):
    if not EDGE_TTS_AVAILABLE:
        messagebox.showerror("edge-tts 未インストール", "pip install edge-tts を実行してください。")
        return

    def _mci_send(cmd: str):
        ctypes.windll.winmm.mciSendStringW(cmd, None, 0, None)

    def _play_mp3(path: str):
        alias = "hanguk_tts"
        _mci_send(f"close {alias}")
        _mci_send(f'open "{path}" type mpegvideo alias {alias}')
        _mci_send(f"play {alias}")

    def runner():
        async def job():
            with _tts_lock:
                mp3_name = f"hanguk_{uuid.uuid4().hex}.mp3"
                mp3_path = os.path.join(tempfile.gettempdir(), mp3_name)
                communicate = edge_tts.Communicate(text, voice=voice, rate=rate)  # type: ignore
                await communicate.save(mp3_path)
                _play_mp3(mp3_path)

        asyncio.run(job())

    threading.Thread(target=runner, daemon=True).start()