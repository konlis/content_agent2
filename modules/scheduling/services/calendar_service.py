"""
Calendar Service - Calendar management and optimal posting time calculation
"""

import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import calendar
from loguru import logger

from shared.config.settings import get_settings
from shared.utils.helpers import DateTimeUtils

class CalendarService:
    """
    Service for managing content calendars and calculating optimal posting times
    """
    
    def __init__(self, container):
        self.container = container
        self.settings = get_settings()
        self.logger = logger.bind(service="CalendarService")
        
        # Platform-specific optimal posting configurations
        self.platform_configs = {
            "wordpress": {
                "optimal_hours": [9, 11, 14, 16],  # 9 AM, 11 AM, 2 PM, 4 PM
                "optimal_days": [1, 2, 3, 4],      # Tuesday, Wednesday, Thursday, Friday
                "content_types": ["blog_post", "article", "tutorial", "case_study"],
                "posting_frequency": "daily",
                "timezone": "UTC"
            },
            "linkedin": {
                "optimal_hours": [8, 12, 17],      # 8 AM, 12 PM, 5 PM
                "optimal_days": [0, 1, 2, 3, 4],  # Weekdays
                "content_types": ["professional", "industry_insights", "company_updates"],
                "posting_frequency": "daily",
                "timezone": "UTC"
            },
            "facebook": {
                "optimal_hours": [13, 15, 19],     # 1 PM, 3 PM, 7 PM
                "optimal_days": [2, 3, 5, 6],     # Wednesday, Thursday, Saturday, Sunday
                "content_types": ["social_media", "community", "promotional"],
                "posting_frequency": "daily",
                "timezone": "UTC"
            },
            "twitter": {
                "optimal_hours": [8, 12, 15, 18],  # Multiple times daily
                "optimal_days": [0, 1, 2, 3, 4],  # Weekdays
                "content_types": ["news", "quick_tips", "engagement"],
                "posting_frequency": "multiple_daily",
                "timezone": "UTC"
            },
            "instagram": {
                "optimal_hours": [11, 13, 17, 19], # 11 AM, 1 PM, 5 PM, 7 PM
                "optimal_days": [2, 3, 5, 6],     # Wednesday, Thursday, Saturday, Sunday
                "content_types": ["visual", "lifestyle", "brand"],
                "posting_frequency": "daily",
                "timezone": "UTC"
            }
        }
        
        # Content type specific timing adjustments
        self.content_type_adjustments = {
            "blog_post": {"time_adjustment": 0, "day_adjustment": 0},
            "social_media": {"time_adjustment": -1, "day_adjustment": 0},  # Earlier in day
            "newsletter": {"time_adjustment": 0, "day_adjustment": 1},      # Next business day
            "product_launch": {"time_adjustment": 2, "day_adjustment": 2},  # Later in week
            "case_study": {"time_adjustment": 0, "day_adjustment": 1}      # Business day
        }
    
    async def get_optimal_posting_time(
        self, 
        content_type: str, 
        target_audience: str = "general",
        platforms: List[str] = None,
        preferred_date: datetime = None
    ) -> Dict[str, Any]:
        """
        Calculate optimal posting time for content
        """
        try:
            if not platforms:
                platforms = ["wordpress"]
            
            self.logger.info(f"Calculating optimal posting time for {content_type} on {platforms}")
            
            # Get base optimal time
            base_time = preferred_date or datetime.utcnow()
            
            # Calculate optimal times for each platform
            platform_times = {}
            overall_optimal_time = None
            
            for platform in platforms:
                if platform in self.platform_configs:
                    optimal_time = await self._calculate_platform_optimal_time(
                        platform, content_type, target_audience, base_time
                    )
                    platform_times[platform] = optimal_time
                    
                    # Track overall optimal time
                    if not overall_optimal_time or optimal_time < overall_optimal_time:
                        overall_optimal_time = optimal_time
            
            # Apply content type adjustments
            if overall_optimal_time:
                overall_optimal_time = self._apply_content_type_adjustments(
                    overall_optimal_time, content_type
                )
            
            return {
                "overall_optimal_time": overall_optimal_time.isoformat() if overall_optimal_time else None,
                "platform_specific_times": platform_times,
                "content_type": content_type,
                "target_audience": target_audience,
                "platforms": platforms,
                "calculated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to calculate optimal posting time: {e}")
            raise
    
    async def get_content_calendar(
        self, 
        start_date: datetime, 
        end_date: datetime,
        platforms: List[str] = None,
        content_types: List[str] = None
    ) -> Dict[str, Any]:
        """
        Get content calendar for specified period
        """
        try:
            if not platforms:
                platforms = list(self.platform_configs.keys())
            
            if not content_types:
                content_types = ["blog_post", "social_media", "newsletter"]
            
            self.logger.info(f"Generating content calendar from {start_date} to {end_date}")
            
            # Generate calendar structure
            calendar_data = await self._generate_calendar_structure(start_date, end_date)
            
            # Add optimal posting times
            calendar_data = await self._add_optimal_posting_times(
                calendar_data, platforms, content_types
            )
            
            # Add content suggestions
            calendar_data = await self._add_content_suggestions(calendar_data, content_types)
            
            return {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "total_days": (end_date - start_date).days + 1
                },
                "platforms": platforms,
                "content_types": content_types,
                "calendar": calendar_data,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate content calendar: {e}")
            raise
    
    async def get_posting_schedule_recommendations(
        self, 
        content_count: int, 
        period_days: int = 30,
        platforms: List[str] = None,
        content_types: List[str] = None
    ) -> Dict[str, Any]:
        """
        Get recommendations for posting schedule
        """
        try:
            if not platforms:
                platforms = ["wordpress", "linkedin"]
            
            if not content_types:
                content_types = ["blog_post", "social_media"]
            
            self.logger.info(f"Generating posting schedule for {content_count} pieces over {period_days} days")
            
            # Calculate optimal distribution
            distribution = self._calculate_content_distribution(content_count, period_days, platforms)
            
            # Generate specific posting times
            posting_times = await self._generate_posting_schedule(
                distribution, platforms, content_types, period_days
            )
            
            # Add engagement predictions
            engagement_predictions = self._predict_engagement(posting_times, platforms)
            
            return {
                "content_count": content_count,
                "period_days": period_days,
                "platforms": platforms,
                "content_types": content_types,
                "distribution": distribution,
                "posting_schedule": posting_times,
                "engagement_predictions": engagement_predictions,
                "recommendations": self._generate_schedule_recommendations(posting_times, platforms),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate posting schedule recommendations: {e}")
            raise
    
    async def get_calendar_analytics(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Get analytics for calendar performance
        """
        try:
            self.logger.info(f"Generating calendar analytics from {start_date} to {end_date}")
            
            # This would analyze actual calendar performance
            # For now, return mock analytics
            
            analytics = {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "total_days": (end_date - start_date).days + 1
                },
                "performance_metrics": {
                    "total_posts": 45,
                    "published_posts": 42,
                    "failed_posts": 3,
                    "success_rate": 93.3,
                    "average_engagement": 8.7,
                    "best_performing_day": "Wednesday",
                    "best_performing_time": "11:00 AM",
                    "best_performing_platform": "LinkedIn"
                },
                "content_type_performance": {
                    "blog_post": {"count": 15, "avg_engagement": 9.2},
                    "social_media": {"count": 20, "avg_engagement": 8.5},
                    "newsletter": {"count": 7, "avg_engagement": 7.8}
                },
                "platform_performance": {
                    "wordpress": {"posts": 15, "engagement": 9.1},
                    "linkedin": {"posts": 20, "engagement": 8.9},
                    "facebook": {"posts": 10, "engagement": 7.2}
                },
                "trends": {
                    "engagement_trend": "increasing",
                    "best_content_themes": ["how-to guides", "industry insights", "case studies"],
                    "optimal_posting_frequency": "3-4 times per week"
                }
            }
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Failed to generate calendar analytics: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Health check for calendar service"""
        try:
            # Basic health checks
            if not self.platform_configs:
                return False
            
            # Test optimal time calculation
            test_time = await self.get_optimal_posting_time("blog_post", ["wordpress"])
            if not test_time:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Calendar service health check failed: {e}")
            return False
    
    async def _calculate_platform_optimal_time(
        self, 
        platform: str, 
        content_type: str, 
        target_audience: str, 
        base_time: datetime
    ) -> datetime:
        """Calculate optimal posting time for a specific platform"""
        try:
            config = self.platform_configs.get(platform, {})
            optimal_hours = config.get('optimal_hours', [10])
            optimal_days = config.get('optimal_days', [0, 1, 2, 3, 4])
            
            # Find next optimal time
            current_time = base_time
            attempts = 0
            max_attempts = 14  # Look up to 2 weeks ahead
            
            while attempts < max_attempts:
                # Check if current day is optimal
                if current_time.weekday() in optimal_days:
                    # Find optimal hour for this day
                    for hour in optimal_hours:
                        candidate_time = current_time.replace(
                            hour=hour, minute=0, second=0, microsecond=0
                        )
                        
                        # Make sure it's in the future
                        if candidate_time > datetime.utcnow():
                            return candidate_time
                
                # Move to next day
                current_time += timedelta(days=1)
                attempts += 1
            
            # Fallback: return next business day at 10 AM
            fallback_time = self._get_next_business_day(base_time)
            return fallback_time.replace(hour=10, minute=0, second=0, microsecond=0)
            
        except Exception as e:
            self.logger.error(f"Failed to calculate optimal time for {platform}: {e}")
            # Return fallback time
            return base_time + timedelta(days=1, hours=10)
    
    def _apply_content_type_adjustments(self, optimal_time: datetime, content_type: str) -> datetime:
        """Apply content type specific timing adjustments"""
        try:
            adjustments = self.content_type_adjustments.get(content_type, {})
            
            # Apply time adjustment (hours)
            time_adjustment = adjustments.get('time_adjustment', 0)
            if time_adjustment != 0:
                optimal_time += timedelta(hours=time_adjustment)
            
            # Apply day adjustment
            day_adjustment = adjustments.get('day_adjustment', 0)
            if day_adjustment != 0:
                optimal_time += timedelta(days=day_adjustment)
                # Ensure it's still a business day
                optimal_time = self._get_next_business_day(optimal_time)
            
            return optimal_time
            
        except Exception as e:
            self.logger.error(f"Failed to apply content type adjustments: {e}")
            return optimal_time
    
    async def _generate_calendar_structure(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Generate basic calendar structure"""
        try:
            calendar_data = []
            current_date = start_date
            
            while current_date <= end_date:
                day_data = {
                    "date": current_date.isoformat(),
                    "day_of_week": current_date.strftime("%A"),
                    "day_of_week_num": current_date.weekday(),
                    "is_weekend": current_date.weekday() >= 5,
                    "is_business_day": current_date.weekday() < 5,
                    "optimal_posting_times": [],
                    "content_suggestions": [],
                    "scheduled_content": []
                }
                
                calendar_data.append(day_data)
                current_date += timedelta(days=1)
            
            return calendar_data
            
        except Exception as e:
            self.logger.error(f"Failed to generate calendar structure: {e}")
            return []
    
    async def _add_optimal_posting_times(
        self, 
        calendar_data: List[Dict[str, Any]], 
        platforms: List[str], 
        content_types: List[str]
    ) -> List[Dict[str, Any]]:
        """Add optimal posting times to calendar"""
        try:
            for day_data in calendar_data:
                if day_data.get('is_business_day'):
                    # Calculate optimal times for this day
                    date_obj = datetime.fromisoformat(day_data['date'])
                    
                    for platform in platforms:
                        for content_type in content_types:
                            optimal_time = await self._calculate_platform_optimal_time(
                                platform, content_type, "general", date_obj
                            )
                            
                            # Only add if it's the same day
                            if optimal_time.date() == date_obj.date():
                                day_data['optimal_posting_times'].append({
                                    "platform": platform,
                                    "content_type": content_type,
                                    "time": optimal_time.strftime("%H:%M"),
                                    "datetime": optimal_time.isoformat()
                                })
                
                # Sort posting times
                day_data['optimal_posting_times'].sort(key=lambda x: x['time'])
            
            return calendar_data
            
        except Exception as e:
            self.logger.error(f"Failed to add optimal posting times: {e}")
            return calendar_data
    
    async def _add_content_suggestions(
        self, 
        calendar_data: List[Dict[str, Any]], 
        content_types: List[str]
    ) -> List[Dict[str, Any]]:
        """Add content suggestions to calendar"""
        try:
            content_suggestions = {
                "blog_post": [
                    "Industry trend analysis",
                    "How-to guide",
                    "Case study",
                    "Expert interview",
                    "Product review",
                    "Best practices",
                    "Industry news commentary"
                ],
                "social_media": [
                    "Quick tip",
                    "Behind the scenes",
                    "Customer spotlight",
                    "Industry insight",
                    "Company update",
                    "Team highlight",
                    "Fun fact"
                ],
                "newsletter": [
                    "Weekly roundup",
                    "Monthly insights",
                    "Special announcement",
                    "Exclusive content",
                    "Community highlights"
                ]
            }
            
            for day_data in calendar_data:
                if day_data.get('is_business_day'):
                    # Add content suggestions for business days
                    for content_type in content_types:
                        suggestions = content_suggestions.get(content_type, [])
                        if suggestions:
                            # Rotate through suggestions based on day
                            day_index = len(calendar_data) - (end_date - current_date).days
                            suggestion_index = day_index % len(suggestions)
                            
                            day_data['content_suggestions'].append({
                                "content_type": content_type,
                                "suggestion": suggestions[suggestion_index],
                                "priority": "medium"
                            })
            
            return calendar_data
            
        except Exception as e:
            self.logger.error(f"Failed to add content suggestions: {e}")
            return calendar_data
    
    def _calculate_content_distribution(
        self, 
        content_count: int, 
        period_days: int, 
        platforms: List[str]
    ) -> Dict[str, Any]:
        """Calculate optimal content distribution across platforms and time"""
        try:
            # Calculate posting frequency
            posts_per_week = content_count / (period_days / 7)
            
            # Distribute across platforms
            platform_distribution = {}
            for platform in platforms:
                config = self.platform_configs.get(platform, {})
                frequency = config.get('posting_frequency', 'daily')
                
                if frequency == 'daily':
                    platform_distribution[platform] = min(posts_per_week, 7)
                elif frequency == 'multiple_daily':
                    platform_distribution[platform] = min(posts_per_week, 14)
                else:
                    platform_distribution[platform] = min(posts_per_week, 3)
            
            return {
                "total_content": content_count,
                "period_days": period_days,
                "posts_per_week": posts_per_week,
                "platform_distribution": platform_distribution,
                "recommended_frequency": self._get_recommended_frequency(posts_per_week)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to calculate content distribution: {e}")
            return {}
    
    async def _generate_posting_schedule(
        self, 
        distribution: Dict[str, Any], 
        platforms: List[str], 
        content_types: List[str], 
        period_days: int
    ) -> List[Dict[str, Any]]:
        """Generate specific posting schedule"""
        try:
            schedule = []
            start_date = datetime.utcnow()
            
            for platform in platforms:
                platform_posts = distribution.get('platform_distribution', {}).get(platform, 0)
                
                # Calculate posting intervals
                if platform_posts > 0:
                    interval_days = period_days / platform_posts
                    
                    for i in range(int(platform_posts)):
                        post_date = start_date + timedelta(days=i * interval_days)
                        
                        # Get optimal time for this platform
                        optimal_time = await self._calculate_platform_optimal_time(
                            platform, content_types[0], "general", post_date
                        )
                        
                        schedule.append({
                            "platform": platform,
                            "content_type": content_types[0],
                            "scheduled_date": optimal_time.isoformat(),
                            "priority": "high" if i == 0 else "medium"
                        })
            
            # Sort by date
            schedule.sort(key=lambda x: x['scheduled_date'])
            
            return schedule
            
        except Exception as e:
            self.logger.error(f"Failed to generate posting schedule: {e}")
            return []
    
    def _predict_engagement(
        self, 
        posting_schedule: List[Dict[str, Any]], 
        platforms: List[str]
    ) -> Dict[str, Any]:
        """Predict engagement for posting schedule"""
        try:
            # Mock engagement prediction based on platform and timing
            platform_engagement = {
                "wordpress": {"base_engagement": 8.5, "timing_multiplier": 1.2},
                "linkedin": {"base_engagement": 9.0, "timing_multiplier": 1.3},
                "facebook": {"base_engagement": 7.5, "timing_multiplier": 1.1},
                "twitter": {"base_engagement": 7.0, "timing_multiplier": 1.0},
                "instagram": {"base_engagement": 8.0, "timing_multiplier": 1.1}
            }
            
            total_predicted_engagement = 0
            platform_predictions = {}
            
            for platform in platforms:
                if platform in platform_engagement:
                    config = platform_engagement[platform]
                    platform_posts = sum(1 for post in posting_schedule if post['platform'] == platform)
                    
                    # Calculate predicted engagement
                    predicted_engagement = platform_posts * config['base_engagement'] * config['timing_multiplier']
                    platform_predictions[platform] = {
                        "posts": platform_posts,
                        "predicted_engagement": round(predicted_engagement, 1),
                        "avg_per_post": round(config['base_engagement'] * config['timing_multiplier'], 1)
                    }
                    
                    total_predicted_engagement += predicted_engagement
            
            return {
                "total_predicted_engagement": round(total_predicted_engagement, 1),
                "platform_predictions": platform_predictions,
                "confidence_level": "medium",
                "factors_considered": ["platform", "timing", "content_type", "audience"]
            }
            
        except Exception as e:
            self.logger.error(f"Failed to predict engagement: {e}")
            return {}
    
    def _generate_schedule_recommendations(
        self, 
        posting_schedule: List[Dict[str, Any]], 
        platforms: List[str]
    ) -> List[str]:
        """Generate recommendations for the posting schedule"""
        try:
            recommendations = []
            
            # Analyze posting frequency
            if len(posting_schedule) > 20:
                recommendations.append("Consider reducing posting frequency to maintain quality")
            elif len(posting_schedule) < 5:
                recommendations.append("Increase posting frequency for better audience engagement")
            
            # Platform-specific recommendations
            for platform in platforms:
                platform_posts = sum(1 for post in posting_schedule if post['platform'] == platform)
                
                if platform == "linkedin" and platform_posts < 3:
                    recommendations.append("Increase LinkedIn posts for professional audience engagement")
                elif platform == "instagram" and platform_posts < 2:
                    recommendations.append("Add more Instagram posts for visual content strategy")
            
            # Timing recommendations
            weekend_posts = sum(1 for post in posting_schedule if self._is_weekend(post['scheduled_date']))
            if weekend_posts == 0:
                recommendations.append("Consider weekend posting for social media platforms")
            
            # Content variety
            content_types = set(post['content_type'] for post in posting_schedule)
            if len(content_types) < 2:
                recommendations.append("Diversify content types for better audience engagement")
            
            return recommendations[:5]  # Limit to top 5 recommendations
            
        except Exception as e:
            self.logger.error(f"Failed to generate schedule recommendations: {e}")
            return []
    
    def _get_next_business_day(self, start_date: datetime) -> datetime:
        """Get next business day"""
        current_date = start_date
        while current_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
            current_date += timedelta(days=1)
        return current_date
    
    def _get_recommended_frequency(self, posts_per_week: float) -> str:
        """Get recommended posting frequency"""
        if posts_per_week >= 7:
            return "daily"
        elif posts_per_week >= 3:
            return "3-4 times per week"
        elif posts_per_week >= 1:
            return "1-2 times per week"
        else:
            return "less than once per week"
    
    def _is_weekend(self, date_string: str) -> bool:
        """Check if date is weekend"""
        try:
            date_obj = datetime.fromisoformat(date_string)
            return date_obj.weekday() >= 5
        except:
            return False
