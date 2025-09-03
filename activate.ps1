# PowerShell script to activate the venv312 virtual environment
# Run this script to activate the environment: .\activate.ps1

Write-Host "Activating Content Agent virtual environment..." -ForegroundColor Green
& ".\venv312\Scripts\Activate.ps1"
Write-Host "Virtual environment activated! You can now run: python main.py --mode frontend" -ForegroundColor Green
