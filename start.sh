#!/bin/bash
# Start script for ReservationAPI
echo "Starting ReservationAPI..."
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
