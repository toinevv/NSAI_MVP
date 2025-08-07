"""
Logistics-Specific Prompts for GPT-4V Analysis
Focused on email → WMS workflow detection and automation opportunities
Pragmatic MVP approach targeting warehouse operations
"""

# System prompt establishing logistics expertise
SYSTEM_PROMPT_LOGISTICS = """You are an expert logistics workflow analyst specializing in warehouse operations and automation opportunities.

Your primary focus is identifying repetitive manual tasks that operators perform daily, especially:
1. Email to WMS (Warehouse Management System) data entry
2. Copy-paste operations between applications
3. Manual report generation
4. Repetitive form filling
5. Data validation and verification tasks

You have deep knowledge of:
- Common WMS interfaces (SAP, Oracle WMS, Manhattan, Blue Yonder)
- Email clients (Outlook, Gmail)
- Spreadsheet applications (Excel, Google Sheets)
- ERP systems
- Logistics-specific workflows

Provide analysis in structured JSON format with specific, actionable insights."""

# Main analysis prompt for workflow detection
WORKFLOW_ANALYSIS_PROMPT = """Analyze these screenshots from a warehouse operator's screen recording to identify automation opportunities.

For each distinct workflow you observe:

1. **Application Detection**: Identify all applications being used (email clients, WMS, Excel, etc.)

2. **Workflow Patterns**: Detect repetitive patterns, especially:
   - Email → WMS data entry (our PRIMARY focus - operators do this 15x daily)
   - Copy-paste operations
   - Manual form filling
   - Tab switching patterns
   - Repetitive clicking sequences

3. **Time Analysis**: Estimate time spent on each activity based on the timestamps

4. **Automation Opportunities**: For each pattern found, assess:
   - Frequency (how often this likely occurs daily)
   - Time per occurrence
   - Automation potential (high/medium/low)
   - Implementation complexity

5. **Specific Data Points**: Extract:
   - Types of data being copied (order numbers, quantities, addresses)
   - Number of fields being filled
   - Number of clicks/actions per workflow

Return analysis as JSON with this EXACT structure:
{
  "workflows_detected": [
    {
      "type": "email_to_wms" | "excel_reporting" | "data_validation" | "other",
      "description": "Clear description of the workflow",
      "applications_involved": ["Application names"],
      "steps_observed": ["Step 1", "Step 2", ...],
      "estimated_duration_seconds": 120,
      "data_types_handled": ["order_numbers", "quantities", "addresses"],
      "repetitive_score": 0.9
    }
  ],
  "automation_opportunities": [
    {
      "workflow_type": "email_to_wms",
      "description": "Automate order entry from email to WMS",
      "frequency_daily": 15,
      "time_per_occurrence_minutes": 2,
      "total_time_saved_daily_minutes": 30,
      "automation_potential": "high",
      "implementation_complexity": "low",
      "specific_recommendation": "Use RPA to read order emails and auto-populate WMS forms"
    }
  ],
  "time_breakdown": {
    "total_time_analyzed_seconds": 300,
    "email_time_seconds": 60,
    "wms_time_seconds": 180,
    "excel_time_seconds": 60,
    "idle_time_seconds": 0
  },
  "key_insights": [
    "Operator spends 60% of time on manual data entry",
    "15 email-to-WMS transfers detected in this session",
    "Same 5 fields copied repeatedly"
  ],
  "confidence_score": 0.85
}

Focus especially on EMAIL → WMS workflows as these represent the highest ROI for automation in logistics."""

# Prompt for email to WMS specific analysis
EMAIL_TO_WMS_PROMPT = """Focus specifically on email to WMS data entry workflows in these screenshots.

Identify:
1. Email client used (Outlook, Gmail, etc.)
2. WMS system interface
3. Specific data fields being copied:
   - Order numbers
   - Customer information
   - Product codes/SKUs
   - Quantities
   - Delivery addresses
   - Special instructions

4. Manual steps involved:
   - Opening email
   - Selecting/copying text
   - Switching to WMS
   - Finding correct form/screen
   - Pasting/typing data
   - Validation steps

Return JSON:
{
  "email_client": "Outlook",
  "wms_system": "SAP WMS",
  "fields_transferred": [
    {"field_name": "order_number", "copy_method": "manual_copy_paste"},
    {"field_name": "quantity", "copy_method": "manual_typing"}
  ],
  "steps_count": 8,
  "estimated_time_seconds": 120,
  "error_prone_steps": ["Manual quantity entry", "Address formatting"],
  "automation_feasibility": "high",
  "recommended_solution": "Email parser with WMS API integration"
}"""

# Prompt for ROI calculation
ROI_CALCULATION_PROMPT = """Based on the workflows observed, calculate the ROI of automation:

Consider:
1. Time saved per automation (minutes/hours daily)
2. Operator hourly rate (~$25/hour for warehouse staff)
3. Error reduction value (fewer mistakes = less rework)
4. Implementation cost estimates

Return JSON:
{
  "current_state": {
    "manual_hours_weekly": 10,
    "manual_cost_weekly": 250,
    "error_rate_percentage": 5
  },
  "automated_state": {
    "manual_hours_weekly": 2,
    "manual_cost_weekly": 50,
    "error_rate_percentage": 1
  },
  "savings": {
    "hours_saved_weekly": 8,
    "cost_saved_weekly": 200,
    "cost_saved_annually": 10400
  },
  "implementation": {
    "estimated_cost": 5000,
    "payback_period_months": 6
  }
}"""

# Prompt for pattern detection
PATTERN_DETECTION_PROMPT = """Identify repetitive patterns in these workflow screenshots:

Look for:
1. Repeated sequences of actions
2. Same applications used in cycles
3. Similar data being processed multiple times
4. Consistent navigation paths
5. Repeated form filling patterns

Return patterns ranked by frequency and automation potential."""

# Prompt for quick analysis (fewer tokens)
QUICK_ANALYSIS_PROMPT = """Quick analysis of these warehouse operator screenshots:

Identify:
1. Main workflow type (email→WMS, reporting, etc.)
2. Time-saving opportunity (high/medium/low)
3. Recommended automation

Return brief JSON:
{
  "workflow": "email_to_wms",
  "automation_potential": "high",
  "time_saved_daily_minutes": 30,
  "recommendation": "Implement email-to-WMS automation"
}"""

# Function to get appropriate prompt based on analysis type
def get_analysis_prompt(analysis_type: str = "full") -> tuple[str, str]:
    """
    Get appropriate prompts for analysis type
    
    Args:
        analysis_type: Type of analysis ("full", "email_wms", "roi", "quick")
    
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    prompts_map = {
        "full": (SYSTEM_PROMPT_LOGISTICS, WORKFLOW_ANALYSIS_PROMPT),
        "email_wms": (SYSTEM_PROMPT_LOGISTICS, EMAIL_TO_WMS_PROMPT),
        "roi": (SYSTEM_PROMPT_LOGISTICS, ROI_CALCULATION_PROMPT),
        "pattern": (SYSTEM_PROMPT_LOGISTICS, PATTERN_DETECTION_PROMPT),
        "quick": (SYSTEM_PROMPT_LOGISTICS, QUICK_ANALYSIS_PROMPT)
    }
    
    return prompts_map.get(analysis_type, prompts_map["full"])

# Validation prompt for testing
TEST_PROMPT = """This is a test analysis. Identify any UI elements you can see and confirm the image was received correctly.

Return JSON:
{
  "test_successful": true,
  "elements_detected": ["List of UI elements seen"],
  "image_quality": "good|medium|poor"
}"""