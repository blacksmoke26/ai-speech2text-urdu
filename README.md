# Urdu Speech-to-Text Transcription Tool

Transcribe Urdu (or any language) audio files and YouTube videos to text using a fine-tuned Whisper model.  
Works on **Windows**, **Linux**, and **macOS** — GPU recommended but not required.

### Model: `kingabzpro/whisper-large-v3-turbo-urdu`

Trained on Mozilla Common Voice 17.0 (Urdu) with these metrics:

| Metric | Score |
|--------|-------|
| WER (Word Error Rate) | 26.23% ↓ lower is better |
| CER (Character Error Rate) | 8.80% ↓ |
| BLEU | 58.03% ↑ higher is better |
| ChrF | 81.64 ↑ |

---

## Quick Links

| Doc | Description |
|-----|-------------|
| [README.md](README.md) — this file | Setup, features overview, usage examples |
| [QUICKSTART.md](QUICKSTART.md) | Step-by-step walkthrough for first-time users |
| [FEATURES.md](FEATURES.md) | Complete feature reference with tables |
| [USAGE.md](USAGE.md) | Every feature tested via 20 sections of cross-platform `.sh` scripts |
| [CHANGELOG.md](CHANGELOG.md) | Version history and what changed |

---

## System Requirements

### OS Support

| Platform | Supported Versions | Notes |
|----------|-------------------|-------|
| **Windows** | 10 (22H2+) / 11 (64-bit) | Full support |
| **Linux** | Ubuntu 20.04+, Debian 11+, or any distro with Python 3.11 + shared libraries | Full support |
| **macOS** | 12 (Monterey+) on Apple Silicon (M1/M2/M3) | CPU only; NVIDIA GPUs not available |

### Hardware

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| **CPU** | 4-core | 8-core+ (i7 / Ryzen 7 or better) |
| **GPU (optional)** | NVIDIA RTX 3060+ with CUDA 12.1+ | More VRAM = faster transcription |
| **RAM** | 8 GB | 16 GB+ |
| **Disk space** | 5 GB | 10 GB (model + cache + audio files) |
| **VRAM (GPU mode)** | 4 GB | 6 GB+ |

### Approximate Speed

| Hardware | Speed | 10-minute audio takes |
|----------|-------|------------------------|
| NVIDIA GPU (RTX 3060+) | 5–15× real-time | ~40–120 seconds |
| CPU — modern 8-core | 1–2× real-time | ~5–10 minutes |
| CPU — older / 4-core | 0.3–1× real-time | ~10–30 minutes |

> **Real-time** = a 60-second audio clip transcribes in ~60 seconds at 1× speed.

---

## Prerequisites Checklist

- [ ] **Python 3.11** — install from https://www.python.org/downloads/
- [ ] **FFmpeg** — needed for YouTube/audio format conversion (see install instructions below)
- [ ] *(Optional)* **NVIDIA GPU** with CUDA drivers — enables fast GPU transcription

---

## Install FFmpeg

Needed for YouTube support and audio format handling. Skip if you only transcribe local files.

### Windows
1. Download from: https://www.gyan.dev/ffmpeg/builds/
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to your system PATH
4. Verify: `ffmpeg -version`

### Linux (Ubuntu/Debian)
```bash
sudo apt install -y ffmpeg
ffmpeg -version
```

### macOS
```bash
brew install ffmpeg
ffmpeg -version
```

---

## File Structure

```
urdu-audio2text/
│
├── src/
│   ├── transcribe.py               ← Main transcription engine (~1500 lines)
│   ├── youtube_transcribe.py       ← YouTube download + transcribe
│   ├── urdu_correction.py          ← Urdu spell/word correction module
│   ├── download_model.py           ← Manual model download for offline use
│   ├── setup_env.py                ← One-time environment setup (venv + deps)
│   └── utils/
│       ├── audio_splitter.py       ← Audio splitting / merging utilities
│       └── __init__.py             ← Package init with public API exports
├── run_transcribe.sh               ← Cross-platform shell wrapper (single file)
├── run_batch.sh                    ← Cross-platform shell wrapper (batch mode)
├── run_youtube.sh                  ← Cross-platform shell wrapper (YouTube)
├── download_model.sh               ← Shell wrapper for model download
├── setup_env.sh                    ← Shell wrapper for environment setup
├── requirements.txt                ← Python dependencies
│
├── transcribe_config.json          ← Config file (auto-created on first use)
├── .transcribe_cache.json          ← File hash cache (auto-created)
├── .batch_status.json              ← Batch completion tracking (auto-created)
├── youtube_downloads/              ← Downloaded YouTube audio (auto-created)
│
├── venv/                           ← Virtual environment (created by setup)
├── samples/                        ← Sample audio files for testing
│
├── README.md                       ← This file
├── QUICKSTART.md                   ← Step-by-step walkthrough
├── FEATURES.md                     ← Complete feature reference
├── USAGE.md                        ← Every feature tested via .sh scripts
├── CHANGELOG.md                    ← Version history
└── LICENSE                         ← Apache 2.0
```

