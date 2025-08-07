#!/usr/bin/env python3
"""
Test the full analysis pipeline from frame extraction to results
Run: python test_full_pipeline.py
"""

import asyncio
import os
import sys
from pathlib import Path
from uuid import UUID

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.analysis.orchestrator import get_orchestrator
from app.core.config import settings
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test session ID from the database - update this with your actual session ID
TEST_SESSION_ID = "d13f02ac-10e6-4f7c-b6af-a6c45fc8c073"
TEST_DURATION = 60  # seconds

async def test_full_pipeline():
    """Test the complete analysis pipeline"""
    print("\n" + "="*60)
    print("FULL PIPELINE TEST - NewSystem.AI MVP")
    print("="*60)
    
    print(f"\nSettings:")
    print(f"  - Session ID: {TEST_SESSION_ID}")
    print(f"  - Duration: {TEST_DURATION} seconds")
    print(f"  - GPT-4V Model: {settings.GPT4V_MODEL}")
    print(f"  - OpenAI API Key: {'✅ Configured' if settings.OPENAI_API_KEY else '❌ Missing'}")
    
    if not settings.OPENAI_API_KEY:
        print("\n❌ Error: OpenAI API key not configured!")
        print("Please set OPENAI_API_KEY in your .env file")
        return False
    
    try:
        # Get the orchestrator
        orchestrator = get_orchestrator()
        print("\n✅ Analysis orchestrator initialized")
        
        # Run full analysis
        print(f"\n🚀 Starting full analysis for session {TEST_SESSION_ID}...")
        print("This will:")
        print("  1. Extract frames from the recording")
        print("  2. Analyze frames with GPT-4V")
        print("  3. Parse and structure results")
        print("  4. Calculate automation opportunities\n")
        
        result = await orchestrator.analyze_recording(
            session_id=UUID(TEST_SESSION_ID),
            duration_seconds=TEST_DURATION,
            analysis_type="full"
        )
        
        # Check if analysis was successful
        if result.get("success"):
            print("\n✅ Analysis completed successfully!")
            
            # Display results
            print("\n📊 Analysis Results:")
            print(f"  Processing time: {result.get('processing_time_seconds', 0):.1f} seconds")
            
            # Frame analysis
            frame_info = result.get("frame_analysis", {})
            print(f"\n🎬 Frame Analysis:")
            print(f"  Frames analyzed: {frame_info.get('frames_analyzed', 0)}")
            print(f"  Estimated cost: ${frame_info.get('estimated_cost', 0):.2f}")
            
            # Workflows detected
            workflows = result.get("workflows", [])
            print(f"\n🔄 Workflows Detected: {len(workflows)}")
            for i, workflow in enumerate(workflows, 1):
                print(f"  {i}. {workflow.get('type', 'unknown')} - {workflow.get('description', 'N/A')}")
            
            # Automation opportunities
            opportunities = result.get("automation_opportunities", [])
            print(f"\n🎯 Automation Opportunities: {len(opportunities)}")
            for i, opp in enumerate(opportunities, 1):
                print(f"  {i}. {opp.get('description', 'N/A')}")
                print(f"     - Potential: {opp.get('automation_potential', 'unknown')}")
                print(f"     - Time saved: {opp.get('total_time_saved_daily_minutes', 0)} min/day")
                print(f"     - Complexity: {opp.get('implementation_complexity', 'unknown')}")
            
            # Time analysis
            time_analysis = result.get("time_analysis", {})
            if time_analysis:
                print(f"\n⏱️ Time Analysis:")
                print(f"  Total daily time saved: {time_analysis.get('total_daily_time_saved_minutes', 0)} minutes")
                print(f"  Annual value: ${time_analysis.get('annual_value_usd', 0):,.2f}")
            
            # Metadata
            metadata = result.get("metadata", {})
            print(f"\n📝 Metadata:")
            print(f"  GPT Model: {metadata.get('gpt_model', 'unknown')}")
            print(f"  Tokens used: {metadata.get('tokens_used', 0)}")
            print(f"  Processing cost: ${metadata.get('processing_cost', 0):.3f}")
            
            return True
            
        else:
            print(f"\n❌ Analysis failed!")
            error = result.get("error", "Unknown error")
            print(f"Error: {error}")
            
            # Show pipeline status to debug
            pipeline_status = result.get("pipeline_status", {})
            if pipeline_status:
                print("\n🔍 Pipeline Status:")
                print(f"  Current step: {pipeline_status.get('current_step', 'unknown')}")
                print(f"  Steps completed: {len(pipeline_status.get('steps_completed', []))}")
                for step in pipeline_status.get('steps_completed', []):
                    print(f"    - {step.get('step', 'unknown')}")
            
            return False
            
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        logger.error(f"Pipeline test failed", exc_info=True)
        return False

async def main():
    """Main test runner"""
    success = await test_full_pipeline()
    
    if success:
        print("\n" + "="*60)
        print("✅ FULL PIPELINE TEST PASSED!")
        print("="*60)
        print("\nThe analysis pipeline is working correctly.")
        print("Next steps:")
        print("  1. Test with different recording sessions")
        print("  2. Verify results in the frontend")
        print("  3. Fine-tune prompts for better accuracy")
    else:
        print("\n" + "="*60)
        print("❌ FULL PIPELINE TEST FAILED")
        print("="*60)
        print("\nTroubleshooting steps:")
        print("  1. Check that the recording exists in Supabase")
        print("  2. Verify OpenAI API key is valid")
        print("  3. Check logs above for specific errors")
        print("  4. Ensure ffmpeg is installed for video processing")

if __name__ == "__main__":
    asyncio.run(main())