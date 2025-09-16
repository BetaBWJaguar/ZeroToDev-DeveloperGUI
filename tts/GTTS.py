# tts/GTTS.py
# -*- coding: utf-8 -*-
from gtts import gTTS
from io import BytesIO
from data_manager.DataManager import DataManager
import time

class GTTSService:
    output_format = "mp3"

    def __init__(self, lang="en", max_chunk_chars=300):
        self.lang = lang
        self.max_chunk_chars = max_chunk_chars

    def _chunk_text(self, text: str):
        if len(text) <= self.max_chunk_chars:
            return [text]
        words, buf, count, parts = text.split(), [], 0, []
        for w in words:
            if count + len(w) + 1 > self.max_chunk_chars:
                parts.append(" ".join(buf))
                buf, count = [w], len(w) + 1
            else:
                buf.append(w); count += len(w) + 1
        if buf: parts.append(" ".join(buf))
        return parts

    def synthesize_to_bytes(self, text: str, progress_cb=None) -> bytes:
        chunks = self._chunk_text(text)
        total = len(chunks)
        raw_all = BytesIO()
        start = time.time()

        for i, chunk in enumerate(chunks, 1):
            buf = BytesIO()
            tts = gTTS(text=chunk, lang=self.lang)
            tts.write_to_fp(buf); buf.seek(0)
            raw_all.write(buf.read())

            if progress_cb:
                frac = i / total
                pct = int(frac * 60)
                elapsed = time.time() - start
                eta = elapsed * (1 - frac) / frac if frac > 0 else 0
                progress_cb(pct, f"TTS {int(frac*100)}%  ~{int(eta)}s left")

        raw_all.seek(0)
        mem_buf = DataManager.write_to_memory(raw_all.read())
        return DataManager.read_from_memory(mem_buf)
