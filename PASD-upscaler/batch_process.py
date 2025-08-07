#!/usr/bin/env python3
"""
PASD Batch Image Processing Script
Processes images with 2x, 4x, 8x upscaling and creates comparisons
"""
import os
import sys
import time
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import subprocess
import glob

class PASDBatchProcessor:
    def __init__(self):
        self.scales = [2, 4, 8]
        self.base_dir = Path(".")
        self.results_dir = self.base_dir / "PASD-results"
        self.examples_dir = self.base_dir / "examples"
        
        # Processing stats
        self.stats = {
            "total_images": 0,
            "processed": 0,
            "failed": 0,
            "start_time": time.time()
        }
    
    def setup_directories(self):
        """Ensure all output directories exist"""
        print("Setting up directory structure...")
        
        # Main directories
        for scale in self.scales:
            scale_dir = self.results_dir / f"{scale}x_upscaled"
            for subdir in ["Set5", "Set14", "RealSRSet", "individual"]:
                (scale_dir / subdir).mkdir(parents=True, exist_ok=True)
        
        # Comparison directories
        comp_dir = self.results_dir / "comparisons"
        for comp_type in ["side_by_side_2x", "side_by_side_4x", "side_by_side_8x", "grid_comparisons"]:
            (comp_dir / comp_type).mkdir(parents=True, exist_ok=True)
        
        # Originals directory
        orig_dir = self.results_dir / "originals"
        for subdir in ["Set5", "Set14", "RealSRSet", "individual"]:
            (orig_dir / subdir).mkdir(parents=True, exist_ok=True)
        
        print(f"Directory structure created at: {self.results_dir}")
    
    def get_image_set_name(self, image_path):
        """Determine which set an image belongs to"""
        path_str = str(image_path)
        if "Set5" in path_str:
            return "Set5"
        elif "Set14" in path_str:
            return "Set14"
        elif "RealSRSet" in path_str:
            return "RealSRSet"
        else:
            return "individual"
    
    def backup_original(self, image_path):
        """Copy original image to results directory"""
        set_name = self.get_image_set_name(image_path)
        dest_dir = self.results_dir / "originals" / set_name
        dest_path = dest_dir / image_path.name
        
        if not dest_path.exists():
            shutil.copy2(image_path, dest_path)
            print(f"Backed up: {image_path.name}")
    
    def upscale_image(self, image_path, scale):
        """Upscale single image using PASD"""
        set_name = self.get_image_set_name(image_path)
        output_dir = self.results_dir / f"{scale}x_upscaled" / set_name
        output_path = output_dir / f"{image_path.stem}_{scale}x.png"
        
        if output_path.exists():
            print(f"Skipping {image_path.name} {scale}x (already exists)")
            return str(output_path)
        
        print(f"Processing {image_path.name} -> {scale}x upscale...")
        
        # PASD command with optimal settings (using correct model path)
        cmd = [
            "python", "test_single.py"
        ]
        
        # Modify the test_single.py arguments for this specific image and scale
        self.create_custom_test_script(image_path, output_dir, scale)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                # Find the generated file
                generated_files = list(output_dir.glob(f"*{image_path.stem}*"))
                if generated_files:
                    # Rename to standardized format
                    actual_output = generated_files[0]
                    if actual_output != output_path:
                        actual_output.rename(output_path)
                    
                    print(f"✅ Successfully upscaled {image_path.name} to {scale}x")
                    return str(output_path)
                else:
                    print(f"❌ No output file found for {image_path.name}")
                    return None
            else:
                print(f"❌ Error processing {image_path.name}: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print(f"❌ Timeout processing {image_path.name}")
            return None
        except Exception as e:
            print(f"❌ Exception processing {image_path.name}: {e}")
            return None
    
    def create_comparison_image(self, original_path, upscaled_paths):
        """Create horizontal comparison: Original | 2x | 4x | 8x"""
        try:
            # Load images
            original = Image.open(original_path)
            upscaled_images = []
            
            for path in upscaled_paths:
                if path and os.path.exists(path):
                    upscaled_images.append(Image.open(path))
                else:
                    # Create placeholder if upscaling failed
                    upscaled_images.append(Image.new('RGB', (64, 64), color='gray'))
            
            # Calculate dimensions for layout
            max_height = max([img.height for img in [original] + upscaled_images])
            total_width = sum([img.width for img in [original] + upscaled_images]) + 30  # 10px spacing between images
            
            # Create comparison canvas
            comparison = Image.new('RGB', (total_width, max_height + 50), color='white')
            
            # Paste images horizontally
            x_offset = 10
            images_info = [
                (original, f"Original\\n{original.width}x{original.height}"),
                (upscaled_images[0], f"2x Upscaled\\n{upscaled_images[0].width}x{upscaled_images[0].height}"),
                (upscaled_images[1], f"4x Upscaled\\n{upscaled_images[1].width}x{upscaled_images[1].height}"),
                (upscaled_images[2], f"8x Upscaled\\n{upscaled_images[2].width}x{upscaled_images[2].height}")
            ]
            
            for img, label in images_info:
                # Paste image
                y_offset = (max_height - img.height) // 2
                comparison.paste(img, (x_offset, y_offset))
                
                # Add label below image
                try:
                    draw = ImageDraw.Draw(comparison)
                    # Use default font
                    font_size = 14
                    draw.text((x_offset, max_height + 5), label, fill='black')
                except:
                    # Fallback if font loading fails
                    pass
                
                x_offset += img.width + 10
            
            # Save comparison
            set_name = self.get_image_set_name(original_path)
            comp_dir = self.results_dir / "comparisons" / "grid_comparisons"
            comp_path = comp_dir / f"{original_path.stem}_comparison.png"
            
            comparison.save(comp_path)
            print(f"✅ Created comparison: {comp_path.name}")
            return str(comp_path)
            
        except Exception as e:
            print(f"❌ Error creating comparison for {original_path.name}: {e}")
            return None
    
    def process_image_set(self, image_paths):
        """Process a set of images with all scales"""
        print(f"\\n🎨 Processing {len(image_paths)} images...")
        
        for i, image_path in enumerate(image_paths, 1):
            print(f"\\n--- Processing {i}/{len(image_paths)}: {image_path.name} ---")
            
            # Backup original
            self.backup_original(image_path)
            
            # Process all scales for this image
            upscaled_paths = []
            for scale in self.scales:
                upscaled_path = self.upscale_image(image_path, scale)
                upscaled_paths.append(upscaled_path)
                
                if upscaled_path:
                    self.stats["processed"] += 1
                else:
                    self.stats["failed"] += 1
            
            # Create comparison image
            self.create_comparison_image(image_path, upscaled_paths)
            
            # Progress update
            elapsed = time.time() - self.stats["start_time"]
            print(f"Progress: {i}/{len(image_paths)} images, {elapsed:.1f}s elapsed")
        
        self.stats["total_images"] = len(image_paths)
    
    def generate_report(self):
        """Generate HTML report with all results"""
        print("\\n📊 Generating processing report...")
        
        report_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>PASD Batch Processing Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #f0f0f0; padding: 20px; border-radius: 10px; }}
                .stats {{ display: flex; gap: 20px; margin: 20px 0; }}
                .stat {{ background: #e8f4fd; padding: 15px; border-radius: 5px; text-align: center; }}
                .images {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
                .image-card {{ border: 1px solid #ddd; padding: 10px; border-radius: 5px; }}
                img {{ max-width: 100%; height: auto; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎨 PASD Batch Processing Results</h1>
                <p>Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="stats">
                <div class="stat">
                    <h3>{self.stats['total_images']}</h3>
                    <p>Total Images</p>
                </div>
                <div class="stat">
                    <h3>{self.stats['processed']}</h3>
                    <p>Successfully Processed</p>
                </div>
                <div class="stat">
                    <h3>{self.stats['failed']}</h3>
                    <p>Failed</p>
                </div>
                <div class="stat">
                    <h3>{time.time() - self.stats['start_time']:.1f}s</h3>
                    <p>Total Time</p>
                </div>
            </div>
            
            <h2>📁 Directory Structure</h2>
            <pre>
PASD-results/
├── 2x_upscaled/     - All 2x upscaled images
├── 4x_upscaled/     - All 4x upscaled images  
├── 8x_upscaled/     - All 8x upscaled images
├── comparisons/     - Side-by-side comparisons
├── originals/       - Backup of original images
└── processing_report.html - This report
            </pre>
            
            <h2>🖼️ Sample Comparisons</h2>
            <p>Check the comparisons/grid_comparisons/ folder for all comparison images</p>
            
        </body>
        </html>
        """
        
        report_path = self.results_dir / "processing_report.html"
        with open(report_path, 'w') as f:
            f.write(report_html)
        
        print(f"📄 Report saved: {report_path}")
    
    def run(self, start_with_set5=True):
        """Main processing function"""
        print("🚀 PASD Batch Processor Starting...")
        
        # Setup
        self.setup_directories()
        
        if start_with_set5:
            # Start with Set5 as requested
            set5_images = list(self.examples_dir.glob("Set5/*.png"))
            if set5_images:
                print(f"\\n🎯 Starting with Set5: {len(set5_images)} images")
                self.process_image_set(set5_images)
            else:
                print("❌ No Set5 images found!")
                return
        
        # Generate report
        self.generate_report()
        
        print("\\n🎉 Processing Complete!")
        print(f"Results saved in: {self.results_dir}")
        print(f"Check processing_report.html for summary")

def main():
    processor = PASDBatchProcessor()
    processor.run(start_with_set5=True)

if __name__ == "__main__":
    main()