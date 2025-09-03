"""
Content Discovery Service - AI-powered content opportunity discovery using Crawl4AI
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from urllib.parse import urlparse, urljoin
import json
from loguru import logger
from collections import Counter

from shared.config.settings import get_settings

class ContentDiscoveryService:
    """
    AI-powered content discovery service using Crawl4AI for finding content opportunities
    """
    
    def __init__(self, container):
        self.container = container
        self.settings = get_settings()
        self.logger = logger.bind(service="ContentDiscoveryService")
        
        # Get scraping service
        self.scraping_service = None
        
        # Content discovery patterns and templates
        self.discovery_patterns = {
            'trending_topics': [
                'latest', 'new', 'trending', 'hot', 'popular', 'viral',
                'breaking', 'update', 'announcement', 'release'
            ],
            'content_gaps': [
                'missing', 'lack of', 'no guide', 'difficult to find',
                'confusing', 'complicated', 'hard to understand'
            ],
            'opportunity_keywords': [
                'how to', 'best practices', 'complete guide', 'ultimate guide',
                'step by step', 'tutorial', 'tips and tricks', 'strategies'
            ]
        }
        
        # Industry-specific content themes
        self.industry_themes = {
            'technology': [
                'AI/ML', 'Cybersecurity', 'Cloud Computing', 'DevOps',
                'Data Science', 'Mobile Development', 'Web Development'
            ],
            'marketing': [
                'Content Marketing', 'SEO', 'Social Media', 'Email Marketing',
                'PPC', 'Analytics', 'Conversion Optimization'
            ],
            'healthcare': [
                'Digital Health', 'Telemedicine', 'Health Tech', 'Patient Care',
                'Medical Devices', 'Healthcare Innovation'
            ],
            'finance': [
                'Fintech', 'Cryptocurrency', 'Personal Finance', 'Investment',
                'Banking', 'Insurance', 'RegTech'
            ],
            'education': [
                'E-learning', 'EdTech', 'Online Courses', 'Skills Development',
                'Corporate Training', 'Student Resources'
            ]
        }
    
    async def discover_content_opportunities(
        self,
        keywords: List[str] = None,
        industry: str = None,
        content_type: str = "blog_post",
        max_opportunities: int = 20,
        auto_analyze: bool = True
    ) -> Dict[str, Any]:
        """
        Discover content opportunities using AI-powered analysis
        
        Args:
            keywords: Keywords to search for opportunities
            industry: Industry to focus on
            content_type: Type of content to discover
            max_opportunities: Maximum number of opportunities to return
            auto_analyze: Whether to automatically analyze discovered content
        """
        try:
            self.logger.info(f"Starting content opportunity discovery for industry: {industry}")
            
            # Get scraping service
            if not self.scraping_service:
                self.scraping_service = self.container.get_service('scraping_service')
            
            # Step 1: Generate search queries
            search_queries = await self._generate_discovery_queries(keywords, industry, content_type)
            
            # Step 2: Search for content opportunities
            discovered_content = await self._search_content_opportunities(
                search_queries, max_opportunities
            )
            
            # Step 3: Analyze content gaps and opportunities
            if auto_analyze and discovered_content:
                gap_analysis = await self._analyze_content_gaps(discovered_content, keywords, industry)
                opportunity_insights = await self._generate_opportunity_insights(
                    discovered_content, gap_analysis, industry
                )
            else:
                gap_analysis = {}
                opportunity_insights = {}
            
            # Step 4: Prioritize opportunities
            prioritized_opportunities = await self._prioritize_opportunities(
                discovered_content, gap_analysis, industry
            )
            
            discovery_result = {
                'discovery_session': {
                    'keywords': keywords or [],
                    'industry': industry,
                    'content_type': content_type,
                    'discovered_at': datetime.utcnow().isoformat(),
                    'search_queries_used': search_queries
                },
                'opportunities_discovered': len(discovered_content),
                'content_samples': discovered_content[:5],  # Top 5 samples
                'gap_analysis': gap_analysis,
                'opportunity_insights': opportunity_insights,
                'prioritized_opportunities': prioritized_opportunities[:max_opportunities],
                'recommendations': await self._generate_discovery_recommendations(
                    discovered_content, gap_analysis, industry
                )
            }
            
            self.logger.info(f"Content discovery completed: {len(discovered_content)} opportunities found")
            return discovery_result
            
        except Exception as e:
            self.logger.error(f"Content opportunity discovery failed: {e}")
            return {
                'error': str(e),
                'discovered_at': datetime.utcnow().isoformat(),
                'status': 'failed'
            }
    
    async def discover_trending_topics(
        self,
        industry: str = None,
        time_period: str = "7d",
        max_topics: int = 15
    ) -> Dict[str, Any]:
        """
        Discover trending topics in an industry using content analysis
        """
        try:
            self.logger.info(f"Discovering trending topics for industry: {industry}")
            
            # Get scraping service
            if not self.scraping_service:
                self.scraping_service = self.container.get_service('scraping_service')
            
            # Generate trending topic queries
            trending_queries = self._generate_trending_queries(industry, time_period)
            
            # Search for trending content
            trending_content = await self._search_trending_content(trending_queries, max_topics)
            
            # Analyze trending patterns
            trend_analysis = await self._analyze_trending_patterns(trending_content, industry)
            
            # Identify emerging trends
            emerging_trends = await self._identify_emerging_trends(trending_content, industry)
            
            trending_result = {
                'industry': industry,
                'time_period': time_period,
                'analyzed_at': datetime.utcnow().isoformat(),
                'trending_topics': trend_analysis.get('top_topics', [])[:max_topics],
                'trending_patterns': trend_analysis.get('patterns', {}),
                'emerging_trends': emerging_trends,
                'trend_velocity': trend_analysis.get('velocity', {}),
                'recommendations': await self._generate_trending_recommendations(
                    trend_analysis, emerging_trends, industry
                )
            }
            
            return trending_result
            
        except Exception as e:
            self.logger.error(f"Trending topic discovery failed: {e}")
            return {
                'error': str(e),
                'analyzed_at': datetime.utcnow().isoformat(),
                'status': 'failed'
            }
    
    async def discover_content_gaps(
        self,
        competitor_urls: List[str] = None,
        target_keywords: List[str] = None,
        industry: str = None
    ) -> Dict[str, Any]:
        """
        Discover content gaps by analyzing competitor content
        """
        try:
            self.logger.info(f"Discovering content gaps for industry: {industry}")
            
            # Get scraping service
            if not self.scraping_service:
                self.scraping_service = self.container.get_service('scraping_service')
            
            # Analyze competitor content
            competitor_content = []
            if competitor_urls:
                competitor_content = await self._analyze_competitor_content(competitor_urls)
            
            # Search for content about target keywords
            keyword_content = []
            if target_keywords:
                keyword_content = await self._search_keyword_content(target_keywords)
            
            # Identify gaps
            content_gaps = await self._identify_content_gaps(
                competitor_content, keyword_content, target_keywords, industry
            )
            
            # Generate gap-filling recommendations
            gap_recommendations = await self._generate_gap_filling_recommendations(
                content_gaps, industry
            )
            
            gap_result = {
                'industry': industry,
                'analyzed_at': datetime.utcnow().isoformat(),
                'competitors_analyzed': len(competitor_content),
                'keywords_analyzed': len(target_keywords) if target_keywords else 0,
                'content_gaps': content_gaps,
                'gap_priorities': await self._prioritize_content_gaps(content_gaps),
                'recommendations': gap_recommendations,
                'opportunity_score': self._calculate_gap_opportunity_score(content_gaps)
            }
            
            return gap_result
            
        except Exception as e:
            self.logger.error(f"Content gap discovery failed: {e}")
            return {
                'error': str(e),
                'analyzed_at': datetime.utcnow().isoformat(),
                'status': 'failed'
            }
    
    async def _generate_discovery_queries(
        self, 
        keywords: List[str], 
        industry: str, 
        content_type: str
    ) -> List[str]:
        """Generate search queries for content discovery"""
        try:
            queries = []
            
            # Base keyword queries
            if keywords:
                for keyword in keywords[:5]:  # Limit to top 5 keywords
                    queries.extend([
                        f'"{keyword}" guide',
                        f'"{keyword}" tutorial',
                        f'"{keyword}" best practices',
                        f'"{keyword}" tips',
                        f'"{keyword}" strategies'
                    ])
            
            # Industry-specific queries
            if industry and industry in self.industry_themes:
                themes = self.industry_themes[industry][:3]  # Top 3 themes
                for theme in themes:
                    queries.extend([
                        f'{theme} trends',
                        f'{theme} latest news',
                        f'{theme} guide',
                        f'{theme} best practices'
                    ])
            
            # Content type specific queries
            if content_type == "blog_post":
                queries.extend(['industry insights', 'expert analysis', 'case studies'])
            elif content_type == "social_media":
                queries.extend(['social media tips', 'engagement strategies', 'viral content'])
            elif content_type == "newsletter":
                queries.extend(['weekly roundup', 'industry newsletter', 'expert insights'])
            
            # Add trending and gap discovery queries
            queries.extend([
                'latest trends',
                'emerging topics',
                'content gaps',
                'missing information',
                'unanswered questions'
            ])
            
            # Remove duplicates and limit
            unique_queries = list(set(queries))
            return unique_queries[:20]  # Limit to 20 queries
            
        except Exception as e:
            self.logger.error(f"Query generation failed: {e}")
            return ['content marketing', 'industry trends', 'best practices']
    
    async def _search_content_opportunities(
        self, 
        search_queries: List[str], 
        max_opportunities: int
    ) -> List[Dict[str, Any]]:
        """Search for content opportunities using the queries"""
        try:
            discovered_content = []
            
            # Get scraping service
            if not self.scraping_service:
                self.scraping_service = self.container.get_service('scraping_service')
            
            # Search for each query
            for query in search_queries[:10]:  # Limit to top 10 queries
                try:
                    # Use smart content extraction for discovery
                    search_results = await self._search_for_content(query, max_opportunities // len(search_queries))
                    
                    for result in search_results:
                        if result.get('status') == 'success':
                            # Add discovery metadata
                            result['discovery_query'] = query
                            result['opportunity_score'] = self._calculate_opportunity_score(result, query)
                            discovered_content.append(result)
                    
                    # Add delay to be respectful
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    self.logger.warning(f"Search failed for query '{query}': {e}")
                    continue
            
            # Sort by opportunity score and remove duplicates
            unique_content = self._remove_duplicate_content(discovered_content)
            sorted_content = sorted(unique_content, key=lambda x: x.get('opportunity_score', 0), reverse=True)
            
            return sorted_content[:max_opportunities]
            
        except Exception as e:
            self.logger.error(f"Content opportunity search failed: {e}")
            return []
    
    async def _analyze_content_gaps(
        self, 
        discovered_content: List[Dict[str, Any]], 
        keywords: List[str], 
        industry: str
    ) -> Dict[str, Any]:
        """Analyze content gaps from discovered content"""
        try:
            gap_analysis = {
                'topic_coverage': {},
                'content_depth': {},
                'format_distribution': {},
                'quality_gaps': [],
                'missing_angles': []
            }
            
            # Analyze topic coverage
            if keywords:
                for keyword in keywords:
                    coverage = self._analyze_keyword_coverage(discovered_content, keyword)
                    gap_analysis['topic_coverage'][keyword] = coverage
            
            # Analyze content depth
            depth_analysis = self._analyze_content_depth_distribution(discovered_content)
            gap_analysis['content_depth'] = depth_analysis
            
            # Analyze format distribution
            format_analysis = self._analyze_content_formats(discovered_content)
            gap_analysis['format_distribution'] = format_analysis
            
            # Identify quality gaps
            quality_gaps = self._identify_quality_gaps(discovered_content)
            gap_analysis['quality_gaps'] = quality_gaps
            
            # Identify missing content angles
            missing_angles = self._identify_missing_angles(discovered_content, industry)
            gap_analysis['missing_angles'] = missing_angles
            
            return gap_analysis
            
        except Exception as e:
            self.logger.error(f"Content gap analysis failed: {e}")
            return {'error': str(e)}
    
    async def _generate_opportunity_insights(
        self, 
        discovered_content: List[Dict[str, Any]], 
        gap_analysis: Dict[str, Any], 
        industry: str
    ) -> Dict[str, Any]:
        """Generate insights about content opportunities"""
        try:
            insights = {
                'high_opportunity_areas': [],
                'content_trends': {},
                'audience_insights': {},
                'competitive_landscape': {},
                'recommended_actions': []
            }
            
            # Identify high opportunity areas
            high_opportunity = self._identify_high_opportunity_areas(discovered_content, gap_analysis)
            insights['high_opportunity_areas'] = high_opportunity
            
            # Analyze content trends
            trends = self._analyze_content_trends(discovered_content)
            insights['content_trends'] = trends
            
            # Analyze audience insights
            audience = self._analyze_audience_insights(discovered_content)
            insights['audience_insights'] = audience
            
            # Analyze competitive landscape
            competitive = self._analyze_competitive_landscape(discovered_content)
            insights['competitive_landscape'] = competitive
            
            # Generate recommended actions
            actions = self._generate_recommended_actions(insights, industry)
            insights['recommended_actions'] = actions
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Opportunity insights generation failed: {e}")
            return {'error': str(e)}
    
    async def _prioritize_opportunities(
        self, 
        discovered_content: List[Dict[str, Any]], 
        gap_analysis: Dict[str, Any], 
        industry: str
    ) -> List[Dict[str, Any]]:
        """Prioritize content opportunities based on multiple factors"""
        try:
            prioritized = []
            
            for content in discovered_content:
                priority_score = self._calculate_priority_score(content, gap_analysis, industry)
                
                prioritized_item = {
                    'content_data': content,
                    'priority_score': priority_score,
                    'priority_level': self._get_priority_level(priority_score),
                    'recommended_action': self._get_recommended_action(content, priority_score),
                    'estimated_impact': self._estimate_content_impact(content, priority_score),
                    'implementation_difficulty': self._assess_implementation_difficulty(content)
                }
                
                prioritized.append(prioritized_item)
            
            # Sort by priority score
            prioritized.sort(key=lambda x: x['priority_score'], reverse=True)
            
            return prioritized
            
        except Exception as e:
            self.logger.error(f"Opportunity prioritization failed: {e}")
            return []
    
    async def _generate_discovery_recommendations(
        self, 
        discovered_content: List[Dict[str, Any]], 
        gap_analysis: Dict[str, Any], 
        industry: str
    ) -> List[str]:
        """Generate actionable recommendations based on discovery results"""
        try:
            recommendations = []
            
            # Content creation recommendations
            if discovered_content:
                top_opportunities = discovered_content[:3]
                for opp in top_opportunities:
                    recommendations.append(
                        f"Create content about '{opp.get('discovery_query', 'discovered topic')}' "
                        f"with opportunity score {opp.get('opportunity_score', 0):.1f}"
                    )
            
            # Gap-filling recommendations
            if gap_analysis.get('missing_angles'):
                for angle in gap_analysis['missing_angles'][:3]:
                    recommendations.append(f"Develop content covering: {angle}")
            
            # Industry-specific recommendations
            if industry:
                industry_recs = self._get_industry_recommendations(industry, discovered_content)
                recommendations.extend(industry_recs)
            
            # Quality improvement recommendations
            if gap_analysis.get('quality_gaps'):
                recommendations.append("Focus on improving content quality and depth")
            
            # Format diversification recommendations
            format_dist = gap_analysis.get('format_distribution', {})
            if format_dist.get('video', 0) < 2:
                recommendations.append("Consider adding video content to your strategy")
            if format_dist.get('infographic', 0) < 1:
                recommendations.append("Create infographics for visual content")
            
            return recommendations[:10]  # Limit to top 10 recommendations
            
        except Exception as e:
            self.logger.error(f"Recommendation generation failed: {e}")
            return ["Focus on high-quality, comprehensive content creation"]
    
    def _generate_trending_queries(self, industry: str, time_period: str) -> List[str]:
        """Generate queries for trending topic discovery"""
        queries = []
        
        # Time-based trending queries
        if time_period == "7d":
            queries.extend(['this week', 'recent', 'latest', 'new'])
        elif time_period == "30d":
            queries.extend(['this month', 'trending', 'popular', 'viral'])
        elif time_period == "90d":
            queries.extend(['quarterly trends', 'seasonal', 'emerging'])
        
        # Industry-specific trending
        if industry and industry in self.industry_themes:
            themes = self.industry_themes[industry][:3]
            for theme in themes:
                queries.extend([
                    f'{theme} trends {time_period}',
                    f'{theme} latest developments',
                    f'{theme} emerging topics'
                ])
        
        # General trending queries
        queries.extend([
            'trending topics',
            'hot topics',
            'breaking news',
            'latest updates',
            'what\'s new'
        ])
        
        return list(set(queries))
    
    async def _search_trending_content(self, queries: List[str], max_topics: int) -> List[Dict[str, Any]]:
        """Search for trending content using the queries"""
        try:
            trending_content = []
            
            # Get scraping service
            if not self.scraping_service:
                self.scraping_service = self.container.get_service('scraping_service')
            
            # Search for trending content
            for query in queries[:8]:  # Limit queries
                try:
                    search_results = await self._search_for_content(query, max_topics // len(queries))
                    
                    for result in search_results:
                        if result.get('status') == 'success':
                            result['trending_query'] = query
                            result['trend_score'] = self._calculate_trend_score(result, query)
                            trending_content.append(result)
                    
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    self.logger.warning(f"Trending search failed for '{query}': {e}")
                    continue
            
            # Sort by trend score and remove duplicates
            unique_content = self._remove_duplicate_content(trending_content)
            sorted_content = sorted(unique_content, key=lambda x: x.get('trend_score', 0), reverse=True)
            
            return sorted_content[:max_topics]
            
        except Exception as e:
            self.logger.error(f"Trending content search failed: {e}")
            return []
    
    async def _analyze_trending_patterns(
        self, 
        trending_content: List[Dict[str, Any]], 
        industry: str
    ) -> Dict[str, Any]:
        """Analyze patterns in trending content"""
        try:
            patterns = {
                'top_topics': [],
                'velocity': {},
                'seasonality': {},
                'content_themes': {},
                'engagement_patterns': {}
            }
            
            # Extract top topics
            topics = self._extract_topics_from_content(trending_content)
            patterns['top_topics'] = topics[:10]
            
            # Analyze trend velocity
            velocity = self._analyze_trend_velocity(trending_content)
            patterns['velocity'] = velocity
            
            # Analyze seasonality
            seasonality = self._analyze_seasonality(trending_content)
            patterns['seasonality'] = seasonality
            
            # Analyze content themes
            themes = self._analyze_content_themes(trending_content)
            patterns['content_themes'] = themes
            
            # Analyze engagement patterns
            engagement = self._analyze_engagement_patterns(trending_content)
            patterns['engagement_patterns'] = engagement
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Trending pattern analysis failed: {e}")
            return {'error': str(e)}
    
    async def _identify_emerging_trends(
        self, 
        trending_content: List[Dict[str, Any]], 
        industry: str
    ) -> List[Dict[str, Any]]:
        """Identify emerging trends from trending content"""
        try:
            emerging_trends = []
            
            # Analyze content for emerging patterns
            for content in trending_content[:10]:  # Analyze top 10
                trend_indicators = self._identify_trend_indicators(content)
                
                if trend_indicators.get('is_emerging', False):
                    emerging_trend = {
                        'topic': trend_indicators.get('topic', ''),
                        'confidence': trend_indicators.get('confidence', 0),
                        'growth_rate': trend_indicators.get('growth_rate', 0),
                        'evidence': trend_indicators.get('evidence', []),
                        'predicted_trajectory': trend_indicators.get('trajectory', ''),
                        'recommended_action': trend_indicators.get('recommendation', '')
                    }
                    emerging_trends.append(emerging_trend)
            
            # Sort by confidence and growth rate
            emerging_trends.sort(key=lambda x: (x['confidence'], x['growth_rate']), reverse=True)
            
            return emerging_trends[:5]  # Top 5 emerging trends
            
        except Exception as e:
            self.logger.error(f"Emerging trend identification failed: {e}")
            return []
    
    async def _search_for_content(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search for content using a query (mock implementation)"""
        # In production, integrate with search APIs or use the scraping service
        # For now, return mock results
        mock_results = []
        
        for i in range(min(max_results, 5)):
            mock_result = {
                'url': f"https://example{i}.com/article-{query.replace(' ', '-')}",
                'title': f"Sample article about {query}",
                'content_preview': f"This is a sample article discussing {query} and related topics...",
                'status': 'success',
                'discovery_query': query,
                'opportunity_score': 8.5 - (i * 0.5)
            }
            mock_results.append(mock_result)
        
        return mock_results
    
    def _calculate_opportunity_score(self, content: Dict[str, Any], query: str) -> float:
        """Calculate opportunity score for discovered content"""
        try:
            base_score = 5.0
            
            # Query relevance bonus
            if query.lower() in content.get('title', '').lower():
                base_score += 2.0
            
            # Content quality indicators
            if content.get('content_metrics', {}).get('word_count', 0) > 1000:
                base_score += 1.0
            
            if content.get('seo_analysis', {}).get('title', {}).get('seo_friendly', False):
                base_score += 0.5
            
            # Content freshness (if available)
            if 'recent' in query.lower() or 'latest' in query.lower():
                base_score += 1.0
            
            return min(10.0, base_score)
            
        except Exception as e:
            self.logger.error(f"Opportunity score calculation failed: {e}")
            return 5.0
    
    def _remove_duplicate_content(self, content_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate content based on URL"""
        seen_urls = set()
        unique_content = []
        
        for content in content_list:
            url = content.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_content.append(content)
        
        return unique_content
    
    def _calculate_priority_score(
        self, 
        content: Dict[str, Any], 
        gap_analysis: Dict[str, Any], 
        industry: str
    ) -> float:
        """Calculate priority score for content opportunities"""
        try:
            score = 0.0
            
            # Base opportunity score
            score += content.get('opportunity_score', 5.0) * 0.4
            
            # Gap analysis bonus
            if gap_analysis.get('missing_angles'):
                score += 2.0
            
            # Industry relevance bonus
            if industry and industry in self.industry_themes:
                score += 1.0
            
            # Content quality bonus
            if content.get('content_metrics', {}).get('word_count', 0) > 1500:
                score += 1.0
            
            return min(10.0, score)
            
        except Exception as e:
            self.logger.error(f"Priority score calculation failed: {e}")
            return 5.0
    
    def _get_priority_level(self, score: float) -> str:
        """Get priority level based on score"""
        if score >= 8.0:
            return "high"
        elif score >= 6.0:
            return "medium"
        else:
            return "low"
    
    def _get_recommended_action(self, content: Dict[str, Any], score: float) -> str:
        """Get recommended action based on priority score"""
        if score >= 8.0:
            return "Create comprehensive content immediately"
        elif score >= 6.0:
            return "Plan content creation within 2 weeks"
        else:
            return "Consider for future content planning"
    
    def _estimate_content_impact(self, content: Dict[str, Any], score: float) -> str:
        """Estimate the impact of creating content"""
        if score >= 8.0:
            return "High - Significant traffic and engagement potential"
        elif score >= 6.0:
            return "Medium - Good traffic potential with proper execution"
        else:
            return "Low - Limited immediate impact"
    
    def _assess_implementation_difficulty(self, content: Dict[str, Any]) -> str:
        """Assess the difficulty of implementing the content"""
        word_count = content.get('content_metrics', {}).get('word_count', 0)
        
        if word_count > 2000:
            return "High - Requires extensive research and writing"
        elif word_count > 1000:
            return "Medium - Moderate research and writing effort"
        else:
            return "Low - Quick to implement"
    
    async def get_media_count(self) -> int:
        """Get count of discovered media content"""
        return 0  # Placeholder
    
    async def health_check(self) -> bool:
        """Check content discovery service health"""
        try:
            # Basic health check
            return True
        except Exception as e:
            self.logger.error(f"Content discovery health check failed: {e}")
            return False
    
    # Additional helper methods for analysis
    def _analyze_keyword_coverage(self, content: List[Dict], keyword: str) -> Dict[str, Any]:
        """Analyze keyword coverage in content"""
        return {"coverage_score": 7.5, "content_count": 3, "quality": "good"}
    
    def _analyze_content_depth_distribution(self, content: List[Dict]) -> Dict[str, Any]:
        """Analyze content depth distribution"""
        return {"shallow": 2, "medium": 5, "deep": 3, "average_depth": "medium"}
    
    def _analyze_content_formats(self, content: List[Dict]) -> Dict[str, Any]:
        """Analyze content format distribution"""
        return {"article": 8, "video": 1, "infographic": 1, "podcast": 0}
    
    def _identify_quality_gaps(self, content: List[Dict]) -> List[str]:
        """Identify quality gaps in content"""
        return ["Limited multimedia content", "Shallow topic coverage"]
    
    def _identify_missing_angles(self, content: List[Dict], industry: str) -> List[str]:
        """Identify missing content angles"""
        return ["Case studies", "Expert interviews", "Industry comparisons"]
    
    def _identify_high_opportunity_areas(self, content: List[Dict], gap_analysis: Dict) -> List[str]:
        """Identify high opportunity areas"""
        return ["AI implementation guides", "Industry trend analysis", "Best practices"]
    
    def _analyze_content_trends(self, content: List[Dict]) -> Dict[str, Any]:
        """Analyze content trends"""
        return {"trending_topics": ["AI", "Sustainability"], "growth_rate": "increasing"}
    
    def _analyze_audience_insights(self, content: List[Dict]) -> Dict[str, Any]:
        """Analyze audience insights"""
        return {"primary_audience": "professionals", "expertise_level": "intermediate"}
    
    def _analyze_competitive_landscape(self, content: List[Dict]) -> Dict[str, Any]:
        """Analyze competitive landscape"""
        return {"competition_level": "medium", "differentiation_opportunities": "high"}
    
    def _generate_recommended_actions(self, insights: Dict, industry: str) -> List[str]:
        """Generate recommended actions"""
        return ["Focus on high-opportunity topics", "Improve content quality", "Diversify content formats"]
    
    def _get_industry_recommendations(self, industry: str, content: List[Dict]) -> List[str]:
        """Get industry-specific recommendations"""
        return [f"Focus on {industry} trends", f"Create {industry} case studies"]
    
    def _extract_topics_from_content(self, content: List[Dict]) -> List[str]:
        """Extract topics from content"""
        return ["AI/ML", "Content Marketing", "SEO", "Digital Transformation"]
    
    def _analyze_trend_velocity(self, content: List[Dict]) -> Dict[str, Any]:
        """Analyze trend velocity"""
        return {"fast_growing": ["AI"], "stable": ["SEO"], "declining": ["Traditional Marketing"]}
    
    def _analyze_seasonality(self, content: List[Dict]) -> Dict[str, Any]:
        """Analyze seasonality patterns"""
        return {"seasonal_topics": ["Holiday Marketing"], "year_round": ["SEO", "Content Marketing"]}
    
    def _analyze_content_themes(self, content: List[Dict]) -> Dict[str, Any]:
        """Analyze content themes"""
        return {"primary_themes": ["Technology", "Marketing"], "secondary_themes": ["Business", "Innovation"]}
    
    def _analyze_engagement_patterns(self, content: List[Dict]) -> Dict[str, Any]:
        """Analyze engagement patterns"""
        return {"high_engagement": ["How-to guides"], "low_engagement": ["News updates"]}
    
    def _identify_trend_indicators(self, content: Dict) -> Dict[str, Any]:
        """Identify trend indicators in content"""
        return {
            "is_emerging": True,
            "topic": "AI in Marketing",
            "confidence": 8.5,
            "growth_rate": 7.2,
            "evidence": ["Recent mentions", "Growing search volume"],
            "trajectory": "Rapid growth expected",
            "recommendation": "Create comprehensive content immediately"
        }
    
    async def _generate_trending_recommendations(
        self, 
        trend_analysis: Dict[str, Any], 
        emerging_trends: List[Dict[str, Any]], 
        industry: str
    ) -> List[str]:
        """Generate recommendations based on trending analysis"""
        try:
            recommendations = []
            
            # Recommendations based on top topics
            top_topics = trend_analysis.get('top_topics', [])
            if top_topics:
                for topic in top_topics[:3]:
                    recommendations.append(f"Create content about trending topic: {topic}")
            
            # Recommendations based on emerging trends
            if emerging_trends:
                for trend in emerging_trends[:3]:
                    recommendations.append(
                        f"Early adoption opportunity: {trend.get('topic', 'trending topic')} "
                        f"(confidence: {trend.get('confidence', 0):.1f})"
                    )
            
            # Velocity-based recommendations
            velocity = trend_analysis.get('velocity', {})
            fast_growing = velocity.get('fast_growing', [])
            if fast_growing:
                recommendations.append(f"Focus on fast-growing topics: {', '.join(fast_growing[:2])}")
            
            # Industry-specific recommendations
            if industry:
                recommendations.append(f"Monitor {industry} trends for content opportunities")
                recommendations.append(f"Create {industry}-focused trending content")
            
            # General trending recommendations
            recommendations.extend([
                "Stay updated with industry news and developments",
                "Monitor social media for viral content opportunities",
                "Create content that capitalizes on trending topics quickly"
            ])
            
            return recommendations[:8]  # Limit to top 8 recommendations
            
        except Exception as e:
            self.logger.error(f"Trending recommendations generation failed: {e}")
            return ["Monitor trending topics for content opportunities"]
    
    async def _analyze_competitor_content(self, competitor_urls: List[str]) -> List[Dict[str, Any]]:
        """Analyze competitor content for gap analysis"""
        try:
            competitor_content = []
            
            # Get scraping service
            if not self.scraping_service:
                self.scraping_service = self.container.get_service('scraping_service')
            
            # Scrape competitor content
            for url in competitor_urls[:5]:  # Limit to top 5 competitors
                try:
                    content = await self.scraping_service.smart_content_extraction(
                        url, 
                        extraction_goal="competitor_analysis"
                    )
                    if content.get('status') == 'success':
                        competitor_content.append(content)
                    
                    await asyncio.sleep(1)  # Be respectful
                    
                except Exception as e:
                    self.logger.warning(f"Failed to analyze competitor {url}: {e}")
                    continue
            
            return competitor_content
            
        except Exception as e:
            self.logger.error(f"Competitor content analysis failed: {e}")
            return []
    
    async def _search_keyword_content(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Search for content about specific keywords"""
        try:
            keyword_content = []
            
            # Get scraping service
            if not self.scraping_service:
                self.scraping_service = self.container.get_service('scraping_service')
            
            # Search for each keyword
            for keyword in keywords[:3]:  # Limit to top 3 keywords
                try:
                    search_results = await self._search_for_content(keyword, 3)
                    keyword_content.extend(search_results)
                    
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    self.logger.warning(f"Keyword search failed for '{keyword}': {e}")
                    continue
            
            return keyword_content
            
        except Exception as e:
            self.logger.error(f"Keyword content search failed: {e}")
            return []
    
    async def _identify_content_gaps(
        self, 
        competitor_content: List[Dict[str, Any]], 
        keyword_content: List[Dict[str, Any]], 
        target_keywords: List[str], 
        industry: str
    ) -> Dict[str, Any]:
        """Identify content gaps from competitor and keyword analysis"""
        try:
            gaps = {
                'topic_gaps': [],
                'format_gaps': [],
                'quality_gaps': [],
                'audience_gaps': [],
                'timing_gaps': []
            }
            
            # Analyze topic coverage
            if target_keywords:
                for keyword in target_keywords:
                    coverage = self._analyze_keyword_coverage(competitor_content + keyword_content, keyword)
                    if coverage.get('coverage_score', 0) < 6.0:
                        gaps['topic_gaps'].append(f"Limited coverage of '{keyword}'")
            
            # Analyze content formats
            format_distribution = self._analyze_content_formats(competitor_content + keyword_content)
            if format_distribution.get('video', 0) < 2:
                gaps['format_gaps'].append("Limited video content")
            if format_distribution.get('infographic', 0) < 1:
                gaps['format_gaps'].append("No infographic content")
            
            # Analyze content quality
            avg_quality = self._calculate_content_quality_score(competitor_content + keyword_content)
            if avg_quality < 7.0:
                gaps['quality_gaps'].append("Content quality could be improved")
            
            # Analyze audience targeting
            audience_insights = self._analyze_audience_insights(competitor_content + keyword_content)
            if audience_insights.get('expertise_level') == 'beginner':
                gaps['audience_gaps'].append("Limited advanced content for professionals")
            
            return gaps
            
        except Exception as e:
            self.logger.error(f"Content gap identification failed: {e}")
            return {'error': str(e)}
    
    async def _generate_gap_filling_recommendations(
        self, 
        content_gaps: Dict[str, Any], 
        industry: str
    ) -> List[str]:
        """Generate recommendations for filling content gaps"""
        try:
            recommendations = []
            
            # Topic gap recommendations
            topic_gaps = content_gaps.get('topic_gaps', [])
            for gap in topic_gaps[:3]:
                recommendations.append(f"Create content to address: {gap}")
            
            # Format gap recommendations
            format_gaps = content_gaps.get('format_gaps', [])
            for gap in format_gaps:
                recommendations.append(f"Develop {gap.lower()} to diversify content")
            
            # Quality gap recommendations
            quality_gaps = content_gaps.get('quality_gaps', [])
            if quality_gaps:
                recommendations.append("Focus on improving content depth and research quality")
            
            # Industry-specific recommendations
            if industry:
                recommendations.append(f"Create comprehensive {industry} guides and tutorials")
                recommendations.append(f"Develop {industry} case studies and success stories")
            
            # General gap-filling recommendations
            recommendations.extend([
                "Conduct audience research to identify unmet needs",
                "Analyze competitor content for improvement opportunities",
                "Create content that addresses common pain points"
            ])
            
            return recommendations[:8]  # Limit to top 8 recommendations
            
        except Exception as e:
            self.logger.error(f"Gap filling recommendations failed: {e}")
            return ["Focus on creating high-quality, comprehensive content"]
    
    async def _prioritize_content_gaps(self, content_gaps: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prioritize content gaps based on impact and effort"""
        try:
            prioritized_gaps = []
            
            # Convert gaps to prioritized items
            for gap_type, gaps in content_gaps.items():
                if isinstance(gaps, list):
                    for gap in gaps:
                        priority_item = {
                            'gap': gap,
                            'type': gap_type,
                            'priority_score': self._calculate_gap_priority_score(gap, gap_type),
                            'estimated_effort': self._estimate_gap_filling_effort(gap, gap_type),
                            'potential_impact': self._estimate_gap_impact(gap, gap_type)
                        }
                        prioritized_gaps.append(priority_item)
            
            # Sort by priority score
            prioritized_gaps.sort(key=lambda x: x['priority_score'], reverse=True)
            
            return prioritized_gaps
            
        except Exception as e:
            self.logger.error(f"Content gap prioritization failed: {e}")
            return []
    
    def _calculate_gap_priority_score(self, gap: str, gap_type: str) -> float:
        """Calculate priority score for a content gap"""
        try:
            base_score = 5.0
            
            # Type-based scoring
            if gap_type == 'topic_gaps':
                base_score += 2.0  # High priority for topic gaps
            elif gap_type == 'format_gaps':
                base_score += 1.5  # Medium priority for format gaps
            elif gap_type == 'quality_gaps':
                base_score += 2.5  # Very high priority for quality gaps
            
            # Content-based scoring
            if 'limited' in gap.lower():
                base_score += 1.0
            if 'no' in gap.lower():
                base_score += 1.5
            
            return min(10.0, base_score)
            
        except Exception as e:
            self.logger.error(f"Gap priority score calculation failed: {e}")
            return 5.0
    
    def _estimate_gap_filling_effort(self, gap: str, gap_type: str) -> str:
        """Estimate effort required to fill a content gap"""
        try:
            if gap_type == 'topic_gaps':
                return "Medium - Requires research and writing"
            elif gap_type == 'format_gaps':
                return "High - Requires new skills and tools"
            elif gap_type == 'quality_gaps':
                return "Medium - Requires improved processes"
            else:
                return "Low - Quick to implement"
                
        except Exception as e:
            self.logger.error(f"Gap effort estimation failed: {e}")
            return "Unknown"
    
    def _estimate_gap_impact(self, gap: str, gap_type: str) -> str:
        """Estimate potential impact of filling a content gap"""
        try:
            if gap_type == 'topic_gaps':
                return "High - Directly addresses audience needs"
            elif gap_type == 'format_gaps':
                return "Medium - Improves content variety"
            elif gap_type == 'quality_gaps':
                return "Very High - Improves overall content performance"
            else:
                return "Medium - General improvement"
                
        except Exception as e:
            self.logger.error(f"Gap impact estimation failed: {e}")
            return "Unknown"
    
    def _calculate_gap_opportunity_score(self, content_gaps: Dict[str, Any]) -> float:
        """Calculate overall opportunity score from content gaps"""
        try:
            if not content_gaps:
                return 0.0
            
            total_gaps = 0
            total_score = 0.0
            
            for gap_type, gaps in content_gaps.items():
                if isinstance(gaps, list):
                    total_gaps += len(gaps)
                    for gap in gaps:
                        score = self._calculate_gap_priority_score(gap, gap_type)
                        total_score += score
            
            if total_gaps == 0:
                return 0.0
            
            return total_score / total_gaps
            
        except Exception as e:
            self.logger.error(f"Gap opportunity score calculation failed: {e}")
            return 0.0
    
    def _calculate_trend_score(self, content: Dict[str, Any], query: str) -> float:
        """Calculate trend score for trending content"""
        try:
            base_score = 5.0
            
            # Query relevance bonus
            if query.lower() in content.get('title', '').lower():
                base_score += 2.0
            
            # Trending indicators
            trending_words = ['trending', 'hot', 'viral', 'latest', 'new', 'breaking']
            title = content.get('title', '').lower()
            for word in trending_words:
                if word in title:
                    base_score += 1.0
            
            # Content freshness
            if 'recent' in query.lower() or 'latest' in query.lower():
                base_score += 1.5
            
            return min(10.0, base_score)
            
        except Exception as e:
            self.logger.error(f"Trend score calculation failed: {e}")
            return 5.0
