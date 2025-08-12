#!/usr/bin/env python3
"""
Configuration and Dependency Verification Script for NewSystem.AI
Diagnoses why Supabase tables remain empty despite analysis pipeline existing
Part of Phase 1: Layer 2 Intelligence debugging
"""

import os
import sys
import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

# Set up logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'backend'))

# Load .env file from project root
from dotenv import load_dotenv
env_path = project_root / '.env'
if env_path.exists():
    load_dotenv(env_path)
    logger.info(f"Loaded environment from: {env_path}")
else:
    logger.warning(f"No .env file found at: {env_path}")

async def check_environment_variables() -> Dict[str, Any]:
    """Check all required environment variables"""
    logger.info("🔍 CHECKING ENVIRONMENT VARIABLES")
    
    required_vars = {
        "OPENAI_API_KEY": "OpenAI API access for GPT-4o",
        "SUPABASE_URL": "Supabase database connection",
        "SUPABASE_SERVICE_KEY": "Supabase service key for database writes",
        "GPT4V_MODEL": "GPT-4o model specification",
        "MAX_TOKENS_PER_REQUEST": "Maximum tokens per GPT-4o request",
        "GPT4V_TEMPERATURE": "GPT-4o temperature setting",
        "GPT4V_IMAGE_DETAIL": "GPT-4o image detail level"
    }
    
    optional_vars = {
        "FRAME_EXTRACTION_MODE": "Frame extraction configuration",
        "DEFAULT_FRAMES_PER_SECOND": "Frame extraction rate",
        "COST_PER_GPT4V_REQUEST": "Cost tracking configuration"
    }
    
    results = {
        "all_required_present": True,
        "missing_required": [],
        "present_required": [],
        "optional_vars": {},
        "issues": []
    }
    
    # Check required variables
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            results["present_required"].append({
                "name": var,
                "description": description,
                "length": len(value),
                "masked_value": f"{value[:8]}..." if len(value) > 8 else "***"
            })
            logger.info(f"  ✅ {var}: {description} (length: {len(value)})")
        else:
            results["missing_required"].append({
                "name": var,
                "description": description
            })
            results["all_required_present"] = False
            results["issues"].append(f"Missing required environment variable: {var}")
            logger.error(f"  ❌ {var}: MISSING - {description}")
    
    # Check optional variables
    for var, description in optional_vars.items():
        value = os.getenv(var)
        results["optional_vars"][var] = {
            "present": bool(value),
            "value": value,
            "description": description
        }
        status = "✅" if value else "⚠️"
        logger.info(f"  {status} {var}: {value or 'NOT SET'} - {description}")
    
    return results

async def check_openai_configuration() -> Dict[str, Any]:
    """Test OpenAI API configuration and connectivity"""
    logger.info("🤖 CHECKING OPENAI CONFIGURATION")
    
    try:
        from app.services.analysis.gpt4v_client import get_gpt4v_client
        
        client = get_gpt4v_client()
        validation = client.validate_configuration()
        
        logger.info(f"  📋 Model: {validation.get('model', 'UNKNOWN')}")
        logger.info(f"  🎯 Max Tokens: {validation.get('max_tokens', 'UNKNOWN')}")
        logger.info(f"  💰 Cost Per Image: ${validation.get('cost_per_image', 'UNKNOWN')}")
        
        if validation.get("configured"):
            logger.info("  ✅ OpenAI client configuration valid")
            
            # Test a simple API call to verify connectivity
            if client.client:
                try:
                    # Test with a minimal API call
                    logger.info("  🔗 Testing OpenAI API connectivity...")
                    
                    # This is a minimal test - we'll make a simple completion request
                    response = client.client.chat.completions.create(
                        model="gpt-3.5-turbo",  # Use cheaper model for test
                        messages=[{"role": "user", "content": "Hello"}],
                        max_tokens=5
                    )
                    
                    logger.info("  ✅ OpenAI API connectivity confirmed")
                    validation["api_test_success"] = True
                    validation["api_test_tokens"] = response.usage.total_tokens
                    
                except Exception as e:
                    logger.error(f"  ❌ OpenAI API test failed: {e}")
                    validation["api_test_success"] = False
                    validation["api_test_error"] = str(e)
            
        else:
            issues = validation.get("issues", [])
            for issue in issues:
                logger.error(f"  ❌ {issue}")
        
        return validation
        
    except Exception as e:
        logger.error(f"  💥 Failed to initialize OpenAI client: {e}")
        return {
            "configured": False,
            "error": str(e),
            "issues": [f"Failed to initialize GPT4V client: {e}"]
        }

