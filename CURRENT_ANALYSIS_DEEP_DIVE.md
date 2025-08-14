# 🧠 Current Analysis Pipeline - Deep Dive

## Executive Summary

Our current analysis system is **jumping straight to Layer 3 (Implementation)** with ROI calculations and automation opportunities, when we should be **perfecting Layer 2 (Translation/Analysis)** first. We need to focus on understanding workflows deeply before calculating business value.

---

## 🏗️ Current Architecture Overview

### Pipeline Flow
```
Recording (2 FPS) → Frame Extraction → GPT-4V Analysis → Result Parsing → UI Display
```

### 1. **Frame Extraction** (`frame_extractor.py`)
- Extracts frames from video at configurable intervals
- Uses FFmpeg or similar video processing
- Produces base64 encoded JPEG frames with timestamps

### 2. **GPT-4V Analysis** (`gpt4v_client.py`)
- Sends frames to OpenAI GPT-4V Vision API
- Uses structured JSON response format
- Cost tracking per request (~$0.01-0.03 per image)

### 3. **Prompt System** (`prompts.py`)
- **17 different prompt types** (too many!)
- Mixed focus: original, discovery, natural language
- Jumping between analysis approaches

### 4. **Result Parser** (`result_parser.py`)
- Converts GPT-4V JSON responses to structured format
- Calculates ROI metrics automatically
- Generates automation opportunities

---

## 🎯 Current Prompts Analysis

### **Problem: We have TOO MANY prompt types**

#### Original Prompts (Layer 3 focused)
- `FULL_ANALYSIS_PROMPT` - Forces specific workflow categories
- `EMAIL_WMS_FOCUSED_PROMPT` - Hyper-focused on one pattern
- `QUICK_ANALYSIS_PROMPT` - Simplified but still Layer 3

#### Discovery Prompts (Better, but unfocused)
- `OPEN_DISCOVERY_PROMPT` - "Tell me what you see" (good!)
- `CLUSTERING_DISCOVERY_PROMPT` - Groups similar actions
- `BUSINESS_LOGIC_DISCOVERY` - Understands decision points

#### Natural Language Prompts (Mixed Layer 2/3)
- `NATURAL_WORKFLOW_ANALYSIS` - Good analysis, but includes ROI
- `SIMPLE_NATURAL_ANALYSIS` - Better, more focused
- `WORKFLOW_FLOW_GENERATION` - Creates flowcharts

---

## 🔍 What GPT-4V Currently Receives

### Input to GPT-4V:
```
System Prompt: "You are an expert workflow analyst..."
User Message: 
  - "Analyze these screenshots..."
  - Frame 1 (base64 JPEG)
  - Frame 2 (base64 JPEG)  
  - Frame 3 (base64 JPEG)
  - ...
```

### Current Response Format Forced:
```json
{
  "workflows_detected": [...],
  "automation_opportunities": [...],  // Layer 3!
  "time_breakdown": {...},            // Layer 3!
  "key_insights": [...],
  "confidence_score": 0.85
}
```

---

## 🚨 Layer Analysis Problems

### **We're Doing Layer 3 Before Layer 2**

| Layer | What It Should Be | What We're Actually Doing |
|-------|------------------|---------------------------|
| **Layer 1: Observation** | ✅ Screen recording at 2 FPS | ✅ Working well |
| **Layer 2: Translation** | 🔍 **What happened?** Applications, sequences, data flow | ❌ Jumping to automation opportunities |
| **Layer 3: Implementation** | 💰 ROI, time savings, automation tools | ✅ Doing this too early |

### **Specific Issues:**

1. **Forcing Workflow Categories**: "email_to_wms", "excel_reporting" 
   - Should: Let patterns emerge naturally
   - Reality: Pre-defining what we expect to find

2. **Calculating ROI Too Early**: "$25,000 annual savings"
   - Should: Understand workflow first
   - Reality: Making financial assumptions without solid analysis

3. **Mixed Prompt Goals**: Same prompt asks for understanding AND automation
   - Should: Separate analysis from opportunity identification  
   - Reality: Confusing the model with multiple objectives

---

## 🎯 What Layer 2 Analysis Should Look Like

### **Perfect Layer 2 Output:**
```json
{
  "what_happened": {
    "natural_description": "User opens Gmail, reads order email, copies customer name and order number, switches to WMS system, navigates to new order form, pastes information, fills additional fields, submits order",
    "temporal_sequence": [
      {"timestamp": "0:05", "action": "Opens Gmail", "app": "Gmail"},
      {"timestamp": "0:12", "action": "Reads email from customer", "app": "Gmail"},
      {"timestamp": "0:25", "action": "Selects and copies customer name", "app": "Gmail"},
      {"timestamp": "0:30", "action": "Switches to WMS tab", "app": "WMS_Browser"},
      {"timestamp": "0:35", "action": "Clicks 'New Order' button", "app": "WMS_Browser"},
      {"timestamp": "0:42", "action": "Pastes customer name in field", "app": "WMS_Browser"},
      // ... detailed sequence
    ]
  },
  "applications_observed": {
    "Gmail": {
      "time_spent": 45,
      "actions": ["open", "read", "select_text", "copy"],
      "data_extracted": ["customer_name", "order_number", "delivery_address"]
    },
    "WMS_Browser": {
      "time_spent": 120,
      "actions": ["navigate", "click_button", "paste", "type", "submit"],
      "data_entered": ["customer_name", "order_number", "delivery_address", "priority_level"]
    }
  },
  "data_flow": [
    {
      "source": "Gmail email body",
      "destination": "WMS customer field", 
      "data_type": "customer_name",
      "method": "copy_paste",
      "manual_steps": 3
    }
    // ... other data flows
  ],
  "patterns_observed": [
    "Same data copied from email to WMS form",
    "User manually types information that was already available in email",
    "User switches between applications 4 times during process",
    "Form validation requires re-entering phone number in different format"
  ],
  "analysis_confidence": 0.92,
  "technical_notes": {
    "apps_detected": ["Gmail (web)", "WMS (web_browser)", "Windows_taskbar"],
    "resolution": "1920x1080",
    "frames_analyzed": 15,
    "unclear_actions": ["typing at 1:23 - text not visible"]
  }
}
```

