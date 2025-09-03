"""
Content Generation API Routes
FastAPI routes for content generation functionality
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime
import asyncio
import json

router = APIRouter()

# Request/Response Models
class ContentGenerationRequest(BaseModel):
    primary_keyword: str = Field(..., description="Primary keyword for content")
    related_keywords: List[str] = Field(default=[], description="Related keywords")
    content_type: str = Field(default="blog_post", description="Type of content to generate")
    target_length: int = Field(default=1000, ge=100, le=5000, description="Target word count")
    tone: str = Field(default="professional", description="Content tone")
    target_audience: str = Field(default="general", description="Target audience")
    quality_level: str = Field(default="standard", description="Quality level: standard or premium")
    
    # Company information
    company_info: Dict[str, Any] = Field(default={}, description="Company context")
    
    # Template and customization
    template: Optional[str] = Field(None, description="Template to use")
    custom_instructions: Optional[str] = Field(None, description="Custom instructions")
    
    # Generation options
    stream: bool = Field(default=False, description="Stream content generation")
    save_to_database: bool = Field(default=True, description="Save generated content")

class ContentGenerationResponse(BaseModel):
    content_id: str
    title: str
    content: str
    meta_description: str
    seo_title: str
    
    # Metadata
    content_type: str
    word_count: int
    reading_time: int
    generation_time: float
    
    # SEO metrics
    seo_score: float
    readability_score: float
    keyword_density: float
    
    # Generation info
    models_used: List[str]
    total_cost: float
    phases_completed: List[str]
    
    generated_at: str

class ContentOptimizeRequest(BaseModel):
    content_id: Optional[str] = None
    content: Optional[str] = None
    primary_keyword: str
    optimization_type: str = Field(default="seo", description="Type of optimization")
    target_score: int = Field(default=85, ge=70, le=100, description="Target optimization score")

class TemplateResponse(BaseModel):
    key: str
    name: str
    description: str
    structure: List[Dict[str, Any]]
    word_count: int

@router.post("/generate", response_model=ContentGenerationResponse)
async def generate_content(request: ContentGenerationRequest, background_tasks: BackgroundTasks):
    """
    Generate content using AI with multi-pass optimization
    """
    try:
        # This would normally get the service from the container
        # For now, simulate content generation
        
        if request.stream:
            raise HTTPException(status_code=400, detail="Use /generate-stream endpoint for streaming")
        
        # Simulate processing time
        await asyncio.sleep(3)
        
        # Mock response based on request
        content_id = f"content_{int(datetime.utcnow().timestamp())}"
        
        # Generate content based on template type
        if request.content_type == "social_media":
            mock_content = f"""🚀 Master {request.primary_keyword} in 2024!

Here's what top performers know about {request.primary_keyword}:

✅ Focus on quality over quantity
✅ Consistency is key to success  
✅ Measure and optimize regularly
✅ Stay updated with trends

💡 Pro tip: Start small and scale gradually for best results.

What's your experience with {request.primary_keyword}? Share in the comments! 👇

