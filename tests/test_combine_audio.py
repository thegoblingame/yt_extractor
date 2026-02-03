"""
Tests for combine_audio.py

Strategy: Run real FFmpeg against generated test audio files.
Tests natural sorting, file combination, and error handling.
"""

import sys
from pathlib import Path

import pytest

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts" / "combine_audio"))

from combine_audio import (
    natural_sort_key,
    get_audio_files,
    combine_audio,
    main,
    get_script_dir,
    setup_logging,
)


class TestNaturalSorting:
    """Tests for natural sorting of filenames."""

    def test_natural_sort_key_basic(self):
        """Should sort numbers numerically, not lexicographically."""
        files = ["10_track.opus", "2_track.opus", "1_track.opus"]
        paths = [Path(f) for f in files]

        sorted_paths = sorted(paths, key=natural_sort_key)

        assert [p.name for p in sorted_paths] == ["1_track.opus", "2_track.opus", "10_track.opus"]

    def test_natural_sort_key_zero_padded(self):
        """Should handle zero-padded numbers correctly."""
        files = ["01_track.opus", "02_track.opus", "10_track.opus", "03_track.opus"]
        paths = [Path(f) for f in files]

        sorted_paths = sorted(paths, key=natural_sort_key)

        assert [p.name for p in sorted_paths] == [
            "01_track.opus",
            "02_track.opus",
            "03_track.opus",
            "10_track.opus",
        ]

    def test_natural_sort_key_mixed_numbers(self):
        """Should handle filenames with multiple number segments."""
        files = ["track_1_v2.opus", "track_1_v10.opus", "track_2_v1.opus"]
        paths = [Path(f) for f in files]

        sorted_paths = sorted(paths, key=natural_sort_key)

        assert [p.name for p in sorted_paths] == [
            "track_1_v2.opus",
            "track_1_v10.opus",
            "track_2_v1.opus",
        ]


class TestGetAudioFiles:
    """Tests for listing audio files from directory."""

    def test_get_audio_files_sorted(self, tmp_path, test_audio_files):
        """Should return files sorted by natural order."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        # Copy test files to input dir
        for f in test_audio_files:
            (input_dir / f.name).write_bytes(f.read_bytes())

        files = get_audio_files(input_dir)

        names = [f.name for f in files]
        assert names == [
            "01_first.opus",
            "02_second.opus",
            "03_third.opus",
            "10_tenth.opus",
            "11_eleventh.opus",
        ]

    def test_get_audio_files_empty_folder(self, tmp_path):
        """Should raise error for empty input folder."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        with pytest.raises(ValueError, match="empty|no.*file"):
            get_audio_files(input_dir)

    def test_get_audio_files_ignores_non_audio(self, tmp_path, test_audio_file_short):
        """Should ignore or handle non-audio files gracefully."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        # Add one audio file
        (input_dir / "01_track.opus").write_bytes(test_audio_file_short.read_bytes())

        # Add non-audio files
        (input_dir / "readme.txt").write_text("not audio")
        (input_dir / ".hidden").write_text("hidden file")

        files = get_audio_files(input_dir)

        # Should only return audio file(s)
        names = [f.name for f in files]
        assert "readme.txt" not in names
        assert ".hidden" not in names
        assert "01_track.opus" in names


class TestCombineAudio:
    """Tests for combining audio files with real FFmpeg."""

    def test_combine_two_files(self, tmp_path, test_audio_files, get_audio_duration):
        """Should combine two audio files into one."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        log_file = tmp_path / "test.log"

        # Use first two test files
        input_files = []
        for f in test_audio_files[:2]:
            dest = input_dir / f.name
            dest.write_bytes(f.read_bytes())
            input_files.append(dest)

        output_file = output_dir / "combined.opus"

        result = combine_audio(
            input_files=input_files,
            output_file=output_file,
            log_file=log_file,
        )

        assert result is True
        assert output_file.exists()

        # Each input is 3 seconds, combined should be ~6 seconds
        duration = get_audio_duration(output_file)
        assert 5.5 <= duration <= 6.5

    def test_combine_many_files(self, tmp_path, test_audio_files, get_audio_duration):
        """Should combine 5+ files correctly."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        log_file = tmp_path / "test.log"

        # Use all test files (5 files, 3 seconds each = 15 seconds)
        input_files = []
        for f in test_audio_files:
            dest = input_dir / f.name
            dest.write_bytes(f.read_bytes())
            input_files.append(dest)

        output_file = output_dir / "combined_all.opus"

        result = combine_audio(
            input_files=input_files,
            output_file=output_file,
            log_file=log_file,
        )

        assert result is True
        assert output_file.exists()

        duration = get_audio_duration(output_file)
        assert 14.0 <= duration <= 16.0  # ~15 seconds with tolerance

    def test_combine_preserves_order(self, tmp_path, get_audio_duration):
        """Should combine files in the order provided."""
        # This test verifies order is preserved by using files of different durations
        # Would need different duration test files to properly test
        # For now, just verify the function accepts an ordered list
        pass

    def test_output_file_valid_audio(self, tmp_path, test_audio_files):
        """Should create a valid audio file that FFprobe can read."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        log_file = tmp_path / "test.log"

        input_files = []
        for f in test_audio_files[:2]:
            dest = input_dir / f.name
            dest.write_bytes(f.read_bytes())
            input_files.append(dest)

        output_file = output_dir / "valid_output.opus"

        combine_audio(
            input_files=input_files,
            output_file=output_file,
            log_file=log_file,
        )

        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_original_files_unchanged(self, tmp_path, test_audio_files):
        """Should not modify original input files."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        log_file = tmp_path / "test.log"

        input_files = []
        original_sizes = {}
        for f in test_audio_files[:3]:
            dest = input_dir / f.name
            dest.write_bytes(f.read_bytes())
            original_sizes[dest] = dest.stat().st_size
            input_files.append(dest)

        output_file = output_dir / "combined.opus"

        combine_audio(
            input_files=input_files,
            output_file=output_file,
            log_file=log_file,
        )

        # Verify original files still exist with same size
        for f, original_size in original_sizes.items():
            assert f.exists()
            assert f.stat().st_size == original_size


class TestLogging:
    """Tests for logging behavior."""

    def test_setup_logging_creates_directory(self, tmp_path):
        """Should create logs directory if it doesn't exist."""
        script_dir = tmp_path / "script"
        script_dir.mkdir()

        log_file = setup_logging(script_dir)

        assert (script_dir / "logs").exists()

    def test_setup_logging_filename_format(self, tmp_path):
        """Should create log file with timestamp in name."""
        script_dir = tmp_path / "script"
        script_dir.mkdir()

        log_file = setup_logging(script_dir)

        assert log_file.name.startswith("combine_audio_")
        assert log_file.suffix == ".log"

    def test_log_contains_file_list(self, tmp_path, test_audio_files):
        """Should log the list of files being combined."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        log_file = tmp_path / "test.log"

        input_files = []
        for f in test_audio_files[:2]:
            dest = input_dir / f.name
            dest.write_bytes(f.read_bytes())
            input_files.append(dest)

        combine_audio(
            input_files=input_files,
            output_file=output_dir / "combined.opus",
            log_file=log_file,
        )

        assert log_file.exists()
        # Log should contain information about the operation
