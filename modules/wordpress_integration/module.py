"""
WordPress Integration Module
Content publishing and management for WordPress sites
"""

from core.base_module import BaseModule, ModuleInfo
from .services.wordpress_client import WordPressClient
from .services.content_formatter import ContentFormatter
from .services.media_manager import MediaManager
from .routes import router
from .ui import WordPressUI

class WordPressIntegrationModule(BaseModule):
    """
    Module for WordPress content publishing and site management
    """
    
    def get_module_info(self) -> ModuleInfo:
        return ModuleInfo(
            name="wordpress_integration",
            version="1.0.0",
            description="WordPress content publishing and site management",
            dependencies=["content_generation"],
            optional_dependencies=["scheduling"],
            author="Content Agent Team"
        )
    
    async def initialize(self) -> bool:
        """Initialize the WordPress integration module"""
        try:
            # Initialize services
            self.wordpress_client = WordPressClient(self.container)
            self.content_formatter = ContentFormatter(self.container)
            self.media_manager = MediaManager(self.container)
            
            # Register services in DI container
            self.register_service('wordpress_client', self.wordpress_client)
            self.register_service('content_formatter', self.content_formatter)
            self.register_service('media_manager', self.media_manager)
            
            # Subscribe to events
            self.subscribe_to_event('content_generation.content_ready', self._on_content_ready)
            self.subscribe_to_event('scheduling.publish_requested', self._on_publish_requested)
            self.subscribe_to_event('content_generation.media_generated', self._on_media_generated)
            
            # Test WordPress connection
            connection_ok = await self.wordpress_client.test_connection()
            if not connection_ok:
                self.logger.warning("WordPress connection test failed - check credentials")
            
            self.logger.info("WordPress integration module initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"WordPress module initialization failed: {e}")
            return False
    
    def register_routes(self, app):
        """Register FastAPI routes"""
        app.include_router(router, prefix="/api/wordpress", tags=["wordpress"])
    
    def register_ui_components(self):
        """Register Streamlit UI components"""
        return {
            "wordpress_dashboard": WordPressUI.dashboard,
            "wordpress_settings": WordPressUI.settings,
            "publish_content": WordPressUI.publish_form,
            "media_library": WordPressUI.media_library,
            "site_management": WordPressUI.site_management,
            "publishing_history": WordPressUI.publishing_history
        }
    
    async def _on_content_ready(self, event):
        """Handle content generation completion"""
        content_data = event.data
        
        # Check if auto-publish to WordPress is enabled
        if content_data.get('auto_publish_wordpress'):
            try:
                # Format content for WordPress
                formatted_content = await self.content_formatter.format_for_wordpress(content_data)
                
                # Publish to WordPress
                publish_result = await self.wordpress_client.publish_post(formatted_content)
                
                self.emit_event('wordpress_published', {
                    'content_id': content_data.get('content_id'),
                    'wordpress_post_id': publish_result.get('id'),
                    'wordpress_url': publish_result.get('link'),
                    'published_at': publish_result.get('date'),
                    'status': publish_result.get('status')
                })
                
            except Exception as e:
                self.logger.error(f"Auto-publish to WordPress failed: {e}")
                self.emit_event('wordpress_publish_failed', {
                    'content_id': content_data.get('content_id'),
                    'error': str(e)
                })
    
    async def _on_publish_requested(self, event):
        """Handle publish requests from scheduling module"""
        publish_data = event.data
        
        if publish_data.get('platform') == 'wordpress':
            try:
                # Get content data
                content_id = publish_data.get('content_id')
                content = await self._get_content_data(content_id)
                
                if not content:
                    raise ValueError("Content not found")
                
                # Format for WordPress
                formatted_content = await self.content_formatter.format_for_wordpress(content)
                
                # Handle media if present
                if content.get('featured_image') or content.get('media_attachments'):
                    media_result = await self.media_manager.upload_content_media(content)
                    if media_result:
                        formatted_content.update(media_result)
                
                # Publish to WordPress
                publish_result = await self.wordpress_client.publish_post(formatted_content)
                
                self.emit_event('content_published', {
                    'content_id': content_id,
                    'platform': 'wordpress',
                    'platform_id': publish_result.get('id'),
                    'published_url': publish_result.get('link'),
                    'published_at': publish_result.get('date'),
                    'status': 'success'
                })
                
            except Exception as e:
                self.logger.error(f"WordPress publish request failed: {e}")
                self.emit_event('content_published', {
                    'content_id': publish_data.get('content_id'),
                    'platform': 'wordpress',
                    'status': 'failed',
                    'error': str(e)
                })
    
    async def _on_media_generated(self, event):
        """Handle generated media (images, videos, etc.)"""
        media_data = event.data
        
        try:
            # Upload media to WordPress
            upload_result = await self.media_manager.upload_media(
                media_data.get('file_path'),
                media_data.get('filename'),
                media_data.get('alt_text', ''),
                media_data.get('caption', '')
            )
            
            self.emit_event('wordpress_media_uploaded', {
                'original_media_id': media_data.get('media_id'),
                'wordpress_media_id': upload_result.get('id'),
                'wordpress_url': upload_result.get('source_url'),
                'uploaded_at': upload_result.get('date')
            })
            
        except Exception as e:
            self.logger.error(f"WordPress media upload failed: {e}")
    
    async def _get_content_data(self, content_id: str):
        """Get content data from content generation service"""
        try:
            content_service = self.container.get_service('content_service')
            if content_service:
                return await content_service.get_content(content_id)
            
            # Mock implementation if service not available
            return {
                'content_id': content_id,
                'title': 'Sample Content Title',
                'content': '<p>Sample content body...</p>',
                'excerpt': 'Sample excerpt...',
                'tags': ['content', 'ai-generated'],
                'category': 'Blog',
                'featured_image': None
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get content data: {e}")
            return None
    
    async def health_check(self):
        """Health check for the WordPress integration module"""
        base_health = await super().health_check()
        
        # Check service health
        wp_client_ok = await self.wordpress_client.health_check()
        formatter_ok = await self.content_formatter.health_check()
        media_manager_ok = await self.media_manager.health_check()
        
        # Test WordPress connection
        wp_connection_ok = await self.wordpress_client.test_connection()
        
        base_health.update({
            "wordpress_client_healthy": wp_client_ok,
            "content_formatter_healthy": formatter_ok,
            "media_manager_healthy": media_manager_ok,
            "wordpress_connection": wp_connection_ok,
            "recent_publications": await self.wordpress_client.get_recent_posts_count(),
            "media_library_size": await self.media_manager.get_media_count()
        })
        
        return base_health