#ContentMarketing #DigitalStrategy #BusinessGrowth"""
            
        elif request.content_type == "website_copy":
            mock_content = f"""# Finally, A {request.primary_keyword.title()} Solution That Actually Works

## Stop Struggling With {request.primary_keyword} - There's A Better Way

Tired of complicated {request.primary_keyword} strategies that promise everything but deliver nothing? You're not alone.

### The Problem With Traditional {request.primary_keyword} Approaches

Most {request.primary_keyword} solutions are:
- Overly complex and hard to implement
- One-size-fits-all approaches that don't work
- Expensive with hidden costs
- Time-consuming with slow results

### Introducing Our {request.primary_keyword.title()} System

Our proven {request.primary_keyword} system is different. Here's why:

**✅ Simple to Implement**
Get started in minutes, not hours or days.

**✅ Customized for Your Needs** 
Tailored solutions that fit your specific situation.

**✅ Transparent Pricing**
No hidden fees or surprise charges.

**✅ Fast Results**
See improvements within the first week.

### What Our Clients Say

*"This {request.primary_keyword} solution transformed our business in just 30 days!"* - Sarah M., CEO

*"Finally, a {request.primary_keyword} approach that actually works!"* - John D., Marketing Director

### Ready to Transform Your {request.primary_keyword.title()}?

Join over 1,000 satisfied customers who've already revolutionized their {request.primary_keyword} approach.

**[Get Started Free Today →]**

30-day money-back guarantee. Cancel anytime."""

        else:  # Default to blog_post
            mock_content = f"""# {request.primary_keyword.title()}: The Complete Guide for {datetime.now().year}

## Introduction

{request.primary_keyword.title()} has become increasingly important in today's digital landscape. Whether you're a beginner or looking to refine your approach, this comprehensive guide will provide you with everything you need to know about {request.primary_keyword}.

## What is {request.primary_keyword.title()}?

{request.primary_keyword.title()} refers to the strategic approach of optimizing and leveraging specific methodologies to achieve desired outcomes. Understanding the fundamentals is crucial for success.

### Key Components of {request.primary_keyword.title()}

1. **Strategic Planning**: Develop a clear roadmap for implementation
2. **Resource Allocation**: Ensure you have the right tools and budget
3. **Execution**: Follow best practices during implementation
4. **Monitoring**: Track performance and adjust strategies accordingly

## Why {request.primary_keyword.title()} Matters

In today's competitive environment, {request.primary_keyword} offers several key advantages:

- **Improved Efficiency**: Streamline your processes and reduce waste
- **Better Results**: Achieve higher success rates and ROI
- **Competitive Edge**: Stay ahead of competitors in your industry
- **Scalability**: Build systems that grow with your business

## Best Practices for {request.primary_keyword.title()}

### 1. Start with Clear Objectives

Before diving into {request.primary_keyword}, define what success looks like for your specific situation.

### 2. Research and Planning

Thorough research is the foundation of successful {request.primary_keyword} implementation.

### 3. Choose the Right Tools

Select tools and platforms that align with your goals and budget.

### 4. Monitor and Optimize

Continuously track your progress and make data-driven improvements.

## Common Mistakes to Avoid

When implementing {request.primary_keyword}, avoid these common pitfalls:

- **Lack of Planning**: Rushing into implementation without proper strategy
- **Ignoring Data**: Making decisions based on assumptions rather than facts
- **Inconsistent Execution**: Not maintaining consistency in your approach
- **Neglecting Optimization**: Failing to continuously improve your methods

## Advanced Strategies

Once you've mastered the basics, consider these advanced {request.primary_keyword} strategies:

### Automation Integration

Leverage automation tools to streamline your {request.primary_keyword} processes.

### Data-Driven Decision Making

Use analytics to guide your {request.primary_keyword} strategy and investments.

### Cross-Channel Integration

Ensure your {request.primary_keyword} efforts work cohesively across all channels.

## Measuring Success

Key metrics to track for {request.primary_keyword} include:

- Performance indicators relevant to your goals
- ROI and cost-effectiveness
- User engagement and satisfaction
- Long-term growth and sustainability

## Future Trends in {request.primary_keyword.title()}

Stay ahead of the curve by understanding emerging trends:

- AI and machine learning integration
- Increased personalization capabilities
- Enhanced automation features
- Cross-platform compatibility improvements

## Conclusion

{request.primary_keyword.title()} is a powerful approach that can transform your results when implemented correctly. By following the strategies and best practices outlined in this guide, you'll be well-positioned to achieve success.

Remember, success with {request.primary_keyword} requires patience, consistency, and continuous learning. Start with the fundamentals, track your progress, and gradually implement more advanced strategies as you gain experience.

## Ready to Get Started?

Take the first step toward mastering {request.primary_keyword} by implementing one strategy from this guide today. Need personalized guidance? Our team of {request.primary_keyword} experts is here to help you achieve your goals faster.

**Contact us today** to learn how we can accelerate your {request.primary_keyword} success."""

        return ContentGenerationResponse(
            content_id=content_id,
            title=f"{request.primary_keyword.title()}: The Complete Guide for {datetime.now().year}",
            content=mock_content,
            meta_description=f"Master {request.primary_keyword} with this comprehensive guide. Learn strategies, best practices, and avoid common mistakes in {datetime.now().year}.",
            seo_title=f"{request.primary_keyword.title()} Guide {datetime.now().year}",
            content_type=request.content_type,
            word_count=len(mock_content.split()),
            reading_time=len(mock_content.split()) // 200,
            generation_time=3.2,
            seo_score=85.7,
            readability_score=71.2,
            keyword_density=2.3,
            models_used=["gpt-4o-mini", "claude-3-haiku"],
            total_cost=0.045,
            phases_completed=["research", "outline", "content", "seo", "review"],
            generated_at=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content generation failed: {str(e)}")

@router.post("/generate-stream")
async def generate_content_stream(request: ContentGenerationRequest):
    """
    Generate content with streaming response
    """
    try:
        async def generate_stream():
            # Phase 1: Research
            yield f"data: {json.dumps({'type': 'status', 'message': 'Starting research phase...', 'progress': 0})}\n\n"
            await asyncio.sleep(1)
            
            yield f"data: {json.dumps({'type': 'status', 'message': 'Analyzing keywords and competition...', 'progress': 20})}\n\n"
            await asyncio.sleep(1)
            
            # Phase 2: Outline
            yield f"data: {json.dumps({'type': 'status', 'message': 'Creating content outline...', 'progress': 40})}\n\n"
            await asyncio.sleep(1)
            
            # Phase 3: Content Generation
            yield f"data: {json.dumps({'type': 'status', 'message': 'Generating content...', 'progress': 60})}\n\n"
            await asyncio.sleep(0.5)
            
            # Simulate streaming content
            content_chunks = [
                f"# {request.primary_keyword.title()}: A Comprehensive Guide\n\n",
                "## Introduction\n\n",
                f"{request.primary_keyword.title()} is a crucial topic that requires careful consideration. ",
                "In this guide, we'll explore the key concepts and strategies you need to know.\n\n",
                f"## Understanding {request.primary_keyword.title()}\n\n",
                "Let's break down the essential components:\n\n",
                "- Key benefits and advantages\n",
                "- Implementation strategies\n", 
                "- Best practices to follow\n",
                "- Common challenges to avoid\n\n",
                "## Implementation Strategies\n\n",
                f"When implementing {request.primary_keyword}, consider these proven approaches:\n\n",
                "1. **Start with research** - Understanding your landscape is crucial\n",
                "2. **Plan thoroughly** - A good plan prevents poor performance\n",
                "3. **Execute consistently** - Consistency is key to success\n",
                "4. **Monitor and optimize** - Continuous improvement drives results\n\n",
                "## Conclusion\n\n",
                f"Mastering {request.primary_keyword} requires dedication and the right approach. ",
                "By following this guide, you'll be well-equipped for success."
            ]
            
            accumulated_content = ""
            for i, chunk in enumerate(content_chunks):
                accumulated_content += chunk
                progress = 60 + (i / len(content_chunks)) * 30
                
                yield f"data: {json.dumps({'type': 'content_chunk', 'content': chunk, 'accumulated_content': accumulated_content, 'progress': progress})}\n\n"
                await asyncio.sleep(0.3)
            
            # Final phase
            yield f"data: {json.dumps({'type': 'status', 'message': 'Optimizing for SEO...', 'progress': 90})}\n\n"
            await asyncio.sleep(1)
            
            yield f"data: {json.dumps({'type': 'status', 'message': 'Finalizing content...', 'progress': 95})}\n\n"
            await asyncio.sleep(0.5)
            
            # Completion
            final_result = {
                'type': 'complete',
                'content_id': f"content_{int(datetime.utcnow().timestamp())}",
                'final_content': accumulated_content,
                'seo_score': 85.2,
                'word_count': len(accumulated_content.split()),
                'progress': 100
            }
            
            yield f"data: {json.dumps(final_result)}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Streaming generation failed: {str(e)}")

