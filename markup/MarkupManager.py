# -*- coding: utf-8 -*-
import time
from io import BytesIO
from pydub import AudioSegment
from data_manager.DataManager import DataManager
from logs_manager.LogsHelperManager import LogsHelperManager
from logs_manager.LogsManager import LogsManager
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
            seg = None

            if token.type == "text":
                seg = self._tts_segment(token.value)

            elif token.type == "break":
                ms = self._parse_duration(token.attrs.get("time", "1s"))
                seg = AudioSegment.silent(duration=ms)

            elif token.type == "emphasis":
                seg = self._tts_segment(token.value)
                level = token.attrs.get("level", "moderate")
                seg = self._apply_emphasis(seg, level)

            elif token.type == "emotion":
                seg = self._tts_segment(token.value)
                seg = self._apply_emotion(seg, token.attrs.get("type", "neutral"))

            elif token.type == "prosody":
                seg = self._tts_segment(token.value)
                seg = self._apply_prosody(seg, token.attrs)

            elif token.type == "voice":
                seg = self._tts_segment(token.value)

            elif token.type == "say-as":
                seg = self._tts_segment(token.value)

            if seg:
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

    def _tts_segment(self, text: str) -> AudioSegment:
        raw_bytes = self.tts_service.synthesize_to_bytes(text)
        return AudioSegment.from_file(BytesIO(raw_bytes), format=self.format)

    def _apply_emphasis(self, audio: AudioSegment, level: str) -> AudioSegment:
        if level == "strong":
            return audio + 6
        elif level == "reduced":
            return audio - 3
        return audio

    def _apply_emotion(self, audio: AudioSegment, emotion: str) -> AudioSegment:
        emotion = emotion.lower()
        if emotion == "happy":
            return audio + 4
        elif emotion == "sad":
            return audio - 5
        elif emotion == "angry":
            return audio + 8
        elif emotion == "calm":
            return audio - 2
        return audio

    def _apply_prosody(self, audio: AudioSegment, attrs: dict) -> AudioSegment:
        rate = float(attrs.get("rate", 1.0))
        pitch = float(attrs.get("pitch", 0))
        new_frame_rate = int(audio.frame_rate * rate)
        modified = audio._spawn(audio.raw_data, overrides={"frame_rate": new_frame_rate})
        modified = modified.set_frame_rate(audio.frame_rate)
        if pitch > 0:
            modified += pitch * 1.5
        elif pitch < 0:
            modified -= abs(pitch) * 1.5
        return modified

    def _parse_duration(self, val: str) -> int:
        val = val.strip().lower()
        if val.endswith("ms"):
            return int(float(val[:-2]))
        if val.endswith("s"):
            return int(float(val[:-1]) * 1000)
        return int(float(val) * 1000)
