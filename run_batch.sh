#!/bin/sh
# run_batch.sh - Batch transcribe all audio files in a folder.
# Usage:
#   sh run_batch.sh <folder>                  [default: txt format]
#   sh run_batch.sh <folder> <format>         txt | json

set -e

echo ""
echo "============================================================"
echo "   Urdu Speech-to-Text  Batch Transcription  v2"
echo "============================================================"
echo ""

# Paths
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_PYTHON="$SCRIPT_DIR/venv/Scripts/python.exe"
TRANSCRIBE_PY="$SCRIPT_DIR/src/transcribe.py"

# On Linux/Mac
if [ -f "$SCRIPT_DIR/venv/bin/python" ]; then
    VENV_PYTHON="$SCRIPT_DIR/venv/bin/python"
fi

# Check venv Python exists
if [ ! -f "$VENV_PYTHON" ]; then
    echo "[ERROR] Virtual environment not found."
    echo "        Expected: $VENV_PYTHON"
    echo "        Please run setup_env.sh first."
    exit 1
fi

echo "[OK]  Found Python: $VENV_PYTHON"
echo ""

# Show usage if no argument given
if [ -z "$1" ]; then
    echo "Usage:"
    echo "  sh run_batch.sh <folder>             [default: txt format]"
    echo "  sh run_batch.sh <folder> <format>    txt | json"
    echo ""
    echo "Examples:"
    echo '  sh run_batch.sh ./MyAudio/'
    echo '  sh run_batch.sh ./podcasts/ json'
    echo '  sh run_batch.sh "/path/to/Lectures/" json'
    echo ''
    exit 0
fi

FOLDER="$1"
FORMAT="${2:-txt}"

echo "[1/2] Processing folder: $FOLDER"
echo "[2/2] Output format:     $FORMAT"
echo ""
echo "Starting batch transcription..."
echo ""

"$VENV_PYTHON" "$TRANSCRIBE_PY" batch "$FOLDER" -f "$FORMAT"

echo ""
echo "============================================================"
echo "   [OK] Batch transcription complete!"
echo "============================================================"
echo ""
