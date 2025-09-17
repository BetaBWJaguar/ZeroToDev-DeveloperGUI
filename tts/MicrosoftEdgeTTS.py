# tts/MicrosoftEdgeTTS.py
# -*- coding: utf-8 -*-
import asyncio, time
from io import BytesIO
import edge_tts
from data_manager.DataManager import DataManager
from tts.TTSUtils import TTSUtils


class MicrosoftEdgeTTS:
    def __init__(self, voice="en-US-AriaNeural", retries=1, retry_delay=0.6, max_chunk_chars=300):
        self.voice = voice
        self.retries = retries
        self.retry_delay = retry_delay
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

    async def _synthesize_async_once(self, text: str, progress_cb=None) -> bytes:
        raw_buf = BytesIO()
        communicate = edge_tts.Communicate(text, self.voice)
        total_chars = len(text)
        processed_chars = 0
        start = time.time()

        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                raw_buf.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                processed_chars = chunk.get("textOffset", processed_chars)
                if progress_cb and total_chars > 0:
                    frac = min(1.0, processed_chars / total_chars)
                    pct = int(frac * 60)
                    elapsed = time.time() - start
                    eta = elapsed * (1 - frac) / frac if frac > 0 else 0
                    progress_cb(pct, f"TTS {int(frac*100)}%  ~{int(eta)}s left")

        raw_buf.seek(0)
        mem_buf = DataManager.write_to_memory(raw_buf.read())
        return DataManager.read_from_memory(mem_buf)

    def synthesize_to_bytes(self, text: str, progress_cb=None) -> bytes:
        chunks = self._chunk_text(text)
        total = len(chunks)
        raw_all = BytesIO()
        start = time.time()

        for i, chunk in enumerate(chunks, 1):
            audio_bytes = asyncio.run(self._synthesize_async_once(chunk, None))
            raw_all.write(audio_bytes)

            if progress_cb:
                frac = i / total
                pct = int(frac * 60)
                elapsed = time.time() - start
                eta = elapsed * (1 - frac) / frac if frac > 0 else 0
                progress_cb(pct, f"TTS {int(frac*100)}%  ~{int(eta)}s left")

        raw_all.seek(0)
        mem_buf = DataManager.write_to_memory(raw_all.read())
        return DataManager.read_from_memory(mem_buf)

    def synthesize_preview(self, text: str, seconds: int = 20, play_audio: bool = True) -> bytes:
        paragraphs = text.split("\n\n")
        snippet = paragraphs[0] if paragraphs else text[:300]

        audio_bytes = self.synthesize_to_bytes(snippet)

        return TTSUtils.preview(audio_bytes, seconds=seconds, play_audio=play_audio)

