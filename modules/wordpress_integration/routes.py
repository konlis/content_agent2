"""
WordPress Integration Module API Routes
"""

from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File
from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from loguru import logger

# Pydantic models for request/response validation
class PublishPostRequest(BaseModel):
    title: str = Field(..., description="Post title")
    content: str = Field(..., description="Post content (HTML)")
    status: str = Field("publish", description="Post status")
    excerpt: Optional[str] = Field("", description="Post excerpt")
    categories: Optional[List[int]] = Field([], description="Category IDs")
    tags: Optional[List[int]] = Field([], description="Tag IDs")
    featured_media: Optional[int] = Field(None, description="Featured image ID")
    format: Optional[str] = Field("standard", description="Post format")
    meta: Optional[Dict[str, Any]] = Field({}, description="Custom meta fields")
    seo: Optional[Dict[str, Any]] = Field({}, description="SEO metadata")

class UpdatePostRequest(BaseModel):
    title: Optional[str] = Field(None, description="Post title")
    content: Optional[str] = Field(None, description="Post content")
    status: Optional[str] = Field(None, description="Post status")
    excerpt: Optional[str] = Field(None, description="Post excerpt")
    categories: Optional[List[int]] = Field(None, description="Category IDs")
    tags: Optional[List[int]] = Field(None, description="Tag IDs")
    featured_media: Optional[int] = Field(None, description="Featured image ID")
    meta: Optional[Dict[str, Any]] = Field(None, description="Custom meta fields")

class SchedulePostRequest(BaseModel):
    title: str = Field(..., description="Post title")
    content: str = Field(..., description="Post content")
    publish_time: datetime = Field(..., description="When to publish")
    status: str = Field("future", description="Post status")
    categories: Optional[List[int]] = Field([], description="Category IDs")
    tags: Optional[List[int]] = Field([], description="Tag IDs")
    featured_media: Optional[int] = Field(None, description="Featured image ID")

class MediaUploadResponse(BaseModel):
    id: int
    title: str
    filename: str
    source_url: str
    media_type: str
    mime_type: str
    date: str

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    excerpt: str
    link: str
    date: str
    status: str
    featured_media: Optional[int]
    categories: List[int]
    tags: List[int]

class GenerateImageRequest(BaseModel):
    prompt: str = Field(..., description="Image generation prompt")
    title: Optional[str] = Field(None, description="Article title for context")
    keywords: Optional[List[str]] = Field([], description="Keywords for image context")
    style: Optional[str] = Field("photorealistic", description="Image style")
    aspect_ratio: Optional[str] = Field("16:9", description="Image aspect ratio")

# Create router
router = APIRouter()

# Dependency to get services
def get_wordpress_client():
    from core.container import get_container
    container = get_container()
    return container.get_service('wordpress_client')

def get_content_formatter():
    from core.container import get_container
    container = get_container()
    return container.get_service('content_formatter')

def get_media_manager():
    from core.container import get_container
    container = get_container()
    return container.get_service('media_manager')

# Content Publishing Endpoints
@router.post("/publish", response_model=PostResponse)
async def publish_post(
    request: PublishPostRequest,
    wordpress_client = Depends(get_wordpress_client),
    content_formatter = Depends(get_content_formatter)
):
    """Publish a post to WordPress"""
    try:
        logger.info(f"API: Publishing WordPress post: {request.title}")
        
        # Format content for WordPress
        content_data = request.dict()
        formatted_content = await content_formatter.format_for_wordpress(content_data)
        
        # Publish to WordPress
        result = await wordpress_client.publish_post(formatted_content)
        
        return PostResponse(**result)
        
    except Exception as e:
        logger.error(f"API: WordPress publish failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/posts/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    request: UpdatePostRequest,
    wordpress_client = Depends(get_wordpress_client)
):
    """Update an existing WordPress post"""
    try:
        # Filter out None values
        update_data = {k: v for k, v in request.dict().items() if v is not None}
        
        result = await wordpress_client.update_post(post_id, update_data)
        return PostResponse(**result)
        
    except Exception as e:
        logger.error(f"API: WordPress update failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: int,
    force: bool = Query(False, description="Force delete (bypass trash)"),
    wordpress_client = Depends(get_wordpress_client)
):
    """Delete a WordPress post"""
    try:
        success = await wordpress_client.delete_post(post_id, force)
        if success:
            return {"post_id": post_id, "status": "deleted"}
        else:
            raise HTTPException(status_code=404, detail="Post not found or delete failed")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: WordPress delete failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/posts/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int,
    wordpress_client = Depends(get_wordpress_client)
):
    """Get a specific WordPress post"""
    try:
        result = await wordpress_client.get_post(post_id)
        if result:
            return PostResponse(**result)
        else:
            raise HTTPException(status_code=404, detail="Post not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Get WordPress post failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/posts", response_model=List[PostResponse])
