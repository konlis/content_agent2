"""
Scheduling Module API Routes
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from loguru import logger

# Pydantic models for request/response validation
class ScheduleRequest(BaseModel):
    content_id: str = Field(..., description="ID of content to schedule")
    publish_time: datetime = Field(..., description="When to publish the content")
    platforms: List[str] = Field(..., description="Target platforms for publishing")
    frequency: str = Field("once", description="Publishing frequency")
    timezone: Optional[str] = Field("UTC", description="Timezone for scheduling")
    retry_attempts: Optional[int] = Field(3, description="Number of retry attempts")
    notification_enabled: Optional[bool] = Field(True, description="Enable notifications")

class ScheduleResponse(BaseModel):
    schedule_id: str
    status: str
    publish_time: str
    platforms: List[str]
    task_id: str
    frequency: str

class WorkflowRequest(BaseModel):
    name: str = Field(..., description="Workflow name")
    description: Optional[str] = Field("", description="Workflow description")
    trigger: str = Field(..., description="Workflow trigger type")
    actions: List[Dict[str, Any]] = Field(..., description="Workflow actions")
    settings: Optional[Dict[str, Any]] = Field({}, description="Workflow settings")

class WorkflowResponse(BaseModel):
    workflow_id: str
    status: str
    name: str
    trigger: str
    actions_count: int

class CalendarEvent(BaseModel):
    id: str
    title: str
    start: str
    platforms: List[str]
    status: str
    content_type: str

# Create router
router = APIRouter()

# Dependency to get services
def get_scheduler_service():
    from core.container import get_container
    container = get_container()
    return container.get_service('scheduler_service')

def get_calendar_service():
    from core.container import get_container
    container = get_container()
    return container.get_service('calendar_service')

def get_automation_service():
    from core.container import get_container
    container = get_container()
    return container.get_service('automation_service')

# Schedule Management Endpoints
@router.post("/schedule", response_model=ScheduleResponse)
async def schedule_content(
    request: ScheduleRequest,
    scheduler_service = Depends(get_scheduler_service)
):
    """Schedule content for publishing"""
    try:
        logger.info(f"API: Scheduling content {request.content_id}")
        
        schedule_data = {
            'content_id': request.content_id,
            'publish_time': request.publish_time,
            'platforms': request.platforms,
            'frequency': request.frequency,
            'timezone': request.timezone,
            'retry_attempts': request.retry_attempts,
            'notification_enabled': request.notification_enabled
        }
        
        result = await scheduler_service.schedule_content(schedule_data)
        return ScheduleResponse(**result)
        
    except Exception as e:
        logger.error(f"API: Schedule content failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/schedule/{schedule_id}")
async def get_schedule(
    schedule_id: str,
    scheduler_service = Depends(get_scheduler_service)
):
    """Get schedule details by ID"""
    try:
        schedule = await scheduler_service._get_schedule(schedule_id)
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")
        return schedule
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Get schedule failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/schedule/{schedule_id}")
async def update_schedule(
    schedule_id: str,
    updates: Dict[str, Any],
    scheduler_service = Depends(get_scheduler_service)
):
    """Update an existing schedule"""
    try:
        await scheduler_service._update_schedule(schedule_id, updates)
        return {
            "schedule_id": schedule_id,
            "status": "updated",
            "updates": updates
        }
    except Exception as e:
        logger.error(f"API: Update schedule failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/schedule/{schedule_id}")
async def cancel_schedule(
    schedule_id: str,
    scheduler_service = Depends(get_scheduler_service)
):
    """Cancel a scheduled publication"""
    try:
        schedule = await scheduler_service._get_schedule(schedule_id)
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")
        
        task_id = schedule.get('task_id')
        if task_id:
            await scheduler_service._cancel_background_task(task_id)
        
        await scheduler_service._update_schedule(schedule_id, {
            'status': 'cancelled',
            'cancelled_at': datetime.utcnow()
        })
        
        return {"schedule_id": schedule_id, "status": "cancelled"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Cancel schedule failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Calendar Endpoints
@router.get("/calendar", response_model=List[CalendarEvent])
async def get_content_calendar(
    start_date: datetime = Query(..., description="Calendar start date"),
    end_date: datetime = Query(..., description="Calendar end date"),
    scheduler_service = Depends(get_scheduler_service)
):
    """Get content calendar for specified date range"""
    try:
        calendar_data = await scheduler_service.get_content_calendar(start_date, end_date)
        return [CalendarEvent(**item) for item in calendar_data]
    except Exception as e:
        logger.error(f"API: Get calendar failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/optimal-times")
async def get_optimal_posting_times(
    content_type: str = Query("blog_post", description="Type of content"),
    platforms: List[str] = Query(["wordpress"], description="Target platforms"),
    industry: Optional[str] = Query(None, description="Industry vertical"),
    scheduler_service = Depends(get_scheduler_service),
    calendar_service = Depends(get_calendar_service)
):
    """Get optimal posting times for content and platforms"""
    try:
        optimal_times = await scheduler_service.get_optimal_posting_times(content_type, platforms)
        
        industry_optimal = await calendar_service.get_optimal_posting_time(
            content_type, 
            industry=industry
        ) if industry else None
        
        return {
            "content_type": content_type,
            "platforms": platforms,
            "optimal_times": {
                platform: time.isoformat() 
                for platform, time in optimal_times.items()
            },
            "industry_recommendation": industry_optimal.isoformat() if industry_optimal else None,
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"API: Get optimal times failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Publishing Endpoints
@router.post("/publish/{schedule_id}")
async def execute_publish_now(
    schedule_id: str,
    scheduler_service = Depends(get_scheduler_service)
):
    """Execute publishing immediately for a scheduled item"""
    try:
        schedule = await scheduler_service._get_schedule(schedule_id)
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")
        
        # Execute publish for each platform
        results = []
        for platform in schedule.get('platforms', []):
            publish_data = {
                'content_id': schedule['content_id'],
                'platform': platform,
                'schedule_id': schedule_id
            }
            
            result = await scheduler_service.execute_publish(publish_data)
            results.append(result)
        
        return {
            "schedule_id": schedule_id,
            "status": "published",
            "results": results,
            "published_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Execute publish failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Automation Workflows Endpoints
@router.post("/workflows", response_model=WorkflowResponse)
async def create_workflow(
    request: WorkflowRequest,
    automation_service = Depends(get_automation_service)
):
    """Create a new automation workflow"""
    try:
        workflow_config = request.dict()
        result = await automation_service.create_workflow(workflow_config)
        return WorkflowResponse(**result)
    except Exception as e:
        logger.error(f"API: Create workflow failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/workflows/templates")
async def get_workflow_templates(
    automation_service = Depends(get_automation_service)
):
    """Get available workflow templates"""
    try:
        templates = await automation_service.get_workflow_templates()
        return {"templates": templates}
    except Exception as e:
        logger.error(f"API: Get templates failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workflows/from-template/{template_id}")
async def create_workflow_from_template(
    template_id: str,
    customizations: Optional[Dict[str, Any]] = None,
    automation_service = Depends(get_automation_service)
):
    """Create workflow from template"""
    try:
        result = await automation_service.create_workflow_from_template(
            template_id, 
            customizations or {}
        )
        return result
    except Exception as e:
        logger.error(f"API: Create workflow from template failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/workflows/{workflow_id}/execute")
async def execute_workflow(
    workflow_id: str,
    trigger_data: Optional[Dict[str, Any]] = None,
    automation_service = Depends(get_automation_service)
):
    """Execute a workflow manually"""
    try:
        result = await automation_service.execute_workflow(workflow_id, trigger_data)
        return result
    except Exception as e:
        logger.error(f"API: Execute workflow failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/workflows/{workflow_id}/pause")
async def pause_workflow(
    workflow_id: str,
    automation_service = Depends(get_automation_service)
):
    """Pause a workflow"""
    try:
        success = await automation_service.pause_workflow(workflow_id)
        if not success:
            raise HTTPException(status_code=404, detail="Workflow not found")
        return {"workflow_id": workflow_id, "status": "paused"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Pause workflow failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/workflows/{workflow_id}/resume")
async def resume_workflow(
    workflow_id: str,
    automation_service = Depends(get_automation_service)
):
    """Resume a paused workflow"""
    try:
        success = await automation_service.resume_workflow(workflow_id)
        if not success:
            raise HTTPException(status_code=404, detail="Workflow not found or not paused")
        return {"workflow_id": workflow_id, "status": "active"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Resume workflow failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workflows/{workflow_id}/history")
async def get_workflow_history(
    workflow_id: str,
    limit: int = Query(50, description="Maximum number of executions to return"),
    automation_service = Depends(get_automation_service)
):
    """Get workflow execution history"""
    try:
        history = await automation_service.get_workflow_history(workflow_id, limit)
        return {"workflow_id": workflow_id, "history": history}
    except Exception as e:
        logger.error(f"API: Get workflow history failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Stats and Health Endpoints
@router.get("/stats")
async def get_scheduling_stats(
    scheduler_service = Depends(get_scheduler_service),
    automation_service = Depends(get_automation_service)
):
    """Get scheduling statistics"""
    try:
        active_schedules = await scheduler_service.get_active_schedules_count()
        pending_publications = await scheduler_service.get_pending_count()
        
        return {
            "active_schedules": active_schedules,
            "pending_publications": pending_publications,
            "automation_workflows": len(automation_service.active_workflows),
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"API: Get stats failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check(
    scheduler_service = Depends(get_scheduler_service),
    calendar_service = Depends(get_calendar_service),
    automation_service = Depends(get_automation_service)
):
    """Health check for scheduling services"""
    try:
        scheduler_healthy = await scheduler_service.health_check()
        calendar_healthy = await calendar_service.health_check()
        automation_healthy = await automation_service.health_check()
        
        overall_healthy = all([scheduler_healthy, calendar_healthy, automation_healthy])
        
        return {
            "status": "healthy" if overall_healthy else "degraded",
            "services": {
                "scheduler": scheduler_healthy,
                "calendar": calendar_healthy,
                "automation": automation_healthy
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"API: Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
