#!/usr/bin/env python3
"""
Simple Image Processor for Testing - Phase 1 MVP
This is a placeholder that simulates AI processing without heavy dependencies
"""
from PIL import Image, ImageFilter, ImageEnhance
import time
import random
from typing import Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleImageProcessor:
    """Simple image processor for testing the interface"""
    
    def __init__(self):
        self.device = "cpu"  # Simulated
        self.model_loaded = True
        logger.info("Simple processor initialized")
        
    def load_models(self, model_id: str = "test-model"):
        """Simulate model loading"""
        logger.info(f"Loading model: {model_id}")
        time.sleep(2)  # Simulate loading time
        self.model_loaded = True
        logger.info("Models loaded successfully")
        
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
        Simulate image processing with basic PIL operations
        This demonstrates the interface while we work on the real AI implementation
        """
        logger.info(f"Processing image: {input_image.size}, prompt: '{prompt[:50]}...'")
        
        # Simulate processing time
        processing_time = 2 + (num_inference_steps * 0.1)
        time.sleep(processing_time)
        
        # Simple image transformations based on prompt keywords
        result = input_image.copy()
        
        # Convert to RGB if needed
        if result.mode != "RGB":
            result = result.convert("RGB")
        
        # Apply transformations based on prompt content
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ["blur", "soft", "dreamy"]):
            result = result.filter(ImageFilter.GaussianBlur(radius=2))
            
        elif any(word in prompt_lower for word in ["sharp", "crisp", "detailed"]):
            result = result.filter(ImageFilter.UnsharpMask(radius=2, percent=150))
            
        elif any(word in prompt_lower for word in ["bright", "light", "sunny"]):
            enhancer = ImageEnhance.Brightness(result)
            result = enhancer.enhance(1.3)
            
        elif any(word in prompt_lower for word in ["dark", "moody", "dramatic"]):
            enhancer = ImageEnhance.Brightness(result)
            result = enhancer.enhance(0.7)
            
        elif any(word in prompt_lower for word in ["colorful", "vibrant", "saturated"]):
            enhancer = ImageEnhance.Color(result)
            result = enhancer.enhance(1.5)
            
        elif any(word in prompt_lower for word in ["vintage", "sepia", "old"]):
            # Convert to sepia
            grayscale = result.convert("L")
            sepia = Image.new("RGB", result.size)
            pixels = sepia.load()
            gray_pixels = grayscale.load()
            
            for y in range(result.height):
                for x in range(result.width):
                    gray = gray_pixels[x, y]
                    # Sepia tone
                    pixels[x, y] = (
                        min(255, int(gray * 1.2)),
                        min(255, int(gray * 1.0)),
                        min(255, int(gray * 0.8))
                    )
            result = sepia
            
        # Apply strength - blend with original
        if strength < 1.0:
            # Blend processed result with original based on strength
            from PIL import Image as PILImage
            result = PILImage.blend(input_image.convert("RGB"), result, strength)
        
        # Add some random variation to simulate different results
        if seed == -1:
            # Apply slight random adjustments
            if random.random() > 0.5:
                enhancer = ImageEnhance.Contrast(result)
                result = enhancer.enhance(1.0 + (random.random() - 0.5) * 0.2)
        
        logger.info(f"Processing completed. Output size: {result.size}")
        return result
    
    def health_check(self) -> Dict[str, Any]:
        """Check if the processor is working"""
        return {
            "status": "healthy",
            "device": self.device,
            "model_loaded": self.model_loaded,
            "processor_type": "simple_test_processor",
            "note": "This is a test processor. Install diffusers/torch for real AI processing."
        }

# Global processor instance
processor = SimpleImageProcessor()

def get_processor() -> SimpleImageProcessor:
    """Get the global processor instance"""
    return processor