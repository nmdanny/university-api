#! /usr/bin/env bash

# Let the DB start
python /app/app/backend_pre_start.py


# Run migrations
alembic upgrade head

# Create initial data in DB
python /app/app/initial_data.py

# serialize and populate DB
python /app/app/serializer/json_serializer.py