---

## Step-by-Step Setup

### Step 1: Install Python 3.11

#### Windows
1. Download from: https://www.python.org/downloads/release/python-3119/
2. Run the installer — **tick "Add python.exe to PATH"** during install
3. Verify: `py -3.11 --version` → should show `Python 3.11.x`

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install -y python3.11 python3.11-venv python3.11-dev
python3.11 --version
```

#### macOS (Homebrew)
```bash
brew install python@3.11
python3.11 --version
```

### Step 2: Run One-Time Setup

This creates a virtual environment and installs all dependencies.

#### Any Platform
```bash
cd urdu-audio2text
python src/setup_env.py
```

**What this does:**
1. Verifies Python 3.11 is available
2. Creates a virtual environment in `venv/`
3. Detects hardware (NVIDIA GPU → CUDA build, otherwise CPU)
4. Installs PyTorch, transformers, accelerate, librosa, soundfile, yt-dlp, etc.

> ⏱ First run takes 5–15 minutes depending on internet speed. The model (~1.6 GB) downloads automatically on first transcription.

### Step 3: Transcribe Your First Audio File

```bash
# Activate the virtual environment first
venv\Scripts\activate          # Windows
source venv/bin/activate       # Linux / macOS

# Basic transcription (Urdu default)
python src/transcribe.py trans audio.mp3

