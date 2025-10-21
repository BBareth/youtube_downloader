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
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import shutil
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except Exception:
    PLAYWRIGHT_AVAILABLE = False

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

def download_direct_file(file_url, output_path='.', filename=None):
    """Download a file from a direct URL (HTTP/HTTPS) with streaming to disk."""
    if not filename:
        filename = os.path.basename(file_url.split('?')[0]) or 'downloaded_video'
    outpath = os.path.join(output_path, filename)

    with requests.get(file_url, stream=True, allow_redirects=True) as r:
        r.raise_for_status()
        with open(outpath, 'wb') as f:
            shutil.copyfileobj(r.raw, f)
    return outpath

def find_video_sources_in_page(page_url, cookiefile=None):
    """Fetch the page HTML and parse <video> tags and <source> elements for src attributes.

    Returns a list of absolute URLs found.
    """
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    cookies = None
    if cookiefile:
        # requests can't read Netscape cookie files directly; leave cookiefile support for yt-dlp only
        cookiefile = None
    resp = requests.get(page_url, headers=headers, allow_redirects=True, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    urls = []
    # <video src="..."> and <video><source src=...></video>
    for video in soup.find_all('video'):
        src = video.get('src')
        if src:
            urls.append(urljoin(page_url, src))
        for source in video.find_all('source'):
            s = source.get('src')
            if s:
                urls.append(urljoin(page_url, s))
    # dedupe while preserving order
    seen = set(); unique = []
    for u in urls:
        if u not in seen:
            seen.add(u); unique.append(u)
    return unique

def playwright_extract_urls(page_url, timeout=15000):
    """Use Playwright to render JS and capture media URLs (m3u8, mp4, blob URLs are skipped).

    Returns a list of discovered media URLs.
    """
    if not PLAYWRIGHT_AVAILABLE:
        raise RuntimeError('Playwright not installed. Install with `pip install playwright` and run `playwright install`')

    found = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        def on_response(response):
            try:
                url = response.url
                # catch common media types
                if any(x in url.lower() for x in ('.m3u8', '.mp4', '.webm', '.mp3')):
                    found.append(url)
            except Exception:
                pass

        page.on('response', on_response)
        page.goto(page_url, timeout=timeout)
        # wait a short while for network activity
        page.wait_for_timeout(3000)

        # also check rendered <video> tags
        vids = page.query_selector_all('video')
        for v in vids:
            src = v.get_attribute('src')
            if src:
                found.append(urljoin(page_url, src))
            sources = v.query_selector_all('source')
            for s in sources:
                ssrc = s.get_attribute('src')
                if ssrc:
                    found.append(urljoin(page_url, ssrc))

        browser.close()
    # dedupe
    seen=set(); unique=[]
    for u in found:
        if u and u not in seen and not u.startswith('blob:'):
            seen.add(u); unique.append(u)
    return unique

def main():
    print("YouTube Downloader CLI")
    print("======================")

    # Get URL
    url = input("Enter URL: ").strip()
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
        # Try yt-dlp first for known sites and for cookie support
        ydl_probe_opts = common_opts.copy()
        if cookiefile:
            ydl_probe_opts['cookiefile'] = cookiefile
        with yt_dlp.YoutubeDL(ydl_probe_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            # if yt-dlp finds direct downloadable URLs (like http(s) links), proceed normally
            formats = info.get('formats') if isinstance(info, dict) else None
            if not formats and info.get('is_live') is None and info.get('url'):
                # no formats but direct url exists; allow continuing
                pass
    except Exception as e:
        # If yt-dlp failed to extract, try a generic HTML <video> tag fallback
        print('\nyt-dlp could not extract info. Attempting <video> tag fallback...')
        try:
            sources = find_video_sources_in_page(url, cookiefile=cookiefile)
            if not sources:
                print('No <video> tags or <source> elements with src attributes were found on the page.')
                # try Playwright fallback if available
                if PLAYWRIGHT_AVAILABLE:
                    resp = input('Playwright is available. Attempt headless rendering to extract JS-loaded media? [y/N]: ').strip().lower()
                    if resp == 'y':
                        try:
                            pw_sources = playwright_extract_urls(url)
                            if pw_sources:
                                sources = pw_sources
                                print('Playwright found media URLs:')
                                for i,s in enumerate(sources,1):
                                    print(f"{i}. {s}")
                            else:
                                print('Playwright did not find any media URLs.')
                        except Exception as pw_e:
                            print('Playwright extraction failed:', pw_e)
                else:
                    print('Playwright is not installed. To enable JS rendering, run:')
                    print('  python -m pip install playwright')
                    print('  python -m playwright install')

                if not sources:
                    print('Details from yt-dlp probe:', e)
                    print("If the site uses JavaScript to load video sources, a headless browser is required (Playwright).")
                    sys.exit(1)
            print('Found the following direct video sources:')
            for i, s in enumerate(sources, 1):
                print(f"{i}. {s}")
            sel = input(f"Select source to download [1-{len(sources)}] (or press Enter to download all): ").strip()
            choices = []
            if sel:
                try:
                    idx = int(sel) - 1
                    if 0 <= idx < len(sources):
                        choices = [sources[idx]]
                    else:
                        print('Selection out of range. Will download all sources.')
                        choices = sources
                except ValueError:
                    print('Invalid selection. Will download all sources.')
                    choices = sources
            else:
                choices = sources

            # ensure output dir
            if not os.path.exists(output_path):
                os.makedirs(output_path)

            for src in choices:
                print(f'Downloading direct file: {src}')
                out = download_direct_file(src, output_path=output_path)
                print(f'Downloaded to: {out}')
                if choice == 'mp3':
                    # try to convert to mp3 using yt-dlp postprocessor (works if ffmpeg available)
                    try:
                        ydl_opts = {'outtmpl': out + '.%(ext)s', 'postprocessors': [{
                            'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]}
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                            ydl.process_info({'_type': 'url', 'url': out})
                    except Exception:
                        print('Audio conversion failed; ensure ffmpeg is installed.')
            print('Fallback downloads complete.')
            sys.exit(0)
        except Exception as e2:
            print('Fallback attempt failed.')
            print('Details:', e2)
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