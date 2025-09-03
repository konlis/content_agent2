@echo off
REM Batch script to activate the venv312 virtual environment
REM Run this script to activate the environment: activate.bat

echo Activating Content Agent virtual environment...
call "venv312\Scripts\activate.bat"
echo Virtual environment activated! You can now run: python main.py --mode frontend
cmd /k
