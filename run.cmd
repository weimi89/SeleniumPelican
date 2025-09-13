@echo off
echo Starting WEDI Scraper Tool...

if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found
    echo Please run setup.cmd first
    pause
    exit /b 1
)

.venv\Scripts\python.exe wedi_selenium_scraper.py %*

echo Process completed.
pause