"""Download YouTube video audio and transcribe it to text.

Usage:
  python youtube_transcribe.py <YouTube_URL>                         # Urdu (default)
  python youtube_transcribe.py <YouTube_URL> -l en                  # English
  python youtube_transcribe.py <YouTube_URL> -m accurate --output result.txt
  python youtube_transcribe.py <YouTube_URL> -f json               # JSON output format
  python youtube_transcribe.py <YouTube_URL> -f docx              # Word document output

Environment:
  YTDLP_NO_PROGRESS=1   Suppress yt-dlp progress bar
  PARALLEL_ENABLED=false  Disable parallel chunk processing
  MAX_WORKERS=N          Max parallel workers (default: auto)
  WORKERS_PER_CPU=N     Workers per CPU core (default: 1)
"""

import argparse
import os
import sys
import signal
import subprocess
from pathlib import Path


# ════════════════════════════════════════════════════════════════════
# Load .env configuration (reads project/.env if present)
# ════════════════════════════════════════════════════════════════════

def _env_str(key: str, default: str) -> str:
    return os.environ.get(key, default)

def _env_int(key: str, default: int) -> int:
    try:
        return int(os.environ.get(key, str(default)))
    except (ValueError, TypeError):
        return default

def _env_bool(key: str, default: bool) -> bool:
    val = os.environ.get(key)
    if val is None:
        return default
    return val.lower() in ("true", "1", "yes")

def _env_float(key: str, default: float) -> float:
    try:
        return float(os.environ.get(key, str(default)))
    except (ValueError, TypeError):
        return default

_env_file = Path(__file__).parents[1] / ".env"
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
                numeric_keys = {"CHUNK_DURATION_S", "CHUNK_OVERLAP_S",
                                "MIN_AUDIO_DURATION_S", "YOUTUBE_MIN_DURATION_S",
                                "MAX_WORKERS", "WORKERS_PER_CPU", "DEFAULT_WORKERS"}
                if key in numeric_keys:
                    try:
                        os.environ[key] = str(float(value))
                    except ValueError:
                        pass
                else:
                    os.environ[key] = value
    del _env_file


# ── Constants (sourced from .env) ─────────────────────────────────

YOUTUBE_AUDIO_EXTENSIONS = set(ext.strip() for ext in _env_str("YOUTUBE_AUDIO_EXTENSIONS", ".mp3,.wav,.flac,.ogg,.m4a,.aac").split(","))
OUTPUT_DIR_NAME = _env_str("YOUTUBE_OUTPUT_DIR", "youtube_downloads")
PROJECT_DIR = Path(__file__).parent
MIN_AUDIO_DURATION_S = _env_int("MIN_AUDIO_DURATION_S", 10)

# Chunking threshold — auto-split YouTube audio > threshold into chunks
CHUNK_THRESHOLD_S = _env_int("MAX_AUDIO_BEFORE_SPLIT_S", 60)
CHUNK_DURATION_S = _env_int("CHUNK_DURATION_S", 55)

# Parallel processing control (shared with transcribe.py)
_PARALLEL_ENABLED = _env_bool("PARALLEL_ENABLED", True)
_DEFAULT_MAX_WORKERS = _env_int("MAX_WORKERS", 0)
_WORKERS_PER_CPU = max(_env_int("WORKERS_PER_CPU", 1), 1)


def _find_ytdlp() -> str:
    """Find the yt-dlp executable in the venv or PATH."""
    venv_scripts = PROJECT_DIR / "venv" / "Scripts"
    if (venv_scripts / "yt-dlp.exe").exists():
        return str(venv_scripts / "yt-dlp.exe")

    venv_bin = PROJECT_DIR / "venv" / "bin"
    if (venv_bin / "yt-dlp").exists():
        return str(venv_bin / "yt-dlp")

    # Fall back to PATH lookup
    import shutil
    path_exe = shutil.which("yt-dlp")
    if path_exe:
        return path_exe

    print("[ERROR] yt-dlp not found. Install it with: pip install yt-dlp")
    sys.exit(1)

YTDLP_EXEC = _find_ytdlp()


