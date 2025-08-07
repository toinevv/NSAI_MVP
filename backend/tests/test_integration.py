#!/usr/bin/env python3
"""
Integration Tests for NewSystem.AI
Tests the complete pipeline and component interactions
"""

import asyncio
import sys
import json
import base64
from pathlib import Path
from io import BytesIO
from PIL import Image, ImageDraw
from uuid import uuid4
from typing import Dict, Any, List

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.analysis.orchestrator import get_orchestrator
from app.services.analysis.gpt4v_client import get_gpt4v_client
from app.services.analysis.result_parser import get_result_parser
from app.services.analysis.prompts import get_analysis_prompt


def create_workflow_frames(num_frames: int = 5) -> List[dict]:
    """Create a series of workflow frames simulating email to WMS process"""
    frames = []
    steps = [
        ("Opening email application", "Outlook"),
        ("Reading order details", "Outlook"),
        ("Copying order information", "Outlook"),
        ("Opening WMS portal", "Chrome Browser"),
        ("Entering order data", "WMS Portal"),
    ]
    
    for i, (text, app) in enumerate(steps[:num_frames]):
        img = Image.new('RGB', (1024, 768), color=(245, 245, 245))
        draw = ImageDraw.Draw(img)
        
        # Add app header
        draw.rectangle([(0, 0), (1024, 60)], fill=(50, 50, 50))
        draw.text((20, 20), app, fill=(255, 255, 255))
        
        # Add main text
        draw.text((50, 150), text, fill=(0, 0, 0))
        
        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        frames.append({
            "sequence_number": i,
            "frame_index": i * 100,
            "timestamp_seconds": i * 10,
            "timestamp_formatted": f"00:{i*10:02d}",
            "image_base64": img_base64,
            "image_format": "png"
        })
    
    return frames


async def test_full_pipeline():
    """Test the complete analysis pipeline end-to-end"""
    print("\n=== Testing Full Analysis Pipeline ===")
    
    # Check GPT-4V configuration first
    client = get_gpt4v_client()
    config = client.validate_configuration()
    
    if not config["configured"]:
        print("⚠️  Skipping pipeline test - GPT-4V not configured")
        print("   Set OPENAI_API_KEY to enable this test")
        return None
    
    print("📸 Creating test workflow frames...")
    frames = create_workflow_frames(5)
    print(f"   Created {len(frames)} frames")
    
    # Test with natural language prompt
    print("\n🤖 Testing natural language analysis...")
    system_prompt, user_prompt = get_analysis_prompt("natural")
    
    result = await client.analyze_frames(
        frames,
        system_prompt,
        user_prompt
    )
    
    if not result["success"]:
        print(f"❌ Analysis failed: {result.get('error')}")
        return False
    
    print("✅ GPT-4V analysis successful")
    print(f"   Tokens used: {result.get('usage', {}).get('total_tokens', 0)}")
    
    # Parse results
    parser = get_result_parser()
    parsed = parser.parse_analysis_result(result)
    
    if not parsed["success"]:
        print(f"❌ Parsing failed: {parsed.get('error')}")
        return False
    
    print("✅ Results parsed successfully")
    
    # Validate results
    assert len(parsed["workflows"]) > 0, "Should detect workflows"
    assert "summary" in parsed, "Should have summary"
    assert parsed["confidence_score"] > 0, "Should have confidence"
    
    # Display summary
    print("\n📊 Analysis Summary:")
    print(f"   Format: {parsed.get('format', 'structured')}")
    print(f"   Workflows: {len(parsed['workflows'])}")
    print(f"   Opportunities: {len(parsed['automation_opportunities'])}")
    print(f"   Confidence: {parsed['confidence_score']:.0%}")
    
    if parsed.get('raw_gpt_response', {}).get('natural_description'):
        desc = parsed['raw_gpt_response']['natural_description']
        print(f"\n📝 Natural Description:")
        print(f"   {desc[:200]}..." if len(desc) > 200 else f"   {desc}")
    
    return True


async def test_discovery_mode():
    """Test discovery mode for finding unknown workflows"""
    print("\n=== Testing Discovery Mode ===")
    
    client = get_gpt4v_client()
    config = client.validate_configuration()
    
    if not config["configured"]:
        print("⚠️  Skipping discovery test - GPT-4V not configured")
        return None
    
    # Create diverse workflow frames
    print("📸 Creating diverse workflow frames...")
    frames = create_workflow_frames(3)
    
    # Use discovery prompt
    system_prompt, user_prompt = get_analysis_prompt("discovery")
    
    print("🔍 Running discovery analysis...")
    result = await client.analyze_frames(frames, system_prompt, user_prompt)
    
    if result["success"]:
        print("✅ Discovery analysis successful")
        
        # Check if it found patterns without forcing categories
        analysis = result.get("analysis", {})
        if "natural_description" in analysis:
            print("✅ Natural description provided")
        if "patterns" in analysis:
            print(f"✅ Found {len(analysis['patterns'])} patterns")
        
        return True
    else:
        print(f"❌ Discovery failed: {result.get('error')}")
        return False


async def test_orchestrator_validation():
    """Test orchestrator prerequisites validation"""
    print("\n=== Testing Orchestrator Validation ===")
    
    orchestrator = get_orchestrator()
    session_id = uuid4()
    
    prereqs = await orchestrator.validate_prerequisites(session_id)
    
    print(f"📋 Prerequisites Check:")
    print(f"   Ready: {prereqs['ready']}")
    print(f"   GPT-4V: {'✅' if prereqs['gpt4v_configured'] else '❌'}")
    
    if prereqs["issues"]:
        print(f"   Issues: {', '.join(prereqs['issues'])}")
    else:
        print(f"   Estimated cost: ${prereqs['estimated_cost']:.2f}")
    
    return True


async def main():
    """Run all integration tests"""
    print("🧪 NewSystem.AI Integration Tests")
    print("=" * 50)
    
    results = []
    
    # Run tests
    results.append(("Orchestrator Validation", await test_orchestrator_validation()))
    results.append(("Full Pipeline", await test_full_pipeline()))
    results.append(("Discovery Mode", await test_discovery_mode()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    
    passed = 0
    failed = 0
    skipped = 0
    
    for name, result in results:
        if result is None:
            status = "⏭️"
            skipped += 1
        elif result:
            status = "✅"
            passed += 1
        else:
            status = "❌"
            failed += 1
        print(f"  {status} {name}")
    
    total = len(results)
    print(f"\nPassed: {passed}/{total}")
    if skipped > 0:
        print(f"Skipped: {skipped} (configure OPENAI_API_KEY to enable)")
    
    if failed == 0:
        print("\n✨ All integration tests passed!")
        return True
    else:
        print(f"\n⚠️  {failed} tests failed")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)