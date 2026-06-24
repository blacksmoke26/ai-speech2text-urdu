# Quick Start Guide — Urdu Audio-to-Text Transcription

Transcribe Urdu (or any language) audio files and YouTube videos to text.  
Works on **Windows**, **Linux**, and **macOS** — GPU recommended but not required.

---

## Prerequisites

- [ ] **Python 3.11** installed
- [ ] **FFmpeg** installed (for YouTube support)
- [ ] *(Optional)* **NVIDIA GPU** with CUDA drivers

---

## Step 1: Install Python 3.11

### Windows
1. Download from https://www.python.org/downloads/release/python-3119/
2. Run installer — **tick "Add python.exe to PATH"**
3. Verify: `py -3.11 --version` → `Python 3.11.x`

### Linux (Ubuntu/Debian)
```bash
sudo apt install -y python3.11 python3.11-venv
python3.11 --version
```

### macOS
```bash
brew install python@3.11
python3.11 --version
```

## Step 2: Install FFmpeg (for YouTube support)

### Windows
Download from https://www.gyan.dev/ffmpeg/builds/, add `bin/` to PATH, verify with `ffmpeg -version`.

### Linux
```bash
sudo apt install -y ffmpeg
```

### macOS
```bash
brew install ffmpeg
```

## Step 3: Setup the Project

```bash
cd ai-speech2text-urdu

# Create virtual environment and install dependencies (runs once)
python src/setup_env.py
```

> ⏱ First run takes 5–15 minutes. The model (~1.6 GB) downloads automatically on first transcription.

## Step 4: Activate the Virtual Environment

```bash
venv\Scripts\activate          # Windows
source venv/bin/activate       # Linux / macOS
```

## Step 5: Transcribe Your First File

```bash
# Basic Urdu transcription
python src/transcribe.py trans audio.mp3

# JSON output with metadata
python src/transcribe.py trans audio.mp3 --format json

# English transcription
python src/transcribe.py trans audio.mp3 --language en

# Best accuracy model
python src/transcribe.py trans audio.mp3 --quality accurate

# Force CPU mode
python src/transcribe.py trans audio.mp3 --device cpu

# Audio metadata only (no transcription)
python src/transcribe.py trans audio.mp3 --info

# Dry-run (preview without processing)
python src/transcribe.py trans audio.mp3 --dry-run
```

A `.txt` file with the same name appears next to your audio file.

## Step 6: Transcribe YouTube Videos (Optional)

```bash
# Default Urdu transcription
python src/youtube_transcribe.py https://youtube.com/watch?v=XXXXX

# English + JSON output
python src/youtube_transcribe.py URL -l en -f json

# Custom chunks for long videos
python src/youtube_transcribe.py URL --chunk 45
```

## Step 7: Batch Process a Folder

```bash
# All files in folder (recursively)
python src/transcribe.py batch ./folder/

# With parallel workers
python src/transcribe.py batch ./folder/ -w 4

# JSON format for all
python src/transcribe.py batch ./folder/ -f json
```

---

## Quick Command Reference

| Task | Command |
|------|---------|
| Single transcription | `python src/transcribe.py trans audio.mp3` |
| Batch mode | `python src/transcribe.py batch ./folder/` |
| YouTube | `python src/youtube_transcribe.py URL` |
| Show config | `python src/transcribe.py config show` |
| Update config | `python src/transcribe.py config set language=en` |
| Download model | `python src/download_model.py` |
| Urdu correction | `python src/urdu_correction.py` |

---

## Key Flags

| Flag | Purpose |
|------|---------|
| `--format txt/json/docx` | Output format |
| `--language en/hi/ar` | Transcription language |
| `--quality fast/turbo/accurate` | Speed vs. accuracy tradeoff |
| `--spell` | Urdu spell correction |
| `--chunk SEC` | Custom chunk size for long files |
| `-w N` / `--workers N` | Parallel workers (batch mode) |
| `-q` | Quiet mode (JSON output) |
| `--dry-run` | Preview without processing |

---

## Performance Reference

| Hardware | 10-min audio takes |
|----------|-------------------|
| NVIDIA GPU (RTX 3060+) | ~40–120 seconds |
| CPU — modern 8-core | ~5–10 minutes |
| CPU — older / 4-core | ~10–30 minutes |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `python` not recognized | Re-install Python, tick **"Add to PATH"** |
| `ffmpeg` not recognized | Add FFmpeg's `bin/` folder to PATH |
| GPU not detected | Verify NVIDIA driver (`nvidia-smi`) |
| Out of Memory on GPU | Use `--device cpu` |
| Model download fails | Check internet; set proxy environment variable |

---

## Next Steps

- Read [FEATURES.md](FEATURES.md) for the complete feature reference
- See [USAGE.md](USAGE.md) for testable examples of every feature split into 20 sections
- Check [CHANGELOG.md](CHANGELOG.md) for version history
