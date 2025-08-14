#!/usr/bin/env python3
"""
Analysis Results Investigation Script for NewSystem.AI
Examines existing analysis results to understand why automation opportunities aren't being created
Part of Phase 1 Step 3: Trace background task execution
"""

import os
import sys
import logging
import json
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the project root to Python path and load environment
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'backend'))

# Load .env file from project root
from dotenv import load_dotenv
env_path = project_root / '.env'
if env_path.exists():
    load_dotenv(env_path)

def examine_analysis_results() -> Dict[str, Any]:
    """Examine all existing analysis results to understand the data structure"""
    logger.info("🔍 EXAMINING EXISTING ANALYSIS RESULTS")
    
    try:
        from app.core.database import get_sync_db
        from app.models.database import AnalysisResult, AutomationOpportunity, RecordingSession
        
        db = get_sync_db()
        
        # Get basic counts
        total_recordings = db.query(RecordingSession).count()
        total_analyses = db.query(AnalysisResult).count()
        total_opportunities = db.query(AutomationOpportunity).count()
        
        logger.info(f"📊 Database Summary:")
        logger.info(f"  RecordingSession count: {total_recordings}")
        logger.info(f"  AnalysisResult count: {total_analyses}")
        logger.info(f"  AutomationOpportunity count: {total_opportunities}")
        
        # Analyze analysis results by status
        analysis_by_status = {}
        all_analyses = db.query(AnalysisResult).all()
        
        for analysis in all_analyses:
            status = analysis.status
            if status not in analysis_by_status:
                analysis_by_status[status] = []
            analysis_by_status[status].append(analysis)
        
        logger.info(f"\n📋 Analysis Results by Status:")
        for status, analyses in analysis_by_status.items():
            logger.info(f"  {status}: {len(analyses)} analyses")
        
        # Examine a few sample analysis results in detail
        logger.info(f"\n🔬 Detailed Analysis of Sample Results:")
        
        sample_analyses = all_analyses[:3]  # Look at first 3 results
        
        for i, analysis in enumerate(sample_analyses, 1):
            logger.info(f"\n--- Sample Analysis #{i} ---")
            logger.info(f"  ID: {analysis.id}")
            logger.info(f"  Session ID: {analysis.session_id}")
            logger.info(f"  Status: {analysis.status}")
            logger.info(f"  GPT Version: {analysis.gpt_version}")
            logger.info(f"  Frames Analyzed: {analysis.frames_analyzed}")
            logger.info(f"  Confidence Score: {analysis.confidence_score}")
            logger.info(f"  Processing Time: {analysis.processing_time_seconds}s")
            logger.info(f"  Analysis Cost: ${analysis.analysis_cost}")
            logger.info(f"  Created: {analysis.created_at}")
            logger.info(f"  Started: {analysis.processing_started_at}")
            logger.info(f"  Completed: {analysis.processing_completed_at}")
            
            # Examine structured insights
            if analysis.structured_insights:
                insights = analysis.structured_insights
                if isinstance(insights, str):
                    try:
                        insights = json.loads(insights)
                    except:
                        pass
                
                logger.info(f"  📊 Structured Insights Keys: {list(insights.keys()) if isinstance(insights, dict) else 'Not a dict'}")
                
                if isinstance(insights, dict):
                    # Look for automation opportunities in structured insights
                    if 'automation_opportunities' in insights:
                        opportunities = insights['automation_opportunities']
                        logger.info(f"    🎯 Automation Opportunities: {len(opportunities) if isinstance(opportunities, list) else 'Not a list'}")
                        
                        if isinstance(opportunities, list) and opportunities:
                            logger.info(f"    📝 First Opportunity Keys: {list(opportunities[0].keys()) if opportunities[0] else 'Empty'}")
                    
                    if 'workflows' in insights:
                        workflows = insights['workflows']  
                        logger.info(f"    🔄 Workflows: {len(workflows) if isinstance(workflows, list) else 'Not a list'}")
                        
                    if 'summary' in insights:
                        summary = insights['summary']
                        logger.info(f"    📈 Summary Keys: {list(summary.keys()) if isinstance(summary, dict) else 'Not a dict'}")
            else:
                logger.warning(f"  ⚠️ No structured_insights found")
            
            # Examine raw GPT response
            if analysis.raw_gpt_response:
                raw_response = analysis.raw_gpt_response
                if isinstance(raw_response, str):
                    logger.info(f"  🤖 Raw GPT Response: {len(raw_response)} characters")
                    logger.info(f"  🤖 First 200 chars: {raw_response[:200]}...")
                elif isinstance(raw_response, dict):
                    logger.info(f"  🤖 Raw GPT Response Keys: {list(raw_response.keys())}")
                else:
                    logger.info(f"  🤖 Raw GPT Response Type: {type(raw_response)}")
            else:
                logger.warning(f"  ⚠️ No raw_gpt_response found")
            
            # Check if there are any automation opportunities linked to this analysis
            linked_opportunities = db.query(AutomationOpportunity).filter(
                AutomationOpportunity.analysis_id == analysis.id
            ).all()
            
            logger.info(f"  🔗 Linked AutomationOpportunities: {len(linked_opportunities)}")
        
        # Check for any orphaned automation opportunities
        logger.info(f"\n🔍 Checking for Orphaned Data:")
        
        all_opportunities = db.query(AutomationOpportunity).all()
        for opp in all_opportunities:
            logger.info(f"  AutomationOpportunity ID: {opp.id}, Analysis ID: {opp.analysis_id}")
        
        db.close()
        
        return {
            "total_recordings": total_recordings,
            "total_analyses": total_analyses,
            "total_opportunities": total_opportunities,
            "analysis_by_status": {status: len(analyses) for status, analyses in analysis_by_status.items()},
            "sample_analysis_data": "See logs for detailed analysis"
        }
        
    except Exception as e:
        logger.error(f"💥 Failed to examine analysis results: {e}", exc_info=True)
        return {"error": str(e)}

