"""setup_env.py - One-time environment setup for Urdu Whisper.

Creates a Python 3.11 virtual environment and installs all dependencies.
Run once from your project folder.
"""

import sys
import os
import subprocess
import platform


def run(cmd, **kwargs):
    """Run a command and raise on failure."""
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", **kwargs)
    if result.returncode != 0:
        print(f"[ERROR] Command failed: {' '.join(cmd)}")
        if result.stderr:
            for line in result.stderr.strip().splitlines():
                print(f"  {line}")
        sys.exit(1)
    return result


def main():
    print()
    print("=" * 60)
    print("   Urdu Whisper - Environment Setup")
    print("=" * 60)
    print()

    # --- Verify Python 3.11 ---
    py_exe = None
    for candidate in ["py -3.11", "python3.11", "python3", "python"]:
        try:
            result = subprocess.run(
                [candidate, "--version"],
                capture_output=True, text=True, encoding="utf-8", errors="replace"
            )
            if result.returncode == 0 and "3.11" in result.stdout:
                # Determine the actual executable path
                which_result = subprocess.run(
                    ["where" if platform.system() == "Windows" else "which", candidate.split()[0]],
                    capture_output=True, text=True
                )
                py_exe = which_result.stdout.strip().splitlines()[0]
                print(f"[OK]  Found: {candidate} ({result.stdout.strip()})")
                break
        except FileNotFoundError:
            pass

    if not py_exe:
        print("[ERROR] Python 3.11 not found.")
        print("        Install from: https://www.python.org/downloads/release/python-3119/")
        sys.exit(1)

    # --- Paths (project root, not src/) ---
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    venv_dir = os.path.join(project_root, "venv")
    venv_python = os.path.join(venv_dir, "Scripts", "python.exe")

    # --- Create venv ---
    if os.path.exists(venv_python):
        print(f"[SKIP] Virtual environment already exists at: {venv_dir}")
        print("        Delete the 'venv' folder and re-run to recreate.")
    else:
        print(f"[....] Creating virtual environment at: {venv_dir}")
        run([py_exe, "-m", "venv", venv_dir])
        print("[OK]  Virtual environment created.")

    # --- Upgrade pip ---
    print(f"[....] Upgrading pip ...")
    run([venv_python, "-m", "pip", "install", "--upgrade", "pip", "--quiet"])
    print("[OK]  pip upgraded.")

    # --- Install CPU-only PyTorch ---
    print("[....] Installing CPU-only PyTorch …")
    cpu_url = "https://download.pytorch.org/whl/cpu"

    # --- Install PyTorch ---
    print(f"[....] Installing PyTorch and torchaudio …")
    run(
        [venv_python, "-m", "pip", "install",
         f"--index-url={cpu_url}", "torch", "torchaudio", "--quiet"]
    )
    print("[OK]  PyTorch installed.")

    # --- Install HuggingFace + audio deps ---
    # tf-keras is required because Transformers includes tf/keras integration code.
    print(f"[....] Installing transformers, accelerate, librosa, soundfile ...")
    run(
        [venv_python, "-m", "pip", "install",
         "transformers", "accelerate", "librosa", "soundfile", "tf-keras", "--quiet"]
    )
    print("[OK]  All dependencies installed.")

    # ── Create youtube_downloads directory if it doesn't exist ────────
    ytdl_dir = os.path.join(project_root, "youtube_downloads")
    if not os.path.exists(ytdl_dir):
        os.makedirs(ytdl_dir)
        print(f"[OK]  Created youtube_downloads/ directory.")

    # ── Create .env from .env.sample if .env doesn't exist ───────────
    env_sample = os.path.join(project_root, ".env.sample")
    env_file = os.path.join(project_root, ".env")
    if os.path.exists(env_sample) and not os.path.exists(env_file):
        with open(env_sample, "r", encoding="utf-8") as src:
            content = src.read()
        with open(env_file, "w", encoding="utf-8") as dst:
            dst.write(content)
        print(f"[OK]  Created .env from .env.sample — review/edit values before use.")
    elif os.path.exists(env_file):
        print("[SKIP] .env already exists — skipping creation. Edit it manually if needed.")

    print()
    print("=" * 60)
    print("   Setup complete!")
    print("=" * 60)
    print()
    print("   Next step - run the transcription:")
    print()
    print("     python src/transcribe.py trans your_audio.mp3")
    print()


if __name__ == "__main__":
    main()
