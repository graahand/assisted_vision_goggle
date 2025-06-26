@echo off

REM Check if the virtual environment folder exists
IF NOT EXIST "venv" (
    echo Virtual environment not found. Creating a new virtual environment...
    python -m venv venv
)

REM Activate the virtual environment
call venv\Scripts\activate

REM Check if activation was successful
IF ERRORLEVEL 1 (
    echo Failed to activate the virtual environment.
    exit /b
)

REM Upgrade pip to the latest version
echo Upgrading pip to the latest version...
python -m pip install --upgrade pip

REM Install dependencies from requirements.txt
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt

echo Dependencies installed successfully.
pause
