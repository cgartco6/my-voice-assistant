@echo off
title My Voice AI Assistant
echo =======================================
echo  Voice AI Assistant - Windows Setup
echo =======================================
echo.

echo Step 1: Installing Python packages...
pip install gradio ollama pyyaml speechrecognition pyttsx3
if errorlevel 1 (
    echo Failed to install packages. Make sure Python is installed.
    pause
    exit /b 1
)
echo.

echo Step 2: Checking Ollama...
where ollama >nul 2>nul
if errorlevel 1 (
    echo Ollama not found. Please install from https://ollama.com
    pause
    exit /b 1
)
echo.

echo Step 3: Pulling uncensored model (first time only, may take several minutes)...
ollama pull dolphin-mistral
echo.

echo Step 4: Starting Voice AI Assistant...
echo.
echo After the server starts, open http://127.0.0.1:7860 in your browser.
echo Make sure your microphone is allowed in the browser.
echo Press Ctrl+C in this window to stop the server.
echo.
python app.py
pause
