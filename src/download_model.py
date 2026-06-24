"""Download the Urdu Whisper model for offline use.

Run once to cache the model locally — after that, transcribe.py works offline.

Usage:
  python download_model.py              # download default model
  python download_model.py --output .\models   # custom local path
  python download_model.py kingabzpro/whisper-large-v3-turbo-urdu  # specific model
"""

import sys
import os
from pathlib import Path

# ── Load .env configuration ──────────────────────────────────────
def _env_str(key: str, default: str) -> str:
    return os.environ.get(key, default)

_env_file = Path(__file__).parent / ".env"
if _env_file.exists():
    with open(_env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            if key and key not in os.environ:
                os.environ[key] = value
    del _env_file


def main():
    model_id = sys.argv[1] if len(sys.argv) > 1 else _env_str("HF_MODEL_ID", "kingabzpro/whisper-large-v3-turbo-urdu")

    print(f"Downloading model: {model_id}")
    print(f"This will download ~1.6 GB. Please allow a few minutes.\n")

    # Allow overriding cache location via env var or --output flag
    output_dir = None
    for i, arg in enumerate(sys.argv):
        if arg == "--output" and i + 1 < len(sys.argv):
            output_dir = Path(sys.argv[i + 1])
            break

    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        os.environ["HF_HOME"] = str(output_dir.resolve())
        print(f"Caching to: {output_dir.resolve()}")

    from transformers import pipeline

    print("[1/2] Downloading model weights …")
    pipe = pipeline(
        "automatic-speech-recognition",
        model=model_id,
        device="cpu",  # CPU only
    )

    print("[2/2] Verifying download …")

    cache_loc = os.path.expanduser("~/.cache/huggingface/hub")
    hf_home = os.environ.get("HF_HOME", cache_loc)

    print(f"\n[OK] Model downloaded and cached!")
    print(f"     Location: {hf_home}")
    print(f"\nYou can now run transcription offline:\n  python transcribe.py trans your_audio.mp3")


if __name__ == "__main__":
    main()
