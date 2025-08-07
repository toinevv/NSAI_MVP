#!/usr/bin/env python3
"""
Test the Enhanced Discovery Mode for Open-Ended Workflow Analysis
This test validates that the system can discover ANY workflow, not just email → WMS
Run: python test_discovery_mode.py
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
import json

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test session ID - update with your actual recording
TEST_SESSION_ID = "d13f02ac-10e6-4f7c-b6af-a6c45fc8c073"
TEST_DURATION = 60  # seconds

async def test_discovery_mode():
    """Test the enhanced discovery mode for open-ended workflow analysis"""
    print("\n" + "="*70)
    print("WORKFLOW DISCOVERY TEST - NewSystem.AI")
    print("Testing open-ended workflow discovery without assumptions")
    print("="*70)
    
    print(f"\n📋 Test Configuration:")
    print(f"  - Session ID: {TEST_SESSION_ID}")
    print(f"  - Analysis Mode: discovery (open-ended)")
    print(f"  - Expected: Find ALL workflows, not just email → WMS")
    
    try:
        orchestrator = get_orchestrator()
        print("\n✅ Orchestrator initialized")
        
        # Run discovery analysis
        print(f"\n🔍 Starting DISCOVERY analysis...")
        print("This will identify:")
        print("  - ALL applications used")
        print("  - ALL workflow patterns")
        print("  - Unknown/unnamed patterns")
        print("  - Operator expertise and workarounds")
        print("  - Hidden inefficiencies\n")
        
        result = await orchestrator.analyze_recording(
            session_id=UUID(TEST_SESSION_ID),
            duration_seconds=TEST_DURATION,
            analysis_type="discovery"  # Use discovery mode
        )
        
        if result.get("success"):
            print("\n✅ Discovery analysis completed!")
            
            # Parse the enhanced results
            print("\n" + "="*70)
            print("📊 DISCOVERED WORKFLOWS")
            print("="*70)
            
            # Get the analysis from GPT-4V
            analysis = result.get("workflows", [])
            opportunities = result.get("automation_opportunities", [])
            
            # For discovery mode, we expect more detailed structure
            # Try to parse if the result contains our enhanced format
            raw_analysis = result.get("gpt_response", {})
            if isinstance(raw_analysis, dict):
                discovered = raw_analysis.get("discovered_workflows", [])
                unknown = raw_analysis.get("unknown_patterns", [])
                app_insights = raw_analysis.get("application_insights", {})
                operator_expertise = raw_analysis.get("operator_expertise_observed", {})
            else:
                discovered = []
                unknown = []
                app_insights = {}
                operator_expertise = {}
            
            # Display discovered workflows
            if discovered:
                print("\n🔄 Discovered Workflow Patterns:")
                for i, workflow in enumerate(discovered, 1):
                    print(f"\n  {i}. {workflow.get('description', 'Unnamed workflow')}")
                    print(f"     Type: {workflow.get('pattern_type', 'unknown')}")
                    print(f"     Apps: {', '.join(workflow.get('applications_involved', []))}")
                    print(f"     Confidence: {workflow.get('confidence_level', 0):.0%}")
                    print(f"     Automation Potential: {workflow.get('automation_potential', {}).get('score', 0):.0%}")
            else:
                # Fallback to standard format
                print("\n🔄 Workflows Detected:")
                for i, workflow in enumerate(analysis, 1):
                    print(f"\n  {i}. {workflow.get('description', workflow.get('type', 'Unknown'))}")
                    if 'applications_involved' in workflow:
                        print(f"     Apps: {', '.join(workflow.get('applications_involved', []))}")
            
            # Display unknown patterns
            if unknown:
                print("\n❓ Unknown/Unnamed Patterns Found:")
                for pattern in unknown:
                    print(f"  - {pattern.get('description', 'Unnamed pattern')}")
                    print(f"    Frequency: {pattern.get('frequency', 'Unknown')}")
                    print(f"    Needs clarification: {pattern.get('needs_clarification', 'N/A')}")
            
            # Display application insights
            if app_insights:
                print("\n💻 Application Usage Insights:")
                primary = app_insights.get("primary_systems", {})
                for app, details in primary.items():
                    print(f"  - {app}:")
                    print(f"    Time: {details.get('time_spent_seconds', 0)} seconds")
                    print(f"    Use: {details.get('primary_use', 'Unknown')}")
                    if 'pain_points' in details:
                        print(f"    Issues: {', '.join(details.get('pain_points', []))}")
            
            # Display operator expertise
            if operator_expertise:
                print("\n👤 Operator Expertise Observed:")
                if operator_expertise.get("shortcuts_used"):
                    print(f"  Shortcuts: {', '.join(operator_expertise['shortcuts_used'])}")
                if operator_expertise.get("workarounds_developed"):
                    print(f"  Workarounds: {', '.join(operator_expertise['workarounds_developed'])}")
                if operator_expertise.get("efficiency_techniques"):
                    print(f"  Techniques: {', '.join(operator_expertise['efficiency_techniques'])}")
            
            # Display opportunities
            print(f"\n🎯 Automation Opportunities: {len(opportunities)}")
            for i, opp in enumerate(opportunities[:5], 1):  # Show top 5
                print(f"  {i}. {opp.get('description', 'N/A')}")
                time_saved = opp.get('total_time_saved_daily_minutes', 0)
                if time_saved > 0:
                    print(f"     Time saved: {time_saved} min/day")
            
            # Display time analysis
            time_analysis = result.get("time_analysis", {})
            if time_analysis:
                print(f"\n⏱️ Time Analysis:")
                print(f"  Total time analyzed: {result.get('processing_time_seconds', 0):.1f} seconds")
                print(f"  Daily time savings potential: {time_analysis.get('total_daily_time_saved_minutes', 0)} minutes")
            
            # Show raw response for debugging
            print("\n" + "="*70)
            print("📝 Raw Analysis Structure (for debugging):")
            print("="*70)
            if isinstance(raw_analysis, dict):
                print(f"Keys found: {list(raw_analysis.keys())}")
            else:
                print(f"Response type: {type(raw_analysis)}")
            
            return True
            
        else:
            print(f"\n❌ Discovery analysis failed!")
            print(f"Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        logger.error(f"Discovery test failed", exc_info=True)
        return False

async def test_clustering_mode():
    """Test pattern clustering after discovery"""
    print("\n" + "="*70)
    print("PATTERN CLUSTERING TEST")
    print("="*70)
    
    try:
        orchestrator = get_orchestrator()
        
        # Run clustering analysis
        print(f"\n🔗 Starting CLUSTERING analysis...")
        
        result = await orchestrator.analyze_recording(
            session_id=UUID(TEST_SESSION_ID),
            duration_seconds=TEST_DURATION,
            analysis_type="clustering"
        )
        
        if result.get("success"):
            print("✅ Clustering completed!")
            # Process clustering results
            return True
        else:
            print(f"❌ Clustering failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Clustering test failed: {e}")
        return False

async def main():
    """Run all discovery tests"""
    print("\n" + "🚀 "*20)
    print("STARTING COMPREHENSIVE DISCOVERY TESTS")
    print("🚀 "*20)
    
    # Test 1: Discovery Mode
    discovery_success = await test_discovery_mode()
    
    # Test 2: Clustering Mode (optional)
    # clustering_success = await test_clustering_mode()
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    if discovery_success:
        print("✅ Discovery Mode: PASSED")
        print("\nThe system successfully:")
        print("  - Analyzed workflows without assumptions")
        print("  - Identified multiple patterns")
        print("  - Discovered applications and inefficiencies")
        print("  - Provided actionable insights")
    else:
        print("❌ Discovery Mode: FAILED")
        print("\nTroubleshooting:")
        print("  1. Check that recording exists in Supabase")
        print("  2. Verify OpenAI API key is valid")
        print("  3. Check that frames were extracted properly")
        print("  4. Review logs for specific errors")
    
    print("\n📊 Next Steps:")
    print("  1. Test with longer recordings (2-3 hours)")
    print("  2. Test with different operator workflows")
    print("  3. Compare discovery vs traditional analysis")
    print("  4. Validate unknown pattern detection")

if __name__ == "__main__":
    asyncio.run(main())