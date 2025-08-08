# 🧪 NewSystem.AI UI Testing Guide

## Quick Start Testing

### 1. Start the Development Environment
```bash
# Use the provided script
./start-dev.sh

# Or manually:
# Terminal 1 - Backend
cd backend
source venv/bin/activate  # If using venv
export OPENAI_API_KEY='your-key-here'
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### 2. Access the Application
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/docs

---

## 📹 Test Scenario 1: Basic Recording Flow

### Steps:
1. **Open the app** at http://localhost:5173
2. **Click "Start Recording"** button
   - ✅ Should see permission dialog
   - ✅ Grant screen recording permission
3. **Perform a simple workflow** (e.g., open email, copy text, paste in another app)
4. **Click "Stop Recording"**
   - ✅ Should show recording duration
   - ✅ Should display "Processing..." status
5. **Wait for upload**
   - ✅ Progress indicator should show chunk upload
   - ✅ Should see "Recording saved successfully"

### Expected Results:
- Recording duration displayed correctly
- File size shown (not 0.0 MB)
- Session ID visible in console
- No errors in browser console

---

## 🤖 Test Scenario 2: Analysis Pipeline

### Steps:
1. **Complete a recording** (as above)
2. **Click "Analyze Recording"** button
   - ✅ Should show "Starting analysis..."
3. **Wait for GPT-4V analysis** (10-30 seconds)
   - ✅ Loading spinner visible
   - ✅ Status updates shown
4. **View results**
   - ✅ Natural language description appears
   - ✅ Applications detected shown
   - ✅ Workflow visualization displayed

### Expected Results:
- Three tabs visible: Overview, Workflow Map, Raw Analysis
- Natural language description makes sense
- Applications list shows programs used
- Confidence score displayed

---

## 🔍 Test Scenario 3: Natural Language Analysis

### Steps:
1. **Record a multi-app workflow:**
   - Open email client
   - Copy order information
   - Open browser/WMS
   - Enter data
   - Submit form
2. **Run analysis**
3. **Check Overview tab:**
   - ✅ "What's Happening" section describes workflow naturally
   - ✅ Applications show time percentages
   - ✅ Patterns listed clearly
4. **Check Workflow Map tab:**
   - ✅ Flow chart shows steps visually
   - ✅ Can zoom/pan the diagram
   - ✅ Nodes show applications and actions
5. **Check Raw Analysis tab:**
   - ✅ JSON data visible
   - ✅ Can copy JSON to clipboard

### Expected Results:
- Natural description reads conversationally
- No forced categorization into rigid patterns
- Workflow map adapts to discovered flow
- Automation opportunities identified

---

## 🎯 Quick Validation Checks

### Frontend Health:
```javascript
// Open browser console (F12) and run:
console.log('Session ID:', localStorage.getItem('recording_session_id'))
console.log('Chunks uploaded:', localStorage.getItem('chunk_count'))
```

### Backend Health:
```bash
# Check API is running
curl http://localhost:8000/health

# Check GPT-4V configuration
curl http://localhost:8000/api/v1/analysis/validate
```

### Common Issues & Fixes:

| Issue | Solution |
|-------|----------|
| "0.0 MB" file size | Refresh page, chunks are being uploaded |
| Analysis fails | Check OPENAI_API_KEY is set |
| No permission dialog | Use HTTPS or localhost only |
| Recording won't start | Check browser supports MediaRecorder API |
| Workflow chart empty | Ensure frames were extracted properly |

---

## 📊 Test Data Examples

### Good Test Workflows:
1. **Email → Data Entry:**
   - Open Gmail/Outlook
   - Read order email
   - Copy details
   - Open CRM/WMS
   - Enter data
   - Save/Submit

2. **Excel → Multiple Systems:**
   - Open Excel report
   - Copy data
   - Update System A
   - Update System B
   - Send confirmation email

3. **Web Research → Documentation:**
   - Search Google
   - Open multiple tabs
   - Copy information
   - Paste into document
   - Format and save

### What to Look For:
- ✅ Natural language describes what you actually did
- ✅ Applications detected match what you used
- ✅ Time estimates seem reasonable
- ✅ Automation suggestions make sense
- ✅ Workflow chart follows your actual steps

---

## 🐛 Debugging Tips

### Enable Debug Mode:
```javascript
// In browser console:
localStorage.setItem('debug', 'true')
```

### Check Logs:
```bash
# Backend logs
tail -f backend/logs/app.log

# Frontend console
# Open DevTools → Console tab
```

### Test Individual Components:
```bash
# Test GPT-4V directly
cd backend
python test_analysis_simple.py

