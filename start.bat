@echo off
echo PyImageEditor - Setup and Launch Script
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)
echo [OK] Python found

REM Check Tesseract installation
tesseract --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Tesseract OCR not found
    echo   Font detection will not work without Tesseract
    echo   Download from: https://github.com/UB-Mannheim/tesseract/wiki
    echo.
) else (
    echo [OK] Tesseract OCR found
)

REM Install Python dependencies
echo.
echo Installing Python dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed

REM Launch application
echo.
echo Launching PyImageEditor...
echo.
python main.py
