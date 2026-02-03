# Testing Specification

## Overview
A test suite to verify the three scripts function correctly after changes. Tests run using pytest.

## Test Framework
- **Framework**: pytest
- **Location**: `tests/` folder at project root

## Folder Structure
```
tests/
├── conftest.py              # Shared fixtures
├── fixtures/
│   └── (generated test audio files)
├── test_download_audio.py
├── test_extract_clips.py
└── test_combine_audio.py
```

## Testing Strategy by Script

### download_audio.py
**Approach**: Mock YT-DLP, test script logic only

Since testing against real YouTube URLs is unreliable, we mock the YT-DLP subprocess calls and test:
- CSV parsing (valid and malformed input)
- Handling of missing/empty CSV
- Error handling when YT-DLP "fails" (mocked failure)
- Batch processing continues after individual failures
- Summary output (success/failure counts)
- Log file creation and content

**What we DON'T test**:
- Actual YouTube downloads
- YT-DLP behavior itself

### extract_clips.py
**Approach**: Run real FFmpeg against test audio files

**Setup**:
- Generate a short test audio file (~30 seconds) using FFmpeg in the fixture setup
- Use simple tones or silence - content doesn't matter, just needs valid audio structure

**Tests**:
- CSV parsing (valid and malformed input)
- Timestamp validation (correct format, end > start)
- Single clip extraction
- Multiple clip extraction from one source
- Output files exist with correct names
- Output files are valid audio (non-zero size, correct format)
- Handling of missing input file
- Handling of empty input folder
- Handling of multiple files in input folder (should abort)
- Log file creation and content

### combine_audio.py
**Approach**: Run real FFmpeg against test audio files

**Setup**:
- Generate multiple small test audio files (~5 seconds each) using FFmpeg in fixture setup
- Name them with numbered prefixes to test sorting

**Tests**:
- Natural sorting order (verify `1, 2, 10` not `1, 10, 2`)
- Combining two files
- Combining many files (5+)
- Output file exists and is valid audio
- Output duration roughly equals sum of input durations
- Handling of empty input folder
- Handling of non-audio files in input folder (should ignore or error gracefully)
- Log file creation and content
- Original files remain unchanged after combination

## Test Fixtures

### conftest.py
Shared fixtures available to all test files:

```python
# Fixtures to create:
- tmp_script_dir    # Temporary directory mimicking script folder structure
- test_audio_file   # Single short audio file for extract_clips tests
- test_audio_files  # Multiple numbered audio files for combine_audio tests
- mock_ytdlp        # Mocked YT-DLP subprocess for download_audio tests
```

### Audio File Generation
Test audio files are generated at test runtime using FFmpeg:
```bash
# Generate 30 seconds of silence as opus
ffmpeg -f lavfi -i anullsrc=r=48000:cl=stereo -t 30 -c:a libopus output.opus

# Generate 5 seconds of a 440Hz tone as opus
ffmpeg -f lavfi -i "sine=frequency=440:duration=5" -c:a libopus output.opus
```

Files are created in a temporary directory and cleaned up after tests complete.

## Running Tests

### Commands
```bash
# Run all tests (quiet mode - recommended)
pytest -q --tb=line

# Run tests for a specific script
pytest -q --tb=line tests/test_download_audio.py
pytest -q --tb=line tests/test_extract_clips.py
pytest -q --tb=line tests/test_combine_audio.py

# Run with full verbose output (debugging)
pytest -v

# Run and show print statements (debugging)
pytest -s
```

### Output Behavior
Default test runs use quiet mode (`-q --tb=line`) to minimize output:
- **Passing tests**: Shows `.` per test, summary at end
- **Failing tests**: Shows `F` and one-line failure summary, with details only for failures

This keeps output clean and avoids cluttering context with unnecessary information.

Any test audio files or temporary directories are cleaned up automatically.

## Dependencies
- pytest
- Python 3.x
- FFmpeg (installed globally)

Install test dependencies:
```bash
pip install pytest
```

## What Tests Verify
After any change to the scripts, running the test suite confirms:
1. CSV parsing still works correctly
2. Error handling behaves as expected
3. FFmpeg commands produce valid output
4. File/folder structure expectations are met
5. Logging works correctly
6. Edge cases are handled gracefully
