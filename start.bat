@echo off
REM Start script for Church Media Automation System (Windows)

echo Starting Church Media Automation System...

REM Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found. Please run setup first:
    echo    python -m venv venv
    echo    venv\Scripts\activate
    echo    pip install -r requirements.txt
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate

REM Check dependencies
echo Checking dependencies...
python utils\dependency_manager.py check

REM Start API server
echo Starting API server on port 5000...
start /B uvicorn api_server:app --host 0.0.0.0 --port 5000

REM Wait a moment
timeout /t 2 /nobreak

REM Start frontend
echo Starting frontend on port 3000...
cd frontend
start /B npm run dev

echo.
echo System started!
echo Web interface: http://localhost:3000
echo API server: http://localhost:5000
echo.
echo Press Ctrl+C to stop services
pause
