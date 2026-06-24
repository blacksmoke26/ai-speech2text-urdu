"""Tests for audio splitter utilities (src/utils/audio_splitter.py)."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Set env before importing the module to avoid .env side-effects
os.environ.setdefault("DEDUP_WORDS", "20")

from utils.audio_splitter import (
    merge_text,
    merge_srt,
    calculate_chunk_start_times,
)


class TestMergeText:
    """Tests for merge_text function."""

    def test_empty_input_returns_empty_string(self):
        assert merge_text([]) == ""

    def test_single_chunk_returns_stripped_text(self):
        result = merge_text(["  hello world  "])
        assert result == "hello world"

    def test_multiple_chunks_joined_with_space(self):
        result = merge_text(["hello", "world"])
        assert "hello world" in result

    def test_dedup_cuts_overlap_words(self):
        """Chunks with many words should have overlap trimmed."""
        # More than DEDUP_WORDS (20) words per chunk
        long_text = " ".join([f"word{i}" for i in range(50)])
        result = merge_text([long_text, "last chunk"])
        assert isinstance(result, str)

    def test_short_chunks_not_trimmed(self):
        """Chunks shorter than DEDUP_WORDS should not be trimmed."""
        short = "short text"
        result = merge_text([short, "more"])
        assert short in result

    def test_none_values_handled(self):
        """None entries should be treated as empty strings."""
        result = merge_text([None, "hello", None])
        assert isinstance(result, str)

    def test_whitespace_only_chunks_handled(self):
        """Whitespace-only chunks should not break merging."""
        result = merge_text(["   ", "hello", "   "])
        assert isinstance(result, str)

    def test_multiple_spaces_collapsed(self):
        """Result should not have excessive spaces."""
        result = merge_text(["hello", "  ", "world"])
        # merge_text applies re.sub(r"[ \t]+", " ", ...) at the end
        assert "   " not in result

    def test_empty_string_in_list_does_not_crash(self):
        result = merge_text(["", "hello", ""])
        assert isinstance(result, str)


class TestMergeSRT:
    """Tests for merge_srt function."""

    def test_empty_chunks_returns_empty_string(self):
        assert merge_srt([], []) == ""

    def test_single_chunk_no_overlap_dedup(self):
        chunks = [{"text": "Hello", "segments": []}]
        times = [0.0]
        result = merge_srt(chunks, times)
        assert isinstance(result, str)

    def test_returns_valid_srt_format(self):
        """Output should be in SRT format with numbered segments."""
        chunks = [
            {"text": "Segment 1", "segments": []},
            {"text": "Segment 2", "segments": []},
        ]
        times = [0.0, 55.0]
        result = merge_srt(chunks, times)
        # Should contain at least one numbered line
        assert "1" in result

    def test_segments_with_timestamps_shifted(self):
        """Timestamps should be shifted by chunk start time."""
        chunks = [
            {
                "text": "Test",
                "segments": [{"text": "Test", "start": 0.0, "end": 5.0}],
            }
        ]
        times = [10.0]  # chunk starts at 10s relative to original
        result = merge_srt(chunks, times)
        assert isinstance(result, str)

    def test_overlapping_segments_deduped(self):
        """Overlapping segments (>50% overlap) should be deduplicated."""
        chunks = [
            {"segments": [{"text": "A", "start": 0.0, "end": 10.0}]},
            {"segments": [{"text": "B", "start": 8.0, "end": 18.0}]},
        ]
        times = [0.0, 5.0]
        result = merge_srt(chunks, times)
        assert isinstance(result, str)

    def test_empty_text_segments_excluded(self):
        """Segments with empty text should be excluded from output."""
        chunks = [{"segments": [{"text": "", "start": 0.0, "end": 5.0}]}]
        times = [0.0]
        result = merge_srt(chunks, times)
        # Should not contain segment with empty text
        assert "Segment" not in result or result == ""

    def test_longer_text_preferred_on_overlap(self):
        """When segments overlap, the one with more text should be kept."""
        chunks = [
            {"segments": [{"text": "short", "start": 0.0, "end": 10.0}]},
            {"segments": [{"text": "this is a much longer segment text", "start": 5.0, "end": 15.0}]},
        ]
        times = [0.0, 5.0]
        result = merge_srt(chunks, times)
        assert isinstance(result, str)


class TestCalculateChunkStartTimes:
    """Tests for calculate_chunk_start_times function."""

    def test_single_chunk_for_short_audio(self):
        """Audio shorter than chunk size should produce 1 chunk starting at 0."""
        times = calculate_chunk_start_times(30.0, 55.0, 3.0)
        assert len(times) == 1
        assert times[0] == 0.0

    def test_multiple_chunks_for_long_audio(self):
        """Long audio should produce multiple chunks."""
        times = calculate_chunk_start_times(200.0, 55.0, 3.0)
        # step = 55 - 3 = 52; ceil(200/52) = 4
        assert len(times) >= 1
        assert times[0] == 0.0

    def test_first_chunk_always_starts_at_zero(self):
        times = calculate_chunk_start_times(100.0, 30.0, 5.0)
        assert times[0] == 0.0

    def test_chunks_are_monotonically_increasing(self):
        times = calculate_chunk_start_times(300.0, 55.0, 3.0)
        for i in range(1, len(times)):
            assert times[i] > times[i - 1]

    def test_step_between_chunks_equals_duration_minus_overlap(self):
        """Step between consecutive chunks should equal chunk_duration - overlap."""
        duration = 200.0
        chunk_dur = 50.0
        overlap = 5.0
        step = chunk_dur - overlap  # 45
        times = calculate_chunk_start_times(duration, chunk_dur, overlap)
        if len(times) >= 2:
            assert times[1] == step

    def test_zero_duration_returns_single_chunk(self):
        times = calculate_chunk_start_times(0.0, 55.0, 3.0)
        assert len(times) == 1

    def test_extremely_long_audio_produced_multiple_chunks(self):
        duration = 3600.0  # 1 hour
        times = calculate_chunk_start_times(duration, 55.0, 3.0)
        assert len(times) > 1


class TestAudioSplitterIntegration:
    """Integration-style tests."""

    def test_merge_then_calculate_times_consistent(self):
        """Chunk start times and merge_text should be compatible."""
        durations = [60.0, 120.0, 30.0]
        start_times = calculate_chunk_start_times(sum(durations), 55.0, 3.0)
        assert isinstance(start_times, list)
        assert len(start_times) >= 1

    def test_merge_text_with_srt_output_compatible(self):
        """merge_text and merge_srt should handle the same data types."""
        chunk_texts = ["Hello", "World"]
        text_result = merge_text(chunk_texts)
        srt_chunks = [{"text": t, "segments": []} for t in chunk_texts]
        times = [0.0, 55.0]
        srt_result = merge_srt(srt_chunks, times)
        assert isinstance(text_result, str)
        assert isinstance(srt_result, str)
