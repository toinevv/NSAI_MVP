"""
Results and insights endpoints for NewSystem.AI
Serves analyzed workflow data and automation recommendations  
Native Supabase implementation with multi-tenant support via RLS
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime, timezone
import logging
import json

from app.api.v1.auth import get_current_user_from_token
from app.services.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)
router = APIRouter()

# ============================================
# RESPONSE MODELS
# ============================================

class AutomationOpportunity(BaseModel):
    id: str
    workflow_type: str
    priority: str
    time_saved_weekly_hours: float
    implementation_complexity: str
    roi_score: float
    description: str
    confidence_score: Optional[float] = None

class ResultsSummary(BaseModel):
    session_id: str
    total_time_analyzed: int
    automation_opportunities: int
    estimated_time_savings: float
    confidence_score: float

class RawAnalysisData(BaseModel):
    session_id: str
    status: str
    raw_gpt_response: Dict[str, Any]
    structured_insights: Dict[str, Any]
    processing_info: Dict[str, Any]
    metadata: Dict[str, Any]

# ============================================
# HELPER FUNCTIONS
# ============================================

def transform_workflow_steps_to_chart(workflow_steps: List[Any]) -> Dict[str, Any]:
    """
    Transform raw workflow_steps from GPT-4V into ReactFlow chart format
    Expected by DynamicWorkflowChart component
    """
    if not workflow_steps or len(workflow_steps) == 0:
        return {"nodes": [], "edges": []}
    
    # Create nodes from workflow steps
    nodes = []
    for index, step in enumerate(workflow_steps):
        # Determine step type based on action
        action = step.get("action", "").lower()
        if "open" in action or "switch" in action or "access" in action:
            step_type = "application"
        elif "copy" in action or "paste" in action or "enter" in action or "input" in action:
            step_type = "action" 
        elif "data" in action or "information" in action:
            step_type = "data"
        elif "check" in action or "verify" in action or "review" in action:
            step_type = "decision"
        else:
            step_type = "action"
        
        node = {
            "id": f"step-{index + 1}",
            "label": step.get("action", f"Step {index + 1}"),
            "type": step_type,
            "metadata": {
                "time": step.get("time_formatted") or (f"{step.get('time_estimate_seconds', 0)}s" if step.get('time_estimate_seconds') else ""),
                "application": step.get("application", ""),
                "purpose": step.get("purpose", ""),
                "frames": len(step.get("visible_in_frames", []))
            }
        }
        nodes.append(node)
    
    # Create edges between sequential steps
    edges = []
    for i in range(len(workflow_steps) - 1):
        edge = {
            "source": f"step-{i + 1}",
            "target": f"step-{i + 2}",
            "label": None,
            "type": None
        }
        edges.append(edge)
    
    return {"nodes": nodes, "edges": edges}

# ============================================
# API ENDPOINTS
# ============================================

@router.get("/{session_id}")
async def get_complete_results(
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
):
    """
    Get complete analysis results for a session
    Native Supabase implementation with automatic RLS filtering
    """
    try:
        logger.info(f"📊 GETTING RESULTS: Fetching complete results for session {session_id}")
        
        supabase = get_supabase_client()
        
        # Get the recording session (RLS will filter by organization automatically)
        recording_result = supabase.client.table('recording_sessions').select("*").eq('id', session_id).single().execute()
        
        if not recording_result.data:
            logger.error(f"❌ RECORDING NOT FOUND: Session {session_id} not found or access denied")
            raise HTTPException(status_code=404, detail=f"Recording {session_id} not found")
        
        recording = recording_result.data
        logger.info(f"✅ RECORDING FOUND: {recording['title']} - {recording['status']}")
        
        # Get the analysis results (RLS will filter by organization automatically)
        analysis_result = supabase.client.table('analysis_results').select("*").eq('session_id', session_id).single().execute()
        
        if not analysis_result.data:
            logger.error(f"❌ ANALYSIS NOT FOUND: Analysis results not found for recording {session_id}")
            raise HTTPException(status_code=404, detail=f"Analysis results not found for recording {session_id}")
        
        analysis = analysis_result.data
        logger.info(f"✅ ANALYSIS FOUND: Status={analysis['status']}, Frames={analysis.get('frames_analyzed', 0)}")
        
        if analysis["status"] != "completed":
            logger.info(f"⏳ ANALYSIS PENDING: Analysis is {analysis['status']}, returning status message")
            return {
                "session_id": session_id,
                "status": analysis["status"],
                "message": f"Analysis is {analysis['status']}. Results will be available when complete.",
                "results": None
            }
        
        # Parse structured insights
        insights = analysis.get("structured_insights") or {}
        logger.info(f"📋 INSIGHTS: Found {len(insights)} insight categories")
        
        # Generate workflow_chart from raw GPT response if available
        workflow_chart = None
        raw_gpt_response = analysis.get("raw_gpt_response", {})
        
        # Try to get workflow steps from raw GPT response
        if raw_gpt_response and isinstance(raw_gpt_response, dict):
            analysis_data = raw_gpt_response.get("analysis", {})
            workflow_steps = analysis_data.get("workflow_steps", [])
            
            if workflow_steps and len(workflow_steps) > 0:
                workflow_chart = transform_workflow_steps_to_chart(workflow_steps)
                logger.info(f"📊 WORKFLOW CHART: Generated chart with {len(workflow_chart['nodes'])} nodes")
            else:
                logger.warning(f"⚠️ NO WORKFLOW STEPS: No workflow_steps found in raw GPT response")
        else:
            logger.warning(f"⚠️ NO RAW RESPONSE: No raw GPT response available for workflow chart generation")
        
        # Build response with real data
        results = {
            "session_id": session_id,
            "status": "completed",
            "recording_info": {
                "title": recording["title"],
                "duration_seconds": recording["duration_seconds"] or 0,
                "created_at": recording["created_at"]
            },
            "analysis_info": {
                "frames_analyzed": analysis["frames_analyzed"] or 0,
                "confidence_score": float(analysis["confidence_score"]) if analysis["confidence_score"] else 0.0,
                "processing_time_seconds": analysis["processing_time_seconds"] or 0,
                "analysis_cost": float(analysis["analysis_cost"]) if analysis["analysis_cost"] else 0.0
            },
            "summary": {
                "total_time_analyzed": recording["duration_seconds"] or 0,
                "automation_opportunities": analysis["automation_opportunities_count"] or 0,
                "estimated_time_savings": float(analysis["time_savings_hours_weekly"]) if analysis["time_savings_hours_weekly"] else 0.0,
                "confidence_score": float(analysis["confidence_score"]) if analysis["confidence_score"] else 0.0,
                "annual_cost_savings": float(analysis["cost_savings_annual"]) if analysis["cost_savings_annual"] else 0.0
            },
            "workflows": insights.get("workflows", []),
            "automation_opportunities": insights.get("automation_opportunities", []),
            "time_analysis": insights.get("time_analysis", {}),
            "insights": insights.get("insights", [])
        }
        
        # Add workflow chart if we have it
        if workflow_chart:
            results["workflow_chart"] = workflow_chart
        
        logger.info(f"🎯 RESULTS COMPLETE: Returning complete results for session {session_id}")
        
        return {
            "results": results,
            "message": "Analysis results retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 ERROR: Failed to retrieve results for session {session_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve results: {str(e)}")

@router.get("/{session_id}/summary")
async def get_results_summary(
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
):
    """
    Get executive summary of results
    Native Supabase implementation with RLS filtering
    """
    try:
        logger.info(f"📊 GETTING SUMMARY: Fetching summary for session {session_id}")
        
        supabase = get_supabase_client()
        
        # Get the recording (RLS filters by organization)
        recording_result = supabase.client.table('recording_sessions').select("*").eq('id', session_id).single().execute()
        
        if not recording_result.data:
            logger.error(f"❌ RECORDING NOT FOUND: Session {session_id} not found")
            raise HTTPException(status_code=404, detail=f"Recording {session_id} not found")
        
        recording = recording_result.data
        
        # Get analysis results (RLS filters by organization)
        analysis_result = supabase.client.table('analysis_results').select("*").eq('session_id', session_id).single().execute()
        
        if not analysis_result.data:
            logger.error(f"❌ ANALYSIS NOT FOUND: Analysis results not found for recording {session_id}")
            raise HTTPException(status_code=404, detail=f"Analysis results not found for recording {session_id}")
        
        analysis = analysis_result.data
        
        summary = ResultsSummary(
            session_id=session_id,
            total_time_analyzed=recording["duration_seconds"] or 0,
            automation_opportunities=analysis["automation_opportunities_count"] or 0,
            estimated_time_savings=float(analysis["time_savings_hours_weekly"]) if analysis["time_savings_hours_weekly"] else 0.0,
            confidence_score=float(analysis["confidence_score"]) if analysis["confidence_score"] else 0.0
        )
        
        logger.info(f"✅ SUMMARY COMPLETE: {summary.automation_opportunities} opportunities, {summary.estimated_time_savings}h savings")
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 ERROR: Failed to retrieve summary for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve summary: {str(e)}")

@router.get("/{session_id}/flow")
async def get_flow_chart_data(
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
):
    """
    Get workflow flow chart data
    Native Supabase implementation with workflow_steps transformation
    """
    try:
        logger.info(f"📊 GETTING FLOW CHART: Fetching flow data for session {session_id}")
        
        supabase = get_supabase_client()
        
        # Get analysis results (RLS filters by organization)
        analysis_result = supabase.client.table('analysis_results').select("*").eq('session_id', session_id).single().execute()
        
        if not analysis_result.data:
            logger.error(f"❌ ANALYSIS NOT FOUND: Analysis results not found for recording {session_id}")
            raise HTTPException(status_code=404, detail=f"Analysis results not found for recording {session_id}")
        
        analysis = analysis_result.data
        
        if analysis["status"] != "completed":
            logger.info(f"⏳ ANALYSIS PENDING: Analysis is {analysis['status']}")
            return {
                "session_id": session_id,
                "status": analysis["status"],
                "message": f"Analysis is {analysis['status']}. Flow chart will be available when complete.",
                "flow_chart": None
            }
        
        # Get flow chart data from raw GPT response
        raw_gpt_response = analysis.get("raw_gpt_response", {})
        flow_chart_data = None
        
        if raw_gpt_response and isinstance(raw_gpt_response, dict):
            analysis_data = raw_gpt_response.get("analysis", {})
            workflow_steps = analysis_data.get("workflow_steps", [])
            
            if workflow_steps and len(workflow_steps) > 0:
                # Transform workflow steps to flow chart format
                flow_chart_data = {
                    "nodes": [],
                    "edges": []
                }
                
                # Create nodes from workflow steps
                for i, step in enumerate(workflow_steps):
                    node = {
                        "id": f"step_{i+1}",
                        "type": "process",
                        "label": step.get("action", f"Step {i+1}"),
                        "timeSpent": step.get("time_estimate_seconds", 0),
                        "automationPotential": 0.7  # Default automation potential
                    }
                    flow_chart_data["nodes"].append(node)
                
                # Create edges between sequential steps
                for i in range(len(workflow_steps) - 1):
                    edge = {
                        "source": f"step_{i+1}",
                        "target": f"step_{i+2}",
                        "label": "next"
                    }
                    flow_chart_data["edges"].append(edge)
                
                logger.info(f"📊 FLOW CHART: Generated {len(flow_chart_data['nodes'])} nodes from workflow steps")
            else:
                logger.warning(f"⚠️ NO WORKFLOW STEPS: No workflow_steps found in analysis")
        
        # Fallback: Generate simple flow chart from available data
        if not flow_chart_data:
            logger.info(f"🔄 FALLBACK FLOW: Generating simple fallback flow chart")
            flow_chart_data = {
                "nodes": [
                    {"id": "start", "type": "start", "label": "Workflow Start", "timeSpent": 0},
                    {"id": "process", "type": "process", "label": "Manual Process", "timeSpent": analysis.get("time_savings_hours_weekly", 0) * 3600},
                    {"id": "end", "type": "end", "label": "Workflow Complete", "timeSpent": 0}
                ],
                "edges": [
                    {"source": "start", "target": "process", "label": "Begin"},
                    {"source": "process", "target": "end", "label": "Complete"}
                ]
            }
        
        return {
            "flow_chart": flow_chart_data,
            "message": "Flow chart data retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 ERROR: Failed to retrieve flow chart for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve flow chart: {str(e)}")

@router.get("/{session_id}/opportunities")
async def get_automation_opportunities(
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
):
    """
    Get automation opportunities list
    Native Supabase implementation with RLS filtering
    """
    try:
        logger.info(f"📊 GETTING OPPORTUNITIES: Fetching opportunities for session {session_id}")
        
        supabase = get_supabase_client()
        
        # Get analysis results (RLS filters by organization)
        analysis_result = supabase.client.table('analysis_results').select("*").eq('session_id', session_id).single().execute()
        
        if not analysis_result.data:
            logger.error(f"❌ ANALYSIS NOT FOUND: Analysis results not found for recording {session_id}")
            raise HTTPException(status_code=404, detail=f"Analysis results not found for recording {session_id}")
        
        analysis = analysis_result.data
        
        if analysis["status"] != "completed":
            logger.info(f"⏳ ANALYSIS PENDING: Analysis is {analysis['status']}")
            return {
                "session_id": session_id,
                "status": analysis["status"],
                "message": f"Analysis is {analysis['status']}. Opportunities will be available when complete.",
                "opportunities": []
            }
        
        # Get opportunities from automation_opportunities table (RLS filters by organization)
        opportunities_result = supabase.client.table('automation_opportunities').select("*").eq('session_id', session_id).execute()
        
        opportunities = []
        if opportunities_result.data:
            for opp in opportunities_result.data:
                # Convert database record to API format
                opportunity = AutomationOpportunity(
                    id=str(opp["id"]),
                    workflow_type=opp["opportunity_type"],
                    priority=opp["priority"],
                    time_saved_weekly_hours=float(opp["current_time_per_occurrence_seconds"] or 0) / 3600 * 5,  # Rough weekly estimate
                    implementation_complexity=opp["automation_complexity"],
                    roi_score=float(opp["roi_percentage"] or 0),
                    description=opp["description"],
                    confidence_score=float(opp["confidence_score"]) if opp["confidence_score"] else None
                )
                opportunities.append(opportunity)
        
        logger.info(f"✅ OPPORTUNITIES: Found {len(opportunities)} automation opportunities")
        
        return {
            "opportunities": opportunities,
            "message": f"Found {len(opportunities)} automation opportunities"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 ERROR: Failed to retrieve opportunities for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve opportunities: {str(e)}")

@router.get("/{session_id}/cost")
async def get_cost_analysis(
    session_id: str,
    hourly_rate: Optional[float] = 25.0,
    implementation_budget: Optional[float] = None,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
):
    """
    Get cost-benefit analysis
    Native Supabase implementation using analysis data
    """
    try:
        logger.info(f"📊 GETTING COST ANALYSIS: Fetching cost analysis for session {session_id}")
        
        supabase = get_supabase_client()
        
        # Get analysis results (RLS filters by organization)
        analysis_result = supabase.client.table('analysis_results').select("*").eq('session_id', session_id).single().execute()
        
        if not analysis_result.data:
            logger.error(f"❌ ANALYSIS NOT FOUND: Analysis results not found for recording {session_id}")
            raise HTTPException(status_code=404, detail=f"Analysis results not found for recording {session_id}")
        
        analysis = analysis_result.data
        
        if analysis["status"] != "completed":
            logger.info(f"⏳ ANALYSIS PENDING: Analysis is {analysis['status']}")
            return {
                "session_id": session_id,
                "status": analysis["status"],
                "message": f"Analysis is {analysis['status']}. Cost analysis will be available when complete.",
                "cost_analysis": None
            }
        
        # Calculate cost analysis from analysis data
        time_savings_weekly = float(analysis["time_savings_hours_weekly"] or 0)
        current_monthly_hours = time_savings_weekly * 4  # 4 weeks per month
        current_monthly_cost = current_monthly_hours * hourly_rate
        
        # After automation
        projected_monthly_hours = current_monthly_hours * 0.2  # Assume 80% time savings
        projected_monthly_cost = projected_monthly_hours * hourly_rate
        
        # Implementation cost (use budget or estimate)
        implementation_cost = implementation_budget or 5000.0  # Default $5k implementation
        
        # Calculate savings
        monthly_savings = current_monthly_cost - projected_monthly_cost
        annual_savings = monthly_savings * 12
        
        # Calculate payback period
        payback_period_days = int((implementation_cost / monthly_savings) * 30) if monthly_savings > 0 else 0
        
        cost_analysis = {
            "current_monthly_cost": current_monthly_cost,
            "projected_monthly_cost": projected_monthly_cost,
            "implementation_cost": implementation_cost,
            "payback_period_days": payback_period_days,
            "annual_savings": annual_savings,
            "hourly_rate_used": hourly_rate,
            "time_savings_weekly_hours": time_savings_weekly,
            "confidence_score": float(analysis["confidence_score"]) if analysis["confidence_score"] else 0.0
        }
        
        # Build ROI metrics
        roi_metrics = {
            "time_savings": {
                "weekly_hours": time_savings_weekly,
                "current_monthly_hours": current_monthly_hours
            },
            "cost_savings": {
                "monthly_usd": monthly_savings,
                "annual_usd": annual_savings
            },
            "implementation": {
                "estimated_cost_usd": implementation_cost,
                "payback_period_days": payback_period_days
            }
        }
        
        logger.info(f"💰 COST ANALYSIS: ${annual_savings}/year savings, {payback_period_days} days payback")
        
        return {
            "cost_analysis": cost_analysis,
            "roi_metrics": roi_metrics,
            "message": "Cost analysis calculated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 ERROR: Failed to calculate cost analysis for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate cost analysis: {str(e)}")

@router.get("/{session_id}/raw")
async def get_raw_analysis_data(
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
):
    """
    Get raw GPT-4V analysis data for development and debugging
    Native Supabase implementation with complete raw response data
    """
    try:
        logger.info(f"🔍 GETTING RAW DATA: Fetching raw analysis data for session {session_id}")
        
        supabase = get_supabase_client()
        
        # Get the recording session (RLS filters by organization)
        recording_result = supabase.client.table('recording_sessions').select("*").eq('id', session_id).single().execute()
        
        if not recording_result.data:
            logger.error(f"❌ RECORDING NOT FOUND: Session {session_id} not found")
            raise HTTPException(status_code=404, detail=f"Recording {session_id} not found")
        
        recording = recording_result.data
        
        # Get the analysis results (RLS filters by organization)
        analysis_result = supabase.client.table('analysis_results').select("*").eq('session_id', session_id).single().execute()
        
        if not analysis_result.data:
            logger.error(f"❌ ANALYSIS NOT FOUND: Analysis results not found for recording {session_id}")
            raise HTTPException(status_code=404, detail=f"Analysis results not found for recording {session_id}")
        
        analysis = analysis_result.data
        
        # Parse raw GPT response
        raw_gpt_response = analysis.get("raw_gpt_response") or {}
        structured_insights = analysis.get("structured_insights") or {}
        
        # Build comprehensive processing info
        processing_info = {
            "gpt_version": analysis["gpt_version"],
            "frames_analyzed": analysis["frames_analyzed"],
            "processing_time_seconds": analysis["processing_time_seconds"],
            "analysis_cost": float(analysis["analysis_cost"]) if analysis["analysis_cost"] else 0.0,
            "confidence_score": float(analysis["confidence_score"]) if analysis["confidence_score"] else 0.0,
            "processing_started_at": analysis["processing_started_at"],
            "processing_completed_at": analysis["processing_completed_at"],
            "status": analysis["status"],
            "error_message": analysis["error_message"]
        }
        
        # Extract token usage from raw GPT response
        token_usage = {}
        if raw_gpt_response and "usage" in raw_gpt_response:
            token_usage = raw_gpt_response["usage"]
        elif structured_insights and "metadata" in structured_insights and "token_usage" in structured_insights["metadata"]:
            token_usage = structured_insights["metadata"]["token_usage"]
        
        # Build metadata
        metadata = {
            "recording_duration_seconds": recording["duration_seconds"],
            "recording_file_size_bytes": recording["file_size_bytes"],
            "workflow_type": recording["workflow_type"],
            "token_usage": token_usage,
            "has_raw_response": bool(raw_gpt_response),
            "has_structured_insights": bool(structured_insights),
            "analysis_id": str(analysis["id"])
        }
        
        # Format raw response for frontend compatibility
        formatted_raw_response = {
            "analysis": raw_gpt_response,
            "usage": token_usage,
            "metadata": {
                "model": processing_info.get("gpt_version", "gpt-4o"),
                "timestamp": processing_info.get("processing_completed_at"),
                "cost": processing_info.get("analysis_cost", 0)
            }
        }

        logger.info(f"🔍 RAW DATA COMPLETE: Returning complete raw analysis data for session {session_id}")

        return {
            "session_id": session_id,
            "status": analysis["status"],
            "raw_gpt_response": formatted_raw_response,
            "structured_insights": structured_insights,
            "processing_info": processing_info,
            "metadata": metadata,
            "message": "Raw analysis data retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 ERROR: Failed to retrieve raw analysis data for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve raw analysis data: {str(e)}")