#!/bin/bash
# Doc2Md Portable Launcher for Unix (macOS/Linux)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH}"

# Try virtual environment Python first, then system Python
if [ -f "${SCRIPT_DIR}/.venv/bin/python" ]; then
    "${SCRIPT_DIR}/.venv/bin/python" "${SCRIPT_DIR}/scripts/converter.py" "$@"
else
    python "${SCRIPT_DIR}/scripts/converter.py" "$@"
fi
