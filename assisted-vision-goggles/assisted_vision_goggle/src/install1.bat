@echo off
REM Set the path to the Python installer
set "PYTHON_INSTALLER=path_to_python_installer.exe"

REM Install Python 3.12.4 silently (without UI)
%PYTHON_INSTALLER% /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

REM Verify Python installation
python --version
IF ERRORLEVEL 1 (
    echo Python installation failed. Exiting...
    exit /b
)

REM Create a virtual environment in the current directory
python -m venv venv

REM Activate the virtual environment
call venv\Scripts\activate

echo Virtual environment created and activated successfully.
pause
