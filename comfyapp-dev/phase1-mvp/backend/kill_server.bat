@echo off
echo Stopping any running Flux servers...

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8002') do (
    echo Killing process %%a
    taskkill /PID %%a /F
)

echo Done!
pause