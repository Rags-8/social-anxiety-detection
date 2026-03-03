@echo off
echo Starting Social Anxiety Backend...
cd /d "%~dp0"
pip install -r requirements.txt --quiet
echo.
echo Backend running at http://localhost:8001
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
