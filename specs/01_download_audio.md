# Script #1: Download Audio (download_audio.py)

## Purpose
Downloads audio from YouTube URLs using YT-DLP. Processes multiple URLs from a CSV file and saves audio files to an output folder.

## Folder Structure
```
scripts/download_audio/
├── download_audio.py
├── input.csv
└── output/
```

## Input

### CSV File: `input.csv`
Located adjacent to the script. Edit this file before each run.

| Column | Description |
|--------|-------------|
| `url` | YouTube video URL |
| `format` | Audio format (default: `opus`) |

Example:
```csv
url,format
https://www.youtube.com/watch?v=abc123,opus
https://www.youtube.com/watch?v=def456,opus
```

## Output
- Audio files saved to `output/` folder adjacent to the script
- Filenames are extracted automatically from YouTube video titles by YT-DLP
- Log file: `logs/download_audio_YYYYMMDD_HHMMSS.log`

## Behavior

### Download Process
1. Read and validate `input.csv`
2. For each row, execute YT-DLP with:
   - `--extract-audio` flag to download audio only
   - `--audio-format` set to the format column value
   - `--retries 10` for connection/download retries
   - `--fragment-retries 10` for fragment retries
   - Output directed to the `output/` folder

### Error Handling
- If a download fails after all retries, log the error and continue to the next URL
- Never abort the batch due to a single failure
- At the end of the run, print a summary: successful downloads, failed downloads, and list of failed URLs

### Logging
- All stdout/stderr from YT-DLP commands written to log file
- Timestamps for each download attempt
- Final summary of results

## Usage
1. Edit `input.csv` with your URLs
2. Run: `python scripts/download_audio/download_audio.py`
3. Find downloaded files in `output/`

## Dependencies
- Python 3.x
- YT-DLP (installed globally)
