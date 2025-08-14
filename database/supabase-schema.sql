-- NewSystem.AI Database Schema
-- Logical, coherent structure for workflow analysis and automation discovery
-- Mission: Save 1,000,000 operator hours monthly through intelligent automation

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- =====================================================
-- ORGANIZATION & USER MANAGEMENT
-- =====================================================

-- Organizations table (supports multi-tenancy)
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    plan_type VARCHAR(50) DEFAULT 'starter', -- starter, growth, enterprise
    billing_email VARCHAR(255),
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Users table (extends Supabase auth.users)
CREATE TABLE users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'operator', -- operator, manager, admin
    department VARCHAR(100), -- logistics, warehouse, operations
    hourly_rate DECIMAL(8,2) DEFAULT 30.00, -- for ROI calculations
    preferences JSONB DEFAULT '{}',
    last_active_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- RECORDING MANAGEMENT
-- Core workflow capture functionality
-- =====================================================

-- Recording sessions
CREATE TABLE recordings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE NOT NULL,
    
    -- Recording metadata
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'recording' NOT NULL, -- recording, processing, completed, failed
    
    -- Technical details
    duration_seconds INTEGER,
    file_path TEXT, -- Supabase Storage path
    file_size_bytes BIGINT,
    frame_rate DECIMAL(3,1) DEFAULT 2.0,
    resolution VARCHAR(20), -- e.g., "1920x1080"
    
    -- Workflow context
    workflow_category VARCHAR(100), -- email_to_wms, excel_reporting, data_entry
    applications_used TEXT[], -- ['Outlook', 'SAP', 'Chrome']
    estimated_complexity VARCHAR(20) DEFAULT 'medium', -- low, medium, high
    
    -- Privacy and security
    privacy_settings JSONB DEFAULT '{}',
    contains_pii BOOLEAN DEFAULT false,
    data_masked BOOLEAN DEFAULT false,
    
    -- Timestamps
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Recording chunks (for chunked upload)
CREATE TABLE recording_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    recording_id UUID REFERENCES recordings(id) ON DELETE CASCADE NOT NULL,
    chunk_number INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    file_size_bytes INTEGER NOT NULL,
    duration_seconds DECIMAL(5,2),
    checksum VARCHAR(64), -- for integrity verification
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- AI ANALYSIS PIPELINE
-- GPT-4V workflow analysis and pattern recognition
-- =====================================================

-- Analysis jobs
CREATE TABLE analysis_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    recording_id UUID REFERENCES recordings(id) ON DELETE CASCADE NOT NULL,
    
    -- Processing metadata
    status VARCHAR(50) DEFAULT 'queued' NOT NULL, -- queued, processing, completed, failed
    gpt_version VARCHAR(50) DEFAULT 'gpt-4-vision-preview',
    
    -- Frame analysis
    total_frames INTEGER,
    analyzed_frames INTEGER,
    frame_selection_strategy VARCHAR(50) DEFAULT 'uniform', -- uniform, keyframe, smart
    
    -- Cost tracking
    processing_time_seconds INTEGER,
    api_calls INTEGER DEFAULT 0,
    processing_cost DECIMAL(8,4) DEFAULT 0.00,
    
    -- Results
    raw_gpt_response JSONB, -- Store complete GPT-4V response
    confidence_score DECIMAL(3,2), -- 0.00 to 1.00
    
    -- Error handling
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    
    -- Timestamps
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Extracted workflow patterns
CREATE TABLE workflow_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID REFERENCES analysis_results(id) ON DELETE CASCADE NOT NULL,
    
    -- Pattern identification
    pattern_type VARCHAR(100) NOT NULL, -- email_to_wms, copy_paste, navigation
    sequence_order INTEGER, -- Order in the workflow
    
    -- Timing analysis
    start_time_seconds DECIMAL(8,2),
    end_time_seconds DECIMAL(8,2),
    duration_seconds DECIMAL(8,2),
    frequency_per_session INTEGER DEFAULT 1,
    
    -- Pattern details
    source_application VARCHAR(100),
    target_application VARCHAR(100),
    action_type VARCHAR(50), -- click, type, copy, paste, navigate
    data_elements TEXT[], -- ['order_id', 'customer_name', 'quantity']
    
    -- Automation potential
    automation_score DECIMAL(3,2), -- 0.00 to 1.00
    repetition_detected BOOLEAN DEFAULT false,
    manual_effort_high BOOLEAN DEFAULT false,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- AUTOMATION OPPORTUNITIES
