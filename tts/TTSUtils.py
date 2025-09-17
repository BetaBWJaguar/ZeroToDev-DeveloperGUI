from io import BytesIO
from pydub import AudioSegment
import simpleaudio as sa
from data_manager.DataManager import DataManager

class TTSUtils:
    @staticmethod
    def preview(audio_bytes: bytes, seconds: int = 20, play_audio: bool = True) -> bytes:
        try:
            audio = AudioSegment.from_file(BytesIO(audio_bytes), format="mp3")

            preview = audio[:seconds * 1000]
            out_buf = BytesIO()
            preview.export(out_buf, format="mp3")
            out_buf.seek(0)

            mem_buf = DataManager.write_to_memory(out_buf.read())
            preview_bytes = DataManager.read_from_memory(mem_buf)

            if play_audio:
                play_obj = sa.play_buffer(
                    preview.raw_data,
                    num_channels=preview.channels,
                    bytes_per_sample=preview.sample_width,
                    sample_rate=preview.frame_rate
                )
                play_obj.wait_done()

            return preview_bytes

        except Exception as e:
            print(f"[TTSUtils.preview] Error: {e}")
            return b""
