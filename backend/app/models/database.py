"""
Database Models for NewSystem.AI
SQLAlchemy models that align with our enhanced Supabase schema
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from sqlalchemy import (
    Boolean, Column, DateTime, Integer, String, Text, 
    DECIMAL, BigInteger, ForeignKey, JSON, ARRAY
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import String as StringType, TypeDecorator
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import os

Base = declarative_base()

# Custom UUID type that works with SQLite
class UUID(TypeDecorator):
    """Platform-independent UUID type for SQLite compatibility"""
    impl = StringType
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(StringType(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        elif dialect.name == 'postgresql':
            return value
        else:
            return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        else:
            if not isinstance(value, uuid4().__class__):
                from uuid import UUID as uuid_class
                return uuid_class(value)
            return value

class Organization(Base):
    """Organization model for multi-tenant support"""
    __tablename__ = "organizations"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    domain = Column(String(255))
    settings = Column(JSON, default=dict)
    subscription_tier = Column(String(50), default="free")
    subscription_status = Column(String(50), default="active")
    max_users = Column(Integer, default=5)
    max_recordings_per_month = Column(Integer, default=50)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user_profiles = relationship("UserProfile", back_populates="organization")

class UserProfile(Base):
    """User profile extending Supabase auth.users"""
    __tablename__ = "user_profiles"
    
    id = Column(UUID, primary_key=True)  # References auth.users(id)
    organization_id = Column(UUID, ForeignKey("organizations.id"))
    role = Column(String(50), default="operator")
    first_name = Column(String(255))
    last_name = Column(String(255))
    job_title = Column(String(255))
    settings = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    organization = relationship("Organization", back_populates="user_profiles")
    # Note: recording_sessions link via user_id to auth.users, not user_profiles

class RecordingSession(Base):
    """Recording session model (enhanced from current schema)"""
    __tablename__ = "recording_sessions"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    user_id = Column(UUID, nullable=False)  # References auth.users(id)
    title = Column(String(255), nullable=False, default="Workflow Recording")
    description = Column(Text)
    status = Column(String(50), nullable=False, default="recording")  # recording, processing, completed, failed
    duration_seconds = Column(Integer, default=0)
    file_size_bytes = Column(BigInteger, default=0)
    analysis_results = Column(JSON, default=dict)
    recording_metadata = Column(JSON, default=dict)
    
    # Enhanced fields from migration
    privacy_settings = Column(JSON, default=lambda: {"blur_passwords": True, "exclude_personal_info": False})
    workflow_type = Column(String(100))
    analysis_cost = Column(DECIMAL(10, 4), default=0.00)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships  
    # Note: user_id references auth.users directly, not user_profiles
    video_chunks = relationship("VideoChunk", back_populates="recording_session")
    workflow_insights = relationship("WorkflowInsight", back_populates="recording_session")
    analysis_results_rel = relationship("AnalysisResult", back_populates="recording_session")

class VideoChunk(Base):
    """Video chunk model for chunked upload system"""
    __tablename__ = "video_chunks"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    session_id = Column(UUID, ForeignKey("recording_sessions.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    file_path = Column(Text)
    file_size_bytes = Column(Integer)
    upload_status = Column(String(50), nullable=False, default="pending")  # pending, uploading, completed, failed
    retry_count = Column(Integer, default=0)
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    uploaded_at = Column(DateTime(timezone=True))
    
    # Relationships
    recording_session = relationship("RecordingSession", back_populates="video_chunks")

class WorkflowInsight(Base):
    """Workflow insights model (existing from current schema)"""
    __tablename__ = "workflow_insights"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    session_id = Column(UUID, ForeignKey("recording_sessions.id"), nullable=False)
    insight_type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    confidence_score = Column(DECIMAL(3, 2), default=0.0)
    time_saved_seconds = Column(Integer, default=0)
    roi_score = Column(DECIMAL(10, 2), default=0.0)
    automation_potential = Column(DECIMAL(3, 2), default=0.0)
    priority = Column(String(50), default="medium")  # low, medium, high, critical
    record_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    recording_session = relationship("RecordingSession", back_populates="workflow_insights")

class AnalysisResult(Base):
    """Enhanced analysis results model"""
    __tablename__ = "analysis_results"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    session_id = Column(UUID, ForeignKey("recording_sessions.id"), nullable=False)
    status = Column(String(50), default="queued")  # queued, processing, completed, failed
    gpt_version = Column(String(50), default="gpt-4-vision-preview")
    processing_started_at = Column(DateTime(timezone=True))
    processing_completed_at = Column(DateTime(timezone=True))
    processing_time_seconds = Column(Integer)
    frames_analyzed = Column(Integer, default=0)
    analysis_cost = Column(DECIMAL(10, 4), default=0.00)
    confidence_score = Column(DECIMAL(3, 2), default=0.00)
    raw_gpt_response = Column(JSON)
    structured_insights = Column(JSON, default=dict)
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    recording_session = relationship("RecordingSession", back_populates="analysis_results_rel")
    automation_opportunities = relationship("AutomationOpportunity", back_populates="analysis_result")
    workflow_visualizations = relationship("WorkflowVisualization", back_populates="analysis_result")
    cost_analyses = relationship("CostAnalysis", back_populates="analysis_result")
    generated_reports = relationship("GeneratedReport", back_populates="analysis_result")

class AutomationOpportunity(Base):
    """Automation opportunities model"""
    __tablename__ = "automation_opportunities"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    analysis_id = Column(UUID, ForeignKey("analysis_results.id"), nullable=False)
    session_id = Column(UUID, ForeignKey("recording_sessions.id"), nullable=False)
    opportunity_type = Column(String(100), nullable=False)  # copy_paste_automation, form_filling, etc.
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    workflow_steps = Column(ARRAY(Text), default=list)
    current_time_per_occurrence_seconds = Column(Integer)
    occurrences_per_day = Column(Integer, default=1)
    automation_complexity = Column(String(50), default="medium")  # low, medium, high
    implementation_effort_hours = Column(Integer)
    estimated_cost_savings_monthly = Column(DECIMAL(10, 2))
    estimated_implementation_cost = Column(DECIMAL(10, 2))
    roi_percentage = Column(DECIMAL(5, 2))
    payback_period_days = Column(Integer)
    confidence_score = Column(DECIMAL(3, 2), default=0.00)
    priority = Column(String(50), default="medium")  # low, medium, high, critical
    record_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    analysis_result = relationship("AnalysisResult", back_populates="automation_opportunities")

class WorkflowVisualization(Base):
    """Workflow visualizations for flow charts"""
    __tablename__ = "workflow_visualizations"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    analysis_id = Column(UUID, ForeignKey("analysis_results.id"), nullable=False)
    session_id = Column(UUID, ForeignKey("recording_sessions.id"), nullable=False)
    visualization_type = Column(String(50), default="flow_chart")
    flow_data = Column(JSON, nullable=False)  # nodes, edges, layout configuration
    layout_algorithm = Column(String(50), default="dagre")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    analysis_result = relationship("AnalysisResult", back_populates="workflow_visualizations")

class CostAnalysis(Base):
    """Cost analysis breakdowns"""
    __tablename__ = "cost_analyses"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    analysis_id = Column(UUID, ForeignKey("analysis_results.id"), nullable=False)
    session_id = Column(UUID, ForeignKey("recording_sessions.id"), nullable=False)
    current_monthly_hours = Column(DECIMAL(8, 2))
    current_hourly_rate = Column(DECIMAL(8, 2), default=25.00)
    current_monthly_cost = Column(DECIMAL(10, 2))
    projected_monthly_hours = Column(DECIMAL(8, 2))
    projected_monthly_cost = Column(DECIMAL(10, 2))
    total_implementation_cost = Column(DECIMAL(10, 2))
    monthly_savings = Column(DECIMAL(10, 2))
    annual_savings = Column(DECIMAL(10, 2))
    payback_period_days = Column(Integer)
    roi_percentage = Column(DECIMAL(5, 2))
    confidence_level = Column(String(50), default="medium")
    assumptions = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    analysis_result = relationship("AnalysisResult", back_populates="cost_analyses")

class GeneratedReport(Base):
    """Generated reports and exports"""
    __tablename__ = "generated_reports"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    analysis_id = Column(UUID, ForeignKey("analysis_results.id"), nullable=False)
    session_id = Column(UUID, ForeignKey("recording_sessions.id"), nullable=False)
    report_type = Column(String(50), nullable=False)  # pdf, excel, shareable_link, json_export
    file_url = Column(Text)
    file_size_bytes = Column(BigInteger)
    access_token = Column(String(255))  # For shareable links
    is_public = Column(Boolean, default=False)
    expires_at = Column(DateTime(timezone=True))
    download_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    analysis_result = relationship("AnalysisResult", back_populates="generated_reports")

# Keep the existing Leads model for compatibility
class Lead(Base):
    """Leads model (preserved from existing schema)"""
    __tablename__ = "leads"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    email = Column(Text, nullable=False, unique=True)
    name = Column(Text)
    company = Column(Text)
    telnr = Column(Text)
    message = Column(Text)
    source = Column(Text, nullable=False, default="website")
    additional_data = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class UseCase(Base):
    """Use cases model (preserved from existing schema)"""
    __tablename__ = "use_cases"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    detailed_description = Column(Text)
    image_url = Column(Text)
    landing_position = Column(Integer, nullable=False, default=0)
    type = Column(Text, nullable=False)  # product, service
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))