-- Business intelligence and recommendations
-- =====================================================

-- Identified automation opportunities
CREATE TABLE automation_opportunities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID REFERENCES analysis_results(id) ON DELETE CASCADE NOT NULL,
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE NOT NULL,
    
    -- Business classification
    workflow_type VARCHAR(100) NOT NULL, -- email_to_wms, excel_reporting, etc.
    priority VARCHAR(20) DEFAULT 'medium', -- high, medium, low
    category VARCHAR(50), -- data_entry, reporting, communication
    
    -- Impact analysis
    time_saved_weekly_hours DECIMAL(5,2) NOT NULL,
    frequency_per_day INTEGER DEFAULT 1,
    affected_users_count INTEGER DEFAULT 1,
    
    -- Implementation assessment
    implementation_complexity VARCHAR(50) NOT NULL, -- quick_win, strategic, consider, defer
    technical_difficulty VARCHAR(20) DEFAULT 'medium', -- easy, medium, hard
    required_integrations TEXT[], -- ['outlook', 'sap', 'excel']
    
    -- ROI calculations
    current_weekly_cost DECIMAL(8,2), -- hours * hourly_rate
    projected_weekly_cost DECIMAL(8,2),
    implementation_cost_estimate DECIMAL(10,2),
    payback_period_weeks INTEGER,
    annual_savings_estimate DECIMAL(12,2),
    roi_score DECIMAL(5,2), -- Calculated ROI percentage
    
    -- Automation details
    automation_potential DECIMAL(3,2) NOT NULL, -- 0.00 to 1.00
    description TEXT NOT NULL,
    recommended_approach TEXT,
    prerequisites TEXT[],
    risks TEXT[],
    
    -- Status tracking
    status VARCHAR(50) DEFAULT 'identified', -- identified, planned, in_progress, completed, rejected
    assigned_to UUID REFERENCES users(id),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- VISUALIZATION & REPORTING
-- Flow charts, dashboards, and business intelligence
-- =====================================================

-- Workflow visualizations (flow chart data)
CREATE TABLE workflow_visualizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID REFERENCES analysis_results(id) ON DELETE CASCADE NOT NULL,
    
    -- Visualization data
    flow_chart_data JSONB NOT NULL, -- nodes, edges, layout information
    thumbnail_url TEXT,
    
    -- Metrics
    total_nodes INTEGER,
    total_edges INTEGER,
    complexity_score DECIMAL(3,2),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Cost analysis results
CREATE TABLE cost_analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID REFERENCES analysis_results(id) ON DELETE CASCADE NOT NULL,
    
    -- Current state costs
    current_monthly_hours DECIMAL(8,2),
    current_monthly_cost DECIMAL(10,2),
    
    -- Projected state costs
    projected_monthly_hours DECIMAL(8,2),
    projected_monthly_cost DECIMAL(10,2),
    
    -- Implementation costs
    implementation_cost DECIMAL(10,2),
    maintenance_monthly_cost DECIMAL(8,2) DEFAULT 0,
    
    -- ROI metrics
    monthly_savings DECIMAL(10,2),
    annual_savings DECIMAL(12,2),
    payback_period_days INTEGER,
    roi_percentage DECIMAL(5,2),
    
    -- Detailed breakdown
    cost_breakdown JSONB DEFAULT '{}',
    assumptions JSONB DEFAULT '{}',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Generated reports (PDFs, exports)
CREATE TABLE generated_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID REFERENCES analysis_results(id) ON DELETE CASCADE NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    
    -- Report details
    report_type VARCHAR(50) NOT NULL, -- pdf, excel, csv, shareable_link
    title VARCHAR(255),
    file_url TEXT,
    file_size_bytes INTEGER,
    
    -- Sharing
    access_token VARCHAR(255) UNIQUE,
    is_public BOOLEAN DEFAULT false,
    expires_at TIMESTAMP WITH TIME ZONE,
    download_count INTEGER DEFAULT 0,
    
    -- Metadata
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_accessed_at TIMESTAMP WITH TIME ZONE
);

