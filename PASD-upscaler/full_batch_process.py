#!/usr/bin/env python3
"""
PASD Full Batch Processing Script
Processes all images with 2x, 4x, 8x upscaling and creates comparisons
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
            "start_time": time.time(),
            "processing_times": []
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
        output_name = f"{image_path.stem}_{scale}x.png"
        output_path = output_dir / output_name
        
        if output_path.exists():
            print(f"Skipping {image_path.name} {scale}x (already exists)")
            return str(output_path)
        
        print(f"Processing {image_path.name} -> {scale}x upscale...")
        start_time = time.time()
        
        # PASD command
        cmd = [
            "python", "test_pasd.py",
            "--image_path", str(image_path),
            "--output_dir", str(output_dir),
            "--upscale", str(scale),
            "--pretrained_model_path", "checkpoints/stable-diffusion-v1-5",
            "--pasd_model_path", "runs/pasd/pasd/checkpoint-100000",
            "--guidance_scale", "7.0",
            "--num_inference_steps", "20"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                # Find the generated file and rename it
                output_files = list(output_dir.glob("*.png"))
                if output_files:
                    # Find the most recently created file
                    latest_file = max(output_files, key=lambda p: p.stat().st_mtime)
                    if latest_file != output_path:
                        latest_file.rename(output_path)
                    
                    processing_time = time.time() - start_time
                    self.stats["processing_times"].append(processing_time)
                    
                    print(f"[SUCCESS] {image_path.name} -> {scale}x ({processing_time:.1f}s)")
                    return str(output_path)
                else:
                    print(f"[ERROR] No output file found for {image_path.name}")
                    return None
            else:
                print(f"[ERROR] Processing failed: {result.stderr[:200]}...")
                return None
                
        except subprocess.TimeoutExpired:
            print(f"[TIMEOUT] Processing {image_path.name} took too long")
            return None
        except Exception as e:
            print(f"[EXCEPTION] Error processing {image_path.name}: {e}")
            return None
    
    def create_comparison_image(self, original_path, upscaled_paths):
        """Create horizontal comparison: Original | 2x | 4x | 8x"""
        try:
            print(f"Creating comparison for {original_path.name}...")
            
            # Load images
            original = Image.open(original_path)
            upscaled_images = []
            
            for path in upscaled_paths:
                if path and os.path.exists(path):
                    upscaled_images.append(Image.open(path))
                else:
                    # Create placeholder if upscaling failed
                    placeholder = Image.new('RGB', (original.width, original.height), color=(128, 128, 128))
                    upscaled_images.append(placeholder)
            
            # Calculate dimensions for layout
            max_height = max([img.height for img in [original] + upscaled_images])
            total_width = sum([img.width for img in [original] + upscaled_images]) + 40  # 10px spacing between images
            
            # Create comparison canvas with space for labels
            comparison = Image.new('RGB', (total_width, max_height + 60), color='white')
            draw = ImageDraw.Draw(comparison)
            
            # Paste images horizontally with labels
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
                    # Calculate text position (center it under the image)
                    text_x = x_offset + (img.width // 2)
                    text_y = max_height + 10
                    
                    # Draw text (split label into lines)
                    lines = label.split('\\n')
                    for i, line in enumerate(lines):
                        line_y = text_y + (i * 15)
                        # Get text size for centering
                        bbox = draw.textbbox((0, 0), line)
                        text_width = bbox[2] - bbox[0]
                        draw.text((text_x - text_width//2, line_y), line, fill='black')
                        
                except Exception as e:
                    print(f"Warning: Could not add text labels: {e}")
                
                x_offset += img.width + 10
            
            # Save comparison
            comp_dir = self.results_dir / "comparisons" / "grid_comparisons"
            comp_path = comp_dir / f"{original_path.stem}_comparison.png"
            
            comparison.save(comp_path, quality=95)
            print(f"[SUCCESS] Created comparison: {comp_path.name}")
            return str(comp_path)
            
        except Exception as e:
            print(f"[ERROR] Failed to create comparison for {original_path.name}: {e}")
            return None
    
    def process_image_set(self, image_paths, set_name):
        """Process a set of images with all scales"""
        print(f"\\n=== Processing {set_name}: {len(image_paths)} images ===")
        
        for i, image_path in enumerate(image_paths, 1):
            print(f"\\n--- {set_name} {i}/{len(image_paths)}: {image_path.name} ---")
            
            # Backup original
            self.backup_original(image_path)
            
            # Process all scales for this image
            upscaled_paths = []
            success_count = 0
            
            for scale in self.scales:
                upscaled_path = self.upscale_image(image_path, scale)
                upscaled_paths.append(upscaled_path)
                
                if upscaled_path:
                    success_count += 1
                    self.stats["processed"] += 1
                else:
                    self.stats["failed"] += 1
            
            # Create comparison image
            if success_count > 0:
                self.create_comparison_image(image_path, upscaled_paths)
            
            # Progress update
            elapsed = time.time() - self.stats["start_time"]
            avg_time = sum(self.stats["processing_times"]) / len(self.stats["processing_times"]) if self.stats["processing_times"] else 0
            print(f"Progress: {i}/{len(image_paths)} in {set_name}, {elapsed/60:.1f}min elapsed, avg {avg_time:.1f}s per image")
    
    def get_all_images(self):
        """Get all images organized by set"""
        image_sets = {
            "Set5": list(self.examples_dir.glob("Set5/*.png")),
            "Set14": list(self.examples_dir.glob("Set14/*.png")),
            "RealSRSet": list(self.examples_dir.glob("RealSRSet/*.png")),
            "individual": list(self.examples_dir.glob("*.png"))
        }
        
        # Remove empty sets
        image_sets = {k: v for k, v in image_sets.items() if v}
        
        total = sum(len(v) for v in image_sets.values())
        print(f"Found {total} images across {len(image_sets)} sets")
        
        return image_sets
    
    def generate_report(self):
        """Generate HTML report with all results"""
        print("\\nGenerating processing report...")
        
        # Calculate statistics
        total_time = time.time() - self.stats["start_time"]
        avg_processing_time = sum(self.stats["processing_times"]) / len(self.stats["processing_times"]) if self.stats["processing_times"] else 0
        success_rate = (self.stats["processed"] / (self.stats["processed"] + self.stats["failed"]) * 100) if (self.stats["processed"] + self.stats["failed"]) > 0 else 0
        
        # Find comparison images
        comp_dir = self.results_dir / "comparisons" / "grid_comparisons"
        comparison_images = list(comp_dir.glob("*.png")) if comp_dir.exists() else []
        
        report_html = f'''<!DOCTYPE html>
<html>
<head>
    <title>PASD Batch Processing Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 30px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }}
        .stat {{ background: #e8f4fd; padding: 20px; border-radius: 10px; text-align: center; }}
        .stat h3 {{ font-size: 2rem; margin: 0; color: #2c5aa0; }}
        .stat p {{ margin: 10px 0 0 0; color: #666; }}
        .directory-tree {{ background: #f8f9fa; padding: 20px; border-radius: 10px; font-family: monospace; white-space: pre-line; }}
        .gallery {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 30px 0; }}
        .gallery-item {{ border: 1px solid #ddd; border-radius: 10px; overflow: hidden; }}
        .gallery-item img {{ width: 100%; height: auto; }}
        .gallery-item .caption {{ padding: 15px; background: #f8f9fa; }}
        h2 {{ color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>PASD Batch Processing Results</h1>
            <p>Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Total Processing Time: {total_time/60:.1f} minutes</p>
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
                <h3>{success_rate:.1f}%</h3>
                <p>Success Rate</p>
            </div>
            <div class="stat">
                <h3>{avg_processing_time:.1f}s</h3>
                <p>Avg Time/Image</p>
            </div>
            <div class="stat">
                <h3>{len(comparison_images)}</h3>
                <p>Comparisons Created</p>
            </div>
        </div>
        
        <h2>Directory Structure</h2>
        <div class="directory-tree">PASD-results/
├── 2x_upscaled/     - All 2x upscaled images organized by set
├── 4x_upscaled/     - All 4x upscaled images organized by set
├── 8x_upscaled/     - All 8x upscaled images organized by set
├── comparisons/     - Side-by-side comparison images
│   └── grid_comparisons/  - Original | 2x | 4x | 8x comparisons
├── originals/       - Backup of all original images
└── processing_report.html - This report</div>
        
        <h2>Processing Summary</h2>
        <p>Successfully processed <strong>{self.stats['processed']}</strong> image upscales across multiple resolutions.</p>
        <p>Each original image was processed at 2x, 4x, and 8x scales using PASD (Pixel-Aware Stable Diffusion).</p>
        <p>Comparison images show: <strong>Original | 2x Upscaled | 4x Upscaled | 8x Upscaled</strong> with dimensions labeled.</p>
        
        <h2>Sample Comparisons</h2>
        <p>Check the <code>comparisons/grid_comparisons/</code> folder for all comparison images.</p>
        <p><strong>Files generated:</strong></p>
        <ul>
            <li><strong>{len(self.stats['processing_times'])} upscaled images</strong> across 3 different scales</li>
            <li><strong>{len(comparison_images)} comparison grids</strong> for easy quality assessment</li>
            <li><strong>Organized directory structure</strong> for easy access</li>
        </ul>
        
        <div style="margin-top: 50px; text-align: center; color: #666;">
            <p>Generated with PASD (Pixel-Aware Stable Diffusion)</p>
            <p>Processing completed in {total_time/60:.1f} minutes</p>
        </div>
    </div>
</body>
</html>'''
        
        report_path = self.results_dir / "processing_report.html"
        with open(report_path, 'w') as f:
            f.write(report_html)
        
        print(f"[SUCCESS] Report saved: {report_path}")
    
    def run(self):
        """Main processing function"""
        print("PASD Full Batch Processor Starting...")
        print("Will process ALL images with 2x, 4x, 8x upscaling")
        
        # Setup
        self.setup_directories()
        
        # Get all images
        image_sets = self.get_all_images()
        self.stats["total_images"] = sum(len(images) for images in image_sets.values())
        
        if self.stats["total_images"] == 0:
            print("No images found to process!")
            return
        
        print(f"\\nStarting to process {self.stats['total_images']} images...")
        print(f"Expected outputs: {self.stats['total_images'] * 3} upscaled images + comparisons")
        
        # Process each set
        for set_name, images in image_sets.items():
            if images:
                self.process_image_set(images, set_name)
        
        # Generate final report
        self.generate_report()
        
        # Final summary
        total_time = time.time() - self.stats["start_time"]
        print("\\n" + "="*60)
        print("PROCESSING COMPLETE!")
        print("="*60)
        print(f"Total images processed: {self.stats['total_images']}")
        print(f"Successful upscales: {self.stats['processed']}")
        print(f"Failed upscales: {self.stats['failed']}")
        print(f"Total processing time: {total_time/60:.1f} minutes")
        print(f"Results saved in: {self.results_dir}")
        print("Check processing_report.html for detailed results")
        print("="*60)

def main():
    processor = PASDBatchProcessor()
    processor.run()

if __name__ == "__main__":
    main()