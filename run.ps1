# Script chạy PowerShell cho Local MCP Server
Set-Location -Path $PSScriptRoot

if (-not (Test-Path ".env")) {
    Write-Host "[INFO] Tạo file .env từ .env.example..." -ForegroundColor Cyan
    Copy-Item ".env.example" ".env"
}

python run.py $args
