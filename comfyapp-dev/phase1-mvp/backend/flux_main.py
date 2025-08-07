#!/usr/bin/env python3
"""
Flux Kontext Max Image Processing App
Using Black Forest Labs API with Dynamic Prompting
"""
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io
import os
import uuid
import logging
import asyncio
from pathlib import Path
from typing import Optional, List
import json
from dotenv import load_dotenv

from flux_processor import get_processor
from segmentation_processor import get_segmentation_processor

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get API key from environment
BFL_API_KEY = os.getenv('BFL_API_KEY')
if not BFL_API_KEY:
    logger.error("BFL_API_KEY not found in environment variables. Please set it in .env file")
    raise ValueError("Missing BFL_API_KEY environment variable")
else:
    logger.info(f"BFL_API_KEY loaded: {BFL_API_KEY[:10]}...")

# Create FastAPI app
app = FastAPI(
    title="Flux Kontext Max Image Processor",
    description="Professional image-to-image generation with dynamic prompting",
    version="2.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Mount static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Professional Flux Kontext Max interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🎨 Flux Kontext Max - Professional Image Generator</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0; padding: 20px; min-height: 100vh;
            }
            .container { 
                max-width: 1200px; margin: 0 auto; 
                background: white; border-radius: 20px; 
                box-shadow: 0 20px 40px rgba(0,0,0,0.15);
                overflow: hidden;
            }
            .header {
                background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                color: white; padding: 30px; text-align: center;
            }
            .header h1 { margin: 0; font-size: 2.5rem; }
            .header p { margin: 10px 0 0 0; opacity: 0.9; }
            
            .main-content { padding: 30px; }
            
            .api-setup {
                background: #fff3cd; border: 1px solid #ffeaa7;
                padding: 20px; border-radius: 10px; margin-bottom: 30px;
            }
            
            .upload-section {
                display: grid; grid-template-columns: 1fr 1fr; gap: 30px;
                margin-bottom: 30px;
            }
            
            .upload-area {
                border: 3px dashed #ddd; border-radius: 15px;
                padding: 40px; text-align: center; cursor: pointer;
                transition: all 0.3s ease; position: relative;
            }
            .upload-area:hover { border-color: #667eea; background: #f8f9ff; }
            .upload-area.dragover { border-color: #667eea; background: #f0f8ff; }
            
            .preview-container {
                border: 2px solid #eee; border-radius: 15px;
                padding: 20px; text-align: center;
                min-height: 300px; display: flex; align-items: center; justify-content: center;
            }
            .preview { max-width: 100%; max-height: 280px; border-radius: 10px; }
            
            .controls-section {
                background: #f8f9fa; padding: 30px; border-radius: 15px; margin-bottom: 30px;
            }
            
            .control-group { margin-bottom: 25px; }
            .control-group label { 
                display: block; margin-bottom: 8px; 
                font-weight: 600; color: #2c3e50;
            }
            
            input[type="text"], select, textarea {
                width: 100%; padding: 12px; border: 2px solid #e9ecef;
                border-radius: 8px; font-size: 16px; transition: border-color 0.3s ease;
            }
            input[type="text"]:focus, select:focus, textarea:focus {
                border-color: #667eea; outline: none;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
            
            .template-grid {
                display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 15px; margin-top: 15px;
            }
            .template-card {
                border: 2px solid #e9ecef; border-radius: 10px; padding: 20px;
                cursor: pointer; transition: all 0.3s ease;
            }
            .template-card:hover { border-color: #667eea; background: #f8f9ff; }
            .template-card.selected { border-color: #667eea; background: #f0f8ff; }
            
            .slider-container {
                display: flex; align-items: center; gap: 15px;
            }
            .slider-container input[type="range"] {
                flex: 1; height: 8px; border-radius: 4px;
                background: #e9ecef; -webkit-appearance: none;
            }
            .slider-value {
                background: #667eea; color: white; padding: 5px 10px;
                border-radius: 15px; font-weight: bold; min-width: 50px; text-align: center;
            }
            
            .generate-section { text-align: center; margin: 30px 0; }
            .btn-generate {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; border: none; padding: 18px 40px;
                font-size: 18px; font-weight: bold; border-radius: 50px;
                cursor: pointer; transition: all 0.3s ease;
                box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
            }
            .btn-generate:hover { transform: translateY(-2px); box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4); }
            .btn-generate:disabled { background: #ccc; cursor: not-allowed; transform: none; }
            
            .results-section {
                border-top: 2px solid #e9ecef; padding-top: 30px; margin-top: 30px;
            }
            .results-grid {
                display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px; margin-top: 20px;
            }
            .result-card {
                border: 2px solid #e9ecef; border-radius: 15px; padding: 20px; text-align: center;
            }
            .result-card img { width: 100%; border-radius: 10px; margin-bottom: 15px; }
            
            .status {
                padding: 15px; border-radius: 10px; margin: 20px 0; text-align: center;
                font-weight: bold;
            }
            .status.processing { background: #fff3cd; border: 2px solid #ffeaa7; color: #856404; }
            .status.success { background: #d4edda; border: 2px solid #c3e6cb; color: #155724; }
            .status.error { background: #f8d7da; border: 2px solid #f5c6cb; color: #721c24; }
            .hidden { display: none; }
            
            input[type="file"] { display: none; }
            
            /* Segmentation Styles */
            .segmentation-section {
                background: #f0f8ff; border: 2px solid #e3f2fd; 
                border-radius: 15px; padding: 25px; margin: 25px 0;
            }
            .segmentation-grid {
                display: grid; grid-template-columns: 1fr 1fr; gap: 25px;
            }
            .segmentation-status {
                padding: 10px; border-radius: 8px; margin: 10px 0;
                background: #e8f5e8; border: 1px solid #c3e6c3; color: #2e7d2e;
            }
            .segmentation-status.processing {
                background: #fff3cd; border-color: #ffeaa7; color: #856404;
            }
            .segmentation-status.error {
                background: #f8d7da; border-color: #f5c6cb; color: #721c24;
            }
            .quality-indicator {
                display: flex; justify-content: space-between; 
                padding: 8px; border-radius: 6px; margin-top: 10px;
                background: #e8f5e8; font-size: 0.9em;
            }
            .quality-score { font-weight: bold; color: #2e7d2e; }
            .method-used { color: #666; font-style: italic; }
            
            @media (max-width: 768px) {
                .upload-section { grid-template-columns: 1fr; }
                .template-grid { grid-template-columns: 1fr; }
                .results-grid { grid-template-columns: 1fr; }
                .segmentation-grid { grid-template-columns: 1fr; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎨 Flux Kontext Max</h1>
                <p>Professional Image-to-Image Generation with Dynamic Prompting</p>
            </div>
            
            <div class="main-content">
                <div class="api-setup">
                    <h3>✅ API Configuration</h3>
                    <p style="margin: 0; color: #28a745; font-weight: bold;">🔐 API key configured securely on server</p>
                    <small>Your Black Forest Labs API key is stored safely in server environment variables</small>
                </div>
                
                <div class="upload-section">
                    <div>
                        <h3>📤 Upload Your Image</h3>
                        <div class="upload-area" onclick="document.getElementById('imageInput').click()">
                            <div id="uploadText">
                                Click here to upload an image<br>
                                <small>or drag and drop an image file</small>
                            </div>
                            <input type="file" id="imageInput" accept="image/*">
                        </div>
                    </div>
                    
                    <div>
                        <h3>🖼️ Original Preview</h3>
                        <div class="preview-container">
                            <img id="preview" class="preview hidden" alt="Preview">
                            <div id="previewPlaceholder">Your image will appear here</div>
                        </div>
                    </div>
                </div>
                
                <!-- Segmentation Section -->
                <div class="segmentation-section hidden" id="segmentationSection">
                    <h3>✂️ Garment Segmentation</h3>
                    <div class="segmentation-grid">
                        <div class="segmentation-controls">
                            <div class="control-group">
                                <label>🎯 Segmentation Prompt</label>
                                <input type="text" id="segmentationPrompt" value="saree" placeholder="e.g., saree, lehenga, dupatta">
                            </div>
                            <div class="segmentation-status" id="segmentationStatus">
                                <span class="status-text">Ready for segmentation</span>
                            </div>
                        </div>
                        <div class="segmentation-preview">
                            <h4>🔍 Segmented Preview</h4>
                            <div class="preview-container">
                                <img id="segmentationPreview" class="preview hidden" alt="Segmentation Preview">
                                <div id="segmentationPlaceholder">Segmented garment will appear here</div>
                            </div>
                            <div class="quality-indicator hidden" id="qualityIndicator">
                                <span class="quality-score">Quality: <span id="qualityScore">-</span>%</span>
                                <span class="method-used">Method: <span id="methodUsed">-</span></span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="controls-section">
                    <div class="control-group">
                        <label>📝 Subject Description</label>
                        <input type="text" id="subject" placeholder="e.g., 'a professional woman in business attire', 'a young man with casual style'">
                    </div>
                    
                    <div class="control-group">
                        <label>🎭 Master Template</label>
                        <div class="template-grid" id="templateGrid">
                            <!-- Templates loaded dynamically -->
                        </div>
                    </div>
                    
                    <div class="control-group">
                        <label>✨ Additional Style Elements (optional)</label>
                        <textarea id="customElements" rows="3" placeholder="Add custom style elements separated by commas, e.g., 'warm tones, soft focus, vintage aesthetic'"></textarea>
                    </div>
                    
                    <div class="control-group">
                        <label>💪 Transformation Strength</label>
                        <div class="slider-container">
                            <input type="range" id="strength" min="0.1" max="1.0" step="0.1" value="0.8">
                            <span id="strengthValue" class="slider-value">0.8</span>
                        </div>
                        <small>0.1 = subtle changes, 1.0 = dramatic transformation</small>
                    </div>
                </div>
                
                <div class="generate-section">
                    <button class="btn-generate" id="generateBtn" onclick="generateImage()">
                        🚀 Generate Professional Images
                    </button>
                </div>
                
                <div id="status" class="status hidden"></div>
                
                <div class="results-section hidden" id="resultsSection">
                    <h3>✨ Generated Results</h3>
                    <div class="results-grid" id="resultsGrid"></div>
                </div>
            </div>
        </div>
        
        <script>
            let selectedTemplate = 'studio_lighting';
            let apiKey = '';
            
            // Load available templates
            fetch('/templates')
                .then(response => response.json())
                .then(templates => loadTemplates(templates))
                .catch(error => console.error('Error loading templates:', error));
            
            function loadTemplates(templates) {
                const grid = document.getElementById('templateGrid');
                grid.innerHTML = '';
                
                Object.entries(templates).forEach(([key, name]) => {
                    const card = document.createElement('div');
                    card.className = 'template-card';
                    if (key === selectedTemplate) card.classList.add('selected');
                    
                    card.innerHTML = `
                        <h4>${name}</h4>
                        <small>Click to select this style</small>
                    `;
                    
                    card.onclick = () => {
                        document.querySelectorAll('.template-card').forEach(c => c.classList.remove('selected'));
                        card.classList.add('selected');
                        selectedTemplate = key;
                    };
                    
                    grid.appendChild(card);
                });
            }
            
            // API key is now handled securely on server-side
            // No client-side API key management needed
            window.onload = function() {
                // Initialize app
                console.log('Flux Kontext Max app initialized');
            };
            
            // File upload handling
            const imageInput = document.getElementById('imageInput');
            const preview = document.getElementById('preview');
            const uploadArea = document.querySelector('.upload-area');
            const strengthSlider = document.getElementById('strength');
            
            strengthSlider.oninput = function() {
                document.getElementById('strengthValue').textContent = this.value;
            };
            
            imageInput.addEventListener('change', handleFileSelect);
            
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
                        document.getElementById('previewPlaceholder').style.display = 'none';
                        document.getElementById('uploadText').innerHTML = 
                            '✅ Image uploaded: ' + file.name + '<br><small>Click to change</small>';
                        
                        // Show segmentation section and start auto-segmentation
                        document.getElementById('segmentationSection').classList.remove('hidden');
                        performSegmentation(file);
                    };
                    reader.readAsDataURL(file);
                }
            }
            
            async function performSegmentation(file) {
                const statusElement = document.getElementById('segmentationStatus');
                const previewElement = document.getElementById('segmentationPreview');
                const placeholderElement = document.getElementById('segmentationPlaceholder');
                const qualityElement = document.getElementById('qualityIndicator');
                const prompt = document.getElementById('segmentationPrompt').value || 'saree';
                
                // Update status
                statusElement.className = 'segmentation-status processing';
                statusElement.innerHTML = '<span class="status-text">🔄 Segmenting garment...</span>';
                
                try {
                    const formData = new FormData();
                    formData.append('file', file);
                    formData.append('prompt', prompt);
                    
                    const response = await fetch('/segment-garment', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (response.ok) {
                        const result = await response.json();
                        
                        if (result.success && result.segmented_image_url) {
                            // Show segmented preview
                            previewElement.src = result.segmented_image_url;
                            previewElement.classList.remove('hidden');
                            placeholderElement.style.display = 'none';
                            
                            // Show quality info
                            document.getElementById('qualityScore').textContent = Math.round(result.mask_quality * 100);
                            document.getElementById('methodUsed').textContent = result.method_used;
                            qualityElement.classList.remove('hidden');
                            
                            // Update status
                            statusElement.className = 'segmentation-status';
                            statusElement.innerHTML = '<span class="status-text">✅ Segmentation completed</span>';
                            
                        } else {
                            throw new Error(result.error_message || 'Segmentation failed');
                        }
                    } else {
                        throw new Error('Segmentation request failed');
                    }
                    
                } catch (error) {
                    console.error('Segmentation error:', error);
                    statusElement.className = 'segmentation-status error';
                    statusElement.innerHTML = '<span class="status-text">❌ Segmentation failed - will use original image</span>';
                }
            }
            
            async function generateImage() {
                if (!imageInput.files[0]) {
                    showStatus('Please select an image first', 'error');
                    return;
                }
                
                const subject = document.getElementById('subject').value.trim();
                if (!subject) {
                    showStatus('Please describe the subject in your image', 'error');
                    return;
                }
                
                const customElements = document.getElementById('customElements').value
                    .split(',').map(s => s.trim()).filter(s => s.length > 0);
                
                const formData = new FormData();
                formData.append('file', imageInput.files[0]);
                formData.append('subject', subject);
                formData.append('template_key', selectedTemplate);
                formData.append('strength', strengthSlider.value);
                if (customElements.length > 0) {
                    formData.append('custom_elements', JSON.stringify(customElements));
                }
                
                document.getElementById('generateBtn').disabled = true;
                showStatus('🎨 Generating your professional image using Flux Kontext Max... This may take 30-60 seconds', 'processing');
                
                try {
                    const response = await fetch('/generate-flux', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (response.ok) {
                        const result = await response.json();
                        showResults([result]);
                        showStatus('✅ Image generated successfully!', 'success');
                    } else {
                        const errorData = await response.json();
                        showStatus('❌ Error: ' + (errorData.detail || 'Generation failed'), 'error');
                    }
                } catch (error) {
                    showStatus('❌ Error: ' + error.message, 'error');
                }
                
                document.getElementById('generateBtn').disabled = false;
            }
            
            function showResults(results) {
                const section = document.getElementById('resultsSection');
                const grid = document.getElementById('resultsGrid');
                
                grid.innerHTML = '';
                results.forEach(result => {
                    const card = document.createElement('div');
                    card.className = 'result-card';
                    card.innerHTML = `
                        <img src="${result.image_url}" alt="Generated Result">
                        <h4>${result.template_name}</h4>
                        <p><small>${result.prompt.substring(0, 100)}...</small></p>
                        <a href="${result.image_url}" download class="btn" style="background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 10px;">
                            ⬇️ Download
                        </a>
                    `;
                    grid.appendChild(card);
                });
                
                section.classList.remove('hidden');
            }
            
            function showStatus(message, type) {
                const status = document.getElementById('status');
                status.textContent = message;
                status.className = 'status ' + type;
                status.classList.remove('hidden');
            }
        </script>
    </body>
    </html>
    """

@app.post("/segment-garment")
async def segment_garment(
    file: UploadFile = File(...),
    prompt: str = Form("saree")
):
    """Segment garment from uploaded image"""
    
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Read image
        image_data = await file.read()
        input_image = Image.open(io.BytesIO(image_data))
        
        # Get segmentation processor
        replicate_key = os.getenv('REPLICATE_API_TOKEN')
        seg_processor = get_segmentation_processor(replicate_key)
        
        # Perform segmentation
        result = seg_processor.segment_garment(input_image, prompt)
        
        if result['success'] and result['segmented_image']:
            # Save segmented image
            segment_filename = f"segment_{uuid.uuid4().hex[:8]}.png"
            segment_path = OUTPUT_DIR / segment_filename
            result['segmented_image'].save(segment_path, "PNG")
            
            # Create thumbnail preview
            thumbnail = seg_processor.create_preview_thumbnail(result['segmented_image'])
            thumb_filename = f"thumb_{uuid.uuid4().hex[:8]}.png"
            thumb_path = OUTPUT_DIR / thumb_filename
            thumbnail.save(thumb_path, "PNG")
            
            return {
                "success": True,
                "segmented_image_url": f"/outputs/{segment_filename}",
                "thumbnail_url": f"/outputs/{thumb_filename}",
                "mask_quality": result['mask_quality'],
                "method_used": result['method_used'],
                "prompt_used": prompt
            }
        else:
            # Segmentation failed - return original image info
            return {
                "success": False,
                "error_message": result.get('error_message', 'Segmentation failed'),
                "fallback_to_original": True
            }
            
    except Exception as e:
        logger.error(f"Error in segmentation endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/templates")
async def get_templates():
    """Get available master templates"""
    processor = get_processor()
    return processor.get_available_templates()

@app.get("/health")
async def health_check():
    """Check system health"""
    processor = get_processor()
    return processor.health_check()

@app.post("/generate-flux")
async def generate_flux_image(
    file: UploadFile = File(...),
    subject: str = Form(...),
    template_key: str = Form(...),
    custom_elements: str = Form(None),
    strength: float = Form(0.8)
):
    """Generate image using Flux Kontext Max"""
    
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Read image
        image_data = await file.read()
        input_image = Image.open(io.BytesIO(image_data))
        
        # Parse custom elements
        custom_elements_list = []
        if custom_elements:
            try:
                custom_elements_list = json.loads(custom_elements)
            except:
                custom_elements_list = [custom_elements]
        
        # Get processor with server-side API key
        processor = get_processor(BFL_API_KEY)
        
        # Process image
        result_image = await processor.process_image_to_image(
            input_image=input_image,
            subject=subject,
            template_key=template_key,
            custom_elements=custom_elements_list,
            strength=strength
        )
        
        # Save result
        output_filename = f"flux_{uuid.uuid4().hex[:8]}.png"
        output_path = OUTPUT_DIR / output_filename
        result_image.save(output_path, "PNG")
        
        # Get template info
        templates = processor.get_available_templates()
        template_name = templates.get(template_key, template_key)
        
        # Generate final prompt for display
        final_prompt = processor.generate_dynamic_prompt(subject, template_key, custom_elements_list)
        
        return {
            "success": True,
            "image_url": f"/outputs/{output_filename}",
            "template_name": template_name,
            "prompt": final_prompt,
            "filename": output_filename
        }
        
    except Exception as e:
        logger.error(f"Error generating image: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting Flux Kontext Max server...")
    uvicorn.run(app, host="127.0.0.1", port=8002)