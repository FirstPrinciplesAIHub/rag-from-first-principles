#!/usr/bin/env bash
set -euo pipefail

REQ_FILE="$(cd "$(dirname "$0")/.." && pwd)/requirements-dev.txt"
if [ ! -f "$REQ_FILE" ]; then
  echo "requirements-dev.txt not found at $REQ_FILE"
  exit 1
fi

# Use venv python if VIRTUAL_ENV is set, otherwise prefer python3
if [ -n "${VIRTUAL_ENV:-}" ]; then
  PYTHON="$VIRTUAL_ENV/bin/python"
else
  PYTHON="$(command -v python3 || command -v python || true)"
fi

if [ -z "$PYTHON" ]; then
  echo "No python executable found. Install Python 3 and try again."
  exit 1
fi

echo "Using python: $PYTHON"
"$PYTHON" -m pip install --upgrade pip
"$PYTHON" -m pip install -r "$REQ_FILE"

echo ""
echo "Done. Run tests with:"
echo "  source /path/to/your/venv/bin/activate  # if you use a virtualenv"
echo "  pytest -q"
