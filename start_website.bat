@echo off
echo ========================================
echo    Face Matching Gateway - Website
echo ========================================
echo.

REM Check if virtual environment exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo No virtual environment found, using system Python...
)

REM Check if requirements are installed
python -c "import fastapi, uvicorn" >nul 2>&1
if errorlevel 1 (
    echo Installing requirements...
    pip install -r requirements.txt
)

REM Check if .env exists
if not exist .env (
    echo.
    echo WARNING: .env file not found!
    echo Please create a .env file with your configuration.
    echo.
    pause
    exit /b 1
)

echo Starting server...
echo.
echo Website: http://127.0.0.1:8080/web
echo API Docs: http://127.0.0.1:8080/docs
echo.
echo Press Ctrl+C to stop the server
echo ========================================

python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8080

pause