# Script #2: Extract Clips (extract_clips.py)

## Implementation Status
Not Implemented

## Purpose
Extracts audio clips from a source audio file using FFmpeg. Takes timestamp pairs from a CSV file and creates individual clip files. Designed for extracting songs from DJ mixes or long audio recordings.

## Folder Structure
```
scripts/extract_clips/
├── extract_clips.py
├── input/
│   └── (place source audio file here)
├── input.csv
└── output/
```

## Input

### Source Audio File
Place a single audio file in the `input/` folder. Any format supported by FFmpeg (opus, mp3, m4a, wav, etc.).

### CSV File: `input.csv`
Located adjacent to the script. Edit this file before each run.

| Column | Description |
|--------|-------------|
| `start_time` | Start timestamp of the clip (format: `HH:MM:SS` or `MM:SS`) |
| `end_time` | End timestamp of the clip (format: `HH:MM:SS` or `MM:SS`) |
| `title` | Output filename for the clip (without extension) |

Example:
```csv
start_time,end_time,title
00:00:00,00:05:30,01_opening_track
00:05:30,00:12:15,02_second_song
00:12:15,00:18:45,03_third_song
01:15:00,01:22:30,15_closing_track
```

## Output
- Individual audio clips saved to `output/` folder
- Output format matches input format (preserves codec)
- Filenames from the `title` column with original file extension
- Log file: `logs/extract_clips_YYYYMMDD_HHMMSS.log`

## Behavior

### Extraction Process
1. Find the audio file in `input/` folder
2. Read and validate `input.csv`
3. For each row, execute FFmpeg with:
   - `-ss` for start time (placed before `-i` for fast seeking)
   - `-to` for end time
   - `-c copy` to avoid re-encoding (fast, lossless)
   - Output file in the `output/` directory

### Error Handling
- Abort if `input/` folder is empty or contains multiple files
- If a clip extraction fails, log the error and continue to the next clip
- Validate timestamps are in correct format before processing
- Warn if end_time <= start_time
- At the end of the run, print a summary: successful extractions, failed extractions

### Logging
- All stdout/stderr from FFmpeg commands written to log file
- Timestamps for each extraction attempt
- Duration of each extracted clip
- Final summary of results

## Usage
1. Place your source audio file in `input/`
2. Edit `input.csv` with your timestamps and titles
3. Run: `python scripts/extract_clips/extract_clips.py`
4. Find extracted clips in `output/`

## Dependencies
- Python 3.x
- FFmpeg (installed globally)
