"""
Utility functions for Content Agent
Common helper functions used across modules
"""

import re
import hashlib
import asyncio
import time
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
import json
import uuid
from urllib.parse import urlparse
import requests
from loguru import logger

class TextProcessor:
    """Text processing utilities"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.,!?;:\-\(\)]', '', text)
        
        return text.strip()
    
    @staticmethod
    def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from text using simple frequency analysis"""
        if not text:
            return []
        
        # Convert to lowercase and split
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Remove common stop words
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before',
            'after', 'above', 'below', 'between', 'among', 'this', 'that', 'these',
            'those', 'was', 'were', 'been', 'have', 'has', 'had', 'can', 'could',
            'will', 'would', 'should', 'may', 'might', 'must', 'shall'
        }
        
        # Filter out stop words
        words = [word for word in words if word not in stop_words]
        
        # Count frequency
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        return [word for word, freq in sorted_words[:max_keywords]]
    
    @staticmethod
    def calculate_readability(text: str) -> Dict[str, float]:
        """Calculate readability scores"""
        if not text or len(text.strip()) < 10:
            return {"flesch_reading_ease": 0, "flesch_kincaid_grade": 0}
        
        try:
            # Simple readability calculation
            sentences = len(re.findall(r'[.!?]+', text))
            words = len(text.split())
            syllables = sum([TextProcessor._count_syllables(word) for word in text.split()])
            
            if sentences == 0 or words == 0:
                return {"flesch_reading_ease": 50, "flesch_kincaid_grade": 10}
            
            # Flesch Reading Ease
            flesch_score = 206.835 - (1.015 * words / sentences) - (84.6 * syllables / words)
            
            # Flesch-Kincaid Grade Level
            fk_grade = (0.39 * words / sentences) + (11.8 * syllables / words) - 15.59
            
            return {
                "flesch_reading_ease": max(0, min(100, flesch_score)),
                "flesch_kincaid_grade": max(0, fk_grade)
            }
        except:
            return {"flesch_reading_ease": 50, "flesch_kincaid_grade": 10}
    
    @staticmethod
    def _count_syllables(word: str) -> int:
        """Count syllables in a word"""
        word = word.lower()
        vowels = 'aeiouy'
        syllable_count = 0
        prev_char_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_char_was_vowel:
                syllable_count += 1
            prev_char_was_vowel = is_vowel
        
        # Handle silent e
        if word.endswith('e'):
            syllable_count -= 1
        
        return max(1, syllable_count)
    
    @staticmethod
    def word_count(text: str) -> int:
        """Count words in text"""
        if not text:
            return 0
        return len(re.findall(r'\b\w+\b', text))
    
    @staticmethod
    def estimate_reading_time(text: str, words_per_minute: int = 200) -> int:
        """Estimate reading time in minutes"""
        word_count = TextProcessor.word_count(text)
        return max(1, round(word_count / words_per_minute))

class SEOAnalyzer:
    """SEO analysis utilities"""
    
    @staticmethod
    def analyze_keyword_density(text: str, keyword: str) -> float:
        """Calculate keyword density as percentage"""
        if not text or not keyword:
            return 0.0
        
        text_lower = text.lower()
        keyword_lower = keyword.lower()
        
        total_words = len(text_lower.split())
        keyword_count = text_lower.count(keyword_lower)
        
        if total_words == 0:
            return 0.0
        
        return (keyword_count / total_words) * 100
    
    @staticmethod
    def check_title_seo(title: str, keyword: str) -> Dict[str, Any]:
        """Analyze title for SEO"""
        if not title:
            return {"score": 0, "issues": ["Title is empty"]}
        
        issues = []
        score = 100
        
        # Length check
        if len(title) > 60:
            issues.append("Title too long (>60 characters)")
            score -= 20
        elif len(title) < 30:
            issues.append("Title too short (<30 characters)")
            score -= 10
        
        # Keyword check
        if keyword and keyword.lower() not in title.lower():
            issues.append("Primary keyword not in title")
            score -= 30
        
        return {
            "score": max(0, score),
            "length": len(title),
            "issues": issues
        }
    
    @staticmethod
    def check_meta_description(description: str, keyword: str) -> Dict[str, Any]:
        """Analyze meta description for SEO"""
        if not description:
            return {"score": 0, "issues": ["Meta description is empty"]}
        
        issues = []
        score = 100
        
        # Length check
        if len(description) > 160:
            issues.append("Meta description too long (>160 characters)")
            score -= 20
        elif len(description) < 120:
            issues.append("Meta description too short (<120 characters)")
            score -= 10
        
        # Keyword check
        if keyword and keyword.lower() not in description.lower():
            issues.append("Primary keyword not in meta description")
            score -= 30
        
        return {
            "score": max(0, score),
            "length": len(description),
            "issues": issues
        }

class URLValidator:
    """URL validation utilities"""
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Check if URL is valid"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    @staticmethod
    def normalize_url(url: str) -> str:
        """Normalize URL format"""
        if not url:
            return ""
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        return url.rstrip('/')



class CostCalculator:
    """Cost calculation utilities"""
    
    MODEL_COSTS = {
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        "gpt-4o": {"input": 0.005, "output": 0.015},
        "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
        "claude-3-sonnet": {"input": 0.003, "output": 0.015}
    }
    
    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Rough estimation of token count"""
        return len(text.split()) * 1.3  # Rough approximation
    
    @staticmethod
    def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for model usage"""
        if model not in CostCalculator.MODEL_COSTS:
            return 0.0
        
        costs = CostCalculator.MODEL_COSTS[model]
        input_cost = (input_tokens / 1000) * costs["input"]
        output_cost = (output_tokens / 1000) * costs["output"]
        
        return input_cost + output_cost

class DateTimeUtils:
    """Date and time utilities"""
    
    @staticmethod
    def next_business_day(date: datetime = None) -> datetime:
        """Get next business day"""
        if date is None:
            date = datetime.now()
        
        # If it's weekend, move to Monday
        while date.weekday() > 4:  # 5 = Saturday, 6 = Sunday
            date += timedelta(days=1)
        
        return date

class ContentFormatter:
    """Content formatting utilities"""
    

    
    @staticmethod
    def html_to_plain_text(html: str) -> str:
        """Convert HTML to plain text"""
        if not html:
            return ""
        
        # Simple regex-based HTML to text conversion
        text = re.sub(r'<[^>]+>', '', html)
        return text.strip()
    
    @staticmethod
    def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
        """Truncate text to specified length"""
        if not text or len(text) <= max_length:
            return text
        
        return text[:max_length - len(suffix)].rstrip() + suffix



class CacheUtils:
    """Caching utilities"""
    
    @staticmethod
    def generate_cache_key(*args) -> str:
        """Generate cache key from arguments"""
        key_string = "_".join(str(arg) for arg in args)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    @staticmethod
    def is_cache_expired(cache_time: datetime, ttl_minutes: int) -> bool:
        """Check if cache is expired"""
        expiry_time = cache_time + timedelta(minutes=ttl_minutes)
        return datetime.utcnow() > expiry_time
