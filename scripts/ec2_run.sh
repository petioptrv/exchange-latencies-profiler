#!/bin/bash

cd ~/exchange-latencies-profiler || retrn

source venv/bin/activate
PYTHONPATH=./ python src/profiler_app.py
