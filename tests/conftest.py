"""
Shared pytest fixtures for yt_extractor tests.
"""

import subprocess
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Path fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).parent.parent.resolve()


@pytest.fixture
def scripts_dir(project_root) -> Path:
    """Return the scripts directory."""
    return project_root / "scripts"


# ---------------------------------------------------------------------------
# Temporary directory fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_script_dir(tmp_path):
    """
    Create a temporary directory mimicking the script folder structure.
    Returns a dict with paths to input, output, logs directories and csv file.
    """
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    logs_dir = tmp_path / "logs"
    csv_file = tmp_path / "input.csv"

    input_dir.mkdir()
    output_dir.mkdir()
    logs_dir.mkdir()

    return {
        "root": tmp_path,
        "input": input_dir,
        "output": output_dir,
        "logs": logs_dir,
        "csv": csv_file,
    }


# ---------------------------------------------------------------------------
# Audio file generation fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def test_audio_file(tmp_path) -> Path:
    """
    Generate a single 30-second test audio file (opus format).
    Uses FFmpeg to create silence - content doesn't matter for testing.
    """
    output_file = tmp_path / "test_audio.opus"

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", "anullsrc=r=48000:cl=stereo",
        "-t", "30",
        "-c:a", "libopus",
        str(output_file)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        pytest.skip(f"FFmpeg failed to create test audio: {result.stderr}")

    return output_file


@pytest.fixture
def test_audio_file_short(tmp_path) -> Path:
    """
    Generate a single 5-second test audio file (opus format).
    Shorter version for faster tests.
    """
    output_file = tmp_path / "test_audio_short.opus"

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", "anullsrc=r=48000:cl=stereo",
        "-t", "5",
        "-c:a", "libopus",
        str(output_file)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        pytest.skip(f"FFmpeg failed to create test audio: {result.stderr}")

    return output_file


@pytest.fixture
def test_audio_files(tmp_path) -> list[Path]:
    """
    Generate multiple numbered test audio files for combine_audio tests.
    Creates 5 files of 3 seconds each with numbered prefixes.
    """
    files = []
    names = [
        "01_first.opus",
        "02_second.opus",
        "03_third.opus",
        "10_tenth.opus",  # Tests natural sorting (10 should come after 03, not after 01)
        "11_eleventh.opus",
    ]

    for name in names:
        output_file = tmp_path / name
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", "anullsrc=r=48000:cl=stereo",
            "-t", "3",
            "-c:a", "libopus",
            str(output_file)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            pytest.skip(f"FFmpeg failed to create test audio: {result.stderr}")

        files.append(output_file)

    return files


# ---------------------------------------------------------------------------
# Mock fixtures for download_audio tests
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_ytdlp_success():
    """
    Mock subprocess.run to simulate successful YT-DLP execution.
    """
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="[download] Downloading video...\n[download] 100%",
            stderr="",
        )
        yield mock_run


@pytest.fixture
def mock_ytdlp_failure():
    """
    Mock subprocess.run to simulate YT-DLP failure.
    """
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="ERROR: Video unavailable",
        )
        yield mock_run


@pytest.fixture
def mock_ytdlp_mixed(request):
    """
    Mock subprocess.run with configurable success/failure pattern.
    Use with @pytest.mark.parametrize to control which calls succeed.

    Example usage:
        @pytest.mark.parametrize("mock_ytdlp_mixed", [[True, False, True]], indirect=True)
        def test_mixed(mock_ytdlp_mixed):
            # First call succeeds, second fails, third succeeds
    """
    pattern = getattr(request, "param", [True])
    call_count = [0]

    def side_effect(*args, **kwargs):
        idx = call_count[0]
        call_count[0] += 1
        success = pattern[idx % len(pattern)]

        if success:
            return MagicMock(returncode=0, stdout="Success", stderr="")
        else:
            return MagicMock(returncode=1, stdout="", stderr="ERROR")

    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = side_effect
        yield mock_run


# ---------------------------------------------------------------------------
# Helper fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def create_csv(tmp_path):
    """
    Factory fixture to create CSV files with custom content.

    Usage:
        def test_something(create_csv):
            csv_path = create_csv("url,format\\nhttps://example.com,opus")
    """
    def _create_csv(content: str, filename: str = "input.csv") -> Path:
        csv_file = tmp_path / filename
        csv_file.write_text(content)
        return csv_file

    return _create_csv


@pytest.fixture
def get_audio_duration():
    """
    Factory fixture to get duration of an audio file using FFprobe.

    Usage:
        def test_something(get_audio_duration, some_audio_file):
            duration = get_audio_duration(some_audio_file)
    """
    def _get_duration(file_path: Path) -> float:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(file_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"FFprobe failed: {result.stderr}")
        return float(result.stdout.strip())

    return _get_duration
