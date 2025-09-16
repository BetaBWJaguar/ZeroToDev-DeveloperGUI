# -*- coding: utf-8 -*-
import io
from pydub import AudioSegment, effects
from data_manager.DataManager import DataManager

class VoiceProcessor:
    @staticmethod
    def apply(audio: AudioSegment, settings: dict) -> AudioSegment:
        original_frame_rate = audio.frame_rate

        if settings.get("volume") != 1.0:
                audio += (settings["volume"] - 1.0) * 10

        if settings.get("speed") != 1.0:
            new_frame_rate = int(audio.frame_rate * settings["speed"])
            audio = audio._spawn(audio.raw_data, overrides={"frame_rate": new_frame_rate})
            audio = audio.set_frame_rate(44100)

        if settings.get("pitch") != 0:
            semitones = settings["pitch"]
            new_sample_rate = int(audio.frame_rate * (2.0 ** (semitones / 12.0)))
            audio = audio._spawn(audio.raw_data, overrides={"frame_rate": new_sample_rate})
            audio = audio.set_frame_rate(44100)

        if settings.get("echo"):
            echo = audio - 6
            audio = audio.overlay(echo, position=250)
            audio = audio.overlay(echo - 2, position=500)

        if settings.get("reverb"):
            audio_with_reverb = audio - 3
            for delay_ms in [50, 100, 150, 200]:
                echo = audio - (delay_ms / 20)

                audio_with_reverb = audio_with_reverb.overlay(echo, position=delay_ms)
                audio = audio_with_reverb
                audio = effects.normalize(audio)
        if settings.get("robot"):

            new_frame_rate = int(audio.frame_rate * 0.9)
            audio = audio._spawn(audio.raw_data, overrides={"frame_rate": new_frame_rate})
            audio = audio.set_frame_rate(original_frame_rate)

            audio = audio.high_pass_filter(300)
            audio = audio.low_pass_filter(3000)

            delayed_version = AudioSegment.silent(duration=10).append(audio, crossfade=0)
            audio = audio.overlay(delayed_version)
            audio = effects.normalize(audio)
        return audio

    @staticmethod
    def process_from_memory(data: bytes, fmt: str, settings: dict, return_audio: bool = False):
        try:
            audio = DataManager.from_bytes(data, fmt)
        except Exception as e:
            raise ValueError(f"Invalid input data or format ({fmt}): {e}")

        processed = VoiceProcessor.apply(audio, settings)

        if return_audio:
            return processed

        buf = io.BytesIO()
        processed.export(buf, format=fmt)
        buf.seek(0)
        return buf.read()