async def check_database_configuration() -> Dict[str, Any]:
    """Test database configuration and connectivity"""
    logger.info("🗄️ CHECKING DATABASE CONFIGURATION")
    
    results = {
        "config_loaded": False,
        "connection_success": False,
        "tables_accessible": False,
        "issues": []
    }
    
    try:
        # Test config loading
        from app.core.config import settings
        
        # Check if Supabase configuration is present
        supabase_configured = bool(settings.SUPABASE_URL and settings.SUPABASE_SERVICE_KEY)
        logger.info(f"  📋 Supabase configured: {'✅' if supabase_configured else '❌'}")
        
        if supabase_configured:
            logger.info(f"  🔗 Supabase URL: {settings.SUPABASE_URL}")
            logger.info(f"  🔑 Service Key: {'✅ Present' if settings.SUPABASE_SERVICE_KEY else '❌ Missing'}")
            results["config_loaded"] = True
        else:
            results["issues"].append("Supabase configuration incomplete")
            
    except Exception as e:
        logger.error(f"  ❌ Failed to load database config: {e}")
        results["issues"].append(f"Config loading failed: {e}")
        return results
    
    try:
        # Test database connection
        from app.core.database import get_db
        
        logger.info("  🔗 Testing database connection...")
        db = next(get_db())
        
        # Test basic query
        from app.models.database import RecordingSession
        count = db.query(RecordingSession).count()
        
        logger.info(f"  ✅ Database connection successful")
        logger.info(f"  📊 RecordingSession count: {count}")
        results["connection_success"] = True
        
        # Test access to analysis tables
        from app.models.database import AnalysisResult, AutomationOpportunity
        
        analysis_count = db.query(AnalysisResult).count()
        opportunities_count = db.query(AutomationOpportunity).count()
        
        logger.info(f"  📊 AnalysisResult count: {analysis_count}")
        logger.info(f"  📊 AutomationOpportunity count: {opportunities_count}")
        
        if analysis_count == 0 and opportunities_count == 0:
            logger.warning("  ⚠️ Analysis tables are empty - this is the core issue!")
            results["issues"].append("Analysis tables are empty despite pipeline existing")
        
        results["tables_accessible"] = True
        results["record_counts"] = {
            "recording_sessions": count,
            "analysis_results": analysis_count,
            "automation_opportunities": opportunities_count
        }
        
        db.close()
        
    except Exception as e:
        logger.error(f"  ❌ Database connection failed: {e}")
        results["issues"].append(f"Database connection failed: {e}")
        
    return results

async def check_orchestrator_initialization() -> Dict[str, Any]:
    """Test analysis orchestrator initialization"""
    logger.info("🎭 CHECKING ANALYSIS ORCHESTRATOR")
    
    results = {
        "orchestrator_init": False,
        "frame_extractor": False,
        "gpt4v_client": False,
        "result_parser": False,
        "issues": []
    }
    
    try:
        from app.services.analysis import get_orchestrator
        
        logger.info("  🎯 Initializing orchestrator...")
        orchestrator = get_orchestrator()
        results["orchestrator_init"] = True
        logger.info("  ✅ Orchestrator initialized successfully")
        
        # Check individual components
        if hasattr(orchestrator, 'frame_extractor') and orchestrator.frame_extractor:
            results["frame_extractor"] = True
            logger.info("  ✅ Frame extractor component loaded")
        else:
            results["issues"].append("Frame extractor not properly initialized")
            logger.error("  ❌ Frame extractor component missing")
            
        if hasattr(orchestrator, 'gpt4v_client') and orchestrator.gpt4v_client:
            results["gpt4v_client"] = True
            logger.info("  ✅ GPT4V client component loaded")
        else:
            results["issues"].append("GPT4V client not properly initialized")
            logger.error("  ❌ GPT4V client component missing")
            
        if hasattr(orchestrator, 'result_parser') and orchestrator.result_parser:
            results["result_parser"] = True
            logger.info("  ✅ Result parser component loaded")
        else:
            results["issues"].append("Result parser not properly initialized")
            logger.error("  ❌ Result parser component missing")
        
        # Test prerequisite validation
        try:
            logger.info("  🔍 Testing prerequisite validation...")
            from uuid import uuid4
            test_session_id = uuid4()
            
            validation = await orchestrator.validate_prerequisites(test_session_id)
            
            if validation.get("ready"):
                logger.info("  ✅ All prerequisites met for analysis")
                results["prerequisites_ready"] = True
            else:
                issues = validation.get("issues", [])
                logger.warning(f"  ⚠️ Prerequisites not met: {issues}")
                results["prerequisites_ready"] = False
                results["prerequisite_issues"] = issues
                results["issues"].extend(issues)
                
        except Exception as e:
            logger.error(f"  ❌ Prerequisite validation failed: {e}")
            results["issues"].append(f"Prerequisite validation failed: {e}")
        
    except Exception as e:
        logger.error(f"  💥 Orchestrator initialization failed: {e}")
        results["issues"].append(f"Orchestrator initialization failed: {e}")
        
    return results

