#!/usr/bin/env python3
"""
Flux Kontext Max Image Processor using Black Forest Labs API
Implements dynamic prompting with master templates
"""
import os
import requests
import base64
import time
import random
from PIL import Image
from io import BytesIO
from typing import Dict, Any, List, Optional
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FluxProcessor:
    """Flux Kontext Max processor with Black Forest Labs API"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("BFL_API_KEY")
        self.base_url = "https://api.bfl.ml"
        self.create_endpoint = "https://api.bfl.ai/v1/flux-kontext-max"
        self.get_result_endpoint = "https://api.bfl.ai/v1/get_result"
        
        # Master prompt templates for themed generation
        self.master_templates = {
            "studio_lighting": {
                "name": "Professional Studio Lighting",
                "template": "{subject}, professional studio lighting setup, softbox lighting, key light and fill light, clean white background, commercial photography style, high-end fashion shoot aesthetic, dramatic shadows, perfect exposure, {style_modifiers}",
                "style_modifiers": [
                    "cinematic quality, 8k resolution",
                    "magazine cover style, pristine quality", 
                    "luxury brand aesthetic, flawless lighting",
                    "high-fashion photography, editorial style"
                ]
            },
            "natural_balcony": {
                "name": "Natural Balcony Setting",  
                "template": "{subject}, on a beautiful balcony overlooking the city, golden hour lighting, natural sunlight streaming through, urban backdrop, relaxed atmosphere, outdoor portrait session, {weather} day, {style_modifiers}",
                "weather": ["sunny", "partly cloudy", "warm evening", "bright morning"],
                "style_modifiers": [
                    "lifestyle photography, natural and candid",
                    "architectural beauty in background",
                    "warm natural tones, inviting atmosphere",
                    "urban elegance, contemporary setting"
                ]
            },
            "dramatic_mood": {
                "name": "Dramatic Mood Lighting",
                "template": "{subject}, dramatic mood lighting, chiaroscuro technique, strong contrast between light and shadow, {mood} atmosphere, cinematic composition, artistic portrait style, {style_modifiers}",
                "mood": ["mysterious", "intense", "contemplative", "powerful"],
                "style_modifiers": [
                    "film noir aesthetic, high contrast",
                    "artistic photography, gallery worthy", 
                    "emotional depth, storytelling through light",
                    "contemporary fine art portrait"
                ]
            },
            "lifestyle_casual": {
                "name": "Casual Lifestyle Setting",
                "template": "{subject}, casual lifestyle setting, {location}, natural candid moment, authentic expression, {time_of_day} lighting, relaxed and comfortable, lifestyle brand aesthetic, {style_modifiers}",
                "location": ["cozy coffee shop", "modern apartment", "trendy restaurant", "outdoor cafe"],
                "time_of_day": ["morning", "afternoon", "early evening"],
                "style_modifiers": [
                    "Instagram-worthy, social media ready",
                    "authentic lifestyle photography",
                    "warm and inviting atmosphere", 
                    "contemporary living, aspirational"
                ]
            }
        }
        
        logger.info(f"Flux processor initialized with {len(self.master_templates)} master templates")
        
    def generate_dynamic_prompt(self, 
                              subject: str, 
                              template_key: str, 
                              custom_elements: List[str] = None) -> str:
        """Generate dynamic prompt from master template"""
        
        if template_key not in self.master_templates:
            available = ", ".join(self.master_templates.keys())
            raise ValueError(f"Template '{template_key}' not found. Available: {available}")
        
        template_data = self.master_templates[template_key]
        template = template_data["template"]
        
        # Build replacements
        replacements = {"subject": subject}
        
        # Add random selections from template variables
        for key, options in template_data.items():
            if key not in ["name", "template"] and isinstance(options, list):
                replacements[key] = random.choice(options)
        
        # Add custom elements if provided
        if custom_elements:
            custom_string = ", ".join(custom_elements)
            if "style_modifiers" in replacements:
                replacements["style_modifiers"] = f"{replacements['style_modifiers']}, {custom_string}"
            else:
                replacements["style_modifiers"] = custom_string
        
        # Replace template variables
        final_prompt = template
        for key, value in replacements.items():
            final_prompt = final_prompt.replace(f"{{{key}}}", str(value))
        
        logger.info(f"Generated dynamic prompt using template '{template_key}'")
        return final_prompt
    
    def get_available_templates(self) -> Dict[str, str]:
        """Get list of available master templates"""
        return {key: data["name"] for key, data in self.master_templates.items()}
    
    async def process_image_to_image(self,
                                   input_image: Image.Image,
                                   subject: str,
                                   template_key: str,
                                   custom_elements: List[str] = None,
                                   strength: float = 0.8,
                                   seed: int = None) -> Image.Image:
        """Process image using Flux Kontext Max via Black Forest Labs API"""
        
        if not self.api_key:
            raise ValueError("Black Forest Labs API key is required")
        
        logger.info(f"Using API key: {self.api_key[:10]}...")
        
        try:
            # Generate dynamic prompt
            prompt = self.generate_dynamic_prompt(subject, template_key, custom_elements)
            logger.info(f"Processing with prompt: {prompt[:100]}...")
            
            # Convert PIL image to base64
            buffered = BytesIO()
            input_image.save(buffered, format="PNG")
            image_b64 = base64.b64encode(buffered.getvalue()).decode()
            
            # Prepare API request matching ComfyUI node parameters
            payload = {
                "prompt": prompt,
                "input_image": image_b64,
                "model": "flux-kontext-max",
                "aspect_ratio": "9:16",
                "seed": seed or random.randint(1, 2000000000),  # Match ComfyUI seed range
                "control_after_generate": "randomize",
                "output_format": "jpeg",
                "safety_tolerance": 2,
                "prompt_upsampling": False
            }
            
            headers = {
                "accept": "application/json",
                "x-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            # Submit request using correct BFL endpoint
            logger.info("Submitting request to Black Forest Labs API...")
            logger.info(f"URL: {self.create_endpoint}")
            logger.info(f"Headers: {headers}")
            logger.info(f"Payload keys: {list(payload.keys())}")
            
            response = requests.post(
                self.create_endpoint,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                error_msg = f"API request failed: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            result = response.json()
            
            # Handle async processing
            if "id" in result:
                # Wait for result using the polling URL from response
                task_id = result["id"]
                polling_url = result.get("polling_url")
                return await self._wait_for_result(task_id, polling_url)
            
            # Handle direct result
            elif "image" in result:
                image_data = base64.b64decode(result["image"])
                return Image.open(BytesIO(image_data))
            
            else:
                raise Exception(f"Unexpected API response format: {result}")
                
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            raise
    
    async def _wait_for_result(self, task_id: str, polling_url: str = None, max_wait: int = 300) -> Image.Image:
        """Wait for async processing result"""
        
        headers = {
            "accept": "application/json",
            "x-key": self.api_key
        }
        start_time = time.time()
        
        # Use polling URL if provided, otherwise construct from task_id
        if polling_url:
            check_url = polling_url
        else:
            check_url = f"{self.get_result_endpoint}?id={task_id}"
        
        while time.time() - start_time < max_wait:
            try:
                response = requests.get(
                    check_url,
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Full API response: {result}")
                    
                    status = result.get("status", "unknown")
                    
                    # Handle successful completion - could be "Task.Succeeded", "Ready", or "Completed"
                    if status in ["Task.Succeeded", "Ready", "Completed"] and "result" in result:
                        # BFL API returns image URLs, not base64 data
                        image_url = None
                        
                        if "result" in result and "sample" in result["result"]:
                            image_url = result["result"]["sample"]
                        elif "sample" in result:
                            image_url = result["sample"]
                        elif "result" in result and "output" in result["result"]:
                            image_url = result["result"]["output"]
                        elif "output" in result:
                            image_url = result["output"]
                        
                        if image_url and image_url.startswith("http"):
                            # Download image from URL
                            logger.info(f"Downloading image from: {image_url}")
                            img_response = requests.get(image_url, timeout=30)
                            if img_response.status_code == 200:
                                logger.info("Image generation completed successfully")
                                return Image.open(BytesIO(img_response.content))
                            else:
                                raise Exception(f"Failed to download image: {img_response.status_code}")
                        else:
                            logger.error(f"Could not find valid image URL in response: {result}")
                            raise Exception("Could not find valid image URL in API response")
                    
                    elif status == "Task.Failed":
                        raise Exception(f"Generation failed: {result.get('error', 'Unknown error')}")
                    
                    else:
                        # Still processing
                        logger.info(f"Status: {status}, waiting...")
                        time.sleep(5)
                        continue
                
                else:
                    logger.warning(f"Status check failed: {response.status_code}")
                    time.sleep(5)
                    
            except Exception as e:
                logger.warning(f"Status check error: {e}")
                time.sleep(5)
        
        raise Exception("Processing timeout - generation took too long")
    
    def generate_batch_variations(self,
                                input_image: Image.Image,
                                subject: str,
                                num_variations: int = 4) -> List[Dict[str, Any]]:
        """Generate multiple themed variations of the same image"""
        
        template_keys = list(self.master_templates.keys())
        selected_templates = random.sample(template_keys, min(num_variations, len(template_keys)))
        
        variations = []
        for template_key in selected_templates:
            template_name = self.master_templates[template_key]["name"]
            prompt = self.generate_dynamic_prompt(subject, template_key)
            
            variations.append({
                "template_key": template_key,
                "template_name": template_name,  
                "prompt": prompt,
                "image": input_image  # Will be processed separately
            })
        
        return variations
    
    def health_check(self) -> Dict[str, Any]:
        """Check API connectivity and status"""
        try:
            return {
                "status": "ready",
                "api_configured": bool(self.api_key),
                "endpoints": {
                    "create": self.create_endpoint,
                    "get_result": self.get_result_endpoint
                },
                "available_templates": list(self.master_templates.keys()),
                "model": "flux-kontext-max",
                "parameters": {
                    "aspect_ratio": "9:16",
                    "output_format": "jpeg",
                    "safety_tolerance": 2,
                    "control_after_generate": "randomize"
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "has_api_key": bool(self.api_key),
                "available_templates": list(self.master_templates.keys())
            }

# Global processor instance
processor = None

def get_processor(api_key: str = None) -> FluxProcessor:
    """Get the global Flux processor instance"""
    global processor
    if processor is None or (api_key and processor.api_key != api_key):
        processor = FluxProcessor(api_key)
    return processor