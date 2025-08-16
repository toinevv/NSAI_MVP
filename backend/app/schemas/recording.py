"""
Pydantic schemas for recording-related API requests and responses
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
from pydantic import BaseModel, Field

# Base schemas
class RecordingBase(BaseModel):
    title: str = Field(..., description="Recording title")
    description: Optional[str] = Field(None, description="Recording description")
    workflow_type: Optional[str] = Field(None, description="Type of workflow being recorded")

class PrivacySettings(BaseModel):
    blur_passwords: bool = Field(True, description="Blur password fields during recording")
    exclude_personal_info: bool = Field(False, description="Exclude frames with personal information")
    custom_exclusions: List[str] = Field(default_factory=list, description="Custom exclusion patterns")

# Request schemas
class RecordingStartRequest(BaseModel):
    title: str = Field("Workflow Recording", description="Recording title")
    description: Optional[str] = Field(None, description="Recording description")
    workflow_type: Optional[str] = Field(None, description="Type of workflow (e.g., 'data_processing', 'reporting', 'communication')")
    privacy_settings: Optional[PrivacySettings] = Field(
        default_factory=lambda: PrivacySettings(),
        description="Privacy settings for the recording"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional metadata (resolution, user agent, etc.)"
    )

class VideoChunkUploadRequest(BaseModel):
    chunk_index: int = Field(..., description="Index of the chunk (0-based)")
    file_size_bytes: int = Field(..., description="Size of the chunk in bytes")
    file_path: Optional[str] = Field(None, description="Path to the uploaded chunk file")

class RecordingCompleteRequest(BaseModel):
    duration_seconds: int = Field(..., description="Total recording duration in seconds")
    total_file_size_bytes: int = Field(..., description="Total size of all chunks")
    chunk_count: int = Field(..., description="Number of chunks uploaded")
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Final recording metadata"
    )

# Response schemas
class VideoChunkResponse(BaseModel):
    id: UUID
    chunk_index: int
    file_size_bytes: Optional[int]
    upload_status: str
    retry_count: int
    created_at: datetime
    uploaded_at: Optional[datetime]

    class Config:
        from_attributes = True

class RecordingResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    status: str
    duration_seconds: int
    file_size_bytes: int
    workflow_type: Optional[str]
    privacy_settings: Dict[str, Any]
    recording_metadata: Dict[str, Any]
    analysis_cost: float
    created_at: datetime
    completed_at: Optional[datetime]
    updated_at: datetime
    
    # Analysis status
    has_analysis: Optional[bool] = None
    
    # Include related data
    video_chunks: Optional[List[VideoChunkResponse]] = None

    class Config:
        from_attributes = True

class RecordingListResponse(BaseModel):
    recordings: List[RecordingResponse]
    total: int
    page: int = 1
    page_size: int = 10
    has_more: bool = False

class RecordingStartResponse(BaseModel):
    id: UUID
    status: str
    message: str
    upload_url: Optional[str] = None  # For Supabase Storage
    chunk_settings: Dict[str, Any] = Field(
        default_factory=lambda: {
            "chunk_size_seconds": 5,
            "max_file_size_mb": 500,
            "allowed_formats": ["webm", "mp4"]
        }
    )

class ChunkUploadResponse(BaseModel):
    chunk_id: UUID
    status: str
    message: str
    upload_url: Optional[str] = None
    next_chunk_index: int

class RecordingCompleteResponse(BaseModel):
    id: UUID
    status: str
    message: str
    analysis_queued: bool = False
    estimated_processing_time_minutes: int = Field(2, description="Estimated time for analysis")

# Error schemas
class RecordingError(BaseModel):
    error: str
    error_code: str
    details: Optional[Dict[str, Any]] = None

# Status update schemas (for real-time updates)
class RecordingStatusUpdate(BaseModel):
    id: UUID
    status: str
    progress_percentage: Optional[int] = None
    message: Optional[str] = None
    updated_at: datetime

# Analytics schemas (for basic recording metrics)
class RecordingMetrics(BaseModel):
    total_recordings: int
    completed_recordings: int
    processing_recordings: int
    failed_recordings: int
    total_duration_hours: float
    average_duration_minutes: float
    total_storage_gb: float