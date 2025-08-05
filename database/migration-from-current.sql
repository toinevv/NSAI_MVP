-- ============================================================================
-- Database Migration Script: Current Schema → Enhanced NewSystem.AI Schema
-- ============================================================================
-- This script safely migrates from current schema to enhanced schema
-- PRESERVES: existing leads table and data
-- ADDS: comprehensive workflow analysis and visualization capabilities
-- 
-- INSTRUCTIONS:
-- 1. Run this in Supabase SQL Editor
-- 2. This will NOT affect your existing leads table or data
-- 3. All new tables work alongside existing structure
-- ============================================================================

-- STEP 1: Create enhanced user management (extending Supabase auth.users)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(255),
    settings JSONB DEFAULT '{}',
    subscription_tier VARCHAR(50) DEFAULT 'free',
    subscription_status VARCHAR(50) DEFAULT 'active',
    max_users INTEGER DEFAULT 5,
    max_recordings_per_month INTEGER DEFAULT 50,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add organization link to extend auth.users (if not exists)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'organization_id') THEN
        -- Since we can't modify auth.users directly, we'll create a user_profiles table
        CREATE TABLE public.user_profiles (
            id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
            organization_id UUID REFERENCES public.organizations(id),
            role VARCHAR(50) DEFAULT 'operator',
            first_name VARCHAR(255),
            last_name VARCHAR(255),
            job_title VARCHAR(255),
            settings JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- Row Level Security for user_profiles
        ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;
        
        CREATE POLICY "Users can view their own profile" ON public.user_profiles
            FOR SELECT USING (auth.uid() = id);
            
        CREATE POLICY "Users can update their own profile" ON public.user_profiles
            FOR UPDATE USING (auth.uid() = id);
    END IF;
END
$$;

-- STEP 2: Enhance existing recording_sessions table (if needed)
-- ============================================================================

-- Add missing columns to recording_sessions if they don't exist
DO $$
BEGIN
    -- Add privacy_settings if not exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'recording_sessions' AND column_name = 'privacy_settings') THEN
        ALTER TABLE public.recording_sessions ADD COLUMN privacy_settings JSONB DEFAULT '{"blur_passwords": true, "exclude_personal_info": false}';
    END IF;
    
    -- Add workflow_type if not exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'recording_sessions' AND column_name = 'workflow_type') THEN
        ALTER TABLE public.recording_sessions ADD COLUMN workflow_type VARCHAR(100);
    END IF;
    
    -- Add cost_tracking if not exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'recording_sessions' AND column_name = 'analysis_cost') THEN
        ALTER TABLE public.recording_sessions ADD COLUMN analysis_cost DECIMAL(10,4) DEFAULT 0.00;
    END IF;
END
$$;

-- STEP 3: Create new analysis and insights tables
-- ============================================================================

