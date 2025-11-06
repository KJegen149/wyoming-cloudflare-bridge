"""Wyoming event handler for Cloudflare Workers AI."""

import asyncio
import io
import logging
import wave
from typing import Optional

import aiohttp
from wyoming.asr import Transcribe, Transcript
from wyoming.audio import AudioChunk, AudioStart, AudioStop
from wyoming.event import Event
from wyoming.info import Describe, Info
from wyoming.server import AsyncEventHandler
from wyoming.tts import Synthesize

_LOGGER = logging.getLogger(__name__)


class CloudflareEventHandler(AsyncEventHandler):
    """Event handler for Wyoming protocol with Cloudflare Workers AI."""

    def __init__(
        self,
        wyoming_info: Info,
        stt_url: str,
        tts_url: str,
        *args,
        **kwargs,
    ) -> None:
        """Initialize handler."""
        super().__init__(*args, **kwargs)
        self.wyoming_info = wyoming_info
        self.stt_url = stt_url
        self.tts_url = tts_url
        self.client_id = str(id(self))

        # Audio recording state
        self._audio_buffer: Optional[io.BytesIO] = None
        self._wav_writer: Optional[wave.Wave_write] = None
        self._is_recording = False
        self._sample_rate = 16000
        self._sample_width = 2
        self._channels = 1

    async def handle_event(self, event: Event) -> bool:
        """Handle Wyoming protocol events."""
        _LOGGER.debug(f"Received event: {event}")

        if Describe.is_type(event.type):
            # Send server info
            await self.write_event(self.wyoming_info.event())
            return True

        if AudioStart.is_type(event.type):
            # Start audio recording
            audio_start = AudioStart.from_event(event)
            await self._handle_audio_start(
                audio_start.rate,
                audio_start.width,
                audio_start.channels,
            )
            return True

        if AudioChunk.is_type(event.type):
            # Accumulate audio data
            chunk = AudioChunk.from_event(event)
            await self._handle_audio_chunk(chunk)
            return True

        if AudioStop.is_type(event.type):
            # Process audio for transcription
            await self._handle_audio_stop()
            return True

        if Transcribe.is_type(event.type):
            # Explicit transcription request
            _LOGGER.debug("Transcribe event received")
            return True

        if Synthesize.is_type(event.type):
            # Text-to-speech request
            synthesize = Synthesize.from_event(event)
            await self._handle_synthesize(synthesize.text)
            return True

        return True

    async def _handle_audio_start(
        self, sample_rate: int, audio_width: int, audio_channels: int
    ) -> None:
        """Start recording audio."""
        _LOGGER.debug(
            f"Audio start: rate={sample_rate}, width={audio_width}, channels={audio_channels}"
        )

        self._sample_rate = sample_rate
        self._sample_width = audio_width
        self._channels = audio_channels
        self._is_recording = True

        # Create WAV buffer
        self._audio_buffer = io.BytesIO()
        self._wav_writer = wave.open(self._audio_buffer, "wb")
        self._wav_writer.setnchannels(audio_channels)
        self._wav_writer.setsampwidth(audio_width)
        self._wav_writer.setframerate(sample_rate)

    async def _handle_audio_chunk(self, chunk: AudioChunk) -> None:
        """Accumulate audio chunk."""
        if self._is_recording and chunk.audio and self._wav_writer:
            self._wav_writer.writeframes(chunk.audio)

    async def _handle_audio_stop(self) -> None:
        """Process accumulated audio for transcription."""
        if not self._is_recording or not self._audio_buffer:
            _LOGGER.warning("Audio stop received but not recording")
            return

        self._is_recording = False

        # Finalize WAV file
        if self._wav_writer:
            self._wav_writer.close()
            self._wav_writer = None

        # Get audio data
        audio_data = self._audio_buffer.getvalue()
        self._audio_buffer = None

        if not audio_data:
            _LOGGER.warning("No audio data to transcribe")
            return

        _LOGGER.info(f"Transcribing {len(audio_data)} bytes of audio")

        try:
            # Send to Cloudflare Workers AI
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.stt_url,
                    data=audio_data,
                    headers={"Content-Type": "audio/wav"},
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        text = result.get("text", "")
                        _LOGGER.info(f"Transcription: {text}")

                        # Send transcript back
                        await self.write_event(
                            Transcript(text=text).event()
                        )
                    else:
                        error_text = await response.text()
                        _LOGGER.error(
                            f"STT failed with status {response.status}: {error_text}"
                        )
                        # Send empty transcript on error
                        await self.write_event(Transcript(text="").event())

        except asyncio.TimeoutError:
            _LOGGER.error("STT request timed out")
            await self.write_event(Transcript(text="").event())
        except Exception as e:
            _LOGGER.error(f"STT error: {e}", exc_info=True)
            await self.write_event(Transcript(text="").event())

    async def _handle_synthesize(self, text: str) -> None:
        """Synthesize speech from text."""
        _LOGGER.info(f"Synthesizing: {text}")

        try:
            # Send to Cloudflare Workers AI
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.tts_url,
                    json={"text": text},
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    if response.status == 200:
                        audio_data = await response.read()
                        _LOGGER.info(f"Received {len(audio_data)} bytes of audio")

                        # Parse WAV to get audio parameters
                        audio_buffer = io.BytesIO(audio_data)
                        with wave.open(audio_buffer, "rb") as wav_file:
                            sample_rate = wav_file.getframerate()
                            sample_width = wav_file.getsampwidth()
                            channels = wav_file.getnchannels()
                            audio_bytes = wav_file.readframes(wav_file.getnframes())

                        # Send audio start event
                        await self.write_event(
                            AudioStart(
                                rate=sample_rate,
                                width=sample_width,
                                channels=channels,
                            ).event()
                        )

                        # Send audio in chunks (16KB chunks)
                        chunk_size = 16384
                        for i in range(0, len(audio_bytes), chunk_size):
                            chunk = audio_bytes[i:i + chunk_size]
                            await self.write_event(
                                AudioChunk(
                                    audio=chunk,
                                    rate=sample_rate,
                                    width=sample_width,
                                    channels=channels,
                                ).event()
                            )

                        # Send audio stop event
                        await self.write_event(AudioStop().event())
                    else:
                        error_text = await response.text()
                        _LOGGER.error(
                            f"TTS failed with status {response.status}: {error_text}"
                        )

        except asyncio.TimeoutError:
            _LOGGER.error("TTS request timed out")
        except Exception as e:
            _LOGGER.error(f"TTS error: {e}", exc_info=True)
