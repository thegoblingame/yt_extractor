# Project Overview

## Purpose

A collection of Python scripts for downloading, extracting, and combining audio from YouTube videos. Designed for workflows like extracting individual songs from DJ mixes or long recordings.

## Workflow

Each script is standalone and must be run individually. There is no automated pipeline—you run one script, then manually set up the input for the next.

**Typical use case**: Download a DJ mix from YouTube, extract individual tracks using timestamps, then optionally recombine selected tracks into a custom mix.

## Scripts

| Script | Purpose | Spec |
|--------|---------|------|
| `download_audio.py` | Download audio from YouTube URLs via YT-DLP | [01_download_audio.md](01_download_audio.md) |
| `extract_clips.py` | Extract clips from audio using timestamps via FFmpeg | [02_extract_clips.md](02_extract_clips.md) |
| `combine_audio.py` | Combine multiple audio files into one via FFmpeg | [03_combine_audio.md](03_combine_audio.md) |

## Project Structure

```
yt_extractor/
├── main.py
├── scripts/
│   ├── download_audio/
│   │   ├── download_audio.py
│   │   ├── input.csv
│   │   └── output/
│   ├── extract_clips/
│   │   ├── extract_clips.py
│   │   ├── input/
│   │   ├── input.csv
│   │   └── output/
│   └── combine_audio/
│       ├── combine_audio.py
│       ├── input/
│       └── output/
├── tests/
│   ├── conftest.py
│   ├── fixtures/
│   ├── test_download_audio.py
│   ├── test_extract_clips.py
│   └── test_combine_audio.py
├── logs/
└── specs/
```

## Dependencies

- **Python 3.x**
- **YT-DLP** - For downloading audio from YouTube
- **FFmpeg** - For audio extraction and combination
- **pytest** - For running tests

## Testing

Tests are run using pytest. See [04_testing.md](04_testing.md) for the full testing specification.

```bash
# Run all tests
pytest -q --tb=line

# Run tests for a specific script
pytest -q --tb=line tests/test_download_audio.py
```

## Spec Files

| File | Description |
|------|-------------|
| [01_download_audio.md](01_download_audio.md) | Spec for downloading audio from YouTube URLs |
| [02_extract_clips.md](02_extract_clips.md) | Spec for extracting clips using timestamps |
| [03_combine_audio.md](03_combine_audio.md) | Spec for combining multiple audio files |
| [04_testing.md](04_testing.md) | Testing strategy and pytest configuration |
