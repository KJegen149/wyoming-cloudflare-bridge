#!/usr/bin/env python3
import asyncio
import logging
import time
from pathlib import Path

from wyoming.event import async_read_event, async_write_event
from wyoming.wake import Detect, Detection

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
_LOGGER = logging.getLogger(__name__)

OWW_HOST = "localhost"
OWW_PORT = 10400
PROXY_PORT = 10401
SIGNAL_FILE = Path("/tmp/conversation_mode")
CONVERSATION_TIMEOUT = 15.0


async def handle_satellite(sat_reader, sat_writer):
    _LOGGER.info("Satellite connected")
    try:
        oww_reader, oww_writer = await asyncio.open_connection(OWW_HOST, OWW_PORT)
    except Exception as e:
        _LOGGER.error(f"Cannot connect to openWakeWord: {e}")
        sat_writer.close()
        return

    async def sat_to_oww():
        try:
            while True:
                event = await async_read_event(sat_reader)
                if event is None:
                    break
                if Detect.is_type(event.type) and SIGNAL_FILE.exists():
                    age = time.time() - SIGNAL_FILE.stat().st_mtime
                    if age < CONVERSATION_TIMEOUT:
                        _LOGGER.info("Conversation mode — auto-triggering after echo delay")
                        SIGNAL_FILE.unlink(missing_ok=True)
                        await asyncio.sleep(3)
                        detection = Detection(name="jarvis", timestamp=0)
                        await async_write_event(detection.event(), sat_writer)
                        continue
                    else:
                        _LOGGER.info("Conversation window expired")
                        SIGNAL_FILE.unlink(missing_ok=True)
                await async_write_event(event, oww_writer)
        except Exception as e:
            _LOGGER.debug(f"sat_to_oww ended: {e}")

    async def oww_to_sat():
        try:
            while True:
                event = await async_read_event(oww_reader)
                if event is None:
                    break
                await async_write_event(event, sat_writer)
        except Exception as e:
            _LOGGER.debug(f"oww_to_sat ended: {e}")

    await asyncio.gather(sat_to_oww(), oww_to_sat())
    oww_writer.close()
    sat_writer.close()
    _LOGGER.info("Satellite disconnected")


async def main():
    server = await asyncio.start_server(handle_satellite, "0.0.0.0", PROXY_PORT)
    _LOGGER.info(f"Conversation proxy listening on port {PROXY_PORT}")
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
