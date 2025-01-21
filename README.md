# FFmpeg Batch GUI

A Python-based graphical user interface for batch processing video and audio files using FFmpeg. This application is specifically designed to combine separate video and audio tracks, with support for various output formats and quality presets.

## Features

- Batch processing of video/audio file pairs
- Multiple output format options (mp4, mkv, mov, avi)
- Customizable FFmpeg parameters
- Quality presets (ultrafast, fast, medium, slow)
- Real-time progress tracking
- File matching for lecture recordings
- Multi-threaded processing
- Simple and intuitive interface

## Prerequisites

Before running the application, ensure you have:

1. Python 3.6 or higher
2. FFmpeg installed and added to your system PATH
   - Windows: Download from [FFmpeg official website](https://ffmpeg.org/download.html)
   - Mac: Install via Homebrew: `brew install ffmpeg`
   - Linux: Install via package manager: `sudo apt-get install ffmpeg`

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ffmpeg-batch-gui.git
cd ffmpeg-batch-gui
```

2. Install the required Python packages:
```bash
pip install -r requirements.txt
```

## Requirements.txt

Create a `requirements.txt` file with the following content:
```
tkinter
pathlib
```

Note: tkinter usually comes pre-installed with Python.

## Usage

1. Run the application:
```bash
python ffmpeg_batch_gui.py
```

2. Using the interface:
   - Click "Browse" to select input folder containing video/audio pairs
   - Select output folder for processed files
   - Choose desired output format (mp4, mkv, mov, avi)
   - Select quality preset based on your needs
   - Optionally add custom FFmpeg parameters
   - Click "Process Files" to start batch processing

## File Naming Convention

The current implementation uses a specific naming pattern for lecture recordings:
```
YYYY-MM-DD - Lecture X_video.m4s
YYYY-MM-DD - Lecture X_audio.m4s
```
Example:
```
2024-01-21 - Lecture 1_video.m4s
2024-01-21 - Lecture 1_audio.m4s
```

This pattern can be easily customized to suit your needs by modifying the `pattern` variable in the `find_matching_files` method. The current pattern was implemented for a specific use case involving lecture recordings, but you can adapt it for any naming convention by changing the regular expression in the code:

```python
# Current pattern
pattern = r'(\d{4}-\d{2}-\d{2} - Lecture \d+.*?)_(audio|video)\.m4s'

# Example of how to modify for different naming conventions:
# For files like: presentation1_video.mp4, presentation1_audio.mp4
# pattern = r'(.*?)_(audio|video)\.(m4s|mp4)'

# For files like: MyVideo-A.mp4, MyVideo-V.mp4
# pattern = r'(.*?)-([AV])\.(mp4|m4s)'
```

## Features In Detail

### Output Settings
- Format Selection: Choose between mp4, mkv, mov, and avi
- Quality Presets: ultrafast, fast, medium, slow
- Custom Parameters: Add specific FFmpeg command line options

### Progress Tracking
- Real-time progress bar
- File count tracking
- Processing status updates
- Completion notifications

### Performance
- Multi-threaded processing
- Optimal CPU core utilization
- Non-blocking GUI during processing

## Error Handling

The application includes robust error handling for:
- Missing FFmpeg installation
- Invalid file pairs
- Processing errors
- Output directory issues
- FFmpeg command execution errors

## Troubleshooting

1. "FFmpeg not found" error:
   - Verify FFmpeg is installed
   - Check if FFmpeg is in system PATH
   - Restart application after installation

2. Files not being detected:
   - Verify file naming pattern matches expected format
   - Check file permissions
   - Ensure files are in the selected input directory

3. Processing errors:
   - Check available disk space
   - Verify file permissions
   - Ensure files aren't in use by other applications
