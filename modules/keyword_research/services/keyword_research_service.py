"""
Keyword Research Service
Main service for conducting comprehensive keyword research
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from loguru import logger
import re

from shared.database.models import KeywordResearch, get_db
from shared.utils.helpers import TextProcessor, CacheUtils
from shared.config.settings import get_settings

class KeywordResearchService:
    """
    Comprehensive keyword research service
    Combines multiple data sources for complete keyword analysis
    """
    
    def __init__(self, container, google_trends_service, serp_service):
        self.container = container
        self.google_trends = google_trends_service
        self.serp = serp_service
        self.settings = get_settings()
        self.logger = logger.bind(service="KeywordResearchService")
    
    async def comprehensive_research(self, primary_keyword: str) -> Dict[str, Any]:
        """
        Conduct comprehensive keyword research
        Combines trends, SERP analysis, and competitor research
        """
        # Validate keyword
        from shared.utils.validation_service import validation_service
        validation = validation_service.validate_keyword(primary_keyword)
        if not validation['valid']:
            raise ValueError(f"Invalid keyword: {', '.join(validation['issues'])}")
        
        self.logger.info(f"Starting comprehensive research for: {primary_keyword}")
        
        # Check cache first
        cache_key = CacheUtils.generate_cache_key("keyword_research", primary_keyword)
        cached_result = await self._get_cached_research(cache_key)
        
        if cached_result:
            self.logger.info("Returning cached keyword research")
            return cached_result
        
        # Gather data from multiple sources concurrently
        research_tasks = [
            self._research_trends(primary_keyword),
            self._research_serp_data(primary_keyword),
            self._research_related_keywords(primary_keyword),
            self._research_competitor_keywords(primary_keyword)
        ]
        
        try:
            trends_data, serp_data, related_keywords, competitor_keywords = await asyncio.gather(
                *research_tasks, return_exceptions=True
            )
            
            # Handle any exceptions
            if isinstance(trends_data, Exception):
                self.logger.warning(f"Trends research failed: {trends_data}")
                trends_data = {}
            
            if isinstance(serp_data, Exception):
                self.logger.warning(f"SERP research failed: {serp_data}")
                serp_data = {}
            
            if isinstance(related_keywords, Exception):
                self.logger.warning(f"Related keywords research failed: {related_keywords}")
                related_keywords = []
            
            if isinstance(competitor_keywords, Exception):
                self.logger.warning(f"Competitor research failed: {competitor_keywords}")
                competitor_keywords = []
            
            # Compile comprehensive research result
            research_result = {
                "primary_keyword": primary_keyword,
                "research_date": datetime.utcnow().isoformat(),
                
                # Trends data
                "search_volume": trends_data.get('search_volume', 0),
                "trending_score": trends_data.get('trending_score', 0),
                "seasonal_trends": trends_data.get('seasonal_data', []),
                "related_queries": trends_data.get('related_queries', []),
                
                # SERP data
                "competition_level": serp_data.get('competition_level', 'unknown'),
                "difficulty_score": serp_data.get('difficulty_score', 0),
                "serp_features": serp_data.get('serp_features', []),
                "top_competitors": serp_data.get('top_competitors', []),
                
                # Related keywords
                "related_keywords": related_keywords,
                "long_tail_keywords": self._generate_long_tail_keywords(primary_keyword, related_keywords),
                
                # Competitor insights
                "competitor_keywords": competitor_keywords,
                "content_gaps": serp_data.get('content_gaps', []),
                
                # Analysis scores
                "overall_opportunity_score": self._calculate_opportunity_score(trends_data, serp_data),
                "recommended_strategy": self._generate_strategy_recommendations(primary_keyword, trends_data, serp_data)
            }
            
            # Cache the result
            await self._cache_research(cache_key, research_result)
            
            # Save to database
            await self._save_research_to_db(research_result)
            
            self.logger.info(f"Completed comprehensive research for: {primary_keyword}")
            return research_result
            
        except Exception as e:
            self.logger.error(f"Error in comprehensive research: {e}")
            raise
    
    async def _research_trends(self, keyword: str) -> Dict[str, Any]:
        """Research Google Trends data"""
        try:
            return await self.google_trends.get_keyword_trends(keyword)
        except Exception as e:
            self.logger.error(f"Trends research failed for {keyword}: {e}")
            return {}
    
    async def _research_serp_data(self, keyword: str) -> Dict[str, Any]:
        """Research SERP data"""
        try:
            return await self.serp.get_serp_analysis(keyword)
        except Exception as e:
            self.logger.error(f"SERP research failed for {keyword}: {e}")
            return {}
    
    def _generate_keyword_variations(self, keyword: str) -> List[str]:
        """Generate keyword variations"""
        variations = []
        
        # Question variations
        question_words = ["how to", "what is", "why", "where", "when", "best"]
        for q_word in question_words:
            variations.append(f"{q_word} {keyword}")
        
        # Modifier variations
        modifiers = ["best", "top", "free", "cheap", "professional", "easy", "quick"]
        for modifier in modifiers:
            variations.append(f"{modifier} {keyword}")
            variations.append(f"{keyword} {modifier}")
        
        return variations[:20]  # Limit variations
    
    def _calculate_opportunity_score(self, trends_data: Dict, serp_data: Dict) -> float:
        """Calculate overall opportunity score for a keyword"""
        search_volume = trends_data.get('search_volume', 0)
        competition = serp_data.get('difficulty_score', 50)
        trending = trends_data.get('trending_score', 0)
        
        # Simple scoring algorithm
        if search_volume == 0:
            return 0.0
        
        # Higher volume and lower competition = better opportunity
        opportunity_score = (search_volume / max(competition, 1)) + trending
        return round(min(opportunity_score, 100), 1)
    
    async def _get_cached_research(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached research data"""
        # Placeholder for caching implementation
        return None
    
    async def _cache_research(self, cache_key: str, data: Dict[str, Any]) -> None:
        """Cache research data"""
        # Placeholder for caching implementation
        pass
    
    async def _save_research_to_db(self, research_data: Dict[str, Any]) -> None:
        """Save research data to database"""
        try:
            # Database saving logic would go here
            self.logger.info(f"Research data saved for: {research_data['primary_keyword']}")
        except Exception as e:
            self.logger.error(f"Failed to save research to database: {e}")
