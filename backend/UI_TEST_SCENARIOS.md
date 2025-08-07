# 🧪 UI Test Scenarios for NewSystem.AI MVP

## Overview
These test scenarios are designed for YOU to run in the actual UI and report back results. Each test validates a specific aspect of the workflow discovery platform.

---

## Test Scenario 1: Complete Workflow Discovery Test
**Purpose**: Validate that the system discovers ALL workflows, not just email → WMS

### Setup
1. Open the application at http://localhost:5173
2. Have multiple applications ready: Email, browser with WMS, Excel, notepad
3. Plan to do various tasks for 5-10 minutes

### Steps to Execute
1. **Start Recording**
   - Click "Start Recording"
   - Grant screen permission
   - Verify recording indicator shows

2. **Perform Various Workflows** (5-10 minutes):
   - [ ] Check email and copy some information
   - [ ] Open WMS and look up an order
   - [ ] Switch to Excel and update a report
   - [ ] Go back to email and compose a response
   - [ ] Open notepad and jot down notes
   - [ ] Do some repetitive task 3-4 times
   - [ ] Include a task you do daily but might seem minor

3. **Stop Recording**
   - Click "Stop Recording"
   - Wait for upload to complete
   - Note the file size displayed

4. **Trigger Analysis**
   - Click "Analyze with AI"
   - Watch the progress indicator
   - Time how long analysis takes

### What to Report Back
```
DISCOVERY TEST RESULTS:
- Recording duration: ___ minutes
- File size shown: ___ MB
- Analysis time: ___ seconds
- Workflows discovered: ___ (list them)
- Were ALL your activities detected? Yes/No
- Any surprising patterns found? ___
- Missing workflows: ___
- Accuracy score (1-10): ___
```

---

## Test Scenario 2: Unknown Pattern Detection Test
**Purpose**: Verify the system identifies patterns it can't categorize

### Setup
1. Think of an unusual workflow unique to your job
2. Something that's repetitive but not standard

### Steps
1. **Record the Unusual Workflow** (2-3 minutes)
   - Perform your unique/unusual task
   - Repeat it 2-3 times if possible

2. **Analyze and Check Results**
   - Look for "Unknown Pattern" or "Unnamed Workflow"
   - Check if system asks for clarification

### What to Report Back
```
UNKNOWN PATTERN TEST:
- What unusual task did you perform? ___
- Did system detect it? Yes/No
- How was it labeled? ___
- Suggested improvement: ___
```

---

## Test Scenario 3: Time and ROI Accuracy Test
**Purpose**: Validate time calculations and ROI projections

### Steps
1. **Record a Known Timed Task**
   - Pick a task you know takes exactly X minutes
   - Record yourself doing it once
   - Stop recording immediately after

2. **Check Analysis Results**
   - Compare system's time estimate vs actual
   - Review ROI calculations
   - Check if frequency estimates make sense

### What to Report Back
```
TIME ACCURACY TEST:
- Actual task duration: ___ minutes
- System estimate: ___ minutes
- Accuracy: ___% 
- Daily frequency (your estimate): ___ times
- System's frequency estimate: ___ times
- ROI calculation believable? Yes/No
- Annual savings shown: $___
```

---

## Test Scenario 4: Multi-Application Flow Test
**Purpose**: Test complex workflows across many systems

### Steps
1. **Record a Complex Multi-Step Process** (5 minutes)
   - Use at least 4 different applications
   - Include copy-paste between them
   - Show your actual daily workflow

2. **Review Workflow Visualization**
   - Check if all applications are identified
   - Verify data flow is mapped correctly
   - Look for integration recommendations

### What to Report Back
```
MULTI-APP TEST:
- Applications used: ___ (list all)
- Applications detected: ___ (list all)
- Data flow accurate? Yes/No
- Integration suggestions helpful? Yes/No
- Missing connections: ___
```

---

