@echo off
title Cocolevio - AI Multi-Agent System
color 0A

echo ============================================
echo   AI Multi-Agent System - Launcher
echo ============================================
echo.

:: --- Start Backend ---
echo [1/2] Starting Backend (FastAPI on port 8000)...
cd /d "%~dp0backend"

if not exist "venv\Scripts\activate.bat" (
    echo [!] Virtual environment not found. Creating one...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo [*] Installing backend dependencies...
    pip install fastapi uvicorn langgraph langchain-groq python-dotenv pydantic
) else (
    call venv\Scripts\activate.bat
)

start "Backend Server" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate.bat && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
echo [OK] Backend server starting in a new window.
echo.

:: --- Start Frontend ---
echo [2/2] Starting Frontend (Vite on port 5173)...
cd /d "%~dp0frontend"

if not exist "node_modules" (
    echo [*] Installing frontend dependencies...
    npm install
)

start "Frontend Server" cmd /k "cd /d %~dp0frontend && npm run dev"
echo [OK] Frontend dev server starting in a new window.
echo.

:: --- Done ---
echo ============================================
echo   Both servers are starting!
echo.
echo   Frontend : http://localhost:5173
echo   Backend  : http://localhost:8000
echo ============================================
echo.

timeout /t 5 /nobreak >nul
start http://localhost:5173

echo Press any key to exit this launcher...
pause >nul
