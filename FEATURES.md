# Features — Urdu Speech-to-Text Transcription Tool

Complete feature reference for every capability in this project.

---

## 1. Single-File Transcription (`trans`)

Core transcription engine for individual audio files.

| Feature | Flag / Option | Description |
|---------|--------------|-------------|
| **Basic transcription** | `python src/transcribe.py trans audio.mp3` | Transcribes to plain text (`.txt`) next to the input file |
| **Custom output path** | `--output <path>` or `-o <path>` | Save transcription to a specific file location |
| **Multiple formats** | `--format txt/json/jsonl/docx` | TXT (default), JSON with metadata, JSONL (batch only), DOCX Word document |
| **Language override** | `--language en` or `-l en` | Transcribe in English, Hindi, Arabic, etc. (default: Urdu) |
| **Quality presets** | `--quality fast/turbo/accurate` | `fast` = distil-medium, `turbo` = default Urdu model, `accurate` = openai whisper-large-v3-turbo |
| **Custom model** | `--model <id>` or `-m <id>` | Use any HuggingFace Whisper model ID |
| **Device override** | `--device cpu/gpu` | Force CPU or GPU mode |
| **Audio info only** | `--info` | Show file size, duration, sample rate, channels — no transcription |
| **Dry-run preview** | `--dry-run` | Preview what would happen without processing |
| **Urdu spell correction** | `--spell` or `-s` | Apply dictionary + pattern-based Urdu text correction |
| **Auto-punctuation** | Config: `auto_punctuate: true` (default) | Heuristic post-processing that adds periods after common Urdu sentence-ending patterns |
| **Chunked long-form** | `--chunk <SEC>` or automatic (>60s) | Splits audio into chunks for accurate transcription of long files |
| **Quiet mode** | `--quiet` or `-q` | Machine-readable JSON output to stdout — pipe to scripts/APIs |
| **Cache control** | `--no-cache` | Force re-transcription even if file hash matches cache |

---

## 2. Batch Transcription (`batch`)

Process entire folders (including subdirectories) of audio files at once.

| Feature | Flag / Option | Description |
|---------|--------------|-------------|
| **Batch process** | `python src/transcribe.py batch <dir>` | Process all audio files in a directory recursively |
| **Batch format** | `--format txt` | Apply format to all files in the batch |
| **Parallel processing** | `--workers 4` or `-w 4` | Use multiple CPU cores for concurrent transcription (CPU mode only) |
| **Auto workers** | `--workers 0` (default) | Auto-detect optimal worker count based on CPU cores |
| **Force parallel** | `--parallel` | Force parallel processing even if disabled by config/env |
| **Disable parallel** | `--no-parallel` | Process files sequentially |
| **Resume support** | Automatic (`.batch_status.json`) | Already-completed files are skipped on restart |
| **Dry-run batch** | `--dry-run-batch <dir>` | Preview which files would be processed without actually running them |
| **Batch spell correction** | `--spell` or `-s` | Apply Urdu spell correction to all batch outputs |
| **JSONL output** | `--format jsonl` | Single JSON Lines file with one object per input file, each containing transcription + metadata |

---

## 3. YouTube Transcription (`youtube_transcribe.py`)

Download audio from any YouTube video and transcribe it in one step.

| Feature | Flag / Option | Description |
|---------|--------------|-------------|
| **Basic YouTube transcribe** | `python src/youtube_transcribe.py <URL>` | Download audio + transcribe to text (Urdu default) |
| **Language override** | `-l en` | Transcribe in a different language |
| **Format output** | `-f json / -f docx` | JSON or Word document output |
| **Quality preset** | `-m accurate` | Use high-quality model |
| **Custom output** | `-o result.txt` | Specify output file path |
| **Chunk control** | `--chunk 45` | Custom chunk duration (e.g., 45-second chunks) |
| **No parallel** | `--no-parallel` | Disable GPU parallel processing for chunks |
| **Quiet mode** | `-q` / `--quiet` | Minimal output |

---

## 4. Long-Form Chunked Pipeline

Automatic chunking for audio files longer than the threshold (default: 60 seconds).

