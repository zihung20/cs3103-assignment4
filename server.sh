#!/usr/bin/env bash
set -euo pipefail

compose="docker compose"

# 1) stop everything
$compose down --remove-orphans

# 2) start receiver
$compose up -d receiver

# 3) follow logs until you Ctrl-C
echo "=== Following receiver logs (Ctrl-C to stop tail, container keeps running) ==="
$compose logs -f receiver
