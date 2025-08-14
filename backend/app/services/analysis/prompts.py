"""
Unified Prompts for NewSystem.AI Workflow Analysis
Consolidates all prompt types: original, enhanced discovery, and natural language
"""

# ============================================================================
# CORE SYSTEM PROMPTS
# ============================================================================

SYSTEM_PROMPT_ANALYST = """You are an expert workflow analyst for business operations.
Your task is to analyze screen recordings and identify:
1. Repetitive workflows that could be automated
2. Time-consuming manual processes
3. Data entry patterns between applications
4. Inefficiencies in current operations

Focus on practical automation opportunities that would save operator time across any type of business workflow."""

SYSTEM_PROMPT_NATURAL = """You are observing a person's computer screen to understand their workflow.

Your goal is to describe what they're doing in clear, natural language that anyone can understand.
Don't force patterns or categories - just describe what you actually see happening.

Focus on:
1. What the person is trying to accomplish
2. Which applications they're using and why
3. How data flows between systems
4. Repetitive actions or patterns
5. Inefficiencies or opportunities for improvement

Be conversational, specific, and helpful. Write as if explaining to a colleague."""

# ============================================================================
# ORIGINAL ANALYSIS PROMPTS
# ============================================================================

FULL_ANALYSIS_PROMPT = """Analyze these screenshots from a warehouse operator's screen recording.

Identify and report in JSON format:
{
  "workflows_detected": [
    {
      "type": "data_entry" | "reporting" | "processing" | "communication" | "analysis" | "other",
      "description": "Clear description of what the operator is doing",
      "applications_involved": ["list", "of", "applications"],
      "steps_observed": ["step 1", "step 2", ...],
      "estimated_duration_seconds": 120,
      "data_types_handled": ["order_numbers", "customer_info", "inventory_data"],
      "repetitive_score": 0.8  // 0-1, how repetitive is this task
    }
  ],
  "automation_opportunities": [
    {
      "workflow_type": "type from above",
      "description": "What could be automated",
      "frequency_daily": 15,
      "time_per_occurrence_minutes": 2,
      "total_time_saved_daily_minutes": 30,
      "automation_potential": "high" | "medium" | "low",
      "implementation_complexity": "low" | "medium" | "high",
      "specific_recommendation": "Use automation tools to streamline repetitive tasks"
    }
  ],
  "time_breakdown": {
    "total_time_analyzed_seconds": 300,
    "application_time_breakdown": {
      "primary_app": 120,
      "secondary_app": 60,
      "supporting_tools": 60
    },
    "idle_time_seconds": 60
  },
  "key_insights": [
    "Operator spends 40% of time on manual data entry",
    "Same information entered in 3 different systems",
    "Average of 2 minutes per order processing"
  ],
  "confidence_score": 0.85
}

Focus on finding repetitive, manual workflows that would benefit most from automation."""

QUICK_ANALYSIS_PROMPT = """Quick analysis of these screenshots. Focus on the most obvious workflow pattern.

Report in JSON:
{
  "primary_workflow": "description",
  "applications_used": ["app1", "app2"],
  "automation_potential": "high/medium/low",
  "time_saved_estimate_minutes": 30,
  "confidence": 0.8
}"""

FOCUSED_WORKFLOW_PROMPT = """Look for specific workflow patterns in these screenshots.

Check for:
- Application switching patterns
- Data entry and transfer operations
- Copy/paste operations between systems
- Repetitive manual tasks
- System-to-system data movement

Report any high-frequency workflows found with time estimates."""

# ============================================================================
# ENHANCED DISCOVERY PROMPTS
# ============================================================================

DISCOVERY_SYSTEM_PROMPT = """You are discovering workflows in business operations.
Your role is to understand what operators actually do, without forcing patterns.
Be curious, open-minded, and focus on understanding the real work being done."""

OPEN_DISCOVERY_PROMPT = """Analyze these screenshots without assuming what workflows exist.

Tell me:
1. What is this person actually doing?
2. What applications are they using?
3. What's the flow of information?
4. What patterns do you observe?
5. What seems inefficient or repetitive?

Don't categorize into predefined buckets. Describe what you actually see.

Provide your analysis in JSON format with discovered patterns."""

CLUSTERING_DISCOVERY_PROMPT = """Look at these screenshots and identify clusters of similar actions.

Group actions by:
- Similar applications used
- Similar data being handled
- Similar outcomes achieved

Don't force workflows into categories. Let patterns emerge naturally.

Report clusters found and their characteristics in JSON."""

