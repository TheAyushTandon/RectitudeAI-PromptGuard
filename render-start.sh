#!/bin/bash
export PYTHONPATH=$PYTHONPATH:.
# Reduced workers to 1 and added memory optimization flags for Uvicorn
gunicorn -w 1 -k uvicorn.workers.UvicornWorker backend.gateway.main:app --bind 0.0.0.0:$PORT --timeout 120