# Test frame extraction
python test_frame_extraction.py
```

---

## ✅ Success Criteria

Your UI test is successful when:
1. **Recording works** - Can record and stop cleanly
2. **Upload completes** - All chunks uploaded, file size shown
3. **Analysis runs** - GPT-4V processes the recording
4. **Results display** - Natural language and visualizations appear
5. **No errors** - Console is clean, no red error messages

---

## 🎯 Week 4 Launch Acceptance Testing

### Manual E2E Testing Requirements

#### Test 1: 2+ Real Recordings with Different Lengths/Apps
**Status**: ⏳ PENDING USER TESTING

Record the following scenarios and document results:

**Scenario A: Short Email Workflow (2-3 minutes)**
- [ ] Open Gmail/Outlook
- [ ] Read and copy order details  
- [ ] Open WMS/CRM system
- [ ] Paste and submit data
- [ ] **Expected**: Analysis identifies email → WMS pattern
- [ ] **Test Results**: `[USER TO FILL]`

**Scenario B: Longer Multi-App Workflow (5-10 minutes)**
- [ ] Excel report → multiple system updates
- [ ] Web research → documentation workflow
- [ ] Complex data entry across 3+ applications
- [ ] **Expected**: Analysis handles longer recordings without timeout
- [ ] **Test Results**: `[USER TO FILL]`

#### Test 2: Concurrency Testing  
**Status**: ⏳ PENDING USER TESTING

**Scenario**: Open 3-5 browser tabs and start recordings simultaneously
- [ ] Tab 1: Start recording workflow A
- [ ] Tab 2: Start recording workflow B  
- [ ] Tab 3: Start recording workflow C
- [ ] **Expected**: All recordings complete without interference
- [ ] **Test Results**: `[USER TO FILL]`

### Critical Performance Checks

#### Recording Performance
- [ ] **Recording starts within 2 seconds** of clicking Start
- [ ] **No dropped frames** during screen capture
- [ ] **Upload completes within 30 seconds** of stopping
- [ ] **Memory usage stays under 500MB** during recording
- [ ] **Test Results**: `[USER TO FILL]`

#### Analysis Performance  
- [ ] **GPT-4V analysis completes within 60 seconds** for 2-minute recording
- [ ] **Cost stays under $0.50** per analysis (check console logs)
- [ ] **Results display within 5 seconds** of analysis completion
- [ ] **No timeout errors** for recordings up to 10 minutes
- [ ] **Test Results**: `[USER TO FILL]`

### Business Value Validation

#### ROI Calculator Accuracy
Record a workflow where you can estimate time savings, then check if the system's calculations are reasonable:
- [ ] **Manual estimate**: ___ hours/week could be saved
- [ ] **System estimate**: ___ hours/week savings shown
- [ ] **Accuracy assessment**: Reasonable ✅ / Too high ❌ / Too low ❌  
- [ ] **Test Results**: `[USER TO FILL]`

#### Automation Opportunity Detection
- [ ] **Email → WMS pattern detected** when present
- [ ] **Repetitive actions identified** (copy/paste, data entry)  
- [ ] **Applications correctly identified** and time allocated
- [ ] **Confidence scores above 70%** for clear workflows
- [ ] **Test Results**: `[USER TO FILL]`

---

## 🚨 Critical Issues to Watch For

### Immediate Launch Blockers
If any of these occur, DO NOT LAUNCH:
- [ ] **Recording fails to start** consistently
- [ ] **Analysis costs exceed $2.00** per recording
- [ ] **Results show completely wrong applications** 
- [ ] **System crashes** with normal workflows
- [ ] **Data loss** - recordings disappear
- [ ] **Issues Found**: `[USER TO FILL]`

### Performance Red Flags  
If these occur frequently, investigate before launch:
- [ ] **Upload takes longer than 2 minutes** for 5-minute recording
- [ ] **Analysis timeout** for recordings under 10 minutes
- [ ] **Browser becomes unresponsive** during recording
- [ ] **Memory leaks** - browser tab uses >1GB RAM
- [ ] **Issues Found**: `[USER TO FILL]`

---

## 📊 Test Environment Verification

### Backend Health Check
```bash
# Run these commands and paste results:
curl http://localhost:8000/health

# Expected: {"status":"healthy","timestamp":"...","services":{...}}
# Actual Result: [USER TO PASTE]
```

### Frontend Configuration Check  
```bash
# In browser console (F12):
console.log('API URL:', import.meta.env.VITE_API_URL)
console.log('Supabase URL:', import.meta.env.VITE_SUPABASE_URL)

# Expected: URLs should point to localhost:8000 and Supabase
# Actual Result: [USER TO PASTE]
```

### GPT-4V Integration Test
```bash
cd backend
python test_gpt4v_integration.py

# Expected: Analysis completes with structured insights
# Actual Result: [USER TO PASTE]
```

---

## 📝 User Testing Report Template

### Test Session Summary
**Date**: `[FILL DATE]`  
**Duration**: `[FILL TOTAL TIME]`  
**Recordings Created**: `[FILL COUNT]`  
**Analysis Runs**: `[FILL COUNT]`  
**Major Issues Found**: `[FILL COUNT]`  

### Detailed Findings

#### What Worked Well ✅
```
[USER TO FILL - List features that worked smoothly]
```

#### Issues Encountered ❌  
```
[USER TO FILL - List problems, include steps to reproduce]
```

#### Performance Notes 📊
```
[USER TO FILL - Recording speed, analysis time, resource usage]
```

#### Business Value Assessment 💰
```
[USER TO FILL - Are the insights valuable? Do ROI calculations seem realistic?]
```

### Launch Recommendation
- [ ] **READY TO LAUNCH** - All critical tests pass
- [ ] **MINOR FIXES NEEDED** - Launch possible with known limitations  
- [ ] **MAJOR ISSUES** - Do not launch, significant work required
- [ ] **UNABLE TO TEST** - Environment/setup problems

**Overall Assessment**: `[USER TO FILL]`

**Key Concerns**: `[USER TO FILL]`

**Launch Confidence (1-10)**: `[USER TO FILL]`

---

## 📝 Reporting Issues

If you find bugs:
1. Note the exact steps to reproduce
2. Check browser console for errors (F12 → Console)
3. Check backend logs if accessible
4. Save the session ID from localStorage
5. Screenshot any error messages
6. Include browser/OS information

**For immediate blockers**: Test multiple browsers (Chrome, Firefox, Safari) to confirm if issue is browser-specific.

Happy Testing! 🚀

### Post-Testing: Ready to Commit & Deploy 
Once testing is complete and issues resolved, the system will be ready for Railway deployment and production launch.