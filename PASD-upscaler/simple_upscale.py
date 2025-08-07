#!/usr/bin/env python3
"""
Simple PASD upscaling script for batch processing
"""
import os
import sys
from pathlib import Path
from PIL import Image
import subprocess
import argparse

def upscale_single_image(input_path, output_dir, scale=2):
    """Upscale a single image using PASD"""
    
    print(f"Upscaling {input_path} -> {scale}x")
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # PASD command
    cmd = [
        "python", "test_pasd.py",
        "--image_path", str(input_path),
        "--output_dir", str(output_dir),
        "--upscale", str(scale),
        "--pretrained_model_path", "checkpoints/stable-diffusion-v1-5", 
        "--pasd_model_path", "runs/pasd/pasd/checkpoint-100000",
        "--guidance_scale", "7.0",
        "--num_inference_steps", "20"
    ]
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        # Set environment to disable xformers checking
        env = os.environ.copy()
        env["DISABLE_XFORMERS"] = "1"
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600, env=env)
        
        if result.returncode == 0:
            print(f"[SUCCESS] Success: {input_path.name}")
            # Find output file
            output_files = list(Path(output_dir).glob("*.png"))
            if output_files:
                return output_files[-1]  # Return the most recent file
        else:
            print(f"[ERROR] Error: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT] Timeout processing {input_path}")
    except Exception as e:
        print(f"[EXCEPTION] Exception: {e}")
    
    return None

def main():
    """Test with Set5 butterfly image"""
    input_image = Path("examples/Set5/butterfly.png")
    output_dir = Path("simple_test_output")
    
    if not input_image.exists():
        print(f"[ERROR] Input image not found: {input_image}")
        return
    
    print("Simple PASD Upscaling Test")
    print(f"Input: {input_image}")
    print(f"Output: {output_dir}")
    
    # Test 2x upscaling
    result = upscale_single_image(input_image, output_dir, scale=2)
    
    if result:
        print(f"Success! Generated: {result}")
        
        # Show file info
        if result.exists():
            img = Image.open(result)
            print(f"Output size: {img.size}")
            print(f"File size: {result.stat().st_size / 1024:.1f} KB")
    else:
        print("Failed to generate image")

if __name__ == "__main__":
    main()