"""
Media Manager Service - WordPress media library management
"""

import aiohttp
import base64
import mimetypes
import os
from typing import Dict, List, Any, Optional, Union, BinaryIO
from datetime import datetime
from loguru import logger
import aiofiles
from PIL import Image
import io

from shared.config.settings import get_settings

class MediaManager:
    """
    Service for managing WordPress media library uploads and optimization
    """
    
    def __init__(self, container):
        self.container = container
        self.settings = get_settings()
        self.logger = logger.bind(service="MediaManager")
        
        # WordPress configuration
        self.wordpress_url = self.settings.WORDPRESS_URL
        self.username = self.settings.WORDPRESS_USERNAME
        self.app_password = self.settings.WORDPRESS_APP_PASSWORD
        
        # API endpoints
        self.api_base = f"{self.wordpress_url.rstrip('/')}/wp-json/wp/v2"
        
        # Authentication
        if self.username and self.app_password:
            credentials = f"{self.username}:{self.app_password}"
            credentials_b64 = base64.b64encode(credentials.encode()).decode()
            self.auth_header = f"Basic {credentials_b64}"
        else:
            self.auth_header = None
        
        # Media settings
        self.supported_image_types = {
            'image/jpeg': ['.jpg', '.jpeg'],
            'image/png': ['.png'],
            'image/gif': ['.gif'],
            'image/webp': ['.webp'],
            'image/bmp': ['.bmp']
        }
        
        self.supported_video_types = {
            'video/mp4': ['.mp4'],
            'video/mpeg': ['.mpeg', '.mpg'],
            'video/quicktime': ['.mov'],
            'video/avi': ['.avi'],
            'video/webm': ['.webm']
        }
        
        self.supported_audio_types = {
            'audio/mpeg': ['.mp3'],
            'audio/wav': ['.wav'],
            'audio/ogg': ['.ogg'],
            'audio/mp4': ['.m4a']
        }
        
        self.supported_document_types = {
            'application/pdf': ['.pdf'],
            'application/msword': ['.doc'],
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
            'application/vnd.ms-excel': ['.xls'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx']
        }
        
        # Image optimization settings
        self.image_optimization = {
            'max_width': 1920,
            'max_height': 1080,
            'quality': 85,
            'format_conversion': {
                'bmp': 'jpeg',  # Convert BMP to JPEG
                'large_png': 'jpeg'  # Convert large PNG to JPEG
            }
        }
    
    async def upload_media(
        self,
        file_path: str,
        filename: Optional[str] = None,
        alt_text: str = "",
        caption: str = "",
        description: str = ""
    ) -> Dict[str, Any]:
        """
        Upload media file to WordPress media library
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Use provided filename or extract from path
            if not filename:
                filename = os.path.basename(file_path)
            
            self.logger.info(f"Uploading media to WordPress: {filename}")
            
            # Read file
            async with aiofiles.open(file_path, 'rb') as file:
                file_content = await file.read()
            
            # Optimize if it's an image
            if self._is_image_file(filename):
                file_content = await self._optimize_image(file_content, filename)
            
            # Prepare headers
            headers = {
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Type': self._get_mime_type(filename)
            }
            
            if self.auth_header:
                headers['Authorization'] = self.auth_header
            
            # Upload to WordPress
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/media",
                    data=file_content,
                    headers=headers
                ) as response:
                    if response.status == 201:
                        result = await response.json()
                        
                        # Update media metadata if provided
                        if alt_text or caption or description:
                            await self._update_media_metadata(
                                result['id'],
                                alt_text,
                                caption,
                                description
                            )
                        
                        self.logger.info(f"Media uploaded successfully: {result['id']}")
                        
                        return self._format_media_response(result)
                    else:
                        error_text = await response.text()
                        raise Exception(f"Media upload failed: HTTP {response.status} - {error_text}")
                        
        except Exception as e:
            self.logger.error(f"Media upload failed: {e}")
            raise
    
    async def upload_from_url(
        self,
        url: str,
        filename: Optional[str] = None,
        alt_text: str = "",
        caption: str = "",
        description: str = ""
    ) -> Dict[str, Any]:
        """
        Download media from URL and upload to WordPress
        """
        try:
            self.logger.info(f"Downloading and uploading media from URL: {url}")
            
            # Download file from URL
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        file_content = await response.read()
                        
                        # Get filename from URL or use provided one
                        if not filename:
                            filename = os.path.basename(url.split('?')[0])
                            if not filename or '.' not in filename:
                                # Generate filename based on content type
                                content_type = response.headers.get('content-type', 'application/octet-stream')
                                extension = mimetypes.guess_extension(content_type) or '.bin'
                                filename = f"media_{datetime.now().strftime('%Y%m%d_%H%M%S')}{extension}"
                        
                        # Optimize if it's an image
                        if self._is_image_file(filename):
                            file_content = await self._optimize_image(file_content, filename)
                        
                        # Upload to WordPress
                        headers = {
                            'Content-Disposition': f'attachment; filename="{filename}"',
                            'Content-Type': self._get_mime_type(filename)
                        }
                        
                        if self.auth_header:
                            headers['Authorization'] = self.auth_header
                        
                        async with session.post(
                            f"{self.api_base}/media",
                            data=file_content,
                            headers=headers
                        ) as upload_response:
                            if upload_response.status == 201:
                                result = await upload_response.json()
                                
                                # Update metadata
                                if alt_text or caption or description:
                                    await self._update_media_metadata(
                                        result['id'],
                                        alt_text,
                                        caption,
                                        description
                                    )
                                
                                self.logger.info(f"Media uploaded from URL: {result['id']}")
                                return self._format_media_response(result)
                            else:
                                error_text = await upload_response.text()
                                raise Exception(f"Upload failed: HTTP {upload_response.status} - {error_text}")
                    else:
                        raise Exception(f"Failed to download from URL: HTTP {response.status}")
                        
        except Exception as e:
            self.logger.error(f"Upload from URL failed: {e}")
            raise
    
    async def upload_content_media(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Upload all media associated with content (featured image, attachments, etc.)
        """
        try:
            media_results = {}
            
            # Upload featured image
            if content_data.get('featured_image'):
                featured_image = content_data['featured_image']
                
                if isinstance(featured_image, str) and (featured_image.startswith('http') or os.path.exists(featured_image)):
                    # URL or file path
                    if featured_image.startswith('http'):
                        result = await self.upload_from_url(
                            featured_image,
                            alt_text=content_data.get('featured_image_alt', ''),
                            caption=content_data.get('featured_image_caption', '')
                        )
                    else:
                        result = await self.upload_media(
                            featured_image,
                            alt_text=content_data.get('featured_image_alt', ''),
                            caption=content_data.get('featured_image_caption', '')
                        )
                    
                    media_results['featured_media'] = result['id']
                    media_results['featured_image_url'] = result['source_url']
            
            # Upload media attachments
            attachments = content_data.get('media_attachments', [])
            if attachments:
                uploaded_attachments = []
                
                for attachment in attachments:
                    try:
                        if isinstance(attachment, str):
                            # Simple file path or URL
                            if attachment.startswith('http'):
                                result = await self.upload_from_url(attachment)
                            else:
                                result = await self.upload_media(attachment)
                        elif isinstance(attachment, dict):
                            # Detailed attachment info
                            file_source = attachment.get('file_path') or attachment.get('url')
                            if file_source:
                                if file_source.startswith('http'):
                                    result = await self.upload_from_url(
                                        file_source,
                                        filename=attachment.get('filename'),
                                        alt_text=attachment.get('alt_text', ''),
                                        caption=attachment.get('caption', ''),
                                        description=attachment.get('description', '')
                                    )
                                else:
                                    result = await self.upload_media(
                                        file_source,
                                        filename=attachment.get('filename'),
                                        alt_text=attachment.get('alt_text', ''),
                                        caption=attachment.get('caption', ''),
                                        description=attachment.get('description', '')
                                    )
                                
                                uploaded_attachments.append(result)
                    except Exception as attachment_error:
                        self.logger.warning(f"Failed to upload attachment: {attachment_error}")
                
                if uploaded_attachments:
                    media_results['attachments'] = uploaded_attachments
            
            return media_results
            
        except Exception as e:
            self.logger.error(f"Content media upload failed: {e}")
            return {}
    
    async def get_media_library(self, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Get media library items
        """
        try:
            query_params = params or {}
            query_params.setdefault('per_page', 20)
            
            headers = {}
            if self.auth_header:
                headers['Authorization'] = self.auth_header
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_base}/media",
                    params=query_params,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        media_items = await response.json()
                        return [self._format_media_response(item) for item in media_items]
                    else:
                        return []
                        
        except Exception as e:
            self.logger.error(f"Failed to get media library: {e}")
            return []
    
    async def get_media_item(self, media_id: int) -> Optional[Dict[str, Any]]:
        """
        Get specific media item
        """
        try:
            headers = {}
            if self.auth_header:
                headers['Authorization'] = self.auth_header
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_base}/media/{media_id}",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return self._format_media_response(result)
                    else:
                        return None
                        
        except Exception as e:
            self.logger.error(f"Failed to get media item {media_id}: {e}")
            return None
    
    async def delete_media_item(self, media_id: int, force: bool = True) -> bool:
        """
        Delete media item from WordPress
        """
        try:
            headers = {}
            if self.auth_header:
                headers['Authorization'] = self.auth_header
            
            params = {'force': 'true'} if force else {}
            
            async with aiohttp.ClientSession() as session:
                async with session.delete(
                    f"{self.api_base}/media/{media_id}",
                    params=params,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        self.logger.info(f"Media item deleted: {media_id}")
                        return True
                    else:
                        return False
                        
        except Exception as e:
            self.logger.error(f"Failed to delete media item {media_id}: {e}")
            return False
    
    async def get_media_count(self) -> int:
        """
        Get total count of media items
        """
        try:
            headers = {}
            if self.auth_header:
                headers['Authorization'] = self.auth_header
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_base}/media",
                    params={'per_page': 1},
                    headers=headers
                ) as response:
                    if response.status == 200:
                        # Get total count from response headers
                        total_header = response.headers.get('X-WP-Total')
                        return int(total_header) if total_header else 0
                    else:
                        return 0
                        
        except Exception as e:
            self.logger.error(f"Failed to get media count: {e}")
            return 0
    
    def _is_image_file(self, filename: str) -> bool:
        """Check if file is an image"""
        extension = os.path.splitext(filename)[1].lower()
        return any(extension in extensions for extensions in self.supported_image_types.values())
    
    def _get_mime_type(self, filename: str) -> str:
        """Get MIME type for file"""
        mime_type, _ = mimetypes.guess_type(filename)
        return mime_type or 'application/octet-stream'
    
    async def _optimize_image(self, image_data: bytes, filename: str) -> bytes:
        """
        Optimize image for web use
        """
        try:
            # Open image with PIL
            image = Image.open(io.BytesIO(image_data))
            
            # Get original format
            original_format = image.format
            
            # Convert to RGB if necessary (for JPEG)
            if image.mode in ('RGBA', 'P') and original_format != 'PNG':
                # Create white background for transparency
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            elif image.mode != 'RGB' and original_format == 'JPEG':
                image = image.convert('RGB')
            
            # Resize if too large
            max_width = self.image_optimization['max_width']
            max_height = self.image_optimization['max_height']
            
            if image.width > max_width or image.height > max_height:
                image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                self.logger.info(f"Resized image: {filename}")
            
            # Determine output format
            output_format = original_format
            if original_format == 'BMP':
                output_format = 'JPEG'
            elif original_format == 'PNG' and image.width * image.height > 1000000:  # Large PNG
                # Convert large PNG to JPEG for better compression
                output_format = 'JPEG'
                if image.mode == 'RGBA':
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    background.paste(image, mask=image.split()[-1])
                    image = background
            
            # Save optimized image
            output_buffer = io.BytesIO()
            
            if output_format == 'JPEG':
                image.save(
                    output_buffer,
                    format='JPEG',
                    quality=self.image_optimization['quality'],
                    optimize=True
                )
            elif output_format == 'PNG':
                image.save(
                    output_buffer,
                    format='PNG',
                    optimize=True
                )
            else:
                # Keep original format
                image.save(output_buffer, format=output_format)
            
            optimized_data = output_buffer.getvalue()
            
            # Log optimization results
            original_size = len(image_data)
            optimized_size = len(optimized_data)
            if optimized_size < original_size:
                savings_percent = ((original_size - optimized_size) / original_size) * 100
                self.logger.info(f"Image optimized: {filename} - {savings_percent:.1f}% size reduction")
            
            return optimized_data
            
        except Exception as e:
            self.logger.warning(f"Image optimization failed for {filename}: {e}")
            return image_data  # Return original if optimization fails
    
    async def _update_media_metadata(
        self,
        media_id: int,
        alt_text: str = "",
        caption: str = "",
        description: str = ""
    ) -> bool:
        """
        Update media metadata (alt text, caption, description)
        """
        try:
            update_data = {}
            
            if alt_text:
                update_data['alt_text'] = alt_text
            
            if caption:
                update_data['caption'] = caption
            
            if description:
                update_data['description'] = description
            
            if not update_data:
                return True  # Nothing to update
            
            headers = {'Content-Type': 'application/json'}
            if self.auth_header:
                headers['Authorization'] = self.auth_header
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/media/{media_id}",
                    json=update_data,
                    headers=headers
                ) as response:
                    return response.status == 200
                    
        except Exception as e:
            self.logger.warning(f"Failed to update media metadata for {media_id}: {e}")
            return False
    
    def _format_media_response(self, wp_media: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format WordPress media API response
        """
        return {
            'id': wp_media.get('id'),
            'title': wp_media.get('title', {}).get('rendered', '') if isinstance(wp_media.get('title'), dict) else wp_media.get('title', ''),
            'filename': wp_media.get('slug', ''),
            'source_url': wp_media.get('source_url', ''),
            'link': wp_media.get('link', ''),
            'alt_text': wp_media.get('alt_text', ''),
            'caption': wp_media.get('caption', {}).get('rendered', '') if isinstance(wp_media.get('caption'), dict) else wp_media.get('caption', ''),
            'description': wp_media.get('description', {}).get('rendered', '') if isinstance(wp_media.get('description'), dict) else wp_media.get('description', ''),
            'media_type': wp_media.get('media_type', ''),
            'mime_type': wp_media.get('mime_type', ''),
            'date': wp_media.get('date', ''),
            'modified': wp_media.get('modified', ''),
            'author': wp_media.get('author'),
            'media_details': wp_media.get('media_details', {}),
            'post': wp_media.get('post')  # Associated post ID
        }
    
    async def health_check(self) -> bool:
        """
        Check media manager health
        """
        try:
            # Test basic API access
            if not self.auth_header:
                return False
            
            headers = {'Authorization': self.auth_header}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_base}/media?per_page=1",
                    headers=headers
                ) as response:
                    return response.status == 200
                    
        except Exception as e:
            self.logger.error(f"Media manager health check failed: {e}")
            return False
    
    async def bulk_upload_media(self, media_files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Upload multiple media files
        """
        try:
            self.logger.info(f"Bulk uploading {len(media_files)} media files")
            
            results = []
            
            for media_file in media_files:
                try:
                    file_path = media_file.get('file_path')
                    url = media_file.get('url')
                    
                    if file_path and os.path.exists(file_path):
                        result = await self.upload_media(
                            file_path,
                            filename=media_file.get('filename'),
                            alt_text=media_file.get('alt_text', ''),
                            caption=media_file.get('caption', ''),
                            description=media_file.get('description', '')
                        )
                    elif url:
                        result = await self.upload_from_url(
                            url,
                            filename=media_file.get('filename'),
                            alt_text=media_file.get('alt_text', ''),
                            caption=media_file.get('caption', ''),
                            description=media_file.get('description', '')
                        )
                    else:
                        raise ValueError("No valid file_path or url provided")
                    
                    results.append({'status': 'success', 'data': result})
                    
                except Exception as file_error:
                    self.logger.error(f"Failed to upload media file: {file_error}")
                    results.append({
                        'status': 'failed',
                        'error': str(file_error),
                        'file': media_file.get('filename', 'unknown')
                    })
            
            successful = len([r for r in results if r['status'] == 'success'])
            failed = len([r for r in results if r['status'] == 'failed'])
            
            self.logger.info(f"Bulk upload completed: {successful} successful, {failed} failed")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Bulk media upload failed: {e}")
            raise
