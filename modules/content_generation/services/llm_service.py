"""
LLM Service - Multi-model LLM management with cost optimization
"""

import asyncio
from typing import Dict, List, Any, Optional, AsyncGenerator
from datetime import datetime
from enum import Enum
import openai
import anthropic
from loguru import logger

from shared.config.settings import get_settings
from shared.utils.helpers import CostCalculator
from shared.database.models import UsageTracking, get_db

class ModelTier(Enum):
    """Model tiers for cost optimization"""
    RESEARCH = "research"      # Cheapest models for research/analysis
    DRAFT = "draft"           # Medium cost for draft generation
    FINAL = "final"           # Most expensive for final polish
    FALLBACK = "fallback"     # Local/free models

class LLMService:
    """
    Multi-model LLM service with intelligent model selection and cost optimization
    """
    
    def __init__(self, container):
        self.container = container
        self.settings = get_settings()
        self.logger = logger.bind(service="LLMService")
        
        # Model configurations
        self.model_configs = {
            ModelTier.RESEARCH: {
                "primary": "gpt-4o-mini",
                "fallback": "claude-3-haiku",
                "max_tokens": 2000,
                "temperature": 0.7
            },
            ModelTier.DRAFT: {
                "primary": "claude-3-haiku", 
                "fallback": "gpt-4o-mini",
                "max_tokens": 4000,
                "temperature": 0.8
            },
            ModelTier.FINAL: {
                "primary": "gpt-4o",
                "fallback": "claude-3-sonnet",
                "max_tokens": 4000,
                "temperature": 0.7
            }
        }
        
        # Initialize clients
        self.openai_client = None
        self.anthropic_client = None
        self._init_clients()
    
    def _init_clients(self):
        """Initialize LLM API clients"""
        try:
            if self.settings.openai_api_key:
                self.openai_client = openai.AsyncOpenAI(api_key=self.settings.openai_api_key)
                self.logger.info("OpenAI client initialized")
            
            if self.settings.anthropic_api_key:
                self.anthropic_client = anthropic.AsyncAnthropic(api_key=self.settings.anthropic_api_key)
                self.logger.info("Anthropic client initialized")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize LLM clients: {e}")
    
    async def generate_content(
        self, 
        prompt: str,
        model_tier: ModelTier = ModelTier.DRAFT,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stream: bool = False,
        user_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Generate content using the appropriate model based on tier and budget
        """
        try:
            # Check user budget and usage limits
            if not await self._check_user_limits(user_id):
                raise Exception("User has exceeded daily limits")
            
            # Select optimal model
            model_info = await self._select_optimal_model(model_tier, user_id)
            
            # Generate content
            if stream:
                return await self._generate_streaming(
                    prompt, model_info, max_tokens, temperature, user_id
                )
            else:
                return await self._generate_complete(
                    prompt, model_info, max_tokens, temperature, user_id
                )
                
        except Exception as e:
            self.logger.error(f"Content generation failed: {e}")
            raise
    
    async def generate_streaming(
        self,
        prompt: str,
        model_tier: ModelTier = ModelTier.DRAFT,
        user_id: str = "default"
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generate content with streaming response
        """
        try:
            model_info = await self._select_optimal_model(model_tier, user_id)
            
            if model_info["provider"] == "openai":
                async for chunk in self._stream_openai(prompt, model_info):
                    yield chunk
            elif model_info["provider"] == "anthropic":
                async for chunk in self._stream_anthropic(prompt, model_info):
                    yield chunk
                    
        except Exception as e:
            self.logger.error(f"Streaming generation failed: {e}")
            yield {"error": str(e), "status": "error"}
    
    async def _select_optimal_model(self, model_tier: ModelTier, user_id: str) -> Dict[str, Any]:
        """
        Select the optimal model based on tier, budget, and availability
        """
        # Get user's current usage
        current_usage = await self._get_user_daily_usage(user_id)
        remaining_budget = self.settings.cost_per_user_limit - current_usage.get('cost', 0)
        
        # Get tier configuration
        tier_config = self.model_configs[model_tier]
        
        # Try primary model first
        primary_model = tier_config["primary"]
        primary_cost = self._estimate_generation_cost(primary_model, 1000)  # Estimate for 1k tokens
        
        if remaining_budget >= primary_cost:
            if self._is_model_available(primary_model):
                return {
                    "model": primary_model,
                    "provider": self._get_provider(primary_model),
                    "config": tier_config,
                    "estimated_cost": primary_cost
                }
        
        # Fallback to secondary model
        fallback_model = tier_config["fallback"]
        fallback_cost = self._estimate_generation_cost(fallback_model, 1000)
        
        if remaining_budget >= fallback_cost:
            if self._is_model_available(fallback_model):
                return {
                    "model": fallback_model,
                    "provider": self._get_provider(fallback_model),
                    "config": tier_config,
                    "estimated_cost": fallback_cost
                }
        
        # If budget is too low, use cheapest available model
        cheapest_model = "gpt-4o-mini"  # Fallback to cheapest
        return {
            "model": cheapest_model,
            "provider": self._get_provider(cheapest_model),
            "config": self.model_configs[ModelTier.RESEARCH],
            "estimated_cost": self._estimate_generation_cost(cheapest_model, 1000)
        }
    
    async def _generate_complete(
        self,
        prompt: str,
        model_info: Dict[str, Any],
        max_tokens: Optional[int],
        temperature: Optional[float],
        user_id: str
    ) -> Dict[str, Any]:
        """Generate complete content response"""
        
        start_time = datetime.utcnow()
        provider = model_info["provider"]
        model = model_info["model"]
        config = model_info["config"]
        
        # Use provided params or config defaults
        max_tokens = max_tokens or config["max_tokens"]
        temperature = temperature or config["temperature"]
        
        try:
            if provider == "openai":
                result = await self._generate_openai(prompt, model, max_tokens, temperature)
            elif provider == "anthropic":
                result = await self._generate_anthropic(prompt, model, max_tokens, temperature)
            else:
                raise ValueError(f"Unsupported provider: {provider}")
            
            # Calculate actual cost
            input_tokens = CostCalculator.estimate_tokens(prompt)
            output_tokens = CostCalculator.estimate_tokens(result.get('content', ''))
            actual_cost = CostCalculator.calculate_cost(model, input_tokens, output_tokens)
            
            # Log usage
            await self._log_usage(user_id, model, input_tokens, output_tokens, actual_cost)
            
            # Add metadata
            result.update({
                "model_used": model,
                "provider": provider,
                "generation_time": (datetime.utcnow() - start_time).total_seconds(),
                "cost": actual_cost,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Generation failed for {provider}/{model}: {e}")
            raise
    
    async def _generate_openai(self, prompt: str, model: str, max_tokens: int, temperature: float) -> Dict[str, Any]:
        """Generate content using OpenAI"""
        if not self.openai_client:
            raise Exception("OpenAI client not initialized")
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return {
                "content": response.choices[0].message.content,
                "finish_reason": response.choices[0].finish_reason,
                "model": response.model
            }
            
        except Exception as e:
            self.logger.error(f"OpenAI generation failed: {e}")
            raise
    
    async def _generate_anthropic(self, prompt: str, model: str, max_tokens: int, temperature: float) -> Dict[str, Any]:
        """Generate content using Anthropic"""
        if not self.anthropic_client:
            raise Exception("Anthropic client not initialized")
        
        try:
            response = await self.anthropic_client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return {
                "content": response.content[0].text,
                "model": response.model,
                "stop_reason": response.stop_reason
            }
            
        except Exception as e:
            self.logger.error(f"Anthropic generation failed: {e}")
            raise
    
    async def _stream_openai(self, prompt: str, model_info: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream content from OpenAI"""
        if not self.openai_client:
            raise Exception("OpenAI client not initialized")
        
        try:
            stream = await self.openai_client.chat.completions.create(
                model=model_info["model"],
                messages=[{"role": "user", "content": prompt}],
                max_tokens=model_info["config"]["max_tokens"],
                temperature=model_info["config"]["temperature"],
                stream=True
            )
            
            collected_content = ""
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content_chunk = chunk.choices[0].delta.content
                    collected_content += content_chunk
                    
                    yield {
                        "type": "content_chunk",
                        "content": content_chunk,
                        "accumulated_content": collected_content,
                        "model": model_info["model"],
                        "status": "generating"
                    }
            
            yield {
                "type": "generation_complete",
                "final_content": collected_content,
                "model": model_info["model"], 
                "status": "complete"
            }
            
        except Exception as e:
            self.logger.error(f"OpenAI streaming failed: {e}")
            yield {"error": str(e), "status": "error"}
    
    async def _stream_anthropic(self, prompt: str, model_info: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream content from Anthropic"""
        if not self.anthropic_client:
            raise Exception("Anthropic client not initialized")
        
        try:
            stream = await self.anthropic_client.messages.create(
                model=model_info["model"],
                max_tokens=model_info["config"]["max_tokens"],
                temperature=model_info["config"]["temperature"],
                messages=[{"role": "user", "content": prompt}],
                stream=True
            )
            
            collected_content = ""
            async for chunk in stream:
                if chunk.type == "content_block_delta":
                    content_chunk = chunk.delta.text
                    collected_content += content_chunk
                    
                    yield {
                        "type": "content_chunk",
                        "content": content_chunk,
                        "accumulated_content": collected_content,
                        "model": model_info["model"],
                        "status": "generating"
                    }
            
            yield {
                "type": "generation_complete",
                "final_content": collected_content,
                "model": model_info["model"],
                "status": "complete"
            }
            
        except Exception as e:
            self.logger.error(f"Anthropic streaming failed: {e}")
            yield {"error": str(e), "status": "error"}
    
    def _get_provider(self, model: str) -> str:
        """Get provider for a model"""
        if model.startswith(("gpt-", "text-", "davinci")):
            return "openai"
        elif model.startswith("claude-"):
            return "anthropic"
        else:
            return "unknown"
    
    def _is_model_available(self, model: str) -> bool:
        """Check if model is available"""
        provider = self._get_provider(model)
        
        if provider == "openai":
            return self.openai_client is not None
        elif provider == "anthropic":
            return self.anthropic_client is not None
        
        return False
    
    def _estimate_generation_cost(self, model: str, estimated_tokens: int) -> float:
        """Estimate generation cost"""
        return CostCalculator.calculate_cost(model, estimated_tokens // 2, estimated_tokens // 2)
    
    async def _check_user_limits(self, user_id: str) -> bool:
        """Check if user is within usage limits"""
        try:
            usage = await self._get_user_daily_usage(user_id)
            daily_cost = usage.get('cost', 0)
            daily_calls = usage.get('api_calls', 0)
            
            return (
                daily_cost < self.settings.cost_per_user_limit and
                daily_calls < self.settings.daily_user_limit
            )
        except Exception as e:
            self.logger.error(f"Error checking user limits: {e}")
            return True  # Allow by default if check fails
    
    async def _get_user_daily_usage(self, user_id: str) -> Dict[str, float]:
        """Get user's daily usage"""
        try:
            # This would query the database for today's usage
            # For now, return mock data
            return {"cost": 0.0, "api_calls": 0, "tokens_used": 0}
        except Exception as e:
            self.logger.error(f"Error getting user usage: {e}")
            return {"cost": 0.0, "api_calls": 0, "tokens_used": 0}
    
    async def _log_usage(self, user_id: str, model: str, input_tokens: int, output_tokens: int, cost: float):
        """Log usage to database"""
        try:
            # This would log to the database
            self.logger.info(f"Usage logged - User: {user_id}, Model: {model}, Cost: ${cost:.4f}")
        except Exception as e:
            self.logger.error(f"Error logging usage: {e}")
    
    async def health_check(self) -> bool:
        """Check if LLM services are available"""
        try:
            # Test OpenAI
            openai_ok = False
            if self.openai_client:
                try:
                    # Simple test call
                    await self.openai_client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": "test"}],
                        max_tokens=1
                    )
                    openai_ok = True
                except:
                    pass
            
            # Test Anthropic
            anthropic_ok = False
            if self.anthropic_client:
                try:
                    # Simple test call
                    await self.anthropic_client.messages.create(
                        model="claude-3-haiku-20240307",
                        max_tokens=1,
                        messages=[{"role": "user", "content": "test"}]
                    )
                    anthropic_ok = True
                except:
                    pass
            
            return openai_ok or anthropic_ok
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
