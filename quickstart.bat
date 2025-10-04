@echo off
REM Quick Start Script for Trading Analysis System (Windows)

echo ========================================
echo Trading Analysis System - Quick Start
echo ========================================
echo.

REM Check Python version
echo 1. Checking Python version...
python --version
if errorlevel 1 (
    echo    X Python is not installed!
    echo    Please install Python 3.8+ from python.org
    pause
    exit /b 1
)
echo    √ Python is available
echo.

REM Check if virtual environment exists
echo 2. Checking virtual environment...
if not exist "venv\" (
    echo    Creating virtual environment...
    python -m venv venv
    echo    √ Virtual environment created
) else (
    echo    √ Virtual environment exists
)
echo.

REM Activate virtual environment
echo 3. Activating virtual environment...
call venv\Scripts\activate.bat
echo    √ Virtual environment activated
echo.

REM Install dependencies
echo 4. Installing dependencies...
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo    √ Dependencies installed
echo.

REM Check Ollama (optional)
echo 5. Checking Ollama (optional for AI analysis)...
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo    ! Ollama is not running (AI analysis will be skipped^)
    echo    To install: Download from https://ollama.ai/download
    echo    Then run: ollama pull llama2:13b
) else (
    echo    √ Ollama is running
)
echo.

REM Run integration tests
echo 6. Running integration tests...
python tests\test_integration.py

if errorlevel 1 (
    echo.
    echo ========================================
    echo X Tests failed - please check errors above
    echo ========================================
    pause
    exit /b 1
)

echo.
echo ========================================
echo √ ALL SYSTEMS READY!
echo ========================================
echo.
echo Quick commands to try:
echo.
echo   # Test with sample data (no AI):
echo   python main.py data\sample_trades.csv --trader-name "Sample" --no-ema
echo.
echo   # Full analysis with AI (requires Ollama):
echo   python main.py data\sample_trades.csv --trader-name "Sample"
echo.
echo   # Analyze your own data:
echo   python main.py C:\path\to\your\trades.csv --trader-name "YourName"
echo.
echo Reports will be saved in: data\reports\
echo.
pause
