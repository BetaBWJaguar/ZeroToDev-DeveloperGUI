# -*- coding: utf-8 -*-
"""
MarkupManager.py
Processes parsed markup tokens and builds final TTS audio output.
Supports <break> and <emphasis> tags.
"""

import time
from io import BytesIO
from pydub import AudioSegment
from data_manager.DataManager import DataManager
from logs_manager.LogsHelperManager import LogsHelperManager
from logs_manager.LogsManager import LogsManager
from VoiceProcessor import VoiceProcessor
from markup.MarkupManagerUtility import MarkupManagerUtility


class MarkupManager:
    def __init__(self, tts_service, default_format="mp3"):
        self.tts_service = tts_service
        self.format = default_format
        self.parser = MarkupManagerUtility()
        self.logger = LogsManager.get_logger("MarkupManager")

    def synthesize_with_markup(self, text: str, progress_cb=None) -> bytes:
        tokens = self.parser.parse(text)
        self.parser.debug_tokens(tokens)

        combined = AudioSegment.silent(duration=0)
        start = time.time()
        total = len(tokens)

        for i, token in enumerate(tokens, 1):
            if token.type == "text":
                seg = self._tts_segment(token.value)
                combined += seg

            elif token.type == "break":
                ms = self._parse_duration(token.attrs.get("time", "1s"))
                combined += AudioSegment.silent(duration=ms)

            elif token.type == "emphasis":
                seg = self._tts_segment(token.value, emphasis=True, attrs=token.attrs)
                combined += seg

            if progress_cb:
                pct = int((i / total) * 100)
                progress_cb(pct, f"Markup synthesis {pct}%")
                LogsHelperManager.log_debug(self.logger, "MARKUP_PROGRESS", {
                    "pct": pct,
                    "token_type": token.type
                })

        buf = BytesIO()
        combined.export(buf, format=self.format)
        buf.seek(0)
        LogsHelperManager.log_debug(self.logger, "MARKUP_DONE", {
            "duration": time.time() - start,
            "tokens": total
        })
        mem_buf = DataManager.write_to_memory(buf.read())
        return DataManager.read_from_memory(mem_buf)

    def _tts_segment(self, text: str, emphasis=False, attrs=None):
        raw_bytes = self.tts_service.synthesize_to_bytes(text)
        audio = AudioSegment.from_file(BytesIO(raw_bytes), format=self.format)

        if emphasis:
            level = (attrs or {}).get("level", "moderate")
            if level == "strong":
                audio += 6
            elif level == "reduced":
                audio -= 3

        processed_bytes = VoiceProcessor.process_from_memory(
            audio.export(BytesIO(), format="mp3").getvalue(), "mp3",
            {"pitch": 0, "speed": 1.0, "volume": 1.0, "echo": False, "reverb": False, "robot": False}
        )
        return AudioSegment.from_file(BytesIO(processed_bytes), format="mp3")

    def _parse_duration(self, val: str) -> int:
        val = val.strip().lower()
        if val.endswith("ms"):
            return int(float(val[:-2]))
        if val.endswith("s"):
            return int(float(val[:-1]) * 1000)
        return int(float(val) * 1000)
