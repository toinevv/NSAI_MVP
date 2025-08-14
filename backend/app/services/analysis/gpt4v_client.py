"""
GPT-4V Client Service for NewSystem.AI
Handles OpenAI GPT-4V API integration for workflow analysis
Pragmatic MVP approach with cost optimization
"""

import logging
import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
import time
import asyncio
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)


class GPT4VClient:
    """
    Client for GPT-4V Vision API integration
    Analyzes screen recording frames to identify automation opportunities
    Focus: General workflow detection for business operations
    """
    
    def __init__(self):
        """Initialize OpenAI client with API key"""
        if not settings.OPENAI_API_KEY:
            logger.warning("OpenAI API key not configured")
            self.client = None
        else:
            self.client = OpenAI(
                api_key=settings.OPENAI_API_KEY,
                timeout=300.0  # 5 minutes for vision analysis
            )
        
        # Configuration for GPT-4V
        self.model = settings.GPT4V_MODEL
        self.max_tokens = settings.MAX_TOKENS_PER_REQUEST
        self.temperature = settings.GPT4V_TEMPERATURE  # From config/env
        self.image_detail = settings.GPT4V_IMAGE_DETAIL  # From config/env
        self.max_retries = 3
        self.retry_delay = 2  # Initial delay in seconds
        
        # Cost tracking
        self.cost_per_image = settings.COST_PER_GPT4V_REQUEST
        
    async def analyze_frames(
        self,
        frames: List[Dict[str, Any]],
        system_prompt: str,
        user_prompt: str
    ) -> Dict[str, Any]:
        """
        Analyze multiple frames using GPT-4V
        
        Args:
            frames: List of frame data with base64 images
            system_prompt: System context for analysis
            user_prompt: Specific analysis instructions
            
        Returns:
            Analysis results with workflow insights
        """
        if not self.client:
            logger.error("OpenAI client not initialized - missing API key")
            return {
                "error": "OpenAI API not configured",
                "success": False
            }
        
        try:
            # Prepare messages with frames
            messages = self._prepare_messages(frames, system_prompt, user_prompt)
            
            # Make API call with retry logic
            response = await self._call_with_retry(messages)
            
            if not response:
                return {
                    "error": "Failed to get response from GPT-4V",
                    "success": False
                }
            
            # Parse and validate response
            result = self._parse_response(response)
            
            # Add metadata
            result["metadata"] = {
                "frame_count": len(frames),
                "model": self.model,
                "estimated_cost": len(frames) * self.cost_per_image,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Successfully analyzed {len(frames)} frames")
            return result
            
        except Exception as e:
            logger.error(f"GPT-4V analysis failed: {e}")
            return {
                "error": str(e),
                "success": False
            }
    
    def _prepare_messages(
        self,
        frames: List[Dict[str, Any]],
        system_prompt: str,
        user_prompt: str
    ) -> List[Dict[str, Any]]:
        """
        Prepare messages for GPT-4V API call
        
        Args:
            frames: Frame data with base64 images
            system_prompt: System context
            user_prompt: Analysis instructions
            
        Returns:
            Formatted messages for OpenAI API
        """
        messages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]
        
        # Build user message with all frames
        user_content = [
            {
                "type": "text",
                "text": user_prompt
            }
        ]
        
        # Add each frame as an image
        frames_added = 0
        for i, frame in enumerate(frames):
            if "image_base64" in frame:
                user_content.append({
                    "type": "text",
                    "text": f"\n--- Frame {i+1} (at {frame.get('timestamp_formatted', 'unknown')}): ---"
                })
                user_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{frame['image_base64']}",
                        "detail": self.image_detail  # Configurable image detail
                    }
                })
                frames_added += 1
        
        logger.info(f"Prepared message with {frames_added} frames out of {len(frames)} total frames")
        
        if frames_added == 0:
            logger.error("No frames with image_base64 data found!")
        
        messages.append({
            "role": "user",
            "content": user_content
        })
        
        return messages
    
    async def _call_with_retry(
        self,
        messages: List[Dict[str, Any]]
    ) -> Optional[Any]:
        """
        Call GPT-4V API with exponential backoff retry
        
        Args:
            messages: Prepared messages for API
            
        Returns:
            API response or None if all retries failed
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Calling GPT-4V API (attempt {attempt + 1}/{self.max_retries})")
                
                # Make the API call
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    response_format={"type": "json_object"}  # Force JSON response
                )
                
                return response
                
            except Exception as e:
                last_error = e
                error_msg = str(e)
                logger.warning(f"GPT-4V API call failed (attempt {attempt + 1}): {error_msg}")
                
                # Log more details about specific error types
                if "invalid_request_error" in error_msg.lower():
                    logger.error(f"Invalid request error - likely malformed data: {error_msg}")
                elif "rate_limit" in error_msg.lower():
                    logger.warning("Rate limit hit - will retry with backoff")
                elif "context_length" in error_msg.lower():
                    logger.error(f"Context length exceeded - too many frames: {error_msg}")
                
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    delay = self.retry_delay * (2 ** attempt)
                    logger.info(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"All GPT-4V API retries exhausted: {last_error}")
        
        return None
    
    def _parse_response(self, response: Any) -> Dict[str, Any]:
        """
        Parse and validate GPT-4V response
        
        Args:
            response: OpenAI API response
            
        Returns:
            Parsed analysis results
        """
        try:
            # Extract content from response
            content = response.choices[0].message.content
            
            # Parse JSON response
            try:
                parsed = json.loads(content)
                logger.info(f"Successfully parsed JSON response with keys: {list(parsed.keys()) if isinstance(parsed, dict) else 'non-dict response'}")
            except json.JSONDecodeError as e:
                logger.error(f"GPT-4V response is not valid JSON: {e}")
                logger.error(f"Raw content (first 500 chars): {content[:500]}")
                parsed = {"raw_response": content}
            
            # Add success flag and usage info
            result = {
                "success": True,
                "analysis": parsed,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse GPT-4V response: {e}")
            return {
                "success": False,
                "error": f"Response parsing failed: {e}",
                "raw_response": str(response) if response else None
            }
    
    async def analyze_single_frame(
        self,
        frame: Dict[str, Any],
        prompt: str
    ) -> Dict[str, Any]:
        """
        Analyze a single frame (for testing or specific analysis)
        
        Args:
            frame: Single frame data with base64 image
            prompt: Analysis prompt
            
        Returns:
            Analysis results for the frame
        """
        system_prompt = "You are analyzing a screenshot from a warehouse operator's workflow."
        return await self.analyze_frames([frame], system_prompt, prompt)
    
    def estimate_cost(self, frame_count: int) -> float:
        """
        Estimate cost for analyzing frames
        
        Args:
            frame_count: Number of frames to analyze
            
        Returns:
            Estimated cost in USD
        """
        return frame_count * self.cost_per_image
    
    def validate_configuration(self) -> Dict[str, Any]:
        """
        Validate client configuration and API connectivity
        
        Returns:
            Validation status and any issues
        """
        issues = []
        
        if not settings.OPENAI_API_KEY:
            issues.append("OpenAI API key not configured")
        
        if not self.client:
            issues.append("OpenAI client not initialized")
        
        return {
            "configured": len(issues) == 0,
            "model": self.model,
            "max_tokens": self.max_tokens,
            "cost_per_image": self.cost_per_image,
            "issues": issues
        }


# Singleton instance
_gpt4v_client: Optional[GPT4VClient] = None

def get_gpt4v_client() -> GPT4VClient:
    """Get singleton GPT-4V client instance"""
    global _gpt4v_client
    if _gpt4v_client is None:
        _gpt4v_client = GPT4VClient()
    return _gpt4v_client