### **NOT This (Current Layer 3 Focus):**
```json
{
  "automation_opportunities": [
    {
      "time_saved_daily_minutes": 30,     // ❌ Too early!
      "cost_saved_annually": 15000,       // ❌ Too early!
      "specific_recommendation": "Use RPA" // ❌ Too early!
    }
  ]
}
```

---

## 🔧 Current Technical Stack Analysis

### **Strengths:**
- ✅ GPT-4V integration working
- ✅ Frame extraction pipeline solid
- ✅ Cost tracking implemented
- ✅ Error handling robust
- ✅ JSON response parsing flexible

### **Weaknesses:**
- ❌ **17 different prompt types** - too scattered
- ❌ **Mixed Layer 2/3 objectives** in same prompt
- ❌ **Forcing predefined workflow categories**
- ❌ **ROI calculations happening in parser**, not analysis
- ❌ **Result parser assumes business context** (e.g., $25/hour)

---

## 📊 Current Cost & Performance

### **GPT-4V Usage:**
- **Model**: `gpt-4o-2024-08-06` (configurable)
- **Cost per image**: ~$0.01-0.03 (depending on detail level)
- **Typical analysis**: 10-20 frames = $0.10-0.60 per recording
- **Token usage**: 2,000-8,000 tokens per analysis

### **Response Times:**
- Frame extraction: ~5-15 seconds
- GPT-4V analysis: ~10-30 seconds  
- Result parsing: <1 second
- **Total**: ~20-50 seconds per recording

---

## 🎯 Layer 2 Focus Recommendations

### **1. Simplify to ONE Analysis Prompt**
Replace 17 prompts with 1 focused Layer 2 prompt:

```
"Observe these screenshots and describe what happened:
1. What applications were used and when?
2. What was the exact sequence of actions?
3. What data moved between applications?
4. What patterns do you notice?
5. Where did the user have to manually re-enter information?

Respond with detailed observations only. Do not suggest automations or calculate time savings."
```

### **2. Remove Layer 3 Calculations from Parser**
- Remove ROI calculations (`cost_saved_annually`)
- Remove automation recommendations 
- Remove predefined workflow categories
- Focus on pure observation and pattern detection

### **3. Enhanced Layer 2 Prompting**
```
SYSTEM: "You are observing a computer user's workflow. Describe exactly what you see happening, step by step, without making assumptions about business value or automation potential."

USER: "Watch these screenshots and tell me:
- Which applications were used?
- What was the sequence of actions?
- What information moved between applications?
- What repetitive actions occurred?
- Where did manual data entry happen?

Be specific and factual. Focus on understanding the workflow deeply."
```

---

## 🚀 Next Steps for Solid Layer 2

### **Phase 1: Simplify (This Week)**
1. **Create single Layer 2 prompt** - Remove 16 other prompts
2. **Remove ROI calculator** from results page  
3. **Focus UI on workflow understanding** - not automation opportunities
4. **Test with manual uploads** using consistent videos

### **Phase 2: Enhance Layer 2 (Next Week)**
1. **Improve sequence detection** - Better temporal understanding
2. **Enhanced data flow mapping** - Track information movement
3. **Application detection refinement** - Better app identification
4. **Pattern recognition improvement** - Spot repetitive actions

### **Phase 3: Add Layer 3 Back (Later)**
1. **Separate opportunity analysis** - Different pipeline
2. **Business context integration** - User-provided context
3. **ROI calculator** - Based on solid Layer 2 understanding
4. **Implementation recommendations** - After workflow is understood

---

## 🎯 Success Metrics for Layer 2

### **Quality Indicators:**
- Can accurately describe what happened in workflow
- Identifies all applications used and time in each
- Maps data flow between systems correctly
- Spots repetitive patterns without being told to look for them
- High confidence scores (>90%) on clear workflows

### **User Validation:**
- User can read analysis and say "Yes, that's exactly what I did"
- Technical team can understand workflow for automation planning
- Analysis provides enough detail for business process documentation

---

## 💡 Key Insight

**We've been trying to build a calculator when we need to build a microscope first.**

Layer 2 is about **understanding workflows deeply** so that Layer 3 automation becomes obvious and valuable. Right now we're guessing at business value without truly understanding what's happening.

Let's build the best workflow understanding system in the world, then layer business value on top of that solid foundation.