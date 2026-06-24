# Frequently Asked Questions — Urdu Speech-to-Text Transcription Tool

> A comprehensive guide to setup, usage, troubleshooting, and best practices for the Urdu Whisper transcription tool.  
> Covers **Windows**, **Linux**, and **macOS**.

---

## Table of Contents

- [Getting Started & Setup](#getting-started--setup)
- [Transcribing Audio Files](#transcribing-audio-files)
- [Batch Processing](#batch-processing)
- [YouTube Integration](#youtube-integration)
- [Output Formats](#output-formats)
- [Configuration & Settings](#configuration--settings)
- [Performance & Hardware](#performance--hardware)
- [Model Management](#model-management)
- [Urdu Spell Correction](#urdu-spell-correction)
- [Troubleshooting — Common Errors](#troubleshooting--common-errors)
- [Troubleshooting — Platform-Specific Issues](#troubleshooting--platform-specific-issues)
- [Maintenance & Updates](#maintenance--updates)
- [Advanced Usage](#advanced-usage)

---

## Getting Started & Setup

### Q: What does this project do?

It transcribes Urdu (and other language) audio files to text using a fine-tuned Whisper model (`kingabzpro/whisper-large-v3-turbo-urdu`) trained on Mozilla Common Voice 17.0 data. Model accuracy metrics:

| Metric | Score |
|--------|-------|
| WER (Word Error Rate) | 26.23% |
| CER (Character Error Rate) | 8.80% |
| BLEU | 58.03% |
| ChrF | 81.64 |

### Q: What are the system requirements?

| Requirement | Minimum | Recommended |
|---|---|---|
| **OS** | Windows 10/11, Linux (Ubuntu 20+), macOS 12+ | Same with latest patches |
| **Python** | 3.11.x | 3.11.9 (latest patch) |
| **RAM** | 8 GB | 16 GB+ |
| **Disk Space** | 5 GB | 10 GB+ (model + cache + audio files) |
| **GPU** | Optional (CPU works) | NVIDIA RTX 3060 or better |
| **FFmpeg** | Required for YouTube | Latest stable |

### Q: Python 3.11 is not found. What do I do?

**Windows:**
1. Download Python 3.11 from https://www.python.org/downloads/release/python-3119/
2. During installation, check **"Add python.exe to PATH"** (critical!)
3. Check **"Use admin privileges when installing py.exe"**
4. Open a new Command Prompt and run: `py -3.11 --version`

**Linux:**
```bash
# Ubuntu/Debian
sudo apt install python3.11 python3.11-venv python3.11-dev

# Fedora/RHEL
sudo dnf install python3.11 python3.11-libs

# Arch
yay -S python3.11
```

**macOS:**
```bash
brew install python@3.11
# Verify
python3.11 --version
```

### Q: How do I run the one-time setup?

Run the setup script from your project directory:

```bash
# Cross-platform (Linux/macOS/Windows Git Bash)
sh setup_env.sh

# Windows PowerShell
python src/setup_env.py
```

This will:
1. Verify Python 3.11 is installed
2. Create a virtual environment (`venv/` folder)
3. Auto-detect NVIDIA GPU and install appropriate PyTorch
4. Install `transformers`, `accelerate`, `librosa`, `soundfile`, etc.
5. Create `youtube_downloads/` directory (if missing)
6. Copy `.env.sample` → `.env` (if `.env` doesn't exist yet)

> ⏱ First run downloads ~2–3 GB. Allow 5–15 minutes.

### Q: I already have Python installed but it says "Python 3.11 not found."

The setup checks for **exactly** Python 3.11.x. It won't accept 3.10, 3.12, etc.

```bash
# Check your exact Python versions
python3 --version   # or python --version
py --list          # Windows: lists all installed Pythons
```

If you have multiple Pythons, use the explicit version:

```bash
python3.11 -m venv venv
```

### Q: Setup failed with "pip install" errors.

This usually means your network can't reach `pypi.org` or `download.pytorch.org`.

**Solutions:**
```bash
# Use a different PyPI mirror (China)
pip install --index-url https://pypi.tuna.tsinghua.edu.cn/simple/ <package>

# Or set proxy
set HTTPS_PROXY=http://your-proxy:port  # Windows cmd
export HTTPS_PROXY=http://your-proxy:port  # Linux/macOS
```

### Q: The `venv` folder is huge. How big should it be?

Typical sizes:
- **CPU-only venv**: ~600 MB
- **CUDA GPU venv**: ~1.5–2 GB (PyTorch with CUDA wheels is large)
- **Model cache** (outside venv): ~1.6 GB in `~/.cache/huggingface/hub/`

---

## Transcribing Audio Files

### Q: How do I transcribe a single audio file?

```bash
# Using the wrapper script (auto-finds venv Python)
sh run_transcribe.sh speech.mp3

# Using Python directly
python src/transcribe.py trans speech.mp3

# With custom output path
python src/transcribe.py trans speech.mp3 --output result.txt
```

### Q: Which audio formats are supported?

| Extension | Format | Notes |
|---|---|---|
| `.mp3` | MP3 | Most common, widely supported |
| `.wav` | WAV | Best quality, uncompressed |
| `.flac` | FLAC | Lossless compressed |
| `.ogg` | OGG Vorbis | Open-source |
| `.m4a` | AAC audio | Apple format |
| `.mp4` | Video (audio extracted) | FFmpeg extracts audio internally |
| `.webm` | WebM | Web video/audio |
| `.aac` | AAC | Advanced codec |
| `.wma` | Windows Media Audio | Windows-only, may need extra codecs |

### Q: The transcription is too slow. How can I speed it up?

**Option 1: Use GPU (fastest)**
```bash
python src/transcribe.py trans audio.mp3 --device gpu
```

**Option 2: Use a faster model**
```bash
python src/transcribe.py trans audio.mp3 --quality fast
# Uses distil-medium.en (smaller, faster, slightly less accurate)
```

**Option 3: Enable parallel batch processing (CPU mode)**
```bash
python src/transcribe.py batch ./folder/ -w 4
# Uses 4 parallel workers
```

**Performance benchmarks:**

| Hardware | Approx. Speed |
|---|---|
| NVIDIA GPU (RTX 3060+) | 5–15x real-time |
| CPU (modern, 8-core) | 1–2x real-time |
| CPU (older / 4-core) | 0.3–1x real-time |

### Q: What does "real-time speed" mean?

It compares transcription time vs. audio duration. For example:
- `2.5x real-time` means a 10-minute audio transcribed in ~4 minutes
- `0.5x real-time` means a 10-minute audio transcribed in ~20 minutes (slower than playback)

### Q: How do I transcribe in a language other than Urdu?

```bash
# English transcription
python src/transcribe.py trans audio.mp3 --language en

# Hindi
python src/transcribe.py trans audio.mp3 --language hi

# Arabic
python src/transcribe.py trans audio.mp3 --language ar

# Set default for all future runs
python src/transcribe.py config set language=en
```

### Q: Can I use a custom HuggingFace model instead of the default?

Yes! Any Whisper-compatible model on HuggingFace works:

```bash
# Use OpenAI's official large model
python src/transcribe.py trans audio.mp3 --model openai/whisper-large-v3-turbo

# Use any model
python src/transcribe.py trans audio.mp3 --model username/model-name

# Set as default in config
python src/transcribe.py config set model=openai/whisper-large-v3-turbo
```

**Recommended models:**

| Model | Best For | Speed | Quality |
|---|---|---|---|
| `kingabzpro/whisper-large-v3-turbo-urdu` | Default Urdu | Fast | 91%+ CER accuracy |
| `openai/whisper-large-v3-turbo` | General multilingual | Fast | Excellent |
| `distil-whisper/distil-medium.en` | Speed-critical | Fastest | Good |

### Q: What do the quality presets do?

| Preset | Model Used | Description |
|---|---|---|
| `fast` | distil-medium.en | Smallest model, fastest, acceptable accuracy |
| `turbo` (default) | whisper-large-v3-turbo-urdu | Balanced speed/accuracy for Urdu |
| `accurate` | whisper-large-v3-turbo (OpenAI) | Best quality, slightly slower |

```bash
python src/transcribe.py trans audio.mp3 --quality accurate
```

### Q: Can I see the audio file info without transcribing?

```bash
# Show audio metadata only
python src/transcribe.py trans audio.mp3 --info

# Output:
#   File       : speech.mp3
#   Size       : 2.45 MB
#   Duration   : 12:30.450
#   Sample Rate: 44100 Hz
#   Channels   : 2
#   Format     : MPEG audio
```

### Q: How do I preview what would happen without actually processing?

```bash
# Single file preview
python src/transcribe.py trans audio.mp3 --dry-run

# Batch folder preview
python src/transcribe.py batch --dry-run-batch ./folder/
```

This shows audio info, model, output path, and cache status before processing.

---

## Batch Processing

### Q: How do I process an entire folder of audio files?

```bash
# Using the wrapper script
sh run_batch.sh ./audio_folder/

# With JSON format
sh run_batch.sh ./audio_folder/ json

# Using Python directly
python transcribe.py batch ./audio_folder/ --format json
```

### Q: Can batch processing handle subdirectories?

Yes! It recursively scans all subdirectories:

```bash
# Processes audio in ./podcasts/, ./podcasts/season1/, etc.
python src/transcribe.py batch ./podcasts/
```

### Q: What happens if a batch job is interrupted? Does it resume?

Yes! The tool tracks completed files in `.batch_status.json`. When you re-run, already-completed files are automatically skipped:

```bash
# Resume interrupted batch — only processes remaining files
python src/transcribe.py batch ./audio_folder/
```

Clear the status to re-process everything:
```bash
rm .batch_status.json  # Linux/macOS
del .batch_status.json  # Windows
```

### Q: Can I process multiple files in parallel?

Yes, on **CPU only** (GPU remains single-threaded):

```bash
# Use 4 parallel workers
python transcribe.py batch ./folder/ --workers 4

# Or via config
python transcribe.py config set workers=4
```

> Note: Parallel workers use `ProcessPoolExecutor` — each worker loads the model independently. Only enable on CPU; GPU with multiprocessing can cause CUDA errors.

### Q: What is JSON Lines (jsonl) format? Why would I use it?

JSONL produces one JSON object per line, ideal for programmatic consumption:

```bash
python src/transcribe.py batch ./folder/ --format jsonl
```

Each line looks like:
```json
{"transcription": "urdu text here", "metadata": {"model": "...", "language": "ur", ...}}
```

> ⚠️ `jsonl` is only supported with `--batch`, not with single files.

### Q: How do I skip the cache and force re-transcription?

```bash
python src/transcribe.py batch ./folder/ --no-cache
python src/transcribe.py trans audio.mp3 --no-cache
```

---

## YouTube Integration

### Q: How do I transcribe a YouTube video?

```bash
# Urdu transcription (default)
python src/youtube_transcribe.py https://youtube.com/watch?v=XXXXX

# English
python src/youtube_transcribe.py https://youtube.com/watch?v=XXXXX -l en

# Word document output
python src/youtube_transcribe.py https://youtube.com/watch?v=XXXXX -f docx

# High-quality model
python src/youtube_transcribe.py https://youtube.com/watch?v=XXXXX -m accurate

# Custom output file
python src/youtube_transcribe.py https://youtube.com/watch?v=XXXXX -o result.txt

# Quiet mode (JSON to stdout)
python src/youtube_transcribe.py https://youtube.com/watch?v=XXXXX --quiet
```

### Q: Can I use the wrapper script for YouTube?

Yes:
```bash
sh run_youtube.sh https://youtube.com/watch?v=XXXXX -l en
```

### Q: Where are downloaded YouTube audio files saved?

In the `youtube_downloads/` directory within your project folder. Audio is extracted as MP3 by default (highest quality).

### Q: YouTube download fails with "ERROR". What now?

Common causes and fixes:

| Error | Cause | Fix |
|---|---|---|
| `ERROR: Video unavailable` | Video removed/region-locked | Try a different video |
| `ERROR: no fmt_streams` | Format not available | Install latest yt-dlp: `pip install -U yt-dlp` |
| `FFmpeg not found` | FFmpeg missing from PATH | Install FFmpeg (see below) |
| `ERROR: [download] Got HTTP error` | Network/proxy issue | Check internet; set proxy env var |

**Install FFmpeg:**

```bash
# Windows: Download from https://ffmpeg.org/download.html
# Add to PATH or put in project folder

# Linux (Ubuntu/Debian)
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Verify
ffmpeg -version
```

### Q: Can I download video without transcribing?

Not directly — the tool combines download and transcription. To extract just the audio:

```bash
venv\Scripts\yt-dlp.exe -x --audio-format mp3 <URL>
```

---

## Output Formats

### Q: What output formats are available?

| Format | Extension | Use Case |
|---|---|---|
| `txt` (default) | `.txt` | Plain text, most compatible |
| `json` | `.json` | Programmatic use, includes metadata |
| `jsonl` | `.jsonl` | Batch JSON lines (batch only) |

```bash
# JSON with metadata
python src/transcribe.py trans audio.mp3 --format json

# TXT output (default)
python src/transcribe.py trans audio.mp3

# JSONL (batch only)
python src/transcribe.py batch samples/ --format jsonl
```

### Q: What does the JSON output look like?

```json
{
  "transcription": "دیکھیے پانی کب تک بہتا اور مچھلی کب تک تیرتی ہے",
  "metadata": {
    "model": "kingabzpro/whisper-large-v3-turbo-urdu",
    "language": "ur",
    "transcription_time_s": 4.23,
    "generated_at": "2026-06-22T10:30:00+00:00",
    "version": "2.0.0"
  }
}
```

---

## Configuration & Settings

### Q: How do I view my current configuration?

```bash
python src/transcribe.py config show
```

Output:
```
=== Current Configuration ===

  model                 : kingabzpro/whisper-large-v3-turbo-urdu
  language              : ur
  device                : None
  format                : txt
  quality               : turbo
  workers               : 1
  auto_punctuate        : True
  auto_spell            : True
  max_segment_minutes   : 30
```

### Q: How do I change the default model/language/format?

```bash
# Set multiple settings at once
python src/transcribe.py config set language=en format=json quality=accurate

# View to verify
python src/transcribe.py config show
```

The config file (`transcribe_config.json`) is auto-created in your project root.

### Q: What happens when both config and CLI flags are provided?

**CLI flags always override config values.** Example:

```bash
# Config has language = "ur"
python src/transcribe.py config set language=ur

# But this overrides to English for just this run
python src/transcribe.py trans audio.mp3 --language en  # ← English, not Urdu
```

### Q: What are all the config options?

| Setting | Default | Description |
|---|---|---|
| `model` | kingabzpro/whisper-large-v3-turbo-urdu | HuggingFace model ID |
| `language` | ur | Language code (ur, en, hi, ar, etc.) |
| `device` | None (auto) | `cpu`, `gpu`, or `null` for auto-detect |
| `format` | txt | Output format: txt, json |
| `quality` | turbo | Speed/quality preset |
| `workers` | 1 | Parallel workers for batch (CPU only) |
| `auto_punctuate` | true | Auto-add Urdu sentence-ending punctuation |
| `auto_spell` | true | Apply Urdu spell correction by default |
| `max_segment_minutes` | 30 | Max audio segment size in minutes |

### Q: Where is the config file stored?

In your project root: `transcribe_config.json`

You can also edit it directly with any text editor.

---

## Performance & Hardware

### Q: How do I check if I have a GPU available?

**Windows:**
```cmd
nvidia-smi
```

**Linux:**
```bash
nvidia-smi
# or
torch.cuda.is_available()
```

**macOS (Apple Silicon):**
```python
import torch
print(torch.backends.mps.is_available())  # True if Apple GPU available
```

> Note: MPS on macOS is not yet supported by this tool's model pipeline. Use CPU mode on macOS.

### Q: How much VRAM does the model need?

The Whisper large-v3-turbo model requires approximately **3–4 GB VRAM**. If your GPU has less, force CPU mode:

```bash
python src/transcribe.py trans audio.mp3 --device cpu
```

### Q: Can I use this on macOS?

Yes! The tool is cross-platform. However:

- **Apple Silicon (M1/M2/M3)**: Works via CPU mode. MPS acceleration is not yet supported by the Whisper pipeline in transformers.
- **Setup**: Use `sh setup_env.sh` — it auto-detects no GPU and installs CPU PyTorch.
- **Performance**: CPU-only on macOS is slower than Windows/Linux with NVIDIA GPU, but fully functional.

### Q: Can I use this on Linux?

Yes! Everything works identically to Windows (except the `setup_env.sh` script is native):

```bash
# Setup
sh setup_env.sh

# Transcribe
python src/transcribe.py trans audio.mp3

# Batch
sh run_batch.sh ./folder/
```

### Q: My transcription speed dropped dramatically. Why?

Common causes:

1. **GPU disconnected or powered down** — Check `nvidia-smi`; your GPU may have gone to sleep
2. **Model cached on CPU instead of GPU** — Run with explicit `--device gpu`
3. **Windows power saving** — Set Power Plan to "High Performance"
4. **RAM swap thrashing** — Close other apps; ensure 16GB+ RAM available
5. **Thermal throttling** — Laptop may have overheated; check CPU/GPU temps

### Q: How do I force GPU mode explicitly?

```bash
python src/transcribe.py trans audio.mp3 --device gpu
```

Verify it's working by checking the output:
```
[INFO] GPU detected: NVIDIA GeForce RTX 3060
```

---

## Model Management

### Q: Where is the model downloaded and cached?

**Windows:**
```
C:\Users\<YourName>\.cache\huggingface\hub\
```

**Linux/macOS:**
```
~/.cache/huggingface/hub/
```

The model occupies ~1.6 GB. You can verify:
```bash
ls -lh ~/.cache/huggingface/hub/  # Linux/macOS
dir /s %USERPROFILE%\.cache\huggingface\hub\  # Windows cmd
```

### Q: Can I transcribe offline?

Yes! After the first run (which downloads the model), everything works offline. The tool uses `local_files_only=True` by default — it will only reach the internet if the model isn't cached yet.

To pre-download for offline use:
```bash
python src/download_model.py
```

### Q: How do I specify a custom cache location?

```bash
# Set HF_HOME environment variable before running
set HF_HOME=C:\my_custom_cache  # Windows cmd
export HF_HOME=/my/custom/cache  # Linux/macOS

python src/transcribe.py trans audio.mp3

# Or use src/download_model.py's --output flag
python src/download_model.py --output ./models
```

### Q: Can I delete the cached model and redownload it?

Yes:
```bash
# Delete cache folder (Linux/macOS)
rm -rf ~/.cache/huggingface/hub/transformers/*whisper*

# Delete cache folder (Windows — File Explorer or cmd)
rmdir /s /q %USERPROFILE%\.cache\huggingface\hub\transformers

# Redownload on next run
python transcribe.py trans audio.mp3  # Will re-download ~1.6 GB
```

### Q: What happens if the model download fails mid-way?

The HuggingFace cache supports **resumable downloads**. If interrupted, simply run again — it will resume from where it left off rather than starting over.

---

## Urdu Spell Correction

### Q: What is the Urdu spell correction feature?

The `UrduSpellCorrector` class corrects common transcription errors:
- Arabic/Persian character normalization to proper Urdu equivalents
- Whitespace fixing (extra spaces, leading/trailing)
- Common misspelling corrections
- Double character removal
- Punctuation spacing fixes

### Q: How do I enable spell correction?

It's **enabled by default** in v2. To use it explicitly:

```bash
python src/transcribe.py trans audio.mp3 --spell
```

Or configure in config:
```bash
python src/transcribe.py config set auto_spell=true
```

### Q: Can I customize the spell correction?

The correction dictionary is in `src/urdu_correction.py` under `_load_word_dictionary()`. Edit it directly to add your own corrections:

```python
# src/urdu_correction.py — add new entries to the dictionary
self.word_dictionary = {
    ...existing entries...
    'your_error': 'your_correct_spelling',
}
```

### Q: What correction levels are available?

| Level | Description |
|---|---|
| `basic` | Pattern corrections only (whitespace, double chars) |
| `medium` | Patterns + dictionary lookups |
| `full` (default) | All three levels including advanced character normalization |

```python
from urdu_correction import UrduSpellCorrector

corrector = UrduSpellCorrector()
text, stats = corrector.correct(raw_text, level="medium")  # medium correction
```

---

## Troubleshooting — Common Errors

### Q: Error: "File not found: audio.mp3"

- Verify the file exists and the path is correct (no typos)
- For paths with spaces, wrap in quotes: `python transcribe.py trans "C:\My Folder\audio.mp3"`
- Use absolute paths if relative paths don't work
- On Windows, use forward slashes or escaped backslashes: `"C:/My Folder/audio.mp3"`

### Q: Error: "Out of Memory" on GPU

```
RuntimeError: CUDA out of memory.
```

**Solutions:**

1. **Force CPU mode:**
   ```bash
   python src/transcribe.py trans audio.mp3 --device cpu
   ```

2. **Use a faster/smaller model:**
   ```bash
   python src/transcribe.py trans audio.mp3 --quality fast
   ```

3. **Close other GPU-using apps** (games, video editors, etc.)

4. **Reduce batch size** — process fewer files at once

### Q: Error: "Transcription returned empty text"

The model produced no output. Causes and fixes:

| Cause | Fix |
|---|---|
| Audio is silence/no speech | Check audio file; record clear speech |
| Wrong language setting | Use `--language` flag for the correct language |
| Corrupt audio file | Open in a media player to verify; re-export if needed |
| Very long audio without proper chunking | Tool should handle this automatically; try `--quality fast` |

### Q: Error: "ModuleNotFoundError: No module named 'transformers'"

The virtual environment is broken or dependencies weren't installed:

```bash
# Delete venv and re-setup
rm -rf venv  # Linux/macOS
rmdir /s /q venv  # Windows

sh setup_env.sh
```

### Q: Error: "ERROR: yt-dlp not found"

```bash
# Install inside the virtual environment
venv\Scripts\pip install yt-dlp  # Windows
venv/bin/pip install yt-dlp      # Linux/macOS

# Or verify it's installed
venv\Scripts\python -c "import yt_dlp; print(yt_dlp.__version__)"
```

### Q: Error: "FFmpeg not found"

YouTube transcription and some audio formats require FFmpeg.

**Windows:** Download from https://ffmpeg.org/download.html → extract → add to PATH

**Linux:**
```bash
sudo apt install ffmpeg  # Ubuntu/Debian
sudo dnf install ffmpeg  # Fedora
sudo pacman -S ffmpeg    # Arch
```

**macOS:**
```bash
brew install ffmpeg
```

Verify:
```bash
ffmpeg -version
```

### Q: Error: "Audio file not loading" / "librosa error"

1. Verify `librosa` and `soundfile` are installed:
   ```bash
   venv\Scripts\pip list | findstr librosa  # Windows cmd
   venv/bin/pip list | grep librosa           # Linux/macOS
   ```

2. Try converting to WAV with Audacity (free): https://www.audacityteam.org/

3. Some exotic codecs may not be supported — convert to WAV or MP3 first.

### Q: Error: "Model loading failed" / network timeout on first run

1. Check internet connectivity
2. The model download can take 5–15 minutes depending on your connection
3. If behind a proxy, set it before running:
   ```bash
   set HTTPS_PROXY=http://your-proxy:port  # Windows
   export HTTPS_PROXY=http://your-proxy:port  # Linux/macOS
   ```

4. Retry — downloads are resumable

### Q: Error: "Unknown command" when running transcribe.py

Make sure you use the correct subcommand as the **first** argument:

```bash
# ✅ Correct
python src/transcribe.py trans audio.mp3
python src/transcribe.py batch ./folder/
python src/transcribe.py config show

# ❌ Wrong — 'trans' must come first
python src/transcribe.py audio.mp3
```

### Q: Transcription output has timestamp markers like `<|2.54|>` in the text

This was a known bug in earlier versions (fixed in v2.1.0). If you see it, update to the latest version or manually strip timestamps:

```bash
python src/transcribe.py trans audio.mp3 --spell
# The spell correction applies whitespace normalization which helps
```

### Q: Batch processing says "All files already completed" but I need fresh output

Clear the batch status file:

```bash
# Linux/macOS
rm .batch_status.json

# Windows
del .batch_status.json

# Then re-run
python transcribe.py batch ./folder/
```

Or use `--no-cache`:
```bash
python transcribe.py batch ./folder/ --no-cache
```

### Q: Output file is not created / permission denied

- Ensure the output directory exists and you have write permissions
- For custom output paths, parent directories are auto-created
- On Linux/macOS, check folder permissions: `ls -la /path/to/output/`
- On Windows, run as administrator if writing to protected locations

### Q: Audio info shows wrong duration or sample rate

- `soundfile` reads the file header — if the header is corrupt, it may report wrong values
- As fallback, `librosa` loads the full file for accurate metadata
- For unreliable files, convert to WAV with Audacity or FFmpeg first:
  ```bash
  ffmpeg -i input.mp3 -vn -acodec pcm_s16le -ar 44100 output.wav
  ```

---

## Troubleshooting — Platform-Specific Issues

### Windows

#### Q: "sh" command not recognized when running shell scripts

Windows doesn't have `sh` by default. Use one of these alternatives:

```bash
# Option 1: Run Python directly (recommended on Windows)
python src/transcribe.py trans audio.mp3
python src/setup_env.py

# Option 2: Use Git Bash (comes with Git for Windows)
git bash run_transcribe.sh audio.mp3

# Option 3: Use PowerShell
pwsh -Command "./run_transcribe.ps1 audio.mp3"
```

#### Q: "py" command not found

Python 3.11 installer includes `py.exe` launcher. If missing:
- Re-run the Python installer and repair the installation
- Or add to PATH manually: `C:\Users\YourName\AppData\Local\Programs\Python\Python311\`

#### Q: Drag-and-drop doesn't work on run_transcribe.sh

Windows needs a `.bat` or `.cmd` wrapper for drag-and-drop. The shell script accepts files as arguments:
```bash
python run_transcribe.sh "C:\path\to\audio.mp3"
```

#### Q: Windows Defender / Antivirus blocks the scripts

Add your project folder to the exclusion list in Windows Security → Virus & threat protection → Exclusions.

#### Q: "Could not find a version that matches torch" on Windows GPU setup

The CUDA PyTorch wheel may not be available for your Python version. Try:
```bash
# Explicitly install CPU version first, then CUDA
venv\Scripts\pip install --upgrade pip
venv\Scripts\pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Linux

#### Q: "Permission denied" on shell scripts

```bash
chmod +x setup_env.sh run_transcribe.sh run_batch.sh run_youtube.sh
# Then run directly:
./setup_env.sh
```

#### Q: Python 3.11 not in default repos (newer Ubuntu)

```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev
```

#### Q: CUDA drivers not detected despite having NVIDIA GPU

```bash
# Install CUDA toolkit and driver
sudo apt install nvidia-cuda-toolkit

# Verify
nvidia-smi
nvcc --version  # If available
```

#### Q: "librosa" installation fails on Linux

```bash
# Install system dependencies first
sudo apt install libsndfile1-dev portaudio19-dev

venv/bin/pip install librosa
```

### macOS

#### Q: Shell scripts use `#!/bin/sh` — is that compatible?

Yes, the setup_env.sh and run_*.sh scripts use POSIX-compliant shell syntax (`sh`) that works on all platforms including macOS, Linux, Windows Git Bash, and WSL.

#### Q: Apple Silicon (M1/M2) GPU acceleration not working

The current Whisper pipeline in `transformers` does not yet support Apple's MPS backend. The tool will run on CPU on macOS. Apple is actively working on MPS support for PyTorch — future versions may add this.

Workaround for faster processing:
```bash
# Use the fast quality preset (smaller model)
python transcribe.py trans audio.mp3 --quality fast
```

#### Q: "xcrun: error: invalid active developer path" on macOS

```bash
xcode-select --install
# Re-run setup_env.sh
sh setup_env.sh
```

#### Q: Homebrew Python conflicts with project venv

Don't use `brew install python` for this project. Always use the Python 3.11 installer or pyenv:

```bash
# Use pyenv to manage Python versions (recommended)
brew install pyenv
pyenv install 3.11.9
pyenv local 3.11.9
```

---

## Maintenance & Updates

### Q: How do I update the dependencies?

```bash
venv\Scripts\activate   # Windows
venv/bin/activate       # Linux/macOS

pip install --upgrade transformers accelerate librosa soundfile tqdm yt-dlp

# Deactivate when done
deactivate
```

### Q: The virtual environment is broken. How do I recreate it?

```bash
# Delete the old venv
rm -rf venv  # Linux/macOS
rmdir /s /q venv  # Windows

# Re-run setup
sh setup_env.sh
```

### Q: How do I clean up disk space?

1. **Clear transcription cache** (safe to delete):
   ```bash
   del .transcribe_cache.json  # Windows
   rm .transcribe_cache.json   # Linux/macOS
   ```

2. **Delete downloaded YouTube audio:**
   ```bash
   rm youtube_downloads/*  # Linux/macOS
   del youtube_downloads\*  # Windows
   ```

3. **Clear model cache** (will re-download on next run):
   ```bash
   rm -rf ~/.cache/huggingface/hub/transformers/*whisper*  # Linux/macOS
   rmdir /s /q %USERPROFILE%\.cache\huggingface\hub\transformers  # Windows
   ```

4. **Remove old venv**: The old venv takes ~1.5 GB — delete and recreate if needed.

### Q: How do I back up my configuration?

```bash
# Copy config to a safe location
cp transcribe_config.json ~/my_backups/urdu-config.json  # Linux/macOS
copy transcribe_config.json C:\backups\urdu-config.json  # Windows
```

To restore:
```bash
cp ~/my_backups/urdu-config.json ./transcribe_config.json
```

### Q: What's in the `.gitignore` — should I track any files?

Currently ignored by default (do NOT commit):
- `venv/` — virtual environment (recreate with setup_env.sh)
- `*.mp3`, `*.wav`, etc. — audio files
- `.transcribe_cache.json`, `transcribe_config.json`, `.batch_status.json` — auto-generated

You might want to track:
- `urdu_correction.py` — your custom dictionary entries
- `CHANGELOG.md` — version history

---

## Advanced Usage

### Q: Can I pipe output to another script (quiet mode)?

Yes! Use `--quiet` to get JSON on stdout only:

```bash
# Get JSON result for programmatic use
python src/transcribe.py trans audio.mp3 --quiet | python -m json.tool

# Use in a bash script
RESULT=$(python src/transcribe.py trans audio.mp3 --quiet)
echo "$RESULT" | jq '.transcription'
```

### Q: Can I integrate this into my own Python code?

Yes! Import the modules directly:

```python
from src.urdu_correction import UrduSpellCorrector, quick_correct

# Spell correction
corrector = UrduSpellCorrector()
text, stats = corrector.correct("یہ acha hai", level="full")

# Quick one-liner
corrected, _ = quick_correct("یہ acha hai", level="full")

# Or import transcribe_single for programmatic transcription
from src.transcribe import transcribe_single
result = transcribe_single("audio.mp3", language="ur", fmt="txt")
print(result["text"])
```

### Q: Can I use this for languages other than Urdu?

Yes! Whisper supports 99+ languages. The tool is not limited to Urdu:

```bash
# Hindi
python src/transcribe.py trans audio.mp3 --language hi

# Arabic
python src/transcribe.py trans audio.mp3 --language ar

# Persian (Farsi) — use 'fa'
python src/transcribe.py trans audio.mp3 --language fa

# English
python src/transcribe.py trans audio.mp3 --language en

# Detect automatically (let Whisper figure it out)
python src/transcribe.py config set language null
```

### Q: What is the maximum audio file size/duration supported?

There is no hard limit. The tool uses chunked processing with 30-second chunks (5s overlap), so even multi-hour files are processed in pieces without running out of memory.

For best results, files under 2 GB work most reliably. For larger files:
- Split them first using Audacity or FFmpeg
- Use `--quality fast` for faster processing of long files

### Q: How does the automatic punctuation work?

The tool adds Urdu sentence-ending periods (۔) after common ending patterns:
- `ہے`, `گا`, `گی`, `یں`, `نا`, `ا`

It detects these patterns and inserts a Urdu full stop (U+06D4) followed by appropriate spacing. This is heuristic-based — not perfect, but helpful for raw transcription output.

To disable:
```bash
python src/transcribe.py config set auto_punctuate=false
```

### Q: Can I use this with Docker?

The tool doesn't have an official Docker image yet, but you can create one:

```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app/

RUN python src/setup_env.py

CMD ["python", "src/transcribe.py", "trans"]
```

Then run:
```bash
docker build -t urdu-transcribe .
docker run --rm -v $(pwd):/data urdu-transcribe trans /data/audio.mp3
```

### Q: How do I contribute or report bugs?

Refer to `CHANGELOG.md` for the version history. For issues:

1. Check this FAQ first
2. Verify Python 3.11, PyTorch, and transformers versions are compatible
3. Test with `--dry-run` to isolate issues
4. Note the full error output and your hardware/OS configuration

---

## Quick Reference Card

### Most Common Commands

```bash
# Setup (one time)
sh setup_env.sh

# Single file transcription
python src/transcribe.py trans audio.mp3

# Transcribe in English
python src/transcribe.py trans audio.mp3 --language en

# Fast mode
python src/transcribe.py trans audio.mp3 --quality fast

# GPU force
python src/transcribe.py trans audio.mp3 --device gpu

# Batch process folder
python src/transcribe.py batch ./folder/ --format json

# Show config
python src/transcribe.py config show

# Change default language
python src/transcribe.py config set language=en

# YouTube transcribe
python src/youtube_transcribe.py https://youtube.com/watch?v=XXXXX

# Dry run (preview)
python src/transcribe.py trans audio.mp3 --dry-run
```

### Common Flags at a Glance

| Flag | Purpose |
|---|---|
| `--format txt\|json` | Output format |
| `--language <code>` | Language code |
| `--quality fast\|turbo\|accurate` | Speed/quality preset |
| `--device cpu\|gpu` | Force device |
| `--model <id>` | Custom HuggingFace model |
| `--output <path>` | Custom output path |
| `--quiet` / `-q` | Minimal JSON output |
| `--dry-run` | Preview only |
| `--info` | Audio info only |
| `--no-cache` | Skip cache |
| `--spell` / `-s` | Apply spell correction |
| `--workers N` / `-w N` | Parallel workers (batch) |