## Test Scenario 5: Operator Expertise Recognition Test
**Purpose**: Verify the system recognizes your efficiency techniques

### Steps
1. **Record Using Your Shortcuts and Tricks** (3 minutes)
   - Use keyboard shortcuts
   - Show your efficient methods
   - Include any workarounds you've developed

2. **Check if System Recognized Your Expertise**
   - Look for "Operator Expertise" section
   - Check if shortcuts were noted
   - See if workarounds were identified

### What to Report Back
```
EXPERTISE TEST:
- Shortcuts used: ___
- Shortcuts detected: ___
- Workarounds shown: ___
- Workarounds detected: ___
- Feel valued/threatened? Valued/Threatened
- Would you share with team? Yes/No
```

---

## Test Scenario 6: Quick Value Test (10 Seconds)
**Purpose**: Can management see ROI immediately?

### Steps
1. **Open Any Completed Analysis**
2. **Start Timer**
3. **Try to Find in 10 Seconds**:
   - Total hours saved per week
   - Primary opportunity
   - Dollar value
4. **Stop Timer**

### What to Report Back
```
10-SECOND TEST:
- Time to find ROI: ___ seconds
- Hours/week visible? Yes/No
- Dollar value visible? Yes/No
- Had to click/scroll? Yes/No
- Clear enough for CFO? Yes/No
```

---

## Test Scenario 7: Real Workday Test (Extended)
**Purpose**: Ultimate validation with real work

### Steps
1. **Record 30-60 Minutes of Actual Work**
   - Don't change your behavior
   - Work normally
   - Include everything you typically do

2. **Review Complete Analysis**
   - Check coverage of your work
   - Validate time breakdowns
   - Review all recommendations

### What to Report Back
```
WORKDAY TEST:
- Recording duration: ___ minutes
- Workflows found: ___ count
- Coverage of your work: ___%
- Time breakdown accurate? Yes/No
- Recommendations useful? Yes/No
- Would implement suggestions? Yes/No
- Most valuable insight: ___
- Biggest surprise: ___
- Missing analysis: ___
```

---

## Test Scenario 8: Error Recovery Test
**Purpose**: Test system resilience

### Steps
1. **Start Recording**
2. **After 1 Minute**: Refresh the browser
3. **Check**: Does it offer to recover?
4. **If Yes**: Continue recording
5. **Complete** and analyze

### What to Report Back
```
RECOVERY TEST:
- Recovery offered? Yes/No
- Recording resumed? Yes/No
- Data lost? Yes/No/Some
- Final analysis complete? Yes/No
```

---

## 📊 Summary Report Template

After running all tests, please provide:

```
OVERALL ASSESSMENT:
Date: ___
Tester Role: ___
Tests Completed: ___/8

STRENGTHS:
1. ___
2. ___
3. ___

WEAKNESSES:
1. ___
2. ___
3. ___

MUST FIX BEFORE LAUNCH:
1. ___
2. ___

NICE TO HAVE:
1. ___
2. ___

Would you use this daily? Yes/No
Would you recommend to team? Yes/No
Ready for customers? Yes/No
Overall Score: ___/10

Additional Comments:
___
```

---

## 🎯 Success Criteria

The MVP is successful if:
- [ ] 6/8 tests pass
- [ ] Workflow discovery accuracy > 80%
- [ ] Time estimates within 20% of actual
- [ ] ROI visible in < 10 seconds
- [ ] Users feel valued, not threatened
- [ ] Recovery from errors works
- [ ] Would recommend to team

---

## 📝 Notes for Testers

1. **Be Honest**: We need real feedback, not encouragement
2. **Think Like a User**: Would your colleagues understand this?
3. **Note Confusion**: Any moment of confusion is a UX issue
4. **Suggest Improvements**: Your ideas make this better
5. **Test Edge Cases**: Try to break it (nicely)

Thank you for testing! Your feedback directly shapes the product.