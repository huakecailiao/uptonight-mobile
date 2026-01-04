@echo off
cd /d "%~dp0"

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activate venv...
call venv\Scripts\activate

echo Installing/Checking dependencies...
pip install -r requirements.txt

echo Starting App...
python main.py
pause
