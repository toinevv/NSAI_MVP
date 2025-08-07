#!/usr/bin/env python3
"""
Test script for frame extraction service
Phase 2A Day 1: Verify frame extraction works with actual recordings
"""

import asyncio
import sys
import os
from pathlib import Path
from uuid import UUID
import logging

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from app.services.analysis import get_frame_extractor
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_frame_extraction():
    """Test frame extraction with a sample recording"""
    
    # You'll need to replace this with an actual recording session ID from your database
    # Use the ID from a completed recording session
    TEST_SESSION_ID = "d13f02ac-10e6-4f7c-b6af-a6c45fc8c073"  # Replace with actual session ID
    TEST_DURATION_SECONDS = 60  # Replace with actual duration
    
    print("\n" + "="*60)
    print("FRAME EXTRACTION TEST - NewSystem.AI MVP")
    print("="*60 + "\n")
    
    print(f"Settings:")
    print(f"  - Supabase URL: {settings.SUPABASE_URL[:30]}..." if settings.SUPABASE_URL else "  - Supabase URL: Not configured")
    print(f"  - Storage Bucket: {settings.SUPABASE_STORAGE_BUCKET}")
    print(f"  - GPT-4V Model: {settings.GPT4V_MODEL}")
    print(f"  - Cost per Request: ${settings.COST_PER_GPT4V_REQUEST}")
    print()
    
    if TEST_SESSION_ID == "YOUR_SESSION_ID_HERE":
        print("⚠️  Please update TEST_SESSION_ID with an actual recording session ID")
        print("   You can find session IDs in your Supabase database or from the frontend after recording")
        return
    
    try:
        # Initialize frame extractor
        extractor = get_frame_extractor()
        print(f"✅ Frame extractor initialized")
        print(f"   - Target frames: {extractor.target_frames}")
        print(f"   - Max frames: {extractor.max_frames}")
        print(f"   - JPEG quality: {extractor.jpeg_quality}")
        print()
        
        # Test frame extraction
        print(f"🎬 Starting frame extraction for session: {TEST_SESSION_ID}")
        print(f"   Duration: {TEST_DURATION_SECONDS} seconds")
        print()
        
        result = await extractor.extract_frames_from_recording(
            UUID(TEST_SESSION_ID),
            TEST_DURATION_SECONDS
        )
        
        if "error" in result:
            print(f"❌ Frame extraction failed: {result['error']}")
            return
        
        print(f"✅ Frame extraction completed successfully!")
        print()
        print("Results:")
        print(f"  - Frames extracted: {result['frame_count']}")
        print(f"  - Estimated GPT-4V cost: ${result.get('estimated_gpt4v_cost', 0):.2f}")
        print()
        
        if result.get('extraction_strategy'):
            strategy = result['extraction_strategy']
            print("Extraction Strategy:")
            print(f"  - Method: {strategy.get('method')}")
            print(f"  - Interval: {strategy.get('interval_seconds')}s")
            print(f"  - Target frames: {strategy.get('target_frames')}")
            print()
        
        if result.get('frames'):
            frames = result['frames']
            print(f"Frame Details ({len(frames)} frames):")
            for i, frame in enumerate(frames[:3]):  # Show first 3 frames
                print(f"  Frame {i+1}:")
                print(f"    - Timestamp: {frame.get('timestamp_formatted', 'N/A')}")
                print(f"    - Size: {frame.get('size_bytes', 0) / 1024:.1f} KB")
                print(f"    - Dimensions: {frame.get('dimensions', {}).get('width')}x{frame.get('dimensions', {}).get('height')}")
            
            if len(frames) > 3:
                print(f"  ... and {len(frames) - 3} more frames")
            print()
            
            # Calculate total size
            total_size = sum(f.get('size_bytes', 0) for f in frames)
            print(f"Total frame data size: {total_size / 1024 / 1024:.2f} MB")
            print(f"Average frame size: {total_size / len(frames) / 1024:.1f} KB")
        
        print("\n✅ Frame extraction test completed successfully!")
        print("   Ready for GPT-4V integration (Day 2-3)")
        
        # Cleanup
        extractor.cleanup_temp_files(UUID(TEST_SESSION_ID))
        print("\n🧹 Cleaned up temporary files")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        logger.exception("Frame extraction test failed")


if __name__ == "__main__":
    print("\nStarting frame extraction test...")
    print("Make sure you have:")
    print("1. A completed recording in Supabase")
    print("2. Updated TEST_SESSION_ID in this script")
    print("3. Configured Supabase credentials in .env")
    print()
    
    asyncio.run(test_frame_extraction())