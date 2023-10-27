#!/bin/bash

# Start the first process
python worker.py >> ./logs/worker.log 2>&1 &


# Start the second process
uvicorn main:app --host 0.0.0.0 --port 8000 >> ./logs/api.log 2>&1 &

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?