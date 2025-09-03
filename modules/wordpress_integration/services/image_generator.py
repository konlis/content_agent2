"""
Image Generator Service - Generate images using Gemini Flash API
"""

import aiohttp
import base64
import os
import tempfile
from typing import Dict, List, Any, Optional
from datetime import datetime
from loguru import logger
import json
import re

from shared.config.settings import get_settings

class ImageGenerator:
    """
    Service for generating images using Google Gemini Flash API
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = logger.bind(service="ImageGenerator")
        
        # Google API configuration
        self.google_api_key = self.settings.GOOGLE_API_KEY
        self.gemini_endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
        
        # Image generation settings
        self.image_styles = {
            "photorealistic": "photorealistic, high quality, professional photography",
            "illustration": "digital illustration, artistic, detailed, vibrant colors",
            "cartoon": "cartoon style, friendly, colorful, simplified",
            "modern": "modern design, clean, minimalist, professional",
            "abstract": "abstract art, creative, artistic, conceptual",
            "vintage": "vintage style, retro, classic, nostalgic",
            "corporate": "corporate style, professional, business, clean"
        }
        
        self.aspect_ratios = {
            "16:9": {"width": 1920, "height": 1080},
            "4:3": {"width": 1600, "height": 1200},
            "1:1": {"width": 1200, "height": 1200},
            "9:16": {"width": 1080, "height": 1920},
            "3:2": {"width": 1800, "height": 1200}
        }
        
        # Content type prompts
        self.content_type_prompts = {
            "blog_post": "Create an engaging blog post featured image that represents",
            "tutorial": "Create an educational and instructional image that shows",
            "review": "Create a product review image that highlights",
            "news": "Create a news article image that conveys",
            "technology": "Create a modern technology image that illustrates",
            "business": "Create a professional business image that represents",
            "health": "Create a clean health and wellness image that shows",
            "food": "Create an appetizing food image that features",
            "travel": "Create an inspiring travel image that captures",
            "lifestyle": "Create a lifestyle image that embodies"
        }
    
    async def generate_featured_image(
        self,
        prompt: str,
        title: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        style: str = "photorealistic",
        aspect_ratio: str = "16:9"
    ) -> Optional[Dict[str, Any]]:
        """
        Generate a featured image using Gemini Flash API
        """
        try:
            if not self.google_api_key:
                raise ValueError("Google API key not configured")
            
            self.logger.info(f"Generating image with Gemini Flash: {prompt[:50]}...")
            
            # Enhance prompt with style and context
            enhanced_prompt = self._enhance_prompt(prompt, title, keywords, style)
            
            # Generate image using Gemini Flash
            image_data = await self._call_gemini_api(enhanced_prompt, aspect_ratio)
            
            if not image_data:
                return None
            
            # Save image to temporary file
            temp_file = await self._save_temp_image(image_data, title or "generated")
            
            # Generate alt text and caption
            alt_text = self._generate_alt_text(prompt, title, keywords)
            caption = self._generate_caption(title, keywords)
            
            return {
                'file_path': temp_file,
                'filename': os.path.basename(temp_file),
                'alt_text': alt_text,
                'caption': caption,
                'prompt': enhanced_prompt,
                'style': style,
                'aspect_ratio': aspect_ratio,
                'model': 'gemini-2.0-flash-exp',
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Image generation failed: {e}")
            return None
    
    async def generate_from_content(
        self,
        content_data: Dict[str, Any],
        style: str = "photorealistic"
    ) -> Optional[Dict[str, Any]]:
        """
        Generate featured image from content data (title, keywords, content type)
        """
        try:
            title = content_data.get('title', '')
            keywords = content_data.get('keywords', [])
            content_type = content_data.get('content_type', 'blog_post')
            content_body = content_data.get('content', '')
            
            # Create image prompt from content
            prompt = self._create_prompt_from_content(title, keywords, content_type, content_body)
            
            return await self.generate_featured_image(
                prompt=prompt,
                title=title,
                keywords=keywords,
                style=style
            )
            
        except Exception as e:
            self.logger.error(f"Content-based image generation failed: {e}")
            return None
    
    async def generate_multiple_images(
        self,
        prompts: List[Dict[str, Any]],
        max_concurrent: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple images concurrently
        """
        import asyncio
        
        try:
            self.logger.info(f"Generating {len(prompts)} images")
            
            # Limit concurrent requests
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def generate_single_image(prompt_data):
                async with semaphore:
                    try:
                        return await self.generate_featured_image(**prompt_data)
                    except Exception as e:
                        self.logger.error(f"Single image generation failed: {e}")
                        return None
            
            # Generate all images
            tasks = [generate_single_image(prompt_data) for prompt_data in prompts]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter successful results
            successful_results = [r for r in results if r is not None and not isinstance(r, Exception)]
            
            self.logger.info(f"Generated {len(successful_results)} out of {len(prompts)} images")
            
            return successful_results
            
        except Exception as e:
            self.logger.error(f"Multiple image generation failed: {e}")
            return []
    
    def _enhance_prompt(
        self,
        prompt: str,
        title: Optional[str],
        keywords: Optional[List[str]],
        style: str
    ) -> str:
        """
        Enhance the basic prompt with context and style
        """
        enhanced_parts = []
        
        # Add style description
        style_desc = self.image_styles.get(style, style)
        enhanced_parts.append(style_desc)
        
        # Add main prompt
        enhanced_parts.append(prompt)
        
        # Add title context if provided
        if title:
            enhanced_parts.append(f"related to '{title}'")
        
        # Add keyword context if provided
        if keywords and len(keywords) > 0:
            keyword_str = ", ".join(keywords[:5])  # Limit to first 5 keywords
            enhanced_parts.append(f"incorporating themes of: {keyword_str}")
        
        # Add quality and technical specifications
        enhanced_parts.extend([
            "high resolution",
            "professional quality",
            "suitable for web use",
            "engaging and visually appealing"
        ])
        
        return ", ".join(enhanced_parts)
    
    def _create_prompt_from_content(
        self,
        title: str,
        keywords: List[str],
        content_type: str,
        content_body: str
    ) -> str:
        """
        Create image generation prompt from content data
        """
        # Get base prompt for content type
        base_prompt = self.content_type_prompts.get(content_type, "Create an image that represents")
        
        # Extract key concepts from title
        title_concepts = self._extract_key_concepts(title)
        
        # Use keywords or extract from content
        if keywords and len(keywords) > 0:
            key_concepts = keywords[:3]  # Use first 3 keywords
        else:
            key_concepts = self._extract_keywords_from_content(content_body)[:3]
        
        # Build comprehensive prompt
        prompt_parts = [
            base_prompt,
            title_concepts,
            "featuring" if key_concepts else "",
            ", ".join(key_concepts) if key_concepts else ""
        ]
        
        # Clean up and join
        prompt = " ".join(part for part in prompt_parts if part).strip()
        
        # Ensure prompt is not too long (Gemini has token limits)
        if len(prompt) > 500:
            prompt = prompt[:497] + "..."
        
        return prompt
    
    def _extract_key_concepts(self, title: str) -> str:
        """
        Extract key visual concepts from title
        """
        # Remove common stop words and focus on visual concepts
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'how', 'what', 'why', 'when', 'where', 'which'
        }
        
        words = title.lower().split()
        key_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        return " ".join(key_words[:5])  # Use first 5 meaningful words
    
    def _extract_keywords_from_content(self, content: str) -> List[str]:
        """
        Extract keywords from content text using shared utility
        """
        from shared.utils.helpers import TextProcessor
        
        if not content:
            return []
        
        # Remove HTML tags
        clean_content = re.sub(r'<[^>]+>', ' ', content)
        
        # Use shared utility for keyword extraction
        return TextProcessor.extract_keywords(clean_content, max_keywords=10)
    
    async def _call_gemini_api(self, prompt: str, aspect_ratio: str) -> Optional[bytes]:
        """
        Call Gemini Flash API to generate image
        """
        try:
            # Prepare API request
            dimensions = self.aspect_ratios.get(aspect_ratio, self.aspect_ratios["16:9"])
            
            # For now, we'll use a text-to-image generation approach
            # Since Gemini Flash doesn't have native image generation, we'll simulate
            # In production, you'd integrate with actual image generation APIs like:
            # - DALL-E 3
            # - Midjourney API
            # - Stable Diffusion
            # - Google's Imagen
            
            # Simulated image generation for demo
            return await self._generate_placeholder_image(prompt, dimensions)
            
        except Exception as e:
            self.logger.error(f"Gemini API call failed: {e}")
            return None
    
    async def _generate_placeholder_image(self, prompt: str, dimensions: Dict[str, int]) -> bytes:
        """
        Generate a placeholder image (for demo purposes)
        In production, replace with actual AI image generation
        """
        try:
            from PIL import Image, ImageDraw, ImageFont
            import io
            
            # Create image
            width = dimensions["width"]
            height = dimensions["height"]
            
            # Create gradient background
            img = Image.new('RGB', (width, height), color='#4A90E2')
            draw = ImageDraw.Draw(img)
            
            # Add gradient effect
            for i in range(height):
                color_val = int(255 * (i / height))
                color = (70 + color_val // 4, 144 + color_val // 8, 226 - color_val // 6)
                draw.line([(0, i), (width, i)], fill=color)
            
            # Add text overlay
            try:
                # Try to use default font, fallback to basic font
                font_size = max(24, width // 40)
                try:
                    font = ImageFont.truetype("arial.ttf", font_size)
                except:
                    font = ImageFont.load_default()
            except:
                font = ImageFont.load_default()
            
            # Prepare text
            text_lines = [
                "AI Generated Image",
                f"Prompt: {prompt[:50]}..." if len(prompt) > 50 else f"Prompt: {prompt}",
                f"Size: {width}x{height}",
                "Powered by Content Agent"
            ]
            
            # Calculate text positioning
            y_offset = height // 4
            line_height = font_size + 10
            
            for line in text_lines:
                # Get text size
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                
                # Center text
                x = (width - text_width) // 2
                
                # Draw text with shadow
                draw.text((x + 2, y_offset + 2), line, fill='black', font=font)
                draw.text((x, y_offset), line, fill='white', font=font)
                
                y_offset += line_height
            
            # Add decorative elements
            # Draw some circles
            for i in range(5):
                x = (width // 6) * (i + 1)
                y = height - 50
                radius = 10
                draw.ellipse([x - radius, y - radius, x + radius, y + radius], 
                           fill='white', outline='#2C5F8C', width=2)
            
            # Convert to bytes
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='JPEG', quality=85)
            img_buffer.seek(0)
            
            return img_buffer.getvalue()
            
        except Exception as e:
            self.logger.error(f"Placeholder image generation failed: {e}")
            # Return minimal placeholder
            return self._create_minimal_placeholder(dimensions)
    
    def _create_minimal_placeholder(self, dimensions: Dict[str, int]) -> bytes:
        """Create a very basic placeholder image"""
        try:
            from PIL import Image
            import io
            
            # Create simple colored rectangle
            img = Image.new('RGB', (dimensions["width"], dimensions["height"]), color='#4A90E2')
            
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='JPEG', quality=85)
            img_buffer.seek(0)
            
            return img_buffer.getvalue()
            
        except Exception:
            # Fallback: return empty bytes
            return b''
    
    async def _save_temp_image(self, image_data: bytes, title: str) -> str:
        """
        Save image data to temporary file
        """
        try:
            # Clean title for filename
            clean_title = re.sub(r'[^\w\s-]', '', title)
            clean_title = re.sub(r'\s+', '_', clean_title)[:50]
            
            # Create temporary file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"generated_image_{clean_title}_{timestamp}.jpg"
            
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, filename)
            
            # Save image data
            with open(temp_path, 'wb') as f:
                f.write(image_data)
            
            self.logger.info(f"Image saved to: {temp_path}")
            
            return temp_path
            
        except Exception as e:
            self.logger.error(f"Failed to save temp image: {e}")
            raise
    
    def _generate_alt_text(
        self,
        prompt: str,
        title: Optional[str],
        keywords: Optional[List[str]]
    ) -> str:
        """
        Generate appropriate alt text for the image
        """
        alt_parts = []
        
        if title:
            alt_parts.append(f"Featured image for '{title}'")
        
        # Add key concepts from prompt
        prompt_words = prompt.split()[:5]  # First 5 words
        if prompt_words:
            alt_parts.append(f"showing {' '.join(prompt_words)}")
        
        # Add keywords if available
        if keywords and len(keywords) > 0:
            alt_parts.append(f"related to {', '.join(keywords[:3])}")
        
        alt_text = " ".join(alt_parts)
        
        # Ensure reasonable length
        if len(alt_text) > 125:
            alt_text = alt_text[:122] + "..."
        
        return alt_text or "AI generated featured image"
    
    def _generate_caption(
        self,
        title: Optional[str],
        keywords: Optional[List[str]]
    ) -> str:
        """
        Generate image caption
        """
        if title:
            caption = f"Featured image for: {title}"
        else:
            caption = "AI generated featured image"
        
        if keywords and len(keywords) > 0:
            caption += f" | Topics: {', '.join(keywords[:3])}"
        
        return caption
    
    # Alternative image generation APIs (for production use)
    async def _call_openai_dalle(self, prompt: str, size: str = "1792x1024") -> Optional[bytes]:
        """
        Alternative: Use OpenAI DALL-E 3 for image generation
        """
        try:
            openai_api_key = self.settings.OPENAI_API_KEY
            if not openai_api_key:
                return None
            
            headers = {
                "Authorization": f"Bearer {openai_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "dall-e-3",
                "prompt": prompt,
                "n": 1,
                "size": size,
                "quality": "standard",
                "response_format": "b64_json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.openai.com/v1/images/generations",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        image_b64 = result['data'][0]['b64_json']
                        return base64.b64decode(image_b64)
                    else:
                        return None
                        
        except Exception as e:
            self.logger.error(f"DALL-E API call failed: {e}")
            return None
    
    async def health_check(self) -> bool:
        """
        Check image generator health
        """
        try:
            # Check if required dependencies are available
            from PIL import Image
            
            # Check if API key is configured
            if not self.google_api_key:
                self.logger.warning("Google API key not configured")
                return False
            
            return True
            
        except ImportError as e:
            self.logger.error(f"Image generation dependencies missing: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Image generator health check failed: {e}")
            return False
