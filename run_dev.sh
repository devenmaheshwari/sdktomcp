#!/usr/bin/env bash
export PYTHONPATH=$(pwd)
uvicorn server.app:app --reload --port 8000