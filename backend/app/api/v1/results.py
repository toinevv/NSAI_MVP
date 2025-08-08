"""
Results and insights endpoints for NewSystem.AI
Serves analyzed workflow data and automation recommendations
Focus: ROI calculations and actionable insights for logistics managers
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.models.database import RecordingSession, AnalysisResult
from app.services.insights import get_roi_calculator

logger = logging.getLogger(__name__)
router = APIRouter()

class AutomationOpportunity(BaseModel):
    id: str
    workflow_type: str
    priority: str
    time_saved_weekly_hours: float
    implementation_complexity: str
    roi_score: float
    description: str

class ResultsSummary(BaseModel):
    session_id: str
    total_time_analyzed: int
    automation_opportunities: int
    estimated_time_savings: float
    confidence_score: float

@router.get("/{session_id}")
async def get_complete_results(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Get complete analysis results for a session
    Returns real data from AnalysisResult table
    """
    try:
        # Get the recording session
        recording = db.query(RecordingSession).filter(
            RecordingSession.id == session_id
        ).first()
        
        if not recording:
            raise HTTPException(status_code=404, detail=f"Recording {session_id} not found")
        
        # Get the analysis results
        analysis = db.query(AnalysisResult).filter(
            AnalysisResult.session_id == session_id
        ).first()
        
        if not analysis:
            raise HTTPException(status_code=404, detail=f"Analysis results not found for recording {session_id}")
        
        if analysis.status != "completed":
            return {
                "session_id": session_id,
                "status": analysis.status,
                "message": f"Analysis is {analysis.status}. Results will be available when complete.",
                "results": None
            }
        
        # Parse structured insights
        insights = analysis.structured_insights or {}
        
        # Build response with real data
        results = {
            "session_id": session_id,
            "status": "completed",
            "recording_info": {
                "title": recording.title,
                "duration_seconds": recording.duration_seconds,
                "created_at": recording.created_at.isoformat()
            },
            "analysis_info": {
                "frames_analyzed": analysis.frames_analyzed,
                "confidence_score": float(analysis.confidence_score) if analysis.confidence_score else 0.0,
                "processing_time_seconds": analysis.processing_time_seconds,
                "analysis_cost": float(analysis.analysis_cost) if analysis.analysis_cost else 0.0
            },
            "summary": {
                "total_time_analyzed": recording.duration_seconds or 0,
                "automation_opportunities": analysis.automation_opportunities_count or 0,
                "estimated_time_savings": float(analysis.time_savings_hours_weekly) if analysis.time_savings_hours_weekly else 0.0,
                "confidence_score": float(analysis.confidence_score) if analysis.confidence_score else 0.0,
                "annual_cost_savings": float(analysis.annual_cost_savings) if analysis.annual_cost_savings else 0.0
            },
            "workflows": insights.get("workflows", []),
            "automation_opportunities": insights.get("automation_opportunities", []),
            "time_analysis": insights.get("time_analysis", {}),
            "insights": insights.get("insights", [])
        }
        
        return {
            "results": results,
            "message": "Analysis results retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving results for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve results: {str(e)}")