-- =====================================================
-- BUSINESS INTELLIGENCE & ANALYTICS
-- Aggregated metrics and insights
-- =====================================================

-- Daily usage metrics (for analytics dashboard)
CREATE TABLE daily_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE NOT NULL,
    date DATE NOT NULL,
    
    -- Recording metrics
    total_recordings INTEGER DEFAULT 0,
    total_recording_hours DECIMAL(8,2) DEFAULT 0,
    unique_users INTEGER DEFAULT 0,
    
    -- Analysis metrics
    completed_analyses INTEGER DEFAULT 0,
    total_processing_cost DECIMAL(8,2) DEFAULT 0,
    average_confidence_score DECIMAL(3,2),
    
    -- Business impact
    opportunities_identified INTEGER DEFAULT 0,
    total_hours_savable DECIMAL(8,2) DEFAULT 0,
    total_cost_savings DECIMAL(10,2) DEFAULT 0,
    
    -- Workflow categories
    workflow_breakdown JSONB DEFAULT '{}', -- {'email_to_wms': 5, 'excel_reporting': 3}
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure one record per org per day
    UNIQUE(organization_id, date)
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Recording indexes
CREATE INDEX idx_recordings_user_status ON recordings(user_id, status);
CREATE INDEX idx_recordings_org_created ON recordings(organization_id, created_at DESC);
CREATE INDEX idx_recordings_workflow_category ON recordings(workflow_category);
CREATE INDEX idx_recordings_status_created ON recordings(status, created_at DESC);

-- Analysis indexes
CREATE INDEX idx_analysis_recording ON analysis_results(recording_id);
CREATE INDEX idx_analysis_status_created ON analysis_results(status, created_at DESC);

-- Automation opportunities indexes
CREATE INDEX idx_opportunities_analysis ON automation_opportunities(analysis_id);
CREATE INDEX idx_opportunities_org_priority ON automation_opportunities(organization_id, priority, roi_score DESC);
CREATE INDEX idx_opportunities_status ON automation_opportunities(status);

-- Workflow patterns indexes
CREATE INDEX idx_patterns_analysis ON workflow_patterns(analysis_id);
CREATE INDEX idx_patterns_type_automation ON workflow_patterns(pattern_type, automation_score DESC);

-- Reports indexes
CREATE INDEX idx_reports_analysis ON generated_reports(analysis_id);
CREATE INDEX idx_reports_token ON generated_reports(access_token);
CREATE INDEX idx_reports_expires ON generated_reports(expires_at);

-- Metrics indexes
CREATE INDEX idx_daily_metrics_org_date ON daily_metrics(organization_id, date DESC);

-- =====================================================
-- TRIGGERS FOR AUTOMATIC UPDATES
-- =====================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers to relevant tables
CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_recordings_updated_at BEFORE UPDATE ON recordings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_opportunities_updated_at BEFORE UPDATE ON automation_opportunities FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- ROW LEVEL SECURITY (RLS)
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE recordings ENABLE ROW LEVEL SECURITY;
ALTER TABLE recording_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE analysis_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE workflow_patterns ENABLE ROW LEVEL SECURITY;
ALTER TABLE automation_opportunities ENABLE ROW LEVEL SECURITY;
ALTER TABLE workflow_visualizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE cost_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE generated_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_metrics ENABLE ROW LEVEL SECURITY;