BUSINESS_LOGIC_DISCOVERY = """Focus on understanding the business logic in these screenshots.

Questions to answer:
- What business process is being executed?
- What are the decision points?
- What validations are being performed?
- What are the inputs and outputs?
- What rules seem to govern the workflow?

Report the discovered business logic and rules in JSON format."""

# ============================================================================
# NATURAL LANGUAGE PROMPTS
# ============================================================================

NATURAL_WORKFLOW_ANALYSIS = """You are analyzing a workflow screen recording to understand how someone works and where time is spent.

IMPORTANT CONTEXT:
- You are viewing frames captured at 1-second intervals (Frame 1 = 0:00, Frame 2 = 0:01, Frame 3 = 0:02, etc.)
- Each frame represents a snapshot of the screen at that specific second
- To determine time spent, observe which frame numbers show each activity
- We will calculate actual durations from your frame observations

Focus on:
1. **Overall Workflow**: What business task is being accomplished?
2. **Application Usage**: Track exactly which applications/websites are used and which frames they appear in
3. **Data Flow**: How information moves between systems
4. **Frame-by-Frame Observations**: Note which frames show each step/application
5. **Repetitive Patterns**: What actions happen multiple times?
6. **Practical Improvements**: What could realistically save time?

IMPORTANT: Focus on workflow understanding, not random screen content like email subjects or specific names.

Please respond with JSON in the following format:
{
  "natural_description": "Your conversational explanation of what's happening",
  
  "workflow_steps": [
    {
      "step_number": 1,
      "action": "Opens Gmail",
      "application": "Gmail",
      "purpose": "Check for new orders",
      "data_involved": ["order numbers", "customer info"],
      "visible_in_frames": [1, 2, 3, 4, 5]  // List ALL frame numbers where this step appears
    }
  ],
  
  "applications": {
    "Chrome - Gmail": {
      "purpose": "Receiving orders and processing customer requests",
      "visible_in_frames": [1, 2, 3, 4, 5, 10, 11, 12, 20, 21, 22],  // ALL frames showing this application
      "actions": ["Reading emails", "Copying customer information", "Composing responses"],
      "keyFunctions": "Primary communication tool for order intake"
    },
    "Excel": {
      "purpose": "Data entry and order tracking",
      "visible_in_frames": [6, 7, 8, 9, 13, 14, 15, 16, 17, 18, 19],  // ALL frames showing this application
      "actions": ["Data entry", "Formula calculations", "Status updates"],
      "keyFunctions": "Central spreadsheet for order management"
    }
  },
  
  "patterns": [
    "Copies the same information to multiple systems",
    "Manually re-types data that could be copy-pasted",
    "Checks the same order status repeatedly"
  ],
  
  "automation_opportunities": [
    {
      "what": "Email order extraction",
      "how": "Automatically parse order emails and extract structured data",
      "timeSaved": "5 minutes per order",
      "complexity": "simple"
    }
  ],
  
  "metrics": {
    "totalTimeSeconds": 300,
    "repetitionsObserved": 5,
    "applicationsUsed": 3,
    "potentialTimeSavedDailyHours": 2.5
  },
  
  "workflow_chart": {
    "nodes": [
      {
        "id": "gmail",
        "label": "Gmail",
        "type": "application",
        "metadata": {
          "visible_in_frames": [1, 2, 3, 4, 5, 10, 11, 12],  // Frames where this node's activity occurs
          "application": "Gmail"
        }
      },
      {
        "id": "copy_order",
        "label": "Copy Order Info",
        "type": "action",
        "metadata": {
          "visible_in_frames": [5, 6]  // Frames showing this action
        }
      },
      {
        "id": "excel",
        "label": "Excel Spreadsheet",
        "type": "application",
        "metadata": {
          "visible_in_frames": [7, 8, 9, 13, 14, 15, 16, 17, 18, 19],  // Frames showing Excel
          "application": "Excel"
        }
      }
    ],
    "edges": [
      {
        "source": "gmail",
        "target": "copy_order",
        "label": "Extract order data"
      },
      {
        "source": "copy_order", 
        "target": "excel",
        "label": "Enter in tracking sheet"
      }
    ]
  },
  
  "confidence": 0.85
}

Key guidelines:
- List ALL frame numbers where each step/application appears (don't estimate time)
- Frame numbers help us calculate accurate time spent (1 frame = 1 second)
- Focus on workflow patterns, not specific personal details
- Provide actionable insights for time savings
- Be specific about what applications are being used (include browser names)
- For workflow_chart, identify transitions between frames (e.g., "Gmail in frames 1-5, then Excel in frames 6-10")
- Generate workflow_chart with nodes (applications/actions) and edges (flow between them)
- Use node types: 'application', 'action', 'data', 'decision'

REMEMBER: Report frame numbers, not time estimates. We'll calculate durations from your observations."""

