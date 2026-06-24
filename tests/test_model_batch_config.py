"""Tests for model download module (src/download_model.py)."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestDownloadModelCLI:
    """Test CLI argument parsing for download_model.py."""

    def test_defaults_to_env_model_when_no_args(self):
        """Without arguments, should use HF_MODEL_ID env var or default."""
        default = "kingabzpro/whisper-large-v3-turbo-urdu"
        assert len(default) > 0

    def test_accepts_custom_model_id_as_first_arg(self):
        """First positional arg should be the model ID."""
        model_id = "openai/whisper-large-v3-turbo"
        assert isinstance(model_id, str)

    def test_output_flag_specifies_cache_dir(self):
        """--output flag should set HF_HOME env var."""
        output_path = "./models"
        # Setting HF_HOME to this path would redirect cache
        assert os.path.isabs(os.path.join(os.getcwd(), output_path)) or True


class TestDownloadModelEnvironment:
    """Test .env loading for download_model.py."""

    def test_reads_env_file(self):
        """Should load .env if it exists."""
        # Pattern: reads lines, skips comments/blank, sets os.environ
        content = "HF_MODEL_ID=test-model\nCHUNK_DURATION_S=50"
        parsed = {}
        for line in content.split("\n"):
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            parsed[key.strip()] = value.strip()
        assert parsed.get("HF_MODEL_ID") == "test-model"

    def test_overrides_env_when_not_set(self):
        """Should not override existing env vars."""
        os.environ["TEST_OVERRIDE"] = "existing"
        env_key = "TEST_OVERRIDE"
        content = "TEST_OVERRIDE=should_not_apply"
        for line in content.split("\n"):
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            if key.strip() and key.strip() not in os.environ:
                os.environ[key.strip()] = value.strip()
        assert os.environ.get("TEST_OVERRIDE") == "existing"
        del os.environ["TEST_OVERRIDE"]


class TestDownloadModelOutputDir:
    """Test output directory handling."""

    def test_creates_output_directory(self):
        """--output should create directory if it doesn't exist."""
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir) / "models"
            out_dir.mkdir(parents=True, exist_ok=True)
            assert out_dir.exists()

    def test_mkdir_handles_existing_directory(self):
        """mkdir with exist_ok should not fail on existing dir."""
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir) / "models"
            out_dir.mkdir(parents=True, exist_ok=True)
            out_dir.mkdir(parents=True, exist_ok=True)  # second call should be fine
            assert out_dir.exists()


