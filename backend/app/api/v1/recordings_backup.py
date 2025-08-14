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

@router.post("/{recording_id}/chunks/signed-url")
async def get_chunk_signed_url(
    recording_id: UUID,
    chunk_index: int,
    expires_in: int = 3600,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
):
    """
    Get a signed URL for direct chunk upload to Supabase Storage
    RLS policies automatically handle organization isolation
    """
    try:
        supabase = get_supabase_client()
        
        # Verify recording session exists and user has access (RLS will filter automatically)
        recording_result = supabase.client.table('recording_sessions').select("*").eq('id', str(recording_id)).single().execute()
        
        if not recording_result.data:
            raise HTTPException(status_code=404, detail="Recording session not found")
        
        recording = recording_result.data
        
        if recording["status"] != "recording":
            raise HTTPException(status_code=400, detail="Recording session is not active")
        
        logger.info(f"Generating signed URL for chunk {chunk_index} of recording {recording_id}")
        
        # Get Supabase client and create signed URL
        signed_url_info = supabase.create_chunk_signed_url(
            session_id=recording_id,
            chunk_index=chunk_index,
            expires_in=expires_in
        )
        
        if not signed_url_info:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate signed upload URL"
            )
        
        return {
            "signed_url": signed_url_info["signed_url"],
            "file_path": signed_url_info["file_path"],
            "expires_at": signed_url_info["expires_at"],
            "chunk_index": chunk_index,
            "content_type": signed_url_info["content_type"],
            "upload_method": "direct",
            "instructions": {
                "method": "PUT",
                "headers": {
                    "Content-Type": signed_url_info["content_type"]
                },
                "body": "Binary chunk data"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating signed URL: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate signed URL: {str(e)}"
        )

@router.post("/{recording_id}/chunks/verify")
async def verify_chunk_upload(
    recording_id: UUID,
    chunk_index: int,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
):
    """
    Verify that a chunk was successfully uploaded via signed URL
    Native Supabase implementation with RLS-based access control
    """
    try:
        supabase = get_supabase_client()
        
        # Verify recording session exists and user has access (RLS handles filtering)
        recording_result = supabase.client.table('recording_sessions').select("*").eq('id', str(recording_id)).single().execute()
        
        if not recording_result.data:
            raise HTTPException(status_code=404, detail="Recording session not found")
        
        recording = recording_result.data
        logger.info(f"Verifying chunk {chunk_index} for recording {recording_id}")
        
        # Verify chunk in Supabase Storage
        verification_result = await supabase.verify_chunk_upload(
            session_id=recording_id,
            chunk_index=chunk_index
        )
        
        if verification_result["exists"]:
            # Check for existing chunk record
            existing_chunk_result = supabase.client.table('video_chunks').select("*").eq('session_id', str(recording_id)).eq('chunk_index', chunk_index).execute()
            
            chunk_data = {
                "session_id": str(recording_id),
                "organization_id": current_user["organization_id"],
                "chunk_index": chunk_index,
                "file_path": verification_result["file_path"],
                "file_size_bytes": verification_result.get("size", 0),
                "upload_status": "completed",
                "uploaded_at": datetime.now(timezone.utc).isoformat(),
                "error_message": None
            }
            
            if existing_chunk_result.data:
                # Update existing chunk
                chunk_id = existing_chunk_result.data[0]["id"]
                update_result = supabase.client.table('video_chunks').update(chunk_data).eq('id', chunk_id).execute()
                chunk_record = update_result.data[0] if update_result.data else existing_chunk_result.data[0]
                logger.info(f"Updated existing chunk record {chunk_index} for session {recording_id}")
            else:
                # Create new chunk record
                chunk_data["id"] = str(uuid4())
                chunk_data["created_at"] = datetime.now(timezone.utc).isoformat()
                insert_result = supabase.client.table('video_chunks').insert(chunk_data).execute()
                chunk_record = insert_result.data[0]
                logger.info(f"Created new chunk record {chunk_index} for session {recording_id}")
            
            return {
                "verified": True,
                "chunk_id": chunk_record["id"],
                "file_path": verification_result["file_path"],
                "file_size": verification_result.get("size", 0),
                "public_url": verification_result.get("public_url"),
                "message": "Chunk verification successful"
            }
        else:
            return {
                "verified": False,
                "error": verification_result.get("error", "Chunk not found in storage"),
                "message": "Chunk verification failed"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying chunk: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to verify chunk: {str(e)}"
        )

@router.post("/{recording_id}/chunks", response_model=ChunkUploadResponse)
async def upload_chunk(
    recording_id: UUID,
    chunk_file: UploadFile = File(...),
    chunk_index: int = 0,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
):
    """
    Upload video chunks during recording
    Native Supabase implementation with RLS-based multi-tenancy
    """
    try:
        supabase = get_supabase_client()
        
        # Verify recording session exists and user has access
        recording_result = supabase.client.table('recording_sessions').select("*").eq('id', str(recording_id)).single().execute()
        
        if not recording_result.data:
            raise HTTPException(status_code=404, detail="Recording session not found")
        
        recording = recording_result.data
        
        if recording["status"] != "recording":
            raise HTTPException(status_code=400, detail="Recording session is not active")
        
        logger.info(f"Uploading chunk {chunk_index} for recording {recording_id}")
        
        # Read file content
        file_content = await chunk_file.read()
        file_size = len(file_content)
        
        # Upload to Supabase Storage
        upload_result = await supabase.upload_video_chunk(
            session_id=recording_id,
            chunk_index=chunk_index,
            file_content=file_content,
            content_type=chunk_file.content_type or "video/webm"
        )
        
        if not upload_result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload chunk: {upload_result['error']}"
            )
        
        # Check for existing chunk record to avoid duplicates
        existing_chunk_result = supabase.client.table('video_chunks').select("*").eq('session_id', str(recording_id)).eq('chunk_index', chunk_index).execute()
        
        chunk_data = {
            "session_id": str(recording_id),
            "organization_id": current_user["organization_id"],
            "chunk_index": chunk_index,
            "file_path": upload_result["file_path"],
            "file_size_bytes": file_size,
            "upload_status": "completed",
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
            "error_message": None
        }
        
        if existing_chunk_result.data:
            # Update existing chunk - handles retry scenarios
            chunk_id = existing_chunk_result.data[0]["id"]
            update_result = supabase.client.table('video_chunks').update(chunk_data).eq('id', chunk_id).execute()
            chunk_record = update_result.data[0] if update_result.data else existing_chunk_result.data[0]
            logger.info(f"Updated existing chunk record {chunk_index} for session {recording_id}")
        else:
            # Create new chunk record
            chunk_data["id"] = str(uuid4())
            chunk_data["created_at"] = datetime.now(timezone.utc).isoformat()
            insert_result = supabase.client.table('video_chunks').insert(chunk_data).execute()
            chunk_record = insert_result.data[0]
            logger.info(f"Created new chunk record {chunk_index} for session {recording_id}")
        
        logger.info(f"Chunk {chunk_index} uploaded successfully for recording {recording_id}")
        
        return ChunkUploadResponse(
            chunk_id=UUID(chunk_record["id"]),
            status="completed",
            message="Chunk uploaded successfully",
            next_chunk_index=chunk_index + 1
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading chunk: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload chunk: {str(e)}"
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
):\n    """\n    List user's recordings with automatic organization filtering via RLS\n    Native Supabase implementation with pagination\n    """\n    try:\n        supabase = get_supabase_client()\n        \n        # Build base query - RLS automatically filters by organization\n        query = supabase.client.table('recording_sessions').select("*")\n        \n        # Filter by status if provided\n        if status:\n            query = query.eq('status', status)\n        \n        # Get total count for pagination\n        count_result = supabase.client.table('recording_sessions').select("*", count="exact").execute()\n        total = count_result.count if hasattr(count_result, 'count') else 0\n        \n        # Apply pagination and ordering\n        offset = (page - 1) * page_size\n        recordings_result = query.order('created_at', desc=True).range(offset, offset + page_size - 1).execute()\n        \n        recordings = recordings_result.data or []\n        \n        # Build response with analysis status\n        recording_responses = []\n        for recording in recordings:\n            # Check if recording has completed analysis\n            analysis_result = supabase.client.table('analysis_results').select("id").eq('session_id', recording['id']).eq('status', 'completed').execute()\n            has_analysis = len(analysis_result.data or []) > 0\n            \n            # Create response object\n            recording_response = {\n                "id": recording["id"],\n                "user_id": recording["user_id"],\n                "title": recording["title"],\n                "description": recording.get("description"),\n                "status": recording["status"],\n                "duration_seconds": recording.get("duration_seconds", 0),\n                "file_size_bytes": recording.get("file_size_bytes", 0),\n                "workflow_type": recording.get("workflow_type"),\n                "privacy_settings": recording.get("privacy_settings", {}),\n                "recording_metadata": recording.get("recording_metadata", {}),\n                "analysis_cost": float(recording.get("analysis_cost", 0)),\n                "created_at": recording["created_at"],\n                "completed_at": recording.get("completed_at"),\n                "updated_at": recording["updated_at"],\n                "has_analysis": has_analysis\n            }\n            recording_responses.append(recording_response)\n        \n        return {\n            "recordings": recording_responses,\n            "total": total,\n            "page": page,\n            "page_size": page_size,\n            "has_more": offset + page_size < total\n        }\n        \n    except Exception as e:\n        logger.error(f"Error listing recordings: {e}")\n        raise HTTPException(\n            status_code=500,\n            detail=f"Failed to list recordings: {str(e)}"\n        )\n\n@router.get("/{recording_id}")\nasync def get_recording(\n    recording_id: UUID,\n    include_chunks: bool = False,\n    current_user: Dict[str, Any] = Depends(get_current_user_from_token)\n):\n    """\n    Get recording details with optional chunk information\n    RLS policies automatically handle access control\n    """\n    try:\n        supabase = get_supabase_client()\n        \n        # Query for recording - RLS automatically filters by organization\n        recording_result = supabase.client.table('recording_sessions').select("*").eq('id', str(recording_id)).single().execute()\n        \n        if not recording_result.data:\n            raise HTTPException(status_code=404, detail="Recording not found")\n        \n        recording = recording_result.data\n        \n        # Build response\n        response = {\n            "id": recording["id"],\n            "user_id": recording["user_id"],\n            "title": recording["title"],\n            "description": recording.get("description"),\n            "status": recording["status"],\n            "duration_seconds": recording.get("duration_seconds", 0),\n            "file_size_bytes": recording.get("file_size_bytes", 0),\n            "workflow_type": recording.get("workflow_type"),\n            "privacy_settings": recording.get("privacy_settings", {}),\n            "recording_metadata": recording.get("recording_metadata", {}),\n            "analysis_cost": float(recording.get("analysis_cost", 0)),\n            "created_at": recording["created_at"],\n            "completed_at": recording.get("completed_at"),\n            "updated_at": recording["updated_at"]\n        }\n        \n        # Include video chunks if requested\n        if include_chunks:\n            chunks_result = supabase.client.table('video_chunks').select("*").eq('session_id', str(recording_id)).order('chunk_index').execute()\n            response["video_chunks"] = chunks_result.data or []\n        \n        return response\n        \n    except HTTPException:\n        raise\n    except Exception as e:\n        logger.error(f"Error getting recording: {e}")\n        raise HTTPException(\n            status_code=500,\n            detail=f"Failed to get recording: {str(e)}"\n        )\n\n@router.delete("/{recording_id}")\nasync def delete_recording(\n    recording_id: UUID,\n    current_user: Dict[str, Any] = Depends(get_current_user_from_token)\n):\n    """\n    Delete a recording with automatic cascade deletion via RLS\n    Native Supabase implementation with storage cleanup\n    """\n    try:\n        supabase = get_supabase_client()\n        \n        # Verify recording exists and user has access\n        recording_result = supabase.client.table('recording_sessions').select("*").eq('id', str(recording_id)).single().execute()\n        \n        if not recording_result.data:\n            raise HTTPException(status_code=404, detail="Recording not found")\n        \n        logger.info(f"Deleting recording {recording_id}")\n        \n        # Delete files from storage\n        storage_deleted = await supabase.delete_recording_files(recording_id)\n        \n        if not storage_deleted:\n            logger.warning(f"Failed to delete storage files for recording {recording_id}")\n        \n        # Delete from database - cascade will handle related records\n        delete_result = supabase.client.table('recording_sessions').delete().eq('id', str(recording_id)).execute()\n        \n        if not delete_result.data:\n            raise HTTPException(status_code=500, detail="Failed to delete recording from database")\n        \n        logger.info(f"Recording {recording_id} deleted successfully")\n        \n        return {"message": "Recording deleted successfully"}\n        \n    except HTTPException:\n        raise\n    except Exception as e:\n        logger.error(f"Error deleting recording: {e}")\n        raise HTTPException(\n            status_code=500,\n            detail=f"Failed to delete recording: {str(e)}"\n        )\n\n@router.put("/{recording_id}/privacy")\nasync def update_privacy_settings(\n    recording_id: UUID,\n    privacy_settings: Dict[str, Any],\n    current_user: Dict[str, Any] = Depends(get_current_user_from_token)\n):\n    """\n    Update privacy settings for recording\n    RLS policies ensure users can only update their organization's recordings\n    """\n    try:\n        supabase = get_supabase_client()\n        \n        # Verify recording exists and user has access\n        recording_result = supabase.client.table('recording_sessions').select("*").eq('id', str(recording_id)).single().execute()\n        \n        if not recording_result.data:\n            raise HTTPException(status_code=404, detail="Recording not found")\n        \n        recording = recording_result.data\n        \n        # Update privacy settings\n        current_privacy = recording.get("privacy_settings", {})\n        current_privacy.update(privacy_settings)\n        \n        update_data = {\n            "privacy_settings": current_privacy,\n            "updated_at": datetime.now(timezone.utc).isoformat()\n        }\n        \n        update_result = supabase.client.table('recording_sessions').update(update_data).eq('id', str(recording_id)).execute()\n        \n        if not update_result.data:\n            raise HTTPException(status_code=500, detail="Failed to update privacy settings")\n        \n        logger.info(f"Privacy settings updated for recording {recording_id}")\n        \n        return {"message": "Privacy settings updated successfully"}\n        \n    except HTTPException:\n        raise\n    except Exception as e:\n        logger.error(f"Error updating privacy settings: {e}")\n        raise HTTPException(\n            status_code=500,\n            detail=f"Failed to update privacy settings: {str(e)}"\n        )\n\n# ============================================\n# BACKGROUND TASKS\n# ============================================\n\nasync def queue_recording_analysis(recording_id: str):\n    """\n    Background task to queue analysis for completed recording\n    Calls the analysis start endpoint to begin GPT-4V processing\n    """\n    try:\n        logger.info(f"Starting background analysis for recording {recording_id}")\n        \n        # Call the analysis start endpoint internally\n        async with httpx.AsyncClient() as client:\n            response = await client.post(\n                f"{settings.API_BASE_URL}/api/v1/analysis/{recording_id}/start",\n                json={"analysis_type": "natural"},\n                timeout=300.0\n            )\n            \n            if response.status_code == 200:\n                result = response.json()\n                logger.info(f"Analysis queued successfully for recording {recording_id}: {result.get('id')}")\n            else:\n                logger.error(f"Failed to start analysis for recording {recording_id}: {response.status_code} - {response.text}")\n                \n    except httpx.ReadTimeout:\n        logger.error(f"Analysis timeout for recording {recording_id} - GPT-4V took longer than 5 minutes")\n    except Exception as e:\n        logger.error(f"Background analysis task failed for recording {recording_id}: {e}", exc_info=True)