def _kill_process_tree(pid: int):
    """Kill a process and its children (Windows-compatible)."""
    import platform
    if platform.system() == "Windows":
        try:
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)],
                         capture_output=True, timeout=5)
        except Exception:
            pass
    else:
        import psutil
        try:
            parent = psutil.Process(pid)
            for child in parent.children(recursive=True):
                child.kill()
            parent.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass


def download_audio(youtube_url: str, output_dir: str, fmt: str = "mp3") -> str | None:
    """Download audio from a YouTube video using yt-dlp.

    Returns the path to the downloaded audio file, or None on failure.
    """
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("[1/3] Downloading audio from YouTube ...")
    env = os.environ.copy()

    # Build cmd: flags first, then -o template with trailing / for dir mode, then -- URL
    if fmt == "mp3":
        output_template = str(out_dir / "%(title)s.%(ext)s") + "/"
        cmd = [
            YTDLP_EXEC,
            "--extract-audio",
            "--audio-format", "mp3",
            "-o", output_template,
        ]
    else:
        audio_fmt = fmt
        output_template = str(out_dir / "%(title)s.%(ext)s") + "/"
        cmd = [
            YTDLP_EXEC,
            "-x",
            "--audio-format", audio_fmt,
            "-o", output_template,
        ]

    # Add --no-progress if requested (always between -o and --)
    if os.environ.get("YTDLP_NO_PROGRESS"):
        cmd.append("--no-progress")

    cmd.extend(["--", youtube_url])
    
    # Use Popen so we can kill it on Ctrl+C
    ytdlp_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  text=True, env=env)
    try:
        stdout, stderr = ytdlp_proc.communicate(timeout=600)  # 10 min timeout for long videos
        returncode = ytdlp_proc.returncode
    except KeyboardInterrupt:
        print("\n[INTERRUPT] Killing yt-dlp download...")
        _kill_process_tree(ytdlp_proc.pid)
        raise
    except subprocess.TimeoutExpired:
        print("[ERROR] yt-dlp timed out after 10 minutes.")
        ytdlp_proc.kill()
        return None

    if returncode != 0:
        stderr_out = stderr.strip()
        # Try to extract a useful error message
        for line in stderr_out.split("\n"):
            if "ERROR" in line or "error" in line:
                print(f"[ERROR] {line.strip()}")
                break
        else:
            print(f"[ERROR] yt-dlp failed with return code {returncode}")
        return None

    # Find the downloaded file
    audio_file = None
    for ext in YOUTUBE_AUDIO_EXTENSIONS:
        for f in out_dir.iterdir():
            if f.suffix.lower() == ext and f.is_file():
                audio_file = str(f)
                break
        if audio_file:
            break

    if not audio_file:
        # Fallback: try any newly created file
        for f in sorted(out_dir.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
            if f.is_file():
                audio_file = str(f)
                break

    if not audio_file:
        print("[ERROR] No audio file was created.")
        return None

    # Validate downloaded audio duration (catch truncated/partial downloads)
    probe_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", audio_file]
    probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
    if probe_result.returncode == 0 and probe_result.stdout.strip():
        try:
            duration_s = float(probe_result.stdout.strip())
            if duration_s < MIN_AUDIO_DURATION_S:
                print(f"[ERROR] Downloaded audio is only {duration_s:.1f}s (expected longer video). File may be truncated.")
                return None
            print(f"[OK]  Audio saved: {Path(audio_file).name} ({duration_s:.0f}s)")
        except ValueError:
            pass  # ffprobe didn't return a number — skip validation
    else:
        print(f"[OK]  Audio saved: {Path(audio_file).name}")

    return audio_file


def transcribe_audio(
    audio_path: str,
    *,
    output_path: str | None = None,
    language: str = "ur",
    model_id: str = _env_str("HF_MODEL_ID", "kingabzpro/whisper-large-v3-turbo-urdu"),
    fmt: str = "txt",
    quiet: bool = False,
    chunk_duration_s: float = 0,
) -> dict | None:
    """Transcribe audio using chunked pipeline for long files.

    For audio > CHUNK_THRESHOLD_S seconds, automatically splits via ffmpeg,
    transcribes each chunk on GPU in parallel, then merges results.
    """
    sys.path.insert(0, str(Path(__file__).parent))
    from transcribe import transcribe_in_chunks, transcribe_single  # type: ignore

    # Probe duration to decide whether to chunk
    import subprocess as _sp
    probe_cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path,
    ]
    probe_result = _sp.run(probe_cmd, capture_output=True, text=True)
    duration_s = 0.0
    if probe_result.returncode == 0 and probe_result.stdout.strip():
        try:
            duration_s = float(probe_result.stdout.strip())
        except ValueError:
            pass

    # Decide: chunked or single?
    use_chunked = (
        chunk_duration_s > 0                    # user explicitly requested
        or duration_s > CHUNK_THRESHOLD_S      # auto-split for long audio
    )

    if use_chunked:
        return transcribe_in_chunks(
            audio_path=audio_path,
            output_path=output_path,
            model_id=model_id,
            language=language,
            fmt=fmt,
            auto_spell=True,
            max_audio_before_split_s=int(chunk_duration_s * 1.2) if chunk_duration_s > 0 else CHUNK_THRESHOLD_S,
        )
    else:
        return transcribe_single(
            audio_path=audio_path,
            output_path=output_path,
            model_id=model_id,
            language=language,
            fmt=fmt,
            auto_punctuate=True,
            auto_spell=True,
            quiet=quiet,
            max_segment_seconds=120,
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Download YouTube video audio and transcribe it to text.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  %(prog)s https://youtube.com/watch?v=XXXXX              Urdu transcription (auto-chunk for long videos)
  %(prog)s URL -l en                                      English transcription
  %(prog)s URL -f json                                    JSON output
  %(prog)s URL -f docx                                  Word document output
  %(prog)s URL -m accurate -o result.txt                  High-quality model + custom output
  %(prog)s URL --chunk 45                                 Custom chunk duration (45s chunks)
  %(prog)s URL --no-parallel                             Disable parallel chunk processing
        """,
    )
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument("-o", "--output", default=None, help="Output text file path")
    parser.add_argument("-f", "--format", choices=["txt", "json", "jsonl", "docx"], default="txt", help="Output format (default: txt)")
    parser.add_argument("-l", "--language", default="ur", help="Language code (default: ur)")
    parser.add_argument("-m", "--model", default=None, help="HuggingFace Whisper model ID")
    parser.add_argument("--chunk", type=float, default=0, metavar="SEC",
                        help="Split audio into chunks of SEC seconds (e.g. 55). Default: auto-split >60s.")
    parser.add_argument("--quiet", "-q", action="store_true", help="Minimal output")
    parser.add_argument("--no-parallel", action="store_true",
                        help="Disable parallel processing (sequential chunks)")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    # Validate URL
    if not args.url.startswith(("http://", "https://")):
        print("[ERROR] Please provide a valid YouTube URL.")
        sys.exit(1)

    # Respect --no-parallel by setting env
    if args.no_parallel:
        os.environ["PARALLEL_ENABLED"] = "false"

    # Create output directory in project root
    base_dir = Path(__file__).parent
    audio_dir = base_dir / OUTPUT_DIR_NAME

    # Track downloaded files for cleanup on interrupt
    downloaded_audio = None

    try:
        # Step 1: Download audio
        audio_file = download_audio(args.url, str(audio_dir))
        if not audio_file:
            sys.exit(1)
        downloaded_audio = audio_file

        # Step 2: Transcribe
        result = transcribe_audio(
            audio_path=audio_file,
            output_path=args.output,
            language=args.language,
            model_id=args.model or _env_str("HF_MODEL_ID", "kingabzpro/whisper-large-v3-turbo-urdu"),
            fmt=args.format,
            quiet=args.quiet,
            chunk_duration_s=args.chunk,
        )

        if result is None:
            print("\n[ERROR] Transcription failed.")
            sys.exit(1)

        print(f"\n{'='*60}")
        print("  Done!")
        print(f"  Audio   : {audio_file}")
        print(f"  Text    : {result.get('output_path', 'stdout')}")
        print(f"{'='*60}\n")

    except KeyboardInterrupt:
        print("\n[INTERRUPT] Cleaning up...")
        # Clean up downloaded audio file if transcription didn't complete
        if downloaded_audio and Path(downloaded_audio).exists():
            try:
                Path(downloaded_audio).unlink()
                print(f"  Removed: {downloaded_audio}")
            except Exception:
                pass
        sys.exit(130)


if __name__ == "__main__":
    main()
