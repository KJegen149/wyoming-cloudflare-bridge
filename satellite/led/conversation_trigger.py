#!/usr/bin/env python3
"""Set conversation mode signal and clean up after timeout."""
import subprocess
import time
from pathlib import Path

SIGNAL_FILE = Path("/tmp/conversation_mode")
TIMEOUT = 15
PYTHON = "/home/kyle/wyoming-satellite/.venv/bin/python"

SIGNAL_FILE.touch()
print(f"Conversation window opened")

time.sleep(TIMEOUT)

if SIGNAL_FILE.exists():
    SIGNAL_FILE.unlink(missing_ok=True)
    subprocess.run([PYTHON, "/home/kyle/led/led_off.py"])
    print("Conversation window expired — LED cleared")
