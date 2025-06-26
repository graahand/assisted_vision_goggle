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

REM Upgrade pip to avoid compatibility issues
python -m pip install --upgrade pip

REM Install dependencies from requirements.txt if not already installed
IF EXIST "requirements.txt" (
    echo Installing/updating dependencies from requirements.txt...
    pip install -r requirements.txt
)

REM Run the Python script
echo Running main_book_reading.py...
python main_book_reading.py

REM Keep the command prompt open after script execution
pause
