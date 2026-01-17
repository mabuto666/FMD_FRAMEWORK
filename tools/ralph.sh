#!/usr/bin/env bash
set -euo pipefail
export DISPATCH_PATH="${DISPATCH_PATH:-contracts/dispatch.json}"
python3 tools/ralph.py