def trace_automation_opportunity_creation() -> Dict[str, Any]:
    """Trace how automation opportunities should be created from analysis results"""
    logger.info("\n🔄 TRACING AUTOMATION OPPORTUNITY CREATION LOGIC")
    
    try:
        # Import the orchestrator to understand the pipeline
        from app.services.analysis import get_orchestrator
        from app.services.analysis.result_parser import get_result_parser
        
        orchestrator = get_orchestrator()
        result_parser = get_result_parser()
        
        logger.info("✅ Successfully imported orchestrator and result parser")
        
        # Look at the result parser logic
        if hasattr(result_parser, 'parse_analysis_result'):
            logger.info("✅ Found parse_analysis_result method in result parser")
        else:
            logger.warning("⚠️ No parse_analysis_result method found")
        
        # Check what methods are available
        parser_methods = [method for method in dir(result_parser) if not method.startswith('_')]
        logger.info(f"📋 Result Parser Methods: {parser_methods}")
        
        return {
            "orchestrator_available": True,
            "result_parser_available": True,
            "parser_methods": parser_methods
        }
        
    except Exception as e:
        logger.error(f"💥 Failed to trace automation opportunity creation: {e}", exc_info=True)
        return {"error": str(e)}

def simulate_background_task_execution() -> Dict[str, Any]:
    """Simulate what happens in the background task execution"""
    logger.info("\n🎭 SIMULATING BACKGROUND TASK EXECUTION")
    
    try:
        from app.api.v1.analysis import run_full_analysis_pipeline
        
        logger.info("✅ Successfully imported run_full_analysis_pipeline function")
        
        # We can't easily simulate this without a real recording, but we can examine the code path
        logger.info("📋 Background task function available for execution")
        
        # Check if we can import the orchestrator's analyze_recording method
        from app.services.analysis import get_orchestrator
        orchestrator = get_orchestrator()
        
        if hasattr(orchestrator, 'analyze_recording'):
            logger.info("✅ Found analyze_recording method in orchestrator")
        else:
            logger.warning("⚠️ No analyze_recording method found in orchestrator")
        
        return {
            "background_task_available": True,
            "orchestrator_analyze_method": hasattr(orchestrator, 'analyze_recording')
        }
        
    except Exception as e:
        logger.error(f"💥 Failed to simulate background task: {e}", exc_info=True)
        return {"error": str(e)}

