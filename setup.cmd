@echo off
echo Installing WEDI Scraper Tool - Windows Compatible Version...

echo Step 1: Installing uv...
pip install uv

echo Step 2: Creating virtual environment...
uv venv

echo Step 3: Installing compatible versions for Windows...
uv pip install selenium==4.15.0
uv pip install webdriver-manager==4.0.1
uv pip install requests==2.31.0
uv pip install beautifulsoup4==4.12.2
uv pip install openpyxl==3.1.2
uv pip install python-dotenv==1.0.0

echo Step 4: Setting up Chrome path for Windows...
if not exist ".env" (
    echo CHROME_BINARY_PATH="C:\Program Files\Google\Chrome\Application\chrome.exe" > .env
    echo Chrome path set to default Windows location
    echo Please edit .env file if your Chrome is installed elsewhere
)

echo Step 5: Creating accounts.json example...
if not exist "accounts.json" (
    copy accounts.json.example accounts.json 2>nul
    echo Please edit accounts.json to add your login credentials
)

echo Setup complete! 
echo.
echo Next steps:
echo 1. Edit accounts.json with your WEDI login credentials
echo 2. Run the program: run.cmd
echo.
echo If you encounter any issues, please check README.md
pause