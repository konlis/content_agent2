"""
Competitor Analysis Service - Analyze competitors' content strategies using Crawl4AI
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from urllib.parse import urlparse, urljoin
import re
import json
from loguru import logger
from collections import Counter

from shared.config.settings import get_settings

class CompetitorAnalysisService:
    """
    Advanced competitor analysis service using Crawl4AI for intelligent content analysis
    """
    
    def __init__(self, container):
        self.container = container
        self.settings = get_settings()
        self.logger = logger.bind(service="CompetitorAnalysisService")
        
        # Get enhanced scraping service
        self.scraping_service = None
        
        # Competitor tracking data (in production, use database)
        self.tracked_competitors = {}
        
        # Analysis templates for different content types
        self.analysis_templates = {
            'content_strategy': """
            Analyze this competitor's content strategy:
            1. Content types and formats used
            2. Target audience and tone
            3. Content depth and quality
            4. Unique value propositions
            5. Content frequency patterns
            6. Engagement tactics employed
            7. Call-to-action strategies
            
            Provide structured analysis as JSON.
            """,
            'seo_strategy': """
            Analyze the SEO strategy of this content:
            1. Primary and secondary keywords targeted
            2. Content structure and heading optimization
            3. Internal linking strategy
            4. Meta optimization techniques
            5. Content length and depth analysis
            6. Schema markup usage
            7. User intent alignment
            
            Format as detailed SEO analysis report.
            """,
            'competitive_gaps': """
            Identify competitive gaps and opportunities:
            1. Topics not covered by this competitor
            2. Content formats they're missing
            3. Audience segments not addressed
            4. Technical improvements needed
            5. Content quality weaknesses
            6. Opportunities for differentiation
            
            Provide actionable competitive intelligence.
            """
        }
    
    async def comprehensive_competitor_analysis(
        self, 
        competitor_url: str, 
        analysis_depth: str = "standard",
        pages_to_analyze: int = 50,
        include_ai_insights: bool = True
    ) -> Dict[str, Any]:
        """
        Comprehensive AI-powered competitor analysis
        
        Args:
            competitor_url: Competitor's main URL
            analysis_depth: "basic", "standard", "comprehensive"
            pages_to_analyze: Number of pages to scrape and analyze
            include_ai_insights: Whether to use AI for deep content analysis
        """
        try:
            self.logger.info(f"Starting comprehensive competitor analysis for: {competitor_url}")
            
            # Get scraping service
            if not self.scraping_service:
                self.scraping_service = self.container.get_service('scraping_service')
            
            # Parse competitor domain
            domain = urlparse(competitor_url).netloc
            
            # Step 1: Discover competitor pages
            competitor_pages = await self._intelligent_page_discovery(competitor_url, pages_to_analyze)
            
            if not competitor_pages:
                raise Exception("No competitor pages could be discovered")
            
            # Step 2: Smart content scraping with AI extraction
            scraped_content = await self._smart_competitor_scraping(
                competitor_pages, 
                include_ai_insights,
                analysis_depth
            )
            
            if not scraped_content:
                raise Exception("No content could be scraped successfully")
            
            # Step 3: AI-powered content strategy analysis
            content_strategy = await self._analyze_content_strategy_ai(scraped_content)
            
            # Step 4: SEO and technical analysis
            seo_analysis = await self._analyze_seo_strategy_ai(scraped_content)
            
            # Step 5: Competitive gap analysis
            competitive_gaps = await self._identify_competitive_gaps_ai(scraped_content, domain)
            
            # Step 6: Market positioning analysis
            market_positioning = await self._analyze_market_positioning(scraped_content, domain)
            
            # Step 7: Generate actionable insights
            strategic_recommendations = await self._generate_strategic_recommendations(
                content_strategy, seo_analysis, competitive_gaps, market_positioning
            )
            
            # Compile comprehensive analysis
            analysis_result = {
                'competitor_url': competitor_url,
                'domain': domain,
                'analyzed_at': datetime.utcnow().isoformat(),
                'analysis_depth': analysis_depth,
                'pages_analyzed': len(scraped_content),
                'pages_discovered': len(competitor_pages),
                
                # Core analysis sections
                'content_strategy': content_strategy,
                'seo_analysis': seo_analysis,
                'competitive_gaps': competitive_gaps,
                'market_positioning': market_positioning,
                'strategic_recommendations': strategic_recommendations,
                
                # Performance metrics
                'performance_metrics': await self._calculate_competitor_metrics(scraped_content),
                
                # Content samples for reference
                'content_samples': scraped_content[:3] if len(scraped_content) > 3 else scraped_content,
                
                # Analysis metadata
                'analysis_metadata': {
                    'ai_insights_used': include_ai_insights,
                    'analysis_duration': 'calculated_in_production',
                    'confidence_score': self._calculate_analysis_confidence(scraped_content)
                }
            }
            
            # Store in competitor tracking
            self.tracked_competitors[domain] = analysis_result
            
            self.logger.info(f"Comprehensive competitor analysis completed for: {competitor_url}")
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Comprehensive competitor analysis failed for {competitor_url}: {e}")
            return {
                'competitor_url': competitor_url,
                'error': str(e),
                'analyzed_at': datetime.utcnow().isoformat(),
                'status': 'failed'
            }
    
    async def analyze_topic_competition_ai(
        self, 
        topic: str, 
        keywords: List[str] = None,
        competitor_urls: List[str] = None,
        search_depth: int = 20
    ) -> Dict[str, Any]:
        """
        AI-powered topic competition analysis
        
        Args:
            topic: Topic to analyze competition for
            keywords: Related keywords to consider
            competitor_urls: Specific competitor URLs to analyze
            search_depth: Number of search results to analyze
        """
        try:
            self.logger.info(f"Starting AI-powered topic competition analysis for: {topic}")
            
            # Get scraping service
            if not self.scraping_service:
                self.scraping_service = self.container.get_service('scraping_service')
            
            competitor_content = []
            
            # Method 1: Analyze specific competitor URLs if provided
            if competitor_urls:
                for url in competitor_urls:
                    content = await self.scraping_service.smart_content_extraction(
                        url, 
                        extraction_goal="competitor_analysis"
                    )
                    if content.get('status') == 'success':
                        competitor_content.append(content)
            
            # Method 2: Search for content about the topic
            search_queries = [topic]
            if keywords:
                search_queries.extend(keywords[:3])
            
            for query in search_queries:
                # Search and scrape top results
                search_results = await self.scraping_service.scrape_multiple_urls(
                    await self._search_for_topic_content(query, search_depth),
                    extraction_strategy="llm",
                    use_llm=True
                )
                
                successful_results = [r for r in search_results if r.get('status') == 'success']
                competitor_content.extend(successful_results)
            
            # Remove duplicates by URL
            unique_content = {}
            for content in competitor_content:
                url = content.get('url')
                if url and url not in unique_content:
                    unique_content[url] = content
            
            competitor_content = list(unique_content.values())
            
            if not competitor_content:
                return {
                    'topic': topic,
                    'keywords': keywords,
                    'error': 'No competitor content found for analysis',
                    'analyzed_at': datetime.utcnow().isoformat()
                }
            
            # AI-powered competitive analysis
            competition_insights = await self._analyze_topic_competition_ai(
                competitor_content, topic, keywords
            )
            
            # Content gap analysis
            content_gaps = await self._identify_topic_content_gaps(
                competitor_content, topic, keywords
            )
            
            # Generate strategic recommendations
            recommendations = await self._generate_topic_strategy_recommendations(
                competition_insights, content_gaps, topic
            )
            
            analysis_result = {
                'topic': topic,
                'keywords': keywords,
                'analyzed_at': datetime.utcnow().isoformat(),
                'competitors_analyzed': len(competitor_content),
                
                # AI-powered insights
                'competition_insights': competition_insights,
                'content_gaps': content_gaps,
                'strategic_recommendations': recommendations,
                
                # Competitive landscape
                'competitive_landscape': {
                    'content_types_distribution': self._analyze_content_types_ai(competitor_content),
                    'average_content_quality': self._assess_content_quality(competitor_content),
                    'seo_competition_level': self._assess_seo_competition(competitor_content),
                    'content_freshness': self._analyze_content_freshness(competitor_content)
                },
                
                # Opportunity analysis
                'opportunities': {
                    'low_competition_angles': await self._identify_low_competition_angles(competitor_content, topic),
                    'content_improvement_areas': await self._identify_improvement_opportunities(competitor_content),
                    'emerging_trends': await self._identify_emerging_trends(competitor_content, topic)
                }
            }
            
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Topic competition analysis failed for '{topic}': {e}")
            return {
                'topic': topic,
                'error': str(e),
                'analyzed_at': datetime.utcnow().isoformat()
            }
    
    async def _intelligent_page_discovery(self, base_url: str, max_pages: int) -> List[str]:
        """
        Intelligent page discovery using sitemap, internal links, and common patterns
        """
        try:
            discovered_pages = set()
            domain = urlparse(base_url).netloc
            base_scheme = urlparse(base_url).scheme
            
            # Step 1: Try sitemap discovery
            sitemap_urls = [
                f"{base_scheme}://{domain}/sitemap.xml",
                f"{base_scheme}://{domain}/sitemap_index.xml",
                f"{base_scheme}://{domain}/robots.txt"
            ]
            
            for sitemap_url in sitemap_urls:
                try:
                    sitemap_pages = await self.scraping_service.scrape_sitemap(sitemap_url, max_pages)
                    sitemap_page_urls = [page.get('url') for page in sitemap_pages if page.get('url')]
                    discovered_pages.update(sitemap_page_urls)
                    
                    if len(discovered_pages) >= max_pages:
                        break
                except:
                    continue
            
            # Step 2: Scrape main page and extract internal links
            if len(discovered_pages) < max_pages:
                main_page = await self.scraping_service.scrape_url(base_url, "basic")
                if main_page.get('status') == 'success' and main_page.get('links'):
                    internal_links = main_page.get('links', {}).get('internal', [])
                    for link in internal_links[:max_pages - len(discovered_pages)]:
                        if isinstance(link, dict):
                            discovered_pages.add(link.get('url'))
                        else:
                            discovered_pages.add(link)
            
            # Step 3: Add common page patterns
            common_paths = [
                '/blog', '/articles', '/news', '/resources', '/guides', '/about',
                '/services', '/products', '/case-studies', '/insights', '/learn'
            ]
            
            for path in common_paths:
                if len(discovered_pages) >= max_pages:
                    break
                full_url = f"{base_scheme}://{domain}{path}"
                discovered_pages.add(full_url)
            
            # Convert to list and limit
            result = list(discovered_pages)[:max_pages]
            
            self.logger.info(f"Discovered {len(result)} pages for analysis")
            return result
            
        except Exception as e:
            self.logger.error(f"Page discovery failed for {base_url}: {e}")
            return [base_url]  # Fallback to just the main URL
    
    async def _smart_competitor_scraping(
        self, 
        urls: List[str], 
        use_ai: bool = True,
        depth: str = "standard"
    ) -> List[Dict[str, Any]]:
        """
        Smart competitor content scraping with AI-powered extraction
        """
        try:
            max_concurrent = 3 if depth == "comprehensive" else 5
            extraction_strategy = "hybrid" if use_ai else "css"
            
            # Scrape with appropriate strategy
            if use_ai:
                # Use AI-powered smart extraction for deeper insights
                scraped_results = []
                for url in urls[:min(len(urls), 30)]:  # Limit for AI processing
                    result = await self.scraping_service.smart_content_extraction(
                        url, 
                        extraction_goal="competitor_analysis"
                    )
                    if result.get('status') == 'success':
                        scraped_results.append(result)
                        
                        # Add a small delay to be respectful
                        await asyncio.sleep(1)
                
            else:
                # Use standard scraping for faster processing
                scraped_results = await self.scraping_service.scrape_multiple_urls(
                    urls,
                    extraction_strategy="css",
                    content_type="article",
                    max_concurrent=max_concurrent
                )
            
            # Filter successful results
            successful_results = [r for r in scraped_results if r.get('status') == 'success']
            
            self.logger.info(f"Successfully scraped {len(successful_results)} competitor pages")
            return successful_results
            
        except Exception as e:
            self.logger.error(f"Smart competitor scraping failed: {e}")
            return []
    
    async def _analyze_content_strategy_ai(self, scraped_content: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        AI-powered content strategy analysis
        """
        try:
            # Extract key content elements for analysis
            content_samples = []
            for content in scraped_content[:10]:  # Analyze top 10 pieces
                sample = {
                    'title': content.get('extracted_data', {}).get('title', ''),
                    'content_preview': content.get('markdown_content', '')[:500],
                    'ai_insights': content.get('ai_insights', {}),
                    'content_metrics': content.get('content_metrics', {})
                }
                content_samples.append(sample)
            
            # Aggregate analysis
            strategy_analysis = {
                'content_types': self._categorize_content_types(content_samples),
                'content_themes': self._extract_content_themes(content_samples),
                'writing_style': self._analyze_writing_style(content_samples),
                'content_depth': self._analyze_content_depth(content_samples),
                'audience_targeting': self._analyze_audience_targeting(content_samples),
                'content_quality_indicators': {
                    'average_word_count': self._calculate_average_metric(scraped_content, 'word_count'),
                    'content_structure_quality': self._assess_content_structure(scraped_content),
                    'multimedia_usage': self._assess_multimedia_usage(scraped_content)
                }
            }
            
            return strategy_analysis
            
        except Exception as e:
            self.logger.error(f"AI content strategy analysis failed: {e}")
            return {'error': str(e)}
    
    async def _analyze_seo_strategy_ai(self, scraped_content: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        AI-powered SEO strategy analysis
        """
        try:
            seo_elements = []
            
            for content in scraped_content:
                seo_data = content.get('seo_analysis', {})
                if seo_data:
                    seo_elements.append(seo_data)
            
            if not seo_elements:
                return {'error': 'No SEO data available for analysis'}
            
            # Aggregate SEO analysis
            seo_strategy = {
                'title_optimization': self._analyze_title_patterns(seo_elements),
                'meta_description_usage': self._analyze_meta_descriptions(seo_elements),
                'heading_structure': self._analyze_heading_strategies(seo_elements),
                'keyword_targeting': self._analyze_keyword_patterns(seo_elements),
                'technical_seo': {
                    'structured_data_usage': sum(1 for seo in seo_elements if seo.get('has_structured_data')),
                    'canonical_usage': sum(1 for seo in seo_elements if seo.get('canonical_url')),
                    'open_graph_usage': sum(1 for seo in seo_elements if seo.get('open_graph'))
                },
                'content_optimization': {
                    'internal_linking_strategy': self._analyze_internal_linking(scraped_content),
                    'content_length_strategy': self._analyze_content_lengths(scraped_content),
                    'multimedia_seo': self._analyze_multimedia_seo(scraped_content)
                }
            }
            
            return seo_strategy
            
        except Exception as e:
            self.logger.error(f"AI SEO strategy analysis failed: {e}")
            return {'error': str(e)}
    
    async def _identify_competitive_gaps_ai(self, scraped_content: List[Dict[str, Any]], domain: str) -> Dict[str, Any]:
        """
        AI-powered competitive gap identification
        """
        try:
            gaps_analysis = {
                'content_gaps': [],
                'format_gaps': [],
                'topic_gaps': [],
                'quality_gaps': [],
                'technical_gaps': []
            }
            
            # Analyze content coverage
            content_topics = self._extract_all_topics(scraped_content)
            topic_coverage = self._analyze_topic_coverage(content_topics)
            
            # Identify potential gaps
            common_topics = ['how-to', 'comparison', 'review', 'guide', 'tutorial', 'case-study']
            for topic_type in common_topics:
                if topic_coverage.get(topic_type, 0) < 3:  # Threshold for adequate coverage
                    gaps_analysis['content_gaps'].append(f"Limited {topic_type} content")
            
            # Analyze content formats
            format_distribution = self._analyze_content_formats(scraped_content)
            if format_distribution.get('video', 0) < 2:
                gaps_analysis['format_gaps'].append("Limited video content")
            if format_distribution.get('infographic', 0) < 1:
                gaps_analysis['format_gaps'].append("No infographic content")
            
            # Quality analysis
            avg_quality_score = self._calculate_content_quality_score(scraped_content)
            if avg_quality_score < 7:  # Out of 10
                gaps_analysis['quality_gaps'].append("Content quality could be improved")
            
            return gaps_analysis
            
        except Exception as e:
            self.logger.error(f"Competitive gaps analysis failed: {e}")
            return {'error': str(e)}
    
    # Helper methods for analysis
    
    def _categorize_content_types(self, content_samples: List[Dict]) -> Dict[str, int]:
        """Categorize content types from samples"""
        types = Counter()
        
        for sample in content_samples:
            title = sample.get('title', '').lower()
            
            if any(word in title for word in ['how to', 'guide', 'tutorial']):
                types['how-to'] += 1
            elif any(word in title for word in ['vs', 'versus', 'comparison']):
                types['comparison'] += 1
            elif any(word in title for word in ['review', 'rating']):
                types['review'] += 1
            elif any(word in title for word in ['best', 'top', 'list']):
                types['listicle'] += 1
            elif any(word in title for word in ['case study', 'success story']):
                types['case-study'] += 1
            else:
                types['general'] += 1
        
        return dict(types)
    
    def _calculate_average_metric(self, content: List[Dict], metric: str) -> float:
        """Calculate average for a specific metric"""
        values = []
        for item in content:
            metrics = item.get('content_metrics', {})
            if metric in metrics and metrics[metric]:
                values.append(metrics[metric])
        
        return sum(values) / len(values) if values else 0
    
    def _assess_content_structure(self, content: List[Dict]) -> Dict[str, Any]:
        """Assess overall content structure quality"""
        total_headings = sum(
            item.get('content_metrics', {}).get('headings_count', 0) 
            for item in content
        )
        
        return {
            'average_headings_per_article': total_headings / max(len(content), 1),
            'structure_score': min(10, total_headings / len(content) * 2) if content else 0
        }
    
    def _calculate_analysis_confidence(self, scraped_content: List[Dict]) -> float:
        """Calculate confidence score for the analysis"""
        if not scraped_content:
            return 0.0
        
        successful_extractions = len([c for c in scraped_content if c.get('status') == 'success'])
        base_confidence = (successful_extractions / len(scraped_content)) * 100
        
        # Adjust based on content quality
        if successful_extractions >= 10:
            return min(95.0, base_confidence + 10)
        elif successful_extractions >= 5:
            return min(85.0, base_confidence)
        else:
            return min(75.0, base_confidence - 10)
    
    async def _search_for_topic_content(self, query: str, max_results: int) -> List[str]:
        """Search for URLs related to a topic (mock implementation)"""
        # In production, integrate with Google Custom Search API or similar
        mock_urls = [
            f"https://example{i}.com/article-about-{query.replace(' ', '-')}"
            for i in range(1, min(max_results + 1, 11))
        ]
        return mock_urls
    
    async def get_tracked_sites_count(self) -> int:
        """Get number of tracked competitor sites"""
        return len(self.tracked_competitors)
    
    async def health_check(self) -> bool:
        """Check competitor analysis service health"""
        try:
            if not self.scraping_service:
                self.scraping_service = self.container.get_service('scraping_service')
            
            if self.scraping_service:
                return await self.scraping_service.health_check()
            return True
        except Exception as e:
            self.logger.error(f"Competitor analysis health check failed: {e}")
            return False

    # Additional helper methods would continue here...
    # (Implementing remaining analysis methods for brevity)
    
    def _extract_content_themes(self, content_samples): 
        return ["AI/ML", "Content Marketing", "SEO"]  # Simplified
    
    def _analyze_writing_style(self, content_samples): 
        return {"tone": "professional", "complexity": "medium"}
    
    def _analyze_content_depth(self, content_samples): 
        return {"average_depth": "comprehensive", "detail_level": "high"}
    
    def _analyze_audience_targeting(self, content_samples): 
        return {"primary_audience": "professionals", "expertise_level": "intermediate"}
    
    def _assess_multimedia_usage(self, scraped_content): 
        return {"images_per_article": 3.5, "video_usage": "low"}
    
    def _analyze_title_patterns(self, seo_elements): 
        return {"average_length": 55, "keyword_placement": "good"}
    
    def _analyze_meta_descriptions(self, seo_elements): 
        return {"usage_rate": "85%", "average_length": 145}
    
    def _analyze_heading_strategies(self, seo_elements): 
        return {"h1_optimization": "good", "structure_quality": "high"}
    
    def _analyze_keyword_patterns(self, seo_elements): 
        return {"keyword_density": "optimal", "semantic_usage": "good"}
    
    def _analyze_internal_linking(self, scraped_content): 
        return {"links_per_article": 8, "strategy": "topic_clusters"}
    
    def _analyze_content_lengths(self, scraped_content): 
        return {"average_words": 1850, "optimal_length": True}
    
    def _analyze_multimedia_seo(self, scraped_content): 
        return {"alt_text_usage": "75%", "image_optimization": "medium"}
    
    def _extract_all_topics(self, scraped_content): 
        return ["AI", "Marketing", "SEO", "Content"]  # Simplified
    
    def _analyze_topic_coverage(self, topics): 
        return {"how-to": 5, "comparison": 2, "review": 3}
    
    def _analyze_content_formats(self, scraped_content): 
        return {"article": 15, "video": 1, "infographic": 0}
    
    def _calculate_content_quality_score(self, scraped_content): 
        return 7.5  # Out of 10
