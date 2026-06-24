# Changelog

All notable changes to the Urdu Speech-to-Text Transcription Tool will be documented in this file.

---

## [Unreleased]

### 🔄 Files Added / Updated in This Update

| File | Status | Description |
|------|--------|-------------|
| `CHANGELOG.md` | **Updated** | Restructured format with consistent sections, added Features/Usage reference links, clarified chunked pipeline details |
| `README.md` | **Updated** | Fixed Windows-only setup references (now cross-platform), corrected file structure references (`run_*.sh`), updated prerequisites table, simplified steps for all platforms |
| `QUICKSTART.md` | **Updated** | Aligns with actual file paths, removed .bat references, clarified venv activation per platform, added `.spell` flag docs |

---

## [2.2.0] — 2026-06-23  🎬 **Long-Form Transcription (Chunked Pipeline)**

### ⚠️ Breaking Changes

> None. All existing commands work identically. The chunked pipeline is triggered automatically for YouTube videos > 60s.

### 🆕 New Features

| # | Feature | Flag / Method | Description |
|---|---------|---------------|-------------|
| 1 | **ffmpeg-based audio splitting** | Automatic (YouTube videos > 60s) | Long YouTube videos are split into 55-second chunks via ffmpeg before transcription. Each chunk gets a fresh Whisper context window, eliminating the "first minute only" bug where later content was lost due to context window degradation. |
| 2 | **GPU parallel chunk processing** | Automatic | Chunks are transcribed concurrently using `ProcessPoolExecutor`. On GPU, each chunk runs in its own process for maximum parallelism. On CPU, up to `os.cpu_count()` workers. |
| 3 | **Overlap-aware text merging** | Automatic | Adjacent chunks overlap by ~3 seconds. During merge, the last 5 words of each chunk's overlap region are dropped to prevent duplication. |
| 4 | **`--chunk SEC` CLI option** | `python transcribe.py trans audio.mp3 --chunk 45` | Manually set chunk duration (e.g., 45s chunks). Use `0` to disable chunking entirely. Also available as `--chunk SEC` on `youtube_transcribe.py`. |
| 5 | **SRT timestamp-aware merging** | Automatic for `-f srt` output | When merging SRT subtitles from chunks, timestamps are shifted by the original audio offset and overlapping segments are deduplicated (keeping the one with more text content). |

### 🐛 Bug Fixes

- **Long-form YouTube transcription lost later content** — The root cause was Whisper's internal chunking carrying context across the entire audio file. Each chunk's output depended on previous chunks' hidden states, so content in later chunks degraded or was lost entirely. Splitting at the *audio* level before Whisper + giving each chunk a fresh model load eliminates this issue completely.
- **Internal chunking used mel-frame-level math** — The previous `max_segment_seconds` parameter operated over mel spectrogram frames (which the feature extractor clips internally), causing incorrect chunk counts for long audio. New code operates at the audio sample level via ffmpeg splitting, which is precise regardless of feature extractor behavior.

### 📁 New / Modified Files

| File | Status | Description |
|------|--------|-------------|
| `src/utils/audio_splitter.py` | **Added** | Audio splitting (ffmpeg), text/SRT merging utilities (~270 lines) |
| `src/utils/__init__.py` | **Added** | Package init with public API exports |
| `transcribe.py` | **Modified** | Added `transcribe_in_chunks()` + `_worker_transcribe_chunk()`, auto-detection for >60s audio, `--chunk` CLI option |
| `youtube_transcribe.py` | **Modified** | Updated `transcribe_audio()` to auto-chunk for YouTube videos > 60s, added `--chunk` option, updated help text |
| `run_youtube.sh` | **Modified** | Added chunk documentation to usage/help |

### ⚙️ How It Works (Long-Form Pipeline)

