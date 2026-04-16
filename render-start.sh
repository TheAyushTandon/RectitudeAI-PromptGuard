#!/bin/bash
export PYTHONPATH=$PYTHONPATH:.
gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.gateway.main:app --bind 0.0.0.0:$PORT
