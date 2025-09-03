"""
Database models and connection management
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, Dict, Any
import uuid

from ..config.settings import get_settings

Base = declarative_base()
settings = get_settings()

# Database Models
class Content(Base):
    """Content generation records"""
    __tablename__ = "content"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    content_type = Column(String(50), nullable=False)  # blog_post, social_media, etc.
    status = Column(String(20), default="draft")  # draft, published, scheduled
    
    # SEO fields
    primary_keyword = Column(String(200))
    related_keywords = Column(JSON)  # List of related keywords
    seo_title = Column(String(60))
    seo_description = Column(String(160))
    seo_score = Column(Float, default=0.0)
    
    # Content metadata
    word_count = Column(Integer, default=0)
    readability_score = Column(Float, default=0.0)
    quality_score = Column(Float, default=0.0)
    tone = Column(String(50), default="professional")
    target_audience = Column(String(200))
    
    # Company/brand info
    company_name = Column(String(200))
    industry = Column(String(100))
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    published_at = Column(DateTime)
    
    # Generation metadata
    generation_cost = Column(Float, default=0.0)
    model_used = Column(String(50))
    generation_time = Column(Float, default=0.0)  # seconds

class Schedule(Base):
    """Content scheduling records"""
    __tablename__ = "schedules"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    content_id = Column(String, nullable=False)
    
    # Scheduling info
    publish_time = Column(DateTime, nullable=False)
    frequency = Column(String(20), default="once")  # once, daily, weekly, monthly
    platforms = Column(JSON)  # List of platforms to publish to
    
    # Status tracking
    status = Column(String(20), default="scheduled")  # scheduled, published, failed, cancelled
    task_id = Column(String(100))  # Celery task ID
    
    # Auto-generation settings
    auto_generate = Column(Boolean, default=False)
    template_id = Column(String)
    
    # Results
    publish_results = Column(JSON)  # Results from each platform
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    executed_at = Column(DateTime)

class KeywordResearch(Base):
    """Keyword research results"""
    __tablename__ = "keyword_research"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    primary_keyword = Column(String(200), nullable=False)
    
    # Research data
    search_volume = Column(Integer)
    competition_level = Column(String(20))  # low, medium, high
    difficulty_score = Column(Float)
    trending_score = Column(Float)
    
    # Related keywords
    related_keywords = Column(JSON)
    competitor_keywords = Column(JSON)
    long_tail_keywords = Column(JSON)
    
    # SERP analysis
    serp_features = Column(JSON)  # Featured snippets, PAA, etc.
    top_competitors = Column(JSON)
    content_gaps = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class UsageTracking(Base):
    """Track API usage and costs"""
    __tablename__ = "usage_tracking"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(100), default="default")  # For future multi-user support
    
    # Usage metrics
    date = Column(DateTime, default=func.now())
    api_calls = Column(Integer, default=0)
    tokens_used = Column(Integer, default=0)
    cost = Column(Float, default=0.0)
    
    # Service breakdown
    openai_calls = Column(Integer, default=0)
    anthropic_calls = Column(Integer, default=0)
    google_calls = Column(Integer, default=0)
    serp_calls = Column(Integer, default=0)
    
    # Content generation stats
    content_generated = Column(Integer, default=0)
    keywords_researched = Column(Integer, default=0)

class WordPressConnection(Base):
    """WordPress site connections"""
    __tablename__ = "wordpress_connections"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    site_name = Column(String(200), nullable=False)
    site_url = Column(String(500), nullable=False)
    
    # Authentication
    username = Column(String(100), nullable=False)
    app_password = Column(String(200), nullable=False)  # Should be encrypted
    
    # Settings
    use_blocks = Column(Boolean, default=True)
    default_category = Column(String(100))
    default_status = Column(String(20), default="draft")
    
    # Connection status
    is_active = Column(Boolean, default=True)
    last_connection_test = Column(DateTime)
    connection_status = Column(String(20), default="unknown")
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

# Database connection management
class DatabaseManager:
    """Manages database connections and sessions"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._setup_database()
    
    def _setup_database(self):
        """Setup database connection"""
        self.engine = create_engine(
            settings.database_url,
            pool_pre_ping=True,
            pool_recycle=300
        )
        
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
    
    def create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    def close_session(self, session: Session):
        """Close database session"""
        session.close()

# Global database manager instance
db_manager = DatabaseManager()

def get_db() -> Session:
    """Dependency for getting database session"""
    session = db_manager.get_session()
    try:
        yield session
    finally:
        db_manager.close_session(session)

def init_database():
    """Initialize database tables"""
    db_manager.create_tables()
