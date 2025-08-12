"""
Frame Extraction Service for GPT-4V Analysis
Extracts strategic frames from screen recordings for cost-effective AI analysis
Pragmatic MVP approach: 10-15 frames per recording
"""

import cv2
import subprocess
import numpy as np
from PIL import Image
import io
import base64
import tempfile
import os
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID
import logging
from pathlib import Path
import requests
from datetime import datetime

from app.core.config import settings
from app.services.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)


class FrameExtractor:
    """
    Extracts key frames from screen recordings for GPT-4V analysis
    Optimized for logistics workflows (email → WMS data entry patterns)
    """
    
    def __init__(self):
        self.supabase = get_supabase_client()
        self.temp_dir = Path(tempfile.gettempdir()) / "newsystem_frames"
        self.temp_dir.mkdir(exist_ok=True)
        
        # Frame extraction settings (optimized for comprehensive analysis)
        if settings.FRAME_EXTRACTION_MODE == "testing":
            # Aggressive extraction for testing
            self.target_frames = 50  # High frame count for detailed analysis
            self.max_frames = 60  # Maximum for comprehensive coverage
            self.min_scene_change_threshold = 0.2  # More sensitive to changes
        else:
            # Production settings (cost-optimized)
            self.target_frames = 20  # Balanced frame count
            self.max_frames = 30  # Moderate maximum
            self.min_scene_change_threshold = 0.3  # Standard sensitivity
            
        self.jpeg_quality = 85  # Balance quality vs size for GPT-4V
        
    async def extract_frames_from_recording(
        self,
        session_id: UUID,
        recording_duration_seconds: int,
        extraction_settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Main entry point: Extract strategic frames from a recording session
        
        Args:
            session_id: Recording session ID
            recording_duration_seconds: Total duration of recording
            
        Returns:
            Dict with extracted frames data and metadata
        """
        try:
            logger.info(f"Starting frame extraction for session {session_id}")
            
            # Step 1: Download video from Supabase
            video_path = await self._download_recording(session_id)
            if not video_path:
                raise ValueError(f"Failed to download recording for session {session_id}")
            
            # Step 2: Calculate frame extraction strategy
            extraction_strategy = self._calculate_extraction_strategy(
                recording_duration_seconds,
                extraction_settings
            )
            
            # Step 3: Extract frames with smart selection
            frames_data = await self._extract_frames_smart(
                video_path,
                extraction_strategy
            )
            
            # Step 4: Clean up temporary video file
            try:
                os.remove(video_path)
            except Exception as e:
                logger.warning(f"Failed to clean up video file: {e}")
            
            # Step 5: Prepare response with frame data and cost analysis
            estimated_cost = len(frames_data) * settings.COST_PER_GPT4V_REQUEST
            cost_warning = None
            
            if len(frames_data) > 40:
                cost_warning = f"High frame count ({len(frames_data)} frames) will result in higher analysis costs (~${estimated_cost:.2f})"
            elif len(frames_data) > 20:
                cost_warning = f"Moderate frame count ({len(frames_data)} frames) - estimated cost: ~${estimated_cost:.2f}"
            
            result = {
                "session_id": str(session_id),
                "frame_count": len(frames_data),
                "extraction_strategy": extraction_strategy,
                "frames": frames_data,
                "estimated_gpt4v_cost": estimated_cost,
                "cost_warning": cost_warning,
                "extraction_mode": settings.FRAME_EXTRACTION_MODE,
                "extraction_timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Extracted {len(frames_data)} frames for session {session_id}")
            return result
            
        except Exception as e:
            logger.error(f"Frame extraction failed for session {session_id}: {e}")
            return {
                "session_id": str(session_id),
                "error": str(e),
                "frame_count": 0,
                "frames": []
            }
    
    async def _download_recording(self, session_id: UUID) -> Optional[str]:
        """
        Download recording from Supabase storage to temporary file
        Downloads all chunks and concatenates them into a single video
        
        Args:
            session_id: Recording session ID
            
        Returns:
            Path to downloaded video file or None if failed
        """
        try:
            # List all chunks for this recording session
            chunk_files = []
            
            # Try to list files in the recording directory
            logger.info(f"Looking for chunks for session {session_id}")
            
            # Download chunks (try up to 100 chunks)
            for i in range(100):
                file_path = f"recordings/{session_id}/chunks/chunk_{i:04d}.webm"
                
                try:
                    # Try to get a signed URL for this chunk
                    result = self.supabase.client.storage.from_(settings.SUPABASE_STORAGE_BUCKET).create_signed_url(file_path, 60)
                    if result and 'signedURL' in result:
                        download_url = result['signedURL']
                    else:
                        # Fallback to public URL
                        download_url = self.supabase.get_public_url(file_path)
                        if not download_url:
                            break  # No more chunks
                    
                    # Download chunk to temporary file
                    temp_chunk_path = self.temp_dir / f"{session_id}_chunk_{i:04d}.webm"
                    
                    response = requests.get(download_url, stream=True)
                    if response.status_code == 404:
                        logger.info(f"No more chunks found at index {i}")
                        break  # No more chunks
                    
                    response.raise_for_status()
                    
                    # Write chunk to temporary file
                    with open(temp_chunk_path, 'wb') as f:
                        for data in response.iter_content(chunk_size=8192):
                            f.write(data)
                    
                    chunk_files.append(str(temp_chunk_path))
                    logger.info(f"Downloaded chunk {i} to {temp_chunk_path}")
                    
                except Exception as e:
                    if i == 0:
                        logger.error(f"Failed to download first chunk: {e}")
                        return None
                    else:
                        logger.info(f"Finished downloading chunks at index {i-1}")
                        break
            
            if not chunk_files:
                logger.error("No chunks found for recording")
                return None
            
            logger.info(f"Downloaded {len(chunk_files)} chunks")
            
            # If only one chunk, return it directly
            if len(chunk_files) == 1:
                return chunk_files[0]
            
            # Concatenate chunks using ffmpeg
            output_path = self.temp_dir / f"{session_id}_recording.webm"
            
            # Create a file list for ffmpeg concat
            list_file = self.temp_dir / f"{session_id}_chunks.txt"
            with open(list_file, 'w') as f:
                for chunk_file in chunk_files:
                    f.write(f"file '{chunk_file}'\n")
            
            logger.info(f"Concatenating {len(chunk_files)} chunks using ffmpeg")
            
            # Use ffmpeg to concatenate chunks
            cmd = [
                'ffmpeg', '-f', 'concat', '-safe', '0',
                '-i', str(list_file),
                '-c', 'copy',  # Copy without re-encoding
                '-y',  # Overwrite output
                str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                logger.error(f"ffmpeg concatenation failed: {result.stderr}")
                # If concat fails, try just using the first chunk
                logger.warning("Falling back to first chunk only")
                return chunk_files[0]
            
            # Clean up individual chunks
            for chunk_file in chunk_files:
                try:
                    Path(chunk_file).unlink()
                except:
                    pass
            
            logger.info(f"Successfully concatenated recording to {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Failed to download recording: {e}")
            return None
    
    def _calculate_extraction_strategy(
        self,
        duration_seconds: int,
        extraction_settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate smart frame extraction strategy based on recording duration
        Pragmatic approach for MVP: Simple interval-based extraction
        
        Args:
            duration_seconds: Recording duration
            
        Returns:
            Strategy configuration dict
        """
        # Use custom settings if provided, otherwise use defaults/presets
        if extraction_settings:
            # Custom settings from API request
            frames_per_second = extraction_settings.get('fps', settings.DEFAULT_FRAMES_PER_SECOND)
            max_frames = extraction_settings.get('max_frames', settings.DEFAULT_MAX_FRAMES_PER_VIDEO)
            scene_threshold = extraction_settings.get('scene_threshold', settings.DEFAULT_SCENE_CHANGE_THRESHOLD)
        elif settings.FRAME_EXTRACTION_MODE == "testing":
            # Standard testing mode: 1 FPS
            frames_per_second = settings.DEFAULT_FRAMES_PER_SECOND  # 1.0 FPS
            max_frames = settings.DEFAULT_MAX_FRAMES_PER_VIDEO  # 120 frames
            scene_threshold = settings.DEFAULT_SCENE_CHANGE_THRESHOLD  # 0.2
        else:
            # Production mode: use quick preset
            preset = settings.FRAME_EXTRACTION_PRESETS["quick"]
            frames_per_second = preset["fps"]
            max_frames = preset["max_frames"]
            scene_threshold = preset["scene_threshold"]
        
        # Calculate interval and target frames
        interval_seconds = 1.0 / frames_per_second
        target_frames = min(max_frames, int(duration_seconds * frames_per_second))
        
        # Update instance scene change threshold for this extraction
        self.min_scene_change_threshold = scene_threshold
        
        return {
            "method": "interval_based",
            "interval_seconds": interval_seconds,
            "frames_per_second": frames_per_second,
            "target_frames": max(5, target_frames),  # Minimum 5 frames
            "max_frames": max_frames,
            "scene_threshold": scene_threshold,
            "duration_seconds": duration_seconds,
            "scene_detection": False,  # DISABLED - scene detection filters out too many frames from UI recordings
            "focus_areas": ["email_interface", "wms_forms", "data_entry"],  # Logistics focus
            "extraction_mode": settings.FRAME_EXTRACTION_MODE,
            "estimated_frame_count": target_frames,
            "estimated_cost": target_frames * settings.COST_PER_GPT4V_REQUEST
        }
    
    def _convert_webm_if_needed(self, video_path: str) -> str:
        """
        Convert WebM to MP4 if OpenCV can't handle it
        
        Args:
            video_path: Path to video file
            
        Returns:
            Path to video file (converted if necessary)
        """
        # Try to open with OpenCV first
        cap = cv2.VideoCapture(video_path)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        cap.release()
        
        if frame_count > 0:
            # OpenCV can handle it
            return video_path
        
        # Need to convert with ffmpeg
        logger.info("Converting WebM to MP4 for better compatibility")
        mp4_path = video_path.replace('.webm', '.mp4')
        
        try:
            # Use ffmpeg to convert
            cmd = [
                'ffmpeg', '-i', video_path,
                '-c:v', 'libx264',  # Use H.264 codec
                '-preset', 'ultrafast',  # Fast conversion
                '-y',  # Overwrite output
                mp4_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info("Successfully converted WebM to MP4")
                return mp4_path
            else:
                logger.warning(f"ffmpeg conversion failed: {result.stderr}")
                return video_path  # Try with original
                
        except Exception as e:
            logger.warning(f"Failed to convert video: {e}")
            return video_path  # Try with original
    
    async def _extract_frames_smart(
        self,
        video_path: str,
        strategy: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Extract frames using smart selection strategy
        
        Args:
            video_path: Path to video file
            strategy: Extraction strategy configuration
            
        Returns:
            List of frame data dictionaries
        """
        # Convert WebM if needed
        video_path = self._convert_webm_if_needed(video_path)
        
        frames_data = []
        cap = cv2.VideoCapture(video_path)
        
        try:
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            if fps <= 0 or fps > 120:  # Validate FPS is reasonable
                logger.warning(f"Invalid FPS detected: {fps}, using fallback calculation")
                fps = 30  # Assume standard 30 FPS for screen recordings
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            if total_frames == 0:
                logger.error("Video has no frames")
                return []
            
            # Calculate actual video duration
            video_duration = total_frames / fps
            logger.info(f"Video properties: {total_frames} frames @ {fps:.1f} FPS = {video_duration:.1f}s duration")
            
            # Calculate frame indices to extract based on time intervals
            interval_seconds = strategy["interval_seconds"]
            target_frames = strategy["target_frames"]
            
            # Generate frame indices based on time intervals
            frame_indices = []
            for i in range(target_frames):
                time_position = i * interval_seconds
                if time_position >= video_duration:
                    break
                frame_index = int(time_position * fps)
                if frame_index < total_frames:
                    frame_indices.append(frame_index)
            
            logger.info(f"Calculated {len(frame_indices)} frame indices for extraction")
            
            # Extract frames at calculated indices
            prev_frame = None
            for idx, frame_idx in enumerate(frame_indices):
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if not ret:
                    logger.warning(f"Failed to read frame at index {frame_idx}")
                    continue
                
                # Basic scene change detection (optional for MVP)
                if strategy.get("scene_detection") and prev_frame is not None:
                    change_ratio = self._calculate_scene_change(prev_frame, frame)
                    if change_ratio < self.min_scene_change_threshold:
                        logger.debug(f"Skipping frame {frame_idx} - minimal scene change")
                        continue
                
                # Convert frame to base64 for GPT-4V
                frame_data = self._prepare_frame_for_gpt4v(
                    frame,
                    frame_idx,
                    fps,
                    idx
                )
                frames_data.append(frame_data)
                
                prev_frame = frame.copy()
                
                # Limit to max frames for cost control
                if len(frames_data) >= self.max_frames:
                    logger.info(f"Reached maximum frame limit ({self.max_frames})")
                    break
            
            logger.info(f"Extracted {len(frames_data)} frames from {len(frame_indices)} candidates")
            
            # Validate extraction performance
            expected_frames = min(strategy["target_frames"], int(video_duration))
            extraction_rate = len(frames_data) / expected_frames if expected_frames > 0 else 0
            
            if extraction_rate < 0.5:  # Less than 50% of expected frames
                logger.error(f"CRITICAL: Frame extraction underperformed! Got {len(frames_data)}/{expected_frames} frames ({extraction_rate:.1%})")
                logger.error(f"Video duration: {video_duration:.1f}s, Target FPS: {strategy['frames_per_second']}, Interval: {interval_seconds}s")
            elif extraction_rate < 0.8:  # Less than 80% of expected frames
                logger.warning(f"Frame extraction below target: {len(frames_data)}/{expected_frames} frames ({extraction_rate:.1%})")
            else:
                logger.info(f"Frame extraction successful: {len(frames_data)}/{expected_frames} frames ({extraction_rate:.1%})")
            
        finally:
            cap.release()
        
        return frames_data
    
    def _calculate_scene_change(
        self,
        prev_frame: np.ndarray,
        curr_frame: np.ndarray
    ) -> float:
        """
        Calculate scene change ratio between two frames
        Simple approach for MVP: Compare histogram differences
        
        Args:
            prev_frame: Previous frame
            curr_frame: Current frame
            
        Returns:
            Change ratio (0.0 = identical, 1.0 = completely different)
        """
        try:
            # Convert to grayscale for simpler comparison
            prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
            curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
            
            # Calculate histogram for both frames
            prev_hist = cv2.calcHist([prev_gray], [0], None, [256], [0, 256])
            curr_hist = cv2.calcHist([curr_gray], [0], None, [256], [0, 256])
            
            # Normalize histograms
            prev_hist = cv2.normalize(prev_hist, prev_hist).flatten()
            curr_hist = cv2.normalize(curr_hist, curr_hist).flatten()
            
            # Calculate correlation (1.0 = identical, -1.0 = opposite)
            correlation = cv2.compareHist(prev_hist, curr_hist, cv2.HISTCMP_CORREL)
            
            # Convert to change ratio (0.0 = identical, 1.0 = different)
            change_ratio = 1.0 - max(0, correlation)
            
            return change_ratio
            
        except Exception as e:
            logger.warning(f"Scene change calculation failed: {e}")
            return 1.0  # Assume frames are different on error
    
    def _prepare_frame_for_gpt4v(
        self,
        frame: np.ndarray,
        frame_index: int,
        fps: float,
        sequence_number: int
    ) -> Dict[str, Any]:
        """
        Prepare frame for GPT-4V analysis
        
        Args:
            frame: OpenCV frame (BGR format)
            frame_index: Frame index in video
            fps: Video FPS
            sequence_number: Sequential number in extracted frames
            
        Returns:
            Frame data dictionary with base64 image and metadata
        """
        try:
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Convert to PIL Image
            pil_image = Image.fromarray(frame_rgb)
            
            # Resize if too large (GPT-4V has size limits)
            max_dimension = 2048
            if pil_image.width > max_dimension or pil_image.height > max_dimension:
                pil_image.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
            
            # Convert to JPEG with optimized quality
            buffer = io.BytesIO()
            pil_image.save(buffer, format="JPEG", quality=self.jpeg_quality, optimize=True)
            
            # Encode to base64
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            # Calculate timestamp
            timestamp_seconds = frame_index / fps if fps > 0 else 0
            
            return {
                "sequence_number": sequence_number,
                "frame_index": frame_index,
                "timestamp_seconds": round(timestamp_seconds, 2),
                "timestamp_formatted": self._format_timestamp(timestamp_seconds),
                "image_base64": image_base64,
                "image_format": "jpeg",
                "dimensions": {
                    "width": pil_image.width,
                    "height": pil_image.height
                },
                "size_bytes": len(buffer.getvalue()),
                "extraction_metadata": {
                    "method": "interval_based",
                    "quality": self.jpeg_quality,
                    "resized": pil_image.width < frame.shape[1] or pil_image.height < frame.shape[0]
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to prepare frame for GPT-4V: {e}")
            raise
    
    def _format_timestamp(self, seconds: float) -> str:
        """
        Format timestamp as MM:SS
        
        Args:
            seconds: Timestamp in seconds
            
        Returns:
            Formatted timestamp string
        """
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
    
    def cleanup_temp_files(self, session_id: Optional[UUID] = None):
        """
        Clean up temporary files
        
        Args:
            session_id: If provided, only clean files for this session
        """
        try:
            if session_id:
                # Clean specific session files
                pattern = f"{session_id}*"
                for file in self.temp_dir.glob(pattern):
                    try:
                        file.unlink()
                        logger.debug(f"Cleaned up {file}")
                    except Exception as e:
                        logger.warning(f"Failed to delete {file}: {e}")
            else:
                # Clean all old files (older than 1 hour)
                from datetime import datetime, timedelta
                cutoff_time = datetime.now().timestamp() - 3600  # 1 hour ago
                
                for file in self.temp_dir.iterdir():
                    if file.stat().st_mtime < cutoff_time:
                        try:
                            file.unlink()
                            logger.debug(f"Cleaned up old file {file}")
                        except Exception as e:
                            logger.warning(f"Failed to delete {file}: {e}")
                            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")


# Singleton instance
_frame_extractor: Optional[FrameExtractor] = None

def get_frame_extractor() -> FrameExtractor:
    """Get singleton frame extractor instance"""
    global _frame_extractor
    if _frame_extractor is None:
        _frame_extractor = FrameExtractor()
    return _frame_extractor