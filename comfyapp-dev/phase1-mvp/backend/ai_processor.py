#!/usr/bin/env python3
"""
AI Processing Core - ComfyUI Workflow Implementation
Converts your ComfyUI workflow into pure Python code using Diffusers
"""
import os
import torch
from diffusers import StableDiffusionImg2ImgPipeline
from PIL import Image
import io
import base64
from typing import Optional, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageProcessor:
    """Core AI processing class - implements your ComfyUI workflow"""
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.pipeline = None
        self.model_loaded = False
        
        logger.info(f"Initializing ImageProcessor on {self.device}")
        
    def load_models(self, model_id: str = "runwayml/stable-diffusion-v1-5"):
        """Load AI models - customize based on your workflow"""
        try:
            logger.info(f"Loading model: {model_id}")
            
            # Basic Stable Diffusion pipeline - customize for your workflow
            self.pipeline = StableDiffusionImg2ImgPipeline.from_pretrained(
                model_id,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                safety_checker=None,
                requires_safety_checker=False
            )
            
            self.pipeline = self.pipeline.to(self.device)
            
            # Optimize for memory
            if self.device == "cuda":
                self.pipeline.enable_attention_slicing()
                self.pipeline.enable_vae_slicing()
            
            self.model_loaded = True
            logger.info("Models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise
    
    def process_image(
        self,
        input_image: Image.Image,
        prompt: str,
        negative_prompt: str = "",
        strength: float = 0.8,
        num_inference_steps: int = 20,
        guidance_scale: float = 7.5,
        seed: int = -1
    ) -> Image.Image:
        """
        Process image using your ComfyUI workflow logic
        
        Args:
            input_image: PIL Image to process
            prompt: Text description of desired output
            negative_prompt: What to avoid in the output
            strength: How much to modify (0.0 = no change, 1.0 = complete change)
            num_inference_steps: Quality vs speed (more = better quality)
            guidance_scale: How closely to follow prompt
            seed: Random seed for reproducible results (-1 = random)
        
        Returns:
            Processed PIL Image
        """
        
        if not self.model_loaded:
            self.load_models()
        
        try:
            # Set random seed if specified
            generator = None
            if seed != -1:
                generator = torch.Generator(device=self.device).manual_seed(seed)
            
            logger.info(f"Processing image: {input_image.size}, prompt: '{prompt[:50]}...'")
            
            # Ensure image is RGB and properly sized
            if input_image.mode != "RGB":
                input_image = input_image.convert("RGB")
            
            # Resize if too large (optional - adjust based on your needs)
            max_size = 768
            if max(input_image.size) > max_size:
                ratio = max_size / max(input_image.size)
                new_size = tuple(int(dim * ratio) for dim in input_image.size)
                input_image = input_image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Make dimensions multiple of 8 (required for diffusion models)
            width, height = input_image.size
            width = (width // 8) * 8
            height = (height // 8) * 8
            input_image = input_image.resize((width, height))
            
            # Run the pipeline - this is where your ComfyUI workflow logic goes
            result = self.pipeline(
                prompt=prompt,
                image=input_image,
                strength=strength,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                negative_prompt=negative_prompt,
                generator=generator
            )
            
            output_image = result.images[0]
            logger.info(f"Processing completed. Output size: {output_image.size}")
            
            return output_image
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """Check if the processor is working correctly"""
        try:
            status = {
                "status": "healthy",
                "device": self.device,
                "model_loaded": self.model_loaded,
                "cuda_available": torch.cuda.is_available()
            }
            
            if torch.cuda.is_available():
                status["gpu_memory"] = {
                    "allocated": torch.cuda.memory_allocated() / 1024**2,  # MB
                    "reserved": torch.cuda.memory_reserved() / 1024**2,    # MB
                }
            
            return status
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

# Global processor instance
processor = ImageProcessor()

def get_processor() -> ImageProcessor:
    """Get the global processor instance"""
    return processor