# Database Migration Guide

## Overview

This migration safely upgrades your existing NewSystem.AI database schema to support comprehensive workflow analysis and visualization capabilities while **preserving all existing data**.

### What's Preserved
- ✅ `leads` table and all existing lead data
- ✅ `recording_sessions` table and all existing recordings
- ✅ `video_chunks` table for chunked uploads
- ✅ `use_cases` table for landing page content
- ✅ `workflow_insights` table for basic insights

### What's Enhanced
- 🚀 **Organizations & User Management**: Multi-tenant support with role-based access
- 🎯 **Advanced Analysis**: Detailed GPT-4V analysis results with cost tracking
- 💰 **ROI Calculations**: Comprehensive cost-benefit analysis
- 📊 **Visualization**: Flow chart data structures for interactive dashboards
- 📄 **Reporting**: PDF generation and shareable links
- 🔒 **Security**: Row Level Security on all tables

## Migration Steps

### 1. Run the Migration Script

In your Supabase SQL Editor, execute the migration script:

```sql
-- Copy and paste the contents of migration-from-current.sql
```

**This is safe to run** - it only adds new tables and columns, never removes existing data.

### 2. Verify Migration Success

Run the verification script to ensure everything worked:

```sql
-- Copy and paste the contents of verify-migration.sql
```

You should see:
- ✅ All existing tables with their data counts
- ✅ All new tables created successfully
- ✅ Row Level Security enabled
- ✅ Foreign key relationships working
- ✅ Indexes created for performance

### 3. Update Environment Configuration

Use the minimal environment configuration:

```bash
# Use the simplified .env.minimal file
cp backend/.env.minimal backend/.env
```

Fill in your actual credentials:
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_SERVICE_KEY`: Your service role key (not anon key)
- `OPENAI_API_KEY`: Your OpenAI API key for GPT-4V

## New Schema Capabilities

### 1. Enhanced Analysis Pipeline

```sql
recording_sessions → analysis_results → automation_opportunities
                  → cost_analyses
                  → workflow_visualizations
                  → generated_reports
```

### 2. Multi-Tenant Organizations

```sql
organizations → user_profiles → recording_sessions
```

### 3. Business Intelligence Views

- `recording_sessions_summary`: Analysis status and ROI overview
- `roi_dashboard`: Aggregated savings and opportunities by user

## Data Relationships

### Core Analysis Flow
```
📹 Recording Session (existing)
   ├── 🧠 Analysis Result (new)
   │   ├── 🎯 Automation Opportunities (enhanced)
   │   ├── 💰 Cost Analysis (new)
   │   ├── 📊 Workflow Visualization (new)
   │   └── 📄 Generated Reports (new)
   └── 📦 Video Chunks (existing)
```

### Multi-Tenant Structure
```
🏢 Organization (new)
   └── 👤 User Profile (new) → 🔐 auth.users (Supabase)
       └── 📹 Recording Sessions (existing)
```

## Security & Privacy

### Row Level Security (RLS) Policies

All new tables have RLS enabled with policies ensuring:
- Users can only access their own data
- Organization-based data isolation
- Public shareable reports when explicitly enabled

### Privacy Controls

The enhanced `recording_sessions` table now supports:
```json
{
  "privacy_settings": {
    "blur_passwords": true,
    "exclude_personal_info": false,
    "custom_exclusions": []
  }
}
```

## Performance Optimizations

### New Indexes Created
- Analysis results by session and status
- Automation opportunities by priority and ROI
- Cost analyses by session
- Generated reports by type and public status

### Query Performance
- Efficient lookups for user recordings
- Fast aggregations for ROI dashboards
- Optimized joins for comprehensive reporting

## API Compatibility

### Existing Endpoints (Unchanged)
- `GET /api/v1/recordings` - Still works
- `POST /api/v1/recordings/start` - Still works
- All existing recording functionality preserved

### New Endpoints Available
- `GET /api/v1/results/{session_id}` - Complete analysis results
- `POST /api/v1/results/{session_id}/pdf` - Generate PDF reports
- `GET /api/v1/insights/dashboard` - ROI dashboard data

## Rollback Plan (If Needed)

If you need to rollback (though this shouldn't be necessary):

```sql
-- Only drop new tables (keeps all existing data)
DROP VIEW IF EXISTS public.roi_dashboard;
DROP VIEW IF EXISTS public.recording_sessions_summary;
DROP TABLE IF EXISTS public.generated_reports;
DROP TABLE IF EXISTS public.cost_analyses;
DROP TABLE IF EXISTS public.workflow_visualizations;
DROP TABLE IF EXISTS public.automation_opportunities;
DROP TABLE IF EXISTS public.analysis_results;
DROP TABLE IF EXISTS public.user_profiles;
DROP TABLE IF EXISTS public.organizations;

-- Remove added columns from existing tables
ALTER TABLE public.recording_sessions 
DROP COLUMN IF EXISTS privacy_settings,
DROP COLUMN IF EXISTS workflow_type,
DROP COLUMN IF EXISTS analysis_cost;
```

## Testing Your Migration

### 1. Verify Data Integrity
```sql
-- Check your leads are still there
SELECT COUNT(*) FROM public.leads;

-- Check recording sessions
SELECT COUNT(*) FROM public.recording_sessions;
```

### 2. Test New Functionality

Your frontend connection test page should now show enhanced capabilities:
- ✅ Database connection with new schema
- ✅ Analysis pipeline ready
- ✅ ROI calculation capabilities

### 3. Run Development Server

```bash
./start-dev.sh
```

Visit http://localhost:5173 to see the enhanced connection dashboard.

## Next Steps

With the migration complete, you're ready for:

1. **Week 2 Development**: GPT-4V analysis pipeline
2. **Enhanced Insights**: ROI calculations and automation opportunities
3. **Advanced Reporting**: PDF generation and flow charts
4. **Team Features**: Multi-user organizations

## Support

If you encounter any issues:

1. Run the verification script to identify problems
2. Check the Supabase logs for error details
3. The migration is designed to be safe - existing functionality remains unchanged

**Your leads table and all existing recording data are completely safe and preserved.**