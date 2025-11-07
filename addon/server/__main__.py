#!/usr/bin/env python3
"""
Wyoming Protocol Bridge to Cloudflare Workers AI
Provides STT and TTS services for Home Assistant Wyoming Satellites
"""

import argparse
import asyncio
import logging
from functools import partial
from pathlib import Path

from wyoming.info import AsrModel, AsrProgram, Attribution, Info, TtsProgram, TtsVoice
from wyoming.server import AsyncServer

from .handler import CloudflareEventHandler

_LOGGER = logging.getLogger(__name__)


async def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Wyoming Cloudflare Bridge")
    parser.add_argument(
        "--uri",
        default="tcp://0.0.0.0:10300",
        help="URI to listen on (default: tcp://0.0.0.0:10300)",
    )
    parser.add_argument(
        "--stt-url",
        required=True,
        help="URL of the Cloudflare STT worker",
    )
    parser.add_argument(
        "--tts-url",
        required=True,
        help="URL of the Cloudflare TTS worker",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Log level (default: INFO)",
    )
    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Create Wyoming info
    wyoming_info = Info(
        asr=[
            AsrProgram(
                name="cloudflare-whisper",
                description="Cloudflare Workers AI Whisper",
                attribution=Attribution(
                    name="OpenAI Whisper via Cloudflare",
                    url="https://developers.cloudflare.com/workers-ai/",
                ),
                installed=True,
                version="1.0.0",
                models=[
                    AsrModel(
                        name="whisper",
                        description="Whisper speech recognition model",
                        attribution=Attribution(
                            name="OpenAI",
                            url="https://github.com/openai/whisper",
                        ),
                        installed=True,
                        version="1.0.0",
                        languages=["en", "es", "fr", "de", "it", "pt", "nl", "pl", "ru", "ja", "ko", "zh"],
                    )
                ],
            )
        ],
        tts=[
            TtsProgram(
                name="cloudflare-aura",
                description="Cloudflare Workers AI Deepgram Aura",
                attribution=Attribution(
                    name="Deepgram Aura via Cloudflare",
                    url="https://developers.cloudflare.com/workers-ai/",
                ),
                installed=True,
                version="1.0.0",
                voices=[
                    TtsVoice(
                        name="aura-en",
                        description="Deepgram Aura English voice",
                        attribution=Attribution(
                            name="Deepgram",
                            url="https://deepgram.com/",
                        ),
                        installed=True,
                        version="1.0.0",
                        languages=["en"],
                    )
                ],
            )
        ],
    )

    _LOGGER.info("Starting Wyoming Cloudflare Bridge")
    _LOGGER.info(f"STT URL: {args.stt_url}")
    _LOGGER.info(f"TTS URL: {args.tts_url}")
    _LOGGER.info(f"Listening on: {args.uri}")

    # Start server
    try:
        server = AsyncServer.from_uri(args.uri)
        _LOGGER.info("Server created successfully")
        _LOGGER.info(f"Server type: {type(server)}")
        _LOGGER.info(f"Server URI: {server.uri if hasattr(server, 'uri') else 'unknown'}")

        _LOGGER.info("Starting server loop...")

        # Run server with handler factory
        handler_factory = partial(
            CloudflareEventHandler,
            wyoming_info,
            args.stt_url,
            args.tts_url,
        )

        _LOGGER.info("Calling server.run()...")
        result = await server.run(handler_factory)
        _LOGGER.warning(f"Server.run() returned unexpectedly with: {result}")

        # Keep alive if server exits
        _LOGGER.info("Entering keep-alive loop...")
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        _LOGGER.info("Shutting down...")
    except Exception as e:
        _LOGGER.error(f"Server error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
