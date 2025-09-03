"""
Scraping Service - Core web scraping functionality using Crawl4AI
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse, parse_qs
import re
from loguru import logger

from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import LLMExtractionStrategy, JsonCssExtractionStrategy
from crawl4ai.chunking_strategy import RegexChunking
from crawl4ai.cache_context import CacheMode

from shared.config.settings import get_settings

class Crawl4AIScrapingService:
    """
    Advanced web scraping service using Crawl4AI for intelligent content extraction
    """
    
    def __init__(self, container):
        self.container = container
        self.settings = get_settings()
        self.logger = logger.bind(service="Crawl4AIScrapingService")
        
        # Crawl4AI configuration
        self.crawler = None
        self.is_initialized = False
        
        # Cache configuration
        self.cache_ttl = 3600  # 1 hour
        self.use_cache = True
        
        # Content extraction schemas
        self.extraction_schemas = {
            'article': {
                'title': {'selector': 'h1, .post-title, .entry-title, .article-title', 'type': 'text'},
                'author': {'selector': '.author, .by-author, [rel="author"], .post-author', 'type': 'text'},
                'date': {'selector': '.date, .published, .post-date, time[datetime]', 'type': 'text'},
                'content': {'selector': '.content, .post-content, .entry-content, .article-content, article, main', 'type': 'html'},
                'tags': {'selector': '.tags a, .post-tags a, .categories a', 'type': 'list'},
                'excerpt': {'selector': '.excerpt, .summary, .description', 'type': 'text'}
            },
            'product': {
                'name': {'selector': 'h1, .product-title, .product-name', 'type': 'text'},
                'price': {'selector': '.price, .cost, .amount', 'type': 'text'},
                'description': {'selector': '.description, .product-description', 'type': 'html'},
                'features': {'selector': '.features li, .specs li', 'type': 'list'},
                'rating': {'selector': '.rating, .stars', 'type': 'text'},
                'availability': {'selector': '.stock, .availability', 'type': 'text'}
            },
            'job_listing': {
                'title': {'selector': 'h1, .job-title', 'type': 'text'},
                'company': {'selector': '.company, .employer', 'type': 'text'},
                'location': {'selector': '.location, .address', 'type': 'text'},
                'salary': {'selector': '.salary, .pay, .compensation', 'type': 'text'},
                'description': {'selector': '.description, .job-description', 'type': 'html'},
                'requirements': {'selector': '.requirements li, .qualifications li', 'type': 'list'}
            }
        }
        
        # LLM extraction prompts
        self.llm_prompts = {
            'article_analysis': """
            Extract the following information from this article:
            1. Main topic and key themes
            2. Target audience
            3. Content structure (headings, sections)
            4. Key insights and takeaways
            5. Writing style and tone
            6. SEO keywords mentioned
            7. Call-to-actions present
            
            Format as JSON with clear sections.
            """,
            'competitor_analysis': """
            Analyze this competitor content for:
            1. Content strategy insights
            2. Unique value propositions
            3. Content gaps or opportunities
            4. SEO optimization techniques used
            5. Content format and structure
            6. Audience engagement tactics
            
            Provide actionable competitive intelligence.
            """,
            'content_summary': """
            Provide a comprehensive summary including:
            1. Executive summary (2-3 sentences)
            2. Main points covered
            3. Key statistics or data mentioned
            4. Actionable insights
            5. Relevance score for content marketing
            """
        }
    
    async def initialize(self):
        """Initialize the Crawl4AI crawler"""
        if self.is_initialized:
            return True
            
        try:
            self.crawler = AsyncWebCrawler(
                # Browser configuration
                headless=True,
                browser_type="chromium",  # or "firefox", "webkit"
                
                # Performance settings
                page_timeout=30000,
                request_timeout=30000,
                
                # Cache settings
                use_cached_html=self.use_cache,
                cache_mode=CacheMode.ENABLED,
                
                # User agent rotation
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                
                # JavaScript execution
                js_code="",
                wait_for="",
                
                # Screenshot capability
                screenshot=False,
                
                # Verbose logging
                verbose=self.settings.debug
            )
            
            # Start the crawler
            await self.crawler.astart()
            self.is_initialized = True
            
            self.logger.info("Crawl4AI scraping service initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Crawl4AI: {e}")
            return False
    
    async def scrape_url(
        self, 
        url: str, 
        extraction_strategy: str = "basic",
        content_type: str = "article",
        use_llm: bool = False,
        custom_schema: Dict = None
    ) -> Dict[str, Any]:
        """
        Scrape a single URL with advanced content extraction
        
        Args:
            url: URL to scrape
            extraction_strategy: "basic", "css", "llm", or "hybrid"
            content_type: "article", "product", "job_listing", etc.
            use_llm: Whether to use LLM for content analysis
            custom_schema: Custom extraction schema
        """
        try:
            if not self.is_initialized:
                await self.initialize()
            
            self.logger.info(f"Scraping URL: {url}")
            
            # Determine extraction strategy
            strategy = None
            
            if extraction_strategy == "css" or extraction_strategy == "basic":
                # Use CSS-based extraction
                schema = custom_schema or self.extraction_schemas.get(content_type, self.extraction_schemas['article'])
                strategy = JsonCssExtractionStrategy(schema)
                
            elif extraction_strategy == "llm" and use_llm:
                # Use LLM-based extraction
                prompt = self.llm_prompts.get('content_summary', self.llm_prompts['article_analysis'])
                strategy = LLMExtractionStrategy(
                    provider="openai",  # or "anthropic", "huggingface"
                    api_token=self.settings.openai_api_key,
                    instruction=prompt
                )
            
            # Execute crawling
            result = await self.crawler.arun(
                url=url,
                extraction_strategy=strategy,
                cache_mode=CacheMode.ENABLED if self.use_cache else CacheMode.DISABLED,
                
                # Content processing
                chunking_strategy=RegexChunking(),
                
                # Session management
                session_id=f"scrape_{int(time.time())}",
                
                # Additional options
                process_iframes=False,
                remove_overlay_elements=True,
                simulate_user=True,
                magic=True,  # Enable smart content extraction
                
                # Custom JavaScript if needed
                js_code="",
                wait_for=""
            )
            
            # Process and structure the result
            processed_result = await self._process_crawl_result(result, url, content_type, use_llm)
            
            self.logger.info(f"Successfully scraped: {url}")
            return processed_result
            
        except Exception as e:
            self.logger.error(f"Failed to scrape {url}: {e}")
            return {
                'url': url,
                'error': str(e),
                'scraped_at': datetime.utcnow().isoformat(),
                'status': 'failed'
            }
    
    async def scrape_multiple_urls(
        self, 
        urls: List[str], 
        extraction_strategy: str = "basic",
        content_type: str = "article",
        max_concurrent: int = 5,
        use_llm: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Scrape multiple URLs concurrently with intelligent rate limiting
        """
        try:
            if not self.is_initialized:
                await self.initialize()
            
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def scrape_single(url):
                async with semaphore:
                    return await self.scrape_url(url, extraction_strategy, content_type, use_llm)
            
            self.logger.info(f"Scraping {len(urls)} URLs concurrently")
            
            # Execute all scraping tasks
            tasks = [scrape_single(url) for url in urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results and handle exceptions
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append({
                        'url': urls[i],
                        'error': str(result),
                        'status': 'failed',
                        'scraped_at': datetime.utcnow().isoformat()
                    })
                else:
                    processed_results.append(result)
            
            successful_count = len([r for r in processed_results if r.get('status') != 'failed'])
            self.logger.info(f"Successfully scraped {successful_count}/{len(urls)} URLs")
            
            return processed_results
            
        except Exception as e:
            self.logger.error(f"Batch scraping failed: {e}")
            return [{'error': str(e), 'status': 'failed'} for _ in urls]
    
    async def smart_content_extraction(
        self, 
        url: str, 
        extraction_goal: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Intelligent content extraction using AI-powered analysis
        
        Args:
            url: URL to scrape
            extraction_goal: "comprehensive", "competitor_analysis", "content_ideas", "seo_analysis"
        """
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # Custom LLM prompt based on extraction goal
            prompts = {
                'comprehensive': self.llm_prompts['content_summary'],
                'competitor_analysis': self.llm_prompts['competitor_analysis'],
                'content_ideas': """
                Analyze this content and suggest:
                1. Related content topics that could be created
                2. Content gaps this piece doesn't cover
                3. Different angles or perspectives to explore
                4. Content formats that would work well for this topic
                5. Target audience segments to consider
                """,
                'seo_analysis': """
                Analyze the SEO aspects of this content:
                1. Primary and secondary keywords used
                2. Content structure and heading optimization
                3. Meta elements and their effectiveness
                4. Internal/external linking strategy
                5. Content length and depth analysis
                6. User intent satisfaction
                7. Recommendations for improvement
                """
            }
            
            prompt = prompts.get(extraction_goal, prompts['comprehensive'])
            
            # Use LLM extraction strategy
            strategy = LLMExtractionStrategy(
                provider="openai",
                api_token=self.settings.openai_api_key,
                instruction=prompt,
                extra_args={
                    "temperature": 0.1,  # More deterministic results
                    "max_tokens": 2000
                }
            )
            
            # Execute smart crawling
            result = await self.crawler.arun(
                url=url,
                extraction_strategy=strategy,
                cache_mode=CacheMode.ENABLED,
                magic=True,  # Enable all smart features
                simulate_user=True,
                remove_overlay_elements=True
            )
            
            # Process AI-extracted insights
            processed_result = await self._process_smart_extraction(result, url, extraction_goal)
            
            return processed_result
            
        except Exception as e:
            self.logger.error(f"Smart extraction failed for {url}: {e}")
            return {
                'url': url,
                'error': str(e),
                'extraction_goal': extraction_goal,
                'status': 'failed'
            }
    
    async def scrape_with_javascript_execution(
        self, 
        url: str, 
        javascript_code: str = "",
        wait_for_selector: str = "",
        wait_time: int = 3
    ) -> Dict[str, Any]:
        """
        Scrape dynamic content that requires JavaScript execution
        """
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # Default JavaScript for common dynamic content
            if not javascript_code:
                javascript_code = """
                // Wait for dynamic content to load
                setTimeout(() => {
                    // Scroll to load lazy content
                    window.scrollTo(0, document.body.scrollHeight);
                    
                    // Click "Load More" buttons if they exist
                    const loadMoreButtons = document.querySelectorAll('[class*="load"], [class*="more"], [data-load]');
                    loadMoreButtons.forEach(btn => btn.click());
                }, 1000);
                """
            
            result = await self.crawler.arun(
                url=url,
                js_code=javascript_code,
                wait_for=wait_for_selector,
                delay_before_return_html=wait_time,
                simulate_user=True,
                magic=True
            )
            
            return await self._process_crawl_result(result, url, "article", False)
            
        except Exception as e:
            self.logger.error(f"JavaScript scraping failed for {url}: {e}")
            return {'url': url, 'error': str(e), 'status': 'failed'}
    
    async def scrape_sitemap(self, sitemap_url: str, max_urls: int = 100) -> List[Dict[str, Any]]:
        """
        Scrape URLs from a sitemap
        """
        try:
            # First, scrape the sitemap
            sitemap_result = await self.scrape_url(sitemap_url, "basic")
            
            if sitemap_result.get('status') == 'failed':
                return []
            
            # Extract URLs from sitemap XML
            urls = self._extract_urls_from_sitemap(sitemap_result.get('html_content', ''))
            
            # Limit the number of URLs
            urls = urls[:max_urls]
            
            # Scrape all URLs from the sitemap
            return await self.scrape_multiple_urls(urls)
            
        except Exception as e:
            self.logger.error(f"Sitemap scraping failed: {e}")
            return []
    
    async def _process_crawl_result(
        self, 
        result, 
        url: str, 
        content_type: str, 
        use_llm: bool
    ) -> Dict[str, Any]:
        """Process and structure the crawling result"""
        
        processed = {
            'url': url,
            'scraped_at': datetime.utcnow().isoformat(),
            'status': 'success' if result.success else 'failed',
            'content_type': content_type
        }
        
        if result.success:
            # Basic extracted data
            processed.update({
                'html_content': result.html,
                'markdown_content': result.markdown,
                'cleaned_html': result.cleaned_html,
                'media': result.media,
                'links': result.links,
                'metadata': result.metadata
            })
            
            # Structured extracted data if available
            if result.extracted_content:
                try:
                    if isinstance(result.extracted_content, str):
                        extracted_data = json.loads(result.extracted_content)
                    else:
                        extracted_data = result.extracted_content
                    
                    processed['extracted_data'] = extracted_data
                except json.JSONDecodeError:
                    processed['extracted_text'] = result.extracted_content
            
            # Calculate content metrics
            processed['content_metrics'] = self._calculate_content_metrics(result)
            
            # SEO analysis
            processed['seo_analysis'] = self._analyze_seo_elements(result)
            
        else:
            processed['error'] = result.error_message if hasattr(result, 'error_message') else 'Unknown error'
        
        return processed
    
    async def _process_smart_extraction(self, result, url: str, extraction_goal: str) -> Dict[str, Any]:
        """Process AI-powered smart extraction results"""
        
        processed = {
            'url': url,
            'scraped_at': datetime.utcnow().isoformat(),
            'extraction_goal': extraction_goal,
            'status': 'success' if result.success else 'failed'
        }
        
        if result.success:
            # AI-extracted insights
            if result.extracted_content:
                try:
                    if isinstance(result.extracted_content, str):
                        ai_insights = json.loads(result.extracted_content)
                    else:
                        ai_insights = result.extracted_content
                    
                    processed['ai_insights'] = ai_insights
                except json.JSONDecodeError:
                    processed['ai_analysis'] = result.extracted_content
            
            # Include basic content data
            processed.update({
                'markdown_content': result.markdown,
                'metadata': result.metadata,
                'links': result.links,
                'media': result.media
            })
            
        else:
            processed['error'] = getattr(result, 'error_message', 'Smart extraction failed')
        
        return processed
    
    def _calculate_content_metrics(self, result) -> Dict[str, Any]:
        """Calculate comprehensive content metrics"""
        try:
            markdown = result.markdown or ""
            html = result.html or ""
            
            # Word count from markdown (more accurate than HTML)
            words = len(markdown.split())
            
            # Character count
            chars = len(markdown)
            
            # Estimated reading time (average 200 words per minute)
            reading_time = max(1, words // 200)
            
            # Count various elements from HTML
            import re
            
            # Count headings
            headings = len(re.findall(r'<h[1-6][^>]*>', html, re.IGNORECASE))
            
            # Count paragraphs
            paragraphs = len(re.findall(r'<p[^>]*>', html, re.IGNORECASE))
            
            # Count images
            images = len(result.media.get('images', [])) if result.media else 0
            
            # Count links
            internal_links = len([link for link in result.links.get('internal', [])]) if result.links else 0
            external_links = len([link for link in result.links.get('external', [])]) if result.links else 0
            
            return {
                'word_count': words,
                'character_count': chars,
                'reading_time_minutes': reading_time,
                'headings_count': headings,
                'paragraphs_count': paragraphs,
                'images_count': images,
                'internal_links_count': internal_links,
                'external_links_count': external_links,
                'content_density': words / max(1, paragraphs)  # Words per paragraph
            }
            
        except Exception as e:
            self.logger.error(f"Content metrics calculation failed: {e}")
            return {'error': 'Metrics calculation failed'}
    
    def _analyze_seo_elements(self, result) -> Dict[str, Any]:
        """Analyze SEO elements from the scraped content"""
        try:
            metadata = result.metadata or {}
            html = result.html or ""
            
            import re
            
            # Simple HTML parsing without BeautifulSoup
            
            # Title analysis
            title = metadata.get('title', '')
            title_length = len(title)
            
            # Meta description
            meta_description = metadata.get('description', '')
            meta_desc_length = len(meta_description)
            
            # Extract H1 tags using regex
            h1_pattern = r'<h1[^>]*>(.*?)</h1>'
            h1_tags = re.findall(h1_pattern, html, re.IGNORECASE | re.DOTALL)
            h1_tags = [re.sub(r'<[^>]+>', '', tag).strip() for tag in h1_tags]
            
            # Extract keywords from meta tags using regex
            keywords_pattern = r'<meta[^>]*name=["\']keywords["\'][^>]*content=["\']([^"\']*)["\']'
            keywords_match = re.search(keywords_pattern, html, re.IGNORECASE)
            keywords = keywords_match.group(1) if keywords_match else ''
            
            # Open Graph tags using regex
            og_pattern = r'<meta[^>]*property=["\'](og:[^"\']*)["\'][^>]*content=["\']([^"\']*)["\']'
            og_tags = {}
            for match in re.findall(og_pattern, html, re.IGNORECASE):
                og_tags[match[0]] = match[1]
            
            # Canonical URL using regex
            canonical_pattern = r'<link[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']*)["\']'
            canonical_match = re.search(canonical_pattern, html, re.IGNORECASE)
            canonical_url = canonical_match.group(1) if canonical_match else ''
            
            # Check for structured data
            structured_data_pattern = r'<script[^>]*type=["\']application/ld\+json["\']'
            has_structured_data = bool(re.search(structured_data_pattern, html, re.IGNORECASE))
            
            return {
                'title': {
                    'content': title,
                    'length': title_length,
                    'seo_friendly': 30 <= title_length <= 60
                },
                'meta_description': {
                    'content': meta_description,
                    'length': meta_desc_length,
                    'seo_friendly': 120 <= meta_desc_length <= 160
                },
                'h1_tags': h1_tags,
                'h1_count': len(h1_tags),
                'meta_keywords': keywords,
                'canonical_url': canonical_url,
                'open_graph': og_tags,
                'has_structured_data': has_structured_data
            }
            
        except Exception as e:
            self.logger.error(f"SEO analysis failed: {e}")
            return {'error': 'SEO analysis failed'}
    
    def _extract_urls_from_sitemap(self, sitemap_content: str) -> List[str]:
        """Extract URLs from sitemap XML content"""
        try:
            import re
            
            # Extract URLs from sitemap XML
            url_pattern = r'<loc>(.*?)</loc>'
            urls = re.findall(url_pattern, sitemap_content)
            
            # Filter out non-HTTP URLs and clean them
            clean_urls = []
            for url in urls:
                url = url.strip()
                if url.startswith(('http://', 'https://')):
                    clean_urls.append(url)
            
            return clean_urls
            
        except Exception as e:
            self.logger.error(f"Sitemap URL extraction failed: {e}")
            return []
    
    async def close(self):
        """Clean up resources"""
        try:
            if self.crawler and self.is_initialized:
                await self.crawler.aclose()
                self.is_initialized = False
                self.logger.info("Crawl4AI scraping service closed")
        except Exception as e:
            self.logger.error(f"Error closing scraping service: {e}")
    
    async def health_check(self) -> bool:
        """Check scraping service health"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # Test with a simple URL
            test_result = await self.scrape_url("https://httpbin.org/user-agent", "basic")
            return test_result.get('status') == 'success'
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
    
    def __del__(self):
        """Cleanup when service is destroyed"""
        try:
            if self.is_initialized:
                import asyncio
                asyncio.create_task(self.close())
        except:
            pass

# Maintain compatibility with existing code
ScrapingService = Crawl4AIScrapingService
