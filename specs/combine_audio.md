# Script #3: Combine Audio (combine_audio.py)

## Implementation Status
Not Implemented

## Purpose
Combines multiple audio files from a folder into a single audio file using FFmpeg.

## Folder Structure
```
scripts/combine_audio/
├── combine_audio.py
├── input/
│   └── (place audio files here with numbered prefixes)
└── output/
```

## Input

### Source Audio Files
Place audio files in the `input/` folder. Use numbered prefixes to control the order of combination.

Example naming:
```
input/
├── 01_intro.opus
├── 02_first_track.opus
├── 03_second_track.opus
└── 10_outro.opus
```

### Output Filename
The script will prompt for the output filename when run, or you can set it in a config at the top of the script.

## Output
- Single combined audio file in `output/` folder
- Original files in `input/` are unchanged
- Log file: `logs/combine_audio_YYYYMMDD_HHMMSS.log`

## Behavior

### File Ordering
Files are combined using **natural sorting**, which handles numbered prefixes correctly:
- `01_track.opus`, `02_track.opus`, `10_track.opus` (correct order)
- NOT: `01_track.opus`, `10_track.opus`, `02_track.opus` (alphabetical, wrong)

### Combination Process
1. Scan `input/` folder for audio files
2. Sort files using natural sorting
3. Create an FFmpeg concat file listing all inputs
4. Execute FFmpeg with:
   - `-f concat` for concatenation mode
   - `-safe 0` to allow absolute paths
   - `-c copy` to avoid re-encoding
5. Save combined file to `output/`

### Error Handling
- Abort if `input/` folder is empty
- Abort if FFmpeg concatenation fails
- Verify output file was created successfully

### Logging
- List of files to be combined (in order)
- FFmpeg output
- Final summary: output file path, total duration

## Usage
1. Place your numbered audio files in `input/`
2. Run: `python scripts/combine_audio/combine_audio.py`
3. Enter the desired output filename when prompted
4. Find combined file in `output/`

## Tip: Naming Files for Correct Order
Use zero-padded numbers as prefixes:
- `01_`, `02_`, ... `09_`, `10_`, `11_`

This ensures natural sorting produces the correct order.

## Dependencies
- Python 3.x
- FFmpeg (installed globally)
