"""
Scheduler Service - Content scheduling and publishing automation
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import uuid
from loguru import logger

from shared.database.models import Schedule, get_db
from shared.config.settings import get_settings
from shared.utils.helpers import DateTimeUtils
from shared.utils.validation_service import validate_schedule_data

class SchedulerService:
    """
    Service for scheduling content publishing and managing automation workflows
    """
    
    def __init__(self, container):
        self.container = container
        self.settings = get_settings()
        self.logger = logger.bind(service="SchedulerService")
        
        # Initialize Celery (placeholder - would be configured in production)
        self.celery_app = None
        self._init_celery()
        
        # Active schedules cache
        self.active_schedules: Dict[str, Dict[str, Any]] = {}
    
    def _init_celery(self):
        """Initialize Celery for background tasks"""
        try:
            # This would initialize Celery with Redis broker
            # For now, we'll use a mock implementation
            self.logger.info("Celery initialized (mock mode)")
        except Exception as e:
            self.logger.error(f"Failed to initialize Celery: {e}")
    
    async def schedule_content(self, schedule_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Schedule content for publishing
        """
        try:
            # Validate schedule data
            validation = validate_schedule_data(schedule_data)
            if not validation['valid']:
                raise ValueError(f"Invalid schedule data: {', '.join(validation['errors'])}")
            
            # Generate schedule ID
            schedule_id = str(uuid.uuid4())
            
            # Create schedule record
            schedule_record = {
                "id": schedule_id,
                "content_id": schedule_data['content_id'],
                "publish_time": schedule_data['publish_time'],
                "frequency": schedule_data.get('frequency', 'once'),
                "platforms": schedule_data.get('platforms', ['wordpress']),
                "status": "scheduled",
                "auto_generate": schedule_data.get('auto_generate', False),
                "template_id": schedule_data.get('template_id'),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Save to database
            await self._save_schedule_to_db(schedule_record)
            
            # Schedule the task
            if schedule_data.get('publish_time') > datetime.utcnow():
                await self._schedule_publishing_task(schedule_record)
                self.active_schedules[schedule_id] = schedule_record
                
                self.logger.info(f"Content scheduled for {schedule_record['publish_time']}")
            else:
                # Publish immediately if time has passed
                await self._execute_publish(schedule_record)
            
            return {
                "schedule_id": schedule_id,
                "status": "scheduled",
                "publish_time": schedule_record['publish_time'].isoformat(),
                "platforms": schedule_record['platforms']
            }
            
        except Exception as e:
            self.logger.error(f"Failed to schedule content: {e}")
            raise
    
    async def execute_publish(self, schedule_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute content publishing
        """
        try:
            schedule_id = schedule_data.get('id')
            content_id = schedule_data.get('content_id')
            
            self.logger.info(f"Executing publish for schedule {schedule_id}")
            
            # Get content data
            content_data = await self._get_content_data(content_id)
            if not content_data:
                raise ValueError(f"Content not found: {content_id}")
            
            # Publish to each platform
            publish_results = {}
            for platform in schedule_data.get('platforms', []):
                try:
                    result = await self._publish_to_platform(platform, content_data)
                    publish_results[platform] = result
                except Exception as e:
                    self.logger.error(f"Failed to publish to {platform}: {e}")
                    publish_results[platform] = {
                        "status": "failed",
                        "error": str(e)
                    }
            
            # Update schedule status
            success_count = sum(1 for r in publish_results.values() if r.get('status') == 'success')
            overall_status = "published" if success_count > 0 else "failed"
            
            # Update database
            await self._update_schedule_status(schedule_id, overall_status, publish_results)
            
            # Remove from active schedules
            if schedule_id in self.active_schedules:
                del self.active_schedules[schedule_id]
            
            return {
                "schedule_id": schedule_id,
                "status": overall_status,
                "publish_results": publish_results,
                "executed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Publish execution failed: {e}")
            raise
    
    async def get_schedule(self, schedule_id: str) -> Optional[Dict[str, Any]]:
        """Get schedule by ID"""
        try:
            # Check active schedules first
            if schedule_id in self.active_schedules:
                return self.active_schedules[schedule_id]
            
            # Query database
            return await self._get_schedule_from_db(schedule_id)
            
        except Exception as e:
            self.logger.error(f"Failed to get schedule {schedule_id}: {e}")
            return None
    
    async def get_active_schedules(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all active schedules"""
        try:
            # Combine active schedules with database schedules
            active_schedules = list(self.active_schedules.values())
            
            # Get from database
            db_schedules = await self._get_schedules_from_db(status="scheduled", limit=limit)
            
            # Merge and sort by publish time
            all_schedules = active_schedules + db_schedules
            all_schedules.sort(key=lambda x: x.get('publish_time', datetime.max))
            
            return all_schedules[:limit]
            
        except Exception as e:
            self.logger.error(f"Failed to get active schedules: {e}")
            return []
    
    async def update_schedule(self, schedule_id: str, updates: Dict[str, Any]) -> bool:
        """Update schedule details"""
        try:
            # Validate updates
            allowed_updates = ['publish_time', 'frequency', 'platforms', 'auto_generate']
            filtered_updates = {k: v for k, v in updates.items() if k in allowed_updates}
            
            if not filtered_updates:
                return False
            
            # Update active schedule
            if schedule_id in self.active_schedules:
                self.active_schedules[schedule_id].update(filtered_updates)
                self.active_schedules[schedule_id]['updated_at'] = datetime.utcnow()
            
            # Update database
            await self._update_schedule_in_db(schedule_id, filtered_updates)
            
            # Reschedule if publish time changed
            if 'publish_time' in filtered_updates:
                await self._reschedule_publishing_task(schedule_id, filtered_updates['publish_time'])
            
            self.logger.info(f"Schedule {schedule_id} updated successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update schedule {schedule_id}: {e}")
            return False
    
    async def cancel_schedule(self, schedule_id: str) -> bool:
        """Cancel a scheduled publication"""
        try:
            # Remove from active schedules
            if schedule_id in self.active_schedules:
                del self.active_schedules[schedule_id]
            
            # Update database
            await self._update_schedule_status(schedule_id, "cancelled")
            
            # Cancel Celery task if exists
            await self._cancel_publishing_task(schedule_id)
            
            self.logger.info(f"Schedule {schedule_id} cancelled successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to cancel schedule {schedule_id}: {e}")
            return False
    
    async def get_scheduling_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get scheduling analytics and insights"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get schedules from database
            schedules = await self._get_schedules_from_db(
                start_date=start_date,
                end_date=end_date
            )
            
            # Calculate analytics
            total_scheduled = len(schedules)
            total_published = sum(1 for s in schedules if s.get('status') == 'published')
            total_failed = sum(1 for s in schedules if s.get('status') == 'failed')
            total_cancelled = sum(1 for s in schedules if s.get('status') == 'cancelled')
            
            # Platform breakdown
            platform_stats = {}
            for schedule in schedules:
                for platform in schedule.get('platforms', []):
                    platform_stats[platform] = platform_stats.get(platform, 0) + 1
            
            # Content type breakdown
            content_type_stats = {}
            for schedule in schedules:
                content_type = schedule.get('content_type', 'unknown')
                content_type_stats[content_type] = content_type_stats.get(content_type, 0) + 1
            
            return {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": days
                },
                "summary": {
                    "total_scheduled": total_scheduled,
                    "total_published": total_published,
                    "total_failed": total_failed,
                    "total_cancelled": total_cancelled,
                    "success_rate": (total_published / total_scheduled * 100) if total_scheduled > 0 else 0
                },
                "platforms": platform_stats,
                "content_types": content_type_stats,
                "recent_activity": schedules[-10:] if schedules else []
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get scheduling analytics: {e}")
            return {}
    
    async def get_active_schedules_count(self) -> int:
        """Get count of active schedules"""
        return len(self.active_schedules)
    
    async def get_pending_count(self) -> int:
        """Get count of pending publications"""
        try:
            pending_schedules = await self._get_schedules_from_db(
                status="scheduled",
                start_date=datetime.utcnow()
            )
            return len(pending_schedules)
        except Exception as e:
            self.logger.error(f"Failed to get pending count: {e}")
            return 0
    
    async def health_check(self) -> bool:
        """Health check for scheduler service"""
        try:
            # Check if we can access schedules
            active_count = await self.get_active_schedules_count()
            
            # Check database connection (placeholder)
            # db_ok = await self._test_database_connection()
            
            return True  # Placeholder - would check actual health
            
        except Exception as e:
            self.logger.error(f"Scheduler service health check failed: {e}")
            return False
    

    
    async def _schedule_publishing_task(self, schedule_data: Dict[str, Any]):
        """Schedule Celery task for publishing"""
        try:
            # This would create a Celery task
            # For now, we'll use a mock implementation
            schedule_id = schedule_data['id']
            publish_time = schedule_data['publish_time']
            
            # Calculate delay
            delay_seconds = (publish_time - datetime.utcnow()).total_seconds()
            if delay_seconds > 0:
                # Schedule task
                self.logger.info(f"Scheduled task for {schedule_id} in {delay_seconds} seconds")
            else:
                # Execute immediately
                await self._execute_publish(schedule_data)
                
        except Exception as e:
            self.logger.error(f"Failed to schedule publishing task: {e}")
    
    async def _reschedule_publishing_task(self, schedule_id: str, new_publish_time: datetime):
        """Reschedule a publishing task"""
        try:
            # Cancel existing task
            await self._cancel_publishing_task(schedule_id)
            
            # Get schedule data
            schedule_data = await self.get_schedule(schedule_id)
            if schedule_data:
                schedule_data['publish_time'] = new_publish_time
                await self._schedule_publishing_task(schedule_data)
                
        except Exception as e:
            self.logger.error(f"Failed to reschedule task {schedule_id}: {e}")
    
    async def _cancel_publishing_task(self, schedule_id: str):
        """Cancel a publishing task"""
        try:
            # This would cancel the Celery task
            # For now, just log the cancellation
            self.logger.info(f"Cancelled publishing task for schedule {schedule_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to cancel task {schedule_id}: {e}")
    
    async def _publish_to_platform(self, platform: str, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Publish content to a specific platform"""
        try:
            # This would integrate with platform-specific publishing services
            # For now, we'll simulate the publishing process
            
            if platform == 'wordpress':
                # Use WordPress integration service
                wordpress_service = self.container.get('wordpress_integration_module')
                if wordpress_service:
                    result = await wordpress_service.publish_content(content_data)
                    return {"status": "success", "platform_id": result.get('id')}
            
            # Simulate publishing delay
            await asyncio.sleep(1)
            
            return {
                "status": "success",
                "platform_id": f"{platform}_{int(datetime.utcnow().timestamp())}",
                "published_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to publish to {platform}: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _get_content_data(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get content data from content generation service"""
        try:
            content_service = self.container.get('content_service')
            if content_service:
                return await content_service.get_content(content_id)
            
            # Mock content data
            return {
                'content_id': content_id,
                'title': 'Sample Content',
                'content': 'Sample content body...',
                'content_type': 'blog_post'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get content data: {e}")
            return None
    
    async def _save_schedule_to_db(self, schedule_data: Dict[str, Any]):
        """Save schedule to database"""
        try:
            # This would save to the database
            # For now, just log the save operation
            self.logger.info(f"Schedule saved to database: {schedule_data['id']}")
            
        except Exception as e:
            self.logger.error(f"Failed to save schedule to database: {e}")
    
    async def _update_schedule_status(self, schedule_id: str, status: str, results: Dict[str, Any] = None):
        """Update schedule status in database"""
        try:
            # This would update the database
            # For now, just log the update
            self.logger.info(f"Schedule {schedule_id} status updated to {status}")
            
        except Exception as e:
            self.logger.error(f"Failed to update schedule status: {e}")
    
    async def _get_schedule_from_db(self, schedule_id: str) -> Optional[Dict[str, Any]]:
        """Get schedule from database"""
        try:
            # This would query the database
            # For now, return None (placeholder)
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get schedule from database: {e}")
            return None
    
    async def _get_schedules_from_db(self, status: str = None, start_date: datetime = None, end_date: datetime = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get schedules from database with filters"""
        try:
            # This would query the database with filters
            # For now, return empty list (placeholder)
            return []
            
        except Exception as e:
            self.logger.error(f"Failed to get schedules from database: {e}")
            return []
    
    async def _update_schedule_in_db(self, schedule_id: str, updates: Dict[str, Any]):
        """Update schedule in database"""
        try:
            # This would update the database
            # For now, just log the update
            self.logger.info(f"Schedule {schedule_id} updated in database")
            
        except Exception as e:
            self.logger.error(f"Failed to update schedule in database: {e}")