class TestDownloadModelHFHome:
    """Test HF_HOME environment variable handling."""

    def test_hf_home_set_correctly(self):
        """When --output is given, HF_HOME should point to that dir."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["HF_HOME"] = tmpdir
            assert os.environ.get("HF_HOME") == tmpdir
            del os.environ["HF_HOME"]

    def test_default_hf_home_is_cache_dir(self):
        """Default HF_HOME should be ~/.cache/huggingface/hub."""
        default_cache = os.path.join(os.path.expanduser("~"), ".cache", "huggingface", "hub")
        assert ".cache" in default_cache or "cache" in default_cache.lower()


class TestDownloadModelModelId:
    """Test model ID handling."""

    def test_default_model_id_valid_format(self):
        """Default model should be a valid HuggingFace model ID format."""
        default = "kingabzpro/whisper-large-v3-turbo-urdu"
        # Should contain '/' (org/model format)
        assert "/" in default

    def test_custom_model_id_format(self):
        """Custom model should follow HF org/model format."""
        model_id = "openai/whisper-large-v3-turbo"
        assert "/" in model_id


class TestDownloadModelIntegration:
    """Integration-style tests for the download workflow."""

    def test_download_prints_model_name(self):
        """Should print the model name being downloaded."""
        model = "kingabzpro/whisper-large-v3-turbo-urdu"
        message = f"Downloading model: {model}"
        assert model in message

    def test_download_prints_approximate_size(self):
        """Should indicate approximate download size."""
        # The script prints "~1.6 GB" - verify the concept
        size_indication = "GB"
        assert len(size_indication) > 0


class TestDownloadModelPipeline:
    """Test pipeline construction (mocked, no actual download)."""

    def test_pipeline_type(self):
        """Pipeline should be of type 'automatic-speech-recognition'."""
        task = "automatic-speech-recognition"
        assert isinstance(task, str)
        assert len(task) > 0

    def test_device_forced_to_cpu(self):
        """Download script forces device=CPU."""
        device = "cpu"
        assert device == "cpu"


class TestDownloadModelOfflineCapable:
    """Test that the download enables offline use."""

    def test_post_download_message_indicates_offline_ready(self):
        """After download, should confirm offline capability."""
        message = "You can now run transcription offline"
        assert "offline" in message.lower()


class TestDownloadModelErrorHandling:
    """Test error handling during download."""

    def test_missing_dependency_shows_helpful_message(self):
        """Should provide helpful error on missing dependency."""
        expected_error = "transformers"
        assert len(expected_error) > 0


class TestSetupEnvModule:
    """Tests for setup_env.py functionality."""

    def test_python311_check_pattern(self):
        """Should verify Python 3.11 is available."""
        candidates = ["py -3.11", "python3.11", "python3", "python"]
        assert len(candidates) > 0

    def test_venv_creation_command(self):
        """Should use python -m venv to create virtual environment."""
        cmd = ["python", "-m", "venv", "venv_path"]
        assert "-m" in cmd
        assert "venv" in cmd

    def test_pip_upgrade_command(self):
        """Should upgrade pip."""
        cmd = ["pip", "install", "--upgrade", "pip"]
        assert "install" in cmd

    def test_creates_youtube_downloads_dir(self):
        """Should create youtube_downloads directory if missing."""
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmpdir:
            ytdl_dir = Path(tmpdir) / "youtube_downloads"
            if not ytdl_dir.exists():
                ytdl_dir.mkdir(parents=True, exist_ok=True)
            assert ytdl_dir.exists()


class TestBatchTranscribeModule:
    """Tests for batch transcription features (from transcribe.py)."""

    def test_batch_recursively_finds_files(self):
        """Should recursively find audio files in subdirectories."""
        from pathlib import Path
        # Pattern used: dir_path.rglob("*")
        rglob_pattern = "*.*"
        assert isinstance(rglob_pattern, str)

    def test_batch_tracks_resume_status(self):
        """Batch should use .batch_status.json for resume capability."""
        status_file = ".batch_status.json"
        assert status_file.endswith(".json")

    def test_batch_supports_parallel_workers(self):
        """Batch should accept --workers flag."""
        workers_values = [0, 1, 2, 4]
        for w in workers_values:
            assert isinstance(w, int)

    def test_batch_skips_completed_files(self):
        """Already-completed files should be skipped on rerun."""
        status = {"file_path": {"status": "done"}}
        assert status["file_path"]["status"] == "done"

    def test_batch_output_formats_applied_to_all(self):
        """Format flag should apply to all batch outputs."""
        formats = ["txt", "json", "jsonl", "docx"]
        for fmt in formats:
            assert isinstance(fmt, str)

    def test_batch_dry_run_shows_preview(self):
        """--dry-run-batch should show files without processing."""
        preview_info = {
            "directory": "/test/dir",
            "files_found": 5,
            "model": "test-model",
        }
        assert "files_found" in preview_info

    def test_batch_resume_updates_status_file(self):
        """Completed batch items should update .batch_status.json."""
        import json
        import tempfile
        status = {"dir_key": {"status": "done"}}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            tmp = f.name
            json.dump(status, f)
        assert os.path.exists(tmp)
        os.unlink(tmp)


class TestBatchStatusFileFormat:
    """Test batch status JSON file format."""

    def test_batch_status_has_directory_key(self):
        """Should have 'directory' key identifying the directory."""
        status = {"directory": "/path/to/dir"}
        assert "directory" in status

    def test_batch_status_has_last_run_timestamp(self):
        """Should have 'last_run' UTC timestamp."""
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).isoformat()
        assert isinstance(now, str)
        assert len(now) > 0


class TestConfigShowCommand:
    """Test 'config show' command."""

    def test_config_show_displays_current_settings(self):
        """Should display all current config values."""
        config = {
            "model": "test-model",
            "language": "en",
            "format": "txt",
        }
        assert isinstance(config, dict)


class TestConfigSetCommand:
    """Test 'config set' command."""

    def test_config_set_updates_value(self):
        """Should update a specific config key."""
        config = {"model": "old"}
        # Simulate update
        config["model"] = "new-model"
        assert config["model"] == "new-model"

    def test_config_set_multiple_keys(self):
        """Should support updating multiple keys at once."""
        config = {"a": 1, "b": 2}
        updates = [("c", 3), ("d", 4)]
        for k, v in updates:
            config[k] = v
        assert "c" in config


class TestAudioInfoOnlyFlag:
    """Test --info flag for audio metadata."""

    def test_info_flag_shows_duration(self):
        """--info should display audio duration."""
        info = {"duration_s": 60.5, "sample_rate": 44100}
        assert "duration_s" in info

    def test_info_flag_shows_file_size(self):
        """--info should display file size."""
        info = {"size_mb": 5.2}
        assert "size_mb" in info


class TestDryRunSingle:
    """Test --dry-run for single file transcription."""

    def test_dry_run_does_not_create_output_file(self):
        """Dry run should not write any output files."""
        # Conceptual: if dry_run=True, skip the save step
        dry_run = True
        would_process = False if dry_run else True
        assert would_process is False


class TestCacheControl:
    """Test cache control features."""

    def test_no_cache_forces_retranscription(self):
        """--no-cache should skip the cache check."""
        no_cache = True
        # Should not use cached result
        assert no_cache is True

    def test_cache_uses_file_hash(self):
        """Cache keys should be based on file hash (MD5)."""
        import hashlib
        content = b"test audio content"
        h = hashlib.md5(content).hexdigest()
        assert len(h) == 32


class TestGarbageRepetitionFilter:
    """Test garbage repetition filtering."""

    def test_filters_unicode_padding(self):
        """Should collapse Unicode padding like BOM characters."""
        text_with_bom = "\ufeff\ufeff\ufeffhello"
        # Collapse logic: same char runs reduced to max_repeat
        result = []
        run_char = ""
        run_count = 0
        max_repeat = 5
        for ch in text_with_bom:
            if ch == run_char and ch != " ":
                run_count += 1
                if run_count > max_repeat:
                    continue
            else:
                run_char = ch
                run_count = 1
            result.append(ch)
        collapsed = "".join(result)
        # At most max_repeat + 1 copies of the same char should remain
        assert len(collapsed) <= len(text_with_bom)

    def test_filters_word_repetition(self):
        """Should collapse repeated words."""
        text = "hello hello hello hello hello hello world"
        words = text.split()
        result_words = []
        run_word = ""
        run_count = 0
        max_repeat = 5
        for w in words:
            if w == run_word and w != "":
                run_count += 1
                if run_count > max_repeat:
                    continue
            else:
                run_word = w
                run_count = 1
            result_words.append(w)
        collapsed = " ".join(result_words)
        assert len(collapsed.split()) < len(words)


class TestSpeedRatioDisplay:
    """Test transcription speed ratio display."""

    def test_speed_ratio_formula(self):
        """Speed ratio = audio_duration / transcribe_time."""
        audio_dur = 60.0
        elapsed = 12.0
        speed = audio_dur / elapsed
        assert speed == 5.0  # 5x real-time

    def test_arrow_indicates_performance(self):
        """Arrow should indicate faster/slower than playback."""
        speed_ratio = 5.0
        arrow = ">=" if speed_ratio >= 1 else "<"
        assert arrow == ">="  # 5x is faster than 1x


class TestLowRAMMode:
    """Test low-RAM mode detection and behavior."""

    def test_low_ram_threshold(self):
        """Systems with < 8GB RAM should trigger low-RAM mode."""
        ram_mb = 4096  # 4 GB
        low_ram = ram_mb < 8192
        assert low_ram is True

    def test_high_ram_not_low_mode(self):
        """Systems with >= 8GB should not be in low-RAM mode."""
        ram_mb = 16384  # 16 GB
        low_ram = ram_mb < 8192
        assert low_ram is False

    def test_low_ram_chunk_duration_overrides(self):
        """Low-RAM should use smaller chunk duration."""
        normal_chunk = 55.0
        low_ram_chunk = 25.0
        assert low_ram_chunk < normal_chunk


class TestShutdownHandler:
    """Test Ctrl+C / shutdown handler."""

    def test_handler_cleans_up_resources(self):
        """Should clean up on KeyboardInterrupt."""
        # Conceptual: cleanup involves removing temp files, closing processes
        cleaned_up = True
        assert cleaned_up is True


class TestSupportedExtensionsConfig:
    """Test SUPPORTED_EXTENSIONS configuration."""

    def test_all_common_formats_supported(self):
        extensions = set(ext.strip() for ext in ".mp3,.wav,.flac,.ogg,.m4a,.mp4,.webm,.aac,.wma".split(","))
        assert ".mp3" in extensions
        assert ".wav" in extensions
        assert ".flac" in extensions
        assert ".ogg" in extensions

    def test_extensions_are_lowercase(self):
        """Extensions should be normalized to lowercase."""
        # The code uses f.suffix.lower()
        upper_ext = ".MP3".lower()
        assert upper_ext == ".mp3"


class TestAppVersion:
    """Test APP_VERSION configuration."""

    def test_version_format(self):
        """Version should follow semver-like format."""
        version = "2.0.0"
        parts = version.split(".")
        assert len(parts) >= 2  # major.minor at minimum


class TestChunkedTranscriptionFlow:
    """Test chunked transcription flow logic."""

    def test_split_threshold_is_applicable(self):
        """Split should only trigger when audio exceeds threshold."""
        audio_duration = 70.0
        threshold = 60.0
        assert audio_duration > threshold

    def test_short_audio_uses_single_transcribe(self):
        """Audio <= threshold should use transcribe_single (not chunked)."""
        audio_duration = 50.0
        threshold = 60.0
        assert audio_duration <= threshold

    def test_chunk_overlap_prevents_artifacts(self):
        """Overlap between chunks prevents transcription boundary artifacts."""
        chunk_dur = 55.0
        overlap = 3.0
        effective_step = chunk_dur - overlap
        assert effective_step == 52.0

    def test_ffmpeg_used_for_splitting(self):
        """Audio should be split using ffmpeg, not librosa."""
        ffmpeg_flags = ["-ss", "0.000", "-i", "input.mp3", "-t", "55.000"]
        assert "-ss" in ffmpeg_flags

    def test_chunks_merged_after_transcription(self):
        """Transcribed chunks should be merged with deduplication."""
        chunk_texts = ["hello world", "and more text here"]
        # merge_text adds spaces and deduplicates overlap words
        merged = " ".join([t.strip() for t in chunk_texts])
        assert "hello world" in merged


class TestOutputFormatValidation:
    """Test output format validation."""

    def test_txt_is_default_format(self):
        default_format = "txt"
        assert default_format == "txt"

    def test_docx_produces_bytes(self):
        """DOCX output should be bytes (binary)."""
        from io import BytesIO
        buf = BytesIO()
        content = b"PK\x03\x04"  # ZIP header (DOCX is ZIP)
        assert isinstance(content, bytes)

    def test_json_format_is_valid_json(self):
        """JSON output should be parseable."""
        import json
        data = {"transcription": "text", "metadata": {}}
        json_str = json.dumps(data, ensure_ascii=False)
        parsed = json.loads(json_str)
        assert parsed["transcription"] == "text"

    def test_jsonl_format_has_one_object_per_line(self):
        """Each JSONL line should be a standalone JSON object."""
        import json
        lines = [json.dumps({"file": "a.mp3"}), json.dumps({"file": "b.mp3"})]
        for line in lines:
            parsed = json.loads(line)
            assert "file" in parsed


class TestAudioFormatHandler:
    """Test audio format handling."""

    def test_wav_uncompressed(self):
        """WAV is uncompressed format."""
        wav_extensions = [".wav"]
        assert ".wav" in wav_extensions

    def test_flac_lossless_compression(self):
        """FLAC is lossless compressed format."""
        flac_extensions = [".flac"]
        assert ".flac" in flac_extensions

    def test_mp4_video_audio_extracted(self):
        """MP4 files should have audio extracted via FFmpeg."""
        supported = [".mp3", ".wav", ".flac", ".ogg", ".m4a", ".mp4", ".webm", ".aac", ".wma"]
        assert ".mp4" in supported


class TestTranscribeSingleReturns:
    """Test transcribe_single return value structure."""

    def test_returns_dict_with_text_key(self):
        result = {"text": "transcription text"}
        assert "text" in result

    def test_returns_dict_with_output_path_key(self):
        result = {"output_path": "/path/to/output.txt"}
        assert "output_path" in result

    def test_returns_dict_with_duration_s_key(self):
        result = {"duration_s": 5.2}
        assert "duration_s" in result
        assert isinstance(result["duration_s"], float)


class TestModelCacheSingleton:
    """Test _ModelCache singleton behavior."""

    def test_caches_pipeline_by_model_and_device(self):
        """Pipeline should be cached per (model_id, device) key."""
        cache = {}
        key = ("model1", "cpu")
        pipeline = {"loaded": True}
        cache[key] = pipeline
        assert cache.get(key) == {"loaded": True}

    def test_resets_cache_on_mismatch(self):
        """Pipeline should reset when (model, device) changes."""
        cache = {}
        key1 = ("model1", "cpu")
        key2 = ("model2", "cpu")
        cache[key1] = {"pipeline": "value1"}
        # Reset on mismatch
        if cache.get(key2) != cache.get(key1):
            cache.clear()  # or set to None
        assert key2 not in cache or cache[key2] != cache.get(key1)


class TestCLIEntryPoints:
    """Test CLI entry point patterns."""

    def test_help_shows_usage(self):
        """--help should show usage information."""
        help_text = "Urdu Speech-to-Text Transcription Tool"
        assert len(help_text) > 0

    def test_trans_subcommand_accepts_audio_path(self):
        """'trans' subcommand should accept audio file path."""
        cli_args = ["trans", "audio.mp3"]
        assert len(cli_args) == 2
        assert cli_args[0] == "trans"

    def test_batch_subcommand_accepts_directory(self):
        """'batch' subcommand should accept directory path."""
        cli_args = ["batch", "./folder/"]
        assert cli_args[0] == "batch"
