#!/bin/bash

# logfile="sender.log"

# echo "Running sender-slow... output will be saved to $logfile"
# docker compose run --rm sender-slow 2>&1 | tee "$logfile"

logfile="sender.log"

echo "Running sender... output will be saved to $logfile"
docker compose run --rm sender 2>&1 | tee "$logfile"