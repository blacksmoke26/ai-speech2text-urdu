#!/bin/sh
# setup_env.sh - One-time environment setup for Urdu Whisper.
# Usage: sh setup_env.sh  (or run via ./setup_env.sh after chmod +x)

set -e

echo ""
echo "============================================================"
echo "   Urdu Whisper - Environment Setup"
echo "============================================================"
echo ""

# --- Verify Python 3.11 ---
PY_CMD=""
for candidate in python3.11 python3 python; do
    if "$candidate" --version 2>&1 | grep -q "Python 3\.11"; then
        PY_CMD="$candidate"
        break
    fi
done

if [ -z "$PY_CMD" ]; then
    echo "[ERROR] Python 3.11 not found."
    echo "        Install from: https://www.python.org/downloads/release/python-3119/"
    exit 1
fi

echo "[OK]  Found: $PY_CMD ($(python3.11 --version 2>/dev/null || python --version))"

# --- Paths ---
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"
VENV_PYTHON="$VENV_DIR/bin/python"

# On Windows (Git Bash / MSYS2), use Scripts; on Linux/Mac, use bin
if [ -f "$VENV_DIR/Scripts/python.exe" ]; then
    VENV_PYTHON="$VENV_DIR/Scripts/python.exe"
fi

# --- Create venv ---
if [ -f "$VENV_PYTHON" ] || [ -f "${VENV_PYTHON%.exe}" ]; then
    echo "[SKIP] Virtual environment already exists at: $VENV_DIR"
    echo "        Delete the 'venv' folder and re-run to recreate."
else
    echo "[....] Creating virtual environment at: $VENV_DIR"
    "$PY_CMD" -m venv "$VENV_DIR"
    echo "[OK]  Virtual environment created."
fi

# --- Upgrade pip ---
echo "[....] Upgrading pip ..."
"$VENV_PYTHON" -m pip install --upgrade pip --quiet
echo "[OK]  pip upgraded."

# --- Detect CUDA and GPU capability ---
echo "[....] Detecting hardware ..."
HAS_GPU=0
GPU_ARCH=""
if command -v nvidia-smi >/dev/null 2>&1; then
    if nvidia-smi >/dev/null 2>&1; then
        HAS_GPU=1
        # Get compute capability (e.g. "86" for RTX 4090, "120" for RTX 5080)
        GPU_ARCH=$(python3 -c "
import torch
if torch.cuda.is_available():
    print(f'sm_{torch.cuda.get_device_capability(0)[0]*10 + torch.cuda.get_device_capability(0)[1]}')
else:
    print('unknown')
" 2>/dev/null || echo "unknown")
        GPU_ARCH=${GPU_ARCH:-unknown}
    fi
fi

if [ "$HAS_GPU" -eq 1 ]; then
    echo "[OK]  NVIDIA GPU detected (compute capability: $GPU_ARCH)."
    # sm_120 (RTX 50xx Blackwell) requires PyTorch >= 2.6 with cu128 wheels
    if echo "$GPU_ARCH" | grep -q "sm_120"; then
        CUDA_URL="https://download.pytorch.org/whl/cu128"
        echo "[INFO]  Using cu128 (PyTorch >= 2.6) for Blackwell support."
    else
        CUDA_URL="https://download.pytorch.org/whl/cu121"
        echo "[INFO]  Using cu121."
    fi
else
    echo "[INFO] No NVIDIA GPU detected - installing CPU-only PyTorch."
    echo "       Transcription will work but will be slower."
    CUDA_URL="https://download.pytorch.org/whl/cpu"
fi

# --- Install PyTorch ---
echo "[....] Installing PyTorch and torchaudio ..."
"$VENV_PYTHON" -m pip install --index-url="$CUDA_URL" torch torchaudio --quiet
echo "[OK]  PyTorch installed."

# --- Install HuggingFace + audio deps ---
echo "[....] Installing transformers, accelerate, librosa, soundfile ..."
"$VENV_PYTHON" -m pip install transformers accelerate librosa soundfile tf-keras --quiet
echo "[OK]  All dependencies installed."

# ── Create youtube_downloads directory if it doesn't exist ────────
ytdl_dir="$SCRIPT_DIR/youtube_downloads"
if [ ! -d "$ytdl_dir" ]; then
    mkdir -p "$ytdl_dir"
    echo "[OK]  Created youtube_downloads/ directory."
fi

# ── Create .env from .env.sample if .env doesn't exist ───────────
env_sample="$SCRIPT_DIR/.env.sample"
env_file="$SCRIPT_DIR/.env"
if [ -f "$env_sample" ] && [ ! -f "$env_file" ]; then
    cp "$env_sample" "$env_file"
    echo "[OK]  Created .env from .env.sample — review/edit values before use."
elif [ -f "$env_file" ]; then
    echo "[SKIP] .env already exists — skipping creation. Edit it manually if needed."
fi

echo ""
echo "============================================================"
echo "   Setup complete!"
echo "============================================================"
echo ""
echo "   Next step - run the transcription:"
echo ""
echo "     python src/transcribe.py trans your_audio.mp3"
