# -*- coding: utf-8 -*-
import time
from io import BytesIO
from pydub import AudioSegment
import simpleaudio as sa
from PathHelper import PathHelper
from VoiceProcessor import VoiceProcessor
from data_manager.MemoryManager import MemoryManager
from logs_manager.LogsHelperManager import LogsHelperManager
from logs_manager.LogsManager import LogsManager


class TTSHelper:
    def __init__(self, lang, retries=1, retry_delay=0.6):
        self.lang = lang
        self._stop_preview = False
        self._preview_play_obj = None
        self.retries = retries
        self.retry_delay = retry_delay

    def _with_retry(self, func, *args, **kwargs):
        last_err = None
        for attempt in range(1, self.retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_err = e
                if attempt < self.retries:
                    time.sleep(self.retry_delay)
                else:
                    raise RuntimeError(f"TTS failed after {self.retries} attempts: {e}")
        raise last_err

    def stop_preview(self):
        self._stop_preview = True
        if getattr(self, "_preview_play_obj", None):
            try:
                if self._preview_play_obj.is_playing():
                    self._preview_play_obj.stop()
            except Exception:
                pass

    def do_preview(self, synthesize_func, text: str,
                   seconds: int = 20,
                   play_audio: bool = True,
                   progress_cb=None) -> bytes:
        paragraphs = text.split("\n\n")
        snippet = paragraphs[0] if paragraphs else text[:300]

        if progress_cb: progress_cb(30, self.lang.get("progress_generating_tts"))
        raw_bytes = synthesize_func(snippet)

        if progress_cb: progress_cb(50, self.lang.get("progress_applying_preview_effects"))
        settings = {k: MemoryManager.get(k, v) for k, v in {
            "pitch": 0, "speed": 1.0, "volume": 1.0,
            "echo": False, "reverb": False, "robot": False
        }.items()}
        logger = LogsManager.get_logger("TTSHelper")
        LogsHelperManager.log_debug(logger, "EFFECTS_APPLIED_PREVIEW", settings)
        processed_bytes = VoiceProcessor.process_from_memory(raw_bytes, "mp3", settings)

        audio = AudioSegment.from_file(BytesIO(processed_bytes), format="mp3")
        preview = audio[:seconds * 1000]

        out_buf = BytesIO()
        preview.export(out_buf, format="mp3")
        out_buf.seek(0)

        if play_audio:
            if progress_cb: progress_cb(90, self.lang.get("preview_playing"))
            self._preview_play_obj = sa.play_buffer(
                preview.raw_data,
                num_channels=preview.channels,
                bytes_per_sample=preview.sample_width,
                sample_rate=preview.frame_rate
            )
            self._preview_play_obj.wait_done()

            while self._preview_play_obj.is_playing():
                if self._stop_preview:
                    break
                time.sleep(0.05)

        if progress_cb: progress_cb(100, self.lang.get("preview_done"))

        ding_path = PathHelper.resource_path("tts/utility/sounds/ding.wav")
        if not ding_path.exists():
            raise FileNotFoundError(f"ding.wav not found at {ding_path}")

        try:
            ding_audio = sa.WaveObject.from_wave_file(str(ding_path))
            ding_play = ding_audio.play()
            ding_play.wait_done()
        except Exception as e:
            raise RuntimeError(f"Ding sound failed: {e}")

        return out_buf.read()