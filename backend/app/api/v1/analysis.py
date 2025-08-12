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
    frame_extraction_settings: Optional[Dict[str, Any]] = None  # Custom frame extraction settings

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
    logger.info(f"🎬 ANALYSIS START: Starting analysis for recording {recording_id}")
    logger.info(f"📋 REQUEST DATA: analysis_type={request.analysis_type}, frame_settings={request.frame_extraction_settings}")
    
    try:
        # Validate recording exists and is ready
        logger.info(f"🔍 DATABASE CHECK: Querying recording {recording_id}")
        recording = db.query(RecordingSession).filter(
            RecordingSession.id == recording_id
        ).first()
        
        if not recording:
            logger.error(f"❌ RECORDING NOT FOUND: {recording_id}")
            raise HTTPException(status_code=404, detail=f"Recording {recording_id} not found")
        
        logger.info(f"✅ RECORDING FOUND: id={recording.id}, status={recording.status}, duration={recording.duration_seconds}s")
        
        if recording.status != "completed":
            logger.error(f"❌ RECORDING NOT READY: status={recording.status}")
            raise HTTPException(
                status_code=400, 
                detail=f"Recording is not ready for analysis. Status: {recording.status}"
            )
        
        # Check if analysis already exists
        logger.info(f"🔍 ANALYSIS CHECK: Looking for existing analysis for recording {recording_id}")
        existing_analysis = db.query(AnalysisResult).filter(
            AnalysisResult.session_id == recording_id
        ).first()
        
        if existing_analysis:
            logger.info(f"📊 EXISTING ANALYSIS: Found id={existing_analysis.id}, status={existing_analysis.status}")
            if existing_analysis.status in ["processing", "completed"]:
                logger.info(f"🔄 RETURNING EXISTING: Analysis already in progress or complete")
                return AnalysisResponse(
                    id=str(existing_analysis.id),
                    status=existing_analysis.status,
                    message="Analysis already exists",
                    confidence_score=float(existing_analysis.confidence_score) if existing_analysis.confidence_score else None,
                    processing_cost=float(existing_analysis.analysis_cost) if existing_analysis.analysis_cost else None
                )
        else:
            logger.info(f"🆕 NEW ANALYSIS: No existing analysis found, will create new one")
        
        # Create or update analysis record
        if existing_analysis:
            logger.info(f"🔄 UPDATING EXISTING: Resetting existing analysis to processing")
            analysis = existing_analysis
            analysis.status = "processing"
            analysis.processing_started_at = datetime.now(timezone.utc)
        else:
            analysis_id = uuid4()
            logger.info(f"🆕 CREATING NEW: Creating new analysis record with id={analysis_id}")
            analysis = AnalysisResult(
                id=analysis_id,
                session_id=UUID(recording_id),
                status="processing",
                gpt_version=settings.GPT4V_MODEL,
                processing_started_at=datetime.now(timezone.utc)
            )
            db.add(analysis)
        
        logger.info(f"💾 DATABASE COMMIT: Committing analysis record to database")
        db.commit()
        logger.info(f"✅ ANALYSIS CREATED: Analysis {analysis.id} created with status=processing")
        
        # Start full analysis pipeline with GPT-4V
        logger.info(f"🚀 BACKGROUND TASK: Starting background analysis pipeline")
        logger.info(f"📊 TASK PARAMS: analysis_id={analysis.id}, recording_id={recording_id}, duration={recording.duration_seconds}s")
        
        background_tasks.add_task(
            run_full_analysis_pipeline,
            str(analysis.id),
            str(recording_id),
            recording.duration_seconds or 0,
            request.frame_extraction_settings
        )
        logger.info(f"✅ TASK QUEUED: Background analysis task added to queue")
        
        # Get orchestrator to estimate cost
        try:
            logger.info(f"💰 COST ESTIMATION: Getting orchestrator for cost estimate")
            orchestrator = get_orchestrator()
            estimated_cost = orchestrator.gpt4v_client.estimate_cost(10) if orchestrator.gpt4v_client else 0.20
            logger.info(f"💰 ESTIMATED COST: ${estimated_cost}")
        except Exception as e:
            logger.warning(f"⚠️ COST ESTIMATION FAILED: {e}")
            estimated_cost = 0.20  # Fallback estimate
        
        logger.info(f"🎯 SUCCESS: Analysis {analysis.id} initiated successfully")
        return AnalysisResponse(
            id=str(analysis.id),
            status="processing",
            message="Full GPT-4V analysis started - identifying automation opportunities",
            processing_cost=estimated_cost
        )
        
    except HTTPException as he:
        logger.error(f"🚫 HTTP EXCEPTION: {he.status_code} - {he.detail}")
        raise
    except Exception as e:
        logger.error(f"💥 UNEXPECTED ERROR: Failed to start analysis for recording {recording_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

async def run_full_analysis_pipeline(
    analysis_id: str,
    recording_id: str,
    duration_seconds: int,
    frame_extraction_settings: Optional[Dict[str, Any]] = None
):
    """
    Background task to run complete analysis pipeline
    Phase 2A Day 2-3: Full GPT-4V integration
    """
    logger.info(f"🎯 PIPELINE START: Beginning full analysis pipeline")
    logger.info(f"📋 PIPELINE PARAMS: analysis_id={analysis_id}, recording_id={recording_id}, duration={duration_seconds}s")
    logger.info(f"⚙️ FRAME SETTINGS: {frame_extraction_settings}")
    
    # Import here to avoid circular imports
    from app.core.database import get_sync_db
    
    # Get database session for background task
    logger.info(f"🗄️ DATABASE: Getting sync database session for background task")
    db = get_sync_db()
    
    try:
        # Get orchestrator
        try:
            logger.info(f"🎭 ORCHESTRATOR: Initializing analysis orchestrator")
            orchestrator = get_orchestrator()
            logger.info(f"✅ ORCHESTRATOR: Successfully initialized")
        except Exception as e:
            logger.error(f"💥 ORCHESTRATOR FAILED: Failed to initialize orchestrator: {e}", exc_info=True)
            # Update analysis as failed and return
            logger.info(f"❌ MARKING FAILED: Updating analysis {analysis_id} as failed due to orchestrator error")
            analysis = db.query(AnalysisResult).filter(
                AnalysisResult.id == analysis_id
            ).first()
            if analysis:
                analysis.status = "failed"
                analysis.error_message = f"Configuration error: {str(e)}"
                analysis.processing_completed_at = datetime.now(timezone.utc)
                db.commit()
                logger.info(f"💾 FAILED SAVED: Analysis marked as failed in database")
            return
        
        # Run complete analysis pipeline using natural format for frontend compatibility
        logger.info(f"🤖 RUNNING ANALYSIS: Starting orchestrator.analyze_recording")
        logger.info(f"📊 ANALYSIS PARAMS: recording_id={recording_id}, duration={duration_seconds}s, type=natural")
        
        result = await orchestrator.analyze_recording(
            UUID(recording_id),
            duration_seconds,
            analysis_type="natural",
            frame_extraction_settings=frame_extraction_settings
        )
        
        logger.info(f"🎯 ANALYSIS COMPLETE: Orchestrator returned result")
        logger.info(f"✅ SUCCESS STATUS: result.success = {result.get('success', 'UNKNOWN')}")
        if result.get("success"):
            logger.info(f"📈 RESULT SUMMARY: workflows={len(result.get('workflows', []))}, opportunities={len(result.get('automation_opportunities', []))}")
        else:
            logger.error(f"❌ ANALYSIS ERROR: {result.get('error', 'Unknown error')}")
        
        # Update analysis record with results
        logger.info(f"💾 DATABASE UPDATE: Retrieving analysis {analysis_id} for result storage")
        analysis = db.query(AnalysisResult).filter(
            AnalysisResult.id == analysis_id
        ).first()
        
        if analysis:
            logger.info(f"📊 FOUND ANALYSIS: Retrieved analysis record {analysis.id}")
            if result.get("success"):
                logger.info(f"✅ SUCCESS RESULT: Updating analysis as completed")
                analysis.status = "completed"
                
                # Store frame analysis data
                frames_analyzed = result.get("frame_analysis", {}).get("frames_analyzed", 0)
                analysis.frames_analyzed = frames_analyzed
                logger.info(f"🎬 FRAMES: {frames_analyzed} frames analyzed")
                
                # Store complete structured insights
                logger.info(f"💾 STORING INSIGHTS: Saving structured_insights to database")
                analysis.structured_insights = result
                
                # Store raw GPT-4V response for debugging and frontend raw tab
                raw_gpt_response = result.get("raw_gpt_response")
                if raw_gpt_response:
                    logger.info(f"🤖 RAW RESPONSE: Storing raw GPT-4V response (size: {len(str(raw_gpt_response))} chars)")
                    analysis.raw_gpt_response = raw_gpt_response
                else:
                    logger.warning(f"⚠️ NO RAW RESPONSE: No raw_gpt_response found in result")
                
                # Store confidence and cost
                confidence_score = result.get("confidence_score", 0)
                analysis.confidence_score = confidence_score
                processing_cost = result.get("metadata", {}).get("processing_cost", 0)
                analysis.analysis_cost = processing_cost
                logger.info(f"📊 METRICS: confidence={confidence_score}, cost=${processing_cost}")
                
                # Extract summary metrics
                summary = result.get("summary", {})
                if summary:
                    opportunities_count = summary.get("total_opportunities", 0)
                    time_savings = summary.get("time_savings_weekly_hours", 0)
                    cost_savings = summary.get("cost_savings_annual_usd", 0)
                    
                    analysis.automation_opportunities_count = opportunities_count
                    analysis.time_savings_hours_weekly = time_savings
                    analysis.cost_savings_annual = cost_savings
                    logger.info(f"💰 SUMMARY: {opportunities_count} opportunities, {time_savings}h/week savings, ${cost_savings}/year")
                else:
                    logger.warning(f"⚠️ NO SUMMARY: No summary data found in result")
                
                # CRITICAL FIX: Create individual AutomationOpportunity records
                logger.info(f"🎯 CREATING AUTOMATION OPPORTUNITY RECORDS")
                automation_opportunities = result.get("automation_opportunities", [])
                
                if isinstance(automation_opportunities, list) and automation_opportunities:
                    logger.info(f"📝 Found {len(automation_opportunities)} automation opportunities to create")
                    
                    from app.models.database import AutomationOpportunity
                    
                    created_opportunities = 0
                    for i, opportunity_data in enumerate(automation_opportunities):
                        try:
                            # Extract opportunity details
                            workflow_type = opportunity_data.get("workflow_type", "Unknown")
                            description = opportunity_data.get("description", "")
                            
                            # Convert time values to standard formats
                            time_per_occurrence_minutes = opportunity_data.get("time_per_occurrence_minutes", 0)
                            time_per_occurrence_seconds = int(time_per_occurrence_minutes * 60)
                            
                            frequency_daily = opportunity_data.get("frequency_daily", 1)
                            time_saved_weekly_hours = opportunity_data.get("time_saved_weekly_hours", 0)
                            cost_saved_annually = opportunity_data.get("cost_saved_annually", 0)
                            
                            # Create AutomationOpportunity record
                            opportunity = AutomationOpportunity(
                                analysis_id=analysis.id,
                                session_id=analysis.session_id,
                                opportunity_type=workflow_type,
                                title=f"{workflow_type} Automation",
                                description=description,
                                workflow_steps=[],  # TODO: Extract workflow steps if available
                                current_time_per_occurrence_seconds=time_per_occurrence_seconds,
                                occurrences_per_day=frequency_daily,
                                automation_complexity=opportunity_data.get("implementation_complexity", "medium"),
                                implementation_effort_hours=24,  # Default estimate
                                estimated_cost_savings_monthly=round(cost_saved_annually / 12, 2),
                                estimated_implementation_cost=2000.00,  # Default estimate
                                roi_percentage=round((cost_saved_annually / 2000.00) * 100, 2) if cost_saved_annually > 0 else 0,
                                payback_period_days=int((2000.00 / (cost_saved_annually / 365)) if cost_saved_annually > 0 else 365),
                                confidence_score=confidence_score,
                                priority=opportunity_data.get("priority_score", "medium"),
                                record_metadata=opportunity_data  # Store full opportunity data
                            )
                            
                            db.add(opportunity)
                            created_opportunities += 1
                            logger.info(f"✅ OPPORTUNITY #{i+1}: {workflow_type} - ${cost_saved_annually}/year savings")
                            
                        except Exception as e:
                            logger.error(f"❌ OPPORTUNITY #{i+1} FAILED: {e}")
                            continue
                    
                    logger.info(f"🎯 CREATED {created_opportunities} automation opportunity records")
                    
                else:
                    logger.warning(f"⚠️ NO AUTOMATION OPPORTUNITIES: Found {type(automation_opportunities)} with {len(automation_opportunities) if isinstance(automation_opportunities, list) else 'N/A'} items")
            else:
                logger.error(f"❌ FAILED RESULT: Analysis failed, updating status")
                analysis.status = "failed"
                error_message = result.get("error", "Analysis failed")
                analysis.error_message = error_message
                logger.error(f"💥 ERROR MESSAGE: {error_message}")
            
            # Set completion time and calculate processing duration
            analysis.processing_completed_at = datetime.now(timezone.utc)
            if analysis.processing_started_at:
                # Handle SQLite timezone-naive datetimes
                start_time = analysis.processing_started_at
                if start_time.tzinfo is None:
                    start_time = start_time.replace(tzinfo=timezone.utc)
                delta = analysis.processing_completed_at - start_time
                processing_time = int(delta.total_seconds())
                analysis.processing_time_seconds = processing_time
                logger.info(f"⏱️ PROCESSING TIME: {processing_time} seconds")
            
            # CRITICAL: Commit to database
            logger.info(f"💾 FINAL COMMIT: Committing analysis results to database")
            db.commit()
            logger.info(f"✅ PIPELINE COMPLETE: Analysis {analysis_id} completed with status: {analysis.status}")
        else:
            logger.error(f"💥 ANALYSIS RECORD MISSING: Analysis record {analysis_id} not found in database")
            
    except Exception as e:
        logger.error(f"💥 PIPELINE EXCEPTION: Analysis pipeline failed with unexpected error: {e}", exc_info=True)
        
        # Update analysis as failed
        logger.info(f"❌ EXCEPTION CLEANUP: Marking analysis {analysis_id} as failed due to exception")
        analysis = db.query(AnalysisResult).filter(
            AnalysisResult.id == analysis_id
        ).first()
        
        if analysis:
            analysis.status = "failed"
            error_message = str(e)
            analysis.error_message = error_message
            analysis.processing_completed_at = datetime.now(timezone.utc)
            logger.error(f"💾 EXCEPTION ERROR: Storing error message: {error_message}")
            
            # Handle SQLite timezone issues for processing time calculation
            if analysis.processing_started_at:
                start_time = analysis.processing_started_at
                if start_time.tzinfo is None:
                    start_time = start_time.replace(tzinfo=timezone.utc)
                delta = analysis.processing_completed_at - start_time
                processing_time = int(delta.total_seconds())
                analysis.processing_time_seconds = processing_time
                logger.info(f"⏱️ EXCEPTION TIME: Processing time before failure: {processing_time} seconds")
            
            logger.info(f"💾 EXCEPTION COMMIT: Committing failed analysis to database")
            db.commit()
            logger.info(f"✅ EXCEPTION HANDLED: Analysis {analysis_id} marked as failed")
        else:
            logger.error(f"💥 EXCEPTION + MISSING RECORD: Could not find analysis {analysis_id} to mark as failed")
    
    finally:
        logger.info(f"🔚 PIPELINE CLEANUP: Closing database connection")
        db.close()
        logger.info(f"🏁 PIPELINE END: Background analysis pipeline completed for {analysis_id}")

@router.get("/{analysis_id}/status")
async def get_analysis_status(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """
    Get analysis processing status
    Returns real-time status of GPT-4V analysis
    """
    logger.info(f"📊 STATUS CHECK: Checking status for analysis {analysis_id}")
    
    analysis = db.query(AnalysisResult).filter(
        AnalysisResult.id == analysis_id
    ).first()
    
    if not analysis:
        logger.error(f"❌ STATUS NOT FOUND: Analysis {analysis_id} not found in database")
        raise HTTPException(status_code=404, detail=f"Analysis {analysis_id} not found")
    
    logger.info(f"✅ STATUS FOUND: Analysis {analysis_id} has status: {analysis.status}")
    
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
    logger.info(f"📋 RESULTS REQUEST: Getting results for analysis {analysis_id}")
    
    analysis = db.query(AnalysisResult).filter(
        AnalysisResult.id == analysis_id
    ).first()
    
    if not analysis:
        logger.error(f"❌ RESULTS NOT FOUND: Analysis {analysis_id} not found in database")
        raise HTTPException(status_code=404, detail=f"Analysis {analysis_id} not found")
    
    logger.info(f"📊 ANALYSIS STATUS: Analysis {analysis_id} has status: {analysis.status}")
    
    if analysis.status != "completed":
        logger.info(f"⏳ NOT READY: Analysis not completed yet, returning status message")
        return {
            "analysis_id": str(analysis.id),
            "status": analysis.status,
            "message": f"Analysis is {analysis.status}. Results will be available when complete.",
            "results": None
        }
    
    # Extract structured insights
    insights = analysis.structured_insights or {}
    logger.info(f"💾 EXTRACTING INSIGHTS: Found {len(insights)} insight keys in structured_insights")
    
    # Log what data we have
    workflows = insights.get("workflows", [])
    opportunities = insights.get("automation_opportunities", [])
    summary = insights.get("summary", {})
    
    logger.info(f"📈 RESULTS CONTENT: {len(workflows)} workflows, {len(opportunities)} opportunities")
    logger.info(f"📊 SUMMARY CONTENT: {len(summary)} summary keys")
    
    result_data = {
        "analysis_id": str(analysis.id),
        "status": "completed",
        "message": "Analysis complete - automation opportunities identified",
        "results": {
            "workflows": workflows,
            "automation_opportunities": opportunities,
            "time_analysis": insights.get("time_analysis", {}),
            "insights": insights.get("insights", []),
            "summary": summary,
            "confidence_score": float(analysis.confidence_score) if analysis.confidence_score else 0,
            "processing_time_seconds": analysis.processing_time_seconds,
            "analysis_cost": float(analysis.analysis_cost) if analysis.analysis_cost else 0
        }
    }
    
    logger.info(f"✅ RESULTS SUCCESS: Returning complete analysis results for {analysis_id}")
    return result_data

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