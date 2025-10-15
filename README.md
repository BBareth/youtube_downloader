# YouTube Downloader CLI

A simple command-line tool to download YouTube videos as MP4 (up to 1440p) or MP3 audio.

## Requirements

- Python 3.6 or higher
- yt-dlp library
- FFmpeg (for MP3 conversion)

## Installation

1. Install Python 3 from [python.org](https://www.python.org/downloads/) if not already installed.

2. Install yt-dlp:
   ```
   pip install yt-dlp
   ```

3. Install FFmpeg:
   - On Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH, or use a package manager like Chocolatey.
   - On macOS: `brew install ffmpeg`
   - On Linux: `sudo apt install ffmpeg` (Ubuntu/Debian) or equivalent.

## Usage

### Option 1: Command Line
Run the script:
```
python youtube_downloader.py
```

### Option 2: Double-click Executable
Double-click `run_downloader.bat` to run the script. This will open a command prompt window where you can interact with the downloader. The window will stay open after completion (due to the `pause` command).

Follow the prompts:
1. Enter the YouTube URL
2. Choose MP4 or MP3
3. Choose to download a single video or the entire playlist (if the URL is a playlist)
4. Specify output directory (optional, defaults to 'videos' folder)

The script will download the best available quality:
- MP4: Best video quality up to 1440p with best audio
- MP3: Best audio quality converted to MP3 (192kbps)

## Notes

- Make sure the YouTube URL is valid and the video is publicly available.
- Downloads may take time depending on video length and quality.
- Respect YouTube's terms of service and copyright laws.