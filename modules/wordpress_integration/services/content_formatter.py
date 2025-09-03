"""
Content Formatter Service - Format content for WordPress publishing
"""

import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from loguru import logger
import html
from markdownify import markdownify
import markdown
from bs4 import BeautifulSoup

from shared.config.settings import get_settings

class ContentFormatter:
    """
    Service for formatting content specifically for WordPress publishing
    """
    
    def __init__(self, container):
        self.container = container
        self.settings = get_settings()
        self.logger = logger.bind(service="ContentFormatter")
        
        # WordPress-specific formatting rules
        self.wordpress_formatting = {
            'convert_headings': True,
            'add_featured_image': True,
            'optimize_images': True,
            'add_table_of_contents': False,
            'add_read_time': True,
            'add_social_sharing': True,
            'auto_excerpt': True,
            'seo_optimization': True
        }
        
        # Content type specific formatting
        self.content_type_formats = {
            'blog_post': {
                'add_author_bio': True,
                'add_related_posts': True,
                'enable_comments': True,
                'post_format': 'standard'
            },
            'tutorial': {
                'add_table_of_contents': True,
                'highlight_code_blocks': True,
                'add_difficulty_level': True,
                'post_format': 'standard'
            },
            'news': {
                'add_publish_date': True,
                'enable_breaking_news': False,
                'post_format': 'standard'
            },
            'review': {
                'add_rating_schema': True,
                'add_pros_cons': True,
                'post_format': 'standard'
            },
            'video': {
                'embed_video': True,
                'add_transcript': True,
                'post_format': 'video'
            },
            'gallery': {
                'create_gallery': True,
                'optimize_images': True,
                'post_format': 'gallery'
            }
        }
    
    async def format_for_wordpress(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format content specifically for WordPress publishing
        """
        try:
            self.logger.info(f"Formatting content for WordPress: {content_data.get('title', 'Untitled')}")
            
            content_type = content_data.get('content_type', 'blog_post')
            
            # Start with base content
            formatted_content = {
                'title': self._format_title(content_data.get('title', '')),
                'content': content_data.get('content', ''),
                'status': content_data.get('publish_status', 'publish'),
                'excerpt': content_data.get('excerpt', ''),
                'categories': self._format_categories(content_data.get('categories', [])),
                'tags': self._format_tags(content_data.get('tags', [])),
                'featured_media': content_data.get('featured_image_id'),
                'format': self._get_post_format(content_type)
            }
            
            # Process content based on type
            formatted_content['content'] = await self._process_content(
                formatted_content['content'],
                content_type,
                content_data
            )
            
            # Auto-generate excerpt if not provided
            if not formatted_content['excerpt']:
                formatted_content['excerpt'] = self._generate_excerpt(formatted_content['content'])
            
            # Add SEO metadata
            if self.wordpress_formatting['seo_optimization']:
                formatted_content['seo'] = await self._generate_seo_metadata(content_data)
            
            # Add custom meta fields
            formatted_content['meta'] = await self._generate_meta_fields(content_data, content_type)
            
            self.logger.info(f"Content formatting completed for: {formatted_content['title']}")
            
            return formatted_content
            
        except Exception as e:
            self.logger.error(f"Content formatting failed: {e}")
            raise
    
    async def _process_content(self, content: str, content_type: str, content_data: Dict[str, Any]) -> str:
        """Process and enhance content for WordPress"""
        try:
            # Clean and sanitize HTML
            content = self._clean_html(content)
            
            # Convert markdown to HTML if needed
            if self._is_markdown(content):
                content = self._markdown_to_html(content)
            
            # Apply content type specific formatting
            type_config = self.content_type_formats.get(content_type, {})
            
            # Add table of contents
            if type_config.get('add_table_of_contents') or self.wordpress_formatting.get('add_table_of_contents'):
                content = self._add_table_of_contents(content)
            
            # Highlight code blocks
            if type_config.get('highlight_code_blocks'):
                content = self._highlight_code_blocks(content)
            
            # Optimize images
            if self.wordpress_formatting.get('optimize_images'):
                content = await self._optimize_images(content)
            
            # Add read time
            if self.wordpress_formatting.get('add_read_time'):
                read_time = self._calculate_read_time(content)
                content = self._add_read_time(content, read_time)
            
            # Add social sharing
            if self.wordpress_formatting.get('add_social_sharing'):
                content = self._add_social_sharing(content)
            
            # Add author bio
            if type_config.get('add_author_bio'):
                content = self._add_author_bio(content, content_data)
            
            # Add difficulty level for tutorials
            if type_config.get('add_difficulty_level'):
                difficulty = content_data.get('difficulty_level', 'Intermediate')
                content = self._add_difficulty_badge(content, difficulty)
            
            # Add pros/cons for reviews
            if type_config.get('add_pros_cons'):
                content = self._add_pros_cons_section(content, content_data)
            
            # Embed videos
            if type_config.get('embed_video') and content_data.get('video_url'):
                content = self._embed_video(content, content_data['video_url'])
            
            return content
            
        except Exception as e:
            self.logger.error(f"Content processing failed: {e}")
            return content  # Return original content if processing fails
    
    def _format_title(self, title: str) -> str:
        """Format title for WordPress"""
        # Clean up title
        title = html.unescape(title)
        title = re.sub(r'\s+', ' ', title).strip()
        
        # Capitalize properly
        # Keep original capitalization for now, but could add title case logic
        
        return title
    
    def _format_categories(self, categories: List[Any]) -> List[int]:
        """Format categories for WordPress API"""
        if not categories:
            return []
        
        # If categories are strings, they need to be converted to category IDs
        # This would require looking up existing categories or creating new ones
        # For now, assume they're already IDs or will be handled by the client
        
        formatted_categories = []
        for category in categories:
            if isinstance(category, int):
                formatted_categories.append(category)
            elif isinstance(category, str):
                # Would need to look up category ID by name
                # For now, skip string categories
                pass
            elif isinstance(category, dict) and category.get('id'):
                formatted_categories.append(category['id'])
        
        return formatted_categories
    
    def _format_tags(self, tags: List[Any]) -> List[int]:
        """Format tags for WordPress API"""
        if not tags:
            return []
        
        # Similar to categories, tags need to be converted to tag IDs
        formatted_tags = []
        for tag in tags:
            if isinstance(tag, int):
                formatted_tags.append(tag)
            elif isinstance(tag, str):
                # Would need to look up tag ID by name
                pass
            elif isinstance(tag, dict) and tag.get('id'):
                formatted_tags.append(tag['id'])
        
        return formatted_tags
    
    def _get_post_format(self, content_type: str) -> str:
        """Get WordPress post format based on content type"""
        type_config = self.content_type_formats.get(content_type, {})
        return type_config.get('post_format', 'standard')
    
    def _clean_html(self, content: str) -> str:
        """Clean and sanitize HTML content"""
        try:
            # Parse HTML
            soup = BeautifulSoup(content, 'html.parser')
            
            # Remove dangerous tags and attributes
            dangerous_tags = ['script', 'style', 'meta', 'link']
            for tag in dangerous_tags:
                for element in soup.find_all(tag):
                    element.decompose()
            
            # Clean up attributes
            for tag in soup.find_all():
                # Keep only safe attributes
                safe_attrs = ['href', 'src', 'alt', 'title', 'class', 'id']
                attrs_to_remove = [attr for attr in tag.attrs if attr not in safe_attrs]
                for attr in attrs_to_remove:
                    del tag[attr]
            
            # Convert back to string
            return str(soup)
            
        except Exception as e:
            self.logger.warning(f"HTML cleaning failed: {e}")
            return content
    
    def _is_markdown(self, content: str) -> bool:
        """Check if content is in Markdown format"""
        # Simple heuristic to detect Markdown
        markdown_indicators = [
            r'^#{1,6}\s',  # Headers
            r'^\*\s',      # Bullet points
            r'^\d+\.\s',   # Numbered lists
            r'\*\*.*\*\*', # Bold
            r'\*.*\*',     # Italic
            r'\[.*\]\(.*\)', # Links
        ]
        
        for indicator in markdown_indicators:
            if re.search(indicator, content, re.MULTILINE):
                return True
        
        return False
    
    def _markdown_to_html(self, content: str) -> str:
        """Convert Markdown to HTML"""
        try:
            return markdown.markdown(content, extensions=['extra', 'codehilite'])
        except Exception as e:
            self.logger.warning(f"Markdown conversion failed: {e}")
            return content
    
    def _add_table_of_contents(self, content: str) -> str:
        """Add table of contents to content"""
        try:
            soup = BeautifulSoup(content, 'html.parser')
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            
            if len(headings) < 3:  # Don't add TOC for short content
                return content
            
            # Generate TOC HTML
            toc_html = '<div class="table-of-contents"><h3>Table of Contents</h3><ul>'
            
            for i, heading in enumerate(headings):
                # Add ID to heading if it doesn't have one
                if not heading.get('id'):
                    heading['id'] = f"toc-{i+1}"
                
                # Add TOC entry
                level = int(heading.name[1])  # h1 -> 1, h2 -> 2, etc.
                indent = '  ' * (level - 1)
                toc_html += f'{indent}<li><a href="#{heading["id"]}">{heading.get_text()}</a></li>'
            
            toc_html += '</ul></div>'
            
            # Insert TOC after first paragraph
            first_p = soup.find('p')
            if first_p:
                toc_soup = BeautifulSoup(toc_html, 'html.parser')
                first_p.insert_after(toc_soup)
            
            return str(soup)
            
        except Exception as e:
            self.logger.warning(f"TOC generation failed: {e}")
            return content
    
    def _highlight_code_blocks(self, content: str) -> str:
        """Add syntax highlighting to code blocks"""
        try:
            # Add CSS classes for syntax highlighting
            content = re.sub(
                r'<pre><code class="language-(\w+)">(.*?)</code></pre>',
                r'<pre class="wp-block-code"><code class="language-\1 hljs">\2</code></pre>',
                content,
                flags=re.DOTALL
            )
            
            # Handle generic code blocks
            content = re.sub(
                r'<pre><code>(.*?)</code></pre>',
                r'<pre class="wp-block-code"><code class="hljs">\1</code></pre>',
                content,
                flags=re.DOTALL
            )
            
            return content
            
        except Exception as e:
            self.logger.warning(f"Code highlighting failed: {e}")
            return content
    
    async def _optimize_images(self, content: str) -> str:
        """Optimize images in content"""
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            for img in soup.find_all('img'):
                # Add responsive classes
                current_class = img.get('class', [])
                if isinstance(current_class, str):
                    current_class = current_class.split()
                
                current_class.extend(['wp-image', 'size-large'])
                img['class'] = ' '.join(current_class)
                
                # Add loading="lazy" for performance
                img['loading'] = 'lazy'
                
                # Ensure alt text exists
                if not img.get('alt'):
                    img['alt'] = 'Image'
            
            return str(soup)
            
        except Exception as e:
            self.logger.warning(f"Image optimization failed: {e}")
            return content
    
    def _calculate_read_time(self, content: str) -> int:
        """Calculate estimated read time in minutes"""
        try:
            # Strip HTML tags
            soup = BeautifulSoup(content, 'html.parser')
            text = soup.get_text()
            
            # Count words
            word_count = len(text.split())
            
            # Average reading speed: 200 words per minute
            read_time = max(1, round(word_count / 200))
            
            return read_time
            
        except Exception as e:
            self.logger.warning(f"Read time calculation failed: {e}")
            return 5  # Default fallback
    
    def _add_read_time(self, content: str, read_time: int) -> str:
        """Add read time indicator to content"""
        try:
            read_time_html = f'''
            <div class="read-time-indicator">
                <span class="read-time-icon">⏱️</span>
                <span class="read-time-text">{read_time} min read</span>
            </div>
            '''
            
            # Insert at the beginning of content
            return read_time_html + content
            
        except Exception as e:
            self.logger.warning(f"Read time addition failed: {e}")
            return content
    
    def _add_social_sharing(self, content: str) -> str:
        """Add social sharing buttons"""
        try:
            sharing_html = '''
            <div class="social-sharing">
                <span class="sharing-label">Share this post:</span>
                <div class="sharing-buttons">
                    <a href="#" class="share-twitter" data-share="twitter">Twitter</a>
                    <a href="#" class="share-facebook" data-share="facebook">Facebook</a>
                    <a href="#" class="share-linkedin" data-share="linkedin">LinkedIn</a>
                    <a href="#" class="share-email" data-share="email">Email</a>
                </div>
            </div>
            '''
            
            # Add at the end of content
            return content + sharing_html
            
        except Exception as e:
            self.logger.warning(f"Social sharing addition failed: {e}")
            return content
    
    def _add_author_bio(self, content: str, content_data: Dict[str, Any]) -> str:
        """Add author bio section"""
        try:
            author_info = content_data.get('author', {})
            
            bio_html = f'''
            <div class="author-bio">
                <div class="author-avatar">
                    <img src="{author_info.get('avatar', '/wp-content/uploads/default-avatar.png')}" 
                         alt="{author_info.get('name', 'Author')}" class="avatar">
                </div>
                <div class="author-info">
                    <h4 class="author-name">{author_info.get('name', 'Content Agent')}</h4>
                    <p class="author-description">
                        {author_info.get('bio', 'AI-powered content creation and optimization.')}
                    </p>
                    <div class="author-social">
                        {self._format_author_social_links(author_info.get('social', {}))}
                    </div>
                </div>
            </div>
            '''
            
            return content + bio_html
            
        except Exception as e:
            self.logger.warning(f"Author bio addition failed: {e}")
            return content
    
    def _format_author_social_links(self, social_links: Dict[str, str]) -> str:
        """Format author social media links"""
        links_html = ""
        
        for platform, url in social_links.items():
            if url:
                links_html += f'<a href="{url}" class="social-link social-{platform}" target="_blank">{platform.title()}</a>'
        
        return links_html
    
    def _add_difficulty_badge(self, content: str, difficulty: str) -> str:
        """Add difficulty level badge for tutorials"""
        try:
            badge_html = f'''
            <div class="difficulty-badge difficulty-{difficulty.lower()}">
                <span class="difficulty-label">Difficulty:</span>
                <span class="difficulty-level">{difficulty}</span>
            </div>
            '''
            
            return badge_html + content
            
        except Exception as e:
            self.logger.warning(f"Difficulty badge addition failed: {e}")
            return content
    
    def _add_pros_cons_section(self, content: str, content_data: Dict[str, Any]) -> str:
        """Add pros and cons section for reviews"""
        try:
            pros = content_data.get('pros', [])
            cons = content_data.get('cons', [])
            
            if not pros and not cons:
                return content
            
            pros_cons_html = '<div class="pros-cons-section">'
            
            if pros:
                pros_cons_html += '<div class="pros"><h4>✅ Pros</h4><ul>'
                for pro in pros:
                    pros_cons_html += f'<li>{pro}</li>'
                pros_cons_html += '</ul></div>'
            
            if cons:
                pros_cons_html += '<div class="cons"><h4>❌ Cons</h4><ul>'
                for con in cons:
                    pros_cons_html += f'<li>{con}</li>'
                pros_cons_html += '</ul></div>'
            
            pros_cons_html += '</div>'
            
            # Insert before the last paragraph
            soup = BeautifulSoup(content, 'html.parser')
            paragraphs = soup.find_all('p')
            if paragraphs:
                last_p = paragraphs[-1]
                pros_cons_soup = BeautifulSoup(pros_cons_html, 'html.parser')
                last_p.insert_before(pros_cons_soup)
                return str(soup)
            
            return content + pros_cons_html
            
        except Exception as e:
            self.logger.warning(f"Pros/cons section addition failed: {e}")
            return content
    
    def _embed_video(self, content: str, video_url: str) -> str:
        """Embed video in content"""
        try:
            # Create responsive video embed
            embed_html = f'''
            <div class="video-embed">
                <div class="video-wrapper">
                    <iframe src="{video_url}" 
                            frameborder="0" 
                            allowfullscreen
                            loading="lazy">
                    </iframe>
                </div>
            </div>
            '''
            
            # Insert at the beginning of content
            return embed_html + content
            
        except Exception as e:
            self.logger.warning(f"Video embedding failed: {e}")
            return content
    
    def _generate_excerpt(self, content: str) -> str:
        """Generate excerpt from content"""
        try:
            # Strip HTML tags
            soup = BeautifulSoup(content, 'html.parser')
            text = soup.get_text()
            
            # Get first paragraph or first 160 characters
            sentences = text.split('.')
            excerpt = sentences[0]
            
            if len(excerpt) > 160:
                excerpt = excerpt[:157] + '...'
            elif len(excerpt) < 50 and len(sentences) > 1:
                excerpt += '. ' + sentences[1]
                if len(excerpt) > 160:
                    excerpt = excerpt[:157] + '...'
            
            return excerpt.strip()
            
        except Exception as e:
            self.logger.warning(f"Excerpt generation failed: {e}")
            return ""
    
    async def _generate_seo_metadata(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate SEO metadata for WordPress"""
        try:
            seo_data = {}
            
            # Meta description
            if content_data.get('meta_description'):
                seo_data['meta_description'] = content_data['meta_description']
            else:
                # Auto-generate from excerpt or content
                excerpt = content_data.get('excerpt', '')
                if not excerpt:
                    excerpt = self._generate_excerpt(content_data.get('content', ''))
                seo_data['meta_description'] = excerpt[:160]
            
            # Focus keyword
            if content_data.get('focus_keyword'):
                seo_data['focus_keyword'] = content_data['focus_keyword']
            elif content_data.get('keywords'):
                # Use first keyword
                keywords = content_data['keywords']
                if isinstance(keywords, list) and keywords:
                    seo_data['focus_keyword'] = keywords[0]
                elif isinstance(keywords, str):
                    seo_data['focus_keyword'] = keywords
            
            # Canonical URL
            if content_data.get('canonical_url'):
                seo_data['canonical_url'] = content_data['canonical_url']
            
            # Schema.org data
            seo_data['schema'] = {
                '@context': 'https://schema.org',
                '@type': 'Article',
                'headline': content_data.get('title', ''),
                'description': seo_data.get('meta_description', ''),
                'author': {
                    '@type': 'Organization',
                    'name': 'Content Agent'
                },
                'publisher': {
                    '@type': 'Organization',
                    'name': 'Content Agent'
                },
                'datePublished': datetime.utcnow().isoformat(),
                'dateModified': datetime.utcnow().isoformat()
            }
            
            return seo_data
            
        except Exception as e:
            self.logger.warning(f"SEO metadata generation failed: {e}")
            return {}
    
    async def _generate_meta_fields(self, content_data: Dict[str, Any], content_type: str) -> Dict[str, Any]:
        """Generate custom meta fields"""
        try:
            meta = {}
            
            # Content Agent metadata
            meta['_content_agent_generated'] = 'true'
            meta['_content_agent_version'] = '1.0.0'
            meta['_content_agent_content_type'] = content_type
            meta['_content_agent_generated_at'] = datetime.utcnow().isoformat()
            
            # Content specific metadata
            if content_data.get('word_count'):
                meta['_word_count'] = str(content_data['word_count'])
            
            if content_data.get('reading_time'):
                meta['_reading_time'] = str(content_data['reading_time'])
            
            if content_data.get('seo_score'):
                meta['_seo_score'] = str(content_data['seo_score'])
            
            # Content type specific metadata
            if content_type == 'review':
                if content_data.get('rating'):
                    meta['_review_rating'] = str(content_data['rating'])
                if content_data.get('review_product'):
                    meta['_review_product'] = content_data['review_product']
            
            elif content_type == 'tutorial':
                if content_data.get('difficulty_level'):
                    meta['_tutorial_difficulty'] = content_data['difficulty_level']
                if content_data.get('estimated_time'):
                    meta['_tutorial_time'] = str(content_data['estimated_time'])
            
            return meta
            
        except Exception as e:
            self.logger.warning(f"Meta fields generation failed: {e}")
            return {}
    
    async def health_check(self) -> bool:
        """Check content formatter health"""
        try:
            # Test basic formatting functionality
            test_content = "<h1>Test</h1><p>This is a test.</p>"
            formatted = self._clean_html(test_content)
            return bool(formatted)
        except Exception as e:
            self.logger.error(f"Content formatter health check failed: {e}")
            return False
