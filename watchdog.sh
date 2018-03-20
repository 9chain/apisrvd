#!/usr/bin/env bash

while :; do
    python3 app.py >> app.log 2>&1
    sleep 5
done