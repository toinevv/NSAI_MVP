"""
Analysis pipeline endpoints for NewSystem.AI
Orchestrates GPT-4V analysis of recorded workflows
Native Supabase implementation with multi-tenant support via RLS
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from datetime import datetime, timezone
import logging

from app.api.v1.auth import get_current_user_from_token
from app.services.analysis import get_frame_extractor, get_orchestrator
from app.services.supabase_client import get_supabase_client
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
    analysis_type: str = "full"  # Options: "full", "quick", "focused", "discovery", "natural"
    frame_extraction_settings: Optional[Dict[str, Any]] = None

# ============================================
# ANALYSIS ENDPOINTS
# ============================================

@router.post("/{recording_id}/start")
async def start_analysis(
    recording_id: str,
    request: StartAnalysisRequest = StartAnalysisRequest(),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
):
    """
    Start GPT-4V analysis of recorded workflow
    Native Supabase implementation with organization context
    """
    logger.info(f"🎬 ANALYSIS START: Starting analysis for recording {recording_id}")
    logger.info(f"📋 REQUEST DATA: analysis_type={request.analysis_type}, frame_settings={request.frame_extraction_settings}")
    logger.info(f"👤 USER CONTEXT: user_id={current_user['id']}, org_id={current_user['organization_id']}")
    
    try:
        supabase = get_supabase_client()
        
        # Validate recording exists and user has access (RLS handles filtering)
        logger.info(f"🔍 DATABASE CHECK: Querying recording {recording_id}")
        recording_result = supabase.client.table('recording_sessions').select("*").eq('id', recording_id).single().execute()
        
        if not recording_result.data:
            logger.error(f"❌ RECORDING NOT FOUND: {recording_id}")
            raise HTTPException(status_code=404, detail=f"Recording {recording_id} not found")
        
        recording = recording_result.data
        logger.info(f"✅ RECORDING FOUND: id={recording['id']}, status={recording['status']}, duration={recording.get('duration_seconds', 0)}s")
        
        if recording["status"] != "completed":
            logger.error(f"❌ RECORDING NOT READY: status={recording['status']}")
            raise HTTPException(
                status_code=400, 
                detail=f"Recording is not ready for analysis. Status: {recording['status']}"
            )
        
        # Check if analysis already exists
        logger.info(f"🔍 ANALYSIS CHECK: Looking for existing analysis for recording {recording_id}")
        existing_analysis_result = supabase.client.table('analysis_results').select("*").eq('session_id', recording_id).execute()
        
        existing_analysis = existing_analysis_result.data[0] if existing_analysis_result.data else None
        
        if existing_analysis:
            logger.info(f"📊 EXISTING ANALYSIS: Found id={existing_analysis['id']}, status={existing_analysis['status']}")
            if existing_analysis["status"] in ["processing", "completed"]:
                logger.info(f"🔄 RETURNING EXISTING: Analysis already in progress or complete")
                return AnalysisResponse(
                    id=str(existing_analysis["id"]),
                    status=existing_analysis["status"],
                    message="Analysis already exists",
                    confidence_score=float(existing_analysis["confidence_score"]) if existing_analysis.get("confidence_score") else None,
                    processing_cost=float(existing_analysis["analysis_cost"]) if existing_analysis.get("analysis_cost") else None
                )
        else:
            logger.info(f"🆕 NEW ANALYSIS: No existing analysis found, will create new one")
        
        # Create or update analysis record
        analysis_id = str(uuid4())
        current_time = datetime.now(timezone.utc).isoformat()
        
        if existing_analysis:
            logger.info(f"🔄 UPDATING EXISTING: Resetting existing analysis to processing")
            update_data = {
                "status": "processing",
                "processing_started_at": current_time,
                "processing_completed_at": None,
                "error_message": None,
                "updated_at": current_time
            }
            analysis_result = supabase.client.table('analysis_results').update(update_data).eq('id', existing_analysis['id']).execute()
            analysis_id = existing_analysis['id']
            analysis = analysis_result.data[0] if analysis_result.data else existing_analysis
        else:
            logger.info(f"🆕 CREATING NEW: Creating new analysis record with id={analysis_id}")
            analysis_data = {
                "id": analysis_id,
                "session_id": recording_id,
                "organization_id": current_user["organization_id"],
                "status": "processing",
                "gpt_version": settings.GPT4V_MODEL,
                "processing_started_at": current_time,
                "frames_analyzed": 0,
                "analysis_cost": 0.00,
                "confidence_score": 0.00,
                "automation_opportunities_count": 0,
                "time_savings_hours_weekly": 0.00,
                "cost_savings_annual": 0.00,
                "structured_insights": {},
                "created_at": current_time,
                "updated_at": current_time
            }
            analysis_result = supabase.client.table('analysis_results').insert(analysis_data).execute()
            analysis = analysis_result.data[0] if analysis_result.data else analysis_data
        
        logger.info(f"✅ ANALYSIS CREATED: Analysis {analysis_id} created with status=processing")
        
        # Start full analysis pipeline with GPT-4V
        logger.info(f"🚀 BACKGROUND TASK: Starting background analysis pipeline")
        logger.info(f"📊 TASK PARAMS: analysis_id={analysis_id}, recording_id={recording_id}, duration={recording.get('duration_seconds', 0)}s")
        
        background_tasks.add_task(
            run_full_analysis_pipeline,
            analysis_id,
            recording_id,
            recording.get("duration_seconds", 0),
            current_user["organization_id"],
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
        
        logger.info(f"🎯 SUCCESS: Analysis {analysis_id} initiated successfully")
        return AnalysisResponse(
            id=analysis_id,
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
    organization_id: str,
    frame_extraction_settings: Optional[Dict[str, Any]] = None
):
    """
    Background task to run complete analysis pipeline
    Native Supabase implementation with organization context
    """
    logger.info(f"🎯 PIPELINE START: Beginning full analysis pipeline")
    logger.info(f"📋 PIPELINE PARAMS: analysis_id={analysis_id}, recording_id={recording_id}, duration={duration_seconds}s")
    logger.info(f"🏢 ORGANIZATION: organization_id={organization_id}")
    logger.info(f"⚙️ FRAME SETTINGS: {frame_extraction_settings}")
    
    supabase = get_supabase_client()
    
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
            update_data = {
                "status": "failed",
                "error_message": f"Configuration error: {str(e)}",
                "processing_completed_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            supabase.client.table('analysis_results').update(update_data).eq('id', analysis_id).execute()
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
        logger.info(f"💾 DATABASE UPDATE: Updating analysis {analysis_id} with results")
        
        current_time = datetime.now(timezone.utc).isoformat()
        
        if result.get("success"):
            logger.info(f"✅ SUCCESS RESULT: Updating analysis as completed")
            
            # Prepare update data
            frames_analyzed = result.get("frame_analysis", {}).get("frames_analyzed", 0)
            logger.info(f"🎬 FRAMES: {frames_analyzed} frames analyzed")
            
            # Store complete structured insights
            logger.info(f"💾 STORING INSIGHTS: Saving structured_insights to database")
            structured_insights = result
            
            # Store raw GPT-4V response for debugging and frontend raw tab
            raw_gpt_response = result.get("raw_gpt_response")
            if raw_gpt_response:
                logger.info(f"🤖 RAW RESPONSE: Storing raw GPT-4V response (size: {len(str(raw_gpt_response))} chars)")
            else:
                logger.warning(f"⚠️ NO RAW RESPONSE: No raw_gpt_response found in result")
            
            # Extract summary metrics
            summary = result.get("summary", {})
            opportunities_count = 0
            time_savings = 0.0
            cost_savings = 0.0
            
            if summary:
                opportunities_count = summary.get("total_opportunities", 0)
                time_savings = summary.get("time_savings_weekly_hours", 0)
                cost_savings = summary.get("cost_savings_annual_usd", 0)
                logger.info(f"💰 SUMMARY: {opportunities_count} opportunities, {time_savings}h/week savings, ${cost_savings}/year")
            else:
                logger.warning(f"⚠️ NO SUMMARY: No summary data found in result")
            
            # Store confidence and cost
            confidence_score = result.get("confidence_score", 0)
            processing_cost = result.get("metadata", {}).get("processing_cost", 0)
            logger.info(f"📊 METRICS: confidence={confidence_score}, cost=${processing_cost}")
            
            update_data = {
                "status": "completed",
                "frames_analyzed": frames_analyzed,
                "structured_insights": structured_insights,
                "raw_gpt_response": raw_gpt_response,
                "confidence_score": confidence_score,
                "analysis_cost": processing_cost,
                "automation_opportunities_count": opportunities_count,
                "time_savings_hours_weekly": time_savings,
                "cost_savings_annual": cost_savings,
                "processing_completed_at": current_time,
                "updated_at": current_time
            }
            
            # Calculate processing time
            analysis_result = supabase.client.table('analysis_results').select('processing_started_at').eq('id', analysis_id).single().execute()
            if analysis_result.data and analysis_result.data.get('processing_started_at'):
                start_time_str = analysis_result.data['processing_started_at']
                start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(current_time.replace('Z', '+00:00'))
                processing_time = int((end_time - start_time).total_seconds())
                update_data["processing_time_seconds"] = processing_time
                logger.info(f"⏱️ PROCESSING TIME: {processing_time} seconds")
            
            # Update analysis record
            supabase.client.table('analysis_results').update(update_data).eq('id', analysis_id).execute()
            
            # CRITICAL: Create individual AutomationOpportunity records
            logger.info(f"🎯 CREATING AUTOMATION OPPORTUNITY RECORDS")
            automation_opportunities = result.get("automation_opportunities", [])
            
            if isinstance(automation_opportunities, list) and automation_opportunities:
                logger.info(f"📝 Found {len(automation_opportunities)} automation opportunities to create")
                
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
                        opportunity_data_record = {
                            "id": str(uuid4()),
                            "analysis_id": analysis_id,
                            "session_id": recording_id,
                            "organization_id": organization_id,
                            "opportunity_type": workflow_type,
                            "title": f"{workflow_type} Automation",
                            "description": description,
                            "workflow_steps": [],  # TODO: Extract workflow steps if available
                            "current_time_per_occurrence_seconds": time_per_occurrence_seconds,
                            "occurrences_per_day": frequency_daily,
                            "automation_complexity": opportunity_data.get("implementation_complexity", "medium"),
                            "implementation_effort_hours": 24,  # Default estimate
                            "estimated_cost_savings_monthly": round(cost_saved_annually / 12, 2) if cost_saved_annually else 0,
                            "estimated_implementation_cost": 2000.00,  # Default estimate
                            "roi_percentage": round((cost_saved_annually / 2000.00) * 100, 2) if cost_saved_annually > 0 else 0,
                            "payback_period_days": int((2000.00 / (cost_saved_annually / 365)) if cost_saved_annually > 0 else 365),
                            "confidence_score": confidence_score,
                            "priority": opportunity_data.get("priority_score", "medium"),
                            "record_metadata": opportunity_data,
                            "created_at": current_time
                        }
                        
                        supabase.client.table('automation_opportunities').insert(opportunity_data_record).execute()
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
            error_message = result.get("error", "Analysis failed")
            logger.error(f"💥 ERROR MESSAGE: {error_message}")
            
            update_data = {
                "status": "failed",
                "error_message": error_message,
                "processing_completed_at": current_time,
                "updated_at": current_time
            }
            
            # Calculate processing time for failed analysis too
            analysis_result = supabase.client.table('analysis_results').select('processing_started_at').eq('id', analysis_id).single().execute()
            if analysis_result.data and analysis_result.data.get('processing_started_at'):
                start_time_str = analysis_result.data['processing_started_at']
                start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(current_time.replace('Z', '+00:00'))
                processing_time = int((end_time - start_time).total_seconds())
                update_data["processing_time_seconds"] = processing_time
                logger.info(f"⏱️ PROCESSING TIME: {processing_time} seconds")
            
            supabase.client.table('analysis_results').update(update_data).eq('id', analysis_id).execute()
        
        logger.info(f"✅ PIPELINE COMPLETE: Analysis {analysis_id} completed")
            
    except Exception as e:
        logger.error(f"💥 PIPELINE EXCEPTION: Analysis pipeline failed with unexpected error: {e}", exc_info=True)
        
        # Update analysis as failed
        logger.info(f"❌ EXCEPTION CLEANUP: Marking analysis {analysis_id} as failed due to exception")
        
        current_time = datetime.now(timezone.utc).isoformat()
        error_message = str(e)
        
        update_data = {
            "status": "failed",
            "error_message": error_message,
            "processing_completed_at": current_time,
            "updated_at": current_time
        }
        
        # Calculate processing time for exception case too
        try:
            analysis_result = supabase.client.table('analysis_results').select('processing_started_at').eq('id', analysis_id).single().execute()
            if analysis_result.data and analysis_result.data.get('processing_started_at'):
                start_time_str = analysis_result.data['processing_started_at']
                start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(current_time.replace('Z', '+00:00'))
                processing_time = int((end_time - start_time).total_seconds())
                update_data["processing_time_seconds"] = processing_time
                logger.info(f"⏱️ EXCEPTION TIME: Processing time before failure: {processing_time} seconds")
        except Exception as time_calc_error:
            logger.error(f"⚠️ TIME CALC ERROR: {time_calc_error}")
        
        supabase.client.table('analysis_results').update(update_data).eq('id', analysis_id).execute()
        logger.info(f"✅ EXCEPTION HANDLED: Analysis {analysis_id} marked as failed")
    
    logger.info(f"🏁 PIPELINE END: Background analysis pipeline completed for {analysis_id}")

@router.get("/{analysis_id}/status")
async def get_analysis_status(
    analysis_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
):
    """
    Get analysis processing status
    Returns real-time status of GPT-4V analysis with RLS filtering
    """
    logger.info(f"📊 STATUS CHECK: Checking status for analysis {analysis_id}")
    
    supabase = get_supabase_client()
    
    # Query with RLS filtering - user can only see analyses from their organization
    analysis_result = supabase.client.table('analysis_results').select("*").eq('id', analysis_id).single().execute()
    
    if not analysis_result.data:
        logger.error(f"❌ STATUS NOT FOUND: Analysis {analysis_id} not found in database")
        raise HTTPException(status_code=404, detail=f"Analysis {analysis_id} not found")
    
    analysis = analysis_result.data
    logger.info(f"✅ STATUS FOUND: Analysis {analysis_id} has status: {analysis['status']}")
    
    message_map = {
        "processing": "GPT-4V is analyzing your workflow for automation opportunities...",
        "completed": "Analysis complete - automation opportunities identified!",
        "failed": f"Analysis failed: {analysis.get('error_message', 'Unknown error')}",
        "frames_extracted": "Frames extracted, starting GPT-4V analysis..."
    }
    
    return AnalysisResponse(
        id=str(analysis["id"]),
        status=analysis["status"],
        message=message_map.get(analysis["status"], "Processing..."),
        confidence_score=float(analysis["confidence_score"]) if analysis.get("confidence_score") else None,
        processing_cost=float(analysis["analysis_cost"]) if analysis.get("analysis_cost") else None
    )

@router.get("/{analysis_id}/results")
async def get_analysis_results(
    analysis_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
):
    """
    Get completed analysis results
    Returns structured workflow insights and automation opportunities with RLS filtering
    """
    logger.info(f"📋 RESULTS REQUEST: Getting results for analysis {analysis_id}")
    
    supabase = get_supabase_client()
    
    # Query with RLS filtering - user can only see analyses from their organization
    analysis_result = supabase.client.table('analysis_results').select("*").eq('id', analysis_id).single().execute()
    
    if not analysis_result.data:
        logger.error(f"❌ RESULTS NOT FOUND: Analysis {analysis_id} not found in database")
        raise HTTPException(status_code=404, detail=f"Analysis {analysis_id} not found")
    
    analysis = analysis_result.data
    logger.info(f"📊 ANALYSIS STATUS: Analysis {analysis_id} has status: {analysis['status']}")
    
    if analysis["status"] != "completed":
        logger.info(f"⏳ NOT READY: Analysis not completed yet, returning status message")
        return {
            "analysis_id": str(analysis["id"]),
            "status": analysis["status"],
            "message": f"Analysis is {analysis['status']}. Results will be available when complete.",
            "results": None
        }
    
    # Extract structured insights
    insights = analysis.get("structured_insights") or {}
    logger.info(f"💾 EXTRACTING INSIGHTS: Found {len(insights)} insight keys in structured_insights")
    
    # Log what data we have
    workflows = insights.get("workflows", [])
    opportunities = insights.get("automation_opportunities", [])
    summary = insights.get("summary", {})
    
    logger.info(f"📈 RESULTS CONTENT: {len(workflows)} workflows, {len(opportunities)} opportunities")
    logger.info(f"📊 SUMMARY CONTENT: {len(summary)} summary keys")
    
    result_data = {
        "analysis_id": str(analysis["id"]),
        "status": "completed",
        "message": "Analysis complete - automation opportunities identified",
        "results": {
            "workflows": workflows,
            "automation_opportunities": opportunities,
            "time_analysis": insights.get("time_analysis", {}),
            "insights": insights.get("insights", []),
            "summary": summary,
            "confidence_score": float(analysis["confidence_score"]) if analysis.get("confidence_score") else 0,
            "processing_time_seconds": analysis.get("processing_time_seconds"),
            "analysis_cost": float(analysis["analysis_cost"]) if analysis.get("analysis_cost") else 0
        }
    }
    
    logger.info(f"✅ RESULTS SUCCESS: Returning complete analysis results for {analysis_id}")
    return result_data

@router.post("/{analysis_id}/retry")
async def retry_analysis(
    analysis_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
):
    """
    Retry failed analysis
    RLS policies ensure users can only retry their organization's analyses
    """
    supabase = get_supabase_client()
    
    # Verify analysis exists and user has access
    analysis_result = supabase.client.table('analysis_results').select("*").eq('id', analysis_id).single().execute()
    
    if not analysis_result.data:
        raise HTTPException(status_code=404, detail=f"Analysis {analysis_id} not found")
    
    analysis = analysis_result.data
    
    if analysis["status"] not in ["failed"]:
        raise HTTPException(status_code=400, detail="Can only retry failed analyses")
    
    # Reset analysis to processing and clear error message
    current_time = datetime.now(timezone.utc).isoformat()
    update_data = {
        "status": "processing",
        "processing_started_at": current_time,
        "processing_completed_at": None,
        "error_message": None,
        "updated_at": current_time
    }
    
    supabase.client.table('analysis_results').update(update_data).eq('id', analysis_id).execute()
    
    # Get recording info for background task
    recording_result = supabase.client.table('recording_sessions').select("*").eq('id', analysis['session_id']).single().execute()
    
    if recording_result.data:
        recording = recording_result.data
        
        # Start analysis pipeline in background
        from fastapi import BackgroundTasks
        background_tasks = BackgroundTasks()
        background_tasks.add_task(
            run_full_analysis_pipeline,
            analysis_id,
            analysis['session_id'],
            recording.get("duration_seconds", 0),
            current_user["organization_id"],
            None
        )
    
    return AnalysisResponse(
        id=analysis_id,
        status="processing",
        message="Analysis retry initiated successfully"
    )