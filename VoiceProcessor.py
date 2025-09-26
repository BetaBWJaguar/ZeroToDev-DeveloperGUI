# -*- coding: utf-8 -*-
import io
from datetime import time

from pydub import AudioSegment, effects
from data_manager.DataManager import DataManager
from logs_manager.LogsManager import LogsManager
from logs_manager.LogsHelperManager import LogsHelperManager

class VoiceProcessor:
    logger = LogsManager.get_logger("VoiceProcessor")
    @staticmethod
    def apply(audio: AudioSegment, settings: dict) -> AudioSegment:
        original_frame_rate = audio.frame_rate

        if settings.get("volume") != 1.0:
            volume_level = settings.get("volume", 1.0)
            LogsHelperManager.log_debug(VoiceProcessor.logger, "APPLY_VOLUME", {"value": volume_level})
            audio += (volume_level - 1.0) * 10

        if settings.get("speed") != 1.0:
            speed_rate = settings.get("speed", 1.0)
            new_frame_rate = int(audio.frame_rate * settings["speed"])
            audio = audio._spawn(audio.raw_data, overrides={"frame_rate": new_frame_rate})
            LogsHelperManager.log_debug(VoiceProcessor.logger, "APPLY_SPEED", {"rate": speed_rate})
            audio = audio.set_frame_rate(44100)

        if settings.get("pitch") != 0:
            semitones = settings.get("pitch", 0)
            LogsHelperManager.log_debug(VoiceProcessor.logger, "APPLY_PITCH", {"semitones": semitones})
            new_sample_rate = int(audio.frame_rate * (2.0 ** (semitones / 12.0)))
            audio = audio._spawn(audio.raw_data, overrides={"frame_rate": new_sample_rate})
            audio = audio.set_frame_rate(44100)

        if settings.get("echo"):
            LogsHelperManager.log_debug(VoiceProcessor.logger, "APPLY_ECHO", {"enabled": True})
            echo = audio - 6
            audio = audio.overlay(echo, position=250)
            audio = audio.overlay(echo - 2, position=500)

        if settings.get("reverb"):
            LogsHelperManager.log_debug(VoiceProcessor.logger, "APPLY_REVERB", {"enabled": True})
            audio_with_reverb = audio - 3
            for delay_ms in [50, 100, 150, 200]:
                echo = audio - (delay_ms / 20)

                audio_with_reverb = audio_with_reverb.overlay(echo, position=delay_ms)
                audio = audio_with_reverb
                audio = effects.normalize(audio)
        if settings.get("robot"):

            LogsHelperManager.log_debug(VoiceProcessor.logger, "APPLY_ROBOT", {"enabled": True})
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
        start_time = time.time()

        LogsHelperManager.log_event(
            VoiceProcessor.logger,
            "VOICE_PROCESS_START",
            {"input_bytes": len(data), "format": fmt, "settings": settings}
        )

        try:
            audio = DataManager.from_bytes(data, fmt)
            LogsHelperManager.log_debug(VoiceProcessor.logger, "AUDIO_LOADED_FROM_BYTES", {"size": len(data)})
        except Exception as e:
            LogsHelperManager.log_error(
                VoiceProcessor.logger,
                "VOICE_PROCESS_LOAD_FAILURE",
                f"Format: {fmt}, Error: {str(e)}"
            )
            raise ValueError(f"Invalid input data or format ({fmt}): {e}")

        processed = VoiceProcessor.apply(audio, settings)

        if return_audio:
            duration = time.time() - start_time
            LogsHelperManager.log_performance(
                VoiceProcessor.logger, "PROCESS_FROM_MEMORY_RETURN_AUDIO", duration,
                {"input_bytes": len(data)}
            )
            return processed

        buf = io.BytesIO()
        processed.export(buf, format=fmt)
        buf.seek(0)
        output_bytes = buf.read()

        duration = time.time() - start_time
        LogsHelperManager.log_performance(
            VoiceProcessor.logger,
            "PROCESS_FROM_MEMORY_SUCCESS",
            duration,
            {"input_bytes": len(data), "output_bytes": len(output_bytes)}
        )

        return output_bytes