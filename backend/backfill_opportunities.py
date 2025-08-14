#!/usr/bin/env python3
"""
Backfill AutomationOpportunity Records for NewSystem.AI
Creates individual AutomationOpportunity records from existing analysis results
that have opportunities in structured_insights but no individual records
Part of Phase 1 Step 3: Fix existing data issue
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

def backfill_automation_opportunities() -> Dict[str, Any]:
    """Backfill automation opportunity records from existing analysis results"""
    logger.info("🔄 STARTING AUTOMATION OPPORTUNITIES BACKFILL")
    
    try:
        from app.core.database import get_sync_db
        from app.models.database import AnalysisResult, AutomationOpportunity
        
        db = get_sync_db()
        
        # Get all completed analysis results
        completed_analyses = db.query(AnalysisResult).filter(
            AnalysisResult.status == "completed"
        ).all()
        
        logger.info(f"📊 Found {len(completed_analyses)} completed analyses to process")
        
        total_opportunities_created = 0
        analyses_processed = 0
        
        for analysis in completed_analyses:
            logger.info(f"\n--- Processing Analysis {analysis.id} ---")
            logger.info(f"Session: {analysis.session_id}")
            logger.info(f"Created: {analysis.created_at}")
            
            # Check if opportunities already exist for this analysis
            existing_opportunities = db.query(AutomationOpportunity).filter(
                AutomationOpportunity.analysis_id == analysis.id
            ).count()
            
            if existing_opportunities > 0:
                logger.info(f"⏭️ SKIPPING: {existing_opportunities} opportunities already exist")
                continue
            
            # Extract structured insights
            if not analysis.structured_insights:
                logger.warning(f"⚠️ SKIPPING: No structured_insights found")
                continue
            
            insights = analysis.structured_insights
            if isinstance(insights, str):
                try:
                    insights = json.loads(insights)
                except:
                    logger.error(f"❌ SKIPPING: Invalid JSON in structured_insights")
                    continue
            
            if not isinstance(insights, dict):
                logger.warning(f"⚠️ SKIPPING: structured_insights is not a dict")
                continue
            
            # Extract automation opportunities
            automation_opportunities = insights.get("automation_opportunities", [])
            
            if not isinstance(automation_opportunities, list) or not automation_opportunities:
                logger.warning(f"⚠️ SKIPPING: No automation_opportunities found in insights")
                continue
            
            logger.info(f"📝 Found {len(automation_opportunities)} opportunities to create")
            
            created_opportunities = 0
            for i, opportunity_data in enumerate(automation_opportunities):
                try:
                    # Extract opportunity details
                    workflow_type = opportunity_data.get("workflow_type", "Unknown")
                    description = opportunity_data.get("description", "")
                    
                    # Convert time values to standard formats
                    time_per_occurrence_minutes = opportunity_data.get("time_per_occurrence_minutes", 0)
                    time_per_occurrence_seconds = int(time_per_occurrence_minutes * 60)
                    
                    frequency_daily = opportunity_data.get("frequency_daily", 1)
                    time_saved_weekly_hours = opportunity_data.get("time_saved_weekly_hours", 0)
                    cost_saved_annually = opportunity_data.get("cost_saved_annually", 0)
                    
                    # Get confidence score from analysis
                    confidence_score = analysis.confidence_score or 0
                    
                    # Create AutomationOpportunity record
                    opportunity = AutomationOpportunity(
                        analysis_id=analysis.id,
                        session_id=analysis.session_id,
                        opportunity_type=workflow_type,
                        title=f"{workflow_type} Automation",
                        description=description,
                        workflow_steps=[],  # TODO: Extract workflow steps if available
                        current_time_per_occurrence_seconds=time_per_occurrence_seconds,
                        occurrences_per_day=frequency_daily,
                        automation_complexity=opportunity_data.get("implementation_complexity", "medium"),
                        implementation_effort_hours=24,  # Default estimate
                        estimated_cost_savings_monthly=round(cost_saved_annually / 12, 2) if cost_saved_annually > 0 else 0,
                        estimated_implementation_cost=2000.00,  # Default estimate
                        roi_percentage=round((cost_saved_annually / 2000.00) * 100, 2) if cost_saved_annually > 0 else 0,
                        payback_period_days=int((2000.00 / (cost_saved_annually / 365))) if cost_saved_annually > 0 else 365,
                        confidence_score=confidence_score,
                        priority=opportunity_data.get("priority_score", "medium"),
                        record_metadata=opportunity_data  # Store full opportunity data
                    )
                    
                    db.add(opportunity)
                    created_opportunities += 1
                    total_opportunities_created += 1
                    logger.info(f"✅ OPPORTUNITY #{i+1}: {workflow_type} - ${cost_saved_annually}/year savings")
                    
                except Exception as e:
                    logger.error(f"❌ OPPORTUNITY #{i+1} FAILED: {e}")
                    continue
            
            if created_opportunities > 0:
                # Commit opportunities for this analysis
                try:
                    db.commit()
                    logger.info(f"💾 COMMITTED: {created_opportunities} opportunities for analysis {analysis.id}")
                    analyses_processed += 1
                except Exception as e:
                    logger.error(f"💥 COMMIT FAILED for analysis {analysis.id}: {e}")
                    db.rollback()
            else:
                logger.warning(f"⚠️ NO OPPORTUNITIES CREATED for analysis {analysis.id}")
        
        db.close()
        
        # Verify the results
        logger.info(f"\n📊 BACKFILL COMPLETE")
        logger.info(f"  Analyses processed: {analyses_processed}")
        logger.info(f"  Total opportunities created: {total_opportunities_created}")
        
        # Check final counts
        db = get_sync_db()
        final_opportunity_count = db.query(AutomationOpportunity).count()
        db.close()
        
        logger.info(f"  Final AutomationOpportunity count: {final_opportunity_count}")
        
        return {
            "success": True,
            "analyses_processed": analyses_processed,
            "opportunities_created": total_opportunities_created,
            "final_opportunity_count": final_opportunity_count
        }
        
    except Exception as e:
        logger.error(f"💥 BACKFILL FAILED: {e}", exc_info=True)
        return {"success": False, "error": str(e)}

def verify_backfill_results() -> Dict[str, Any]:
    """Verify that backfill worked correctly"""
    logger.info("\n🔍 VERIFYING BACKFILL RESULTS")
    
    try:
        from app.core.database import get_sync_db
        from app.models.database import AnalysisResult, AutomationOpportunity
        
        db = get_sync_db()
        
        # Get counts
        total_analyses = db.query(AnalysisResult).filter(
            AnalysisResult.status == "completed"
        ).count()
        total_opportunities = db.query(AutomationOpportunity).count()
        
        # Check some sample opportunities
        sample_opportunities = db.query(AutomationOpportunity).limit(3).all()
        
        logger.info(f"📊 Final Verification:")
        logger.info(f"  Completed analyses: {total_analyses}")
        logger.info(f"  Total opportunities: {total_opportunities}")
        
        for i, opp in enumerate(sample_opportunities, 1):
            logger.info(f"\n--- Sample Opportunity #{i} ---")
            logger.info(f"  ID: {opp.id}")
            logger.info(f"  Analysis ID: {opp.analysis_id}")
            logger.info(f"  Type: {opp.opportunity_type}")
            logger.info(f"  Title: {opp.title}")
            logger.info(f"  Annual Savings: ${opp.estimated_cost_savings_monthly * 12}")
            logger.info(f"  ROI: {opp.roi_percentage}%")
            logger.info(f"  Confidence: {opp.confidence_score}")
        
        db.close()
        
        return {
            "total_analyses": total_analyses,
            "total_opportunities": total_opportunities,
            "sample_count": len(sample_opportunities)
        }
        
    except Exception as e:
        logger.error(f"💥 VERIFICATION FAILED: {e}", exc_info=True)
        return {"error": str(e)}

if __name__ == "__main__":
    logger.info("🚀 STARTING AUTOMATION OPPORTUNITIES BACKFILL PROCESS")
    logger.info("=" * 80)
    
    # Run backfill
    backfill_result = backfill_automation_opportunities()
    
    if backfill_result.get("success"):
        logger.info("✅ BACKFILL SUCCESSFUL")
        
        # Verify results
        verification_result = verify_backfill_results()
        
        if "error" not in verification_result:
            logger.info("✅ VERIFICATION SUCCESSFUL")
            logger.info(f"\n🎯 FINAL RESULTS:")
            logger.info(f"  {verification_result['total_opportunities']} automation opportunities now exist")
            logger.info(f"  {verification_result['total_analyses']} completed analyses in database")
            logger.info(f"  Average: {verification_result['total_opportunities'] / max(verification_result['total_analyses'], 1):.1f} opportunities per analysis")
        else:
            logger.error("❌ VERIFICATION FAILED")
    else:
        logger.error("❌ BACKFILL FAILED")
        logger.error(f"Error: {backfill_result.get('error')}")
    
    logger.info(f"\n🏁 Backfill process completed at {datetime.now().isoformat()}")