async def check_api_endpoints() -> Dict[str, Any]:
    """Test API endpoint accessibility"""
    logger.info("🌐 CHECKING API ENDPOINTS")
    
    results = {
        "analysis_module": False,
        "endpoints_accessible": False,
        "issues": []
    }
    
    try:
        # Test if analysis module can be imported
        from app.api.v1 import analysis
        results["analysis_module"] = True
        logger.info("  ✅ Analysis API module imports successfully")
        
        # Check if FastAPI router is properly configured
        if hasattr(analysis, 'router'):
            logger.info("  ✅ Analysis router configured")
            results["endpoints_accessible"] = True
            
            # List available routes
            if hasattr(analysis.router, 'routes'):
                routes = []
                for route in analysis.router.routes:
                    if hasattr(route, 'path') and hasattr(route, 'methods'):
                        routes.append(f"{list(route.methods)} {route.path}")
                
                logger.info(f"  📋 Available routes: {routes}")
                results["available_routes"] = routes
        else:
            results["issues"].append("Analysis router not found")
            logger.error("  ❌ Analysis router not configured")
            
    except Exception as e:
        logger.error(f"  💥 API endpoint check failed: {e}")
        results["issues"].append(f"API endpoint check failed: {e}")
        
    return results

async def run_comprehensive_diagnosis() -> Dict[str, Any]:
    """Run complete system diagnosis"""
    logger.info("🔧 STARTING COMPREHENSIVE SYSTEM DIAGNOSIS")
    logger.info("=" * 80)
    
    diagnosis = {
        "timestamp": datetime.now().isoformat(),
        "overall_status": "unknown",
        "critical_issues": [],
        "warnings": [],
        "components": {}
    }
    
    # Run all checks
    checks = [
        ("environment", check_environment_variables()),
        ("openai", check_openai_configuration()),
        ("database", check_database_configuration()),
        ("orchestrator", check_orchestrator_initialization()),
        ("api_endpoints", check_api_endpoints())
    ]
    
    for check_name, check_coro in checks:
        logger.info(f"\n{'=' * 40}")
        try:
            result = await check_coro
            diagnosis["components"][check_name] = result
            
            # Collect issues
            if "issues" in result and result["issues"]:
                diagnosis["critical_issues"].extend(result["issues"])
                
        except Exception as e:
            logger.error(f"💥 {check_name.upper()} CHECK FAILED: {e}")
            diagnosis["components"][check_name] = {
                "error": str(e),
                "success": False
            }
            diagnosis["critical_issues"].append(f"{check_name} check failed: {e}")
    
    # Determine overall status
    if not diagnosis["critical_issues"]:
        diagnosis["overall_status"] = "healthy"
        logger.info("\n✅ SYSTEM DIAGNOSIS: ALL CHECKS PASSED")
    elif len(diagnosis["critical_issues"]) <= 2:
        diagnosis["overall_status"] = "issues_found"
        logger.warning(f"\n⚠️ SYSTEM DIAGNOSIS: {len(diagnosis['critical_issues'])} ISSUES FOUND")
    else:
        diagnosis["overall_status"] = "critical"
        logger.error(f"\n❌ SYSTEM DIAGNOSIS: {len(diagnosis['critical_issues'])} CRITICAL ISSUES")
    
    # Summary report
    logger.info("\n" + "=" * 80)
    logger.info("🎯 DIAGNOSIS SUMMARY")
    logger.info("=" * 80)
    
    if diagnosis["critical_issues"]:
        logger.error("CRITICAL ISSUES TO FIX:")
        for i, issue in enumerate(diagnosis["critical_issues"], 1):
            logger.error(f"  {i}. {issue}")
    else:
        logger.info("✅ All configuration checks passed!")
    
    # Component status summary
    logger.info("\nCOMPONENT STATUS:")
    for component, result in diagnosis["components"].items():
        if result.get("error"):
            logger.error(f"  ❌ {component.upper()}: FAILED")
        elif component == "environment" and result.get("all_required_present"):
            logger.info(f"  ✅ {component.upper()}: ALL REQUIRED VARS PRESENT")
        elif component == "openai" and result.get("configured"):
            logger.info(f"  ✅ {component.upper()}: CONFIGURED")
        elif component == "database" and result.get("connection_success"):
            logger.info(f"  ✅ {component.upper()}: CONNECTED")
        elif component == "orchestrator" and result.get("orchestrator_init"):
            logger.info(f"  ✅ {component.upper()}: INITIALIZED")
        elif component == "api_endpoints" and result.get("endpoints_accessible"):
            logger.info(f"  ✅ {component.upper()}: ACCESSIBLE")
        else:
            logger.warning(f"  ⚠️ {component.upper()}: PARTIAL SUCCESS")
    
    return diagnosis

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Diagnose NewSystem.AI configuration issues")
    parser.add_argument("--save-report", help="Save diagnosis report to file")
    args = parser.parse_args()
    
    # Run diagnosis
    diagnosis = asyncio.run(run_comprehensive_diagnosis())
    
    # Save report if requested
    if args.save_report:
        import json
        with open(args.save_report, 'w') as f:
            json.dump(diagnosis, f, indent=2, default=str)
        logger.info(f"📄 Diagnosis report saved to: {args.save_report}")
    
    # Exit with appropriate code
    if diagnosis["overall_status"] == "healthy":
        sys.exit(0)
    elif diagnosis["overall_status"] == "issues_found":
        sys.exit(1)  
    else:
        sys.exit(2)  # Critical issues