"""
Keyword Research Module
Provides comprehensive keyword research using multiple APIs and scraping
"""

from core.base_module import BaseModule, ModuleInfo
from .services.keyword_research_service import KeywordResearchService
from .services.google_trends_service import GoogleTrendsService
from .services.serp_service import SerpService
from .routes import router
from .ui import KeywordResearchUI

class KeywordResearchModule(BaseModule):
    """
    Module for keyword research functionality
    Integrates Google Trends, SERP API, and web scraping
    """
    
    def get_module_info(self) -> ModuleInfo:
        return ModuleInfo(
            name="keyword_research",
            version="1.0.0",
            description="Comprehensive keyword research and analysis",
            dependencies=[],  # No dependencies - this is a core module
            optional_dependencies=["seo_optimization"],
            author="Content Agent Team"
        )
    
    async def initialize(self) -> bool:
        """Initialize the keyword research module"""
        try:
            # Initialize services
            self.google_trends_service = GoogleTrendsService(self.container)
            self.serp_service = SerpService(self.container)
            self.keyword_research_service = KeywordResearchService(
                self.container, self.google_trends_service, self.serp_service
            )
            
            # Register services in DI container
            self.register_service('google_trends_service', self.google_trends_service)
            self.register_service('serp_service', self.serp_service)
            self.register_service('keyword_research_service', self.keyword_research_service)
            
            # Subscribe to events
            self.subscribe_to_event('content_generation.keyword_needed', self._on_keyword_needed)
            
            self.logger.info("Keyword Research module initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Keyword Research module initialization failed: {e}")
            return False
    
    def register_routes(self, app):
        """Register FastAPI routes"""
        app.include_router(router, prefix="/api/keyword-research", tags=["keyword-research"])
    
    def register_ui_components(self):
        """Register Streamlit UI components"""
        return {
            "keyword_research_dashboard": KeywordResearchUI.dashboard,
            "keyword_input_form": KeywordResearchUI.input_form,
            "keyword_results_display": KeywordResearchUI.results_display,
            "competitor_analysis": KeywordResearchUI.competitor_analysis
        }
    
    async def _on_keyword_needed(self, event):
        """Handle keyword research requests from other modules"""
        keyword = event.data.get('keyword')
        if keyword:
            try:
                research_result = await self.keyword_research_service.comprehensive_research(keyword)
                self.emit_event('keyword_research_completed', {
                    'keyword': keyword,
                    'research_data': research_result,
                    'request_id': event.data.get('request_id')
                })
            except Exception as e:
                self.logger.error(f"Error processing keyword research request: {e}")
    
    async def health_check(self):
        """Health check for the keyword research module"""
        base_health = await super().health_check()
        
        # Check API availability
        google_trends_ok = await self.google_trends_service.health_check()
        serp_ok = await self.serp_service.health_check()
        
        base_health.update({
            "google_trends_available": google_trends_ok,
            "serp_api_available": serp_ok,
            "services_healthy": google_trends_ok and serp_ok
        })
        
        return base_health
