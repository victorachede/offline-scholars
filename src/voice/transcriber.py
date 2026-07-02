"""
Voice Transcriber — offline speech to text.
Uses faster-whisper (whisper-tiny) running entirely on CPU.
Supports English, Hausa, Yoruba, Igbo.
"""

import os
import tempfile
from pathlib import Path

try:
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

try:
    import sounddevice as sd
    import scipy.io.wavfile as wavfile
    import numpy as np
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

CACHE_DIR = Path(__file__).parent.parent.parent / "models" / "whisper"

SUPPORTED_LANGUAGES = {
    "English": "en",
    "Hausa": "ha",
    "Yoruba": "yo",
    "Igbo": "ig",
}


class VoiceTranscriber:
    def __init__(self, model_size: str = "tiny"):
        self._model = None
        self._model_size = model_size

    def _load(self):
        if self._model is not None:
            return
        if not WHISPER_AVAILABLE:
            raise RuntimeError("faster-whisper not installed. Run: pip install faster-whisper")
        print(f"Loading Whisper {self._model_size} model...")
        self._model = WhisperModel(
            self._model_size,
            device="cpu",
            compute_type="int8",
            download_root=str(CACHE_DIR),
        )
        print("Whisper loaded.")

    def transcribe_file(self, audio_path: str, language: str = "English") -> dict:
        """
        Transcribe an audio file to text.

        Args:
            audio_path: Path to WAV/MP3/M4A file
            language: One of "English", "Hausa", "Yoruba", "Igbo"

        Returns:
            {"text": str, "language": str, "duration": float}
        """
        self._load()
        lang_code = SUPPORTED_LANGUAGES.get(language, "en")

        segments, info = self._model.transcribe(
            audio_path,
            language=lang_code,
            beam_size=5,
            vad_filter=True,
        )

        text = " ".join(seg.text.strip() for seg in segments)
        return {
            "text": text,
            "language": info.language,
            "duration": info.duration,
        }

    def record_and_transcribe(self, duration: int = 5, language: str = "English") -> dict:
        """
        Record from microphone and transcribe.

        Args:
            duration: Recording duration in seconds
            language: Target language

        Returns:
            {"text": str, "language": str}
        """
        if not AUDIO_AVAILABLE:
            raise RuntimeError("sounddevice/scipy not installed. Run: pip install sounddevice scipy")

        print(f"Recording for {duration} seconds...")
        sample_rate = 16000
        audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype="float32")
        sd.wait()
        print("Recording complete. Transcribing...")

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            tmp_path = f.name
            wavfile.write(tmp_path, sample_rate, (audio * 32767).astype("int16"))

        try:
            result = self.transcribe_file(tmp_path, language)
        finally:
            os.unlink(tmp_path)

        return result

    def transcribe_bytes(self, audio_bytes: bytes, language: str = "English") -> dict:
        """Transcribe raw audio bytes (for Gradio integration)."""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_bytes)
            tmp_path = f.name
        try:
            return self.transcribe_file(tmp_path, language)
        finally:
            os.unlink(tmp_path)


if __name__ == "__main__":
    t = VoiceTranscriber()
    result = t.record_and_transcribe(duration=5, language="English")
    print(result["text"])
