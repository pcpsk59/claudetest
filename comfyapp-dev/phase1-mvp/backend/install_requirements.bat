@echo off
echo Installing requirements for Flux Kontext Max...
echo.

pip install fastapi==0.104.1
pip install uvicorn==0.24.0
pip install pillow==10.0.1
pip install python-multipart==0.0.6
pip install python-dotenv==1.0.0

REM Segmentation dependencies
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install transformers==4.35.0
pip install accelerate==0.24.1
pip install opencv-python==4.8.1.78
pip install numpy==1.24.3
pip install replicate==0.22.0

echo.
echo Installation complete!
echo You can now run start.bat to launch the server
pause