@echo off
echo Starting Flux Kontext Max Server...
echo.
echo Make sure you have the following installed:
echo - Python 3.8+
echo - pip install fastapi uvicorn pillow python-multipart
echo.
echo The server will run on: http://localhost:8002
echo Press Ctrl+C to stop the server
echo.
pause

cd /d "%~dp0"
python start_server.py
pause