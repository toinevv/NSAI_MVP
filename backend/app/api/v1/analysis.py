"""
Analysis pipeline endpoints for NewSystem.AI
Orchestrates GPT-4V analysis of recorded workflows
Focus: Email → WMS pattern detection for logistics automation
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from datetime import datetime, timezone
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.models.database import RecordingSession, AnalysisResult
from app.services.analysis import get_frame_extractor, get_orchestrator
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

class AnalysisResponse(BaseModel):
    id: str
    status: str
    message: str
    confidence_score: Optional[float] = None
    processing_cost: Optional[float] = None

class FrameExtractionResponse(BaseModel):
    session_id: str
    frame_count: int
    estimated_cost: float
    extraction_strategy: Dict[str, Any]
    
class StartAnalysisRequest(BaseModel):
    analysis_type: str = "full"  # Options: "full", "quick", "email_wms"

@router.post("/{recording_id}/start")
async def start_analysis(
    recording_id: str,
    request: StartAnalysisRequest = StartAnalysisRequest(),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """
    Start GPT-4V analysis of recorded workflow
    Phase 2A: Frame extraction implementation
    """
    try:
        # Validate recording exists and is ready
        recording = db.query(RecordingSession).filter(
            RecordingSession.id == recording_id
        ).first()
        
        if not recording:
            raise HTTPException(status_code=404, detail=f"Recording {recording_id} not found")
        
        if recording.status != "completed":
            raise HTTPException(
                status_code=400, 
                detail=f"Recording is not ready for analysis. Status: {recording.status}"
            )
        
        # Check if analysis already exists
        existing_analysis = db.query(AnalysisResult).filter(
            AnalysisResult.session_id == recording_id
        ).first()
        
        if existing_analysis and existing_analysis.status in ["processing", "completed"]:
            return AnalysisResponse(
                id=str(existing_analysis.id),
                status=existing_analysis.status,
                message="Analysis already exists",
                confidence_score=float(existing_analysis.confidence_score) if existing_analysis.confidence_score else None,
                processing_cost=float(existing_analysis.analysis_cost) if existing_analysis.analysis_cost else None
            )
        
        # Create or update analysis record
        if existing_analysis:
            analysis = existing_analysis
            analysis.status = "processing"
            analysis.processing_started_at = datetime.now(timezone.utc)
        else:
            analysis = AnalysisResult(
                id=uuid4(),
                session_id=UUID(recording_id),
                status="processing",
                gpt_version=settings.GPT4V_MODEL,
                processing_started_at=datetime.now(timezone.utc)
            )
            db.add(analysis)
        
        db.commit()
        
        # Start full analysis pipeline with GPT-4V
        background_tasks.add_task(
            run_full_analysis_pipeline,
            str(analysis.id),
            str(recording_id),
            recording.duration_seconds or 0
        )
        
        # Get orchestrator to estimate cost
        try:
            orchestrator = get_orchestrator()
            estimated_cost = orchestrator.gpt4v_client.estimate_cost(10) if orchestrator.gpt4v_client else 0.20
        except Exception as e:
            logger.warning(f"Could not initialize orchestrator for cost estimation: {e}")
            estimated_cost = 0.20  # Fallback estimate
        
        return AnalysisResponse(
            id=str(analysis.id),
            status="processing",
            message="Full GPT-4V analysis started - identifying automation opportunities",
            processing_cost=estimated_cost
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start analysis for recording {recording_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def run_full_analysis_pipeline(
    analysis_id: str,
    recording_id: str,
    duration_seconds: int
):
    """
    Background task to run complete analysis pipeline
    Phase 2A Day 2-3: Full GPT-4V integration
    """
    logger.info(f"Starting full analysis pipeline for recording {recording_id}")
    
    # Import here to avoid circular imports
    from app.core.database import get_sync_db
    
    # Get database session for background task
    db = get_sync_db()
    
    try:
        # Get orchestrator
        try:
            orchestrator = get_orchestrator()
        except Exception as e:
            logger.error(f"Failed to initialize orchestrator: {e}")
            # Update analysis as failed and return
            analysis = db.query(AnalysisResult).filter(
                AnalysisResult.id == analysis_id
            ).first()
            if analysis:
                analysis.status = "failed"
                analysis.error_message = f"Configuration error: {str(e)}"
                analysis.processing_completed_at = datetime.now(timezone.utc)
                db.commit()
            return
        
        # Run complete analysis pipeline
        result = await orchestrator.analyze_recording(
            UUID(recording_id),
            duration_seconds,
            analysis_type="full"
        )
        
        # Update analysis record with results
        analysis = db.query(AnalysisResult).filter(
            AnalysisResult.id == analysis_id
        ).first()
        
        if analysis:
            if result.get("success"):
                analysis.status = "completed"
                analysis.frames_analyzed = result.get("frame_analysis", {}).get("frames_analyzed", 0)
                analysis.structured_insights = result
                analysis.confidence_score = result.get("confidence_score", 0)
                analysis.analysis_cost = result.get("metadata", {}).get("processing_cost", 0)
                
                # Extract summary metrics
                summary = result.get("summary", {})
                if summary:
                    analysis.automation_opportunities_count = summary.get("total_opportunities", 0)
                    analysis.time_savings_hours_weekly = summary.get("time_savings_weekly_hours", 0)
                    analysis.cost_savings_annual = summary.get("cost_savings_annual_usd", 0)
            else:
                analysis.status = "failed"
                analysis.error_message = result.get("error", "Analysis failed")
            
            analysis.processing_completed_at = datetime.now(timezone.utc)
            if analysis.processing_started_at:
                # Handle SQLite timezone-naive datetimes
                start_time = analysis.processing_started_at
                if start_time.tzinfo is None:
                    start_time = start_time.replace(tzinfo=timezone.utc)
                delta = analysis.processing_completed_at - start_time
                analysis.processing_time_seconds = int(delta.total_seconds())
            
            db.commit()
            logger.info(f"Analysis {analysis_id} completed with status: {analysis.status}")
        else:
            logger.error(f"Analysis record {analysis_id} not found")
            
    except Exception as e:
        logger.error(f"Analysis pipeline failed: {e}", exc_info=True)
        
        # Update analysis as failed
        analysis = db.query(AnalysisResult).filter(
            AnalysisResult.id == analysis_id
        ).first()
        
        if analysis:
            analysis.status = "failed"
            analysis.error_message = str(e)
            analysis.processing_completed_at = datetime.now(timezone.utc)
            
            # Handle SQLite timezone issues for processing time calculation
            if analysis.processing_started_at:
                start_time = analysis.processing_started_at
                if start_time.tzinfo is None:
                    start_time = start_time.replace(tzinfo=timezone.utc)
                delta = analysis.processing_completed_at - start_time
                analysis.processing_time_seconds = int(delta.total_seconds())
            
            db.commit()
    
    finally:
        db.close()

@router.get("/{analysis_id}/status")
async def get_analysis_status(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """
    Get analysis processing status
    Returns real-time status of GPT-4V analysis
    """
    analysis = db.query(AnalysisResult).filter(
        AnalysisResult.id == analysis_id
    ).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail=f"Analysis {analysis_id} not found")
    
    message_map = {
        "processing": "GPT-4V is analyzing your workflow for automation opportunities...",
        "completed": "Analysis complete - automation opportunities identified!",
        "failed": f"Analysis failed: {analysis.error_message or 'Unknown error'}",
        "frames_extracted": "Frames extracted, starting GPT-4V analysis..."
    }
    
    return AnalysisResponse(
        id=str(analysis.id),
        status=analysis.status,
        message=message_map.get(analysis.status, "Processing..."),
        confidence_score=float(analysis.confidence_score) if analysis.confidence_score else None,
        processing_cost=float(analysis.analysis_cost) if analysis.analysis_cost else None
    )

@router.get("/{analysis_id}/results")
async def get_analysis_results(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """
    Get completed analysis results
    Returns structured workflow insights and automation opportunities
    """
    analysis = db.query(AnalysisResult).filter(
        AnalysisResult.id == analysis_id
    ).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail=f"Analysis {analysis_id} not found")
    
    if analysis.status != "completed":
        return {
            "analysis_id": str(analysis.id),
            "status": analysis.status,
            "message": f"Analysis is {analysis.status}. Results will be available when complete.",
            "results": None
        }
    
    # Extract structured insights
    insights = analysis.structured_insights or {}
    
    return {
        "analysis_id": str(analysis.id),
        "status": "completed",
        "message": "Analysis complete - automation opportunities identified",
        "results": {
            "workflows": insights.get("workflows", []),
            "automation_opportunities": insights.get("automation_opportunities", []),
            "time_analysis": insights.get("time_analysis", {}),
            "insights": insights.get("insights", []),
            "summary": insights.get("summary", {}),
            "confidence_score": float(analysis.confidence_score) if analysis.confidence_score else 0,
            "processing_time_seconds": analysis.processing_time_seconds,
            "analysis_cost": float(analysis.analysis_cost) if analysis.analysis_cost else 0
        }
    }

@router.post("/{analysis_id}/retry")
async def retry_analysis(analysis_id: str):
    """
    Retry failed analysis
    Week 2 Priority: Error handling and retry logic
    """
    # TODO: Implement analysis retry
    return AnalysisResponse(
        id=analysis_id,
        status="retrying",
        message="Analysis retry initiated - Week 2 implementation"
    )