@router.get("/templates", response_model=List[TemplateResponse])
async def get_available_templates():
    """
    Get list of available content templates
    """
    try:
        # Mock templates
        templates = [
            TemplateResponse(
                key="blog_post",
                name="Blog Post",
                description="Comprehensive blog post template with SEO optimization",
                structure=[
                    {"section": "introduction", "word_count": 150},
                    {"section": "main_content", "word_count": 800},
                    {"section": "conclusion", "word_count": 150}
                ],
                word_count=1100
            ),
            TemplateResponse(
                key="social_media",
                name="Social Media Post",
                description="Engaging social media content for various platforms",
                structure=[
                    {"section": "hook", "word_count": 20},
                    {"section": "value", "word_count": 80},
                    {"section": "cta", "word_count": 20}
                ],
                word_count=120
            ),
            TemplateResponse(
                key="website_copy",
                name="Website Copy",
                description="Conversion-focused website content",
                structure=[
                    {"section": "headline", "word_count": 20},
                    {"section": "problem", "word_count": 100},
                    {"section": "solution", "word_count": 200},
                    {"section": "cta", "word_count": 50}
                ],
                word_count=370
            ),
            TemplateResponse(
                key="product_description",
                name="Product Description",
                description="E-commerce product descriptions that convert",
                structure=[
                    {"section": "headline", "word_count": 15},
                    {"section": "features", "word_count": 100},
                    {"section": "benefits", "word_count": 120},
                    {"section": "guarantee", "word_count": 35}
                ],
                word_count=270
            ),
            TemplateResponse(
                key="email_newsletter",
                name="Email Newsletter",
                description="Engaging email newsletter content",
                structure=[
                    {"section": "subject_line", "word_count": 8},
                    {"section": "greeting", "word_count": 20},
                    {"section": "main_content", "word_count": 200},
                    {"section": "cta", "word_count": 30}
                ],
                word_count=258
            )
        ]
        
        return templates
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get templates: {str(e)}")

