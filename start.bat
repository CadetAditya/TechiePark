@echo off
echo ===================================================
echo  Starting Techie Park Server
echo ===================================================
call .venv\Scripts\activate.bat
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
pause

