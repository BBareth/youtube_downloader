@echo off
cd /d "C:\dev\youtube_downloader"
if not exist venv (
    echo Virtual environment not found. Creating venv...
    python -m venv venv
    echo Installing dependencies...
    call venv\Scripts\activate
    python -m pip install -r requirements.txt
    python -m playwright install
    deactivate
)
call venv\Scripts\activate
python youtube_downloader.py
deactivate
pause