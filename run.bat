@echo off
setlocal enabledelayedexpansion
cd /d %~dp0

if not exist .venv (
  echo Creating venv...
  python -m venv .venv
)

call .venv\Scripts\activate.bat
pip install -r requirements.txt
python -m bot.main



