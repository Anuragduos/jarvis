from __future__ import annotations


class SpeechToTextAdapter:
    def __init__(self, provider: str = "whisper") -> None:
        self.provider = provider

    def transcribe(self, audio_path: str) -> str:
        # Integrate Vosk/Whisper local engines here.
        return f"transcribed text from {audio_path} via {self.provider}"


class TextToSpeechAdapter:
    def speak(self, text: str) -> None:
        del text
        # Hook platform TTS or external provider.
