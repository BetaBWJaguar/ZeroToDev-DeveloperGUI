# -*- coding: utf-8 -*-
from gtts import gTTS
from io import BytesIO
from data_manager.DataManager import DataManager
import time
from tts.utility.TTSHelper import TTSHelper


class GTTSService(TTSHelper):
    def __init__(self, lang, max_chunk_chars=300, retries=1, retry_delay=0.6):
        super().__init__(retries, retry_delay)
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
                buf.append(w)
                count += len(w) + 1
        if buf:
            parts.append(" ".join(buf))
        return parts

    def _synthesize_chunk(self, chunk: str) -> bytes:
        buf = BytesIO()
        tts = gTTS(text=chunk, lang=self.lang)
        tts.write_to_fp(buf)
        buf.seek(0)
        return buf.read()

    def synthesize_to_bytes(self, text: str, progress_cb=None) -> bytes:
        chunks = self._chunk_text(text)
        total = len(chunks)
        raw_all = BytesIO()
        start = time.time()

        for i, chunk in enumerate(chunks, 1):

            raw_all.write(self._with_retry(self._synthesize_chunk, chunk))

            if progress_cb:
                frac = i / total
                pct = int(frac * 60)
                elapsed = time.time() - start
                eta = elapsed * (1 - frac) / frac if frac > 0 else 0
                progress_cb(pct, f"TTS {int(frac * 100)}%  ~{int(eta)}s left")

        raw_all.seek(0)
        mem_buf = DataManager.write_to_memory(raw_all.read())
        return DataManager.read_from_memory(mem_buf)

    def synthesize_preview(self, text: str, seconds=20, play_audio=True, progress_cb=None) -> bytes:
        return self.do_preview(self.synthesize_to_bytes, text, seconds, play_audio, progress_cb)
