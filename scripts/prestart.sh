#! /usr/bin/env bash

set -e
set -x

# Let the DB start
python src/pre_start.py

# Run migrations
alembic upgrade head

# Create initial data in DB
PYTHONPATH=./:$PYTHONPATH python src/initial_data.py