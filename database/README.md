# NewSystem.AI Database Schema

This directory contains the database schema and migration scripts for NewSystem.AI.

## Mission
Save 1,000,000 operator hours monthly through intelligent workflow analysis and automation discovery.

## Architecture Overview

Our database is designed with a logical, coherent structure that supports:

1. **Multi-tenant Organizations** - Support multiple logistics companies
2. **User Management** - Operators, managers, and admins with role-based access
3. **Recording Pipeline** - Screen recording capture and chunked upload
4. **AI Analysis** - GPT-4V workflow analysis and pattern recognition
5. **Business Intelligence** - ROI calculations and automation opportunities
6. **Reporting** - PDF generation and shareable insights

## Core Tables

### Organization & User Management
- `organizations` - Multi-tenant organization data
- `users` - Extended user profiles (references Supabase auth.users)

### Recording Pipeline
- `recordings` - Screen recording sessions
- `recording_chunks` - Chunked upload data for reliability
- `analysis_results` - GPT-4V analysis jobs and results
- `workflow_patterns` - Extracted workflow sequences

### Business Intelligence
- `automation_opportunities` - Identified automation with ROI analysis
- `cost_analyses` - Detailed cost-benefit calculations
- `workflow_visualizations` - Flow chart data for UI
- `generated_reports` - PDF reports and shareable links
- `daily_metrics` - Aggregated analytics for dashboards

## Key Features

### 1. Workflow-Centric Design
Focus on email → WMS workflows and logistics operations:
- `workflow_category` field tracks common patterns
- `applications_used` array stores application stack
- Pattern recognition optimized for logistics workflows

### 2. ROI-First Approach
Every automation opportunity includes:
- Time savings calculations (weekly hours)
- Cost impact analysis (hourly rates × time saved)
- Implementation complexity assessment
- Payback period calculations

### 3. Privacy & Security
- Row Level Security (RLS) enabled on all tables
- PII detection and masking capabilities
- Organization-based data isolation
- Audit trails for all operations

### 4. Performance Optimized
- Strategic indexes for common queries
- Efficient aggregation views
- Partitioning ready for scale
- Cost tracking for GPT-4V API usage

## Setup Instructions

### 1. Supabase Setup
1. Create a new Supabase project
2. Copy your project URL and service role key
3. Run the schema script in Supabase SQL Editor

### 2. Local Development
```bash
# Set environment variables
export SUPABASE_URL="your-project-url"
export SUPABASE_SERVICE_KEY="your-service-key"

# The backend will automatically connect using these credentials
```

### 3. Apply Schema
Execute `supabase-schema.sql` in your Supabase project's SQL Editor.

## Business Logic Examples

### Recording a Logistics Workflow
```sql
-- Create a recording session
INSERT INTO recordings (user_id, organization_id, title, workflow_category, applications_used)
VALUES (
    'user-uuid',
    'org-uuid', 
    'Daily email to WMS data entry',
    'email_to_wms',
    ARRAY['Outlook', 'SAP WMS', 'Excel']
);
```

### Identifying Automation Opportunities
```sql
-- Find high-ROI automation opportunities
SELECT 
    workflow_type,
    time_saved_weekly_hours,
    annual_savings_estimate,
    implementation_complexity
FROM automation_opportunities
WHERE roi_score > 5.0
ORDER BY annual_savings_estimate DESC;
```

### Organization Dashboard Metrics
```sql
-- Get organization performance summary
SELECT * FROM organization_dashboard 
WHERE organization_id = 'your-org-uuid';
```

## Data Flow

1. **Recording** → User records screen workflow
2. **Upload** → Chunked upload to Supabase Storage
3. **Analysis** → GPT-4V analyzes frames for patterns
4. **Intelligence** → Extract automation opportunities
5. **Reporting** → Generate ROI analysis and recommendations

## Scaling Considerations

- **Partitioning**: Ready for time-based partitioning on large tables
- **Indexes**: Optimized for common query patterns
- **Views**: Pre-aggregated data for dashboard performance
- **RLS**: Security-first design for multi-tenant scaling

## Migration Strategy

- Version tracking via `schema_version` table
- Backward compatibility maintained
- Rolling updates supported
- Data migration scripts included

---

*Built to save 1,000,000 operator hours monthly through intelligent automation discovery.*