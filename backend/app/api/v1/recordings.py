"""
Recording management endpoints for NewSystem.AI
Handles screen recording lifecycle: start, upload chunks, complete
Native Supabase implementation with multi-tenant support via RLS
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, File, UploadFile
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
import logging
import httpx

from app.api.v1.auth import get_current_user_from_token
from app.schemas.recording import (
    RecordingStartRequest, RecordingStartResponse,
    VideoChunkUploadRequest, ChunkUploadResponse,
    RecordingCompleteRequest, RecordingCompleteResponse,
    RecordingResponse, RecordingListResponse,
    RecordingError
)
from app.services.supabase_client import get_supabase_client
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# ============================================
# HELPER FUNCTIONS
# ============================================

def format_uuid_for_supabase(uuid_obj):
    """Convert UUID object to string for Supabase compatibility"""
    if isinstance(uuid_obj, UUID):
        return str(uuid_obj)
    return uuid_obj

# ============================================
# RECORDING ENDPOINTS
# ============================================

@router.post("/start", response_model=RecordingStartResponse)
async def start_recording(
    request: RecordingStartRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
):
    """
    Start a new screen recording session
    Native Supabase implementation with organization context
    """
    try:
        logger.info(f"Starting recording for user {current_user['id']} in organization {current_user['organization_id']}")
        
        if not current_user.get("organization_id"):
            raise HTTPException(status_code=400, detail="User must be associated with an organization")
        
        supabase = get_supabase_client()
        
        # Create new recording session in Supabase
        recording_data = {
            "id": str(uuid4()),
            "user_id": current_user["id"],
            "organization_id": current_user["organization_id"],
            "title": request.title,
            "description": request.description,
            "workflow_type": request.workflow_type,
            "status": "recording",
            "privacy_settings": request.privacy_settings.dict() if request.privacy_settings else {"blur_passwords": True, "exclude_personal_info": False},
            "recording_metadata": request.metadata or {},
            "duration_seconds": 0,
            "file_size_bytes": 0,
            "analysis_cost": 0.00,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Insert recording session
        result = supabase.client.table('recording_sessions').insert(recording_data).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create recording session")
        
        recording = result.data[0]
        logger.info(f"Recording session created: {recording['id']}")
        
        return RecordingStartResponse(
            id=UUID(recording["id"]),
            status="recording",
            message="Recording session started successfully",
            chunk_settings={
                "chunk_size_seconds": settings.CHUNK_SIZE_SECONDS,
                "max_file_size_mb": settings.MAX_FILE_SIZE_MB,
                "allowed_formats": settings.ALLOWED_VIDEO_FORMATS,
                "recording_fps": settings.RECORDING_FPS
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting recording: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start recording session: {str(e)}"
        )

@router.post("/{recording_id}/complete", response_model=RecordingCompleteResponse)
async def complete_recording(
    recording_id: UUID,
    request: RecordingCompleteRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
):
    """
    Mark recording as complete and trigger analysis
    Native Supabase implementation with automatic analysis queueing
    """
    try:
        supabase = get_supabase_client()
        
        # Verify recording session exists and user has access
        recording_result = supabase.client.table('recording_sessions').select("*").eq('id', str(recording_id)).single().execute()
        
        if not recording_result.data:
            raise HTTPException(status_code=404, detail="Recording session not found")
        
        recording = recording_result.data
        
        if recording["status"] != "recording":
            raise HTTPException(status_code=400, detail="Recording is not in recording state")
        
        logger.info(f"Completing recording {recording_id}")
        
        # Prepare updated recording data
        current_metadata = recording.get("recording_metadata", {})
        current_metadata.update(request.metadata or {})
        current_metadata.update({
            "chunk_count": request.chunk_count,
            "completion_time": datetime.now(timezone.utc).isoformat()
        })
        
        update_data = {
            "status": "completed",
            "duration_seconds": request.duration_seconds,
            "file_size_bytes": request.total_file_size_bytes,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "recording_metadata": current_metadata
        }
        
        # Update recording in Supabase
        update_result = supabase.client.table('recording_sessions').update(update_data).eq('id', str(recording_id)).execute()
        
        if not update_result.data:
            raise HTTPException(status_code=500, detail="Failed to update recording")
        
        # Queue analysis task automatically
        logger.info(f"Recording {recording_id} completed. Queuing analysis...")
        background_tasks.add_task(queue_recording_analysis, str(recording_id))
        
        return RecordingCompleteResponse(
            id=recording_id,
            status="completed",
            message="Recording completed successfully - analysis started",
            analysis_queued=True,
            estimated_processing_time_minutes=2
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing recording: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to complete recording: {str(e)}"
        )

@router.get("/", response_model=RecordingListResponse)
async def list_recordings(
    page: int = 1,
    page_size: int = 10,
    status: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
):
    """
    List user's recordings with automatic organization filtering via RLS
    Native Supabase implementation with pagination
    """
    try:
        supabase = get_supabase_client()
        
        # Build base query - RLS automatically filters by organization
        query = supabase.client.table('recording_sessions').select("*")
        
        # Filter by status if provided
        if status:
            query = query.eq('status', status)
        
        # Get total count for pagination
        count_result = supabase.client.table('recording_sessions').select("*", count="exact").execute()
        total = count_result.count if hasattr(count_result, 'count') else 0
        
        # Apply pagination and ordering
        offset = (page - 1) * page_size
        recordings_result = query.order('created_at', desc=True).range(offset, offset + page_size - 1).execute()
        
        recordings = recordings_result.data or []
        
        # Build response with analysis status
        recording_responses = []
        for recording in recordings:
            # Check if recording has completed analysis
            analysis_result = supabase.client.table('analysis_results').select("id").eq('session_id', recording['id']).eq('status', 'completed').execute()
            has_analysis = len(analysis_result.data or []) > 0
            
            # Create response object
            recording_response = {
                "id": recording["id"],
                "user_id": recording["user_id"],
                "title": recording["title"],
                "description": recording.get("description"),
                "status": recording["status"],
                "duration_seconds": recording.get("duration_seconds", 0),
                "file_size_bytes": recording.get("file_size_bytes", 0),
                "workflow_type": recording.get("workflow_type"),
                "privacy_settings": recording.get("privacy_settings", {}),
                "recording_metadata": recording.get("recording_metadata", {}),
                "analysis_cost": float(recording.get("analysis_cost", 0)),
                "created_at": recording["created_at"],
                "completed_at": recording.get("completed_at"),
                "updated_at": recording["updated_at"],
                "has_analysis": has_analysis
            }
            recording_responses.append(recording_response)
        
        return {
            "recordings": recording_responses,
            "total": total,
            "page": page,
            "page_size": page_size,
            "has_more": offset + page_size < total
        }
        
    except Exception as e:
        logger.error(f"Error listing recordings: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list recordings: {str(e)}"
        )

# ============================================
# BACKGROUND TASKS
# ============================================

async def queue_recording_analysis(recording_id: str):
    """
    Background task to queue analysis for completed recording
    Calls the analysis start endpoint to begin GPT-4V processing
    """
    try:
        logger.info(f"Starting background analysis for recording {recording_id}")
        
        # Call the analysis start endpoint internally
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.API_BASE_URL}/api/v1/analysis/{recording_id}/start",
                json={"analysis_type": "natural"},
                timeout=300.0
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Analysis queued successfully for recording {recording_id}: {result.get('id')}")
            else:
                logger.error(f"Failed to start analysis for recording {recording_id}: {response.status_code} - {response.text}")
                
    except httpx.ReadTimeout:
        logger.error(f"Analysis timeout for recording {recording_id} - GPT-4V took longer than 5 minutes")
    except Exception as e:
        logger.error(f"Background analysis task failed for recording {recording_id}: {e}", exc_info=True)