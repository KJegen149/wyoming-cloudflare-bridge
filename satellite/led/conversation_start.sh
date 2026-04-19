#!/bin/bash
/home/kyle/wyoming-satellite/.venv/bin/python /home/kyle/led/led_ready.py
nohup /home/kyle/wyoming-satellite/.venv/bin/python /home/kyle/led/conversation_trigger.py >/dev/null 2>&1 &