async def get_posts(
    per_page: int = Query(10, description="Posts per page"),
    page: int = Query(1, description="Page number"),
    status: Optional[str] = Query(None, description="Post status filter"),
    search: Optional[str] = Query(None, description="Search term"),
    wordpress_client = Depends(get_wordpress_client)
):
    """Get list of WordPress posts"""
    try:
        params = {
            'per_page': per_page,
            'page': page
        }
        
        if status:
            params['status'] = status
        if search:
            params['search'] = search
        
        posts = await wordpress_client.get_posts(params)
        return [PostResponse(**post) for post in posts]
        
    except Exception as e:
        logger.error(f"API: Get WordPress posts failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/schedule", response_model=PostResponse)
async def schedule_post(
    request: SchedulePostRequest,
    wordpress_client = Depends(get_wordpress_client),
    content_formatter = Depends(get_content_formatter)
):
    """Schedule a post for future publication"""
    try:
        logger.info(f"API: Scheduling WordPress post: {request.title}")
        
        # Format content
        content_data = request.dict()
        formatted_content = await content_formatter.format_for_wordpress(content_data)
        
        # Schedule post
        result = await wordpress_client.schedule_post(formatted_content, request.publish_time)
        
        return PostResponse(**result)
        
    except Exception as e:
        logger.error(f"API: WordPress scheduling failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# Media Management Endpoints
@router.post("/media/upload", response_model=MediaUploadResponse)
async def upload_media(
    file: UploadFile = File(...),
    alt_text: Optional[str] = Query("", description="Alt text for image"),
    caption: Optional[str] = Query("", description="Image caption"),
    description: Optional[str] = Query("", description="Image description"),
    media_manager = Depends(get_media_manager)
):
    """Upload media file to WordPress"""
    try:
        logger.info(f"API: Uploading media file: {file.filename}")
        
        # Save uploaded file temporarily
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # Upload to WordPress
            result = await media_manager.upload_media(
                tmp_file_path,
                filename=file.filename,
                alt_text=alt_text,
                caption=caption,
                description=description
            )
            
            return MediaUploadResponse(**result)
            
        finally:
            # Clean up temporary file
            os.unlink(tmp_file_path)
            
    except Exception as e:
        logger.error(f"API: Media upload failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/media/upload-from-url", response_model=MediaUploadResponse)
async def upload_media_from_url(
    url: str = Query(..., description="Media URL"),
    filename: Optional[str] = Query(None, description="Custom filename"),
    alt_text: Optional[str] = Query("", description="Alt text"),
    caption: Optional[str] = Query("", description="Caption"),
    description: Optional[str] = Query("", description="Description"),
    media_manager = Depends(get_media_manager)
):
    """Upload media from URL to WordPress"""
    try:
        result = await media_manager.upload_from_url(
            url,
            filename=filename,
            alt_text=alt_text,
            caption=caption,
            description=description
        )
        
        return MediaUploadResponse(**result)
        
    except Exception as e:
        logger.error(f"API: Media upload from URL failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/media", response_model=List[MediaUploadResponse])
async def get_media_library(
    per_page: int = Query(20, description="Items per page"),
    page: int = Query(1, description="Page number"),
    media_type: Optional[str] = Query(None, description="Media type filter"),
    media_manager = Depends(get_media_manager)
):
    """Get WordPress media library"""
    try:
        params = {
            'per_page': per_page,
            'page': page
        }
        
        if media_type:
            params['media_type'] = media_type
        
        media_items = await media_manager.get_media_library(params)
        return [MediaUploadResponse(**item) for item in media_items]
        
    except Exception as e:
        logger.error(f"API: Get media library failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/media/{media_id}", response_model=MediaUploadResponse)
async def get_media_item(
    media_id: int,
    media_manager = Depends(get_media_manager)
):
    """Get specific media item"""
    try:
        result = await media_manager.get_media_item(media_id)
        if result:
            return MediaUploadResponse(**result)
        else:
            raise HTTPException(status_code=404, detail="Media item not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Get media item failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/media/{media_id}")
async def delete_media_item(
    media_id: int,
    force: bool = Query(True, description="Force delete"),
    media_manager = Depends(get_media_manager)
):
    """Delete media item from WordPress"""
    try:
        success = await media_manager.delete_media_item(media_id, force)
        if success:
            return {"media_id": media_id, "status": "deleted"}
        else:
            raise HTTPException(status_code=404, detail="Media item not found or delete failed")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Delete media item failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Image Generation Endpoints
@router.post("/generate-image")
async def generate_image(
    request: GenerateImageRequest,
    media_manager = Depends(get_media_manager)
):
    """Generate featured image using Gemini Flash and upload to WordPress"""
    try:
        logger.info(f"API: Generating image with prompt: {request.prompt}")
        
        # Import image generation service
        from modules.wordpress_integration.services.image_generator import ImageGenerator
        
        image_generator = ImageGenerator()
        
        # Generate image
        image_result = await image_generator.generate_featured_image(
            prompt=request.prompt,
            title=request.title,
            keywords=request.keywords,
            style=request.style,
            aspect_ratio=request.aspect_ratio
        )
        
        if not image_result:
            raise HTTPException(status_code=500, detail="Image generation failed")
        
        # Upload generated image to WordPress
        upload_result = await media_manager.upload_media(
            image_result['file_path'],
            filename=image_result['filename'],
            alt_text=image_result.get('alt_text', ''),
            caption=image_result.get('caption', '')
        )
        
        # Clean up temporary file
        import os
        try:
            os.unlink(image_result['file_path'])
        except:
            pass
        
        return {
            "status": "success",
            "message": "Image generated and uploaded successfully",
            "media": MediaUploadResponse(**upload_result),
            "generation_info": {
                "prompt": request.prompt,
                "style": request.style,
                "model": image_result.get('model', 'gemini-flash')
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Image generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-featured-image")
async def generate_featured_image_from_content(
    content_id: str = Query(..., description="Content ID"),
    auto_upload: bool = Query(True, description="Auto-upload to WordPress"),
    style: Optional[str] = Query("photorealistic", description="Image style"),
    media_manager = Depends(get_media_manager)
):
    """Generate featured image from existing content"""
    try:
        # Get content service to retrieve content data
        from core.container import get_container
        container = get_container()
        content_service = container.get_service('content_service')
        
        if not content_service:
            raise HTTPException(status_code=503, detail="Content service not available")
        
        # Get content data
        content = await content_service.get_content(content_id)
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
        
        # Import image generation service
        from modules.wordpress_integration.services.image_generator import ImageGenerator
        
        image_generator = ImageGenerator()
        
        # Generate image from content
        image_result = await image_generator.generate_from_content(
            content_data=content,
            style=style
        )
        
        if not image_result:
            raise HTTPException(status_code=500, detail="Image generation failed")
        
        response_data = {
            "status": "success",
            "message": "Featured image generated successfully",
            "generation_info": {
                "prompt": image_result.get('prompt', ''),
                "style": style,
                "model": image_result.get('model', 'gemini-flash')
            }
        }
        
        # Upload to WordPress if requested
        if auto_upload:
            upload_result = await media_manager.upload_media(
                image_result['file_path'],
                filename=image_result['filename'],
                alt_text=image_result.get('alt_text', ''),
                caption=image_result.get('caption', '')
            )
            
            response_data["media"] = MediaUploadResponse(**upload_result)
            response_data["wordpress_media_id"] = upload_result['id']
            
            # Clean up temporary file
            import os
            try:
                os.unlink(image_result['file_path'])
            except:
                pass
        else:
            response_data["file_path"] = image_result['file_path']
            response_data["filename"] = image_result['filename']
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Featured image generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WordPress Site Management
@router.get("/categories")
async def get_categories(
    wordpress_client = Depends(get_wordpress_client)
):
    """Get WordPress categories"""
    try:
        categories = await wordpress_client.get_categories()
        return {"categories": categories}
    except Exception as e:
        logger.error(f"API: Get categories failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tags")
async def get_tags(
    wordpress_client = Depends(get_wordpress_client)
):
    """Get WordPress tags"""
    try:
        tags = await wordpress_client.get_tags()
        return {"tags": tags}
    except Exception as e:
        logger.error(f"API: Get tags failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/categories")
async def create_category(
    name: str = Query(..., description="Category name"),
    description: str = Query("", description="Category description"),
    wordpress_client = Depends(get_wordpress_client)
):
    """Create new WordPress category"""
    try:
        result = await wordpress_client.create_category(name, description)
        if result:
            return result
        else:
            raise HTTPException(status_code=400, detail="Failed to create category")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Create category failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tags")
async def create_tag(
    name: str = Query(..., description="Tag name"),
    description: str = Query("", description="Tag description"),
    wordpress_client = Depends(get_wordpress_client)
):
    """Create new WordPress tag"""
    try:
        result = await wordpress_client.create_tag(name, description)
        if result:
            return result
        else:
            raise HTTPException(status_code=400, detail="Failed to create tag")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Create tag failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/site-info")
async def get_site_info(
    wordpress_client = Depends(get_wordpress_client)
):
    """Get WordPress site information"""
    try:
        site_info = await wordpress_client.get_site_info()
        return site_info
    except Exception as e:
        logger.error(f"API: Get site info failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/connection-test")
async def test_wordpress_connection(
    wordpress_client = Depends(get_wordpress_client)
):
    """Test WordPress connection"""
    try:
        connection_ok = await wordpress_client.test_connection()
        return {
            "status": "connected" if connection_ok else "failed",
            "connected": connection_ok,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"API: Connection test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Bulk Operations
@router.post("/bulk-publish")
async def bulk_publish_posts(
    posts: List[PublishPostRequest],
    wordpress_client = Depends(get_wordpress_client),
    content_formatter = Depends(get_content_formatter)
):
    """Bulk publish multiple posts"""
    try:
        logger.info(f"API: Bulk publishing {len(posts)} posts")
        
        # Format all posts
        formatted_posts = []
        for post_data in posts:
            formatted_content = await content_formatter.format_for_wordpress(post_data.dict())
            formatted_posts.append(formatted_content)
        
        # Bulk publish
        results = await wordpress_client.bulk_publish_posts(formatted_posts)
        
        return {
            "total": len(posts),
            "successful": len([r for r in results if r['status'] == 'success']),
            "failed": len([r for r in results if r['status'] == 'failed']),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"API: Bulk publish failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Health and Stats
@router.get("/health")
async def wordpress_health_check(
    wordpress_client = Depends(get_wordpress_client),
    media_manager = Depends(get_media_manager)
):
    """WordPress integration health check"""
    try:
        wp_connection = await wordpress_client.test_connection()
        media_manager_ok = await media_manager.health_check()
        recent_posts = await wordpress_client.get_recent_posts_count()
        media_count = await media_manager.get_media_count()
        
        overall_healthy = wp_connection and media_manager_ok
        
        return {
            "status": "healthy" if overall_healthy else "degraded",
            "services": {
                "wordpress_connection": wp_connection,
                "media_manager": media_manager_ok
            },
            "stats": {
                "recent_posts_count": recent_posts,
                "media_library_size": media_count
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"API: WordPress health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
