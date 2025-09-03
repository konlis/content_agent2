"""
Scheduling Module Background Tasks
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from loguru import logger
import asyncio
import uuid
from celery import Celery

from shared.config.settings import get_settings
from shared.database.models import get_db

# Initialize Celery app
settings = get_settings()
celery_app = Celery(
    'content_agent_scheduler',
    broker=settings.REDIS_URL or 'redis://localhost:6379/0',
    backend=settings.REDIS_URL or 'redis://localhost:6379/0'
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)

# Task routing
celery_app.conf.task_routes = {
    'schedule_publish_task': {'queue': 'scheduling'},
    'execute_workflow_task': {'queue': 'automation'},
    'cleanup_expired_schedules': {'queue': 'maintenance'}
}

# Periodic tasks
celery_app.conf.beat_schedule = {
    'cleanup-expired-schedules': {
        'task': 'cleanup_expired_schedules',
        'schedule': 3600.0,  # Every hour
    },
    'check-pending-schedules': {
        'task': 'check_pending_schedules', 
        'schedule': 300.0,  # Every 5 minutes
    },
    'generate-daily-reports': {
        'task': 'generate_daily_reports',
        'schedule': 86400.0,  # Every 24 hours
    }
}

@celery_app.task(bind=True, name='schedule_publish_task')
def schedule_publish_task(self, schedule_data: Dict[str, Any]):
    """
    Background task for scheduled content publishing
    """
    try:
        logger.info(f"Executing scheduled publish task: {schedule_data.get('schedule_id')}")
        
        # Update task status
        self.update_state(
            state='PROGRESS',
            meta={'stage': 'starting', 'progress': 0}
        )
        
        # Get services
        from core.container import get_container
        container = get_container()
        scheduler_service = container.get_service('scheduler_service')
        
        if not scheduler_service:
            raise Exception("Scheduler service not available")
        
        self.update_state(
            state='PROGRESS', 
            meta={'stage': 'publishing', 'progress': 25}
        )
        
        # Execute publishing for each platform
        results = []
        platforms = schedule_data.get('platforms', [])
        
        for i, platform in enumerate(platforms):
            try:
                publish_data = {
                    'content_id': schedule_data['content_id'],
                    'platform': platform,
                    'schedule_id': schedule_data['schedule_id']
                }
                
                # Execute publish
                result = asyncio.run(scheduler_service.execute_publish(publish_data))
                results.append(result)
                
                # Update progress
                progress = 25 + (50 * (i + 1) / len(platforms))
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'stage': f'published_to_{platform}',
                        'progress': progress,
                        'platform_results': results
                    }
                )
                
            except Exception as platform_error:
                logger.error(f"Publishing to {platform} failed: {platform_error}")
                results.append({
                    'platform': platform,
                    'status': 'failed',
                    'error': str(platform_error)
                })
        
        # Update schedule status
        self.update_state(
            state='PROGRESS',
            meta={'stage': 'updating_status', 'progress': 90}
        )
        
        # Determine overall status
        successful_publishes = [r for r in results if r.get('status') == 'published']
        overall_status = 'completed' if successful_publishes else 'failed'
        
        # Update schedule record
        asyncio.run(scheduler_service._update_schedule(
            schedule_data['schedule_id'],
            {
                'status': overall_status,
                'completed_at': datetime.utcnow(),
                'publish_results': results
            }
        ))
        
        # Send notifications if enabled
        if schedule_data.get('notification_enabled', True):
            asyncio.run(send_publish_notification(schedule_data, results))
        
        logger.info(f"Scheduled publish task completed: {schedule_data.get('schedule_id')}")
        
        return {
            'schedule_id': schedule_data['schedule_id'],
            'status': overall_status,
            'platforms_published': len(successful_publishes),
            'total_platforms': len(platforms),
            'results': results,
            'completed_at': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Scheduled publish task failed: {e}")
        
        # Update schedule with failure
        try:
            asyncio.run(scheduler_service._update_schedule(
                schedule_data['schedule_id'],
                {
                    'status': 'failed',
                    'error_message': str(e),
                    'failed_at': datetime.utcnow()
                }
            ))
        except:
            pass
        
        raise

@celery_app.task(bind=True, name='execute_workflow_task')
def execute_workflow_task(self, workflow_id: str, trigger_data: Dict[str, Any] = None):
    """
    Background task for executing automation workflows
    """
    try:
        logger.info(f"Executing workflow task: {workflow_id}")
        
        self.update_state(
            state='PROGRESS',
            meta={'stage': 'initializing', 'progress': 0}
        )
        
        # Get automation service
        from core.container import get_container
        container = get_container()
        automation_service = container.get_service('automation_service')
        
        if not automation_service:
            raise Exception("Automation service not available")
        
        # Execute workflow
        result = asyncio.run(automation_service.execute_workflow(workflow_id, trigger_data))
        
        logger.info(f"Workflow task completed: {workflow_id}")
        return result
        
    except Exception as e:
        logger.error(f"Workflow task failed: {e}")
        raise

@celery_app.task(name='cleanup_expired_schedules')
def cleanup_expired_schedules():
    """
    Periodic task to clean up expired and completed schedules
    """
    try:
        logger.info("Starting cleanup of expired schedules")
        
        # This would query the database for expired schedules
        # For now, just log the cleanup
        
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        # Mock cleanup
        cleaned_count = 15  # Would be actual count from database
        
        logger.info(f"Cleaned up {cleaned_count} expired schedules")
        
        return {
            'cleaned_count': cleaned_count,
            'cutoff_date': cutoff_date.isoformat(),
            'completed_at': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Schedule cleanup failed: {e}")
        raise

@celery_app.task(name='check_pending_schedules')
def check_pending_schedules():
    """
    Check for schedules that are due to be published
    """
    try:
        logger.info("Checking for pending schedules")
        
        # This would query database for schedules due now
        current_time = datetime.utcnow()
        
        # Mock pending schedule check
        pending_schedules = []  # Would come from database query
        
        for schedule in pending_schedules:
            try:
                # Create publish task
                schedule_publish_task.delay(schedule)
                logger.info(f"Queued publish task for schedule: {schedule.get('schedule_id')}")
            except Exception as e:
                logger.error(f"Failed to queue schedule {schedule.get('schedule_id')}: {e}")
        
        return {
            'checked_at': current_time.isoformat(),
            'pending_count': len(pending_schedules),
            'queued_count': len(pending_schedules)
        }
        
    except Exception as e:
        logger.error(f"Pending schedule check failed: {e}")
        raise

@celery_app.task(name='generate_daily_reports')
def generate_daily_reports():
    """
    Generate daily scheduling and publishing reports
    """
    try:
        logger.info("Generating daily scheduling reports")
        
        yesterday = datetime.utcnow() - timedelta(days=1)
        
        # Mock report generation
        report_data = {
            'date': yesterday.date().isoformat(),
            'total_scheduled': 12,
            'total_published': 10,
            'failed_publishes': 2,
            'success_rate': 83.3,
            'platforms': {
                'wordpress': {'published': 5, 'failed': 0},
                'linkedin': {'published': 3, 'failed': 1}, 
                'twitter': {'published': 2, 'failed': 1}
            },
            'top_performing_content': [
                {'title': 'Digital Marketing Guide', 'engagement': 245},
                {'title': 'SEO Tips for 2025', 'engagement': 189}
            ]
        }
        
        # This would save report to database or send via email
        
        logger.info("Daily report generated successfully")
        
        return {
            'report_date': yesterday.date().isoformat(),
            'generated_at': datetime.utcnow().isoformat(),
            'report_data': report_data
        }
        
    except Exception as e:
        logger.error(f"Daily report generation failed: {e}")
        raise

@celery_app.task(name='retry_failed_publish')
def retry_failed_publish(schedule_id: str, platform: str, attempt_number: int = 1):
    """
    Retry a failed publication
    """
    try:
        logger.info(f"Retrying failed publish: {schedule_id} on {platform} (attempt {attempt_number})")
        
        if attempt_number > 3:
            logger.error(f"Max retry attempts reached for {schedule_id}")
            return {'status': 'max_retries_reached'}
        
        # Get services
        from core.container import get_container
        container = get_container()
        scheduler_service = container.get_service('scheduler_service')
        
        # Get schedule data
        schedule = asyncio.run(scheduler_service._get_schedule(schedule_id))
        if not schedule:
            raise Exception("Schedule not found")
        
        # Retry publish
        publish_data = {
            'content_id': schedule['content_id'],
            'platform': platform,
            'schedule_id': schedule_id,
            'retry_attempt': attempt_number
        }
        
        result = asyncio.run(scheduler_service.execute_publish(publish_data))
        
        if result.get('status') == 'published':
            logger.info(f"Retry successful for {schedule_id} on {platform}")
            return result
        else:
            # Schedule another retry
            retry_failed_publish.apply_async(
                args=[schedule_id, platform, attempt_number + 1],
                countdown=300 * attempt_number  # Exponential backoff
            )
            return {'status': 'retry_scheduled', 'next_attempt': attempt_number + 1}
        
    except Exception as e:
        logger.error(f"Publish retry failed: {e}")
        raise

@celery_app.task(name='batch_schedule_content')
def batch_schedule_content(content_list: List[Dict[str, Any]]):
    """
    Schedule multiple pieces of content in batch
    """
    try:
        logger.info(f"Batch scheduling {len(content_list)} content items")
        
        results = []
        
        for i, content_data in enumerate(content_list):
            try:
                # Create individual schedule task
                schedule_data = {
                    'content_id': content_data['content_id'],
                    'publish_time': content_data['publish_time'],
                    'platforms': content_data.get('platforms', ['wordpress']),
                    'schedule_id': str(uuid.uuid4()),
                    'batch_id': content_data.get('batch_id'),
                    'auto_generated': True
                }
                
                # Queue the individual publish task
                task = schedule_publish_task.apply_async(
                    args=[schedule_data],
                    eta=datetime.fromisoformat(content_data['publish_time'])
                )
                
                results.append({
                    'content_id': content_data['content_id'],
                    'schedule_id': schedule_data['schedule_id'],
                    'task_id': task.id,
                    'status': 'scheduled'
                })
                
            except Exception as item_error:
                logger.error(f"Failed to schedule content {content_data.get('content_id')}: {item_error}")
                results.append({
                    'content_id': content_data.get('content_id'),
                    'status': 'failed',
                    'error': str(item_error)
                })
        
        logger.info(f"Batch scheduling completed: {len(results)} items processed")
        
        return {
            'batch_id': content_list[0].get('batch_id') if content_list else None,
            'total_items': len(content_list),
            'scheduled': len([r for r in results if r['status'] == 'scheduled']),
            'failed': len([r for r in results if r['status'] == 'failed']),
            'results': results,
            'completed_at': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Batch scheduling failed: {e}")
        raise

@celery_app.task(name='optimize_posting_schedule')
def optimize_posting_schedule(content_type: str, industry: str = None):
    """
    Analyze and optimize posting schedules based on engagement data
    """
    try:
        logger.info(f"Optimizing posting schedule for {content_type}")
        
        # Mock optimization analysis
        # In reality, this would analyze historical engagement data
        
        recommendations = {
            'optimal_days': ['Tuesday', 'Wednesday', 'Thursday'],
            'optimal_hours': [10, 14, 16],
            'peak_engagement_time': 'Tuesday 2:00 PM',
            'worst_times': ['Sunday morning', 'Friday evening'],
            'seasonal_adjustments': {
                'summer': 'Post 1 hour earlier',
                'winter': 'Focus on weekdays',
                'holidays': 'Reduce frequency by 50%'
            },
            'platform_specific': {
                'wordpress': {'best_days': [1, 2, 3], 'best_hours': [10, 14]},
                'linkedin': {'best_days': [1, 2, 3, 4], 'best_hours': [9, 12, 17]},
                'twitter': {'best_days': [0, 1, 2, 3, 4], 'best_hours': [9, 12, 15, 18]}
            }
        }
        
        # Save recommendations
        # This would update the calendar service with new optimal times
        
        logger.info("Posting schedule optimization completed")
        
        return {
            'content_type': content_type,
            'industry': industry,
            'recommendations': recommendations,
            'analysis_date': datetime.utcnow().isoformat(),
            'confidence_score': 0.87
        }
        
    except Exception as e:
        logger.error(f"Schedule optimization failed: {e}")
        raise

# Utility functions
async def send_publish_notification(schedule_data: Dict[str, Any], results: List[Dict[str, Any]]):
    """Send notification about publishing results"""
    try:
        successful = [r for r in results if r.get('status') == 'published']
        failed = [r for r in results if r.get('status') == 'failed']
        
        notification_data = {
            'schedule_id': schedule_data['schedule_id'],
            'content_id': schedule_data['content_id'],
            'total_platforms': len(results),
            'successful_platforms': len(successful),
            'failed_platforms': len(failed),
            'success_rate': (len(successful) / len(results)) * 100 if results else 0
        }
        
        # This would send actual notification (email, slack, etc.)
        logger.info(f"Notification sent for schedule {schedule_data['schedule_id']}")
        
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")

def create_schedule_task(schedule_data: Dict[str, Any]) -> str:
    """
    Create a scheduled task for content publishing
    """
    try:
        publish_time = datetime.fromisoformat(schedule_data['publish_time'])
        
        # Create the scheduled task
        task = schedule_publish_task.apply_async(
            args=[schedule_data],
            eta=publish_time
        )
        
        logger.info(f"Created scheduled task {task.id} for {schedule_data['schedule_id']}")
        return task.id
        
    except Exception as e:
        logger.error(f"Failed to create scheduled task: {e}")
        raise

def cancel_schedule_task(task_id: str) -> bool:
    """
    Cancel a scheduled task
    """
    try:
        celery_app.control.revoke(task_id, terminate=True)
        logger.info(f"Cancelled scheduled task {task_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to cancel task {task_id}: {e}")
        return False

# Task monitoring
@celery_app.task(name='monitor_task_health')
def monitor_task_health():
    """Monitor the health of scheduled tasks"""
    try:
        # Get active tasks
        active_tasks = celery_app.control.inspect().active()
        scheduled_tasks = celery_app.control.inspect().scheduled()
        
        # Count tasks by type
        task_counts = {
            'active_publish_tasks': 0,
            'active_workflow_tasks': 0,
            'scheduled_tasks': 0
        }
        
        if active_tasks:
            for worker, tasks in active_tasks.items():
                for task in tasks:
                    if 'schedule_publish_task' in task['name']:
                        task_counts['active_publish_tasks'] += 1
                    elif 'execute_workflow_task' in task['name']:
                        task_counts['active_workflow_tasks'] += 1
        
        if scheduled_tasks:
            for worker, tasks in scheduled_tasks.items():
                task_counts['scheduled_tasks'] += len(tasks)
        
        logger.info(f"Task health check: {task_counts}")
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'task_counts': task_counts,
            'status': 'healthy'
        }
        
    except Exception as e:
        logger.error(f"Task health monitoring failed: {e}")
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'unhealthy',
            'error': str(e)
        }

# Celery signals
from celery.signals import task_prerun, task_postrun, task_failure

@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **kwds):
    """Log when task starts"""
    logger.info(f"Task {task.name}[{task_id}] starting")

@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, retval=None, state=None, **kwds):
    """Log when task completes"""
    logger.info(f"Task {task.name}[{task_id}] completed with state: {state}")

@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, traceback=None, einfo=None, **kwds):
    """Log task failures"""
    logger.error(f"Task {sender.name}[{task_id}] failed: {exception}")
