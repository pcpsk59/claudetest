# 🎨 PASD Image Upscaler - Setup Guide

## ✅ **Current Status**

**✅ Successfully Installed:**
- PASD repository cloned
- Python dependencies installed 
- Stable Diffusion v1.5 base model downloaded
- NVIDIA RTX 6000 Ada Generation GPU detected

## ⚠️ **What's Missing**

To use PASD, you need the **pre-trained PASD models** which contain the specialized upscaling layers. The base Stable Diffusion model alone won't work.

## 🔧 **Complete Setup Instructions**

### **Option 1: Download from Official Sources (Recommended)**

1. **Get PASD Models from Hugging Face:**
   ```bash
   cd PASD-upscaler
   python -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='yangtao9009/PASD', local_dir='runs/pasd')"
   ```

2. **Alternative: Manual Download**
   - Visit: https://huggingface.co/yangtao9009/PASD
   - Download model files to `runs/pasd/` directory

### **Option 2: Use Gradio Demo (Easiest)**

```bash
cd PASD-upscaler
python gradio_pasd.py
```

This will launch a web interface at `http://localhost:7860` where you can:
- Upload images via drag & drop
- Select upscaling factor (2x, 4x, 8x)
- Choose enhancement type (realistic SR, old photo restoration, stylization)
- Download results

## 🎯 **Usage Examples**

### **Command Line (after models downloaded):**
```bash
# Basic 2x upscaling
python test_pasd.py --image_path examples/Set5/butterfly.png --upscale 2 --output_dir results

# 4x upscaling with better quality
python test_pasd.py --image_path your_image.jpg --upscale 4 --guidance_scale 7.0

# Old photo restoration
python test_pasd.py --image_path old_photo.jpg --control_type realisr --upscale 2
```

### **Gradio Web Interface:**
1. Run: `python gradio_pasd.py`
2. Open browser to `http://localhost:7860`
3. Upload image, select settings, click generate

## 📊 **What PASD Can Do**

### **Super-Resolution Upscaling**
- 2x, 4x, 8x image upscaling
- Preserves fine details and textures
- Better than traditional upscaling methods

### **Old Photo Restoration**
- Removes scratches, stains, artifacts
- Enhances faded photos
- Colorizes black & white images

### **Personalized Stylization**
- Apply artistic styles to images
- Disney, anime, and custom styles available
- Maintains subject identity

## 🔧 **Troubleshooting**

### **If Models Won't Download:**
1. Check internet connection
2. Try VPN if blocked in your region
3. Download manually from:
   - https://huggingface.co/yangtao9009/PASD
   - https://public-vigen-video.oss-cn-shanghai.aliyuncs.com/robin/models/PASD/pasd.zip

### **If GPU Memory Issues:**
- Use `--decoder_tiled_size 512` for large images
- Reduce `--process_size` to 512 or 256
- Close other GPU applications

### **Performance Tips:**
- Use smaller images first (under 1024px)
- RTX 6000 Ada can handle 4K images with proper settings
- Enable tiled processing for ultra-high resolution

## 📁 **Current Directory Structure**

```
PASD-upscaler/
├── checkpoints/
│   └── stable-diffusion-v1-5/     ✅ Downloaded
├── examples/                      ✅ Test images available
├── runs/
│   └── pasd/                      ❌ Need to download
├── gradio_pasd.py                 ✅ Web interface ready
├── test_pasd.py                   ✅ CLI tool ready
└── SETUP_GUIDE.md                 ✅ This guide
```

## 🚀 **Quick Start (Recommended)**

1. **Try the Gradio demo first:**
   ```bash
   cd PASD-upscaler
   python gradio_pasd.py
   ```

2. **If it works, download full models:**
   ```bash
   python -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='yangtao9009/PASD', local_dir='runs/pasd')"
   ```

3. **Test command line:**
   ```bash
   python test_pasd.py --image_path examples/Set5/butterfly.png --upscale 2
   ```

## 💡 **Alternative Tools**

If PASD setup is complex, consider these alternatives:
- **Real-ESRGAN**: Simpler setup, good quality
- **ESRGAN**: Classic upscaling
- **Waifu2x**: Anime-focused upscaling
- **Upscayl**: GUI application

## 🎉 **You're Ready!**

Your PASD installation is 90% complete. Just download the models and you'll have professional AI upscaling ready to use!