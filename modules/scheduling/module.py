"""
Scheduling Module
Content scheduling and automation system
"""

from core.base_module import BaseModule, ModuleInfo
from .services.scheduler_service import SchedulerService
from .services.calendar_service import CalendarService
from .services.automation_service import AutomationService
from .routes import router
from .ui import SchedulingUI

class SchedulingModule(BaseModule):
    """
    Module for content scheduling and publishing automation
    """
    
    def get_module_info(self) -> ModuleInfo:
        return ModuleInfo(
            name="scheduling",
            version="1.0.0",
            description="Content scheduling and publishing automation",
            dependencies=[],  # No hard dependencies - can work independently
            optional_dependencies=["content_generation", "wordpress_integration"],
            author="Content Agent Team"
        )
    
    async def initialize(self) -> bool:
        """Initialize the scheduling module"""
        try:
            # Initialize services
            self.scheduler_service = SchedulerService(self.container)
            self.calendar_service = CalendarService(self.container)
            self.automation_service = AutomationService(self.container)
            
            # Register services in DI container
            self.register_service('scheduler_service', self.scheduler_service)
            self.register_service('calendar_service', self.calendar_service)
            self.register_service('automation_service', self.automation_service)
            
            # Subscribe to events (only if modules are available)
            try:
                self.subscribe_to_event('content_generation.content_generated', self._on_content_generated)
            except:
                self.logger.info("Content generation module not available - skipping event subscription")
            
            try:
                self.subscribe_to_event('wordpress_integration.publish_requested', self._on_publish_requested)
            except:
                self.logger.info("WordPress integration module not available - skipping event subscription")
            
            self.logger.info("Scheduling module initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Scheduling module initialization failed: {e}")
            return False
    
    def register_routes(self, app):
        """Register FastAPI routes"""
        app.include_router(router, prefix="/api/scheduling", tags=["scheduling"])
    
    def register_ui_components(self):
        """Register Streamlit UI components"""
        return {
            "scheduling_dashboard": SchedulingUI.dashboard,
            "content_calendar": SchedulingUI.calendar_view,
            "schedule_content": SchedulingUI.schedule_form,
            "automation_settings": SchedulingUI.automation_settings,
            "publishing_history": SchedulingUI.publishing_history
        }
    
    async def _on_content_generated(self, event):
        """Handle content generation completion"""
        content_data = event.data
        
        # Check if auto-scheduling is enabled
        if content_data.get('auto_schedule'):
            try:
                # Get optimal posting time
                optimal_time = await self.calendar_service.get_optimal_posting_time(
                    content_data.get('content_type', 'blog_post'),
                    content_data.get('target_audience', 'general')
                )
                
                # Schedule the content
                schedule_result = await self.scheduler_service.schedule_content({
                    'content_id': content_data.get('content_id'),
                    'publish_time': optimal_time,
                    'platforms': content_data.get('target_platforms', ['wordpress']),
                    'auto_generated': True
                })
                
                self.emit_event('content_scheduled', {
                    'schedule_id': schedule_result.get('schedule_id'),
                    'content_id': content_data.get('content_id'),
                    'publish_time': optimal_time.isoformat(),
                    'platforms': content_data.get('target_platforms', ['wordpress'])
                })
                
            except Exception as e:
                self.logger.error(f"Auto-scheduling failed: {e}")
    
    async def _on_publish_requested(self, event):
        """Handle publish requests from other modules"""
        try:
            publish_data = event.data
            
            # Execute the publishing
            result = await self.scheduler_service.execute_publish(publish_data)
            
            self.emit_event('content_published', {
                'content_id': publish_data.get('content_id'),
                'platform': publish_data.get('platform'),
                'result': result,
                'published_at': result.get('published_at')
            })
            
        except Exception as e:
            self.logger.error(f"Publishing execution failed: {e}")
    
    async def health_check(self):
        """Health check for the scheduling module"""
        base_health = await super().health_check()
        
        # Check service health
        scheduler_ok = await self.scheduler_service.health_check()
        calendar_ok = await self.calendar_service.health_check()
        automation_ok = await self.automation_service.health_check()
        
        base_health.update({
            "scheduler_service_healthy": scheduler_ok,
            "calendar_service_healthy": calendar_ok,
            "automation_service_healthy": automation_ok,
            "active_schedules": await self.scheduler_service.get_active_schedules_count(),
            "pending_publications": await self.scheduler_service.get_pending_count()
        })
        
        return base_health
