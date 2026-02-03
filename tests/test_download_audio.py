"""
Tests for download_audio.py

Strategy: Mock YT-DLP subprocess calls, test script logic only.
We don't test actual YouTube downloads - just CSV parsing, error handling,
and batch processing behavior.
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts" / "download_audio"))

from download_audio import read_csv, download_audio, main, get_script_dir, setup_logging


class TestCSVParsing:
    """Tests for CSV reading and validation."""

    def test_read_valid_csv(self, create_csv):
        """Should parse a valid CSV with url and format columns."""
        csv_content = "url,format\nhttps://youtube.com/watch?v=abc123,opus\nhttps://youtube.com/watch?v=def456,mp3"
        csv_path = create_csv(csv_content)

        rows = read_csv(csv_path)

        assert len(rows) == 2
        assert rows[0]["url"] == "https://youtube.com/watch?v=abc123"
        assert rows[0]["format"] == "opus"
        assert rows[1]["url"] == "https://youtube.com/watch?v=def456"
        assert rows[1]["format"] == "mp3"

    def test_read_csv_missing_url_column(self, create_csv):
        """Should raise error when url column is missing."""
        csv_content = "format\nopus\nmp3"
        csv_path = create_csv(csv_content)

        with pytest.raises(ValueError, match="url"):
            read_csv(csv_path)

    def test_read_csv_missing_format_column(self, create_csv):
        """Should raise error when format column is missing."""
        csv_content = "url\nhttps://youtube.com/watch?v=abc123"
        csv_path = create_csv(csv_content)

        with pytest.raises(ValueError, match="format"):
            read_csv(csv_path)

    def test_read_csv_empty_file(self, create_csv):
        """Should raise error for empty CSV file."""
        csv_content = ""
        csv_path = create_csv(csv_content)

        with pytest.raises(ValueError):
            read_csv(csv_path)

    def test_read_csv_headers_only(self, create_csv):
        """Should return empty list when CSV has headers but no data rows."""
        csv_content = "url,format"
        csv_path = create_csv(csv_content)

        rows = read_csv(csv_path)

        assert rows == []

    def test_read_csv_file_not_found(self, tmp_path):
        """Should raise FileNotFoundError for missing CSV."""
        csv_path = tmp_path / "nonexistent.csv"

        with pytest.raises(FileNotFoundError):
            read_csv(csv_path)

    def test_read_csv_empty_url(self, create_csv):
        """Should skip or error on rows with empty URL."""
        csv_content = "url,format\n,opus\nhttps://youtube.com/watch?v=abc123,opus"
        csv_path = create_csv(csv_content)

        rows = read_csv(csv_path)

        # Should either skip empty rows or raise an error
        # Implementation decides which - test the chosen behavior
        assert all(row["url"] for row in rows)


class TestDownloadFunction:
    """Tests for the download_audio function with mocked YT-DLP."""

    def test_download_success(self, tmp_path, mock_ytdlp_success):
        """Should return True when YT-DLP succeeds."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        log_file = tmp_path / "test.log"

        result = download_audio(
            url="https://youtube.com/watch?v=abc123",
            audio_format="opus",
            output_dir=output_dir,
            log_file=log_file,
        )

        assert result is True
        mock_ytdlp_success.assert_called_once()

    def test_download_failure(self, tmp_path, mock_ytdlp_failure):
        """Should return False when YT-DLP fails."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        log_file = tmp_path / "test.log"

        result = download_audio(
            url="https://youtube.com/watch?v=abc123",
            audio_format="opus",
            output_dir=output_dir,
            log_file=log_file,
        )

        assert result is False

    def test_download_calls_ytdlp_with_correct_args(self, tmp_path, mock_ytdlp_success):
        """Should call YT-DLP with expected arguments."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        log_file = tmp_path / "test.log"

        download_audio(
            url="https://youtube.com/watch?v=test",
            audio_format="mp3",
            output_dir=output_dir,
            log_file=log_file,
        )

        call_args = mock_ytdlp_success.call_args
        cmd = call_args[0][0]  # First positional arg is the command list

        assert "yt-dlp" in cmd[0] or cmd[0] == "yt-dlp"
        assert "--extract-audio" in cmd
        assert "--audio-format" in cmd
        assert "mp3" in cmd
        assert "--retries" in cmd
        assert "--fragment-retries" in cmd


class TestBatchProcessing:
    """Tests for batch processing behavior."""

    @pytest.mark.parametrize("mock_ytdlp_mixed", [[True, False, True]], indirect=True)
    def test_continues_after_failure(self, tmp_path, create_csv, mock_ytdlp_mixed):
        """Should continue processing after individual download failures."""
        csv_content = "url,format\nhttps://youtube.com/1,opus\nhttps://youtube.com/2,opus\nhttps://youtube.com/3,opus"
        csv_path = create_csv(csv_content)
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # This test requires main() or a batch processing function
        # The mock is set up so: call 1 succeeds, call 2 fails, call 3 succeeds
        # All three URLs should be attempted
        assert mock_ytdlp_mixed.call_count == 0  # Not called yet

        # TODO: Call the batch processing function and verify all 3 calls were made


class TestLogging:
    """Tests for logging behavior."""

    def test_setup_logging_creates_directory(self, tmp_path):
        """Should create logs directory if it doesn't exist."""
        script_dir = tmp_path / "script"
        script_dir.mkdir()

        log_file = setup_logging(script_dir)

        assert (script_dir / "logs").exists()
        assert log_file.parent == script_dir / "logs"

    def test_setup_logging_filename_format(self, tmp_path):
        """Should create log file with timestamp in name."""
        script_dir = tmp_path / "script"
        script_dir.mkdir()

        log_file = setup_logging(script_dir)

        assert log_file.name.startswith("download_audio_")
        assert log_file.suffix == ".log"

    def test_log_file_written(self, tmp_path, mock_ytdlp_success):
        """Should write YT-DLP output to log file."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        log_file = tmp_path / "test.log"

        download_audio(
            url="https://youtube.com/watch?v=abc123",
            audio_format="opus",
            output_dir=output_dir,
            log_file=log_file,
        )

        assert log_file.exists()
        content = log_file.read_text()
        assert len(content) > 0


class TestSummaryOutput:
    """Tests for end-of-run summary."""

    def test_summary_counts_successes_and_failures(self):
        """Should report correct counts of successful and failed downloads."""
        # TODO: Implement after main() is fleshed out
        # This will test the summary printed at the end of a batch run
        pass

    def test_summary_lists_failed_urls(self):
        """Should list URLs that failed to download."""
        # TODO: Implement after main() is fleshed out
        pass
