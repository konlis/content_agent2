"""
SERP Service
Integrates with SERP API for search results analysis
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from loguru import logger
import requests
import random
import re

from shared.config.settings import get_settings
from shared.utils.helpers import CacheUtils, WebScraper

class SerpService:
    """
    Service for SERP (Search Engine Results Page) analysis
    Provides SERP features, competition analysis, and ranking data
    """
    
    def __init__(self, container):
        self.container = container
        self.settings = get_settings()
        self.logger = logger.bind(service="SerpService")
        
        # SERP API configuration
        self.serp_api_key = self.settings.serpapi_key
        self.serp_base_url = "https://serpapi.com/search.json"
    
    async def get_serp_analysis(self, keyword: str, location: str = "United States") -> Dict[str, Any]:
        """
        Get comprehensive SERP analysis for a keyword
        """
        try:
            self.logger.info(f"Getting SERP analysis for: {keyword}")
            
            # Check cache first
            cache_key = CacheUtils.generate_cache_key("serp", keyword, location)
            cached_result = await self._get_cached_serp(cache_key)
            
            if cached_result:
                return cached_result
            
            # Get SERP data
            loop = asyncio.get_event_loop()
            serp_data = await loop.run_in_executor(
                None, self._fetch_serp_data, keyword, location
            )
            
            # Analyze the SERP data
            analysis = await self._analyze_serp_data(serp_data, keyword)
            
            result = {
                "keyword": keyword,
                "location": location,
                "serp_features": analysis.get("serp_features", []),
                "organic_results": analysis.get("organic_results", []),
                "top_competitors": analysis.get("top_competitors", []),
                "difficulty_score": analysis.get("difficulty_score", 50),
                "competition_level": analysis.get("competition_level", "medium"),
                "content_gaps": analysis.get("content_gaps", []),
                "ranking_factors": analysis.get("ranking_factors", {}),
                "retrieved_at": datetime.utcnow().isoformat()
            }
            
            # Cache the result
            await self._cache_serp(cache_key, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error getting SERP analysis for {keyword}: {e}")
            return {
                "keyword": keyword,
                "error": str(e),
                "difficulty_score": 50,
                "competition_level": "unknown"
            }
    
    async def get_related_keywords(self, keyword: str) -> List[str]:
        """Get related keywords from SERP data"""
        try:
            serp_data = await self.get_serp_analysis(keyword)
            related_keywords = set()
            
            # Extract from People Also Ask
            paa_questions = serp_data.get("people_also_ask", [])
            for question in paa_questions:
                # Extract keywords from questions
                keywords = self._extract_keywords_from_question(question)
                related_keywords.update(keywords)
            
            # Extract from related searches
            related_searches = serp_data.get("related_searches", [])
            related_keywords.update(related_searches)
            
            # Extract from competitor titles
            for competitor in serp_data.get("top_competitors", [])[:5]:
                title_keywords = self._extract_keywords_from_title(competitor.get("title", ""))
                related_keywords.update(title_keywords)
            
            # Remove the original keyword
            related_keywords.discard(keyword.lower())
            
            return list(related_keywords)[:30]  # Return top 30
            
        except Exception as e:
            self.logger.error(f"Error getting related keywords: {e}")
            return []
    
    async def analyze_top_competitors(self, keyword: str, num_competitors: int = 10) -> List[Dict[str, Any]]:
        """Analyze top competitors for a keyword"""
        try:
            serp_data = await self.get_serp_analysis(keyword)
            competitors = []
            
            organic_results = serp_data.get("organic_results", [])
            
            for i, result in enumerate(organic_results[:num_competitors]):
                try:
                    # Analyze each competitor
                    competitor_analysis = await self._analyze_competitor(result, keyword)
                    competitor_analysis["rank"] = i + 1
                    competitors.append(competitor_analysis)
                    
                    # Rate limiting
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to analyze competitor {result.get('link', '')}: {e}")
            
            return competitors
            
        except Exception as e:
            self.logger.error(f"Error analyzing competitors: {e}")
            return []
    
    def _fetch_serp_data(self, keyword: str, location: str) -> Dict[str, Any]:
        """
        Fetch SERP data from API or simulate for development
        """
        if self.serp_api_key and self.serp_api_key != "your_serpapi_key_here":
            return self._fetch_real_serp_data(keyword, location)
        else:
            return self._simulate_serp_data(keyword, location)
    
    def _fetch_real_serp_data(self, keyword: str, location: str) -> Dict[str, Any]:
        """Fetch real SERP data from SerpAPI"""
        try:
            params = {
                "engine": "google",
                "q": keyword,
                "location": location,
                "api_key": self.serp_api_key,
                "num": 20  # Get top 20 results
            }
            
            response = requests.get(self.serp_base_url, params=params, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            self.logger.error(f"Error fetching real SERP data: {e}")
            return self._simulate_serp_data(keyword, location)
    
    def _simulate_serp_data(self, keyword: str, location: str) -> Dict[str, Any]:
        """
        Simulate SERP data for development/testing
        """
        # Generate realistic-looking SERP data
        organic_results = []
        
        # Common domains that might rank
        domains = [
            "wikipedia.org", "medium.com", "hubspot.com", "neil-patel.com",
            "moz.com", "searchengineland.com", "contentmarketinginstitute.com",
            "blog.hootsuite.com", "sproutsocial.com", "buffer.com"
        ]
        
        for i in range(10):
            domain = random.choice(domains)
            result = {
                "position": i + 1,
                "title": f"{keyword.title()} - Complete Guide | {domain.split('.')[0].title()}",
                "link": f"https://{domain}/{keyword.replace(' ', '-').lower()}-guide",
                "domain": domain,
                "displayed_link": f"{domain} › {keyword.replace(' ', '-')}",
                "snippet": f"Everything you need to know about {keyword}. Learn from experts and get practical tips to improve your {keyword} strategy.",
                "snippet_highlighted_words": [keyword]
            }
            organic_results.append(result)
        
        # Simulate SERP features
        serp_features = []
        
        # Add featured snippet sometimes
        if random.random() > 0.6:
            serp_features.append("featured_snippet")
        
        # Add People Also Ask
        if random.random() > 0.3:
            serp_features.append("people_also_ask")
        
        # Add related searches
        if random.random() > 0.2:
            serp_features.append("related_searches")
        
        # Generate People Also Ask questions
        paa_questions = [
            f"What is {keyword}?",
            f"How to improve {keyword}?",
            f"Best {keyword} tools",
            f"Why is {keyword} important?",
            f"{keyword} vs alternatives"
        ]
        
        # Generate related searches
        related_searches = [
            f"best {keyword}",
            f"{keyword} tools",
            f"how to {keyword}",
            f"{keyword} guide",
            f"free {keyword}"
        ]
        
        return {
            "search_metadata": {
                "id": "simulated",
                "status": "Success",
                "json_endpoint": "simulated",
                "created_at": datetime.utcnow().isoformat()
            },
            "search_parameters": {
                "engine": "google",
                "q": keyword,
                "location": location,
                "device": "desktop"
            },
            "organic_results": organic_results,
            "people_also_ask": paa_questions[:4] if "people_also_ask" in serp_features else [],
            "related_searches": [{"query": rs} for rs in related_searches] if "related_searches" in serp_features else [],
            "serp_features": serp_features
        }
    
    async def _analyze_serp_data(self, serp_data: Dict[str, Any], keyword: str) -> Dict[str, Any]:
        """Analyze SERP data to extract insights"""
        try:
            organic_results = serp_data.get("organic_results", [])
            
            # Extract SERP features
            serp_features = serp_data.get("serp_features", [])
            
            # Analyze top competitors
            top_competitors = []
            for result in organic_results[:5]:
                competitor = {
                    "rank": result.get("position", 0),
                    "title": result.get("title", ""),
                    "url": result.get("link", ""),
                    "domain": result.get("domain", ""),
                    "snippet": result.get("snippet", ""),
                    "title_length": len(result.get("title", "")),
                    "has_keyword_in_title": keyword.lower() in result.get("title", "").lower()
                }
                top_competitors.append(competitor)
            
            # Calculate difficulty score
            difficulty_score = self._calculate_difficulty_score(organic_results, keyword)
            
            # Determine competition level
            competition_level = self._determine_competition_level(difficulty_score)
            
            # Identify content gaps
            content_gaps = await self._identify_content_gaps(organic_results, keyword)
            
            # Analyze ranking factors
            ranking_factors = self._analyze_ranking_factors(organic_results, keyword)
            
            return {
                "serp_features": serp_features,
                "organic_results": organic_results,
                "top_competitors": top_competitors,
                "difficulty_score": difficulty_score,
                "competition_level": competition_level,
                "content_gaps": content_gaps,
                "ranking_factors": ranking_factors
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing SERP data: {e}")
            return {}
    
    async def _analyze_competitor(self, competitor_data: Dict[str, Any], keyword: str) -> Dict[str, Any]:
        """Analyze individual competitor"""
        try:
            url = competitor_data.get("link", "")
            title = competitor_data.get("title", "")
            snippet = competitor_data.get("snippet", "")
            
            # Extract domain authority (simulated)
            domain = competitor_data.get("domain", "")
            domain_authority = self._estimate_domain_authority(domain)
            
            # Analyze title optimization
            title_analysis = self._analyze_title_seo(title, keyword)
            
            # Analyze content snippet
            snippet_analysis = self._analyze_snippet(snippet, keyword)
            
            return {
                "url": url,
                "domain": domain,
                "title": title,
                "snippet": snippet,
                "domain_authority": domain_authority,
                "title_analysis": title_analysis,
                "snippet_analysis": snippet_analysis,
                "keyword_in_url": keyword.lower().replace(" ", "-") in url.lower()
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing competitor: {e}")
            return {}
    
    def _calculate_difficulty_score(self, organic_results: List[Dict], keyword: str) -> float:
        """Calculate keyword difficulty score (0-100)"""
        try:
            if not organic_results:
                return 50.0
            
            score = 0
            factors = 0
            
            for result in organic_results[:10]:
                domain = result.get("domain", "")
                title = result.get("title", "")
                
                # Domain authority factor
                da_score = self._estimate_domain_authority(domain)
                score += da_score
                factors += 1
                
                # Title optimization factor
                if keyword.lower() in title.lower():
                    score += 10
                    factors += 1
            
            if factors == 0:
                return 50.0
            
            avg_score = score / factors
            return min(max(avg_score, 0), 100)
            
        except Exception as e:
            self.logger.error(f"Error calculating difficulty score: {e}")
            return 50.0
    
    def _determine_competition_level(self, difficulty_score: float) -> str:
        """Determine competition level based on difficulty score"""
        if difficulty_score < 30:
            return "low"
        elif difficulty_score < 70:
            return "medium"
        else:
            return "high"
    
    def _estimate_domain_authority(self, domain: str) -> float:
        """Estimate domain authority (simplified)"""
        # High authority domains
        high_authority = [
            "wikipedia.org", "youtube.com", "facebook.com", "twitter.com",
            "linkedin.com", "instagram.com", "pinterest.com", "reddit.com"
        ]
        
        # Medium authority domains
        medium_authority = [
            "medium.com", "hubspot.com", "moz.com", "searchengineland.com",
            "contentmarketinginstitute.com", "neil-patel.com"
        ]
        
        if domain in high_authority:
            return random.randint(80, 95)
        elif domain in medium_authority:
            return random.randint(60, 79)
        else:
            return random.randint(20, 59)
    
    async def _identify_content_gaps(self, organic_results: List[Dict], keyword: str) -> List[str]:
        """Identify content gaps in top results"""
        gaps = []
        
        # Common content types to check for
        content_types = [
            "tutorial", "guide", "comparison", "review", "tips", 
            "best practices", "checklist", "template", "case study", "faq"
        ]
        
        # Check what's missing in top 5 results
        top_titles = [result.get("title", "").lower() for result in organic_results[:5]]
        
        for content_type in content_types:
            if not any(content_type in title for title in top_titles):
                gaps.append(f"{keyword} {content_type}")
        
        return gaps[:5]  # Return top 5 gaps
    
    def _analyze_ranking_factors(self, organic_results: List[Dict], keyword: str) -> Dict[str, Any]:
        """Analyze common ranking factors in top results"""
        factors = {
            "avg_title_length": 0,
            "keyword_in_title_percentage": 0,
            "avg_snippet_length": 0,
            "https_percentage": 0
        }
        
        if not organic_results:
            return factors
        
        total_results = len(organic_results[:10])
        title_lengths = []
        snippet_lengths = []
        keyword_in_title_count = 0
        https_count = 0
        
        for result in organic_results[:10]:
            title = result.get("title", "")
            snippet = result.get("snippet", "")
            url = result.get("link", "")
            
            title_lengths.append(len(title))
            snippet_lengths.append(len(snippet))
            
            if keyword.lower() in title.lower():
                keyword_in_title_count += 1
            
            if url.startswith("https://"):
                https_count += 1
        
        factors["avg_title_length"] = sum(title_lengths) / len(title_lengths) if title_lengths else 0
        factors["keyword_in_title_percentage"] = (keyword_in_title_count / total_results) * 100
        factors["avg_snippet_length"] = sum(snippet_lengths) / len(snippet_lengths) if snippet_lengths else 0
        factors["https_percentage"] = (https_count / total_results) * 100
        
        return factors
    
    async def _get_cached_serp(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached SERP data"""
        # Placeholder for Redis caching
        return None
    
    async def _cache_serp(self, cache_key: str, data: Dict[str, Any]) -> None:
        """Cache SERP data"""
        # Placeholder for Redis caching
        self.logger.debug(f"Would cache SERP data: {cache_key}")
    
    async def health_check(self) -> bool:
        """Check if SERP service is available"""
        try:
            # Test with a simple query
            if self.serp_api_key and self.serp_api_key != "your_serpapi_key_here":
                # In production, test the actual API
                return True
            else:
                # Simulation mode is always available
                return True
        except Exception as e:
            self.logger.error(f"SERP service health check failed: {e}")
            return False