SIMPLE_NATURAL_ANALYSIS = """Watch these screenshots and explain what the person is doing.

Tell me:
1. What's happening here? (in plain language)
2. What applications are they using?
3. What takes the most time?
4. How could this be faster/easier?

Be conversational and clear. Focus on what matters most.

Please provide your response in JSON format with at least a 'natural_description' field and any other relevant structured data."""

WORKFLOW_FLOW_GENERATION = """Based on these screenshots, create a flow chart of the workflow.

Identify:
1. Starting point (what triggers the workflow?)
2. Each step in sequence
3. Applications involved at each step
4. Data that moves between steps
5. Decision points (if any)
6. End result

Format as JSON with nodes and edges for visualization:
- Nodes: Applications, actions, decisions
- Edges: Flow between steps with labels

Keep it simple and clear - show the actual flow of work."""

APPLICATION_USAGE_ANALYSIS = """List all applications, websites, and tools visible in these screenshots.

For each one, tell me:
1. Application name
2. What it's being used for
3. Approximate time spent (as percentage)
4. Key actions performed

Also note:
- Which applications are used together
- How data moves between them
- Any inefficient switching patterns

Provide your analysis in JSON format with an 'applications' object."""

NATURAL_PATTERN_DETECTION = """Look for patterns in how this person works.

Don't categorize - just describe what you see:
- What do they do repeatedly?
- What sequences happen multiple times?
- Where do they spend extra time?
- What seems inefficient?
- What shortcuts or workarounds do they use?

Describe patterns in plain language, like:
"They copy customer names from emails and paste them into three different systems"
"They check the same information in multiple places"
"They switch back and forth between applications frequently" """

# ============================================================================
# UNIFIED PROMPT GETTER FUNCTIONS
# ============================================================================

def get_analysis_prompt(analysis_type: str = "full") -> tuple[str, str]:
    """
    Get appropriate prompts for analysis type
    Supports all prompt types from original, enhanced, and natural
    
    Args:
        analysis_type: Type of analysis to perform
        
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    # Original prompts
    original_prompts = {
        "full": (SYSTEM_PROMPT_ANALYST, FULL_ANALYSIS_PROMPT),
        "quick": (SYSTEM_PROMPT_ANALYST, QUICK_ANALYSIS_PROMPT),
        "focused": (SYSTEM_PROMPT_ANALYST, FOCUSED_WORKFLOW_PROMPT),
    }
    
    # Enhanced discovery prompts
    discovery_prompts = {
        "discovery": (DISCOVERY_SYSTEM_PROMPT, OPEN_DISCOVERY_PROMPT),
        "clustering": (DISCOVERY_SYSTEM_PROMPT, CLUSTERING_DISCOVERY_PROMPT),
        "business_logic": (DISCOVERY_SYSTEM_PROMPT, BUSINESS_LOGIC_DISCOVERY),
    }
    
    # Natural language prompts
    natural_prompts = {
        "natural": (SYSTEM_PROMPT_NATURAL, NATURAL_WORKFLOW_ANALYSIS),
        "simple": (SYSTEM_PROMPT_NATURAL, SIMPLE_NATURAL_ANALYSIS),
        "flow": (SYSTEM_PROMPT_NATURAL, WORKFLOW_FLOW_GENERATION),
        "applications": (SYSTEM_PROMPT_NATURAL, APPLICATION_USAGE_ANALYSIS),
        "patterns": (SYSTEM_PROMPT_NATURAL, NATURAL_PATTERN_DETECTION),
    }
    
    # Check all prompt dictionaries
    if analysis_type in original_prompts:
        return original_prompts[analysis_type]
    elif analysis_type in discovery_prompts:
        return discovery_prompts[analysis_type]
    elif analysis_type in natural_prompts:
        return natural_prompts[analysis_type]
    else:
        # Default to full analysis
        return original_prompts["full"]


# Legacy function names for backward compatibility
def get_enhanced_analysis_prompt(analysis_type: str = "discovery") -> tuple[str, str]:
    """Legacy function - redirects to unified prompt getter"""
    return get_analysis_prompt(analysis_type)


def get_natural_prompt(analysis_type: str = "natural") -> tuple[str, str]:
    """Legacy function - redirects to unified prompt getter"""
    return get_analysis_prompt(analysis_type)