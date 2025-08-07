#!/usr/bin/env python3
"""
PASD Quick Test and Setup Verification
"""
import os
import sys
import torch
from PIL import Image

def check_system():
    """Check system requirements"""
    print("PASD System Check")
    print("=" * 40)
    
    # Python version
    print(f"[OK] Python: {sys.version.split()[0]}")
    
    # PyTorch
    print(f"[OK] PyTorch: {torch.__version__}")
    
    # GPU
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        print(f"[OK] GPU: {gpu_name}")
        print(f"[OK] CUDA Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    else:
        print("[FAIL] No CUDA GPU detected")
    
    print()

def check_models():
    """Check if required models exist"""
    print("Model Status")
    print("=" * 40)
    
    # Stable Diffusion base model
    sd_path = "checkpoints/stable-diffusion-v1-5"
    if os.path.exists(os.path.join(sd_path, "model_index.json")):
        print("[OK] Stable Diffusion v1.5: Downloaded")
    else:
        print("[FAIL] Stable Diffusion v1.5: Missing")
    
    # PASD models
    pasd_path = "runs/pasd"
    if os.path.exists(pasd_path) and len(os.listdir(pasd_path)) > 1:
        print("[OK] PASD Models: Available")
        return True
    else:
        print("[NEED] PASD Models: Not found")
        print("       Need to download from: https://huggingface.co/yangtao9009/PASD")
        return False
    
    print()

def test_basic_functionality():
    """Test if we can load basic components"""
    print("Basic Functionality Test")
    print("=" * 40)
    
    try:
        from diffusers import AutoencoderKL
        print("[OK] Diffusers library working")
        
        # Test loading a sample image
        sample_images = ["examples/Set5/butterfly.png", "examples/Set5/bird.png"]
        found_image = None
        
        for img_path in sample_images:
            if os.path.exists(img_path):
                found_image = img_path
                break
        
        if found_image:
            img = Image.open(found_image)
            print(f"[OK] Sample image loaded: {found_image} ({img.size})")
        else:
            print("[FAIL] No sample images found")
            
    except ImportError as e:
        print(f"[FAIL] Import error: {e}")
    
    print()

def show_next_steps():
    """Show user what to do next"""
    print("Next Steps")
    print("=" * 40)
    
    if not os.path.exists("runs/pasd") or len(os.listdir("runs/pasd")) <= 1:
        print("1. Download PASD models:")
        print("   python -c \"from huggingface_hub import snapshot_download; snapshot_download(repo_id='yangtao9009/PASD', local_dir='runs/pasd')\"")
        print()
        print("2. Or download manually from:")
        print("   https://huggingface.co/yangtao9009/PASD")
        print()
    
    print("3. Test upscaling with:")
    print("   python test_pasd.py --image_path examples/Set5/butterfly.png --upscale 2")
    print()
    
    print("4. For web interface (once models downloaded):")
    print("   python gradio_pasd.py")
    print("   Then open: http://localhost:7860")
    print()
    
    print("Read SETUP_GUIDE.md for detailed instructions")

def main():
    """Main test function"""
    print("PASD Image Upscaler - Quick Setup Test")
    print("=" * 50)
    print()
    
    check_system()
    models_ready = check_models()
    test_basic_functionality()
    show_next_steps()
    
    print("=" * 50)
    if models_ready:
        print("[SUCCESS] Setup complete! Ready to upscale images.")
    else:
        print("[ALMOST] Almost ready! Just download the PASD models.")
    print()

if __name__ == "__main__":
    main()