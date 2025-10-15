#!/usr/bin/env python3
"""
YouTube Video/Audio Downloader CLI

This script allows you to download YouTube videos as MP4 (up to 1440p) or MP3 audio.
You can choose to download a single video or an entire playlist.

Requirements:
- Python 3.6+
- yt-dlp (install with: pip install yt-dlp)

Usage:
python youtube_downloader.py
Then follow the prompts.
"""

import yt_dlp
import os
import sys

def download_video(url, output_path='.', noplaylist=False):
    """Download video in best quality up to 1440p"""
    ydl_opts = {
        'format': 'bestvideo[height<=1440]+bestaudio/best[height<=1440]',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'noplaylist': noplaylist,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def download_audio(url, output_path='.', noplaylist=False):
    """Download audio as MP3"""
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'noplaylist': noplaylist,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def main():
    print("YouTube Downloader CLI")
    print("======================")

    # Get YouTube URL
    url = input("Enter YouTube URL: ").strip()
    if not url:
        print("No URL provided. Exiting.")
        sys.exit(1)

    # Choose format
    while True:
        choice = input("Download as MP4 (video) or MP3 (audio)? [mp4/mp3]: ").strip().lower()
        if choice in ['mp4', 'mp3']:
            break
        print("Invalid choice. Please enter 'mp4' or 'mp3'.")

    # Choose download type
    while True:
        dl_choice = input("Download: 1. Single video 2. Playlist (if applicable) [1/2]: ").strip()
        if dl_choice in ['1', '2']:
            noplaylist = dl_choice == '1'
            break
        print("Invalid choice. Please enter '1' or '2'.")

    # Set output path (optional)
    output_path = input("Output directory (press Enter for 'C:\\Users\\baret\\Videos'): ").strip()
    if not output_path:
        output_path = 'C:\\Users\\baret\\Videos'

    # Ensure output directory exists
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    try:
        if choice == 'mp4':
            print("Downloading video...")
            download_video(url, output_path, noplaylist)
        else:
            print("Downloading audio...")
            download_audio(url, output_path, noplaylist)
        print("Download completed successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()