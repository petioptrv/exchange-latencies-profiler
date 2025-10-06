#!/bin/bash

cd ~/exchange-latencies-profiler || retrn

source venv/bin/activate
#PYTHONPATH=./ python src/server_app.py
uvicorn src.server_app:app --host 127.0.0.1 --port 8000 --workers 2
