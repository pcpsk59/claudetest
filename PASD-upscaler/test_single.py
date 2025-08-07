#!/usr/bin/env python3
"""
Quick test script for PASD without xformers
"""
import os
import sys
import argparse

# Import the main function from test_pasd
sys.path.append('.')
from test_pasd import main

def test_pasd_single():
    """Test PASD with a single image, no xformers"""
    
    # Create test arguments
    args = argparse.Namespace(
        pretrained_model_path="checkpoints/stable-diffusion-v1-5",
        pasd_model_path="runs/pasd/pasd/checkpoint-100000",
        image_path="examples/Set5/butterfly.png",
        output_dir="test_output",
        upscale=2,
        mixed_precision="fp16",
        guidance_scale=7.0,
        conditioning_scale=1.0,
        num_inference_steps=20,
        process_size=512,
        control_type="realisr",
        high_level_info="classification",
        prompt="",
        added_prompt="",
        negative_prompt="",
        blending_alpha=0.8,
        multiplier=1.0,
        decoder_tiled_size=None,
        encoder_tiled_size=None,
        latent_tiled_size=None,
        latent_tiled_overlap=32,
        use_personalized_model=False,
        use_pasd_light=False,
        use_lcm_lora=False,
        use_blip=False,
        init_latent_with_noise=False,
        added_noise_level=0.0,
        offset_noise_scale=0.1,
        seed=None,
        personalized_model_path=None,
        lcm_lora_path=None
    )
    
    print("Testing PASD with single image (no xformers)...")
    print(f"Input: {args.image_path}")
    print(f"Output: {args.output_dir}")
    print(f"Scale: {args.upscale}x")
    
    try:
        # Run with xformers disabled
        main(args, enable_xformers_memory_efficient_attention=False)
        print("[SUCCESS] Test successful!")
        return True
    except Exception as e:
        print(f"[FAIL] Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_pasd_single()
    if success:
        print("PASD is working! Ready for batch processing.")
    else:
        print("Need to fix issues before batch processing.")