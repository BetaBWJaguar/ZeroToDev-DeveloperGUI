# -*- coding: utf-8 -*-
from pydub import AudioSegment
from pydub.effects import low_pass_filter, high_pass_filter
from logs_manager.LogsManager import LogsManager


class VoiceCharacterManager:
    def __init__(self):
        self.logger = LogsManager.get_logger("VoiceCharacterManager")


        self.CHARACTER_PROFILE = {
            "radio": {
                "gain": +4, "pause": 50, "softness": 1.0,
                "warmth": 1.2, "clarity": 1.4, "tempo_shift": 1.08
            },
            "storyteller": {
                "gain": +1, "pause": 180, "softness": 0.9,
                "warmth": 1.1, "clarity": 1.0, "tempo_shift": 0.95
            },
            "robotic": {
                "gain": +2, "pause": 60, "softness": 1.3,
                "warmth": 0.7, "clarity": 1.6, "tempo_shift": 1.0
            },
            "deep": {
                "gain": +3, "pause": 220, "softness": 0.85,
                "warmth": 1.4, "clarity": 0.8, "tempo_shift": 0.9
            },
            "soft": {
                "gain": -1, "pause": 200, "softness": 0.8,
                "warmth": 1.05, "clarity": 0.9, "tempo_shift": 0.92
            },
            "cinematic": {
                "gain": +5, "pause": 100, "softness": 1.1,
                "warmth": 1.2, "clarity": 1.3, "tempo_shift": 1.05
            },
            "narrator": {
                "gain": +2, "pause": 140, "softness": 0.95,
                "warmth": 1.0, "clarity": 1.0, "tempo_shift": 1.0
            },
            "energetic": {
                "gain": +6, "pause": 40, "softness": 1.0,
                "warmth": 1.1, "clarity": 1.2, "tempo_shift": 1.15
            },
        }

    def apply(self, audio: AudioSegment, style: str) -> AudioSegment:
        style = (style or "narrator").lower().strip()
        profile = self.CHARACTER_PROFILE.get(style, self.CHARACTER_PROFILE["narrator"])

        audio = audio + profile["gain"]

        if profile["softness"] < 1.0:
            audio = audio.fade_in(30).fade_out(30)


        if profile["warmth"] > 1.0:
            audio = low_pass_filter(audio, int(4500 * profile["warmth"]))
        elif profile["clarity"] > 1.0:
            audio = high_pass_filter(audio, int(3000 * profile["clarity"]))


        if profile["tempo_shift"] != 1.0:
            new_rate = int(audio.frame_rate * profile["tempo_shift"])
            audio = audio._spawn(audio.raw_data, overrides={"frame_rate": new_rate})
            audio = audio.set_frame_rate(44100)


        pause = AudioSegment.silent(duration=profile["pause"])
        audio = audio + pause

        self.logger.debug(f"[Style] {style} applied → {profile}")
        return audio
