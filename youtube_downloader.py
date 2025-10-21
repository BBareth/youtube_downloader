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
import getpass

def download_video(url, output_path='.', noplaylist=False):
    """Download video in best quality up to 1440p"""
    ydl_opts = {
        'format': 'bestvideo[height<=1440]+bestaudio/best[height<=1440]',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        # common options to reduce HTTP 403 issues
        'noplaylist': noplaylist,
        'geo_bypass': True,
        'nocheckcertificate': True,
        'http_chunk_size': 10485760,  # 10MB chunks
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
        'geo_bypass': True,
        'nocheckcertificate': True,
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
    default_videos = os.path.join(os.path.expanduser('~'), 'Videos')
    output_path = input(f"Output directory (press Enter for '{default_videos}'): ").strip()
    if not output_path:
        output_path = default_videos

    # optional cookiefile for authenticated or age-restricted content
    cookiefile = input("Cookie file path (optional, export from browser in Netscape format; press Enter to skip): ").strip()
    if cookiefile == '':
        cookiefile = None

    # Ensure output directory exists
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Build common options for dry-run/info-extract and pass cookiefile if provided
    common_opts = {
        'geo_bypass': True,
        'nocheckcertificate': True,
        'http_chunk_size': 10485760,
    }
    if cookiefile:
        common_opts['cookiefile'] = cookiefile

    # Do a dry-run extraction to catch permission/403 errors early and show clearer messages
    try:
        print('Probing URL (info extraction)...')
        with yt_dlp.YoutubeDL(common_opts) as ydl:
            ydl.extract_info(url, download=False)
    except Exception as e:
        print('\nFailed to extract video info. This often means the video is restricted, requires login, or yt-dlp needs cookies or an updated extractor.')
        print(f'Details: {e}')
        print("If the video is age-restricted or private, try exporting your browser cookies (Netscape format) and provide the path when prompted next time.")
        print("You can export cookies using browser extensions like 'EditThisCookie' or 'Get cookies.txt' and then re-run this script with the cookie file.")
        sys.exit(1)

    try:
        if choice == 'mp4':
            print("Downloading video...")
            # merge our download-specific options with common_opts
            ydl_opts = common_opts.copy()
            ydl_opts.update({'format': 'bestvideo[height<=1440]+bestaudio/best[height<=1440]',
                             'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                             'merge_output_format': 'mp4',
                             'noplaylist': noplaylist})
            if cookiefile:
                ydl_opts['cookiefile'] = cookiefile
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        else:
            print("Downloading audio...")
            ydl_opts = common_opts.copy()
            ydl_opts.update({'format': 'bestaudio/best',
                             'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                             'postprocessors': [{
                                 'key': 'FFmpegExtractAudio',
                                 'preferredcodec': 'mp3',
                                 'preferredquality': '192',
                             }],
                             'noplaylist': noplaylist})
            if cookiefile:
                ydl_opts['cookiefile'] = cookiefile
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        print("Download completed successfully!")
    except Exception as e:
        print(f"An error occurred during download: {e}")
        print("Common fixes: provide a cookie file, update yt-dlp (pip install -U yt-dlp), or try again later.")
        sys.exit(1)

if __name__ == "__main__":
    main()