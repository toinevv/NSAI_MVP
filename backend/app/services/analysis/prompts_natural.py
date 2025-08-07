"""
Natural Language Prompts for Workflow Understanding
Focus: Understand and describe what's actually happening, without forcing patterns
Goal: Natural, conversational analysis that builds trust and understanding
"""

# Natural language system prompt
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

# Main natural discovery prompt
NATURAL_WORKFLOW_ANALYSIS = """Please analyze these screenshots and tell me what's happening in plain language.

First, provide a natural description:
1. **Overall Summary**: What is this person doing? What's their goal?
2. **Step-by-Step Process**: Walk me through what happens in sequence
3. **Applications Used**: Which programs/websites are they using and for what?
4. **Patterns Observed**: What do they repeat? What seems inefficient?
5. **Automation Opportunities**: How could this be improved or automated?

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
      "time_estimate_seconds": 30
    }
  ],
  
  "applications": {
    "Gmail": {
      "purpose": "Receiving orders and sending confirmations",
      "time_percentage": 25,
      "actions": ["reading emails", "copying data", "sending replies"]
    }
  },
  
  "patterns": [
    "Copies the same information to 3 different places",
    "Switches between Gmail and WMS 15 times",
    "Manually retypes information that's visible on screen"
  ],
  
  "automation_opportunities": [
    {
      "what": "Email to WMS data entry",
      "how": "Parse emails automatically and populate WMS fields",
      "time_saved": "10 minutes per order",
      "complexity": "simple"
    }
  ],
  
  "flow_chart_data": {
    "nodes": [
      {"id": "1", "label": "Gmail", "type": "application"},
      {"id": "2", "label": "Copy Order #", "type": "action"},
      {"id": "3", "label": "WMS", "type": "application"},
      {"id": "4", "label": "Paste Data", "type": "action"}
    ],
    "edges": [
      {"source": "1", "target": "2", "label": "Read"},
      {"source": "2", "target": "3", "label": "Switch"},
      {"source": "3", "target": "4", "label": "Enter"}
    ]
  },
  
  "metrics": {
    "total_time_seconds": 300,
    "repetitions_observed": 5,
    "applications_used": 3,
    "copy_paste_actions": 15,
    "potential_time_saved_daily_hours": 2.5
  },
  
  "confidence": 0.85,
  "analysis_notes": "Clear workflow with obvious automation potential"
}

IMPORTANT:
- Write the natural description FIRST, as if talking to a friend
- Don't assume workflows - describe what you actually see
- Be specific about applications and actions
- Focus on understanding the person's actual work
- Suggest practical, realistic improvements"""

# Simplified prompt for quick analysis
SIMPLE_NATURAL_ANALYSIS = """Watch these screenshots and explain what the person is doing.

Tell me:
1. What's happening here? (in plain language)
2. What applications are they using?
3. What takes the most time?
4. How could this be faster/easier?

Be conversational and clear. Focus on what matters most.

Please provide your response in JSON format with at least a 'natural_description' field and any other relevant structured data."""

# Flow chart generation prompt
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

# Application detection prompt
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

# Pattern detection without categories
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

# Function to get natural language prompts
def get_natural_prompt(analysis_type: str = "full") -> tuple[str, str]:
    """
    Get natural language prompts for workflow understanding
    
    Args:
        analysis_type: Type of analysis needed
    
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    prompts_map = {
        "full": (SYSTEM_PROMPT_NATURAL, NATURAL_WORKFLOW_ANALYSIS),
        "simple": (SYSTEM_PROMPT_NATURAL, SIMPLE_NATURAL_ANALYSIS),
        "flow": (SYSTEM_PROMPT_NATURAL, WORKFLOW_FLOW_GENERATION),
        "applications": (SYSTEM_PROMPT_NATURAL, APPLICATION_USAGE_ANALYSIS),
        "patterns": (SYSTEM_PROMPT_NATURAL, NATURAL_PATTERN_DETECTION),
        # Alias for discovery mode
        "natural": (SYSTEM_PROMPT_NATURAL, NATURAL_WORKFLOW_ANALYSIS),
    }
    
    return prompts_map.get(analysis_type, prompts_map["full"])