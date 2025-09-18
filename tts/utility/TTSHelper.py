# -*- coding: utf-8 -*-
import time
from io import BytesIO
from pydub import AudioSegment
import simpleaudio as sa
from VoiceProcessor import VoiceProcessor
from data_manager.MemoryManager import MemoryManager


class TTSHelper:
    def __init__(self, retries=1, retry_delay=0.6):
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

    def do_preview(self, synthesize_func, text: str,
                    seconds: int = 20,
                    play_audio: bool = True,
                    progress_cb=None) -> bytes:
        paragraphs = text.split("\n\n")
        snippet = paragraphs[0] if paragraphs else text[:300]


        if progress_cb: progress_cb(30, "Generating TTS…")
        raw_bytes = synthesize_func(snippet)


        if progress_cb: progress_cb(50, "Applying preview effects…")
        settings = {k: MemoryManager.get(k, v) for k, v in {
            "pitch": 0, "speed": 1.0, "volume": 1.0,
            "echo": False, "reverb": False, "robot": False
        }.items()}
        processed_bytes = VoiceProcessor.process_from_memory(raw_bytes, "mp3", settings)


        audio = AudioSegment.from_file(BytesIO(processed_bytes), format="mp3")
        preview = audio[:seconds * 1000]

        out_buf = BytesIO()
        preview.export(out_buf, format="mp3")
        out_buf.seek(0)


        if play_audio:
            if progress_cb: progress_cb(90, "Playing preview…")
            play_obj = sa.play_buffer(
                preview.raw_data,
                num_channels=preview.channels,
                bytes_per_sample=preview.sample_width,
                sample_rate=preview.frame_rate
            )
            play_obj.wait_done()

        if progress_cb: progress_cb(100, "Preview done ✔️")
        return out_buf.read()
