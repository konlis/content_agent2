"""
Content Generation Module
AI-powered content creation with multi-model support and cost optimization
"""

from core.base_module import BaseModule, ModuleInfo
from .services.content_service import ContentService
from .services.llm_service import LLMService
from .services.template_service import TemplateService
from .routes import router
from .ui import ContentGenerationUI

class ContentGenerationModule(BaseModule):
    """
    Module for AI-powered content generation
    Supports multiple LLM providers with cost optimization
    """
    
    def get_module_info(self) -> ModuleInfo:
        return ModuleInfo(
            name="content_generation",
            version="1.0.0",
            description="AI-powered content generation with multi-model support",
            dependencies=[],  # No hard dependencies - can work independently
            optional_dependencies=["keyword_research", "seo_optimization", "scheduling"],
            author="Content Agent Team"
        )
    
    async def initialize(self) -> bool:
        """Initialize the content generation module"""
        try:
            # Initialize services
            self.llm_service = LLMService(self.container)
            self.template_service = TemplateService(self.container)
            self.content_service = ContentService(
                self.container, self.llm_service, self.template_service
            )
            
            # Register services in DI container
            self.register_service('llm_service', self.llm_service)
            self.register_service('template_service', self.template_service)
            self.register_service('content_service', self.content_service)
            
            # Subscribe to events (only if modules are available)
            try:
                self.subscribe_to_event('keyword_research.keyword_research_completed', self._on_keyword_research_completed)
            except:
                self.logger.info("Keyword research module not available - skipping event subscription")
            
            try:
                self.subscribe_to_event('scheduling.content_generation_requested', self._on_content_generation_requested)
            except:
                self.logger.info("Scheduling module not available - skipping event subscription")
            
            self.logger.info("Content Generation module initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Content Generation module initialization failed: {e}")
            return False
    
    def register_routes(self, app):
        """Register FastAPI routes"""
        app.include_router(router, prefix="/api/content", tags=["content-generation"])
    
    def register_ui_components(self):
        """Register Streamlit UI components"""
        return {
            "content_generator_dashboard": ContentGenerationUI.dashboard,
            "content_generator_form": ContentGenerationUI.generator_form,
            "content_editor": ContentGenerationUI.content_editor,
            "template_manager": ContentGenerationUI.template_manager,
            "content_history": ContentGenerationUI.content_history
        }
    
    async def _on_keyword_research_completed(self, event):
        """Handle keyword research completion"""
        keyword_data = event.data.get('research_data', {})
        request_id = event.data.get('request_id')
        
        if keyword_data.get('auto_generate_content'):
            try:
                # Auto-generate content based on keyword research
                content_request = {
                    'primary_keyword': keyword_data.get('primary_keyword'),
                    'related_keywords': keyword_data.get('related_keywords', []),
                    'content_type': keyword_data.get('content_type', 'blog_post'),
                    'target_audience': keyword_data.get('target_audience', 'general'),
                    'company_info': keyword_data.get('company_info', {}),
                    'request_id': request_id
                }
                
                content_result = await self.content_service.generate_content(content_request)
                
                self.emit_event('content_generated', {
                    'content_id': content_result.get('content_id'),
                    'content': content_result,
                    'request_id': request_id,
                    'auto_generated': True
                })
                
            except Exception as e:
                self.logger.error(f"Auto content generation failed: {e}")
    
    async def _on_content_generation_requested(self, event):
        """Handle content generation requests from scheduling module"""
        try:
            content_request = event.data
            content_result = await self.content_service.generate_content(content_request)
            
            self.emit_event('content_generated', {
                'content_id': content_result.get('content_id'),
                'content': content_result,
                'request_id': content_request.get('request_id'),
                'scheduled': True
            })
            
        except Exception as e:
            self.logger.error(f"Scheduled content generation failed: {e}")
    
    async def health_check(self):
        """Health check for the content generation module"""
        base_health = await super().health_check()
        
        # Check LLM service availability
        llm_health = await self.llm_service.health_check()
        
        base_health.update({
            "llm_services_available": llm_health,
            "templates_loaded": len(self.template_service.get_available_templates()),
            "content_generation_ready": llm_health and self.template_service.is_ready()
        })
        
        return base_health
