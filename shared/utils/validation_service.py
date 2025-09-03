"""
Centralized Validation Service
Common validation patterns for Content Agent services
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import re
from shared.utils.logging_utils import ServiceLogger

class ValidationService:
    """Centralized validation service for common patterns"""
    
    def __init__(self):
        self.logger = ServiceLogger("ValidationService")
    
    def validate_content_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Validate content generation request"""
        errors = []
        
        # Required fields
        required_fields = ['primary_keyword', 'content_type']
        for field in required_fields:
            if not request.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Content type validation
        valid_content_types = ['blog_post', 'social_media', 'website_copy', 'newsletter', 'tutorial']
        content_type = request.get('content_type')
        if content_type and content_type not in valid_content_types:
            errors.append(f"Invalid content_type: {content_type}. Must be one of {valid_content_types}")
        
        # Keyword validation
        primary_keyword = request.get('primary_keyword', '')
        if primary_keyword:
            keyword_validation = self.validate_keyword(primary_keyword)
            if not keyword_validation['valid']:
                errors.extend(keyword_validation['issues'])
        
        # Word count validation
        target_word_count = request.get('target_word_count')
        if target_word_count and not isinstance(target_word_count, int):
            errors.append("target_word_count must be an integer")
        elif target_word_count and (target_word_count < 100 or target_word_count > 10000):
            errors.append("target_word_count must be between 100 and 10000")
        
        # Tone validation
        valid_tones = ['professional', 'casual', 'friendly', 'authoritative', 'conversational']
        tone = request.get('tone')
        if tone and tone not in valid_tones:
            errors.append(f"Invalid tone: {tone}. Must be one of {valid_tones}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def validate_schedule_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate scheduling request data"""
        errors = []
        
        # Required fields
        required_fields = ['content_id', 'publish_time']
        for field in required_fields:
            if not data.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Content ID validation
        content_id = data.get('content_id')
        if content_id and not isinstance(content_id, str):
            errors.append("content_id must be a string")
        
        # Publish time validation
        publish_time = data.get('publish_time')
        if publish_time:
            try:
                if isinstance(publish_time, str):
                    datetime.fromisoformat(publish_time.replace('Z', '+00:00'))
                elif isinstance(publish_time, datetime):
                    pass  # Already a datetime object
                else:
                    errors.append("publish_time must be a string or datetime object")
            except ValueError:
                errors.append("Invalid publish_time format")
        
        # Frequency validation
        valid_frequencies = ['once', 'daily', 'weekly', 'monthly']
        frequency = data.get('frequency')
        if frequency and frequency not in valid_frequencies:
            errors.append(f"Invalid frequency: {frequency}. Must be one of {valid_frequencies}")
        
        # Platforms validation
        platforms = data.get('platforms', [])
        if platforms and not isinstance(platforms, list):
            errors.append("platforms must be a list")
        elif platforms:
            valid_platforms = ['wordpress', 'linkedin', 'facebook', 'twitter', 'instagram']
            for platform in platforms:
                if platform not in valid_platforms:
                    errors.append(f"Invalid platform: {platform}. Must be one of {valid_platforms}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def validate_workflow_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate automation workflow configuration"""
        errors = []
        
        # Required fields
        required_fields = ['name', 'triggers', 'actions']
        for field in required_fields:
            if not config.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Name validation
        name = config.get('name')
        if name and not isinstance(name, str):
            errors.append("name must be a string")
        elif name and len(name.strip()) < 3:
            errors.append("name must be at least 3 characters long")
        
        # Triggers validation
        triggers = config.get('triggers', [])
        if triggers and not isinstance(triggers, list):
            errors.append("triggers must be a list")
        elif triggers:
            valid_trigger_types = ['schedule', 'event', 'manual', 'webhook']
            for trigger in triggers:
                trigger_type = trigger.get('type')
                if trigger_type not in valid_trigger_types:
                    errors.append(f"Invalid trigger type: {trigger_type}. Must be one of {valid_trigger_types}")
        
        # Actions validation
        actions = config.get('actions', [])
        if actions and not isinstance(actions, list):
            errors.append("actions must be a list")
        elif actions:
            valid_action_types = ['publish', 'generate', 'optimize', 'notify', 'social_media']
            for action in actions:
                action_type = action.get('type')
                if action_type not in valid_action_types:
                    errors.append(f"Invalid action type: {action_type}. Must be one of {valid_action_types}")
        
        # Schedule validation
        schedule = config.get('schedule')
        if schedule:
            schedule_validation = self.validate_schedule_data(schedule)
            if not schedule_validation['valid']:
                errors.extend([f"Schedule: {error}" for error in schedule_validation['errors']])
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def validate_keyword(self, keyword: str) -> Dict[str, Any]:
        """Validate keyword format"""
        issues = []
        
        if not keyword:
            issues.append("Keyword is empty")
        elif len(keyword) < 2:
            issues.append("Keyword too short")
        elif len(keyword) > 100:
            issues.append("Keyword too long")
        
        # Check for special characters
        if re.search(r'[^a-zA-Z0-9\s\-]', keyword):
            issues.append("Keyword contains special characters")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }
    
    def validate_email(self, email: str) -> bool:
        """Validate email address"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_url(self, url: str) -> bool:
        """Validate URL format"""
        try:
            from urllib.parse import urlparse
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def validate_content_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Validate content metadata"""
        errors = []
        
        # Title validation
        title = metadata.get('title', '')
        if not title:
            errors.append("Title is required")
        elif len(title) > 100:
            errors.append("Title too long (max 100 characters)")
        
        # Meta description validation
        meta_description = metadata.get('meta_description', '')
        if meta_description and len(meta_description) > 160:
            errors.append("Meta description too long (max 160 characters)")
        
        # Categories validation
        categories = metadata.get('categories', [])
        if categories and not isinstance(categories, list):
            errors.append("Categories must be a list")
        
        # Tags validation
        tags = metadata.get('tags', [])
        if tags and not isinstance(tags, list):
            errors.append("Tags must be a list")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

# Global validation service instance
validation_service = ValidationService()

# Convenience functions for quick validation
def validate_content_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """Quick validation for content requests"""
    return validation_service.validate_content_request(request)

def validate_schedule_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Quick validation for schedule data"""
    return validation_service.validate_schedule_data(data)

def validate_workflow_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Quick validation for workflow configs"""
    return validation_service.validate_workflow_config(config)