| Feature | Detail |
|---------|--------|
| **Audio-level splitting** | Uses ffmpeg to split audio samples precisely (not mel-spectrogram frames) |
| **Chunk duration** | Default: 55 seconds per chunk |
| **Overlap** | 3-second overlap between consecutive chunks prevents boundary artifacts |
| **GPU parallel processing** | Chunks transcribed concurrently via `ProcessPoolExecutor` on GPU |
| **CPU fallback** | Falls back to `os.cpu_count()` workers on CPU machines |
| **Text deduplication** | Last N words of each chunk's overlap region are dropped during merge (configurable via `DEDUP_WORDS` in `.env`) |
| **Auto-trigger** | Activated automatically for files >60s; disabled for subtitle formats |

---

## 5. Model Management

| Feature | Command / Config | Description |
|---------|-----------------|-------------|
| **Model download** | `python src/download_model.py` | Download the model manually for offline use (~1.6 GB) |
| **Custom cache path** | `python src/download_model.py --output ./models` | Cache model to a custom local directory |
| **Specific model** | `python src/download_model.py kingabzpro/whisper-large-v3-turbo-urdu` | Download a specific model ID |
| **Cached location** | `~/.cache/huggingface/hub/` | Default HuggingFace cache directory |
| **Quality presets → models** | `fast` = distil-medium, `turbo` = default Urdu, `accurate` = whisper-large-v3-turbo | Auto-selects model based on quality flag |

---

## 6. Configuration System

Persistent defaults stored in `transcribe_config.json`.

| Config Key | Default | Description |
|-----------|---------|-------------|
| `model` | `kingabzpro/whisper-large-v3-turbo-urdu` | HuggingFace model ID to use |
| `language` | `ur` | Default transcription language |
| `device` | `null` (auto-detect) | Force device type |
| `format` | `txt` | Default output format |
| `quality` | `turbo` | Speed/quality preset |
| `workers` | `1` | Default worker count for batch mode |
| `auto_punctuate` | `true` | Enable auto-punctuation |

| Command | Description |
|---------|-------------|
| `python src/transcribe.py config show` | Display current configuration |
| `python src/transcribe.py config set model=my-model language=en` | Update one or more settings |

**CLI flags always override config values.**

---

## 7. Urdu Spell & Word Correction (`urdu_correction.py`)

Advanced correction system specifically for Urdu transcription output.

| Feature | Description |
|---------|-------------|
| **Dictionary corrections** | Common misspellings mapped to correct forms (e.g., `ہیے` → `ہے`, `کریا` → `کیا`) |
| **Pattern corrections** | Regex-based fixes for whitespace, double characters, punctuation spacing |
| **Character normalization** | Arabic/Persian characters normalized to Urdu equivalents |
| **Correction levels** | `basic` (patterns only), `medium` (patterns + dictionary), `full` (all three levels) |
| **Confidence scoring** | Returns a confidence score based on correction count vs text length |
| **Correction statistics** | Detailed breakdown of corrections by type (characters, words, patterns) |
| **Usage in transcribe** | `--spell` flag on any `trans` or `batch` command |

---

## 8. Audio Splitting Utilities (`audio_spliter.py`)

Low-level utilities for audio manipulation, used internally by the chunked pipeline.

| Function | Purpose |
|----------|---------|
| `split_audio()` | Split audio into fixed-duration chunks using ffmpeg |
| `merge_text()` | Merge transcribed texts with overlap-aware deduplication |
| `calculate_chunk_start_times()` | Calculate start times for each chunk relative to original audio |

---

## 9. Environment Configuration (`.env`)

Override behavior via `.env` file in `src/` directory.