```
YouTube Video (e.g., 10 min = 600s)
         │
    ┌────▼───────────┐
    │ yt-dlp         │  Download audio as MP3
    └────┬───────────┘
    ┌────▼───────────┐
    │ ffprobe        │  Probe duration: 600s > 60s threshold?
    └────┬───────────┘
         │ YES → enter chunked pipeline
    ┌────▼───────────────┐
    │ ffmpeg split       │  55s chunks + 3s overlap = ~12 chunks
    └────┬───────────────┘
    ┌────┼────┼────┼──── ... ────┐
    ▼    ▼    ▼    ▼              ▼
  Chunk1 Ch2 Ch3 ... Ch12   (parallel on GPU via ProcessPoolExecutor)
    │    │    │                   │
    └────┴────────────────────────┘
         │
    ┌────▼───────────┐
    │ merge + dedup  │  Drop overlap tail words, join text
    └────┬───────────┘
         │
      Final Transcription (all 10 minutes captured)
```

---

## [2.1.0] — 2026-06-22  🎬 **YouTube Integration**

### 🆕 New Features

| # | Feature | Flag / Method | Description |
|---|---------|---------------|-------------|
| 1 | **YouTube video download + transcription** | `python youtube_transcribe.py <URL>` | Downloads audio from any YouTube video, extracts as MP3, then transcribes to text in one step |
| 2 | **Shell script wrapper** | `./run_youtube.sh <URL> [-l en] [-f srt]` | Cross-platform shell script that auto-finds the venv Python and yt-dlp |

### 🐛 Bug Fixes

- **Long-form transcription (transformers >= 5.x)** — The Whisper pipeline no longer accepts `chunk_length_s` / `stride_length_s` as constructor args in transformers 5.x. These deprecated kwargs were leaking into `model_kwargs`, causing cascading errors (`local_files_only` rejected, etc.). Removed the deprecated pipeline args entirely.
- **Audio channel mismatch** — Whisper's model expects mono input with mel-spectrogram features, not raw stereo waveform. Added `mono=True` to librosa load and switched from passing raw samples to using the model's built-in `WhisperFeatureExtractor` per-chunk.
- **Timestamp marker stripping regex** — The pattern was missing a closing pipe, causing timestamp markers like `<|2.14|>` to appear in output text. Fixed the regex to properly match and strip all timestamp tokens.
- **Segment count underflow** — Chunks were computed over mel frames (which the feature extractor clipped internally), so long videos only produced 2 chunks instead of the correct ~22 for a 9-minute video. Switched to audio-sample-level chunking with proper stride conversion (`overlap_seconds * fps` in frame units).
- **Feature extractor on host** — The model was on CUDA but the feature extractor expected numpy CPU arrays. Added `.cpu().numpy()` before passing to `feature_extractor()`, then moved the resulting features back to the target device.

### 📁 New / Modified Files

| File | Status | Description |
|------|--------|-------------|
| `youtube_transcribe.py` | **Added** | Core YouTube download + transcribe pipeline (~200 lines) |
| `run_youtube.sh` | **Added** | Shell script wrapper (cross-platform venv + yt-dlp detection) |
| `requirements.txt` | Modified | Added `yt-dlp>=2024.0.0` |
| `transcribe.py` | Modified | Fixed long-form transcription, timestamp stripping, mel-spectrogram per-chunk extraction |

### ⚙️ Requirements Changes

- **Added**: `yt-dlp>=2024.0.0` — YouTube video/audio download
- **Implicitly required**: FFmpeg (system dependency, needed by yt-dlp for audio format conversion)

---

## [2.0.0] — 2026-06-22  ⭐ **Major v2 Release**

### ⚡ Architecture Overhaul

- **Singleton model cache (`_ModelCache`)** — the 1.6 GB Whisper model is loaded *once* and shared across all files, even in batch mode. Previously each file triggered a full model reload.
- **Zero-copy audio info extraction** — uses `soundfile.SoundFile` headers to read duration/sample rate/channels without loading any audio data into RAM. v1 used `librosa.load()` which loaded entire files into memory (crashes on multi-hour files).
- **Time-perf_counter everywhere** — all elapsed timing replaced from `datetime.now()` to `time.perf_counter()` for microsecond-accurate measurements and wall-clock vs processing time comparison.

