@echo off
SETLOCAL

REM Remove any previous virtual environment
IF EXIST venv (
    rmdir /s /q venv
    echo Previous virtual environment removed.
)

REM Create a new virtual environment
python -m venv venv

REM Activate the virtual environment
CALL venv\Scripts\activate

echo Virtual environment created and activated.

REM Ensure pip is installed and updated
python -m pip install --upgrade pip

echo Pip updated and installed.

REM Install required packages
pip install -r requirements.txt

echo All requirements installed.

ENDLOCAL
pause