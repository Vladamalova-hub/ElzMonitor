#!/bin/bash
set -e
cd "$(dirname "$0")"
python3 -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} &
python3 bot_main.py
