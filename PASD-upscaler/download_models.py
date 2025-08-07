#!/usr/bin/env python3
"""
Download required models for PASD Image Upscaling
"""
import os
from huggingface_hub import snapshot_download
import requests
from tqdm import tqdm

def download_file(url, filename):
    """Download file with progress bar"""
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    total_size = int(response.headers.get('content-length', 0))
    
    with open(filename, 'wb') as file, tqdm(
        desc=filename,
        total=total_size,
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
    ) as pbar:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)
                pbar.update(len(chunk))

def main():
    print("🚀 Downloading PASD models...")
    
    # Create directories
    os.makedirs("checkpoints/stable-diffusion-v1-5", exist_ok=True)
    os.makedirs("runs/pasd", exist_ok=True)
    
    try:
        # 1. Download Stable Diffusion 1.5 base model
        print("\n📥 Downloading Stable Diffusion v1.5...")
        snapshot_download(
            repo_id="runwayml/stable-diffusion-v1-5",
            local_dir="checkpoints/stable-diffusion-v1-5",
            ignore_patterns=["*.bin"]  # Download safetensors instead
        )
        print("✅ Stable Diffusion v1.5 downloaded!")
        
        # 2. Download PASD specific models from alternative sources
        print("\n📥 Downloading PASD models...")
        pasd_models = [
            ("https://public-vigen-video.oss-cn-shanghai.aliyuncs.com/robin/models/PASD/pasd.zip", "pasd.zip")
        ]
        
        for url, filename in pasd_models:
            filepath = os.path.join("runs/pasd", filename)
            if not os.path.exists(filepath):
                print(f"Downloading {filename}...")
                try:
                    download_file(url, filepath)
                    
                    # Extract if it's a zip file
                    if filename.endswith('.zip'):
                        import zipfile
                        with zipfile.ZipFile(filepath, 'r') as zip_ref:
                            zip_ref.extractall("runs/pasd/")
                        os.remove(filepath)  # Remove zip after extraction
                        print(f"✅ {filename} downloaded and extracted!")
                    else:
                        print(f"✅ {filename} downloaded!")
                        
                except Exception as e:
                    print(f"❌ Failed to download {filename}: {e}")
                    print("You may need to download this manually.")
            else:
                print(f"✅ {filename} already exists!")
        
        print("\n🎉 Model download completed!")
        print("\nYou can now test PASD with:")
        print("python test_pasd.py --image_path examples/Set5/butterfly.png --output_dir output_test --upscale 2")
        
    except Exception as e:
        print(f"❌ Error downloading models: {e}")
        print("\n🔧 Manual setup instructions:")
        print("1. Go to https://huggingface.co/runwayml/stable-diffusion-v1-5")
        print("2. Download and place in checkpoints/stable-diffusion-v1-5/")
        print("3. Download PASD models from the paper's resources")

if __name__ == "__main__":
    main()