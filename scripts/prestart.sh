#! /usr/bin/env bash

set -e
set -x

# Let the DB start
PYTHONPATH=./:$PYTHONPATH python src/pre_start.py

# Run migrations
alembic upgrade head

PYTHONPATH=./:$PYTHONPATH python src/initial_data.py