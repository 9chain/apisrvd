#!/usr/bin/env bash

while :; do
    uptime >> app.log 
    echo "start app.py" >> app.log 
    python3 app.py >> app.log 2>&1
    sleep 5
done
