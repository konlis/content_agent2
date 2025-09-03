"""
Template Service - Content template management
"""

from typing import Dict, List, Any, Optional
from loguru import logger

class TemplateService:
    """
    Service for managing content templates and structures
    """
    
    def __init__(self, container):
        self.container = container
        self.logger = logger.bind(service="TemplateService")
        
        # Initialize templates
        self.templates = self._load_templates()
        
        # Industry-specific variations
        self.industry_variations = self._load_industry_variations()
    
    def _load_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load content templates"""
        return {
            "blog_post": {
                "name": "Blog Post",
                "description": "Comprehensive blog post template",
                "structure": [
                    {"section": "introduction", "word_count": 150, "purpose": "Hook and overview"},
                    {"section": "main_content", "word_count": 800, "purpose": "Core information"},
                    {"section": "conclusion", "word_count": 150, "purpose": "Summary and CTA"}
                ],
                "seo_requirements": {
                    "title_length": [30, 60],
                    "meta_description_length": [150, 160],
                    "h1_count": 1,
                    "h2_minimum": 3,
                    "keyword_density": [1, 3]
                }
            },
            
            "social_media": {
                "name": "Social Media Post",
                "description": "Engaging social media content",
                "structure": [
                    {"section": "hook", "word_count": 20, "purpose": "Grab attention"},
                    {"section": "value", "word_count": 80, "purpose": "Provide value"},
                    {"section": "cta", "word_count": 20, "purpose": "Call to action"}
                ],
                "platform_variants": {
                    "linkedin": {"tone": "professional", "length": [150, 300]},
                    "twitter": {"tone": "casual", "length": [50, 280]},
                    "facebook": {"tone": "friendly", "length": [100, 250]},
                    "instagram": {"tone": "visual", "length": [100, 200]}
                }
            },
            
            "website_copy": {
                "name": "Website Copy",
                "description": "Conversion-focused website content",
                "structure": [
                    {"section": "headline", "word_count": 20, "purpose": "Value proposition"},
                    {"section": "problem", "word_count": 100, "purpose": "Identify pain points"},
                    {"section": "solution", "word_count": 200, "purpose": "Present solution"},
                    {"section": "benefits", "word_count": 150, "purpose": "List benefits"},
                    {"section": "social_proof", "word_count": 100, "purpose": "Build trust"},
                    {"section": "cta", "word_count": 50, "purpose": "Drive action"}
                ],
                "conversion_elements": [
                    "clear_value_proposition",
                    "benefit_focused_copy", 
                    "social_proof_integration",
                    "urgency_creation",
                    "multiple_ctas"
                ]
            },
            
            "product_description": {
                "name": "Product Description",
                "description": "E-commerce product descriptions",
                "structure": [
                    {"section": "headline", "word_count": 15, "purpose": "Product name and key benefit"},
                    {"section": "features", "word_count": 100, "purpose": "Key features"},
                    {"section": "benefits", "word_count": 120, "purpose": "Customer benefits"},
                    {"section": "specifications", "word_count": 80, "purpose": "Technical details"},
                    {"section": "guarantee", "word_count": 35, "purpose": "Risk reversal"}
                ]
            },
            
            "email_newsletter": {
                "name": "Email Newsletter",
                "description": "Engaging email newsletter content",
                "structure": [
                    {"section": "subject_line", "word_count": 8, "purpose": "Open rate optimization"},
                    {"section": "greeting", "word_count": 20, "purpose": "Personal connection"},
                    {"section": "main_content", "word_count": 200, "purpose": "Value delivery"},
                    {"section": "cta", "word_count": 30, "purpose": "Drive action"},
                    {"section": "signature", "word_count": 20, "purpose": "Brand consistency"}
                ]
            }
        }
    
    def _load_industry_variations(self) -> Dict[str, Dict[str, Any]]:
        """Load industry-specific template variations"""
        return {
            "technology": {
                "tone_adjustments": {
                    "technical_depth": "high",
                    "jargon_level": "moderate",
                    "innovation_focus": True
                },
                "content_elements": [
                    "technical_specifications",
                    "use_cases",
                    "integration_examples",
                    "scalability_discussion"
                ]
            },
            
            "healthcare": {
                "tone_adjustments": {
                    "authority_level": "high",
                    "compliance_awareness": True,
                    "empathy_focus": True
                },
                "content_elements": [
                    "credibility_indicators",
                    "patient_outcomes",
                    "safety_information",
                    "expert_endorsements"
                ]
            },
            
            "finance": {
                "tone_adjustments": {
                    "trust_building": "critical",
                    "regulatory_awareness": True,
                    "risk_disclosure": True
                },
                "content_elements": [
                    "regulatory_compliance",
                    "risk_warnings",
                    "performance_data",
                    "security_features"
                ]
            },
            
            "education": {
                "tone_adjustments": {
                    "accessibility": "high",
                    "encouragement": True,
                    "step_by_step": True
                },
                "content_elements": [
                    "learning_objectives",
                    "practical_examples",
                    "progress_indicators",
                    "additional_resources"
                ]
            }
        }
    
    async def get_template_structure(self, content_type: str) -> Dict[str, Any]:
        """Get template structure for content type"""
        template = self.templates.get(content_type, {})
        return template.get('structure', [])
    
    def get_available_templates(self) -> List[Dict[str, str]]:
        """Get list of available templates"""
        return [
            {
                "key": key,
                "name": template.get('name', key.title()),
                "description": template.get('description', '')
            }
            for key, template in self.templates.items()
        ]
    
    def get_template_details(self, template_key: str) -> Optional[Dict[str, Any]]:
        """Get detailed template information"""
        return self.templates.get(template_key)
    
    async def get_industry_optimized_template(self, content_type: str, industry: str) -> Dict[str, Any]:
        """Get template optimized for specific industry"""
        base_template = self.templates.get(content_type, {})
        industry_variation = self.industry_variations.get(industry, {})
        
        # Merge base template with industry-specific adjustments
        optimized_template = base_template.copy()
        
        if industry_variation:
            # Apply tone adjustments
            tone_adjustments = industry_variation.get('tone_adjustments', {})
            optimized_template['tone_adjustments'] = tone_adjustments
            
            # Add industry-specific content elements
            content_elements = industry_variation.get('content_elements', [])
            optimized_template['industry_elements'] = content_elements
            
            # Adjust structure if needed
            if industry == 'healthcare':
                # Add disclaimer section for healthcare content
                structure = optimized_template.get('structure', [])
                structure.append({
                    "section": "disclaimer",
                    "word_count": 50,
                    "purpose": "Medical disclaimer"
                })
            
            elif industry == 'finance':
                # Add risk disclosure for finance content
                structure = optimized_template.get('structure', [])
                structure.append({
                    "section": "risk_disclosure", 
                    "word_count": 75,
                    "purpose": "Financial risk warning"
                })
        
        return optimized_template
    
    def get_content_prompts(self, template_key: str, **kwargs) -> Dict[str, str]:
        """Get specialized prompts for different content types"""
        
        prompts = {
            "blog_post": {
                "intro_prompt": "Write an engaging introduction that hooks the reader and clearly presents the topic.",
                "body_prompt": "Develop the main content with detailed explanations, examples, and actionable insights.",
                "conclusion_prompt": "Summarize key points and provide a clear call-to-action."
            },
            
            "social_media": {
                "hook_prompt": "Create an attention-grabbing opening that stops the scroll.",
                "value_prompt": "Deliver valuable information or insights in a concise, engaging way.",
                "cta_prompt": "Include a compelling call-to-action that encourages engagement."
            },
            
            "website_copy": {
                "headline_prompt": "Create a compelling headline that clearly communicates the value proposition.",
                "body_prompt": "Write persuasive copy that addresses pain points and presents solutions.",
                "cta_prompt": "Write conversion-focused calls-to-action that drive desired actions."
            },
            
            "product_description": {
                "feature_prompt": "List key product features in an organized, scannable format.",
                "benefit_prompt": "Explain how each feature translates into customer benefits.",
                "conversion_prompt": "Add persuasive elements that encourage purchase decisions."
            },
            
            "email_newsletter": {
                "subject_prompt": "Write compelling subject lines that maximize open rates.",
                "content_prompt": "Create valuable newsletter content that engages subscribers.",
                "cta_prompt": "Include clear calls-to-action that drive desired behaviors."
            }
        }
        
        return prompts.get(template_key, {})
    
    def validate_content_against_template(self, content: str, template_key: str) -> Dict[str, Any]:
        """Validate generated content against template requirements"""
        template = self.templates.get(template_key, {})
        if not template:
            return {"valid": False, "errors": ["Template not found"]}
        
        errors = []
        warnings = []
        
        # Check word count
        word_count = len(content.split())
        expected_structure = template.get('structure', [])
        expected_total_words = sum(section.get('word_count', 0) for section in expected_structure)
        
        word_count_variance = abs(word_count - expected_total_words) / expected_total_words if expected_total_words > 0 else 0
        
        if word_count_variance > 0.3:  # More than 30% variance
            warnings.append(f"Word count variance: expected ~{expected_total_words}, got {word_count}")
        
        # Check SEO requirements if applicable
        seo_requirements = template.get('seo_requirements', {})
        if seo_requirements:
            # Check title length (if title is in content)
            title_match = content.split('\n')[0] if content else ""
            title_length = len(title_match)
            
            expected_title_range = seo_requirements.get('title_length', [0, 100])
            if not (expected_title_range[0] <= title_length <= expected_title_range[1]):
                warnings.append(f"Title length should be {expected_title_range[0]}-{expected_title_range[1]} characters")
        
        # Check structure elements
        structure_score = self._analyze_content_structure(content, expected_structure)
        if structure_score < 0.7:
            warnings.append("Content structure doesn't match template expectations")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "structure_score": structure_score,
            "word_count": word_count,
            "expected_word_count": expected_total_words
        }
    
    def _analyze_content_structure(self, content: str, expected_structure: List[Dict]) -> float:
        """Analyze how well content matches expected structure"""
        if not expected_structure:
            return 1.0
        
        # Simple structure analysis
        sections_found = 0
        lines = content.split('\n')
        
        for expected_section in expected_structure:
            section_name = expected_section.get('section', '').lower()
            
            # Look for section indicators (headers, keywords)
            for line in lines:
                if section_name in line.lower() or any(word in line.lower() for word in section_name.split('_')):
                    sections_found += 1
                    break
        
        return sections_found / len(expected_structure) if expected_structure else 1.0
    
    def get_template_examples(self, template_key: str) -> Dict[str, str]:
        """Get example content for templates"""
        examples = {
            "blog_post": {
                "title": "The Complete Guide to {keyword}",
                "introduction": "Are you looking to master {keyword}? In this comprehensive guide, we'll explore everything you need to know to get started and achieve success.",
                "conclusion": "By following these strategies for {keyword}, you'll be well on your way to achieving your goals. Start implementing these tips today!"
            },
            
            "social_media": {
                "linkedin": "🚀 Here's what I learned about {keyword} this week:\n\n✅ Key insight 1\n✅ Key insight 2\n✅ Key insight 3\n\nWhat's your experience with {keyword}?",
                "twitter": "Quick tip for {keyword}: [insert valuable insight] 💡\n\nTried this yet? Let me know how it goes! 👇",
                "facebook": "Struggling with {keyword}? Here's a simple approach that's worked wonders for our clients... [continue with value]"
            },
            
            "website_copy": {
                "headline": "Finally, A {keyword} Solution That Actually Works",
                "subheadline": "Join thousands who've already transformed their results with our proven {keyword} system",
                "cta": "Get Started Free Today"
            }
        }
        
        return examples.get(template_key, {})
    
    def is_ready(self) -> bool:
        """Check if template service is ready"""
        return len(self.templates) > 0
    
    async def create_custom_template(self, template_data: Dict[str, Any]) -> str:
        """Create a custom template"""
        template_key = template_data.get('key', f"custom_{len(self.templates)}")
        
        # Validate template data
        required_fields = ['name', 'description', 'structure']
        for field in required_fields:
            if field not in template_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Add to templates
        self.templates[template_key] = template_data
        
        self.logger.info(f"Custom template created: {template_key}")
        return template_key
    
    def get_template_statistics(self) -> Dict[str, Any]:
        """Get statistics about available templates"""
        total_templates = len(self.templates)
        industry_variations = len(self.industry_variations)
        
        # Calculate average word counts by template type
        avg_word_counts = {}
        for key, template in self.templates.items():
            structure = template.get('structure', [])
            total_words = sum(section.get('word_count', 0) for section in structure)
            avg_word_counts[key] = total_words
        
        return {
            "total_templates": total_templates,
            "industry_variations": industry_variations,
            "average_word_counts": avg_word_counts,
            "most_comprehensive": max(avg_word_counts.items(), key=lambda x: x[1])[0] if avg_word_counts else None,
            "most_concise": min(avg_word_counts.items(), key=lambda x: x[1])[0] if avg_word_counts else None
        }