| Variable | Default | Description |
|----------|---------|-------------|
| `HF_MODEL_ID` | `kingabzpro/whisper-large-v3-turbo-urdu` | HuggingFace model ID |
| `CHUNK_DURATION_S` | `55` | Duration of each audio chunk in seconds |
| `CHUNK_OVERLAP_S` | `3` | Overlap between consecutive chunks in seconds |
| `MAX_AUDIO_BEFORE_SPLIT_S` | `60` | Auto-split threshold in seconds |
| `MIN_AUDIO_DURATION_S` | `10` | Minimum valid audio duration for YouTube downloads |
| `YOUTUBE_MIN_DURATION_S` | Same as above | Alias for YouTube-specific validation |
| `PARALLEL_ENABLED` | `true` | Enable/disable parallel chunk processing |
| `MAX_WORKERS` | `0` (auto) | Maximum parallel workers |
| `WORKERS_PER_CPU` | `1` | Workers per CPU core |
| `YTDLP_NO_PROGRESS` | (empty) | Suppress yt-dlp progress bar |
| `YOUTUBE_OUTPUT_DIR` | `youtube_downloads` | Directory for downloaded YouTube audio |
| `YOUTUBE_AUDIO_EXTENSIONS` | `.mp3,.wav,.flac,.ogg,.m4a,.aac` | Allowed audio extensions from YouTube |
| `DEDUP_WORDS` | `20` | Number of overlap words to drop during text merge |
| `LAST_CHUNK_DURATION_SRT` | `60.0` | Internal constant (legacy) |

---

## 10. Supported Audio Formats

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

---

## 11. Output Formats

| Format | Extension | Use Case | Features |
|--------|-----------|----------|----------|
| **Plain text** | `.txt` (default) | Copy/paste, editing | Merged chunk text with deduplication |
| **JSON** | `.json` | Programmatic use, APIs | Transcription + metadata (model, language, duration, etc.) |
| **JSONL** | `.jsonl` | Batch programmatic use | One JSON object per line per file (batch only) |
| **DOCX** | Word document | Professional documents | Formatted Word file with metadata |

---

## 12. Performance Reference

| Hardware | Approximate Speed | 10-minute audio takes |
|----------|------------------|------------------------|
| NVIDIA GPU (RTX 3060+) | 5–15× real-time | ~40–120 seconds |
| CPU — modern 8-core (i7/Ryzen 7) | 1–2× real-time | ~5–10 minutes |
| CPU — older / 4-core | 0.3–1× real-time | ~10–30 minutes |

> **Real-time** = a 60-second audio clip transcribes in ~60 seconds at 1× speed.

---

## 13. Cross-Platform Shell Scripts

All shell scripts work on Windows (Git Bash / WSL), Linux, and macOS.

| Script | Purpose |
|--------|---------|
| `run_transcribe.sh` | Single-file transcription via CLI wrapper |
| `run_batch.sh` | Batch process a folder of audio files |
| `run_youtube.sh` | YouTube download + transcribe wrapper |
| `download_model.sh` | Download model for offline use |
| `setup_env.sh` | One-time environment setup |

**Auto-detection**: Scripts find the venv Python on both Windows (`venv/Scripts/python.exe`) and Unix (`venv/bin/python`).

---

## 14. System Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| **OS** | Windows 10 / Linux (Ubuntu 20.04+) / macOS 12+ | Latest supported version |
| **Python** | 3.11.x | 3.11.x |
| **RAM** | 8 GB | 16 GB+ |
| **Disk space** | 5 GB | 10 GB (model + cache + audio) |
| **VRAM (GPU)** | 4 GB | 6 GB+ |
| **FFmpeg** | Any recent version | Required for YouTube support |

---

## 15. Hidden / Undocumented Features

| Feature | How to Access | Description |
|---------|---------------|-------------|
| **Zero-copy audio info** | Internal (`get_audio_info()`) | Uses `soundfile.SoundFile` headers — reads duration/sample rate in microseconds without loading audio into RAM |
| **Singleton model cache** | Internal (`_ModelCache`) | Model loaded once, shared across all files and even batch mode — saves 30+ seconds per file |
| **Time-perf_counter timing** | Internal | Microsecond-accurate elapsed timing using `time.perf_counter()` instead of `datetime.now()` |
| **Speed ratio display** | Shown after each transcription | Displays `X.XX× real-time` with arrow indicating if faster/slower than playback |
| **Duration in HH:MM:SS.mmm** | Audio info panel | Human-readable duration with fractional milliseconds |
| **Graceful Ctrl+C handling** | Automatic (`_shutdown_handler`) | Catches keyboard interrupts, cleans up downloaded audio, kills yt-dlp process trees |
| **Batch status tracking** | `.batch_status.json` | UTC-timestamped completion tracking — restart a batch and skipped files are preserved |
| **Garbage repetition filter** | Internal (`_filter_garbage_repetition`) | Detects and collapses transcription artifacts like repeated phrases or stuck audio loops |
