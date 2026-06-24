# Usage Guide — Test Every Feature

Every parameter, flag, config option, environment variable, and edge case covered with terminal commands via `sh` shell script wrappers. Urdu is the primary language.

---

## Table of Contents

1. [Setup & Prerequisites](#1-setup--prerequisites)
2. [Single-File Transcription — Basic Commands](#2-single-file-transcription---basic-commands)
3. [Single-File Transcription — All Output Formats](#3-single-file-transcription---all-output-formats)
4. [Single-File Transcription — Quality Presets & Custom Models](#4-single-file-transcription---quality-presets--custom-models)
5. [Single-File Transcription — Language & Device Overrides](#5-single-file-transcription---language--device-overrides)
6. [Single-File Transcription — Info, Dry-Run, Quiet, Cache](#6-single-file-transcription---info-dry-run-quiet-cache)
7. [Single-File Transcription — Chunked Long-Form](#7-single-file-transcription---chunked-long-form)
8. [Single-File Transcription — Urdu Spell Correction](#8-single-file-transcription---urdu-spell-correction)
9. [Single-File Transcription — Combined Flags (Full Combinations)](#9-single-file-transcription---combined-flags-full-combinations)
10. [Batch Transcription — Basic](#10-batch-transcription---basic)
11. [Batch Transcription — Parallel Workers & Threading](#11-batch-transcription---parallel-workers--threading)
12. [Batch Transcription — All Formats](#12-batch-transcription---all-formats)
13. [Batch Transcription — Cache, Spell, Resume](#13-batch-transcription---cache-spell-resume)
14. [Batch Transcription — Combined Flags (Full Combinations)](#14-batch-transcription---combined-flags-full-combinations)
15. [YouTube Transcription — Basic Download + Transcribe](#15-youtube-transcription---basic-download--transcribe)
16. [YouTube Transcription — Output Formats & Quality](#16-youtube-transcription---output-formats--quality)
17. [YouTube Transcription — Chunk Control & Parallel](#17-youtube-transcription---chunk-control--parallel)
18. [YouTube Transcription — Combined Flags (Full Combinations)](#18-youtube-transcription---combined-flags-full-combinations)
19. [Configuration System — Persistent Defaults](#19-configuration-system---persistent-defaults)
20. [Model Management — Download & Offline Use](#20-model-management---download--offline-use)
21. [Environment Variables — Full .env Reference](#21-environment-variables---full-env-reference)
22. [Urdu Correction Module — Standalone API](#22-urdu-correction-module---standalone-api)
23. [Error Handling & Edge Cases](#23-error-handling--edge-cases)
24. [Hidden / Undocumented Features](#24-hidden--undocumented-features)
25. [Shell Script Wrappers — All Scripts](#25-shell-script-wrappers---all-scripts)
26. [Quick Reference Card — Every Flag Mapped](#26-quick-reference-card---every-flag-mapped)

---

## 1. Setup & Prerequisites

### Install dependencies and verify environment
```sh
sh setup_env.sh
```

---

## 2. Single-File Transcription — Basic Commands

### Default Urdu transcription (TXT output, auto-detect device)
```sh
sh run_transcribe.sh samples/sample.mp3
```

### Specify custom output path
```sh
sh run_transcribe.sh samples/sample.mp3 ./output.txt
```

### Transcribe WAV file
```sh
sh run_transcribe.sh samples/sample.wav
```

### Transcribe FLAC file (lossless)
```sh
sh run_transcribe.sh samples/sample.flac
```

### Transcribe OGG file
```sh
sh run_transcribe.sh samples/sample.ogg
```

### Transcribe M4A file (Apple audio)
```sh
sh run_transcribe.sh samples/sample.m4a
```

### Transcribe AAC file
```sh
sh run_transcribe.sh samples/sample.aac
```

### Transcribe MP4 video (audio extracted via FFmpeg)
```sh
sh run_transcribe.sh samples/sample.mp4
```

### Transcribe WebM file (web video/audio)
```sh
sh run_transcribe.sh samples/sample.webm
```

---

## 3. Single-File Transcription — All Output Formats

### TXT output (default — plain text, most compatible)
```sh
sh run_transcribe.sh samples/sample.mp3 txt
```

### JSON output (transcription + metadata: model, language, duration, timestamp)
```sh
sh run_transcribe.sh samples/sample.mp3 json
```

### DOCX output (formatted Word document with metadata paragraph)
```sh
sh run_transcribe.sh samples/sample.mp3 docx
```

---

## 4. Single-File Transcription — Quality Presets & Custom Models

### Fast quality preset (distil-medium model, fastest inference)
```sh
sh run_transcribe.sh samples/sample.mp3 txt --quality fast
```

### Turbo quality preset (default Urdu model, balanced speed/accuracy)
```sh
sh run_transcribe.sh samples/sample.mp3 txt --quality turbo
```

### Accurate quality preset (openai whisper-large-v3-turbo, slowest best accuracy)
```sh
sh run_transcribe.sh samples/sample.mp3 txt --quality accurate
```

### Custom HuggingFace model ID
```sh
sh run_transcribe.sh samples/sample.mp3 txt --model kingabzpro/whisper-large-v3-turbo-urdu
```

---

## 5. Single-File Transcription — Language & Device Overrides

### Force Urdu language
```sh
sh run_transcribe.sh samples/sample.mp3 txt --language ur
```

### Force CPU device (CPU mode is always available)
```sh
sh run_transcribe.sh samples/sample.mp3 txt --device cpu
```

### Auto-detect device (default behavior)
```sh
sh run_transcribe.sh samples/sample.mp3 txt
```

---

## 6. Single-File Transcription — Info, Dry-Run, Quiet, Cache

### Show audio metadata only (no transcription)
```sh
sh run_transcribe.sh samples/sample.mp3 txt --info
```

### Dry-run preview (shows cache status, estimated time, model — no processing)
```sh
sh run_transcribe.sh samples/sample.mp3 txt --dry-run
```

### Bypass cache (force fresh transcription regardless of hash)
```sh
sh run_transcribe.sh samples/sample.mp3 txt --no-cache
```

### Quiet mode (minimal JSON output to stdout — pipe to scripts/APIs)
```sh
sh run_transcribe.sh samples/sample.mp3 txt -q
```

---

## 7. Single-File Transcription — Chunked Long-Form

### Auto-chunk long audio (>60s threshold, splits into 55s chunks with 3s overlap)
```sh
sh run_transcribe.sh samples/long_audio.mp3 txt --chunk 55
```

### Manual chunk duration (45-second chunks)
```sh
sh run_transcribe.sh samples/sample.mp3 txt --chunk 45
```

### Disable chunking entirely (force single-file processing even for long audio)
```sh
sh run_transcribe.sh samples/long_audio.mp3 txt --chunk 0
```

---

## 8. Single-File Transcription — Urdu Spell Correction

### Apply Urdu spell/word correction during transcription
```sh
sh run_transcribe.sh samples/sample.mp3 txt --spell
```

### Short flag for spell correction
```sh
sh run_transcribe.sh samples/sample.mp3 txt -s
```

### Spell correction with JSON output
```sh
sh run_transcribe.sh samples/sample.mp3 json --spell
```

### Spell correction with accurate quality model
```sh
sh run_transcribe.sh samples/sample.mp3 txt --spell --quality accurate
```

### Run standalone Urdu correction module demo
```sh
python src/urdu_correction.py
```

---

## 9. Single-File Transcription — Combined Flags (Full Combinations)

### Spell + turbo quality + JSON output + custom path
```sh
sh run_transcribe.sh samples/sample.mp3 ./result.txt --spell -f json -m turbo
```

### Accurate quality + Urdu language + dry-run (preview only)
```sh
sh run_transcribe.sh samples/sample.mp3 txt -l ur -q --dry-run
```

### Fast quality + custom model + output path + no-cache
```sh
sh run_transcribe.sh samples/sample.mp3 ./fast.txt -f txt -m kingabzpro/whisper-large-v3-turbo-urdu -o ./output.txt --no-cache
```

### Chunked + spell correction + accurate quality
```sh
sh run_transcribe.sh samples/long_audio.mp3 txt --spell --quality accurate --chunk 50
```

### Info display with specific model override
```sh
sh run_transcribe.sh samples/sample.mp3 txt -m kingabzpro/whisper-large-v3-turbo-urdu --info
```

---

## 10. Batch Transcription — Basic

### Process all files in folder (TXT format, default settings)
```sh
sh run_batch.sh samples/ txt
```

### JSONL output (one JSON object per line per file, batch only)
```sh
sh run_batch.sh samples/ jsonl
```

### JSON output with metadata for each file
```sh
sh run_batch.sh samples/ json
```

### DOCX Word documents for each file
```sh
sh run_batch.sh samples/ docx
```

### Dry-run batch (preview without processing)
```sh
sh run_batch.sh samples/ txt --dry-run-batch samples/
```

---

## 11. Batch Transcription — Parallel Workers & Threading

### Auto-detect optimal worker count (default)
```sh
sh run_batch.sh samples/ txt --workers 0
```

### Force specific worker count (4 parallel workers)
```sh
sh run_batch.sh samples/ txt -w 4
```

### Single worker (sequential processing)
```sh
sh run_batch.sh samples/ txt -w 1
```

### Force parallel processing override (overrides PARALLEL_ENABLED=false in .env)
```sh
sh run_batch.sh samples/ txt --parallel
```

### Disable parallel processing completely
```sh
sh run_batch.sh samples/ txt --no-parallel
```

---

## 12. Batch Transcription — All Formats

### TXT batch output (default)
```sh
sh run_batch.sh samples/ txt
```

### JSONL batch output (single file with one JSON object per line)
```sh
sh run_batch.sh samples/ jsonl
```

### JSON batch output (each file gets .json)
```sh
sh run_batch.sh samples/ json
```

### DOCX batch output (each file gets .docx)
```sh
sh run_batch.sh samples/ docx
```

---

## 13. Batch Transcription — Cache, Spell, Resume

### First batch run (cache miss — processes all files)
```sh
sh run_batch.sh samples/ txt
```

### Second batch run (auto-resume — skips already-completed files via .batch_status.json)
```sh
sh run_batch.sh samples/ txt
```

### Force fresh processing of all files (bypass cache)
```sh
sh run_batch.sh samples/ txt --no-cache
```

### Batch with Urdu spell correction applied to every file
```sh
sh run_batch.sh samples/ txt --spell
```

---

## 14. Batch Transcription — Combined Flags (Full Combinations)

### JSON output + 4 workers + no-cache + spell correction
```sh
sh run_batch.sh samples/ json -w 4 --no-cache --spell
```

### DOCX output + force parallel + dry-run preview first
```sh
sh run_batch.sh samples/ docx -m kingabzpro/whisper-large-v3-turbo-urdu --dry-run-batch samples/
```

### JSONL + custom language + workers + no-parallel
```sh
sh run_batch.sh samples/ jsonl -w 2 --no-parallel
```

---

## 15. YouTube Transcription — Basic Download + Transcribe

### Download audio from YouTube and transcribe to Urdu (default)
```sh
sh run_youtube.sh https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

### List downloaded audio files in output directory
```sh
ls -la youtube_downloads/
```

---

## 16. YouTube Transcription — Output Formats & Quality

### JSON output with metadata
```sh
sh run_youtube.sh https://www.youtube.com/watch?v=VIDEO_ID -f json
```

### DOCX Word document output
```sh
sh run_youtube.sh https://www.youtube.com/watch?v=VIDEO_ID -f docx
```

### Accurate quality model (whisper-large-v3-turbo)
```sh
sh run_youtube.sh https://www.youtube.com/watch?v=VIDEO_ID -m accurate
```

### Custom output file path
```sh
sh run_youtube.sh https://www.youtube.com/watch?v=VIDEO_ID -o ./custom_result.txt
```

### Quiet mode (minimal JSON to stdout)
```sh
sh run_youtube.sh https://www.youtube.com/watch?v=VIDEO_ID -q
```

### Custom chunk duration (45 seconds per chunk)
```sh
sh run_youtube.sh https://www.youtube.com/watch?v=VIDEO_ID --chunk 45
```

---

## 17. YouTube Transcription — Chunk Control & Parallel

### Auto-chunk for long videos (>60s threshold, splits into 55s chunks automatically)
```sh
sh run_youtube.sh https://www.youtube.com/watch?v=LONG_VIDEO_ID
```

### Custom chunk size (45 seconds per chunk)
```sh
sh run_youtube.sh https://www.youtube.com/watch?v=LONG_VIDEO_ID --chunk 45
```

### Disable chunking entirely (process as single file even for long videos)
```sh
sh run_youtube.sh https://www.youtube.com/watch?v=MEDIUM_VIDEO_ID --chunk 0
```

### Disable GPU parallel processing for chunks (sequential processing)
```sh
sh run_youtube.sh https://www.youtube.com/watch?v=LONG_VIDEO_ID --no-parallel
```

### Chunked + JSON output with custom chunk size
```sh
sh run_youtube.sh https://www.youtube.com/watch?v=LONG_VIDEO_ID -f json --chunk 50
```

---

## 18. YouTube Transcription — Combined Flags (Full Combinations)

### Urdu transcription + accurate quality + JSON + custom output + 45s chunks + no-parallel
```sh
sh run_youtube.sh https://www.youtube.com/watch?v=VIDEO_ID -m accurate -f json -o ./yt_result.json --chunk 45 --no-parallel
```

### Accurate model + quiet mode + DOCX output
```sh
sh run_youtube.sh https://www.youtube.com/watch?v=VIDEO_ID -m accurate -q -f docx
```

---

## 19. Configuration System — Persistent Defaults

### Show current configuration values
```sh
sh run_transcribe.sh config show
```

### Set model (HuggingFace model ID)
```sh
sh run_transcribe.sh config set model=kingabzpro/whisper-large-v3-turbo-urdu
```

### Check config after setting model
```sh
sh run_transcribe.sh config show
```

### Set language (e.g., ur, en, hi, ar)
```sh
sh run_transcribe.sh config set language=ur
```

### Set default output format (txt, json, jsonl, docx)
```sh
sh run_transcribe.sh config set format=json
```

### Check config after setting format
```sh
sh run_transcribe.sh config show
```

### Set quality preset (fast, turbo, accurate)
```sh
sh run_transcribe.sh config set quality=accurate
```

### Enable auto-punctuation (adds periods after Urdu sentence-ending patterns)
```sh
sh run_transcribe.sh config set auto_punctuate=true
```

### Disable auto-punctuation
```sh
sh run_transcribe.sh config set auto_punctuate=false
```

### Set batch default worker count
```sh
sh run_transcribe.sh config set workers=4
```

### Set device (cpu, gpu, or null for auto-detect)
```sh
sh run_transcribe.sh config set device=cpu
```

### Check config after setting device
```sh
sh run_transcribe.sh config show
```

### CLI flags always override config values (example: force Urdu even if config has en)
```sh
sh run_transcribe.sh samples/sample.mp3 txt -l ur --dry-run
```

### Reset config to factory defaults via direct file edit
```sh
cat > transcribe_config.json << 'EOF'
{
  "model": "kingabzpro/whisper-large-v3-turbo-urdu",
  "language": "ur",
  "device": null,
  "format": "txt",
  "quality": "turbo",
  "workers": 1,
  "auto_punctuate": true
}
EOF
```

### Verify config reset to defaults
```sh
sh run_transcribe.sh config show
```

---

## 20. Model Management — Download & Offline Use

### Download default Urdu model to HuggingFace cache (~1.6 GB)
```sh
sh download_model.sh
```

### Download a specific model by ID
```sh
sh download_model.sh kingabzpro/whisper-large-v3-turbo-urdu
```

### Download model to custom local directory
```sh
sh download_model.sh --output ./models
```

### Verify offline access works after download
```sh
sh run_transcribe.sh samples/sample.mp3 txt --dry-run
```

---

## 21. Environment Variables — Full .env Reference

Edit `src/.env` to override all behaviors:

### Full .env with all variables set to defaults
```sh
cat > src/.env << 'EOF'
# Model selection
HF_MODEL_ID=kingabzpro/whisper-large-v3-turbo-urdu

# Audio chunking settings (long-form pipeline)
CHUNK_DURATION_S=55
CHUNK_OVERLAP_S=3
MAX_AUDIO_BEFORE_SPLIT_S=60

# YouTube download settings
MIN_AUDIO_DURATION_S=10
YOUTUBE_MIN_DURATION_S=10
PARALLEL_ENABLED=true
MAX_WORKERS=0
WORKERS_PER_CPU=1
YTDLP_NO_PROGRESS=
YOUTUBE_OUTPUT_DIR=youtube_downloads
YOUTUBE_AUDIO_EXTENSIONS=.mp3,.wav,.flac,.ogg,.m4a,.aac

# Deduplication (overlap text collapse during chunk merge)
DEDUP_WORDS=20
LAST_CHUNK_DURATION_SRT=60.0
EOF
```

### Verify .env values loaded by the application
```sh
cat src/.env | grep -v '^#' | grep -v '^$'
```

### Override only chunk duration and overlap (partial .env)
```sh
cat > src/.env << 'EOF'
CHUNK_DURATION_S=30
CHUNK_OVERLAP_S=5
MAX_AUDIO_BEFORE_SPLIT_S=45
DEDUP_WORDS=10
PARALLEL_ENABLED=true
WORKERS_PER_CPU=2
EOF
```

### Disable parallel processing and YouTube progress suppression via .env
```sh
cat > src/.env << 'EOF'
PARALLEL_ENABLED=false
YTDLP_NO_PROGRESS=1
MAX_WORKERS=4
WORKERS_PER_CPU=1
EOF
```

### Reset .env to full defaults
```sh
cat > src/.env << 'EOF'
HF_MODEL_ID=kingabzpro/whisper-large-v3-turbo-urdu
CHUNK_DURATION_S=55
CHUNK_OVERLAP_S=3
MAX_AUDIO_BEFORE_SPLIT_S=60
MIN_AUDIO_DURATION_S=10
YOUTUBE_MIN_DURATION_S=10
PARALLEL_ENABLED=true
MAX_WORKERS=0
WORKERS_PER_CPU=1
YTDLP_NO_PROGRESS=
YOUTUBE_OUTPUT_DIR=youtube_downloads
YOUTUBE_AUDIO_EXTENSIONS=.mp3,.wav,.flac,.ogg,.m4a,.aac
DEDUP_WORDS=20
LAST_CHUNK_DURATION_SRT=60.0
EOF
```

---

## 22. Urdu Correction Module — Standalone API

### Run the built-in demo with sample corrections
```sh
python src/urdu_correction.py
```

### Use as Python library (import directly)
```sh
python -c "from src.urdu_correction import UrduSpellCorrector; c = UrduSpellCorrector(); print(c.correct('ہیے', level='full'))"
```

---

## 23. Error Handling & Edge Cases

### Non-existent input file
```sh
sh run_transcribe.sh /nonexistent/file.mp3 txt
```

### Invalid YouTube URL format
```sh
sh run_youtube.sh "not_a_url"
```

### JSONL format on single file (not supported — should fail)
```sh
sh run_transcribe.sh samples/sample.mp3 jsonl
```

### Very short audio with tiny chunk size (< threshold)
```sh
sh run_transcribe.sh samples/sample.mp3 txt --chunk 10
```

### Invalid device value (should be rejected by argparse)
```sh
sh run_transcribe.sh samples/sample.mp3 txt --device invalid_device
```

### Unknown subcommand
```sh
sh run_transcribe.sh invalid_cmd
```

### Global help flag
```sh
sh run_transcribe.sh --help
```

### Trans subcommand help
```sh
sh run_transcribe.sh trans --help
```

### Batch on empty directory (zero files to process)
```sh
mkdir -p ./test_empty_dir
sh run_batch.sh ./test_empty_dir/ txt
rm -rf ./test_empty_dir
```

---

## 24. Hidden / Undocumented Features

### Zero-copy audio info (get_audio_info uses soundfile headers — no RAM load)
```sh
sh run_transcribe.sh samples/sample.mp3 txt --info
```

### Singleton model cache (model loaded once, shared across batch — saves 30+ seconds per file)
```sh
sh run_batch.sh samples/ txt -w 4
```

### Speed ratio display (shown after each transcription as X.XX× real-time with arrow)
```sh
sh run_transcribe.sh samples/sample.mp3 txt
```

### Duration in HH:MM:SS.mmm format (human-readable audio info panel)
```sh
sh run_transcribe.sh samples/sample.mp3 txt --info
```

### Graceful Ctrl+C handling (catches keyboard interrupts, cleans up yt-dlp trees)
```sh
sh run_youtube.sh https://www.youtube.com/watch?v=LONG_VIDEO_ID
```

### Batch status tracking via .batch_status.json (UTC-timestamped completion — restart skips completed files)
```sh
sh run_batch.sh samples/ txt
sh run_batch.sh samples/ txt
```

### Garbage repetition filter (detects and collapses transcription artifacts like repeated phrases or stuck audio loops)
```sh
sh run_transcribe.sh samples/sample.mp3 txt --spell
```

---

## 25. Shell Script Wrappers — All Scripts

Five cross-platform shell scripts (Windows Git Bash / WSL, Linux, macOS):

### setup_env.sh — one-time environment setup
```sh
sh setup_env.sh
```

### run_transcribe.sh — single-file transcription wrapper
```sh
sh run_transcribe.sh samples/sample.mp3
```

### run_batch.sh — batch folder processing wrapper
```sh
sh run_batch.sh samples/ txt
```

### run_youtube.sh — YouTube download + transcribe wrapper
```sh
sh run_youtube.sh https://www.youtube.com/watch?v=VIDEO_ID
```

### download_model.sh — model download for offline use
```sh
sh download_model.sh
```

---

## 26. Quick Reference Card — Every Flag Mapped

```
┌─────────────────────────────────────────────────────────────────────┐
│                 EVERY FLAG / PARAMETER MAPPED                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  SETUP                                                              │
│    sh setup_env.sh                  Environment setup              │
│                                                                     │
│  SINGLE FILE (trans)                                                │
│    trans <file>                     Basic Urdu transcription        │
│    trans <file> -o <path>          Custom output path              │
│    trans <file> txt                 TXT format output               │
│    trans <file> json                JSON output with metadata       │
│    trans <file> docx                DOCX Word document output       │
│    trans <file> -l ur               Urdu language override          │
│    trans <file> -q                  Quiet mode (JSON to stdout)     │
│    trans <file> -m <model_id>      Custom HuggingFace model         │
│    trans <file> --quality fast      Fast preset (distil-medium)     │
│    trans <file> --quality turbo     Turbo preset (default Urdu)     │
│    trans <file> --quality accurate  Accurate preset (whisper-lv3-t)  │
│    trans <file> --info              Audio metadata only             │
│    trans <file> --dry-run           Preview without processing      │
│    trans <file> --spell or -s       Urdu spell/word correction      │
│    trans <file> --chunk 55          Chunk into 55s segments         │
│    trans <file> --chunk 0           Disable chunking                │
│    trans <file> -device cpu         Force CPU device                │
│    trans <file> --no-cache          Bypass cache                    │
│                                                                     │
│  BATCH                                                              │
│    batch <dir>                      Basic batch (all files)        │
│    batch <dir> txt                  TXT output for all              │
│    batch <dir> json                 JSON output for all             │
│    batch <dir> jsonl                JSONL output (single file)      │
│    batch <dir> docx                 DOCX output for all             │
│    batch <dir> -w 4 or --workers 4  4 parallel workers             │
│    batch <dir> -w 0 or --workers 0  Auto-detect workers            │
│    batch <dir> -w 1                 Single worker (sequential)      │
│    batch <dir> --parallel           Force parallel override         │
│    batch <dir> --no-parallel        Disable parallel processing     │
│    batch <dir> --spell or -s       Spell correction on all files   │
│    batch <dir> --no-cache           Bypass cache for all            │
│    batch <dir> --dry-run-batch d    Preview only                    │
│                                                                     │
│  YOUTUBE                                                            │
│    youtube <URL>                    Urdu transcription + download   │
│    youtube <URL> -f json            JSON output                     │
│    youtube <URL> -f docx            DOCX output                     │
│    youtube <URL> -m accurate        Accurate quality model          │
│    youtube <URL> -o <path>         Custom output path               │
│    youtube <URL> -q                 Quiet mode                      │
│    youtube <URL> --chunk 45         Custom chunk duration           │
│    youtube <URL> --chunk 0          Disable chunking                │
│    youtube <URL> --no-parallel      Disable parallel processing     │
│                                                                     │
│  CONFIG                                                             │
│    config show                      View all config values          │
│    config set model=X               Set model                       │
│    config set language=X            Set default language            │
│    config set format=X              Set default format              │
│    config set quality=X             Set default quality preset      │
│    config set workers=N             Set default worker count        │
│    config set auto_punctuate=true   Enable auto-punctuation         │
│    config set device=X              Set default device              │
│                                                                     │
│  MODEL                                                              │
│    sh download_model.sh             Download default model          │
│    sh download_model.sh <id>        Download specific model         │
│    sh download_model.sh -o ./dir    Download to custom path         │
│                                                                     │
│  ENVIRONMENT (.env in src/)                                         │
│    HF_MODEL_ID=<model>              Override default model          │
│    CHUNK_DURATION_S=55              Chunk segment duration (sec)    │
│    CHUNK_OVERLAP_S=3                Chunk overlap (sec)             │
│    MAX_AUDIO_BEFORE_SPLIT_S=60      Auto-split threshold (sec)     │
│    MIN_AUDIO_DURATION_S=10          Min YouTube audio duration (s)  │
│    YOUTUBE_MIN_DURATION_S=10        Alias for above                 │
│    PARALLEL_ENABLED=true            Enable/disable parallel chunks  │
│    MAX_WORKERS=0                    Max parallel workers (0=auto)   │
│    WORKERS_PER_CPU=1                Workers per CPU core            │
│    YTDLP_NO_PROGRESS=               Suppress yt-dlp progress bar    │
│    YOUTUBE_OUTPUT_DIR=youtube_downloads  YouTube audio output dir  │
│    YOUTUBE_AUDIO_EXTENSIONS=...     Allowed YouTube audio extensions│
│    DEDUP_WORDS=20                   Overlap words to collapse       │
│    LAST_CHUNK_DURATION_SRT=60.0     Last SRT chunk fallback (sec)   │
│                                                                     │
│  SHELL SCRIPTS                                                      │
│    sh setup_env.sh                  Setup environment               │
│    sh run_transcribe.sh <f>         Transcribe single file          │
│    sh run_batch.sh <dir>            Batch process folder            │
│    sh run_youtube.sh <URL>          YouTube download + transcribe   │
│    sh download_model.sh             Download model offline          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```
