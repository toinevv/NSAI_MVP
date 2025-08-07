"""
Enhanced Prompts for Open-Ended Workflow Discovery
Focus: Discover ANY logistics operator workflow, not just email → WMS
Goal: Understand what operators ACTUALLY do, without assumptions
"""

# Enhanced system prompt for comprehensive workflow understanding
SYSTEM_PROMPT_DISCOVERY = """You are an expert logistics workflow analyst with a discovery-first mindset.

Your mission is to DISCOVER and UNDERSTAND all operator workflows without assumptions. You recognize that logistics operations involve diverse, complex patterns beyond simple data entry.

Core Principles:
1. OBSERVE first, categorize second - don't force patterns into predefined boxes
2. Every repetitive action is valuable - from major workflows to micro-optimizations
3. Operators are experts - their workflows contain hidden business logic
4. Context matters - understand WHY actions are taken, not just WHAT

You have expertise in:
- Warehouse Management Systems (WMS): SAP, Oracle, Manhattan, Blue Yonder, and custom systems
- Transportation Management Systems (TMS): Various platforms
- Enterprise Resource Planning (ERP): SAP, Oracle, Microsoft Dynamics
- Communication Tools: Email, Teams, Slack, phone systems
- Data Tools: Excel, Google Sheets, BI dashboards
- Specialized Logistics Software: Route planning, inventory management, yard management
- Paper-based Processes: Printouts, manual logs, physical signatures

Provide analysis in structured JSON format capturing the COMPLETE picture of operator work."""

# Comprehensive workflow discovery prompt
WORKFLOW_DISCOVERY_PROMPT = """Analyze these screenshots to discover ALL workflows and patterns in this operator's work.

DO NOT ASSUME you know what the operator does. DISCOVER it through observation.

Analyze EVERYTHING you observe:

1. **Application Ecosystem Mapping**
   - List EVERY application, browser tab, and window visible
   - Note switching patterns between applications
   - Identify primary vs supporting applications
   - Track time spent in each application

2. **Workflow Pattern Discovery** (Be comprehensive!):
   - Data Entry Patterns:
     * System-to-system transfers (ANY combination)
     * Manual typing vs copy-paste vs auto-fill
     * Form filling sequences
     * Bulk operations vs single entries
   
   - Information Lookup Patterns:
     * Cross-referencing between systems
     * Search operations and filters used
     * Status checking and monitoring
     * Verification and validation steps
   
   - Communication Patterns:
     * Email reading/writing patterns
     * Chat/messaging interactions
     * Phone + system coordination
     * Screenshot creation and sharing
   
   - Navigation Patterns:
     * Menu navigation paths
     * Bookmark/favorite usage
     * Keyboard shortcuts vs mouse clicks
     * Tab management strategies
   
   - Decision-Making Patterns:
     * Information gathering before decisions
     * Approval/rejection workflows
     * Exception handling processes
     * Priority/urgency assessment

3. **Unknown Pattern Detection**
   - Flag any repetitive sequences you can't categorize
   - Note patterns that seem inefficient or unusual
   - Identify "workarounds" (complex steps for simple tasks)

4. **Micro-Workflow Identification**
   - Small repetitive tasks (< 30 seconds)
   - Frequent corrections or adjustments
   - Copy-paste of specific fields
   - Repeated searches or filters

5. **Time and Frequency Analysis**
   - Actual time per action/workflow
   - Estimated daily/weekly frequency
   - Time gaps (waiting, loading, thinking)
   - Peak activity periods

6. **Data Flow Mapping**
   - What data moves between systems?
   - Data transformation (formatting, parsing)
   - Manual data enrichment or correction
   - Data validation steps

7. **Context and Business Logic**
   - Why might they be doing this?
   - What business rules are being applied?
   - What exceptions are being handled?

Return comprehensive JSON analysis:
{
  "session_overview": {
    "total_duration_seconds": 0,
    "applications_used": ["List all applications"],
    "primary_activity": "Overall theme of the session",
    "workflow_complexity": "simple|moderate|complex|highly_complex"
  },
  
  "discovered_workflows": [
    {
      "workflow_id": "WF001",
      "pattern_type": "data_entry|lookup|communication|reporting|navigation|decision|unknown",
      "confidence_level": 0.95,
      "description": "Detailed description of what operator is doing",
      "business_purpose": "Why this workflow exists (best guess)",
      "applications_involved": ["App1", "App2"],
      "steps_observed": [
        {
          "step": 1,
          "action": "Specific action taken",
          "application": "Where it happened",
          "data_involved": "What data was used/created",
          "time_seconds": 5
        }
      ],
      "frequency_indicators": {
        "observed_count": 3,
        "estimated_daily": 15,
        "pattern_regularity": "consistent|variable"
      },
      "inefficiency_indicators": [
        "Multiple tab switches for same data",
        "Manual retyping of visible information"
      ],
      "automation_potential": {
        "score": 0.8,
        "blockers": ["Requires human judgment", "System limitations"],
        "quick_wins": ["Auto-fill this field", "Direct API connection"]
      }
    }
  ],
  
  "unknown_patterns": [
    {
      "pattern_id": "UP001",
      "description": "Operator repeatedly does X then Y then Z",
      "frequency": "Observed 5 times",
      "needs_clarification": "What is the purpose of this sequence?",
      "time_impact": "2 minutes per occurrence"
    }
  ],
  
  "application_insights": {
    "primary_systems": {
      "Application_Name": {
        "time_spent_seconds": 120,
        "primary_use": "Data entry|Lookup|Reporting",
        "efficiency_score": 0.7,
        "pain_points": ["Slow loading", "Many clicks required"]
      }
    },
    "integration_opportunities": [
      {
        "systems": ["System A", "System B"],
        "data_overlap": "Order numbers, customer info",
        "current_method": "Manual copy-paste",
        "potential_solution": "Direct integration or RPA"
      }
    ]
  },
  
  "data_patterns": {
    "frequently_accessed_data": ["Order numbers", "Customer names", "Tracking IDs"],
    "data_transformations": ["Formatting addresses", "Parsing email content"],
    "validation_steps": ["Checking inventory", "Verifying addresses"],
    "error_corrections": ["Fixed typo in address", "Updated quantity"]
  },
  
  "time_analysis": {
    "productive_time": 240,
    "waiting_time": 30,
    "navigation_time": 45,
    "correction_time": 15,
    "highest_impact_workflows": [
      {
        "workflow_id": "WF001",
        "total_time_seconds": 180,
        "optimization_potential_seconds": 120
      }
    ]
  },
  
  "operator_expertise_observed": {
    "shortcuts_used": ["Ctrl+C/V", "Tab navigation"],
    "workarounds_developed": ["Using notepad as temporary storage"],
    "domain_knowledge": ["Knows which fields are critical", "Skips unnecessary steps"],
    "efficiency_techniques": ["Batches similar tasks", "Pre-opens required tabs"]
  },
  
  "recommendations": {
    "immediate_wins": [
      {
        "action": "Implement auto-fill for recurring data",
        "time_saved_daily_minutes": 15,
        "complexity": "low"
      }
    ],
    "strategic_improvements": [
      {
        "action": "Integrate System A with System B",
        "time_saved_daily_minutes": 45,
        "complexity": "medium"
      }
    ],
    "training_opportunities": [
      "Keyboard shortcuts could save 5 min/day",
      "Bulk operations feature not being used"
    ]
  },
  
  "confidence_score": 0.85,
  "analysis_notes": "Any observations about video quality, incomplete workflows, or assumptions made"
}

IMPORTANT: 
- Do NOT force patterns into email→WMS category unless that's actually what you see
- DO capture every small inefficiency - they add up
- DO note workarounds and unusual patterns - they reveal system limitations
- DO recognize operator expertise and smart shortcuts - these should be preserved"""

