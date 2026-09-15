@echo off
chcp 65001 > nul
echo ==============================================================================
echo   KH?I ??NG LOCAL MCP & REST SERVER D?NH CHO GPT
echo ==============================================================================
cd /d "%~dp0"

if not exist ".env" (
    echo [INFO] T?o file .env t? .env.example...
    copy .env.example .env > nul
)

python run.py %*
pause
