#!/bin/bash

logfile="sender.log"
sender_type="sender-slow"

echo "Running $sender_type... output will be saved to $logfile"
docker compose run --rm $sender_type 2>&1 | tee "$logfile"