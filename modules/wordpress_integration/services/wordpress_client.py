"""
WordPress Client Service - WordPress REST API integration
"""

import aiohttp
import base64
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from loguru import logger
import asyncio

from shared.config.settings import get_settings

class WordPressClient:
    """
    WordPress REST API client for content publishing and management
    """
    
    def __init__(self, container):
        self.container = container
        self.settings = get_settings()
        self.logger = logger.bind(service="WordPressClient")
        
        # WordPress configuration
        self.wordpress_url = self.settings.wordpress_url
        self.username = self.settings.wordpress_username  
        self.app_password = self.settings.wordpress_app_password
        
        # API endpoints
        self.api_base = f"{self.wordpress_url.rstrip('/')}/wp-json/wp/v2"
        
        # Request session configuration
        self.session_config = {
            'timeout': aiohttp.ClientTimeout(total=30),
            'headers': {
                'User-Agent': 'ContentAgent/1.0',
                'Content-Type': 'application/json'
            }
        }
        
        # Authentication
        if self.username and self.app_password:
            credentials = f"{self.username}:{self.app_password}"
            credentials_b64 = base64.b64encode(credentials.encode()).decode()
            self.session_config['headers']['Authorization'] = f"Basic {credentials_b64}"
        
        # Post status mapping
        self.status_mapping = {
            'draft': 'draft',
            'publish': 'publish', 
            'private': 'private',
            'pending': 'pending',
            'future': 'future'  # For scheduled posts
        }
    
    async def test_connection(self) -> bool:
        """Test connection to WordPress site"""
        try:
            async with aiohttp.ClientSession(**self.session_config) as session:
                # Test basic API access
                async with session.get(f"{self.api_base}/posts?per_page=1") as response:
                    if response.status == 200:
                        self.logger.info("WordPress connection test successful")
                        return True
                    else:
                        self.logger.error(f"WordPress connection failed: HTTP {response.status}")
                        return False
                        
        except Exception as e:
            self.logger.error(f"WordPress connection test failed: {e}")
            return False
    
    async def publish_post(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Publish a post to WordPress
        """
        try:
            self.logger.info(f"Publishing post to WordPress: {post_data.get('title', 'Untitled')}")
            
            # Prepare WordPress post data
            wp_post = self._prepare_post_data(post_data)
            
            async with aiohttp.ClientSession(**self.session_config) as session:
                async with session.post(f"{self.api_base}/posts", json=wp_post) as response:
                    if response.status == 201:
                        result = await response.json()
                        
                        self.logger.info(f"Post published successfully: {result.get('id')}")
                        
                        return {
                            'id': result.get('id'),
                            'title': result.get('title', {}).get('rendered', ''),
                            'link': result.get('link', ''),
                            'date': result.get('date', ''),
                            'status': result.get('status', ''),
                            'excerpt': result.get('excerpt', {}).get('rendered', ''),
                            'featured_media': result.get('featured_media'),
                            'categories': result.get('categories', []),
                            'tags': result.get('tags', [])
                        }
                    else:
                        error_text = await response.text()
                        raise Exception(f"WordPress publish failed: HTTP {response.status} - {error_text}")
                        
        except Exception as e:
            self.logger.error(f"WordPress post publishing failed: {e}")
            raise
    
    async def update_post(self, post_id: int, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing WordPress post"""
        try:
            self.logger.info(f"Updating WordPress post: {post_id}")
            
            wp_post = self._prepare_post_data(post_data)
            
            async with aiohttp.ClientSession(**self.session_config) as session:
                async with session.post(f"{self.api_base}/posts/{post_id}", json=wp_post) as response:
                    if response.status == 200:
                        result = await response.json()
                        self.logger.info(f"Post updated successfully: {post_id}")
                        return self._format_post_response(result)
                    else:
                        error_text = await response.text()
                        raise Exception(f"WordPress update failed: HTTP {response.status} - {error_text}")
                        
        except Exception as e:
            self.logger.error(f"WordPress post update failed: {e}")
            raise
    
    async def delete_post(self, post_id: int, force: bool = False) -> bool:
        """Delete a WordPress post"""
        try:
            self.logger.info(f"Deleting WordPress post: {post_id}")
            
            params = {'force': 'true'} if force else {}
            
            async with aiohttp.ClientSession(**self.session_config) as session:
                async with session.delete(f"{self.api_base}/posts/{post_id}", params=params) as response:
                    if response.status == 200:
                        self.logger.info(f"Post deleted successfully: {post_id}")
                        return True
                    else:
                        error_text = await response.text()
                        raise Exception(f"WordPress delete failed: HTTP {response.status} - {error_text}")
                        
        except Exception as e:
            self.logger.error(f"WordPress post deletion failed: {e}")
            return False
    
    async def get_post(self, post_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific WordPress post"""
        try:
            async with aiohttp.ClientSession(**self.session_config) as session:
                async with session.get(f"{self.api_base}/posts/{post_id}") as response:
                    if response.status == 200:
                        result = await response.json()
                        return self._format_post_response(result)
                    else:
                        return None
                        
        except Exception as e:
            self.logger.error(f"Failed to get WordPress post {post_id}: {e}")
            return None
    
    async def get_posts(self, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get list of WordPress posts"""
        try:
            query_params = params or {}
            query_params.setdefault('per_page', 10)
            
            async with aiohttp.ClientSession(**self.session_config) as session:
                async with session.get(f"{self.api_base}/posts", params=query_params) as response:
                    if response.status == 200:
                        results = await response.json()
                        return [self._format_post_response(post) for post in results]
                    else:
                        return []
                        
        except Exception as e:
            self.logger.error(f"Failed to get WordPress posts: {e}")
            return []
    
    async def get_categories(self) -> List[Dict[str, Any]]:
        """Get WordPress categories"""
        try:
            async with aiohttp.ClientSession(**self.session_config) as session:
                async with session.get(f"{self.api_base}/categories") as response:
                    if response.status == 200:
                        categories = await response.json()
                        return [
                            {
                                'id': cat.get('id'),
                                'name': cat.get('name'),
                                'slug': cat.get('slug'),
                                'count': cat.get('count', 0)
                            }
                            for cat in categories
                        ]
                    else:
                        return []
                        
        except Exception as e:
            self.logger.error(f"Failed to get WordPress categories: {e}")
            return []
    
    async def get_tags(self) -> List[Dict[str, Any]]:
        """Get WordPress tags"""
        try:
            async with aiohttp.ClientSession(**self.session_config) as session:
                async with session.get(f"{self.api_base}/tags") as response:
                    if response.status == 200:
                        tags = await response.json()
                        return [
                            {
                                'id': tag.get('id'),
                                'name': tag.get('name'),
                                'slug': tag.get('slug'),
                                'count': tag.get('count', 0)
                            }
                            for tag in tags
                        ]
                    else:
                        return []
                        
        except Exception as e:
            self.logger.error(f"Failed to get WordPress tags: {e}")
            return []
    
    async def create_category(self, name: str, description: str = "") -> Optional[Dict[str, Any]]:
        """Create a new WordPress category"""
        try:
            category_data = {
                'name': name,
                'description': description
            }
            
            async with aiohttp.ClientSession(**self.session_config) as session:
                async with session.post(f"{self.api_base}/categories", json=category_data) as response:
                    if response.status == 201:
                        result = await response.json()
                        return {
                            'id': result.get('id'),
                            'name': result.get('name'),
                            'slug': result.get('slug')
                        }
                    else:
                        return None
                        
        except Exception as e:
            self.logger.error(f"Failed to create WordPress category: {e}")
            return None
    
    async def create_tag(self, name: str, description: str = "") -> Optional[Dict[str, Any]]:
        """Create a new WordPress tag"""
        try:
            tag_data = {
                'name': name,
                'description': description
            }
            
            async with aiohttp.ClientSession(**self.session_config) as session:
                async with session.post(f"{self.api_base}/tags", json=tag_data) as response:
                    if response.status == 201:
                        result = await response.json()
                        return {
                            'id': result.get('id'),
                            'name': result.get('name'),
                            'slug': result.get('slug')
                        }
                    else:
                        return None
                        
        except Exception as e:
            self.logger.error(f"Failed to create WordPress tag: {e}")
            return None
    
    async def schedule_post(self, post_data: Dict[str, Any], publish_time: datetime) -> Dict[str, Any]:
        """Schedule a post for future publication"""
        try:
            self.logger.info(f"Scheduling WordPress post for {publish_time}")
            
            wp_post = self._prepare_post_data(post_data)
            wp_post['status'] = 'future'
            wp_post['date'] = publish_time.isoformat()
            
            async with aiohttp.ClientSession(**self.session_config) as session:
                async with session.post(f"{self.api_base}/posts", json=wp_post) as response:
                    if response.status == 201:
                        result = await response.json()
                        self.logger.info(f"Post scheduled successfully: {result.get('id')}")
                        return self._format_post_response(result)
                    else:
                        error_text = await response.text()
                        raise Exception(f"WordPress scheduling failed: HTTP {response.status} - {error_text}")
                        
        except Exception as e:
            self.logger.error(f"WordPress post scheduling failed: {e}")
            raise
    
    async def get_site_info(self) -> Dict[str, Any]:
        """Get WordPress site information"""
        try:
            async with aiohttp.ClientSession(**self.session_config) as session:
                async with session.get(f"{self.wordpress_url.rstrip('/')}/wp-json") as response:
                    if response.status == 200:
                        site_info = await response.json()
                        return {
                            'name': site_info.get('name', ''),
                            'description': site_info.get('description', ''),
                            'url': site_info.get('url', ''),
                            'home': site_info.get('home', ''),
                            'gmt_offset': site_info.get('gmt_offset', 0),
                            'timezone_string': site_info.get('timezone_string', ''),
                            'namespaces': site_info.get('namespaces', [])
                        }
                    else:
                        return {}
                        
        except Exception as e:
            self.logger.error(f"Failed to get WordPress site info: {e}")
            return {}
    
    async def get_recent_posts_count(self, days: int = 7) -> int:
        """Get count of recent posts"""
        try:
            # Calculate date threshold (use UTC for WordPress API compatibility)
            threshold_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            params = {
                'after': threshold_date,
                'per_page': 100  # Max to get accurate count
            }
            
            posts = await self.get_posts(params)
            return len(posts)
            
        except Exception as e:
            self.logger.error(f"Failed to get recent posts count: {e}")
            return 0
    
    def _prepare_post_data(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare post data for WordPress API"""
        wp_post = {
            'title': post_data.get('title', ''),
            'content': post_data.get('content', ''),
            'status': self.status_mapping.get(post_data.get('status', 'publish'), 'publish'),
            'excerpt': post_data.get('excerpt', ''),
            'format': post_data.get('format', 'standard')  # standard, aside, chat, gallery, etc.
        }
        
        # Handle categories
        if post_data.get('categories'):
            if isinstance(post_data['categories'], list):
                wp_post['categories'] = post_data['categories']
            else:
                wp_post['categories'] = [post_data['categories']]
        
        # Handle tags
        if post_data.get('tags'):
            if isinstance(post_data['tags'], list):
                wp_post['tags'] = post_data['tags']
            else:
                wp_post['tags'] = [post_data['tags']]
        
        # Handle featured image
        if post_data.get('featured_media'):
            wp_post['featured_media'] = post_data['featured_media']
        
        # Handle custom fields/meta
        if post_data.get('meta'):
            wp_post['meta'] = post_data['meta']
        
        # Handle SEO data (if using Yoast or similar)
        if post_data.get('seo'):
            seo_data = post_data['seo']
            wp_post['meta'] = wp_post.get('meta', {})
            
            if seo_data.get('meta_description'):
                wp_post['meta']['_yoast_wpseo_metadesc'] = seo_data['meta_description']
            
            if seo_data.get('focus_keyword'):
                wp_post['meta']['_yoast_wpseo_focuskw'] = seo_data['focus_keyword']
            
            if seo_data.get('canonical_url'):
                wp_post['meta']['_yoast_wpseo_canonical'] = seo_data['canonical_url']
        
        return wp_post
    
    def _format_post_response(self, wp_post: Dict[str, Any]) -> Dict[str, Any]:
        """Format WordPress API response"""
        return {
            'id': wp_post.get('id'),
            'title': wp_post.get('title', {}).get('rendered', '') if isinstance(wp_post.get('title'), dict) else wp_post.get('title', ''),
            'content': wp_post.get('content', {}).get('rendered', '') if isinstance(wp_post.get('content'), dict) else wp_post.get('content', ''),
            'excerpt': wp_post.get('excerpt', {}).get('rendered', '') if isinstance(wp_post.get('excerpt'), dict) else wp_post.get('excerpt', ''),
            'link': wp_post.get('link', ''),
            'date': wp_post.get('date', ''),
            'modified': wp_post.get('modified', ''),
            'status': wp_post.get('status', ''),
            'featured_media': wp_post.get('featured_media'),
            'categories': wp_post.get('categories', []),
            'tags': wp_post.get('tags', []),
            'format': wp_post.get('format', 'standard'),
            'meta': wp_post.get('meta', {}),
            'author': wp_post.get('author'),
            'slug': wp_post.get('slug', '')
        }
    
    async def health_check(self) -> bool:
        """Check WordPress client health"""
        try:
            # Basic configuration check
            if not self.wordpress_url:
                return False
            
            # Connection test
            return await self.test_connection()
            
        except Exception as e:
            self.logger.error(f"WordPress health check failed: {e}")
            return False

    async def bulk_publish_posts(self, posts_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Publish multiple posts to WordPress"""
        try:
            self.logger.info(f"Bulk publishing {len(posts_data)} posts to WordPress")
            
            results = []
            
            # Process posts concurrently but with rate limiting
            semaphore = asyncio.Semaphore(3)  # Limit to 3 concurrent requests
            
            async def publish_single_post(post_data):
                async with semaphore:
                    try:
                        result = await self.publish_post(post_data)
                        return {'status': 'success', 'data': result}
                    except Exception as e:
                        return {
                            'status': 'failed', 
                            'error': str(e),
                            'title': post_data.get('title', 'Unknown')
                        }
            
            # Execute all publishing tasks
            tasks = [publish_single_post(post_data) for post_data in posts_data]
            results = await asyncio.gather(*tasks)
            
            successful = len([r for r in results if r['status'] == 'success'])
            failed = len([r for r in results if r['status'] == 'failed'])
            
            self.logger.info(f"Bulk publish completed: {successful} successful, {failed} failed")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Bulk publishing failed: {e}")
            raise
