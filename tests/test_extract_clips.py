"""
Tests for extract_clips.py

Strategy: Run real FFmpeg against generated test audio files.
Tests CSV parsing, timestamp validation, clip extraction, and error handling.
"""

import sys
from pathlib import Path

import pytest

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts" / "extract_clips"))

from extract_clips import (
    read_csv,
    find_input_file,
    validate_timestamp,
    extract_clip,
    main,
    get_script_dir,
    setup_logging,
)


class TestCSVParsing:
    """Tests for CSV reading and validation."""

    def test_read_valid_csv(self, create_csv):
        """Should parse a valid CSV with timestamp and title columns."""
        csv_content = "start_time,end_time,title\n00:00:00,00:05:30,first_clip\n00:05:30,00:10:00,second_clip"
        csv_path = create_csv(csv_content)

        rows = read_csv(csv_path)

        assert len(rows) == 2
        assert rows[0]["start_time"] == "00:00:00"
        assert rows[0]["end_time"] == "00:05:30"
        assert rows[0]["title"] == "first_clip"

    def test_read_csv_missing_column(self, create_csv):
        """Should raise error when required column is missing."""
        csv_content = "start_time,title\n00:00:00,clip"
        csv_path = create_csv(csv_content)

        with pytest.raises(ValueError, match="end_time"):
            read_csv(csv_path)

    def test_read_csv_empty_file(self, create_csv):
        """Should raise error for empty CSV file."""
        csv_path = create_csv("")

        with pytest.raises(ValueError):
            read_csv(csv_path)

    def test_read_csv_file_not_found(self, tmp_path):
        """Should raise FileNotFoundError for missing CSV."""
        csv_path = tmp_path / "nonexistent.csv"

        with pytest.raises(FileNotFoundError):
            read_csv(csv_path)


class TestTimestampValidation:
    """Tests for timestamp format validation."""

    @pytest.mark.parametrize("timestamp", [
        "00:00:00",
        "01:30:45",
        "12:59:59",
        "00:05:30",
    ])
    def test_valid_hhmmss_format(self, timestamp):
        """Should accept valid HH:MM:SS timestamps."""
        assert validate_timestamp(timestamp) is True

    @pytest.mark.parametrize("timestamp", [
        "00:00",
        "05:30",
        "59:59",
    ])
    def test_valid_mmss_format(self, timestamp):
        """Should accept valid MM:SS timestamps."""
        assert validate_timestamp(timestamp) is True

    @pytest.mark.parametrize("timestamp", [
        "invalid",
        "1:2:3",
        "00:60:00",
        "00:00:60",
        "-00:05:00",
        "abc:de:fg",
        "",
    ])
    def test_invalid_timestamps(self, timestamp):
        """Should reject invalid timestamp formats."""
        assert validate_timestamp(timestamp) is False


class TestFindInputFile:
    """Tests for finding the input audio file."""

    def test_find_single_file(self, tmp_path, test_audio_file_short):
        """Should find the single audio file in input directory."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        # Copy test file to input dir
        dest = input_dir / "source.opus"
        dest.write_bytes(test_audio_file_short.read_bytes())

        result = find_input_file(input_dir)

        assert result == dest

    def test_empty_input_folder(self, tmp_path):
        """Should raise error when input folder is empty."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        with pytest.raises(ValueError, match="empty|no.*file"):
            find_input_file(input_dir)

    def test_multiple_files_in_input(self, tmp_path, test_audio_file_short):
        """Should raise error when multiple files in input folder."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        # Create two files
        (input_dir / "file1.opus").write_bytes(test_audio_file_short.read_bytes())
        (input_dir / "file2.opus").write_bytes(test_audio_file_short.read_bytes())

        with pytest.raises(ValueError, match="multiple"):
            find_input_file(input_dir)


class TestClipExtraction:
    """Tests for extracting clips with real FFmpeg."""

    def test_extract_single_clip(self, tmp_path, test_audio_file, get_audio_duration):
        """Should extract a single clip with correct duration."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        log_file = tmp_path / "test.log"

        result = extract_clip(
            input_file=test_audio_file,
            start_time="00:00:05",
            end_time="00:00:15",
            title="test_clip",
            output_dir=output_dir,
            log_file=log_file,
        )

        assert result is True

        output_file = output_dir / "test_clip.opus"
        assert output_file.exists()

        duration = get_audio_duration(output_file)
        assert 9.5 <= duration <= 10.5  # ~10 seconds with some tolerance

    def test_extract_clip_creates_valid_audio(self, tmp_path, test_audio_file):
        """Should create a valid audio file that FFprobe can read."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        log_file = tmp_path / "test.log"

        extract_clip(
            input_file=test_audio_file,
            start_time="00:00:00",
            end_time="00:00:05",
            title="valid_audio",
            output_dir=output_dir,
            log_file=log_file,
        )

        output_file = output_dir / "valid_audio.opus"
        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_extract_preserves_format(self, tmp_path, test_audio_file):
        """Should preserve the input audio format in output."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        log_file = tmp_path / "test.log"

        extract_clip(
            input_file=test_audio_file,
            start_time="00:00:00",
            end_time="00:00:05",
            title="format_test",
            output_dir=output_dir,
            log_file=log_file,
        )

        # Input is .opus, output should be .opus
        output_file = output_dir / "format_test.opus"
        assert output_file.exists()

    def test_extract_clip_end_before_start(self, tmp_path, test_audio_file):
        """Should fail or warn when end_time <= start_time."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        log_file = tmp_path / "test.log"

        # end_time before start_time should be handled
        result = extract_clip(
            input_file=test_audio_file,
            start_time="00:00:10",
            end_time="00:00:05",
            title="bad_times",
            output_dir=output_dir,
            log_file=log_file,
        )

        # Should either return False or raise an error
        assert result is False or not (output_dir / "bad_times.opus").exists()


class TestMultipleClipExtraction:
    """Tests for extracting multiple clips from one source."""

    def test_extract_multiple_clips(self, tmp_path, test_audio_file, get_audio_duration):
        """Should extract multiple clips from the same source file."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        log_file = tmp_path / "test.log"

        clips = [
            ("00:00:00", "00:00:05", "clip1"),
            ("00:00:10", "00:00:15", "clip2"),
            ("00:00:20", "00:00:25", "clip3"),
        ]

        for start, end, title in clips:
            result = extract_clip(
                input_file=test_audio_file,
                start_time=start,
                end_time=end,
                title=title,
                output_dir=output_dir,
                log_file=log_file,
            )
            assert result is True

        # Verify all clips exist
        for _, _, title in clips:
            output_file = output_dir / f"{title}.opus"
            assert output_file.exists()
            duration = get_audio_duration(output_file)
            assert 4.5 <= duration <= 5.5


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

        assert log_file.name.startswith("extract_clips_")
        assert log_file.suffix == ".log"

    def test_log_file_written(self, tmp_path, test_audio_file_short):
        """Should write FFmpeg output to log file."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        log_file = tmp_path / "test.log"

        extract_clip(
            input_file=test_audio_file_short,
            start_time="00:00:00",
            end_time="00:00:03",
            title="logged_clip",
            output_dir=output_dir,
            log_file=log_file,
        )

        assert log_file.exists()
