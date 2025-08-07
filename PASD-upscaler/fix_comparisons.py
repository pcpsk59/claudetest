#!/usr/bin/env python3
"""
Fixed Comparison Image Generator
Fixes the image matching issues in PASD batch processing results
"""
import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import shutil

class ComparisonFixer:
    def __init__(self):
        self.base_dir = Path(".")
        self.results_dir = self.base_dir / "PASD-results"
        
        # Known good images that processed correctly
        self.verified_images = {
            "butterfly": {"original": "examples/Set5/butterfly.png", "set": "Set5"},
            "bird": {"original": "examples/Set5/bird.png", "set": "Set5"},
            "baby": {"original": "examples/Set5/baby.png", "set": "Set5"},
            "head": {"original": "examples/Set5/head.png", "set": "Set5"},
        }
        
        # Images with processing issues (need to be excluded or reprocessed)
        self.problematic_images = ["LQ_sample", "woman", "barbara"]
    
    def validate_image_set(self, image_name, set_name):
        """Check if an image set has consistent processing results"""
        print(f"\n[CHECK] Validating {image_name} from {set_name}...")
        
        # Paths to check
        original_path = self.results_dir / "originals" / set_name / f"{image_name}.png"
        upscaled_2x = self.results_dir / "2x_upscaled" / set_name / f"{image_name}_2x.png"
        upscaled_4x = self.results_dir / "4x_upscaled" / set_name / f"{image_name}_4x.png"
        upscaled_8x = self.results_dir / "8x_upscaled" / set_name / f"{image_name}_8x.png"
        
        # Check if files exist
        files_exist = {
            "original": original_path.exists(),
            "2x": upscaled_2x.exists(),
            "4x": upscaled_4x.exists(), 
            "8x": upscaled_8x.exists()
        }
        
        print(f"Files exist: {files_exist}")
        
        # For known problematic images, mark as invalid
        if image_name in self.problematic_images:
            print(f"[SKIP] {image_name} marked as problematic - skipping")
            return False
            
        # Check if at least original and one upscaled version exist
        if files_exist["original"] and (files_exist["2x"] or files_exist["4x"] or files_exist["8x"]):
            print(f"[VALID] {image_name} has valid file set")
            return True
        else:
            print(f"[INVALID] {image_name} missing required files")
            return False
    
    def create_fixed_comparison(self, image_name, set_name):
        """Create a corrected comparison image for a specific image"""
        print(f"\n[CREATE] Creating fixed comparison for {image_name}...")
        
        # Load images that exist
        original_path = self.results_dir / "originals" / set_name / f"{image_name}.png"
        upscaled_paths = {
            "2x": self.results_dir / "2x_upscaled" / set_name / f"{image_name}_2x.png",
            "4x": self.results_dir / "4x_upscaled" / set_name / f"{image_name}_4x.png",
            "8x": self.results_dir / "8x_upscaled" / set_name / f"{image_name}_8x.png"
        }
        
        try:
            # Load original
            original = Image.open(original_path)
            images_to_show = [original]
            labels = [f"Original\\n{original.width}x{original.height}"]
            
            # Load upscaled versions that exist
            for scale, path in upscaled_paths.items():
                if path.exists():
                    try:
                        upscaled = Image.open(path)
                        images_to_show.append(upscaled)
                        labels.append(f"{scale.upper()} Upscaled\\n{upscaled.width}x{upscaled.height}")
                        print(f"[LOADED] Loaded {scale}: {upscaled.width}x{upscaled.height}")
                    except Exception as e:
                        print(f"[ERROR] Failed to load {scale}: {e}")
                        # Create placeholder
                        placeholder = Image.new('RGB', (100, 100), color=(200, 200, 200))
                        images_to_show.append(placeholder)
                        labels.append(f"{scale.upper()} Failed\\n100x100")
                else:
                    print(f"[MISSING] {scale} version not found")
                    # Create placeholder
                    placeholder = Image.new('RGB', (100, 100), color=(128, 128, 128))
                    images_to_show.append(placeholder)
                    labels.append(f"{scale.upper()} Missing\\n100x100")
            
            # Create comparison canvas
            max_height = max(img.height for img in images_to_show)
            total_width = sum(img.width for img in images_to_show) + (len(images_to_show) + 1) * 10
            
            comparison = Image.new('RGB', (total_width, max_height + 60), color='white')
            draw = ImageDraw.Draw(comparison)
            
            # Place images horizontally
            x_offset = 10
            for img, label in zip(images_to_show, labels):
                # Paste image
                y_offset = (max_height - img.height) // 2
                comparison.paste(img, (x_offset, y_offset))
                
                # Add label
                text_x = x_offset + (img.width // 2)
                text_y = max_height + 10
                
                # Split label into lines and center
                lines = label.split('\\n')
                for i, line in enumerate(lines):
                    line_y = text_y + (i * 15)
                    bbox = draw.textbbox((0, 0), line)
                    text_width = bbox[2] - bbox[0]
                    draw.text((text_x - text_width//2, line_y), line, fill='black')
                
                x_offset += img.width + 10
            
            # Save fixed comparison
            comp_dir = self.results_dir / "comparisons" / "grid_comparisons_fixed"
            comp_dir.mkdir(parents=True, exist_ok=True)
            comp_path = comp_dir / f"{image_name}_comparison_fixed.png"
            
            comparison.save(comp_path, quality=95)
            print(f"[SUCCESS] Created fixed comparison: {comp_path}")
            return str(comp_path)
            
        except Exception as e:
            print(f"[ERROR] Failed to create comparison for {image_name}: {e}")
            return None
    
    def remove_problematic_comparisons(self):
        """Remove the incorrect comparison images"""
        print("\n[CLEANUP] Removing problematic comparison images...")
        
        comp_dir = self.results_dir / "comparisons" / "grid_comparisons"
        
        for problem_img in self.problematic_images:
            comp_file = comp_dir / f"{problem_img}_comparison.png"
            if comp_file.exists():
                # Move to backup instead of delete
                backup_dir = comp_dir / "backup_problematic"
                backup_dir.mkdir(exist_ok=True)
                backup_path = backup_dir / f"{problem_img}_comparison_problematic.png"
                shutil.move(str(comp_file), str(backup_path))
                print(f"[MOVED] Moved problematic comparison to backup: {problem_img}")
            else:
                print(f"[NOT_FOUND] Comparison not found: {problem_img}")
    
    def generate_status_report(self):
        """Generate a status report of all processing results"""
        print("\n[REPORT] Generating status report...")
        
        # Scan all original images
        originals_dir = self.results_dir / "originals"
        all_images = []
        
        for set_dir in originals_dir.glob("*"):
            if set_dir.is_dir():
                set_name = set_dir.name
                for img_file in set_dir.glob("*.png"):
                    img_name = img_file.stem
                    all_images.append((img_name, set_name))
        
        report = []
        report.append("# PASD Processing Results Analysis")
        report.append("=" * 50)
        report.append(f"Total images found: {len(all_images)}")
        report.append("")
        
        valid_count = 0
        invalid_count = 0
        
        for img_name, set_name in all_images:
            is_valid = self.validate_image_set(img_name, set_name)
            status = "[VALID]" if is_valid else "[INVALID]"
            report.append(f"{status:<10} {set_name}/{img_name}")
            
            if is_valid:
                valid_count += 1
            else:
                invalid_count += 1
        
        report.append("")
        report.append(f"Valid: {valid_count}, Invalid: {invalid_count}")
        report.append(f"Success Rate: {valid_count/len(all_images)*100:.1f}%")
        
        # Save report
        report_path = self.results_dir / "processing_analysis.txt"
        with open(report_path, 'w') as f:
            f.write('\n'.join(report))
        
        print(f"[SAVED] Analysis report saved: {report_path}")
        return valid_count, invalid_count
    
    def run_fix(self):
        """Main fix process"""
        print("[FIX] Starting PASD Comparison Fix Process...")
        
        # Phase 1: Generate status report
        valid_count, invalid_count = self.generate_status_report()
        
        # Phase 2: Remove problematic comparisons
        self.remove_problematic_comparisons()
        
        # Phase 3: Create fixed comparisons for valid images
        print("\n[FIX] Creating fixed comparisons for valid images...")
        
        fixed_count = 0
        originals_dir = self.results_dir / "originals"
        
        for set_dir in originals_dir.glob("*"):
            if set_dir.is_dir():
                set_name = set_dir.name
                for img_file in set_dir.glob("*.png"):
                    img_name = img_file.stem
                    
                    # Only process valid images
                    if self.validate_image_set(img_name, set_name):
                        result = self.create_fixed_comparison(img_name, set_name)
                        if result:
                            fixed_count += 1
        
        # Phase 4: Summary
        print("\n" + "="*60)
        print("[SUCCESS] FIX PROCESS COMPLETE!")
        print("="*60)
        print(f"[STATS] Total images analyzed: {valid_count + invalid_count}")
        print(f"[VALID] Valid images: {valid_count}")
        print(f"[INVALID] Invalid images: {invalid_count}")
        print(f"[FIXED] Fixed comparisons created: {fixed_count}")
        print(f"[OUTPUT] Fixed comparisons saved in: comparisons/grid_comparisons_fixed/")
        print(f"[REPORT] Full analysis report: processing_analysis.txt")

def main():
    fixer = ComparisonFixer()
    fixer.run_fix()

if __name__ == "__main__":
    main()