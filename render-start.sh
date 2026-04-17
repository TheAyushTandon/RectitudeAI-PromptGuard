#!/bin/bash
export PYTHONPATH=$PYTHONPATH:.
# Ensure demo database exists in production environment
python scripts/seed_demo_db.py
# Reduced workers to 1 and added memory optimization flags for Uvicorn
gunicorn -w 1 -k uvicorn.workers.UvicornWorker backend.gateway.main:app --bind 0.0.0.0:$PORT --timeout 120
