#!/bin/sh
# run_transcribe.sh - Transcribe an Urdu audio file to text.
# Usage:
#   sh run_transcribe.sh <audio_file>                  Output as .txt (default)
#   sh run_transcribe.sh <audio_file> <output_txt>     Custom output path

set -e

echo ""
echo "============================================================"
echo "   Urdu Speech-to-Text Transcription  v2"
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
    echo "  sh run_transcribe.sh <audio_file>             [output as .txt]"
    echo "  sh run_transcribe.sh <audio_file> <output>    custom output path"
    echo ""
    echo "Examples:"
    echo '  sh run_transcribe.sh speech.mp3'
    echo '  sh run_transcribe.sh recording.wav result.txt'
    echo ''
    exit 0
fi

AUDIO_FILE="$1"
echo "[1/2] Processing: $AUDIO_FILE"
echo ""

# Run transcription
if [ -n "$2" ]; then
    "$VENV_PYTHON" "$TRANSCRIBE_PY" trans "$AUDIO_FILE" --output "$2"
else
    "$VENV_PYTHON" "$TRANSCRIBE_PY" trans "$AUDIO_FILE"
fi

echo ""
echo "============================================================"
echo "   [OK] Transcription complete!"
echo "============================================================"
echo ""
