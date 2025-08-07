#!/usr/bin/env python3
"""
FastAPI Backend for ComfyUI Image Processing
Phase 1 MVP - Basic functionality
"""
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io
import os
import uuid
import logging
from pathlib import Path
from typing import Optional

from ai_processor import get_processor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="ComfyUI Image Processor",
    description="Convert your ComfyUI workflow into a production API",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directories
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Mount static files (for serving images)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

# Serve frontend
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the simple frontend interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Image Processor - Phase 1 MVP</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                max-width: 800px; 
                margin: 0 auto; 
                padding: 20px;
                background: #f5f5f5;
            }
            .container { 
                background: white; 
                padding: 30px; 
                border-radius: 10px; 
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .upload-area {
                border: 2px dashed #ccc;
                border-radius: 10px;
                padding: 40px;
                text-align: center;
                margin: 20px 0;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .upload-area:hover { border-color: #007bff; }
            .upload-area.dragover { border-color: #007bff; background: #f0f8ff; }
            input[type="file"] { display: none; }
            input, textarea, button {
                width: 100%;
                padding: 10px;
                margin: 10px 0;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 16px;
            }
            button {
                background: #007bff;
                color: white;
                border: none;
                cursor: pointer;
                padding: 15px;
                font-weight: bold;
            }
            button:hover { background: #0056b3; }
            button:disabled { background: #ccc; cursor: not-allowed; }
            .preview { max-width: 100%; margin: 20px 0; border-radius: 10px; }
            .status { 
                padding: 15px; 
                border-radius: 5px; 
                margin: 10px 0; 
                text-align: center;
            }
            .status.processing { background: #fff3cd; border: 1px solid #ffeaa7; }
            .status.success { background: #d4edda; border: 1px solid #c3e6cb; }
            .status.error { background: #f8d7da; border: 1px solid #f5c6cb; }
            .hidden { display: none; }
            .slider-container {
                margin: 15px 0;
            }
            .slider-container label {
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
            }
            input[type="range"] {
                width: 100%;
            }
            .slider-value {
                color: #007bff;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎨 AI Image Processor</h1>
            <p>Upload an image and describe how you want it transformed</p>
            
            <form id="uploadForm">
                <div class="upload-area" onclick="document.getElementById('imageInput').click()">
                    <div id="uploadText">
                        📤 Click here to upload an image<br>
                        <small>Or drag and drop an image file</small>
                    </div>
                    <input type="file" id="imageInput" accept="image/*">
                </div>
                
                <img id="preview" class="preview hidden" alt="Preview">
                
                <textarea 
                    id="prompt" 
                    placeholder="Describe how you want to transform the image (e.g., 'make it look like an oil painting')"
                    rows="3"
                ></textarea>
                
                <textarea 
                    id="negativePrompt" 
                    placeholder="What to avoid in the result (optional)"
                    rows="2"
                ></textarea>
                
                <div class="slider-container">
                    <label>Strength: <span id="strengthValue" class="slider-value">0.8</span></label>
                    <input type="range" id="strength" min="0.1" max="1.0" step="0.1" value="0.8">
                    <small>How much to change the image (0.1 = subtle, 1.0 = major changes)</small>
                </div>
                
                <div class="slider-container">
                    <label>Quality Steps: <span id="stepsValue" class="slider-value">20</span></label>
                    <input type="range" id="steps" min="10" max="50" step="5" value="20">
                    <small>Higher = better quality but slower</small>
                </div>
                
                <button type="submit" id="processBtn">🚀 Transform Image</button>
            </form>
            
            <div id="status" class="status hidden"></div>
            <img id="result" class="preview hidden" alt="Result">
            <a id="downloadLink" class="hidden" download>⬇️ Download Result</a>
        </div>

        <script>
            const form = document.getElementById('uploadForm');
            const imageInput = document.getElementById('imageInput');
            const preview = document.getElementById('preview');
            const uploadArea = document.querySelector('.upload-area');
            const uploadText = document.getElementById('uploadText');
            const status = document.getElementById('status');
            const result = document.getElementById('result');
            const downloadLink = document.getElementById('downloadLink');
            const strengthSlider = document.getElementById('strength');
            const stepsSlider = document.getElementById('steps');
            
            // Update slider values
            strengthSlider.oninput = function() {
                document.getElementById('strengthValue').textContent = this.value;
            }
            stepsSlider.oninput = function() {
                document.getElementById('stepsValue').textContent = this.value;
            }
            
            // File input handling
            imageInput.addEventListener('change', handleFileSelect);
            
            // Drag and drop
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('dragover');
            });
            
            uploadArea.addEventListener('dragleave', () => {
                uploadArea.classList.remove('dragover');
            });
            
            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('dragover');
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    imageInput.files = files;
                    handleFileSelect();
                }
            });
            
            function handleFileSelect() {
                const file = imageInput.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        preview.src = e.target.result;
                        preview.classList.remove('hidden');
                        uploadText.innerHTML = '✅ Image uploaded: ' + file.name;
                    };
                    reader.readAsDataURL(file);
                }
            }
            
            // Form submission
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                if (!imageInput.files[0]) {
                    showStatus('Please select an image first', 'error');
                    return;
                }
                
                const prompt = document.getElementById('prompt').value.trim();
                if (!prompt) {
                    showStatus('Please enter a description', 'error');
                    return;
                }
                
                const formData = new FormData();
                formData.append('file', imageInput.files[0]);
                formData.append('prompt', prompt);
                formData.append('negative_prompt', document.getElementById('negativePrompt').value);
                formData.append('strength', strengthSlider.value);
                formData.append('num_inference_steps', stepsSlider.value);
                
                document.getElementById('processBtn').disabled = true;
                showStatus('Processing your image... This may take 30-60 seconds', 'processing');
                result.classList.add('hidden');
                downloadLink.classList.add('hidden');
                
                try {
                    const response = await fetch('/process-image', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (response.ok) {
                        const blob = await response.blob();
                        const imageUrl = URL.createObjectURL(blob);
                        result.src = imageUrl;
                        result.classList.remove('hidden');
                        downloadLink.href = imageUrl;
                        downloadLink.classList.remove('hidden');
                        showStatus('✅ Image processed successfully!', 'success');
                    } else {
                        const errorData = await response.json();
                        showStatus('❌ Error: ' + (errorData.detail || 'Processing failed'), 'error');
                    }
                } catch (error) {
                    showStatus('❌ Error: ' + error.message, 'error');
                }
                
                document.getElementById('processBtn').disabled = false;
            });
            
            function showStatus(message, type) {
                status.textContent = message;
                status.className = 'status ' + type;
                status.classList.remove('hidden');
            }
        </script>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """Check if the service is healthy"""
    try:
        processor = get_processor()
        health_status = processor.health_check()
        return health_status
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {e}")

@app.post("/process-image")
async def process_image(
    file: UploadFile = File(...),
    prompt: str = Form(...),
    negative_prompt: str = Form(""),
    strength: float = Form(0.8),
    num_inference_steps: int = Form(20),
    guidance_scale: float = Form(7.5),
    seed: int = Form(-1)
):
    """Process an uploaded image"""
    
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Read and process image
        image_data = await file.read()
        input_image = Image.open(io.BytesIO(image_data))
        
        logger.info(f"Processing image: {file.filename}, size: {input_image.size}")
        
        # Get processor and process image
        processor = get_processor()
        
        result_image = processor.process_image(
            input_image=input_image,
            prompt=prompt,
            negative_prompt=negative_prompt,
            strength=strength,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            seed=seed
        )
        
        # Save result
        output_filename = f"{uuid.uuid4()}.png"
        output_path = OUTPUT_DIR / output_filename
        result_image.save(output_path, "PNG")
        
        logger.info(f"Image processed successfully: {output_filename}")
        
        # Return the processed image
        return FileResponse(
            output_path,
            media_type="image/png",
            headers={"Content-Disposition": f"attachment; filename={output_filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {e}")

if __name__ == "__main__":
    import uvicorn
    
    # Load models on startup
    logger.info("Starting server and loading AI models...")
    processor = get_processor()
    
    # Start server
    uvicorn.run(app, host="0.0.0.0", port=8000)