-- Basic RLS policies (users can only see their organization's data)
CREATE POLICY "Users can view their own profile" ON users FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update their own profile" ON users FOR UPDATE USING (auth.uid() = id);

-- Organization-based access for recordings
CREATE POLICY "Users can view org recordings" ON recordings FOR SELECT USING (
    organization_id IN (
        SELECT organization_id FROM users WHERE id = auth.uid()
    )
);

CREATE POLICY "Users can create recordings in their org" ON recordings FOR INSERT WITH CHECK (
    organization_id IN (
        SELECT organization_id FROM users WHERE id = auth.uid()
    )
);

-- Similar policies for other tables would be added here
-- For MVP, we'll implement basic policies and enhance in Week 2

-- =====================================================
-- SAMPLE DATA FOR DEVELOPMENT
-- =====================================================

-- Insert sample organization
INSERT INTO organizations (id, name, plan_type, billing_email) VALUES 
('550e8400-e29b-41d4-a716-446655440000', 'ACME Logistics', 'growth', 'billing@acmelogistics.com');

-- Note: Users will be created automatically via Supabase Auth
-- Sample user data will be inserted via the application

-- =====================================================
-- VIEWS FOR COMMON QUERIES
-- =====================================================

-- View for complete recording analysis data
CREATE VIEW recording_analysis_summary AS
SELECT 
    r.id as recording_id,
    r.title,
    r.duration_seconds,
    r.workflow_category,
    r.status as recording_status,
    ar.id as analysis_id,
    ar.status as analysis_status,
    ar.confidence_score,
    ar.processing_cost,
    COUNT(ao.id) as opportunities_count,
    COALESCE(SUM(ao.time_saved_weekly_hours), 0) as total_weekly_savings,
    COALESCE(SUM(ao.annual_savings_estimate), 0) as total_annual_savings
FROM recordings r
LEFT JOIN analysis_results ar ON r.id = ar.recording_id
LEFT JOIN automation_opportunities ao ON ar.id = ao.analysis_id
GROUP BY r.id, ar.id;

-- View for organization dashboard metrics
CREATE VIEW organization_dashboard AS
SELECT 
    o.id as organization_id,
    o.name as organization_name,
    COUNT(DISTINCT u.id) as total_users,
    COUNT(DISTINCT r.id) as total_recordings,
    COALESCE(SUM(r.duration_seconds), 0) / 3600.0 as total_hours_recorded,
    COUNT(DISTINCT CASE WHEN ar.status = 'completed' THEN ar.id END) as completed_analyses,
    COUNT(DISTINCT ao.id) as total_opportunities,
    COALESCE(SUM(ao.time_saved_weekly_hours), 0) as total_weekly_savings,
    COALESCE(SUM(ao.annual_savings_estimate), 0) as total_annual_savings,
    COALESCE(AVG(ar.confidence_score), 0) as avg_confidence_score
FROM organizations o
LEFT JOIN users u ON o.id = u.organization_id
LEFT JOIN recordings r ON o.id = r.organization_id
LEFT JOIN analysis_results ar ON r.id = ar.recording_id
LEFT JOIN automation_opportunities ao ON ar.id = ao.analysis_id
GROUP BY o.id, o.name;

-- =====================================================
-- DATABASE VERSION & METADATA
-- =====================================================

-- Track schema version for migrations
CREATE TABLE schema_version (
    version VARCHAR(20) PRIMARY KEY,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    description TEXT
);

INSERT INTO schema_version (version, description) VALUES 
('1.0.0', 'Initial NewSystem.AI schema - Foundation for saving 1,000,000 operator hours monthly');

-- =====================================================
-- COMMENTS FOR DOCUMENTATION
-- =====================================================

COMMENT ON DATABASE postgres IS 'NewSystem.AI - AI-powered workflow analysis for logistics operations';

COMMENT ON TABLE organizations IS 'Multi-tenant organization management';
COMMENT ON TABLE users IS 'Extended user profiles for logistics operators';
COMMENT ON TABLE recordings IS 'Screen recording sessions capturing operator workflows';
COMMENT ON TABLE analysis_results IS 'GPT-4V analysis results and processing metadata';
COMMENT ON TABLE automation_opportunities IS 'Identified automation opportunities with ROI analysis';
COMMENT ON TABLE workflow_patterns IS 'Extracted workflow patterns and sequences';
COMMENT ON TABLE cost_analyses IS 'Detailed cost-benefit analysis for automation opportunities';

-- Success message
SELECT 'NewSystem.AI database schema created successfully! Ready to save 1,000,000 operator hours monthly.' as message;