@router.get("/templates/{template_key}")
async def get_template_details(template_key: str):
    """
    Get detailed information about a specific template
    """
    try:
        templates = {
            "blog_post": {
                "key": "blog_post",
                "name": "Blog Post",
                "description": "Comprehensive blog post template with SEO optimization",
                "structure": [
                    {"section": "introduction", "word_count": 150, "purpose": "Hook readers and introduce the topic"},
                    {"section": "main_content", "word_count": 800, "purpose": "Deliver core value and information"},
                    {"section": "conclusion", "word_count": 150, "purpose": "Summarize and provide call-to-action"}
                ],
                "seo_requirements": {
                    "title_length": [30, 60],
                    "meta_description_length": [150, 160],
                    "keyword_density": [1, 3]
                },
                "examples": {
                    "title": "The Complete Guide to {keyword}",
                    "introduction": "Are you looking to master {keyword}? This comprehensive guide covers everything you need to know...",
                    "conclusion": "By implementing these {keyword} strategies, you'll see significant improvements in your results."
                }
            }
            # Add other templates as needed
        }
        
        template = templates.get(template_key)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return template
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get template details: {str(e)}")

@router.get("/history")
async def get_content_history(limit: int = 50, content_type: Optional[str] = None):
    """
    Get content generation history
    """
    try:
        # Mock history data
        history = []
        for i in range(min(limit, 10)):  # Return up to 10 mock items
            history.append({
                "content_id": f"content_{i}",
                "title": f"Sample Content {i+1}",
                "primary_keyword": f"sample keyword {i+1}",
                "content_type": content_type or "blog_post",
                "word_count": 1200 + i * 100,
                "seo_score": 80.5 + i,
                "generated_at": (datetime.utcnow().timestamp() - i * 3600),
                "status": "completed"
            })
        
        return {
            "history": history,
            "total": len(history),
            "limit": limit,
            "filter": {"content_type": content_type} if content_type else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get content history: {str(e)}")

@router.get("/{content_id}")
async def get_content_by_id(content_id: str):
    """
    Get specific content by ID
    """
    try:
        # Mock content retrieval
        mock_content = {
            "content_id": content_id,
            "title": "Sample Content Title",
            "content": "This is sample content that would be retrieved from the database...",
            "meta_description": "Sample meta description",
            "seo_title": "Sample SEO Title",
            "content_type": "blog_post",
            "word_count": 1200,
            "seo_score": 85.3,
            "generated_at": datetime.utcnow().isoformat(),
            "models_used": ["gpt-4o-mini"],
            "total_cost": 0.045
        }
        
        return mock_content
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get content: {str(e)}")

@router.delete("/{content_id}")
async def delete_content(content_id: str):
    """
    Delete content by ID
    """
    try:
        # Mock deletion
        return {
            "success": True,
            "message": f"Content {content_id} deleted successfully",
            "deleted_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete content: {str(e)}")