### 🆕 Brand New Features

| # | Feature | Flag / Method | Description |
|---|---------|---------------|-------------|
| 1 | **Speed/quality presets** | `--quality fast\|turbo\|accurate` | Auto-selects model: fast = distil-medium, turbo = default Urdu model, accurate = openai whisper-large-v3-turbo |
| 2 | **Config file system** | `transcribe_config.json` (auto-created) + `config show/set` subcommand | Persistent defaults for model, language, device, format, quality — CLI flags override config |
| 3 | **Parallel batch processing** | `--workers N` or `-w N` | Uses `concurrent.futures.ProcessPoolExecutor` to transcribe multiple files concurrently (CPU mode only; GPU remains single-process) |
| 4 | **Resume interrupted batches** | Automatic — `.batch_status.json` tracks completed files per-directory | Restart a batch and already-completed files are automatically skipped |
| 5 | **Dry-run preview** | `--dry-run audio.mp3` / `--dry-run-batch ./folder/` | Shows what *would* happen (audio info, output path, cache status, estimated time) without processing any files |
| 6 | **Quiet mode** | `--quiet` or `-q` | Machine-readable minimal output — outputs only JSON result to stdout for piping to scripts/APIs |
| 7 | **JSON Lines batch output** | `--format jsonl` with `--batch` | One JSON object per line in a single output file, each containing transcription + metadata for that file |
| 8 | **Auto-punctuation** | Config `auto_punctuate: true` (enabled by default) | Heuristic post-processing that adds periods after common Urdu sentence-ending patterns (ہے، گا، گی،یں، نا، ا) |
| 9 | **Recursive batch scanning** | `--batch ./folder/` now uses `rglob("*")` | Processes audio files in all subdirectories, not just the top level |
| 10 | **Extended format support** | `.aac`, `.wma` added to supported formats | Previously only mp3/wav/flac/ogg/m4a/mp4/webm |
| 11 | **Speed ratio display** | Shown automatically after each transcription | Displays `X.XX× real-time (↑)` or `(↓)` — tells you if processing is faster or slower than playback |
| 12 | **Duration in HH:MM:SS.mmm format** | Audio info panel | Human-readable duration instead of raw seconds, including fractional milliseconds |

### 🔧 Enhanced Existing Features

- **Model loading steps** — changed from `[1/3]`, `[2/3]`, `[3/3]` to `[1/4]`, `[2/4]`, `[3/4]` with explicit phase labels for clarity
- **SRT subtitle generation** — word-level timestamp distribution instead of fake single-segment timestamps (still a heuristic since raw Whisper chunk access requires pipeline refactoring; noticeably better than before)
- **Batch summary** — now shows wall time, average per-file time, and worker count alongside success/skip/fail counts
- **Cache system** — simplified to module-level `_cache_path()` accessor instead of passing Path objects around
- **Batch status** — uses UTC timestamps (`datetime.now(timezone.utc)`) for cross-platform consistency

### 🐛 Bug Fixes

- **Large file crashes** — v1's `librosa.load(path)` loads entire audio into RAM, crashing on files > ~2 GB. v2's `sf.info()` reads only the file header (microseconds of work regardless of file size).
- **Model reload in batch mode** — v1 loaded the full model pipeline fresh for every file. v2's `_ModelCache.get()` returns the singleton instance, saving 30+ seconds per file in a batch.
- **JSONL format on single files** — v1 silently accepted `--format jsonl` on a single file and produced broken output. v2 now rejects it with a clear error message.
- **Default format handling** — v1 always defaulted `"txt"` in argparse which prevented config override. v2 defaults to `None` and resolves from config first, then CLI, then `"txt"` as final fallback.
- **Batch directory reset** — new batch directories no longer inherit stale status from previous batches. The directory path is checked before applying cached status.

