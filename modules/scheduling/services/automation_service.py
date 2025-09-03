"""
Automation Service - Automated content workflows and publishing
"""

import asyncio
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
import uuid
from loguru import logger

from shared.config.settings import get_settings
from shared.utils.helpers import DateTimeUtils
from shared.utils.validation_service import validate_workflow_config

class AutomationTrigger(Enum):
    """Automation trigger types"""
    TIME_BASED = "time_based"
    CONTENT_GENERATED = "content_generated"
    KEYWORD_RESEARCH = "keyword_research"
    MANUAL = "manual"
    WEBHOOK = "webhook"

class AutomationAction(Enum):
    """Automation action types"""
    SCHEDULE_PUBLISH = "schedule_publish"
    GENERATE_CONTENT = "generate_content"
    OPTIMIZE_SEO = "optimize_seo"
    SEND_NOTIFICATION = "send_notification"
    CREATE_SOCIAL_MEDIA = "create_social_media"

class WorkflowStatus(Enum):
    """Workflow execution status"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class AutomationService:
    """
    Service for managing automated content workflows and publishing
    """
    
    def __init__(self, container):
        self.container = container
        self.settings = get_settings()
        self.logger = logger.bind(service="AutomationService")
        
        # Active workflows
        self.active_workflows = {}
        
        # Workflow templates
        self.workflow_templates = {
            "blog_automation": {
                "name": "Blog Post Automation",
                "description": "Automatically generate and schedule blog posts based on keyword research",
                "trigger": AutomationTrigger.KEYWORD_RESEARCH,
                "actions": [
                    {"type": AutomationAction.GENERATE_CONTENT, "delay": 0},
                    {"type": AutomationAction.OPTIMIZE_SEO, "delay": 300},  # 5 minutes
                    {"type": AutomationAction.SCHEDULE_PUBLISH, "delay": 600}  # 10 minutes
                ]
            },
            "social_media_automation": {
                "name": "Social Media Automation",
                "description": "Create and schedule social media posts from blog content",
                "trigger": AutomationTrigger.CONTENT_GENERATED,
                "actions": [
                    {"type": AutomationAction.CREATE_SOCIAL_MEDIA, "delay": 0},
                    {"type": AutomationAction.SCHEDULE_PUBLISH, "delay": 300}
                ]
            },
            "daily_content": {
                "name": "Daily Content Pipeline",
                "description": "Generate daily content based on trending keywords",
                "trigger": AutomationTrigger.TIME_BASED,
                "schedule": "0 9 * * *",  # Every day at 9 AM
                "actions": [
                    {"type": AutomationAction.GENERATE_CONTENT, "delay": 0},
                    {"type": AutomationAction.SCHEDULE_PUBLISH, "delay": 1800}  # 30 minutes
                ]
            }
        }
    
    async def create_workflow(self, workflow_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new automation workflow
        """
        try:
            workflow_id = str(uuid.uuid4())
            
            # Validate workflow configuration
            validation = validate_workflow_config(workflow_config)
            if not validation['valid']:
                raise ValueError(f"Invalid workflow config: {', '.join(validation['errors'])}")
            
            # Create workflow data
            workflow_data = {
                'workflow_id': workflow_id,
                'name': workflow_config.get('name', f'Workflow {workflow_id[:8]}'),
                'description': workflow_config.get('description', ''),
                'trigger': workflow_config['trigger'],
                'actions': workflow_config['actions'],
                'status': WorkflowStatus.ACTIVE.value,
                'created_at': datetime.utcnow(),
                'settings': workflow_config.get('settings', {}),
                'metadata': {
                    'execution_count': 0,
                    'success_count': 0,
                    'failure_count': 0,
                    'last_execution': None,
                    'next_execution': self._calculate_next_execution(workflow_config)
                }
            }
            
            # Save workflow
            await self._save_workflow(workflow_data)
            
            # Register workflow for execution
            self.active_workflows[workflow_id] = workflow_data
            
            # Setup trigger handlers
            await self._setup_workflow_triggers(workflow_data)
            
            self.logger.info(f"Created automation workflow: {workflow_id}")
            
            return {
                'workflow_id': workflow_id,
                'status': 'created',
                'name': workflow_data['name'],
                'trigger': workflow_data['trigger'],
                'actions_count': len(workflow_data['actions'])
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create workflow: {e}")
            raise
    
    async def execute_workflow(self, workflow_id: str, trigger_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a specific workflow
        """
        try:
            workflow = self.active_workflows.get(workflow_id)
            if not workflow:
                workflow = await self._load_workflow(workflow_id)
                if not workflow:
                    raise ValueError(f"Workflow not found: {workflow_id}")
            
            execution_id = str(uuid.uuid4())
            
            self.logger.info(f"Executing workflow {workflow_id} (execution: {execution_id})")
            
            # Update execution metadata
            workflow['metadata']['execution_count'] += 1
            workflow['metadata']['last_execution'] = datetime.utcnow()
            
            # Execute actions sequentially
            execution_results = []
            context = {
                'workflow_id': workflow_id,
                'execution_id': execution_id,
                'trigger_data': trigger_data or {},
                'started_at': datetime.utcnow()
            }
            
            for i, action in enumerate(workflow['actions']):
                try:
                    # Apply delay if specified
                    delay = action.get('delay', 0)
                    if delay > 0:
                        await asyncio.sleep(delay)
                    
                    # Execute action
                    action_result = await self._execute_action(action, context)
                    execution_results.append({
                        'action_index': i,
                        'action_type': action['type'],
                        'status': 'success',
                        'result': action_result,
                        'executed_at': datetime.utcnow().isoformat()
                    })
                    
                    # Update context with result
                    context[f'action_{i}_result'] = action_result
                    
                except Exception as action_error:
                    execution_results.append({
                        'action_index': i,
                        'action_type': action['type'],
                        'status': 'failed',
                        'error': str(action_error),
                        'executed_at': datetime.utcnow().isoformat()
                    })
                    
                    # Stop execution on failure (unless configured to continue)
                    if not action.get('continue_on_failure', False):
                        break
            
            # Determine overall execution status
            failed_actions = [r for r in execution_results if r['status'] == 'failed']
            execution_status = 'failed' if failed_actions else 'success'
            
            # Update workflow statistics
            if execution_status == 'success':
                workflow['metadata']['success_count'] += 1
            else:
                workflow['metadata']['failure_count'] += 1
            
            # Calculate next execution time
            workflow['metadata']['next_execution'] = self._calculate_next_execution(workflow)
            
            # Save workflow updates
            await self._save_workflow(workflow)
            
            # Save execution record
            execution_record = {
                'execution_id': execution_id,
                'workflow_id': workflow_id,
                'status': execution_status,
                'started_at': context['started_at'],
                'completed_at': datetime.utcnow(),
                'trigger_data': trigger_data,
                'results': execution_results
            }
            await self._save_execution_record(execution_record)
            
            self.logger.info(f"Workflow execution completed: {execution_id} (status: {execution_status})")
            
            return {
                'execution_id': execution_id,
                'workflow_id': workflow_id,
                'status': execution_status,
                'actions_executed': len(execution_results),
                'actions_successful': len([r for r in execution_results if r['status'] == 'success']),
                'actions_failed': len(failed_actions),
                'execution_time': (datetime.utcnow() - context['started_at']).total_seconds(),
                'results': execution_results
            }
            
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {e}")
            raise
    
    async def _execute_action(self, action: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """Execute a specific workflow action"""
        action_type = AutomationAction(action['type'])
        
        if action_type == AutomationAction.SCHEDULE_PUBLISH:
            return await self._action_schedule_publish(action, context)
        elif action_type == AutomationAction.GENERATE_CONTENT:
            return await self._action_generate_content(action, context)
        elif action_type == AutomationAction.OPTIMIZE_SEO:
            return await self._action_optimize_seo(action, context)
        elif action_type == AutomationAction.SEND_NOTIFICATION:
            return await self._action_send_notification(action, context)
        elif action_type == AutomationAction.CREATE_SOCIAL_MEDIA:
            return await self._action_create_social_media(action, context)
        else:
            raise ValueError(f"Unknown action type: {action_type}")
    
    async def _action_schedule_publish(self, action: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule content for publishing"""
        try:
            # Get scheduler service
            scheduler_service = self.container.get_service('scheduler_service')
            
            # Prepare schedule request
            schedule_request = {
                'content_id': context.get('content_id') or action.get('content_id'),
                'platforms': action.get('platforms', ['wordpress']),
                'publish_time': action.get('publish_time') or (datetime.utcnow() + timedelta(hours=1)),
                'frequency': action.get('frequency', 'once'),
                'auto_generated': True
            }
            
            # Execute scheduling
            result = await scheduler_service.schedule_content(schedule_request)
            
            return {
                'action': 'schedule_publish',
                'schedule_id': result['schedule_id'],
                'platforms': result['platforms'],
                'publish_time': result['publish_time']
            }
            
        except Exception as e:
            self.logger.error(f"Schedule publish action failed: {e}")
            raise
    
    async def _action_generate_content(self, action: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content using AI"""
        try:
            # Get content generation service (if available)
            content_service = self.container.get_service('content_service')
            
            if not content_service:
                # Mock content generation
                content_id = str(uuid.uuid4())
                return {
                    'action': 'generate_content',
                    'content_id': content_id,
                    'title': 'Auto-Generated Content',
                    'status': 'generated'
                }
            
            # Prepare generation request
            generation_request = {
                'content_type': action.get('content_type', 'blog_post'),
                'keywords': action.get('keywords') or context.get('keywords', []),
                'tone': action.get('tone', 'professional'),
                'length': action.get('length', 'medium'),
                'auto_generated': True
            }
            
            # Generate content
            result = await content_service.generate_content(generation_request)
            
            # Store content_id in context for next actions
            context['content_id'] = result['content_id']
            
            return {
                'action': 'generate_content',
                'content_id': result['content_id'],
                'title': result.get('title', 'Generated Content'),
                'word_count': result.get('word_count', 0)
            }
            
        except Exception as e:
            self.logger.error(f"Generate content action failed: {e}")
            raise
    
    async def _action_optimize_seo(self, action: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize content for SEO"""
        try:
            # Mock SEO optimization
            await asyncio.sleep(2)  # Simulate processing
            
            return {
                'action': 'optimize_seo',
                'content_id': context.get('content_id'),
                'seo_score': 85,
                'optimizations_applied': ['title_optimization', 'meta_description', 'keyword_density']
            }
            
        except Exception as e:
            self.logger.error(f"SEO optimization action failed: {e}")
            raise
    
    async def _action_send_notification(self, action: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Send notification"""
        try:
            # Mock notification sending
            notification_type = action.get('type', 'email')
            recipients = action.get('recipients', ['admin@example.com'])
            
            await asyncio.sleep(1)  # Simulate sending
            
            return {
                'action': 'send_notification',
                'type': notification_type,
                'recipients': recipients,
                'status': 'sent'
            }
            
        except Exception as e:
            self.logger.error(f"Send notification action failed: {e}")
            raise
    
    async def _action_create_social_media(self, action: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Create social media posts from content"""
        try:
            # Mock social media post creation
            content_id = context.get('content_id')
            platforms = action.get('platforms', ['twitter', 'linkedin'])
            
            await asyncio.sleep(1)  # Simulate creation
            
            social_posts = []
            for platform in platforms:
                post_id = str(uuid.uuid4())
                social_posts.append({
                    'platform': platform,
                    'post_id': post_id,
                    'content': f"Check out our latest content! #{platform} #content",
                    'status': 'created'
                })
            
            return {
                'action': 'create_social_media',
                'source_content_id': content_id,
                'posts': social_posts,
                'platforms': platforms
            }
            
        except Exception as e:
            self.logger.error(f"Create social media action failed: {e}")
            raise
    
    async def get_workflow_templates(self) -> List[Dict[str, Any]]:
        """Get available workflow templates"""
        return [
            {
                'template_id': template_id,
                **template_data
            }
            for template_id, template_data in self.workflow_templates.items()
        ]
    
    async def create_workflow_from_template(self, template_id: str, customizations: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create workflow from template"""
        template = self.workflow_templates.get(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        
        # Start with template
        workflow_config = template.copy()
        
        # Apply customizations
        if customizations:
            workflow_config.update(customizations)
        
        # Create workflow
        return await self.create_workflow(workflow_config)
    
    async def pause_workflow(self, workflow_id: str) -> bool:
        """Pause a workflow"""
        try:
            workflow = self.active_workflows.get(workflow_id)
            if workflow:
                workflow['status'] = WorkflowStatus.PAUSED.value
                await self._save_workflow(workflow)
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to pause workflow: {e}")
            return False
    
    async def resume_workflow(self, workflow_id: str) -> bool:
        """Resume a paused workflow"""
        try:
            workflow = self.active_workflows.get(workflow_id)
            if workflow and workflow['status'] == WorkflowStatus.PAUSED.value:
                workflow['status'] = WorkflowStatus.ACTIVE.value
                await self._save_workflow(workflow)
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to resume workflow: {e}")
            return False
    
    async def get_workflow_history(self, workflow_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get workflow execution history"""
        # Mock implementation
        return [
            {
                'execution_id': f'exec_{i}',
                'workflow_id': workflow_id,
                'status': 'success' if i % 3 != 0 else 'failed',
                'started_at': (datetime.utcnow() - timedelta(days=i)).isoformat(),
                'execution_time': 45.5
            }
            for i in range(min(limit, 10))
        ]
    

    
    def _calculate_next_execution(self, workflow: Dict[str, Any]) -> Optional[datetime]:
        """Calculate next execution time for time-based workflows"""
        trigger = workflow.get('trigger')
        if trigger != AutomationTrigger.TIME_BASED.value:
            return None
        
        # Simple implementation: add 24 hours for daily schedule
        # In real implementation, would parse cron schedule
        schedule = workflow.get('schedule', '0 9 * * *')  # Default: 9 AM daily
        
        # For now, return tomorrow at 9 AM
        tomorrow = datetime.now() + timedelta(days=1)
        return tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)
    
    async def _setup_workflow_triggers(self, workflow: Dict[str, Any]) -> None:
        """Setup trigger handlers for workflow"""
        trigger = AutomationTrigger(workflow['trigger'])
        
        if trigger == AutomationTrigger.TIME_BASED:
            # Would setup cron-like scheduling
            pass
        elif trigger == AutomationTrigger.CONTENT_GENERATED:
            # Would subscribe to content_generated events
            pass
        elif trigger == AutomationTrigger.KEYWORD_RESEARCH:
            # Would subscribe to keyword_research events
            pass
    
    async def _save_workflow(self, workflow_data: Dict[str, Any]) -> None:
        """Save workflow to database"""
        # Mock implementation
        self.logger.info(f"Workflow saved: {workflow_data['workflow_id']}")
    
    async def _load_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Load workflow from database"""
        # Mock implementation
        return None
    
    async def _save_execution_record(self, execution_record: Dict[str, Any]) -> None:
        """Save execution record to database"""
        # Mock implementation
        self.logger.info(f"Execution record saved: {execution_record['execution_id']}")
    
    async def health_check(self) -> bool:
        """Check automation service health"""
        try:
            active_count = len(self.active_workflows)
            self.logger.info(f"Automation service healthy: {active_count} active workflows")
            return True
        except Exception as e:
            self.logger.error(f"Automation health check failed: {e}")
            return False
