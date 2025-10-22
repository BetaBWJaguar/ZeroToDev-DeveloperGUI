# -*- coding: utf-8 -*-
from gtts import gTTS
from io import BytesIO
from data_manager.DataManager import DataManager
import time

from logs_manager.LogsHelperManager import LogsHelperManager
from logs_manager.LogsManager import LogsManager
from tts.utility.TTSHelper import TTSHelper


class GTTSService(TTSHelper):
    def __init__(self, gtts_lang: str, ui_lang, max_chunk_chars=300, retries=1, retry_delay=0.6):
        super().__init__(lang=ui_lang, retries=retries, retry_delay=retry_delay)
        self.gtts_lang_code = gtts_lang

        self.max_chunk_chars = max_chunk_chars
        self.logger = LogsManager.get_logger("GTTSService")


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
        LogsHelperManager.log_debug(self.logger, "CHUNK_SPLIT", {
            "chunks": len(parts),
            "max_chunk_chars": self.max_chunk_chars
        })
        return parts

    def _synthesize_chunk(self, chunk: str) -> bytes:
        LogsHelperManager.log_debug(self.logger, "CHUNK_SYNTH", {
            "chars": len(chunk),
            "lang": self.gtts_lang_code
        })
        buf = BytesIO()
        tts = gTTS(text=chunk, lang=self.gtts_lang_code,slow=False)
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
                LogsHelperManager.log_debug(self.logger, "SYNTH_PROGRESS", {
                    "chunk": i,
                    "total": total,
                    "pct": pct,
                    "eta": eta
                })
                progress_cb(pct, f"TTS {int(frac * 100)}%  ~{int(eta)}s left")

        raw_all.seek(0)
        mem_buf = DataManager.write_to_memory(raw_all.read())
        LogsHelperManager.log_debug(self.logger, "SYNTH_DONE", {
            "total_chunks": total,
            "duration": time.time() - start
        })
        return DataManager.read_from_memory(mem_buf)

    def synthesize_preview(self, text: str, seconds=20, play_audio=True, progress_cb=None) -> bytes:
        return self.do_preview(self.synthesize_to_bytes, text, seconds, play_audio, progress_cb)