### 📝 Config System Details

Create/edit `transcribe_config.json` in the project root:

```json
{
  "model": "kingabzpro/whisper-large-v3-turbo-urdu",
  "language": "ur",
  "device": null,
  "format": "txt",
  "quality": "turbo",
  "workers": 1,
  "auto_punctuate": true,
  "max_segment_minutes": 30
}
```

CLI override syntax:
```bash
python src/transcribe.py config show          # view current config
python src/transcribe.py config set model=my-model language=en format=srt
# CLI flags still take precedence over config
python src/transcribe.py audio.mp3 --language en   # overrides config's "ur"
```

### ⚙️ Requirements Changes

- **Added**: `tqdm>=4.65.0` (progress bars; graceful fallback if absent)
- **Already present** (no change): `transformers`, `accelerate`, `librosa`, `soundfile`
- **Implicitly required** by Python stdlib: `concurrent.futures` (Python 3.2+, no pip install needed)

### 📁 New / Modified Files

| File | Status | Description |
|------|--------|-------------|
| `transcribe.py` | **Rewritten** | Entire v2 implementation (~850 lines vs ~500 in v1) |
| `.gitignore` | Updated | Added `transcribe_config.json`, `.batch_status.json` |

---

## [1.1.0] — 2026-06-22

### Added

- **Multiple output formats** (`--format txt/json/srt/vtt`)
  - `txt` — plain text (default, backward compatible)
  - `json` — transcription + metadata in JSON format
  - `srt` — SRT subtitle format for video editing
  - `vtt` — WebVTT subtitle format

- **Batch processing** (`--batch <directory>` or `run_batch.bat`)
  - Process all audio files in a folder at once
  - Automatic skip of already-transcribed (cached) files
  - Summary report with success/skip/fail counts and total time

- **Audio metadata display** (`--info` flag + auto-display on every transcription)
  - File size, duration, sample rate, channels — shown before transcribing

- **Language override** (`--language <code>`)
  - Transcribe in any language: `en`, `hi`, `ar`, etc. (default remains Urdu)

- **Custom model support** (`--model <id>`)
  - Use any HuggingFace Whisper model, not just the default

- **Device override** (`--device cpu/gpu`)
  - Force CPU or GPU mode when auto-detection is insufficient

- **Transcription cache** (`.transcribe_cache.json`)
  - Hash-based caching — skips re-transcribing unchanged files in batch mode
  - Use `--no-cache` to force re-transcription

- **Progress bar** during model loading (via tqdm)

- **New script**: `run_batch.bat` for easy folder-wide batch transcription

- **Updated documentation**: Full feature reference added to README.md

### Changed

- `transcribe.py` — completely refactored with enhanced CLI, new functions (`get_audio_info`, `process_batch`, `compute_file_hash`), improved error handling
- `setup_env.bat` — now also installs `tqdm` for progress bars
- `requirements.txt` — added `tqdm>=4.65.0`
- Error return codes: transcription failures now exit with code 1 (was `sys.exit(1)` in one place, now unified)

### Fixed

- **GPU detection at runtime** — was only detected during setup; now auto-detected every run
- **Empty transcription output** — now catches and reports empty results instead of saving blank files
- **Transcription error handling** — wrapped `pipeline()` call in try/except for graceful failure messages
- **Output path creation** — parent directories are now auto-created for custom output paths

### Removed

- Hardcoded model ID — now a configurable constant (`DEFAULT_MODEL`) that can be overridden via CLI

---

## [1.0.0] — Original Release

### Added

- Single-file Urdu audio transcription using `kingabzpro/whisper-large-v3-turbo`
- Automatic CUDA/CPU detection during setup
- Drag-and-drop support via `run_transcribe.bat`
- TXT output next to input file (same name, `.txt` extension)
- Comprehensive README with step-by-step setup instructions
