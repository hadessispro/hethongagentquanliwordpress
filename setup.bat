@echo off
chcp 65001 > nul
echo ==============================================================================
echo   C?I ??T M?I TR??NG LOCAL MCP & REST SERVER CHO GPT TR?N LAPTOP
echo ==============================================================================

cd /d "%~dp0"

echo [1/4] Ki?m tra v? t?o file c?u h?nh .env...
if not exist ".env" (
    copy .env.example .env > nul
    echo       ?? t?o file .env t? .env.example.
) else (
    echo       File .env ?? t?n t?i.
)

echo.
echo [2/4] C?i ??t c?c th? vi?n Python...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [L?I] C?i ??t th? vi?n Python th?t b?i! Vui l?ng ki?m tra Python tr?n m?y.
    pause
    exit /b 1
)

echo.
echo [3/4] C?i ??t c?c g?i Node.js cho Ponytail...
call npm --prefix ponytail install
call npm --prefix ponytail/ponytail-mcp install

echo.
echo [4/4] Ki?m tra t?i ngrok binary qua pyngrok...
python -c "import os; from pyngrok import conf, installer; p = conf.get_default().ngrok_path; installer.install_ngrok(p) if not os.path.exists(p) else None; print('Ngrok s?n s?ng t?i:', p)"

echo.
echo ==============================================================================
echo   C?I ??T HO?N T?T!
echo   1. M? file .env v? ?i?n NGROK_AUTHTOKEN c?a b?n v?o.
echo   2. Nh?p ??p v?o file run.bat ?? kh?i ??ng server v? k?t n?i ChatGPT.
echo ==============================================================================
pause
