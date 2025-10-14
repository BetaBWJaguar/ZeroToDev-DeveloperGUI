# -*- coding: utf-8 -*-
import re
from io import BytesIO
from pydub import AudioSegment

from data_manager.MemoryManager import MemoryManager
from markup.MarkupManagerUtility import MarkupManagerUtility
from logs_manager.LogsManager import LogsManager
from markup.VoiceCharacterManager import VoiceCharacterManager
from markup.utils.SayAsTagManager import SayAsTagManager


class MarkupManager:
    def __init__(self, tts_service, default_format="mp3"):
        self.tts_service = tts_service
        self.format = default_format
        self.parser = MarkupManagerUtility()
        self.character_manager = VoiceCharacterManager()
        self.logger = LogsManager.get_logger("MarkupManager")
        locale = MemoryManager.get("tts_lang", "en")
        self.sayas_manager = SayAsTagManager(locale)


    def synthesize_with_markup(self, text: str, progress_cb=None) -> bytes:
        if not text or not text.strip():
            raise ValueError("Empty text provided to MarkupManager.")

        tokens = self.parser.parse(text)
        self.parser.debug_tokens(tokens)

        combined = AudioSegment.silent(duration=0)
        pos = 0

        pattern = re.compile(
            r'(<(emphasis|prosody|style|say-as).*?>.*?</\2>|<break.*?>)',
            re.DOTALL | re.IGNORECASE
        )

        total_len = len(text.strip())
        processed_len = 0

        def update_progress(local_msg: str = ""):
            if progress_cb:
                pct = min(100, int((processed_len / total_len) * 100))
                progress_cb(pct, f"Processing markup… {pct}% {local_msg}")

        for match in pattern.finditer(text):
            start, end = match.span()

            plain = text[pos:start]
            if plain and plain.strip():
                raw = self.tts_service.synthesize_to_bytes(plain.strip())
                audio = AudioSegment.from_file(BytesIO(raw), format=self.format)
                combined += audio
                processed_len += len(plain.strip())
                update_progress("plain segment")

            seg = match.group(0)
            if not seg or not seg.strip():
                pos = end
                continue

            if "<break" in seg:
                ms = self._parse_duration(seg)
                combined += AudioSegment.silent(duration=ms)

            elif "<emphasis" in seg:
                inner = self._extract_inner(seg)
                if inner:
                    raw = self.tts_service.synthesize_to_bytes(inner)
                    audio = AudioSegment.from_file(BytesIO(raw), format=self.format)
                    level = self._get_attr(seg, "level", "moderate")
                    combined += self._apply_emphasis(audio, level)
                    processed_len += len(inner.strip())
                    update_progress(f"emphasis:{level}")

            elif "<style" in seg:
                inner = self._extract_inner(seg)
                if inner:
                    raw = self.tts_service.synthesize_to_bytes(inner)
                    audio = AudioSegment.from_file(BytesIO(raw), format=self.format)
                    style = self._get_attr(seg, "type", "neutral")
                    combined += self._apply_style(audio, style)
                    processed_len += len(inner.strip())
                    update_progress(f"style:{style}")

            elif "<prosody" in seg:
                inner = self._extract_inner(seg)
                if inner:
                    raw = self.tts_service.synthesize_to_bytes(inner)
                    audio = AudioSegment.from_file(BytesIO(raw), format=self.format)
                    rate = self._get_attr(seg, "rate", "1.0")
                    pitch = self._get_attr(seg, "pitch", "0")
                    combined += self._apply_prosody(audio, {"rate": rate, "pitch": pitch})
                    processed_len += len(inner.strip())
                    update_progress(f"prosody")

            elif "<say-as" in seg:
                inner = self._extract_inner(seg)
                if inner:
                    interpret_as = self._get_attr(seg, "interpret-as", "text")
                    transformed = self.sayas_manager.interpret(inner, interpret_as)

                    raw = self.tts_service.synthesize_to_bytes(transformed)
                    audio = AudioSegment.from_file(BytesIO(raw), format=self.format)
                    combined += audio
                    processed_len += len(inner.strip())
                    update_progress(f"say-as:{interpret_as}")

            pos = end

        if pos < len(text):
            plain = text[pos:]
            if plain and plain.strip():
                raw = self.tts_service.synthesize_to_bytes(plain.strip())
                combined += AudioSegment.from_file(BytesIO(raw), format=self.format)
                processed_len += len(plain.strip())
                update_progress("final segment")

        update_progress("complete")

        buf = BytesIO()
        combined.export(buf, format=self.format)
        buf.seek(0)
        return buf.read()

    def _extract_inner(self, seg: str) -> str:
        inner = re.sub(r"<.*?>", "", seg)
        return inner.strip()

    def _parse_duration(self, seg: str) -> int:
        dur = re.search(r'time="(.*?)"', seg)
        if not dur:
            return 1000
        val = dur.group(1).strip().lower()
        if val.endswith("ms"):
            return int(float(val[:-2]))
        if val.endswith("s"):
            return int(float(val[:-1]) * 1000)
        try:
            return int(float(val) * 1000)
        except ValueError:
            return 1000

    def _get_attr(self, text: str, attr: str, default: str) -> str:
        match = re.search(rf'{attr}="(.*?)"', text)
        return match.group(1) if match else default

    def _apply_emphasis(self, audio: AudioSegment, level: str) -> AudioSegment:
        if level == "strong":
            return audio + 6
        elif level == "reduced":
            return audio - 3
        return audio

    def _apply_style(self, audio: AudioSegment, style: str) -> AudioSegment:
        return self.character_manager.apply(audio, style)

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
