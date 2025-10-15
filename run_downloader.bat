@echo off
cd /d "C:\dev\youtube_downloader"
call venv\Scripts\activate
C:\dev\youtube_downloader\venv\Scripts\python.exe youtube_downloader.py
deactivate
pause