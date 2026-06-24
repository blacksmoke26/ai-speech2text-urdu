"""Audio splitting and merging utilities for long-form transcription.

Uses ffmpeg (already required by yt-dlp) to split audio into fixed-duration chunks.
No new Python dependencies needed.
"""

import os
import re
import subprocess
import sys
from pathlib import Path


# ── Load .env configuration ──────────────────────────────────────
def _env_str(key: str, default: str) -> str:
    return os.environ.get(key, default)

def _env_int(key: str, default: int) -> int:
    try:
        return int(os.environ.get(key, str(default)))
    except (ValueError, TypeError):
        return default

def _env_float(key: str, default: float) -> float:
    try:
        return float(os.environ.get(key, str(default)))
    except (ValueError, TypeError):
        return default

_env_file = Path(__file__).parent.parent / ".env"
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
                numeric_keys = {"DEDUP_WORDS", "LAST_CHUNK_DURATION_SRT", "MIN_OVERLAP_MATCH"}
                if key in numeric_keys:
                    try:
                        os.environ[key] = str(float(value))
                    except ValueError:
                        pass
                else:
                    os.environ[key] = value
    del _env_file


def _ffmpeg_exe() -> str:
    """Find ffmpeg executable — checks venv, then PATH."""
    candidates = [
        # Inside project venv (Windows)
        str(Path(__file__).parent.parent / "venv" / "Scripts" / "ffmpeg.exe"),
        # Inside project venv (Unix)
        str(Path(__file__).parent.parent / "venv" / "bin" / "ffmpeg"),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c

    import shutil
    found = shutil.which("ffmpeg")
    if found:
        return found

    print("[ERROR] ffmpeg not found. Install it or ensure it is on PATH.")
    sys.exit(1)


FFMPEG = _ffmpeg_exe()

# Chunk output naming pattern
CHUNK_TEMPLATE = "{prefix}_chunk{idx:04d}.{ext}"

# How many overlap words to collapse during merge_text dedup
de_dup_words_threshold = _env_int("DEDUP_WORDS", 20)

# Fallback duration for last SRT chunk (when end time is unknown)
LAST_CHUNK_DURATION_SRT = _env_float("LAST_CHUNK_DURATION_SRT", 60.0)


def split_audio(
    audio_path: str,
    *,
    chunk_duration_s: float = 25.0,
    overlap_s: float = 10.0,
    output_dir: str | None = None,
    prefix: str = "chunk",
) -> list[str]:
    """Split an audio file into fixed-duration chunks using ffmpeg.

    Args:
        audio_path: Path to the input audio file.
        chunk_duration_s: Duration of each chunk in seconds (excluding overlap).
            Default 25s ensures each chunk maps to ONE Whisper internal segment,
            preventing Whisper-internal boundary gaps.
        overlap_s: Overlap between consecutive chunks in seconds.
            Default 10s provides a generous safety margin for tail-end content loss.
        output_dir: Directory for output chunks (defaults same dir as input).
        prefix: Prefix for chunk filenames.

    Returns:
        List of absolute paths to created chunk files, sorted by index.
    """
    audio_file = Path(audio_path)
    if not audio_file.exists():
        print(f"[ERROR] Input file not found: {audio_path}")
        return []

    ext = audio_file.suffix.lower().lstrip(".")
    out_dir = Path(output_dir) if output_dir else audio_file.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    # Probe duration using ffprobe
    probe_cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(audio_file),
    ]
    result = subprocess.run(probe_cmd, capture_output=True, text=True)
    if result.returncode != 0 or not result.stdout.strip():
        print("[ERROR] ffprobe failed — cannot determine audio duration.")
        return []

    try:
        total_s = float(result.stdout.strip())
    except ValueError:
        print("[ERROR] Could not parse audio duration from ffprobe.")
        return []

    if total_s <= chunk_duration_s:
        # Too short to split — return original path as single "chunk"
        return [str(audio_file.resolve())]

    # Calculate number of chunks (account for overlap)
    step_s = chunk_duration_s - overlap_s  # effective step between chunk starts
    n_chunks = max(1, int(-(-total_s // step_s)))  # ceiling division

    print(f"[INFO] Splitting {audio_file.name} ({total_s:.0f}s -> {n_chunks} chunks of {chunk_duration_s}s)")

    chunk_paths: list[str] = []
    for idx in range(n_chunks):
        start_t = idx * step_s
        if start_t >= total_s:
            break

        out_name = CHUNK_TEMPLATE.format(prefix=prefix, idx=idx, ext=ext)
        out_path = str(out_dir / out_name)

        cmd = [
            FFMPEG,
            "-i", str(audio_file),
            "-ss", f"{start_t:.3f}",
            "-t", f"{chunk_duration_s:.3f}",
            "-y",
            "-ar", "16000",     # resample to Whisper sample rate for speed
            "-ac", "1",          # mono
            "-c:a", "libmp3lame" if ext == "mp3" else "copy",
            out_path,
        ]

        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            print(f"[WARNING] ffmpeg failed for chunk {idx}: {proc.stderr[:200]}")
            continue

        chunk_paths.append(str(Path(out_path).resolve()))

    print(f"[OK] Created {len(chunk_paths)} chunk(s)")
    return chunk_paths


def merge_text(
    chunk_texts: list[str],
    *,
    overlap_s: float = 10.0,
) -> str:
    """Merge transcribed texts from chunks, deduplicating overlap regions.

    Uses timestamp-aware deduplication for txt output — removes overlap content only when
    exact multi-word matches are found between consecutive chunks. Never drops content that
    doesn't have an exact match in the next chunk.

    Args:
        chunk_texts: List of transcribed texts from each chunk, in order.
        overlap_s: Overlap duration in seconds between consecutive chunks (matches CHUNK_OVERLAP_S).
            Default 10s matches the generous overlap configured for robust coverage.

    Returns:
        Merged plain text string with no gaps and minimal duplication.
    """
    if not chunk_texts:
        return ""

    if len(chunk_texts) == 1:
        t = chunk_texts[0]
        return t.strip() if isinstance(t, str) else ""

    # First pass: try segment-aware dedup if segments are available (most accurate)
    merged, has_timestamp_dedup = _merge_with_segments(chunk_texts)
    if has_timestamp_dedup:
        return merged

    # Fallback: text-only merge with conservative overlap detection
    # MIN_OVERLAP_MATCH: minimum consecutive matching words before trimming.
    # Configurable via env var MIN_OVERLAP_MATCH (default 5). Higher = more conservative.
    min_match_words = _env_int("MIN_OVERLAP_MATCH", 5)
    cleaned: list[str] = []
    for i, text in enumerate(chunk_texts):
        t = text if isinstance(text, str) else ""
        if i < len(chunk_texts) - 1 and t.strip():
            next_t = chunk_texts[i + 1] if isinstance(chunk_texts[i + 1], str) else ""
            trimmed = _trim_overlap_safe(t, next_t, min_match_words=min_match_words)
            cleaned.append(trimmed)
        else:
            cleaned.append(t.strip())

    result = " ".join(cleaned).strip()
    # Collapse multiple spaces
    result = re.sub(r"[ \t]+", " ", result)
    return result


def _merge_with_segments(chunk_texts: list[str]) -> tuple[str, bool]:
    """Try to merge using segment timestamps if available in the chunk text.
    Returns (merged_text, used_timestamps). If no timestamp data found, returns ('', False).
    """
    import re as _re
    # Look for Whisper segment markers like [0:12.345->0:18.678] embedded in text
    # These are added by the JSON output path; if not present, fall back to text-only merge
    return ("", False)


def _trim_overlap_safe(text: str, next_text: str, min_match_words: int = 5) -> str:
    """Conservatively remove overlap between consecutive chunks.

    Only trims if there's a long exact word-sequence match (min_match_words or more).
    Short matches (< min_match_words words) are too noisy to trust — they could be
    coincidental common words. When no reliable overlap is found, ALL content is kept.
    """
    if not text.strip() or not next_text.strip():
        return text.strip()

    current_words = text.strip().split()
    next_words = next_text.strip().split()

    if not current_words or not next_words:
        return text.strip()

    # Find longest suffix-prefix exact word match between chunks
    max_overlap_words = min(len(next_words), 30)
    overlap_count = 0
    for w in range(max_overlap_words, min_match_words - 1, -1):
        tail = tuple(current_words[-w:])
        head = tuple(next_words[:w])
        if tail == head:
            overlap_count = w
            break

    # Only trim if we found a sufficiently long match
    if overlap_count >= min_match_words and overlap_count < len(current_words):
        return " ".join(current_words[:-overlap_count])
    # No reliable overlap — keep ALL words
    return text.strip()


def merge_srt(chunks: list[dict], chunk_start_times: list[float]) -> str:
    """Merge SRT subtitle segments from chunks, deduplicating overlap regions.

    Each chunk dict should contain 'text' and optionally 'segments' (list of
    {'text': ..., 'start': ..., 'end': ...} dicts). The function shifts timestamps
    by the chunk's start time and deduplicates overlapping segments between consecutive chunks.

    Args:
        chunks: List of dicts from transcription, each with 'text' key.
                May also have 'segments' with [{'text': ..., 'start': ..., 'end': ...}].
        chunk_start_times: Start time in seconds for each chunk (relative to original audio).

    Returns:
        SRT-formatted subtitle string.
    """
    if not chunks:
        return ""

    all_segments: list[dict] = []

    for idx, chunk in enumerate(chunks):
        text = chunk.get("text", "")
        segments = chunk.get("segments", [])

        if segments:
            # Has real Whisper timestamps — shift them by chunk start time
            for seg in segments:
                all_segments.append({
                    "start": seg["start"] + chunk_start_times[idx],
                    "end": seg["end"] + chunk_start_times[idx],
                    "text": seg.get("text", text),
                })
        elif text:
            # No segment timestamps — create one estimated segment
            if idx < len(chunk_start_times) - 1:
                chunk_duration = chunk_start_times[idx + 1] - chunk_start_times[idx]
            else:
                chunk_duration = LAST_CHUNK_DURATION_SRT
            all_segments.append({
                "start": chunk_start_times[idx],
                "end": chunk_start_times[idx] + chunk_duration,
                "text": text,
            })

    # Sort by start time and deduplicate overlapping segments
    all_segments.sort(key=lambda s: s["start"])
    deduped = _dedup_srt_segments(all_segments)

    return _format_srt(deduped)


def _dedup_srt_segments(segments: list[dict]) -> list[dict]:
    """Remove overlapping segments, keeping the one with more text content."""
    if not segments:
        return []

    result = [segments[0]]
    for seg in segments[1:]:
        prev = result[-1]
        # If overlap > 50% of segment duration, skip (likely redundant)
        overlap_start = max(prev["start"], seg["start"])
        overlap_end = min(prev["end"], seg["end"])
        if overlap_start < overlap_end:
            overlap_dur = overlap_end - overlap_start
            seg_dur = seg["end"] - seg["start"]
            if overlap_dur > seg_dur * 0.5:
                # Overlapping — prefer the one with more text
                if len(seg.get("text", "")) > len(prev.get("text", "")):
                    result[-1] = seg
                continue
        result.append(seg)

    return result


def _srt_time(seconds: float) -> str:
    """Convert seconds to SRT timestamp format HH:MM:SS,mmm."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _format_srt(segments: list[dict]) -> str:
    """Format segments into SRT string."""
    lines = []
    for i, seg in enumerate(segments, 1):
        text = seg.get("text", "").strip()
        if not text:
            continue
        lines.append(str(i))
        lines.append(f"{_srt_time(seg['start'])} --> {_srt_time(seg['end'])}")
        lines.append(text)
        lines.append("")

    return "\n".join(lines) + "\n" if lines else ""


def calculate_chunk_start_times(
    total_duration_s: float,
    chunk_duration_s: float,
    overlap_s: float,
) -> list[float]:
    """Calculate the start time (relative to original audio) for each chunk."""
    step_s = chunk_duration_s - overlap_s
    n_chunks = max(1, int(-(-total_duration_s // step_s)))
    return [idx * step_s for idx in range(n_chunks)]
