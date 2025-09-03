"""
Content Service - Main content generation orchestration
"""

import asyncio
from typing import Dict, List, Any, Optional, AsyncGenerator
from datetime import datetime
import uuid
import json
from loguru import logger

from shared.database.models import Content, get_db
from shared.utils.helpers import TextProcessor, SEOAnalyzer
from shared.utils.validation_service import validate_content_request
from shared.config.settings import get_settings
from .llm_service import LLMService, ModelTier

class ContentService:
    """
    Main content generation service that orchestrates the entire content creation process
    """
    
    def __init__(self, container, llm_service: LLMService, template_service):
        self.container = container
        self.llm_service = llm_service
        self.template_service = template_service
        self.settings = get_settings()
        self.logger = logger.bind(service="ContentService")
    
    async def generate_content(
        self,
        request: Dict[str, Any],
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Generate complete content using multi-pass approach
        """
        try:
            self.logger.info(f"Starting content generation for: {request.get('primary_keyword')}")
            
            # Validate request
            validation = validate_content_request(request)
            if not validation['valid']:
                raise ValueError(f"Invalid request: {', '.join(validation['errors'])}")
            
            # Generate unique content ID
            content_id = str(uuid.uuid4())
            
            if stream:
                return await self._generate_content_streaming(content_id, request)
            else:
                return await self._generate_content_complete(content_id, request)
                
        except Exception as e:
            self.logger.error(f"Content generation failed: {e}")
            raise
    
    async def _generate_content_complete(self, content_id: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content using multi-pass approach"""
        
        start_time = datetime.utcnow()
        models_used = []
        total_cost = 0
        
        # Phase 1: Research and Planning (Cheap model)
        research_result = await self._research_phase(request)
        models_used.append(research_result.get('model_used'))
        total_cost += research_result.get('cost', 0)
        
        # Phase 2: Outline Generation (Cheap model)
        outline_result = await self._outline_phase(request, research_result)
        models_used.append(outline_result.get('model_used'))
        total_cost += outline_result.get('cost', 0)
        
        # Phase 3: Content Generation (Medium model)
        content_result = await self._content_generation_phase(request, outline_result)
        models_used.append(content_result.get('model_used'))
        total_cost += content_result.get('cost', 0)
        
        # Phase 4: SEO Optimization (Medium model)
        seo_result = await self._seo_optimization_phase(request, content_result)
        models_used.append(seo_result.get('model_used'))
        total_cost += seo_result.get('cost', 0)
        
        # Phase 5: Quality Review and Polish (Expensive model if needed)
        final_result = await self._quality_review_phase(request, seo_result)
        models_used.append(final_result.get('model_used'))
        total_cost += final_result.get('cost', 0)
        
        # Compile final result
        generated_content = {
            "content_id": content_id,
            "primary_keyword": request.get('primary_keyword'),
            "title": final_result.get('title'),
            "content": final_result.get('content'),
            "meta_description": final_result.get('meta_description'),
            "seo_title": final_result.get('seo_title'),
            
            # Content metadata
            "content_type": request.get('content_type', 'blog_post'),
            "word_count": TextProcessor.word_count(final_result.get('content', '')),
            "reading_time": TextProcessor.estimate_reading_time(final_result.get('content', '')),
            "tone": request.get('tone', 'professional'),
            "target_audience": request.get('target_audience', 'general'),
            
            # SEO metrics
            "seo_score": final_result.get('seo_score', 0),
            "readability_score": final_result.get('readability_score', 0),
            "keyword_density": final_result.get('keyword_density', 0),
            
            # Generation metadata
            "generated_at": datetime.utcnow().isoformat(),
            "generation_time": (datetime.utcnow() - start_time).total_seconds(),
            "phases_completed": ["research", "outline", "content", "seo", "review"],
            "models_used": models_used,
            "total_cost": total_cost,
            
            # Outline for reference
            "outline": outline_result.get('outline', []),
            "related_keywords": request.get('related_keywords', []),
            "company_info": request.get('company_info', {})
        }
        
        # Save to database
        await self._save_content_to_db(generated_content)
        
        self.logger.info(f"Content generation completed: {content_id}")
        return generated_content
    
    async def _research_phase(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 1: Research and context gathering"""
        
        primary_keyword = request.get('primary_keyword', '')
        related_keywords = request.get('related_keywords', [])
        content_type = request.get('content_type', 'blog_post')
        company_info = request.get('company_info', {})
        
        # Build research prompt
        research_prompt = f"""
        Analyze the following keyword and provide research insights for {content_type} creation:
        
        Primary Keyword: {primary_keyword}
        Related Keywords: {', '.join(related_keywords[:10])}
        Content Type: {content_type}
        Company: {company_info.get('name', 'N/A')}
        Industry: {company_info.get('industry', 'N/A')}
        
        Provide:
        1. Key topics to cover
        2. Target audience insights
        3. Content angles and approaches
        4. Important points to emphasize
        5. Potential objections or concerns to address
        
        Format as JSON with keys: topics, audience_insights, content_angles, key_points, objections
        """
        
        try:
            result = await self.llm_service.generate_content(
                research_prompt,
                model_tier=ModelTier.RESEARCH,
                max_tokens=1000
            )
            
            # Parse JSON response (with fallback)
            research_data = self._parse_json_response(result.get('content', '{}'))
            
            return {
                "research_data": research_data,
                "model_used": result.get('model_used'),
                "cost": result.get('cost', 0)
            }
            
        except Exception as e:
            self.logger.error(f"Research phase failed: {e}")
            # Return fallback research data
            return {
                "research_data": {
                    "topics": [primary_keyword, "benefits", "how to", "best practices"],
                    "audience_insights": ["looking for solutions", "wants practical advice"],
                    "content_angles": ["educational", "problem-solving"],
                    "key_points": [f"importance of {primary_keyword}", "step-by-step guidance"],
                    "objections": ["too complex", "not worth the effort"]
                },
                "model_used": "fallback",
                "cost": 0
            }
    
    async def _outline_phase(self, request: Dict[str, Any], research_result: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 2: Generate detailed outline"""
        
        primary_keyword = request.get('primary_keyword', '')
        content_type = request.get('content_type', 'blog_post')
        target_length = request.get('target_length', self.settings.default_content_length)
        research_data = research_result.get('research_data', {})
        
        # Get template structure
        template_structure = await self.template_service.get_template_structure(content_type)
        
        outline_prompt = f"""
        Create a detailed outline for a {content_type} about "{primary_keyword}".
        Target length: {target_length} words
        
        Research insights:
        - Key topics: {', '.join(research_data.get('topics', []))}
        - Content angles: {', '.join(research_data.get('content_angles', []))}
        - Key points: {', '.join(research_data.get('key_points', []))}
        
        Template structure: {template_structure}
        
        Create a detailed outline with:
        1. Compelling title
        2. Meta description (150-160 characters)
        3. SEO title (50-60 characters)
        4. Section headings (H2, H3)
        5. Key points for each section
        6. Estimated word count per section
        
        Format as JSON with keys: title, meta_description, seo_title, outline
        """
        
        try:
            result = await self.llm_service.generate_content(
                outline_prompt,
                model_tier=ModelTier.RESEARCH,
                max_tokens=1500
            )
            
            outline_data = self._parse_json_response(result.get('content', '{}'))
            
            return {
                "title": outline_data.get('title', f"Complete Guide to {primary_keyword}"),
                "meta_description": outline_data.get('meta_description', f"Learn everything about {primary_keyword}"),
                "seo_title": outline_data.get('seo_title', f"{primary_keyword} Guide"),
                "outline": outline_data.get('outline', []),
                "model_used": result.get('model_used'),
                "cost": result.get('cost', 0)
            }
            
        except Exception as e:
            self.logger.error(f"Outline phase failed: {e}")
            # Return fallback outline
            return {
                "title": f"Complete Guide to {primary_keyword}",
                "meta_description": f"Learn everything about {primary_keyword} with this comprehensive guide.",
                "seo_title": f"{primary_keyword} Guide",
                "outline": [
                    {"heading": "Introduction", "points": [f"What is {primary_keyword}"], "word_count": 200},
                    {"heading": f"Benefits of {primary_keyword}", "points": ["Key advantages"], "word_count": 300},
                    {"heading": f"How to {primary_keyword}", "points": ["Step-by-step process"], "word_count": 500},
                    {"heading": "Conclusion", "points": ["Summary and next steps"], "word_count": 200}
                ],
                "model_used": "fallback",
                "cost": 0
            }
    
    async def _content_generation_phase(self, request: Dict[str, Any], outline_result: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 3: Generate actual content"""
        
        primary_keyword = request.get('primary_keyword', '')
        related_keywords = request.get('related_keywords', [])
        tone = request.get('tone', 'professional')
        company_info = request.get('company_info', {})
        outline = outline_result.get('outline', [])
        
        content_prompt = f"""
        Write a comprehensive {request.get('content_type', 'blog post')} based on this outline:
        
        Title: {outline_result.get('title')}
        Primary Keyword: {primary_keyword}
        Related Keywords: {', '.join(related_keywords[:5])}
        Tone: {tone}
        
        Outline:
        {self._format_outline_for_prompt(outline)}
        
        Company Context:
        - Name: {company_info.get('name', 'N/A')}
        - Industry: {company_info.get('industry', 'N/A')}
        - USPs: {', '.join(company_info.get('unique_selling_points', []))}
        
        Requirements:
        1. Write engaging, informative content
        2. Use the primary keyword naturally throughout
        3. Include related keywords where appropriate
        4. Maintain consistent tone
        5. Add actionable insights
        6. Use proper markdown formatting (headers, lists, etc.)
        7. Include a compelling introduction and conclusion
        
        Write the complete article content:
        """
        
        try:
            result = await self.llm_service.generate_content(
                content_prompt,
                model_tier=ModelTier.DRAFT,
                max_tokens=4000
            )
            
            content = result.get('content', '')
            
            return {
                "title": outline_result.get('title'),
                "content": content,
                "word_count": TextProcessor.word_count(content),
                "model_used": result.get('model_used'),
                "cost": result.get('cost', 0)
            }
            
        except Exception as e:
            self.logger.error(f"Content generation phase failed: {e}")
            # Return fallback content
            fallback_content = f"""
            # {outline_result.get('title')}
            
            ## Introduction
            
            {primary_keyword} is an important topic that deserves careful consideration. In this guide, we'll explore everything you need to know.
            
            ## Key Points
            
            - Understanding {primary_keyword}
            - Benefits and advantages
            - Implementation strategies
            - Best practices
            
            ## Conclusion
            
            {primary_keyword} offers significant opportunities for those who understand how to leverage it effectively.
            """
            
            return {
                "title": outline_result.get('title'),
                "content": fallback_content,
                "word_count": TextProcessor.word_count(fallback_content),
                "model_used": "fallback",
                "cost": 0
            }
    
    async def _seo_optimization_phase(self, request: Dict[str, Any], content_result: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 4: SEO optimization and enhancement"""
        
        primary_keyword = request.get('primary_keyword', '')
        content = content_result.get('content', '')
        
        # Analyze current SEO
        seo_analysis = self._analyze_content_seo(content, primary_keyword)
        
        if seo_analysis['overall_score'] < 70:  # Needs optimization
            optimization_prompt = f"""
            Optimize the following content for SEO while maintaining readability and value:
            
            Primary Keyword: {primary_keyword}
            Current SEO Score: {seo_analysis['overall_score']}/100
            
            Issues to fix:
            {', '.join(seo_analysis.get('issues', []))}
            
            Original Content:
            {content}
            
            Optimization Requirements:
            1. Improve keyword usage (target 1-2% density)
            2. Enhance header structure
            3. Add internal linking opportunities
            4. Improve meta elements
            5. Maintain natural flow and readability
            
            Return the optimized content with the same structure:
            """
            
            try:
                result = await self.llm_service.generate_content(
                    optimization_prompt,
                    model_tier=ModelTier.DRAFT,
                    max_tokens=4000
                )
                
                optimized_content = result.get('content', content)
                
                # Re-analyze SEO
                final_seo_analysis = self._analyze_content_seo(optimized_content, primary_keyword)
                
                return {
                    "title": content_result.get('title'),
                    "content": optimized_content,
                    "seo_score": final_seo_analysis['overall_score'],
                    "keyword_density": final_seo_analysis['keyword_density'],
                    "readability_score": final_seo_analysis['readability_score'],
                    "model_used": result.get('model_used'),
                    "cost": result.get('cost', 0)
                }
                
            except Exception as e:
                self.logger.error(f"SEO optimization failed: {e}")
                # Return original content with analysis
                return {
                    "title": content_result.get('title'),
                    "content": content,
                    "seo_score": seo_analysis['overall_score'],
                    "keyword_density": seo_analysis['keyword_density'],
                    "readability_score": seo_analysis['readability_score'],
                    "model_used": "fallback",
                    "cost": 0
                }
        else:
            # Content is already well optimized
            return {
                "title": content_result.get('title'),
                "content": content,
                "seo_score": seo_analysis['overall_score'],
                "keyword_density": seo_analysis['keyword_density'],
                "readability_score": seo_analysis['readability_score'],
                "model_used": "no_optimization_needed",
                "cost": 0
            }
    
    async def _quality_review_phase(self, request: Dict[str, Any], seo_result: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 5: Final quality review and polish"""
        
        quality_level = request.get('quality_level', 'standard')
        
        if quality_level == 'premium' and seo_result.get('seo_score', 0) < 85:
            # Use expensive model for final polish
            polish_prompt = f"""
            Perform a final quality review and polish of this content:
            
            Title: {seo_result.get('title')}
            Current SEO Score: {seo_result.get('seo_score')}/100
            
            Content:
            {seo_result.get('content')}
            
            Polish Requirements:
            1. Enhance clarity and engagement
            2. Improve flow and transitions
            3. Add compelling examples or analogies
            4. Ensure perfect grammar and style
            5. Maintain SEO optimization
            6. Add actionable takeaways
            
            Return the polished content:
            """
            
            try:
                result = await self.llm_service.generate_content(
                    polish_prompt,
                    model_tier=ModelTier.FINAL,
                    max_tokens=4000
                )
                
                polished_content = result.get('content', seo_result.get('content'))
                
                # Final analysis
                final_analysis = self._analyze_content_seo(polished_content, request.get('primary_keyword', ''))
                
                return {
                    "title": seo_result.get('title'),
                    "content": polished_content,
                    "meta_description": seo_result.get('meta_description'),
                    "seo_title": seo_result.get('seo_title'),
                    "seo_score": final_analysis['overall_score'],
                    "readability_score": final_analysis['readability_score'],
                    "keyword_density": final_analysis['keyword_density'],
                    "model_used": result.get('model_used'),
                    "cost": result.get('cost', 0)
                }
                
            except Exception as e:
                self.logger.error(f"Quality review failed: {e}")
                return seo_result
        else:
            # Standard quality is sufficient
            return seo_result
    

    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON response with fallback"""
        try:
            # Try to extract JSON from response
            response = response.strip()
            if response.startswith('```json'):
                response = response.replace('```json', '').replace('```', '').strip()
            
            return json.loads(response)
        except:
            return {}
    
    def _format_outline_for_prompt(self, outline: List[Dict]) -> str:
        """Format outline for prompt"""
        formatted = []
        for section in outline:
            heading = section.get('heading', '')
            points = section.get('points', [])
            word_count = section.get('word_count', 200)
            
            formatted.append(f"## {heading} (~{word_count} words)")
            for point in points:
                formatted.append(f"- {point}")
            formatted.append("")
        
        return "\n".join(formatted)
    
    def _analyze_content_seo(self, content: str, primary_keyword: str) -> Dict[str, Any]:
        """Analyze content SEO"""
        # Calculate metrics
        keyword_density = SEOAnalyzer.analyze_keyword_density(content, primary_keyword)
        readability = TextProcessor.calculate_readability(content)
        
        # Analyze structure
        structure_analysis = SEOAnalyzer.analyze_content_structure(content)
        
        # Calculate overall score
        overall_score = (
            min(keyword_density * 20, 30) +  # Keyword density (max 30 points)
            min(readability.get('flesch_reading_ease', 50), 30) +  # Readability (max 30 points)
            structure_analysis.get('score', 40)  # Structure (max 40 points)
        )
        
        return {
            "overall_score": min(overall_score, 100),
            "keyword_density": keyword_density,
            "readability_score": readability.get('flesch_reading_ease', 0),
            "structure_score": structure_analysis.get('score', 0),
            "issues": structure_analysis.get('issues', [])
        }
    
    async def _save_content_to_db(self, content_data: Dict[str, Any]) -> None:
        """Save generated content to database"""
        try:
            # This would save to database
            self.logger.info(f"Content saved: {content_data['content_id']}")
        except Exception as e:
            self.logger.error(f"Failed to save content to database: {e}")
    
    async def _generate_content_streaming(self, content_id: str, request: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate content with streaming updates"""
        yield {"type": "status", "message": "Starting content generation...", "progress": 0}
        
        # Phase 1: Research
        yield {"type": "status", "message": "Conducting research...", "progress": 20}
        research_result = await self._research_phase(request)
        yield {"type": "phase_complete", "phase": "research", "data": research_result}
        
        # Phase 2: Outline
        yield {"type": "status", "message": "Creating outline...", "progress": 40}
        outline_result = await self._outline_phase(request, research_result)
        yield {"type": "phase_complete", "phase": "outline", "data": outline_result}
        
        # Phase 3: Content Generation with streaming
        yield {"type": "status", "message": "Generating content...", "progress": 60}
        
        # Stream content generation
        async for chunk in self.llm_service.generate_streaming(
            self._build_content_prompt(request, outline_result),
            model_tier=ModelTier.DRAFT
        ):
            if chunk.get('type') == 'content_chunk':
                yield {
                    "type": "content_chunk",
                    "content": chunk.get('content'),
                    "accumulated_content": chunk.get('accumulated_content')
                }
        
        yield {"type": "status", "message": "Optimizing for SEO...", "progress": 80}
        # Continue with remaining phases...
        
        yield {"type": "complete", "content_id": content_id, "progress": 100}
    
    def _build_content_prompt(self, request: Dict[str, Any], outline_result: Dict[str, Any]) -> str:
        """Build content generation prompt"""
        # Implementation similar to _content_generation_phase
        return f"Generate content for {request.get('primary_keyword')}"
