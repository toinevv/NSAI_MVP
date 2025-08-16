#!/usr/bin/env python3
"""
Unit Tests for NewSystem.AI Components
Tests individual components in isolation
"""

import asyncio
import sys
import json
import base64
from pathlib import Path
from io import BytesIO
from PIL import Image
from typing import Dict, Any, List

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.analysis.gpt4v_client import get_gpt4v_client
from app.services.analysis.result_parser import get_result_parser
from app.services.analysis.frame_extractor import get_frame_extractor
from app.services.analysis.prompts import get_analysis_prompt
from app.core.config import settings


def create_test_frame(text: str, frame_num: int = 0) -> dict:
    """Create a test frame for testing"""
    img = Image.new('RGB', (1024, 768), color=(245, 245, 245))
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return {
        "sequence_number": frame_num,
        "frame_index": frame_num * 100,
        "timestamp_seconds": frame_num * 10,
        "timestamp_formatted": f"00:{frame_num*10:02d}",
        "image_base64": img_base64,
        "image_format": "png"
    }


async def test_gpt4v_configuration():
    """Test GPT-4V client configuration"""
    print("\n=== Testing GPT-4V Configuration ===")
    
    client = get_gpt4v_client()
    config = client.validate_configuration()
    
    assert "configured" in config, "Configuration should have 'configured' key"
    
    if config["configured"]:
        print("✅ GPT-4V is properly configured")
        assert config["issues"] == [], "Should have no issues when configured"
    else:
        print(f"⚠️  GPT-4V not configured: {config['issues']}")
        print("   Set OPENAI_API_KEY environment variable to enable")
    
    return config["configured"]


async def test_prompt_system():
    """Test prompt generation system"""
    print("\n=== Testing Prompt System ===")
    
    # Test different prompt types
    prompt_types = ["full", "quick", "natural", "discovery"]
    
    for ptype in prompt_types:
        try:
            system_prompt, user_prompt = get_analysis_prompt(ptype)
            assert isinstance(system_prompt, str), f"System prompt should be string for {ptype}"
            assert isinstance(user_prompt, str), f"User prompt should be string for {ptype}"
            assert len(system_prompt) > 0, f"System prompt should not be empty for {ptype}"
            assert len(user_prompt) > 0, f"User prompt should not be empty for {ptype}"
            assert "json" in user_prompt.lower() or "JSON" in user_prompt, f"Prompt should mention JSON for {ptype}"
            print(f"✅ Prompt type '{ptype}' works correctly")
        except Exception as e:
            print(f"❌ Prompt type '{ptype}' failed: {e}")
            return False
    
    return True


async def test_result_parser():
    """Test result parser with various response formats"""
    print("\n=== Testing Result Parser ===")
    
    parser = get_result_parser()
    
    # Test successful natural language format
    natural_response = {
        "success": True,
        "analysis": {
            "natural_description": "User is processing orders from email",
            "applications": {
                "Outlook": {"purpose": "Reading emails", "timePercentage": 30},
                "WMS": {"purpose": "Entering orders", "timePercentage": 70}
            },
            "patterns": ["Repetitive data entry", "Manual copying"],
            "automation_opportunities": [
                {
                    "what": "Email to WMS automation",
                    "how": "Use API integration",
                    "timeSaved": "30 minutes daily",
                    "complexity": "simple"
                }
            ],
            "confidence": 0.85
        }
    }
    
    result = parser.parse_analysis_result(natural_response)
    assert result["success"] == True, "Should parse natural format successfully"
    assert "format" in result, "Should indicate format type"
    assert len(result["workflows"]) > 0, "Should extract workflows"
    print("✅ Natural language format parsing works")
    
    # Test legacy format
    legacy_response = {
        "success": True,
        "analysis": {
            "workflows_detected": [
                {
                    "type": "email_to_wms",
                    "description": "Email order processing",
                    "applications_involved": ["Outlook", "WMS"],
                    "estimated_duration_seconds": 120
                }
            ],
            "automation_opportunities": [],
            "time_breakdown": {"total_time_analyzed_seconds": 300},
            "key_insights": ["Manual process identified"],
            "confidence_score": 0.75
        }
    }
    
    result = parser.parse_analysis_result(legacy_response)
    assert result["success"] == True, "Should parse legacy format"
    assert len(result["workflows"]) == 1, "Should have one workflow"
    print("✅ Legacy format parsing works")
    
    # Test error handling
    error_response = {"success": False, "error": "Test error"}
    result = parser.parse_analysis_result(error_response)
    assert result["success"] == False, "Should handle errors"
    assert "error" in result, "Should include error message"
    print("✅ Error handling works")
    
    return True


async def test_frame_extractor_config():
    """Test frame extractor configuration"""
    print("\n=== Testing Frame Extractor Configuration ===")
    
    extractor = get_frame_extractor()
    
    # Test extraction strategy calculation
    strategy = extractor.calculate_extraction_strategy(duration_seconds=60)
    
    assert "interval_seconds" in strategy, "Should have interval"
    assert "total_frames" in strategy, "Should have frame count"
    assert strategy["total_frames"] <= 10, "Should limit frames for cost"
    assert strategy["interval_seconds"] >= 5, "Should have reasonable interval"
    
    print(f"✅ Extraction strategy: {strategy['total_frames']} frames at {strategy['interval_seconds']}s intervals")
    
    return True


async def main():
    """Run all unit tests"""
    print("🧪 NewSystem.AI Unit Tests")
    print("=" * 50)
    
    results = []
    
    # Run tests
    results.append(("GPT-4V Configuration", await test_gpt4v_configuration()))
    results.append(("Prompt System", await test_prompt_system()))
    results.append(("Result Parser", await test_result_parser()))
    results.append(("Frame Extractor", await test_frame_extractor_config()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"  {status} {name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n✨ All unit tests passed!")
        return True
    else:
        print(f"\n⚠️  {total - passed} tests failed")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)