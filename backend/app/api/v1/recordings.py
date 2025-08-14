"""
Recording management endpoints for NewSystem.AI
Handles screen recording lifecycle: start, upload chunks, complete
Focus: General workflow capture for business operations
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, File, UploadFile
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
import logging

from app.core.database import get_db
from app.models.database import RecordingSession, VideoChunk, AnalysisResult
from app.schemas.recording import (
    RecordingStartRequest, RecordingStartResponse,
    VideoChunkUploadRequest, ChunkUploadResponse,
    RecordingCompleteRequest, RecordingCompleteResponse,
    RecordingResponse, RecordingListResponse,
    RecordingError
)
from app.services.supabase_client import get_supabase_client
from app.core.config import settings
import asyncio
import httpx

logger = logging.getLogger(__name__)
router = APIRouter()

# Mock user authentication for MVP (replace with proper auth in production)
async def get_current_user_id() -> UUID:
    """Mock user authentication - replace with proper Supabase auth"""
    # For MVP, return a fixed user ID
    # In production, this would extract user ID from JWT token
    return UUID("00000000-0000-0000-0000-000000000001")

@router.post("/start", response_model=RecordingStartResponse)
async def start_recording(
    request: RecordingStartRequest,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    """
    Start a new screen recording session
    Week 1 Implementation: Core recording infrastructure with database
    """
    try:
        logger.info(f"Starting recording for user {user_id}")
        
        # Create new recording session
        recording = RecordingSession(
            id=uuid4(),
            user_id=user_id,
            title=request.title,
            description=request.description,
            workflow_type=request.workflow_type,
            status="recording",
            privacy_settings=request.privacy_settings.dict(),
            recording_metadata=request.metadata
        )
        
        db.add(recording)
        db.commit()
        db.refresh(recording)
        
        logger.info(f"Recording session created: {recording.id}")
        
        # Get Supabase client for upload URL generation
        supabase_client = get_supabase_client()
        
        return RecordingStartResponse(
            id=recording.id,
            status="recording",
            message="Recording session started successfully",
            chunk_settings={
                "chunk_size_seconds": settings.CHUNK_SIZE_SECONDS,
                "max_file_size_mb": settings.MAX_FILE_SIZE_MB,
                "allowed_formats": settings.ALLOWED_VIDEO_FORMATS,
                "recording_fps": settings.RECORDING_FPS
            }
        )
        
    except Exception as e:
        logger.error(f"Error starting recording: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start recording session: {str(e)}"
        )

@router.post("/{recording_id}/chunks/signed-url")
async def get_chunk_signed_url(
    recording_id: UUID,
    chunk_index: int,
    expires_in: int = 3600,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    """
    Get a signed URL for direct chunk upload to Supabase Storage
    Week 1 Day 2: Direct storage optimization
    """
    try:
        # Verify recording session exists and belongs to user
        recording = db.query(RecordingSession).filter(
            RecordingSession.id == recording_id,
            RecordingSession.user_id == user_id
        ).first()
        
        if not recording:
            raise HTTPException(status_code=404, detail="Recording session not found")
        
        if recording.status != "recording":
            raise HTTPException(status_code=400, detail="Recording session is not active")
        
        logger.info(f"Generating signed URL for chunk {chunk_index} of recording {recording_id}")
        
        # Get Supabase client and create signed URL
        supabase_client = get_supabase_client()
        signed_url_info = supabase_client.create_chunk_signed_url(
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
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    """
    Verify that a chunk was successfully uploaded via signed URL
    Week 1 Day 2: Upload verification for direct storage
    """
    try:
        # Verify recording session exists and belongs to user
        recording = db.query(RecordingSession).filter(
            RecordingSession.id == recording_id,
            RecordingSession.user_id == user_id
        ).first()
        
        if not recording:
            raise HTTPException(status_code=404, detail="Recording session not found")
        
        logger.info(f"Verifying chunk {chunk_index} for recording {recording_id}")
        
        # Verify chunk in Supabase Storage
        supabase_client = get_supabase_client()
        verification_result = await supabase_client.verify_chunk_upload(
            session_id=recording_id,
            chunk_index=chunk_index
        )
        
        if verification_result["exists"]:
            # Update or create video chunk record in database
            chunk_record = db.query(VideoChunk).filter(
                VideoChunk.session_id == recording_id,
                VideoChunk.chunk_index == chunk_index
            ).first()
            
            if chunk_record:
                # Update existing chunk
                chunk_record.file_path = verification_result["file_path"]
                chunk_record.file_size_bytes = verification_result.get("size", 0)
                chunk_record.upload_status = "completed"
                chunk_record.uploaded_at = datetime.now(timezone.utc)
            else:
                # Create new chunk record
                chunk_record = VideoChunk(
                    session_id=recording_id,
                    chunk_index=chunk_index,
                    file_path=verification_result["file_path"],
                    file_size_bytes=verification_result.get("size", 0),
                    upload_status="completed",
                    uploaded_at=datetime.now(timezone.utc)
                )
                db.add(chunk_record)
            
            db.commit()
            db.refresh(chunk_record)
            
            return {
                "verified": True,
                "chunk_id": chunk_record.id,
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
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    """
    Upload video chunks during recording
    Week 1 Implementation: Chunked upload system (5-second chunks)
    """
    try:
        # Verify recording session exists and belongs to user
        recording = db.query(RecordingSession).filter(
            RecordingSession.id == recording_id,
            RecordingSession.user_id == user_id
        ).first()
        
        if not recording:
            raise HTTPException(status_code=404, detail="Recording session not found")
        
        if recording.status != "recording":
            raise HTTPException(status_code=400, detail="Recording session is not active")
        
        logger.info(f"Uploading chunk {chunk_index} for recording {recording_id}")
        
        # Read file content
        file_content = await chunk_file.read()
        file_size = len(file_content)
        
        # Upload to Supabase Storage
        supabase_client = get_supabase_client()
        upload_result = await supabase_client.upload_video_chunk(
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
        chunk_record = db.query(VideoChunk).filter(
            VideoChunk.session_id == recording_id,
            VideoChunk.chunk_index == chunk_index
        ).first()
        
        if chunk_record:
            # Update existing chunk - this handles retry scenarios
            logger.info(f"Updating existing chunk record {chunk_index} for session {recording_id}")
            chunk_record.file_path = upload_result["file_path"]
            chunk_record.file_size_bytes = file_size
            chunk_record.upload_status = "completed"
            chunk_record.uploaded_at = datetime.now(timezone.utc)
            chunk_record.error_message = None  # Clear any previous error
        else:
            # Create new chunk record
            logger.info(f"Creating new chunk record {chunk_index} for session {recording_id}")
            chunk_record = VideoChunk(
                session_id=recording_id,
                chunk_index=chunk_index,
                file_path=upload_result["file_path"],
                file_size_bytes=file_size,
                upload_status="completed",
                uploaded_at=datetime.now(timezone.utc)
            )
            db.add(chunk_record)
        
        try:
            db.commit()
            db.refresh(chunk_record)
        except Exception as commit_error:
            logger.error(f"Database commit error: {commit_error}")
            db.rollback()
            
            # Try to find the existing record in case of race condition
            existing_chunk = db.query(VideoChunk).filter(
                VideoChunk.session_id == recording_id,
                VideoChunk.chunk_index == chunk_index
            ).first()
            
            if existing_chunk:
                logger.info(f"Found existing chunk record after commit error - using it")
                chunk_record = existing_chunk
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to save chunk record: {str(commit_error)}"
                )
        
        logger.info(f"Chunk {chunk_index} uploaded successfully for recording {recording_id}")
        
        return ChunkUploadResponse(
            chunk_id=chunk_record.id,
            status="completed",
            message="Chunk uploaded successfully",
            next_chunk_index=chunk_index + 1
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading chunk: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload chunk: {str(e)}"
        )

@router.post("/{recording_id}/complete", response_model=RecordingCompleteResponse)
async def complete_recording(
    recording_id: UUID,
    request: RecordingCompleteRequest,
    background_tasks: BackgroundTasks,  # Will be used in Week 2 for analysis
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    """
    Mark recording as complete and trigger analysis
    Week 1 Implementation: Recording completion with background task queue
    """
    try:
        # Verify recording session exists and belongs to user
        recording = db.query(RecordingSession).filter(
            RecordingSession.id == recording_id,
            RecordingSession.user_id == user_id
        ).first()
        
        if not recording:
            raise HTTPException(status_code=404, detail="Recording session not found")
        
        if recording.status != "recording":
            raise HTTPException(status_code=400, detail="Recording is not in recording state")
        
        logger.info(f"Completing recording {recording_id}")
        
        # Update recording with completion data
        recording.status = "completed"
        recording.duration_seconds = request.duration_seconds
        recording.file_size_bytes = request.total_file_size_bytes
        recording.completed_at = datetime.now(timezone.utc)
        recording.updated_at = datetime.now(timezone.utc)
        
        # Update metadata
        recording.recording_metadata.update(request.metadata)
        recording.recording_metadata.update({
            "chunk_count": request.chunk_count,
            "completion_time": datetime.now(timezone.utc).isoformat()
        })
        
        db.commit()
        db.refresh(recording)
        
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
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to complete recording: {str(e)}"
        )

@router.get("/", response_model=RecordingListResponse)
async def list_recordings(
    page: int = 1,
    page_size: int = 10,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    """
    List user's recordings
    Week 1 Implementation: Basic CRUD operations with pagination
    """
    try:
        # Build query
        query = db.query(RecordingSession).filter(RecordingSession.user_id == user_id)
        
        # Filter by status if provided
        if status:
            query = query.filter(RecordingSession.status == status)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * page_size
        recordings = query.order_by(RecordingSession.created_at.desc()).offset(offset).limit(page_size).all()
        
        # Build response with analysis status
        recording_responses = []
        for recording in recordings:
            # Check if recording has completed analysis
            analysis_exists = db.query(AnalysisResult).filter(
                AnalysisResult.session_id == str(recording.id),
                AnalysisResult.status == "completed"
            ).first() is not None
            
            # Create response object
            recording_response = RecordingResponse.from_orm(recording)
            recording_response.has_analysis = analysis_exists
            recording_responses.append(recording_response)
        
        return RecordingListResponse(
            recordings=recording_responses,
            total=total,
            page=page,
            page_size=page_size,
            has_more=offset + page_size < total
        )
        
    except Exception as e:
        logger.error(f"Error listing recordings: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list recordings: {str(e)}"
        )

@router.get("/{recording_id}", response_model=RecordingResponse)
async def get_recording(
    recording_id: UUID,
    include_chunks: bool = False,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    """
    Get recording details
    Week 1 Implementation: Recording metadata retrieval with optional chunk details
    """
    try:
        # Query for recording
        query = db.query(RecordingSession).filter(
            RecordingSession.id == recording_id,
            RecordingSession.user_id == user_id
        )
        
        recording = query.first()
        
        if not recording:
            raise HTTPException(status_code=404, detail="Recording not found")
        
        # Convert to response model
        response = RecordingResponse.from_orm(recording)
        
        # Include video chunks if requested
        if include_chunks:
            chunks = db.query(VideoChunk).filter(
                VideoChunk.session_id == recording_id
            ).order_by(VideoChunk.chunk_index).all()
            response.video_chunks = chunks
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recording: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get recording: {str(e)}"
        )

@router.delete("/{recording_id}")
async def delete_recording(
    recording_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    """
    Delete a recording
    Week 1 Implementation: Recording cleanup with storage deletion
    """
    try:
        # Verify recording exists and belongs to user
        recording = db.query(RecordingSession).filter(
            RecordingSession.id == recording_id,
            RecordingSession.user_id == user_id
        ).first()
        
        if not recording:
            raise HTTPException(status_code=404, detail="Recording not found")
        
        logger.info(f"Deleting recording {recording_id}")
        
        # Delete files from storage
        supabase_client = get_supabase_client()
        storage_deleted = await supabase_client.delete_recording_files(recording_id)
        
        if not storage_deleted:
            logger.warning(f"Failed to delete storage files for recording {recording_id}")
        
        # Delete from database (cascades to related tables)
        db.delete(recording)
        db.commit()
        
        logger.info(f"Recording {recording_id} deleted successfully")
        
        return {"message": "Recording deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting recording: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete recording: {str(e)}"
        )

@router.put("/{recording_id}/privacy")
async def update_privacy_settings(
    recording_id: UUID,
    privacy_settings: Dict[str, Any],
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    """
    Update privacy settings for recording
    Week 1 Implementation: Privacy controls for logistics operators
    """
    try:
        # Verify recording exists and belongs to user
        recording = db.query(RecordingSession).filter(
            RecordingSession.id == recording_id,
            RecordingSession.user_id == user_id
        ).first()
        
        if not recording:
            raise HTTPException(status_code=404, detail="Recording not found")
        
        # Update privacy settings
        recording.privacy_settings.update(privacy_settings)
        recording.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        
        logger.info(f"Privacy settings updated for recording {recording_id}")
        
        return {"message": "Privacy settings updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating privacy settings: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update privacy settings: {str(e)}"
        )

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
                json={"analysis_type": "natural"},  # Updated to use natural format
                timeout=300.0  # 5 minutes - GPT-4V can take 2-4 minutes for complex analysis
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Analysis queued successfully for recording {recording_id}: {result.get('id')}")
            else:
                logger.error(f"Failed to start analysis for recording {recording_id}: {response.status_code} - {response.text}")
                
    except httpx.ReadTimeout:
        logger.error(f"Analysis timeout for recording {recording_id} - GPT-4V took longer than 5 minutes. Consider reducing frame count or splitting analysis.")
    except Exception as e:
        logger.error(f"Background analysis task failed for recording {recording_id}: {e}", exc_info=True)