-- Enhanced analysis results (extends your existing workflow_insights)
CREATE TABLE IF NOT EXISTS public.analysis_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES public.recording_sessions(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'queued' CHECK (status IN ('queued', 'processing', 'completed', 'failed')),
    gpt_version VARCHAR(50) DEFAULT 'gpt-4-vision-preview',
    processing_started_at TIMESTAMP WITH TIME ZONE,
    processing_completed_at TIMESTAMP WITH TIME ZONE,
    processing_time_seconds INTEGER,
    frames_analyzed INTEGER DEFAULT 0,
    analysis_cost DECIMAL(10,4) DEFAULT 0.00,
    confidence_score DECIMAL(3,2) DEFAULT 0.00 CHECK (confidence_score >= 0.00 AND confidence_score <= 1.00),
    raw_gpt_response JSONB,
    structured_insights JSONB DEFAULT '{}',
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Automation opportunities (more detailed than existing workflow_insights)
CREATE TABLE IF NOT EXISTS public.automation_opportunities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL REFERENCES public.analysis_results(id) ON DELETE CASCADE,
    session_id UUID NOT NULL REFERENCES public.recording_sessions(id) ON DELETE CASCADE,
    opportunity_type VARCHAR(100) NOT NULL, -- 'copy_paste_automation', 'form_filling', 'data_entry', etc.
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    workflow_steps TEXT[] DEFAULT '{}',
    current_time_per_occurrence_seconds INTEGER,
    occurrences_per_day INTEGER DEFAULT 1,
    automation_complexity VARCHAR(50) DEFAULT 'medium' CHECK (automation_complexity IN ('low', 'medium', 'high')),
    implementation_effort_hours INTEGER,
    estimated_cost_savings_monthly DECIMAL(10,2),
    estimated_implementation_cost DECIMAL(10,2),
    roi_percentage DECIMAL(5,2),
    payback_period_days INTEGER,
    confidence_score DECIMAL(3,2) DEFAULT 0.00 CHECK (confidence_score >= 0.00 AND confidence_score <= 1.00),
    priority VARCHAR(50) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Workflow visualizations for flow charts
CREATE TABLE IF NOT EXISTS public.workflow_visualizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL REFERENCES public.analysis_results(id) ON DELETE CASCADE,
    session_id UUID NOT NULL REFERENCES public.recording_sessions(id) ON DELETE CASCADE,
    visualization_type VARCHAR(50) DEFAULT 'flow_chart',
    flow_data JSONB NOT NULL, -- nodes, edges, layout configuration
    layout_algorithm VARCHAR(50) DEFAULT 'dagre',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Cost analysis breakdowns
CREATE TABLE IF NOT EXISTS public.cost_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL REFERENCES public.analysis_results(id) ON DELETE CASCADE,
    session_id UUID NOT NULL REFERENCES public.recording_sessions(id) ON DELETE CASCADE,
    current_monthly_hours DECIMAL(8,2),
    current_hourly_rate DECIMAL(8,2) DEFAULT 25.00,
    current_monthly_cost DECIMAL(10,2),
    projected_monthly_hours DECIMAL(8,2),
    projected_monthly_cost DECIMAL(10,2),
    total_implementation_cost DECIMAL(10,2),
    monthly_savings DECIMAL(10,2),
    annual_savings DECIMAL(10,2),
    payback_period_days INTEGER,
    roi_percentage DECIMAL(5,2),
    confidence_level VARCHAR(50) DEFAULT 'medium',
    assumptions JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Generated reports and exports
CREATE TABLE IF NOT EXISTS public.generated_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL REFERENCES public.analysis_results(id) ON DELETE CASCADE,
    session_id UUID NOT NULL REFERENCES public.recording_sessions(id) ON DELETE CASCADE,
    report_type VARCHAR(50) NOT NULL CHECK (report_type IN ('pdf', 'excel', 'shareable_link', 'json_export')),
    file_url TEXT,
    file_size_bytes BIGINT,
    access_token VARCHAR(255), -- For shareable links
    is_public BOOLEAN DEFAULT FALSE,
    expires_at TIMESTAMP WITH TIME ZONE,
    download_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- STEP 4: Create indexes for performance
-- ============================================================================

-- Analysis results indexes
CREATE INDEX IF NOT EXISTS idx_analysis_results_session_status ON public.analysis_results(session_id, status);
CREATE INDEX IF NOT EXISTS idx_analysis_results_created_at ON public.analysis_results(created_at DESC);

-- Automation opportunities indexes
CREATE INDEX IF NOT EXISTS idx_automation_opportunities_analysis ON public.automation_opportunities(analysis_id);
CREATE INDEX IF NOT EXISTS idx_automation_opportunities_session ON public.automation_opportunities(session_id);
CREATE INDEX IF NOT EXISTS idx_automation_opportunities_priority_roi ON public.automation_opportunities(priority, roi_percentage DESC);

-- Workflow visualizations indexes
CREATE INDEX IF NOT EXISTS idx_workflow_visualizations_analysis ON public.workflow_visualizations(analysis_id);
CREATE INDEX IF NOT EXISTS idx_workflow_visualizations_session ON public.workflow_visualizations(session_id);

-- Cost analyses indexes
CREATE INDEX IF NOT EXISTS idx_cost_analyses_analysis ON public.cost_analyses(analysis_id);
CREATE INDEX IF NOT EXISTS idx_cost_analyses_session ON public.cost_analyses(session_id);

-- Generated reports indexes
CREATE INDEX IF NOT EXISTS idx_generated_reports_analysis ON public.generated_reports(analysis_id);
CREATE INDEX IF NOT EXISTS idx_generated_reports_type_public ON public.generated_reports(report_type, is_public);

-- STEP 5: Row Level Security (RLS) policies
-- ============================================================================

-- Enable RLS on all new tables
ALTER TABLE public.organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analysis_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.automation_opportunities ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workflow_visualizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.cost_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.generated_reports ENABLE ROW LEVEL SECURITY;

-- Organizations policies
CREATE POLICY "Users can view their organization" ON public.organizations
    FOR SELECT USING (
        id IN (
            SELECT organization_id FROM public.user_profiles 
            WHERE id = auth.uid()
        )
    );

-- Analysis results policies
CREATE POLICY "Users can view analysis results for their recordings" ON public.analysis_results
    FOR SELECT USING (
        session_id IN (
            SELECT id FROM public.recording_sessions 
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert analysis results for their recordings" ON public.analysis_results
    FOR INSERT WITH CHECK (
        session_id IN (
            SELECT id FROM public.recording_sessions 
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update analysis results for their recordings" ON public.analysis_results
    FOR UPDATE USING (
        session_id IN (
            SELECT id FROM public.recording_sessions 
            WHERE user_id = auth.uid()
        )
    );

-- Automation opportunities policies  
CREATE POLICY "Users can view automation opportunities for their recordings" ON public.automation_opportunities
    FOR SELECT USING (
        session_id IN (
            SELECT id FROM public.recording_sessions 
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert automation opportunities for their recordings" ON public.automation_opportunities
    FOR INSERT WITH CHECK (
        session_id IN (
            SELECT id FROM public.recording_sessions 
            WHERE user_id = auth.uid()
        )
    );

-- Workflow visualizations policies
CREATE POLICY "Users can view workflow visualizations for their recordings" ON public.workflow_visualizations
    FOR SELECT USING (
        session_id IN (
            SELECT id FROM public.recording_sessions 
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert workflow visualizations for their recordings" ON public.workflow_visualizations
    FOR INSERT WITH CHECK (
        session_id IN (
            SELECT id FROM public.recording_sessions 
            WHERE user_id = auth.uid()
        )
    );

-- Cost analyses policies
CREATE POLICY "Users can view cost analyses for their recordings" ON public.cost_analyses
    FOR SELECT USING (
        session_id IN (
            SELECT id FROM public.recording_sessions 
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert cost analyses for their recordings" ON public.cost_analyses
    FOR INSERT WITH CHECK (
        session_id IN (
            SELECT id FROM public.recording_sessions 
            WHERE user_id = auth.uid()
        )
    );

-- Generated reports policies
CREATE POLICY "Users can view their generated reports" ON public.generated_reports
    FOR SELECT USING (
        session_id IN (
            SELECT id FROM public.recording_sessions 
            WHERE user_id = auth.uid()
        )
        OR is_public = TRUE
    );

CREATE POLICY "Users can insert reports for their recordings" ON public.generated_reports
    FOR INSERT WITH CHECK (
        session_id IN (
            SELECT id FROM public.recording_sessions 
            WHERE user_id = auth.uid()
        )
    );

-- STEP 6: Create useful views for business intelligence
-- ============================================================================

-- Summary view for recording sessions with analysis status
CREATE OR REPLACE VIEW public.recording_sessions_summary AS
SELECT 
    rs.id,
    rs.user_id,
    rs.title,
    rs.status as recording_status,
    rs.duration_seconds,
    rs.created_at,
    rs.completed_at,
    ar.id as analysis_id,
    ar.status as analysis_status,
    ar.confidence_score,
    ar.analysis_cost,
    COUNT(ao.id) as automation_opportunities_count,
    COALESCE(SUM(ao.estimated_cost_savings_monthly), 0) as total_monthly_savings,
    COALESCE(AVG(ao.roi_percentage), 0) as average_roi
FROM public.recording_sessions rs
LEFT JOIN public.analysis_results ar ON rs.id = ar.session_id
LEFT JOIN public.automation_opportunities ao ON ar.id = ao.analysis_id
GROUP BY rs.id, ar.id;

-- ROI dashboard view
CREATE OR REPLACE VIEW public.roi_dashboard AS
SELECT 
    rs.user_id,
    COUNT(DISTINCT rs.id) as total_recordings,
    COUNT(DISTINCT ar.id) as completed_analyses,
    SUM(rs.duration_seconds) as total_recorded_seconds,
    SUM(ar.analysis_cost) as total_analysis_cost,
    COUNT(ao.id) as total_opportunities,
    SUM(ao.estimated_cost_savings_monthly) as total_monthly_savings,
    AVG(ao.roi_percentage) as average_roi,
    SUM(ca.annual_savings) as total_annual_savings
FROM public.recording_sessions rs
LEFT JOIN public.analysis_results ar ON rs.id = ar.session_id AND ar.status = 'completed'
LEFT JOIN public.automation_opportunities ao ON ar.id = ao.analysis_id
LEFT JOIN public.cost_analyses ca ON ar.id = ca.analysis_id
GROUP BY rs.user_id;

-- STEP 7: Insert default organization for existing users (optional)
-- ============================================================================

-- Create a default organization for MVP
INSERT INTO public.organizations (id, name, domain, subscription_tier, max_users, max_recordings_per_month)
VALUES (
    gen_random_uuid(),
    'NewSystem.AI MVP',
    'newsystem.ai',
    'mvp',
    100,
    1000
) ON CONFLICT DO NOTHING;

-- STEP 8: Migration complete message
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'DATABASE MIGRATION COMPLETED SUCCESSFULLY';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'PRESERVED: leads table and all existing data';
    RAISE NOTICE 'ENHANCED: recording_sessions with new analysis capabilities';
    RAISE NOTICE 'ADDED: comprehensive workflow analysis and visualization tables';
    RAISE NOTICE 'SECURED: Row Level Security policies for all tables';
    RAISE NOTICE 'OPTIMIZED: Indexes for query performance';
    RAISE NOTICE '';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '1. Update your backend .env with minimal configuration';
    RAISE NOTICE '2. Test connections with enhanced schema';
    RAISE NOTICE '3. Begin Week 2 development: GPT-4V analysis pipeline';
    RAISE NOTICE '========================================';
END
$$;