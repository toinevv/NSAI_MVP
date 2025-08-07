"""
Analysis Orchestrator for NewSystem.AI
Coordinates the complete analysis pipeline from frame extraction to insights
Manages the flow: Recording → Frames → GPT-4V → Parsing → Storage
"""

import logging
from typing import Dict, Any, Optional
from uuid import UUID
from datetime import datetime, timezone
import asyncio

from app.services.analysis.frame_extractor import get_frame_extractor
from app.services.analysis.gpt4v_client import get_gpt4v_client
from app.services.analysis.prompts import get_analysis_prompt
from app.services.analysis.prompts_enhanced import get_enhanced_analysis_prompt
from app.services.analysis.prompts_natural import get_natural_prompt
from app.services.analysis.result_parser import get_result_parser
from app.core.config import settings

logger = logging.getLogger(__name__)


class AnalysisOrchestrator:
    """
    Orchestrates the complete workflow analysis pipeline
    Coordinates frame extraction, GPT-4V analysis, and result parsing
    """
    
    def __init__(self):
        self.frame_extractor = get_frame_extractor()
        self.gpt4v_client = get_gpt4v_client()
        self.result_parser = get_result_parser()
        
    async def analyze_recording(
        self,
        session_id: UUID,
        duration_seconds: int,
        analysis_type: str = "full"
    ) -> Dict[str, Any]:
        """
        Complete analysis pipeline for a recording
        
        Args:
            session_id: Recording session ID
            duration_seconds: Recording duration
            analysis_type: Type of analysis ("full", "quick", "email_wms")
            
        Returns:
            Complete analysis results
        """
        logger.info(f"Starting analysis pipeline for session {session_id}")
        
        # Track timing
        start_time = datetime.now(timezone.utc)
        pipeline_status = {
            "session_id": str(session_id),
            "started_at": start_time.isoformat(),
            "analysis_type": analysis_type,
            "steps_completed": []
        }
        
        try:
            # Step 1: Extract frames from recording
            logger.info(f"Step 1: Extracting frames from recording {session_id}")
            frame_result = await self.frame_extractor.extract_frames_from_recording(
                session_id,
                duration_seconds
            )
            
            if "error" in frame_result:
                logger.error(f"Frame extraction failed: {frame_result['error']}")
                return self._create_error_result(
                    session_id,
                    f"Frame extraction failed: {frame_result['error']}",
                    pipeline_status
                )
            
            frames = frame_result.get("frames", [])
            if not frames:
                logger.error("No frames extracted from recording")
                return self._create_error_result(
                    session_id,
                    "No frames could be extracted from the recording",
                    pipeline_status
                )
            
            pipeline_status["steps_completed"].append({
                "step": "frame_extraction",
                "frame_count": len(frames),
                "completed_at": datetime.now(timezone.utc).isoformat()
            })
            
            logger.info(f"Extracted {len(frames)} frames successfully")
            
            # Step 2: Analyze frames with GPT-4V
            logger.info(f"Step 2: Analyzing {len(frames)} frames with GPT-4V using {analysis_type} mode")
            
            # Get appropriate prompts for analysis type
            # Use natural prompts for better understanding
            if analysis_type in ["natural", "simple", "flow", "applications", "patterns"]:
                system_prompt, user_prompt = get_natural_prompt(analysis_type)
            elif analysis_type in ["discovery", "clustering", "team_comparison", "business_logic"]:
                system_prompt, user_prompt = get_enhanced_analysis_prompt(analysis_type)
            else:
                system_prompt, user_prompt = get_analysis_prompt(analysis_type)
            
            # Call GPT-4V
            gpt_result = await self.gpt4v_client.analyze_frames(
                frames,
                system_prompt,
                user_prompt
            )
            
            if not gpt_result.get("success"):
                logger.error(f"GPT-4V analysis failed: {gpt_result.get('error')}")
                return self._create_error_result(
                    session_id,
                    f"AI analysis failed: {gpt_result.get('error')}",
                    pipeline_status
                )
            
            pipeline_status["steps_completed"].append({
                "step": "gpt4v_analysis",
                "tokens_used": gpt_result.get("usage", {}).get("total_tokens", 0),
                "completed_at": datetime.now(timezone.utc).isoformat()
            })
            
            logger.info("GPT-4V analysis completed successfully")
            
            # Step 3: Parse and structure results
            logger.info("Step 3: Parsing analysis results")
            
            parsed_result = self.result_parser.parse_analysis_result(gpt_result)
            
            if not parsed_result.get("success"):
                logger.error(f"Result parsing failed: {parsed_result.get('error')}")
                return self._create_error_result(
                    session_id,
                    f"Result parsing failed: {parsed_result.get('error')}",
                    pipeline_status
                )
            
            pipeline_status["steps_completed"].append({
                "step": "result_parsing",
                "workflows_found": len(parsed_result.get("workflows", [])),
                "opportunities_found": len(parsed_result.get("automation_opportunities", [])),
                "completed_at": datetime.now(timezone.utc).isoformat()
            })
            
            # Step 4: Enhance with additional metadata
            logger.info("Step 4: Enhancing results with metadata")
            
            # Calculate total processing time
            end_time = datetime.now(timezone.utc)
            processing_time = (end_time - start_time).total_seconds()
            
            # Compile final result
            final_result = {
                "success": True,
                "session_id": str(session_id),
                "analysis_type": analysis_type,
                "processing_time_seconds": round(processing_time, 2),
                "frame_analysis": {
                    "frames_analyzed": len(frames),
                    "extraction_strategy": frame_result.get("extraction_strategy", {}),
                    "estimated_cost": frame_result.get("estimated_gpt4v_cost", 0)
                },
                "workflows": parsed_result.get("workflows", []),
                "automation_opportunities": parsed_result.get("automation_opportunities", []),
                "time_analysis": parsed_result.get("time_analysis", {}),
                "insights": parsed_result.get("insights", []),
                "summary": parsed_result.get("summary", {}),
                "confidence_score": parsed_result.get("confidence_score", 0),
                "pipeline_status": pipeline_status,
                "metadata": {
                    "gpt_model": settings.GPT4V_MODEL,
                    "analysis_timestamp": end_time.isoformat(),
                    "tokens_used": gpt_result.get("usage", {}).get("total_tokens", 0),
                    "processing_cost": self._calculate_total_cost(
                        len(frames),
                        gpt_result.get("usage", {}).get("total_tokens", 0)
                    )
                }
            }
            
            # Log success metrics
            logger.info(
                f"Analysis complete for session {session_id}: "
                f"{len(final_result['workflows'])} workflows, "
                f"{len(final_result['automation_opportunities'])} opportunities, "
                f"{processing_time:.1f}s processing time"
            )
            
            return final_result
            
        except Exception as e:
            logger.error(f"Analysis pipeline failed: {e}", exc_info=True)
            return self._create_error_result(
                session_id,
                f"Analysis pipeline error: {str(e)}",
                pipeline_status
            )
    
    async def quick_analysis(
        self,
        session_id: UUID,
        duration_seconds: int
    ) -> Dict[str, Any]:
        """
        Quick analysis with fewer frames and simpler prompts
        
        Args:
            session_id: Recording session ID
            duration_seconds: Recording duration
            
        Returns:
            Quick analysis results
        """
        # Use quick analysis type for faster, cheaper processing
        return await self.analyze_recording(session_id, duration_seconds, "quick")
    
    async def analyze_email_to_wms(
        self,
        session_id: UUID,
        duration_seconds: int
    ) -> Dict[str, Any]:
        """
        Specialized analysis for email to WMS workflows
        
        Args:
            session_id: Recording session ID
            duration_seconds: Recording duration
            
        Returns:
            Email to WMS focused analysis
        """
        # Use specialized email_wms analysis type
        return await self.analyze_recording(session_id, duration_seconds, "email_wms")
    
    def _calculate_total_cost(self, frame_count: int, tokens_used: int) -> float:
        """
        Calculate total cost of analysis
        
        Args:
            frame_count: Number of frames analyzed
            tokens_used: Total tokens used in GPT-4V
            
        Returns:
            Total cost in USD
        """
        # Frame cost (simplified - GPT-4V charges per image)
        frame_cost = frame_count * settings.COST_PER_GPT4V_REQUEST
        
        # Token cost (GPT-4V: ~$0.01 per 1K input tokens, $0.03 per 1K output tokens)
        # Simplified average
        token_cost = (tokens_used / 1000) * 0.02
        
        return round(frame_cost + token_cost, 4)
    
    def _create_error_result(
        self,
        session_id: UUID,
        error_message: str,
        pipeline_status: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create error result structure
        
        Args:
            session_id: Recording session ID
            error_message: Error description
            pipeline_status: Pipeline execution status
            
        Returns:
            Error result dict
        """
        return {
            "success": False,
            "session_id": str(session_id),
            "error": error_message,
            "workflows": [],
            "automation_opportunities": [],
            "summary": {
                "total_workflows_detected": 0,
                "total_opportunities": 0,
                "time_savings_daily_minutes": 0,
                "cost_savings_annual_usd": 0
            },
            "pipeline_status": pipeline_status,
            "metadata": {
                "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
                "processing_cost": 0
            }
        }
    
    async def validate_prerequisites(self, session_id: UUID) -> Dict[str, Any]:
        """
        Validate that all prerequisites are met for analysis
        
        Args:
            session_id: Recording session ID
            
        Returns:
            Validation status and any issues
        """
        issues = []
        
        # Check GPT-4V client configuration
        gpt_validation = self.gpt4v_client.validate_configuration()
        if not gpt_validation["configured"]:
            issues.extend(gpt_validation["issues"])
        
        # Check if recording exists (would need DB access in real implementation)
        # For now, just return the validation status
        
        return {
            "ready": len(issues) == 0,
            "issues": issues,
            "gpt4v_configured": gpt_validation["configured"],
            "estimated_cost": self.gpt4v_client.estimate_cost(10)  # Assume 10 frames
        }


# Singleton instance
_orchestrator: Optional[AnalysisOrchestrator] = None

def get_orchestrator() -> AnalysisOrchestrator:
    """Get singleton orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AnalysisOrchestrator()
    return _orchestrator