def check_result_parser_implementation() -> Dict[str, Any]:
    """Examine the result parser implementation to understand how opportunities are extracted"""
    logger.info("\n🧩 EXAMINING RESULT PARSER IMPLEMENTATION")
    
    try:
        from app.services.analysis.result_parser import get_result_parser
        
        result_parser = get_result_parser()
        
        # Check if the parser has the expected methods
        expected_methods = ['parse_analysis_result', 'extract_automation_opportunities', 'parse_gpt_response']
        available_methods = []
        
        for method in expected_methods:
            if hasattr(result_parser, method):
                available_methods.append(method)
                logger.info(f"✅ Found method: {method}")
            else:
                logger.warning(f"⚠️ Missing method: {method}")
        
        # Get all methods of the result parser
        all_methods = [method for method in dir(result_parser) if not method.startswith('_')]
        logger.info(f"📋 All Result Parser Methods: {all_methods}")
        
        return {
            "expected_methods": expected_methods,
            "available_methods": available_methods,
            "all_methods": all_methods
        }
        
    except Exception as e:
        logger.error(f"💥 Failed to examine result parser: {e}", exc_info=True)
        return {"error": str(e)}

def run_comprehensive_analysis_investigation():
    """Run complete investigation of analysis results and pipeline"""
    logger.info("🕵️ STARTING COMPREHENSIVE ANALYSIS INVESTIGATION")
    logger.info("=" * 80)
    
    investigation = {
        "timestamp": datetime.now().isoformat(),
        "components": {}
    }
    
    # Run all investigations
    investigations = [
        ("analysis_results", examine_analysis_results()),
        ("opportunity_creation", trace_automation_opportunity_creation()),
        ("background_task", simulate_background_task_execution()),
        ("result_parser", check_result_parser_implementation())
    ]
    
    for investigation_name, result in investigations:
        logger.info(f"\n{'=' * 40}")
        investigation["components"][investigation_name] = result
    
    logger.info("\n" + "=" * 80)
    logger.info("🎯 INVESTIGATION SUMMARY")
    logger.info("=" * 80)
    
    # Summarize findings
    analysis_results = investigation["components"].get("analysis_results", {})
    if "total_analyses" in analysis_results and "total_opportunities" in analysis_results:
        logger.info(f"📊 KEY FINDING: {analysis_results['total_analyses']} analyses but {analysis_results['total_opportunities']} opportunities")
        
        if analysis_results["total_analyses"] > 0 and analysis_results["total_opportunities"] == 0:
            logger.error("❌ CRITICAL ISSUE: Analyses exist but no automation opportunities are being created!")
            logger.info("🔍 This suggests the result parsing or opportunity extraction logic is failing")
    
    return investigation

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Investigate analysis results and opportunity creation")
    parser.add_argument("--save-report", help="Save investigation report to file")
    args = parser.parse_args()
    
    # Run investigation
    investigation = run_comprehensive_analysis_investigation()
    
    # Save report if requested
    if args.save_report:
        import json
        with open(args.save_report, 'w') as f:
            json.dump(investigation, f, indent=2, default=str)
        logger.info(f"📄 Investigation report saved to: {args.save_report}")
    
    logger.info(f"\n🏁 Investigation completed at {datetime.now().isoformat()}")