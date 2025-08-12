#!/usr/bin/env python3
"""
Test Frame Extraction Performance
Verifies that frame extraction is working correctly after fixes
"""

import asyncio
import logging
from pathlib import Path
import sys

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_frame_extraction():
    """Test frame extraction with a sample recording"""
    
    from app.services.analysis.frame_extractor import get_frame_extractor
    from app.core.database import get_sync_db
    from app.models.database import RecordingSession
    from uuid import UUID
    
    # Get a sample recording
    db = get_sync_db()
    sample_recording = db.query(RecordingSession).filter(
        RecordingSession.status == "completed",
        RecordingSession.duration_seconds > 30  # Get a decent length recording
    ).first()
    
    if not sample_recording:
        logger.error("No completed recordings found for testing")
        return
    
    logger.info(f"Testing with recording: {sample_recording.id}")
    logger.info(f"Duration: {sample_recording.duration_seconds}s")
    
    # Initialize frame extractor
    extractor = get_frame_extractor()
    
    # Test extraction with default settings
    logger.info("Starting frame extraction...")
    result = await extractor.extract_frames_from_recording(
        sample_recording.id,
        sample_recording.duration_seconds
    )
    
    if "error" in result:
        logger.error(f"Extraction failed: {result['error']}")
        return
    
    # Analyze results
    frame_count = result.get("frame_count", 0)
    duration = sample_recording.duration_seconds
    expected_frames = min(duration, 120)  # 1 FPS up to max 120
    extraction_rate = frame_count / expected_frames if expected_frames > 0 else 0
    
    logger.info("=" * 60)
    logger.info("EXTRACTION RESULTS:")
    logger.info(f"Recording Duration: {duration}s")
    logger.info(f"Frames Extracted: {frame_count}")
    logger.info(f"Expected Frames (1 FPS): {expected_frames}")
    logger.info(f"Extraction Rate: {extraction_rate:.1%}")
    logger.info(f"Actual FPS: {frame_count/duration:.3f}")
    logger.info(f"Estimated Cost: ${result.get('estimated_gpt4v_cost', 0):.2f}")
    
    # Check extraction strategy
    strategy = result.get("extraction_strategy", {})
    logger.info(f"Strategy: {strategy.get('method', 'unknown')}")
    logger.info(f"Target FPS: {strategy.get('frames_per_second', 0)}")
    logger.info(f"Interval: {strategy.get('interval_seconds', 0)}s")
    logger.info(f"Scene Detection: {strategy.get('scene_detection', 'unknown')}")
    
    if extraction_rate < 0.5:
        logger.error("❌ FAILED: Extraction rate below 50%")
    elif extraction_rate < 0.8:
        logger.warning("⚠️ WARNING: Extraction rate below 80%")
    else:
        logger.info("✅ SUCCESS: Extraction rate acceptable")
    
    db.close()
    
    return {
        "recording_id": str(sample_recording.id),
        "duration": duration,
        "frames_extracted": frame_count,
        "expected_frames": expected_frames,
        "extraction_rate": extraction_rate,
        "status": "success" if extraction_rate >= 0.8 else "failed"
    }

if __name__ == "__main__":
    result = asyncio.run(test_frame_extraction())
    
    if result:
        logger.info("=" * 60)
        logger.info("TEST COMPLETE")
        if result["status"] == "success":
            logger.info("✅ Frame extraction is working correctly!")
        else:
            logger.error("❌ Frame extraction needs further investigation")