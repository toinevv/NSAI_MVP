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

## 📝 Reporting Issues

If you find bugs:
1. Note the exact steps to reproduce
2. Check browser console for errors
3. Check backend logs
4. Save the session ID
5. Screenshot any error messages

Happy Testing! 🚀