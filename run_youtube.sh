#!/bin/sh
# run_youtube.sh - Download YouTube video audio and transcribe it to text.
# Usage:
#   sh run_youtube.sh <YouTube_URL>                    Urdu (default, auto-chunk for long videos)
#   sh run_youtube.sh <URL> -l en                      English transcription
#   sh run_youtube.sh <URL> -f json                     JSON output format
#   sh run_youtube.sh <URL> -m accurate                High-quality model
#   sh run_youtube.sh <URL> -o result.txt              Custom output file
#   sh run_youtube.sh <URL> --chunk 45                 Custom chunk size (e.g. 45s)
#
# Long videos (>60s) are automatically split into 55s chunks for accurate transcription.

set -e

echo ""
echo "============================================================"
echo "   YouTube Audio Download + Urdu Speech-to-Text  v2"
echo "============================================================"
echo ""

# Paths
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_PYTHON="$SCRIPT_DIR/venv/Scripts/python.exe"
YOUTUBE_PY="$SCRIPT_DIR/src/youtube_transcribe.py"

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

# Find yt-dlp in venv (matches python youtube_transcribe.py behavior)
YTDLP="$SCRIPT_DIR/venv/Scripts/yt-dlp.exe"
if [ ! -f "$YTDLP" ] && [ -f "$SCRIPT_DIR/venv/bin/yt-dlp" ]; then
    YTDLP="$SCRIPT_DIR/venv/bin/yt-dlp"
fi

# Check yt-dlp exists
if [ ! -f "$YTDLP" ]; then
    echo "[ERROR] yt-dlp not found. Install it with: pip install yt-dlp"
    exit 1
fi

echo "[OK]  Found yt-dlp: $YTDLP"
echo ""

# Show usage if no URL given
if [ -z "$1" ]; then
    echo "Usage:"
    echo "  sh run_youtube.sh <YouTube_URL>                  Urdu (default, auto-chunk for long videos)"
    echo "  sh run_youtube.sh <URL> -l en                    English transcription"
    echo "  sh run_youtube.sh <URL> -f json                  JSON output format"
    echo "  sh run_youtube.sh <URL> -m accurate              High-quality model"
    echo "  sh run_youtube.sh <URL> -o result.txt            Custom output file"
    echo "  sh run_youtube.sh <URL> --chunk 45              Custom chunk size (e.g. 45s)"
    echo ""
    echo "Examples:"
    echo '  sh run_youtube.sh https://youtube.com/watch?v=XXXXX'
    echo '  sh run_youtube.sh https://youtube.com/watch?v=XXXXX -l en -f json'
    echo ''
    exit 0
fi

# Pass all arguments to the Python script
"$VENV_PYTHON" "$YOUTUBE_PY" "$@"

echo ""
echo "============================================================"
echo "   [OK] Done!"
echo "============================================================"
echo ""
