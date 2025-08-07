# Phase 1 MVP - ComfyUI Image Processor

## 🎯 What This Does

Converts your ComfyUI workflow into a working web application with:
- ✅ **Simple web interface** for uploading images
- ✅ **FastAPI backend** with your AI processing logic
- ✅ **Real image-to-image processing** using Stable Diffusion
- ✅ **Parameter controls** (strength, quality, prompts)
- ✅ **Download processed results**

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd phase1-mvp/backend
pip install -r requirements.txt
```

### 2. Run the Server
```bash
python main.py
```

### 3. Open Your Browser
Visit: http://localhost:8000

## 🎨 How to Use

1. **Upload an image** - Click or drag & drop
2. **Enter a prompt** - Describe how to transform the image
3. **Adjust settings** - Strength and quality steps
4. **Click "Transform Image"** - Wait 30-60 seconds
5. **Download result** - Your processed image

## 🔧 Customization

### Your ComfyUI Workflow
The current implementation uses basic Stable Diffusion img2img. To use your specific workflow:

1. **Edit `ai_processor.py`**:
   - Change the model in `load_models()`
   - Modify `process_image()` with your workflow logic
   - Add any custom nodes or LoRA models

2. **Common Customizations**:
   ```python
   # Different base model
   model_id = "stabilityai/stable-diffusion-xl-base-1.0"
   
   # Add LoRA
   self.pipeline.load_lora_weights("path/to/your/lora")
   
   # Add ControlNet
   from diffusers import ControlNetModel, StableDiffusionControlNetImg2ImgPipeline
   controlnet = ControlNetModel.from_pretrained("lllyasviel/sd-controlnet-canny")
   ```

3. **Add Custom Parameters**:
   - Edit the frontend form in `main.py`
   - Add parameters to the `process_image()` function
   - Update the AI processing logic

### Frontend Modifications
The UI is embedded in `main.py` for simplicity. You can:
- Modify the HTML/CSS/JavaScript directly
- Add new parameter controls
- Change the styling and layout
- Add more advanced features

## 📊 Performance

### Expected Processing Times
- **Small images (512x512)**: 15-30 seconds
- **Large images (1024x1024)**: 30-60 seconds
- **First run**: +10-15 seconds (model loading)

### GPU vs CPU
- **With GPU**: Much faster processing
- **CPU only**: Works but slower (2-5 minutes per image)

### Memory Usage
- **GPU**: ~4-6GB VRAM required
- **CPU**: ~8-12GB RAM required

## 🐛 Troubleshooting

### Common Issues

**"CUDA out of memory"**
```python
# In ai_processor.py, add:
self.pipeline.enable_attention_slicing()
self.pipeline.enable_vae_slicing()
```

**"Model loading failed"**
- Check internet connection
- Ensure you have enough disk space (~4GB for models)
- Try a different model if Hugging Face is down

**"Processing too slow"**
- Reduce `num_inference_steps` to 10-15
- Use smaller input images
- Enable optimizations in the code

**"Server won't start"**
```bash
# Check if port 8000 is already in use
netstat -an | findstr :8000

# Use different port
python main.py --port 8001
```

## 📋 What's Working

- ✅ **Image upload and processing**
- ✅ **Basic Stable Diffusion img2img**
- ✅ **Parameter controls**
- ✅ **Download results**
- ✅ **Error handling**
- ✅ **Simple responsive UI**

## 🔄 Next Steps (Phase 2)

- [ ] **Modern React frontend**
- [ ] **Cloud deployment**
- [ ] **User accounts and history**
- [ ] **Batch processing**
- [ ] **Advanced parameters**
- [ ] **Multiple model support**

## 🎯 Testing

Try these test prompts:
- "make it look like an oil painting"
- "transform into anime style"
- "add dramatic lighting"
- "make it photorealistic"
- "convert to watercolor painting"

## 📝 Notes

This is a **Phase 1 MVP** - functional but basic. It proves the concept works and provides a foundation for the full production application in Phase 2.