@router.get("/{session_id}/summary")
async def get_results_summary(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Get executive summary of results
    Returns real data from AnalysisResult table
    """
    try:
        # Get the recording and analysis
        recording = db.query(RecordingSession).filter(
            RecordingSession.id == session_id
        ).first()
        
        if not recording:
            raise HTTPException(status_code=404, detail=f"Recording {session_id} not found")
        
        analysis = db.query(AnalysisResult).filter(
            AnalysisResult.session_id == session_id
        ).first()
        
        if not analysis:
            raise HTTPException(status_code=404, detail=f"Analysis results not found for recording {session_id}")
        
        return ResultsSummary(
            session_id=session_id,
            total_time_analyzed=recording.duration_seconds or 0,
            automation_opportunities=analysis.automation_opportunities_count or 0,
            estimated_time_savings=float(analysis.time_savings_hours_weekly) if analysis.time_savings_hours_weekly else 0.0,
            confidence_score=float(analysis.confidence_score) if analysis.confidence_score else 0.0
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving summary for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve summary: {str(e)}")

@router.get("/{session_id}/flow")
async def get_flow_chart_data(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Get workflow flow chart data
    Returns real flow data from analysis results
    """
    try:
        # Get analysis results
        analysis = db.query(AnalysisResult).filter(
            AnalysisResult.session_id == session_id
        ).first()
        
        if not analysis:
            raise HTTPException(status_code=404, detail=f"Analysis results not found for recording {session_id}")
        
        if analysis.status != "completed":
            return {
                "session_id": session_id,
                "status": analysis.status,
                "message": f"Analysis is {analysis.status}. Flow chart will be available when complete.",
                "flow_chart": None
            }
        
        # Parse structured insights for workflow data
        insights = analysis.structured_insights or {}
        workflows = insights.get("workflows", [])
        
        # If we have workflow data, use it; otherwise provide a simple fallback
        if workflows:
            flow_chart_data = insights.get("flow_chart", {})
        else:
            # Generate simple flow chart from available data
            flow_chart_data = {
                "nodes": [
                    {"id": "start", "type": "start", "label": "Workflow Start", "timeSpent": 0},
                    {"id": "process", "type": "process", "label": "Manual Process", "timeSpent": analysis.time_savings_hours_weekly * 3600 if analysis.time_savings_hours_weekly else 0},
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
        logger.error(f"Error retrieving flow chart for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve flow chart: {str(e)}")

@router.get("/{session_id}/opportunities")
async def get_automation_opportunities(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Get automation opportunities list
    Returns real opportunities from analysis results
    """
    try:
        # Get analysis results
        analysis = db.query(AnalysisResult).filter(
            AnalysisResult.session_id == session_id
        ).first()
        
        if not analysis:
            raise HTTPException(status_code=404, detail=f"Analysis results not found for recording {session_id}")
        
        if analysis.status != "completed":
            return {
                "session_id": session_id,
                "status": analysis.status,
                "message": f"Analysis is {analysis.status}. Opportunities will be available when complete.",
                "opportunities": []
            }
        
        # Parse structured insights for automation opportunities
        insights = analysis.structured_insights or {}
        opportunities_data = insights.get("automation_opportunities", [])
        
        # Convert to AutomationOpportunity models
        opportunities = []
        for i, opp in enumerate(opportunities_data):
            if isinstance(opp, dict):
                opportunities.append(AutomationOpportunity(
                    id=opp.get("id", f"opp_{i+1}"),
                    workflow_type=opp.get("workflow_type", "unknown"),
                    priority=opp.get("priority", "medium"),
                    time_saved_weekly_hours=float(opp.get("time_saved_weekly_hours", 0)),
                    implementation_complexity=opp.get("implementation_complexity", "consider"),
                    roi_score=float(opp.get("roi_score", 0)),
                    description=opp.get("description", "Automation opportunity identified")
                ))
        
        return {
            "opportunities": opportunities,
            "message": f"Found {len(opportunities)} automation opportunities"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving opportunities for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve opportunities: {str(e)}")

@router.get("/{session_id}/cost")
async def get_cost_analysis(
    session_id: str,
    hourly_rate: Optional[float] = 25.0,
    implementation_budget: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """
    Get cost-benefit analysis
    Uses real ROI calculator with analysis data
    """
    try:
        # Get analysis results
        analysis = db.query(AnalysisResult).filter(
            AnalysisResult.session_id == session_id
        ).first()
        
        if not analysis:
            raise HTTPException(status_code=404, detail=f"Analysis results not found for recording {session_id}")
        
        if analysis.status != "completed":
            return {
                "session_id": session_id,
                "status": analysis.status,
                "message": f"Analysis is {analysis.status}. Cost analysis will be available when complete.",
                "cost_analysis": None
            }
        
        # Use the ROI calculator
        calculator = get_roi_calculator()
        insights = analysis.structured_insights or {}
        
        roi_metrics = calculator.calculate_roi(
            insights,
            hourly_rate=hourly_rate,
            implementation_budget=implementation_budget
        )
        
        # Extract cost analysis from ROI metrics
        cost_analysis = {
            "current_monthly_cost": roi_metrics["cost_savings"]["monthly_usd"] + roi_metrics["time_savings"]["current_monthly_hours"] * hourly_rate,
            "projected_monthly_cost": roi_metrics["time_savings"]["current_monthly_hours"] * hourly_rate - roi_metrics["cost_savings"]["monthly_usd"],
            "implementation_cost": implementation_budget or roi_metrics.get("implementation", {}).get("estimated_cost_usd", 5000),
            "payback_period_days": roi_metrics.get("implementation", {}).get("payback_period_days", 0),
            "annual_savings": roi_metrics["cost_savings"]["annual_usd"],
            "hourly_rate_used": hourly_rate,
            "time_savings_weekly_hours": roi_metrics["time_savings"]["weekly_hours"],
            "confidence_score": float(analysis.confidence_score) if analysis.confidence_score else 0.0
        }
        
        return {
            "cost_analysis": cost_analysis,
            "roi_metrics": roi_metrics,
            "message": "Cost analysis calculated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating cost analysis for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate cost analysis: {str(e)}")

# Export functionality removed per CTO feedback - not needed for MVP
# Focus on core recording→analysis→results pipeline