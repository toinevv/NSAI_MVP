#!/usr/bin/env python3
"""
Simple test for natural language GPT-4V analysis
Tests the discovery-based approach with plain test frames
"""

import asyncio
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent))

from app.services.analysis.gpt4v_client import get_gpt4v_client
from app.services.analysis.prompts_natural import get_natural_prompt
from app.services.analysis.result_parser import get_result_parser


def create_workflow_frame(text: str, app_name: str = "Application", frame_num: int = 0) -> dict:
    """Create a test frame simulating a workflow step"""
    img = Image.new('RGB', (1024, 768), color=(245, 245, 245))
    draw = ImageDraw.Draw(img)
    
    # Add app header
    draw.rectangle([(0, 0), (1024, 60)], fill=(50, 50, 50))
    draw.text((20, 20), app_name, fill=(255, 255, 255))
    
    # Add main text
    draw.text((50, 150), text, fill=(0, 0, 0))
    
    # Convert to base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    # Return in the format expected by GPT-4V client
    return {
        "sequence_number": frame_num,
        "frame_index": frame_num * 100,
        "timestamp_seconds": frame_num * 10,
        "timestamp_formatted": f"00:{frame_num*10:02d}",
        "image_base64": img_base64,
        "image_format": "png"
    }


async def test_natural_language_analysis():
    """Test natural language analysis with simulated workflow"""
    print("\n╔══════════════════════════════════════════════╗")
    print("║   Testing Natural Language GPT-4V Analysis   ║")
    print("╚══════════════════════════════════════════════╝\n")
    
    # Create workflow frames simulating email to WMS process
    frames = [
        create_workflow_frame("Reading email with order details", "Outlook", 0),
        create_workflow_frame("Copying order number and customer info", "Outlook", 1),
        create_workflow_frame("Opening warehouse management system", "Chrome Browser", 2),
        create_workflow_frame("Entering order details into form", "WMS Portal", 3),
        create_workflow_frame("Submitting order to warehouse", "WMS Portal", 4),
    ]
    
    print(f"📸 Created {len(frames)} workflow simulation frames")
    
    # Get GPT-4V client
    client = get_gpt4v_client()
    
    # Check configuration
    config = client.validate_configuration()
    if not config["configured"]:
        print(f"❌ GPT-4V not configured: {config['issues']}")
        print("\n⚠️  Set your OpenAI API key:")
        print("   export OPENAI_API_KEY='your-key-here'")
        return False
    
    print("✅ GPT-4V configured and ready")
    
    # Get natural language prompts
    system_prompt, user_prompt = get_natural_prompt("simple")
    
    print("🤖 Analyzing workflow with natural language approach...")
    
    # Analyze frames
    result = await client.analyze_frames(
        frames,
        system_prompt,
        user_prompt
    )
    
    if not result.get("success"):
        print(f"❌ Analysis failed: {result.get('error')}")
        return False
    
    print("✅ GPT-4V analysis complete!")
    print(f"   Tokens: {result.get('usage', {}).get('total_tokens', 0)}")
    
    # Parse results
    parser = get_result_parser()
    parsed = parser.parse_analysis_result(result)
    
    if not parsed.get("success"):
        print(f"❌ Parsing failed: {parsed.get('error')}")
        return False
    
    print("✅ Results parsed successfully!")
    
    # Display natural language results
    print("\n" + "="*50)
    print("📊 ANALYSIS RESULTS")
    print("="*50)
    
    raw = parsed.get('raw_gpt_response', {})
    
    # Natural description
    if 'natural_description' in raw:
        print("\n📝 What We Observed:")
        print("-" * 40)
        desc = raw['natural_description']
        # Format nicely
        import textwrap
        for line in textwrap.wrap(desc, width=60):
            print(f"  {line}")
    
    # Applications detected
    if 'applications' in raw:
        print("\n💻 Applications Used:")
        print("-" * 40)
        for app_name, app_info in raw['applications'].items():
            print(f"  • {app_name}")
            if isinstance(app_info, dict):
                print(f"    Purpose: {app_info.get('purpose', 'N/A')}")
    
    # Patterns found
    if 'patterns' in raw:
        print("\n🔍 Patterns Discovered:")
        print("-" * 40)
        for pattern in raw['patterns'][:3]:
            print(f"  • {pattern}")
    
    # Automation opportunities
    if parsed['automation_opportunities']:
        print("\n💡 Automation Opportunities:")
        print("-" * 40)
        for i, opp in enumerate(parsed['automation_opportunities'][:3], 1):
            print(f"  {i}. {opp['description']}")
            print(f"     Time saved: {opp['time_saved_daily_minutes']:.0f} min/day")
            print(f"     Complexity: {opp.get('implementation_complexity', 'N/A')}")
    
    # Summary
    summary = parsed.get('summary', {})
    if summary:
        print("\n📈 Impact Summary:")
        print("-" * 40)
        print(f"  Daily savings: {summary.get('time_savings_daily_minutes', 0):.0f} minutes")
        print(f"  Annual savings: ${summary.get('cost_savings_annual_usd', 0):,.0f}")
        print(f"  Confidence: {parsed.get('confidence_score', 0):.0%}")
    
    print("\n" + "="*50)
    
    return True


async def main():
    """Run the test"""
    success = await test_natural_language_analysis()
    
    if success:
        print("\n✨ Test completed successfully!")
        print("The natural language analysis pipeline is working.")
    else:
        print("\n❌ Test failed. Check configuration and logs above.")
    
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)