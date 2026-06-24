#!/bin/sh
# download_model.sh - Download the Urdu Whisper model for offline use.
# Usage:
#   sh download_model.sh                          # default model
#   sh download_model.sh --output ./models        # custom cache path
#   sh download_model.sh my/custom-model-id       # specific model

set -e

MODEL="kingabzpro/whisper-large-v3-turbo-urdu"
OUTPUT_DIR=""

while [ $# -gt 0 ]; do
    case "$1" in
        --output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --*)
            echo "Unknown option: $1"
            exit 1
            ;;
        *)
            MODEL="$1"
            shift
            ;;
    esac
done

echo "Downloading model: $MODEL"
echo "This will download ~1.6 GB. Please allow a few minutes."
echo ""

if [ -n "$OUTPUT_DIR" ]; then
    mkdir -p "$OUTPUT_DIR"
    export HF_HOME="$(cd "$OUTPUT_DIR" && pwd)"
    echo "Caching to: $HF_HOME"
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_PYTHON="$SCRIPT_DIR/venv/Scripts/python.exe"

if [ -f "$SCRIPT_DIR/venv/bin/python" ]; then
    VENV_PYTHON="$SCRIPT_DIR/venv/bin/python"
fi

if [ ! -f "$VENV_PYTHON" ]; then
    echo "[ERROR] Virtual environment not found."
    echo "        Run setup_env.sh first."
    exit 1
fi

"$VENV_PYTHON" "$SCRIPT_DIR/src/download_model.py"
