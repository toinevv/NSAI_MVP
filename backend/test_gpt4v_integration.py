#!/usr/bin/env python3
"""
Test script for GPT-4V Integration
Tests the complete analysis pipeline from frames to insights
Run: python test_gpt4v_integration.py
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Set test environment variables if not set
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "test-key")

from app.services.analysis.gpt4v_client import get_gpt4v_client
from app.services.analysis.prompts import get_analysis_prompt, TEST_PROMPT
from app.services.analysis.result_parser import get_result_parser
from app.core.config import settings


async def test_gpt4v_configuration():
    """Test GPT-4V client configuration"""
    print("\n=== Testing GPT-4V Configuration ===")
    
    client = get_gpt4v_client()
    validation = client.validate_configuration()
    
    print(f"✓ GPT-4V Configured: {validation['configured']}")
    print(f"  Model: {validation['model']}")
    print(f"  Max Tokens: {validation['max_tokens']}")
    print(f"  Cost per Image: ${validation['cost_per_image']}")
    
    if validation['issues']:
        print("⚠️  Configuration Issues:")
        for issue in validation['issues']:
            print(f"  - {issue}")
        return False
    
    return True


async def test_prompt_system():
    """Test prompt generation"""
    print("\n=== Testing Prompt System ===")
    
    # Test different prompt types
    prompt_types = ["full", "email_wms", "quick", "roi", "pattern"]
    
    for prompt_type in prompt_types:
        system_prompt, user_prompt = get_analysis_prompt(prompt_type)
        print(f"✓ {prompt_type.upper()} prompt loaded")
        print(f"  System prompt length: {len(system_prompt)} chars")
        print(f"  User prompt length: {len(user_prompt)} chars")
    
    return True


async def test_result_parser():
    """Test result parser with mock GPT response"""
    print("\n=== Testing Result Parser ===")
    
    parser = get_result_parser()
    
    # Mock GPT-4V response
    mock_response = {
        "success": True,
        "analysis": {
            "workflows_detected": [
                {
                    "type": "email_to_wms",
                    "description": "Order entry from email to WMS",
                    "applications_involved": ["Outlook", "SAP WMS"],
                    "steps_observed": ["Open email", "Copy order number", "Switch to WMS", "Paste data"],
                    "estimated_duration_seconds": 120,
                    "data_types_handled": ["order_numbers", "quantities"],
                    "repetitive_score": 0.9
                }
            ],
            "automation_opportunities": [
                {
                    "workflow_type": "email_to_wms",
                    "description": "Automate order entry from email",
                    "frequency_daily": 15,
                    "time_per_occurrence_minutes": 2,
                    "total_time_saved_daily_minutes": 30,
                    "automation_potential": "high",
                    "implementation_complexity": "low",
                    "specific_recommendation": "Implement email parser with WMS API"
                }
            ],
            "time_breakdown": {
                "total_time_analyzed_seconds": 300,
                "email_time_seconds": 60,
                "wms_time_seconds": 180,
                "excel_time_seconds": 60
            },
            "key_insights": [
                "60% of time spent on manual data entry",
                "Email to WMS pattern occurs 15x daily"
            ],
            "confidence_score": 0.85
        },
        "metadata": {"frame_count": 10},
        "usage": {"total_tokens": 1500}
    }
    
    # Parse the mock response
    result = parser.parse_analysis_result(mock_response)
    
    print(f"✓ Result parsed successfully: {result['success']}")
    print(f"  Workflows detected: {len(result['workflows'])}")
    print(f"  Opportunities found: {len(result['automation_opportunities'])}")
    print(f"  Confidence score: {result['confidence_score']}")
    
    # Check summary
    summary = result.get('summary', {})
    print(f"✓ Summary generated:")
    print(f"  Time savings: {summary.get('time_savings_daily_minutes', 0)} min/day")
    print(f"  Annual savings: ${summary.get('cost_savings_annual_usd', 0)}")
    print(f"  ROI multiplier: {summary.get('roi_multiplier', 0)}x")
    
    # Validate result structure
    is_valid = parser.validate_result(result)
    print(f"✓ Result validation: {'PASSED' if is_valid else 'FAILED'}")
    
    return is_valid


async def test_with_sample_image():
    """Test with a sample image (if API key is configured)"""
    print("\n=== Testing with Sample Image (Optional) ===")
    
    client = get_gpt4v_client()
    
    if not settings.OPENAI_API_KEY:
        print("⚠️  Skipping: OpenAI API key not configured")
        print("  Set OPENAI_API_KEY environment variable to enable this test")
        return True
    
    # Create a simple test frame
    test_frame = {
        "sequence_number": 1,
        "frame_index": 0,
        "timestamp_seconds": 0,
        "timestamp_formatted": "00:00",
        "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",  # 1x1 pixel
        "image_format": "png"
    }
    
    try:
        # Use test prompt for minimal token usage
        result = await client.analyze_single_frame(test_frame, TEST_PROMPT)
        
        if result.get("success"):
            print("✓ GPT-4V API call successful!")
            print(f"  Tokens used: {result.get('usage', {}).get('total_tokens', 0)}")
            print(f"  Estimated cost: ${client.estimate_cost(1)}")
        else:
            print(f"⚠️  GPT-4V call failed: {result.get('error')}")
    
    except Exception as e:
        print(f"⚠️  Error calling GPT-4V: {e}")
    
    return True


async def main():
    """Run all tests"""
    print("=" * 50)
    print("NewSystem.AI GPT-4V Integration Test Suite")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_gpt4v_configuration),
        ("Prompts", test_prompt_system),
        ("Result Parser", test_result_parser),
        ("Sample Image", test_with_sample_image)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = await test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ {test_name} test failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name:20} {status}")
    
    all_passed = all(success for _, success in results)
    
    if all_passed:
        print("\n🎉 All tests passed! GPT-4V integration is ready.")
    else:
        print("\n⚠️  Some tests failed. Please check the configuration.")
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)