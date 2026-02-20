@echo off
echo ====================================
echo Emotion Detection Django App Setup
echo ====================================
echo.

cd /d "%~dp0"

echo Step 1: Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)
echo.

echo Step 2: Creating virtual environment...
if not exist venv (
    python -m venv venv
    echo Virtual environment created successfully!
) else (
    echo Virtual environment already exists.
)
echo.

echo Step 3: Activating virtual environment...
call venv\Scripts\activate.bat
echo.

echo Step 4: Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
echo.

echo Step 5: Running migrations...
python manage.py migrate
echo.

echo ====================================
echo Setup Complete!
echo ====================================
echo.
echo Starting Django development server...
echo The app will be available at: http://127.0.0.1:8000/
echo.
echo Press Ctrl+C to stop the server
echo.

python manage.py runserver
pause