# Prompt for pattern clustering and categorization
PATTERN_CLUSTERING_PROMPT = """Analyze these workflow patterns and cluster them into logical groups.

Group patterns by:
1. Business objective (what goal they achieve)
2. Systems involved (which applications are used)
3. Data type (what information is being processed)
4. Frequency (how often they occur)
5. Complexity (number of steps/decisions)

For unnamed patterns, suggest descriptive names based on observed behavior.

Return JSON:
{
  "pattern_clusters": [
    {
      "cluster_name": "Order Processing Workflows",
      "pattern_count": 5,
      "total_time_daily_minutes": 120,
      "common_characteristics": ["Involves WMS", "Order data", "Customer communication"],
      "patterns": ["WF001", "WF003", "WF007"],
      "optimization_strategy": "Bulk processing and automation"
    }
  ],
  "suggested_names": {
    "UP001": "Inventory Verification Loop",
    "UP002": "Customer Status Check Sequence"
  }
}"""

# Prompt for multi-operator pattern comparison
TEAM_PATTERN_COMPARISON_PROMPT = """Compare workflow patterns across multiple operators to identify:

1. Common patterns everyone does
2. Unique patterns specific to individuals
3. Efficiency variations (same task, different methods)
4. Best practices to share
5. Training opportunities

Return insights for team optimization and standardization."""

# Prompt for discovering hidden business rules
BUSINESS_LOGIC_DISCOVERY_PROMPT = """Identify the hidden business rules and logic in these workflows:

Look for:
1. Decision points (if-then logic)
2. Validation criteria being applied
3. Exceptions being handled
4. Priority/urgency determinations
5. Approval hierarchies
6. Compliance checks
7. Data quality standards

These rules are often undocumented but critical for automation."""

# Function to get appropriate prompt based on analysis needs
def get_enhanced_analysis_prompt(analysis_type: str = "discovery") -> tuple[str, str]:
    """
    Get enhanced prompts for comprehensive workflow discovery
    
    Args:
        analysis_type: Type of analysis needed
    
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    prompts_map = {
        "discovery": (SYSTEM_PROMPT_DISCOVERY, WORKFLOW_DISCOVERY_PROMPT),
        "clustering": (SYSTEM_PROMPT_DISCOVERY, PATTERN_CLUSTERING_PROMPT),
        "team_comparison": (SYSTEM_PROMPT_DISCOVERY, TEAM_PATTERN_COMPARISON_PROMPT),
        "business_logic": (SYSTEM_PROMPT_DISCOVERY, BUSINESS_LOGIC_DISCOVERY_PROMPT),
        # Fallback to original prompts for backward compatibility
        "full": (SYSTEM_PROMPT_DISCOVERY, WORKFLOW_DISCOVERY_PROMPT),
    }
    
    return prompts_map.get(analysis_type, prompts_map["discovery"])

# Prompt for testing open-ended discovery
DISCOVERY_TEST_PROMPT = """This is a discovery test. Describe EVERYTHING you observe without assumptions.

List:
1. Every application/window visible
2. Every action taken
3. Every pattern noticed
4. Any inefficiencies observed
5. Operator expertise demonstrated

Don't categorize - just observe and report."""