# That's it — a .txt file appears next to your audio file.
```

---

## Core Commands Reference

### Single-File Transcription

```bash
python src/transcribe.py trans audio.mp3                     # Urdu (default)
python src/transcribe.py trans audio.mp3 --language en       # English
python src/transcribe.py trans audio.mp3 --format json        # JSON with metadata
python src/transcribe.py trans audio.mp3 --quality fast      # Faster, lower quality
python src/transcribe.py trans audio.mp3 --quality accurate  # Best accuracy
python src/transcribe.py trans audio.mp3 --info              # Audio metadata only
python src/transcribe.py trans audio.mp3 --dry-run           # Preview without processing
python src/transcribe.py trans audio.mp3 --spell             # Apply Urdu spell correction
python src/transcribe.py trans audio.mp3 --chunk 45          # Split into 45s chunks
python src/transcribe.py trans audio.mp3 -q                  # Quiet mode (JSON to stdout)
python src/transcribe.py trans audio.mp3 --no-cache          # Force re-transcription
python src/transcribe.py trans audio.mp3 -o output.txt       # Custom output path
```

### Batch Transcription

```bash
python src/transcribe.py batch ./folder/                     # All files in folder
python src/transcribe.py batch ./folder/ -w 4                # 4 parallel workers
python src/transcribe.py batch ./folder/ -f json              # JSON for all files
python src/transcribe.py batch ./folder/ --spell             # With spell correction
python src/transcribe.py batch ./folder/ --dry-run-batch     # Preview what would happen
```

### YouTube Transcription

```bash
python src/youtube_transcribe.py https://youtube.com/watch?v=XXXXX    # Urdu (default)
python src/youtube_transcribe.py URL -l en                             # English
python src/youtube_transcribe.py URL -f json                            # JSON output
python src/youtube_transcribe.py URL --chunk 45                        # Custom chunks
python src/youtube_transcribe.py URL -q                                # Quiet mode
```

### Configuration

```bash
python src/transcribe.py config show                       # View current config
python src/transcribe.py config set language=en format=json # Update settings
```

### Model Management

```bash
python src/download_model.py                               # Download default model
python src/download_model.py openai/whisper-large-v3-turbo # Specific model
python src/download_model.py --output ./models             # Custom cache path
```

---

## Supported Audio Formats

| Extension | Format | Notes |
|-----------|--------|-------|
| `.mp3` | MP3 | Most common, lossy compression |
| `.wav` | WAV | Uncompressed, best quality |
| `.flac` | FLAC | Lossless compression |
| `.ogg` | OGG | Open-source format |
| `.m4a` | M4A | Apple audio format |
| `.aac` | AAC | AAC audio |
| `.mp4` | MP4 | Video file (audio extracted via FFmpeg) |
| `.webm` | WebM | Web video/audio |
| `.wma` | WMA | Windows Media Audio |

## Output Formats

| Format | Extension | Use Case |
|--------|-----------|----------|
| Plain text | `.txt` (default) | Copy/paste, editing |
| JSON | `.json` | Programmatic use, APIs |
| JSONL | `.jsonl` (batch only) | One JSON object per line per file |
| DOCX | `.docx` | Formatted Word document |

---

## Long-Form Transcription (Chunked Pipeline)

Audio files longer than 60 seconds are automatically split into 55-second chunks for accurate transcription:

```
Long audio → ffmpeg splits → parallel GPU chunks → merge with deduplication → final text
```

| Feature | Detail |
|---------|--------|
| **Splitting** | Audio-level splitting via ffmpeg (precise, not mel-frame math) |
| **Chunk size** | Default: 55s, configurable with `--chunk SEC` |
| **Overlap** | 3-second overlap prevents boundary artifacts |
| **Parallel** | GPU parallel processing via `ProcessPoolExecutor` |
| **Deduplication** | Last N words of each chunk's overlap dropped during merge |

Videos longer than 60s auto-split. Use `--chunk 0` to disable, or `--chunk 45` for custom size.

---

## Urdu Spell Correction

Built-in correction system for common Urdu transcription errors:

- Dictionary-based corrections (e.g., `ہیے` → `هے`, `کریا` → `کیا`)
- Pattern-based fixes (whitespace, double characters, punctuation)
- Character normalization (Arabic/Persian → Urdu equivalents)
- Three levels: basic / medium / full

```bash
python src/transcribe.py trans audio.mp3 --spell          # Apply during transcription
python src/urdu_correction.py                              # Run standalone demo
```

---

## Configuration System

Persistent defaults in `transcribe_config.json`:

```json
{
  "model": "kingabzpro/whisper-large-v3-turbo-urdu",
  "language": "ur",
  "device": null,
  "format": "txt",
  "quality": "turbo",
  "workers": 1,
  "auto_punctuate": true
}
```

CLI flags always override config values. Use `config show` / `config set key=value` to manage it.

---

## Environment Variables

Override behavior via `.env` file in `src/` directory:

| Variable | Default | Description |
|----------|---------|-------------|
| `HF_MODEL_ID` | model ID | HuggingFace model to use |
| `CHUNK_DURATION_S` | `55` | Audio chunk size (seconds) |
| `CHUNK_OVERLAP_S` | `3` | Overlap between chunks (seconds) |
| `MAX_AUDIO_BEFORE_SPLIT_S` | `60` | Auto-split threshold |
| `DEDUP_WORDS` | `20` | Overlap words to drop during merge |
| `PARALLEL_ENABLED` | `true` | Enable parallel processing |
| `WORKERS_PER_CPU` | `1` | Workers per CPU core |

---

## Example Output

**Input:** `speech.mp3` (an Urdu sentence)

```
============================================================
  Urdu Speech Recognition
  Model : kingabzpro/whisper-large-v3-turbo-urdu
  Input : speech.mp3
  Output: speech.txt
============================================================

--- Audio Info ---
  File       : speech.mp3
  Size       : 2.45 MB
  Duration   : 12.80s
  Sample Rate: 44100 Hz
  Channels   : 2
------------------

[1/4] Loading model ...
Loading: 100%|██████████| 5/5 [00:32<00:00,  6.42s/it]
[2/4] Transcribing audio ...
      Done in 4.2s
      Speed ratio: 3.05× real-time (↑ faster than playback)

--- Transcription ---
دیکھیے پانی کب تک بہتا اور مچھلی کب تک تیرتی ہے
--------------------

[4/4] Saving output ...
[OK]  Transcription saved to: speech.txt
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `python` not recognized | Re-install Python, tick **"Add to PATH"** |
| `ffmpeg` not recognized | Add FFmpeg's `bin/` folder to PATH |
| GPU not detected | Verify NVIDIA driver; run `nvidia-smi` |
| Out of Memory on GPU | Use `--device cpu` |
| Model download fails | Check internet; set proxy: `set HTTPS_PROXY=http://proxy:port` (Windows) or export HTTPS_PROXY=... (Linux/macOS) |
| Audio won't load | Convert to WAV with Audacity or FFmpeg |

---

## License

The model is released under the **Apache 2.0 License**.  
See: https://huggingface.co/kingabzpro/whisper-large-v3-turbo-urdu
