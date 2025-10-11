# -*- coding: utf-8 -*-
import re
from io import BytesIO
from pydub import AudioSegment
from markup.MarkupManagerUtility import MarkupManagerUtility
from logs_manager.LogsManager import LogsManager


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
        pos = 0

        pattern = re.compile(
            r'(<(emphasis|emotion|prosody).*?>.*?</\2>|<break.*?>)',
            re.DOTALL | re.IGNORECASE
        )

        for match in pattern.finditer(text):
            start, end = match.span()

            plain = text[pos:start].strip()
            if plain:
                raw = self.tts_service.synthesize_to_bytes(plain, progress_cb=progress_cb)
                combined += AudioSegment.from_file(BytesIO(raw), format=self.format)

            seg = match.group(0)

            if "<break" in seg:
                dur = re.search(r'time="(.*?)"', seg)
                ms = 1000
                if dur:
                    val = dur.group(1)
                    if val.endswith("ms"):
                        ms = int(float(val[:-2]))
                    elif val.endswith("s"):
                        ms = int(float(val[:-1]) * 1000)
                combined += AudioSegment.silent(duration=ms)

            elif "<emphasis" in seg:
                inner = re.sub(r"<.*?>", "", seg).strip()
                if inner:
                    raw = self.tts_service.synthesize_to_bytes(inner, progress_cb=progress_cb)
                    audio = AudioSegment.from_file(BytesIO(raw), format=self.format)
                    level = self._get_attr(seg, "level", "moderate")
                    audio = self._apply_emphasis(audio, level)
                    combined += audio

            elif "<emotion" in seg:
                inner = re.sub(r"<.*?>", "", seg).strip()
                if inner:
                    raw = self.tts_service.synthesize_to_bytes(inner, progress_cb=progress_cb)
                    audio = AudioSegment.from_file(BytesIO(raw), format=self.format)
                    emotion = self._get_attr(seg, "type", "neutral")
                    audio = self._apply_emotion(audio, emotion)
                    combined += audio

            elif "<prosody" in seg:
                inner = re.sub(r"<.*?>", "", seg).strip()
                if inner:
                    raw = self.tts_service.synthesize_to_bytes(inner, progress_cb=progress_cb)
                    audio = AudioSegment.from_file(BytesIO(raw), format=self.format)
                    rate = self._get_attr(seg, "rate", "1.0")
                    pitch = self._get_attr(seg, "pitch", "0")
                    audio = self._apply_prosody(audio, {"rate": rate, "pitch": pitch})
                    combined += audio

            pos = end

        if pos < len(text):
            plain = text[pos:].strip()
            if plain:
                raw = self.tts_service.synthesize_to_bytes(plain, progress_cb=progress_cb)
                combined += AudioSegment.from_file(BytesIO(raw), format=self.format)

        buf = BytesIO()
        combined.export(buf, format=self.format)
        buf.seek(0)
        return buf.read()

    def _get_attr(self, text: str, attr: str, default: str) -> str:
        match = re.search(rf'{attr}="(.*?)"', text)
        return match.group(1) if match else default

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
