-- NewSystem.AI - Incremental Database Migration
-- Run this in Supabase SQL Editor to add missing tables and update existing ones
-- This handles the case where some tables already exist

-- Enable UUID extension if not exists
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- CREATE MISSING TABLES (IF NOT EXISTS)
-- ============================================

-- User profiles table (extends auth.users)
CREATE TABLE IF NOT EXISTS user_profiles (
  id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
  organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  role TEXT DEFAULT 'operator' CHECK (role IN ('owner', 'admin', 'operator')),
  first_name TEXT,
  last_name TEXT,
  job_title TEXT,
  settings JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Recording sessions table  
CREATE TABLE IF NOT EXISTS recording_sessions (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  organization_id UUID REFERENCES organizations(id) NOT NULL,
  title TEXT NOT NULL DEFAULT 'Workflow Recording',
  description TEXT,
  status TEXT NOT NULL DEFAULT 'recording' CHECK (status IN ('recording', 'processing', 'completed', 'failed')),
  duration_seconds INTEGER DEFAULT 0,
  file_size_bytes BIGINT DEFAULT 0,
  workflow_type TEXT,
  privacy_settings JSONB DEFAULT '{"blur_passwords": true, "exclude_personal_info": false}',
  recording_metadata JSONB DEFAULT '{}',
  analysis_cost DECIMAL(10,4) DEFAULT 0.00,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Video chunks table
CREATE TABLE IF NOT EXISTS video_chunks (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  session_id UUID REFERENCES recording_sessions(id) ON DELETE CASCADE NOT NULL,
  organization_id UUID REFERENCES organizations(id) NOT NULL,
  chunk_index INTEGER NOT NULL,
  file_path TEXT,
  file_size_bytes INTEGER,
  upload_status TEXT NOT NULL DEFAULT 'pending' CHECK (upload_status IN ('pending', 'uploading', 'completed', 'failed')),
  retry_count INTEGER DEFAULT 0,
  error_message TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  uploaded_at TIMESTAMPTZ
);

-- Analysis results table
CREATE TABLE IF NOT EXISTS analysis_results (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  session_id UUID REFERENCES recording_sessions(id) ON DELETE CASCADE NOT NULL,
  organization_id UUID REFERENCES organizations(id) NOT NULL,
  status TEXT DEFAULT 'queued' CHECK (status IN ('queued', 'processing', 'completed', 'failed')),
  gpt_version TEXT DEFAULT 'gpt-4o',
  processing_started_at TIMESTAMPTZ,
  processing_completed_at TIMESTAMPTZ,
  processing_time_seconds INTEGER,
  frames_analyzed INTEGER DEFAULT 0,
  analysis_cost DECIMAL(10,4) DEFAULT 0.00,
  confidence_score DECIMAL(3,2) DEFAULT 0.00 CHECK (confidence_score >= 0.00 AND confidence_score <= 1.00),
  
  -- Summary metrics for quick access
  automation_opportunities_count INTEGER DEFAULT 0,
  time_savings_hours_weekly DECIMAL(8,2) DEFAULT 0.00,
  cost_savings_annual DECIMAL(12,2) DEFAULT 0.00,
  
  -- Data storage
  raw_gpt_response JSONB,
  structured_insights JSONB DEFAULT '{}',
  error_message TEXT,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Automation opportunities table
CREATE TABLE IF NOT EXISTS automation_opportunities (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  analysis_id UUID REFERENCES analysis_results(id) ON DELETE CASCADE NOT NULL,
  session_id UUID REFERENCES recording_sessions(id) ON DELETE CASCADE NOT NULL,
  organization_id UUID REFERENCES organizations(id) NOT NULL,
  
  opportunity_type TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  workflow_steps JSONB DEFAULT '[]',
  
  -- Time and cost metrics
  current_time_per_occurrence_seconds INTEGER,
  occurrences_per_day INTEGER DEFAULT 1,
  automation_complexity TEXT DEFAULT 'medium' CHECK (automation_complexity IN ('low', 'medium', 'high')),
  implementation_effort_hours INTEGER,
  estimated_cost_savings_monthly DECIMAL(10,2),
  estimated_implementation_cost DECIMAL(10,2),
  roi_percentage DECIMAL(5,2),
  payback_period_days INTEGER,
  
  -- Metadata
  confidence_score DECIMAL(3,2) DEFAULT 0.00 CHECK (confidence_score >= 0.00 AND confidence_score <= 1.00),
  priority TEXT DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'critical')),
  record_metadata JSONB DEFAULT '{}',
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- UPDATE EXISTING ORGANIZATIONS TABLE
-- ============================================

-- Add missing columns to organizations table if they don't exist
DO $$
BEGIN
  -- Add domain column if missing
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'organizations' AND column_name = 'domain') THEN
    ALTER TABLE organizations ADD COLUMN domain TEXT;
  END IF;
  
  -- Add settings column if missing
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'organizations' AND column_name = 'settings') THEN
    ALTER TABLE organizations ADD COLUMN settings JSONB DEFAULT '{}';
  END IF;
  
  -- Add subscription_tier column if missing
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'organizations' AND column_name = 'subscription_tier') THEN
    ALTER TABLE organizations ADD COLUMN subscription_tier TEXT DEFAULT 'free' CHECK (subscription_tier IN ('free', 'starter', 'growth', 'enterprise'));
  END IF;
  
  -- Add subscription_status column if missing
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'organizations' AND column_name = 'subscription_status') THEN
    ALTER TABLE organizations ADD COLUMN subscription_status TEXT DEFAULT 'active' CHECK (subscription_status IN ('active', 'inactive', 'suspended'));
  END IF;
  
  -- Add max_users column if missing
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'organizations' AND column_name = 'max_users') THEN
    ALTER TABLE organizations ADD COLUMN max_users INTEGER DEFAULT 5;
  END IF;
  
  -- Add max_recordings_per_month column if missing
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'organizations' AND column_name = 'max_recordings_per_month') THEN
    ALTER TABLE organizations ADD COLUMN max_recordings_per_month INTEGER DEFAULT 50;
  END IF;
  
  -- Add created_at column if missing
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'organizations' AND column_name = 'created_at') THEN
    ALTER TABLE organizations ADD COLUMN created_at TIMESTAMPTZ DEFAULT NOW();
  END IF;
  
  -- Add updated_at column if missing
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'organizations' AND column_name = 'updated_at') THEN
    ALTER TABLE organizations ADD COLUMN updated_at TIMESTAMPTZ DEFAULT NOW();
  END IF;
END $$;

-- ============================================
-- ENABLE ROW LEVEL SECURITY
-- ============================================

-- Enable RLS on all tables
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE recording_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE video_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE analysis_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE automation_opportunities ENABLE ROW LEVEL SECURITY;

-- ============================================
-- DROP EXISTING POLICIES (IF ANY) AND RECREATE
-- ============================================

-- Drop existing policies to avoid conflicts
DROP POLICY IF EXISTS "Users can view own organization" ON organizations;
DROP POLICY IF EXISTS "Users can update own organization" ON organizations;
DROP POLICY IF EXISTS "Users can view own profile" ON user_profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON user_profiles;
DROP POLICY IF EXISTS "Users can view org members" ON user_profiles;
DROP POLICY IF EXISTS "Organization recording isolation" ON recording_sessions;
DROP POLICY IF EXISTS "Organization chunk isolation" ON video_chunks;
DROP POLICY IF EXISTS "Organization analysis isolation" ON analysis_results;
DROP POLICY IF EXISTS "Organization opportunity isolation" ON automation_opportunities;

-- Organizations: Users can only see their own organization
CREATE POLICY "Users can view own organization" ON organizations
  FOR SELECT USING (
    id = (SELECT organization_id FROM user_profiles WHERE id = auth.uid())
  );

CREATE POLICY "Users can update own organization" ON organizations
  FOR UPDATE USING (
    id = (SELECT organization_id FROM user_profiles WHERE id = auth.uid())
    AND (SELECT role FROM user_profiles WHERE id = auth.uid()) IN ('owner', 'admin')
  );

-- User Profiles: Users can see their own profile and org members
CREATE POLICY "Users can view own profile" ON user_profiles
  FOR SELECT USING (id = auth.uid());

CREATE POLICY "Users can update own profile" ON user_profiles
  FOR UPDATE USING (id = auth.uid());

CREATE POLICY "Users can view org members" ON user_profiles
  FOR SELECT USING (
    organization_id = (SELECT organization_id FROM user_profiles WHERE id = auth.uid())
  );

-- Recording Sessions: Organization isolation
CREATE POLICY "Organization recording isolation" ON recording_sessions
  FOR ALL USING (
    organization_id = (SELECT organization_id FROM user_profiles WHERE id = auth.uid())
  );

-- Video Chunks: Organization isolation  
CREATE POLICY "Organization chunk isolation" ON video_chunks
  FOR ALL USING (
    organization_id = (SELECT organization_id FROM user_profiles WHERE id = auth.uid())
  );

-- Analysis Results: Organization isolation
CREATE POLICY "Organization analysis isolation" ON analysis_results
  FOR ALL USING (
    organization_id = (SELECT organization_id FROM user_profiles WHERE id = auth.uid())
  );

-- Automation Opportunities: Organization isolation
CREATE POLICY "Organization opportunity isolation" ON automation_opportunities
  FOR ALL USING (
    organization_id = (SELECT organization_id FROM user_profiles WHERE id = auth.uid())
  );

-- ============================================
-- HELPER FUNCTIONS
-- ============================================

-- Function to get current user's organization ID
CREATE OR REPLACE FUNCTION get_user_organization_id(user_uuid UUID)
RETURNS UUID AS $$
BEGIN
  RETURN (SELECT organization_id FROM user_profiles WHERE id = user_uuid);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to create organization and owner profile
CREATE OR REPLACE FUNCTION create_organization_and_owner(
  user_id UUID,
  org_name TEXT,
  owner_first_name TEXT DEFAULT NULL,
  owner_last_name TEXT DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
  new_org_id UUID;
BEGIN
  -- Create organization
  INSERT INTO organizations (name)
  VALUES (org_name)
  RETURNING id INTO new_org_id;
  
  -- Create owner profile
  INSERT INTO user_profiles (id, organization_id, role, first_name, last_name)
  VALUES (user_id, new_org_id, 'owner', owner_first_name, owner_last_name);
  
  RETURN new_org_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================
-- CREATE INDEXES FOR PERFORMANCE
-- ============================================

-- Create indexes only if they don't exist
CREATE INDEX IF NOT EXISTS idx_user_profiles_organization_id ON user_profiles(organization_id);
CREATE INDEX IF NOT EXISTS idx_recording_sessions_org_user ON recording_sessions(organization_id, user_id);
CREATE INDEX IF NOT EXISTS idx_recording_sessions_status ON recording_sessions(status);
CREATE INDEX IF NOT EXISTS idx_video_chunks_session ON video_chunks(session_id, chunk_index);
CREATE INDEX IF NOT EXISTS idx_analysis_results_org_status ON analysis_results(organization_id, status);
CREATE INDEX IF NOT EXISTS idx_automation_opportunities_analysis ON automation_opportunities(analysis_id);

-- ============================================
-- UPDATED_AT TRIGGERS
-- ============================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop existing triggers and recreate them
DROP TRIGGER IF EXISTS update_organizations_updated_at ON organizations;
DROP TRIGGER IF EXISTS update_user_profiles_updated_at ON user_profiles;
DROP TRIGGER IF EXISTS update_recording_sessions_updated_at ON recording_sessions;
DROP TRIGGER IF EXISTS update_analysis_results_updated_at ON analysis_results;

-- Apply to tables that need updated_at
CREATE TRIGGER update_organizations_updated_at 
  BEFORE UPDATE ON organizations 
  FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_user_profiles_updated_at 
  BEFORE UPDATE ON user_profiles 
  FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_recording_sessions_updated_at 
  BEFORE UPDATE ON recording_sessions 
  FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_analysis_results_updated_at 
  BEFORE UPDATE ON analysis_results 
  FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

-- ============================================
-- MIGRATION COMPLETE
-- ============================================

-- Add table comments
COMMENT ON TABLE organizations IS 'Multi-tenant organization structure for NewSystem.AI - Updated incrementally';
COMMENT ON TABLE user_profiles IS 'User profiles extending Supabase auth.users with organization context';
COMMENT ON TABLE recording_sessions IS 'Screen recording sessions with multi-tenant isolation';
COMMENT ON TABLE analysis_results IS 'GPT-4V analysis results with RLS for data isolation';
COMMENT ON TABLE automation_opportunities IS 'Identified automation opportunities from analysis';

-- Success message
DO $$
BEGIN
  RAISE NOTICE 'NewSystem.AI incremental migration completed successfully!';
  RAISE NOTICE 'All missing tables created and existing tables updated.';
  RAISE NOTICE 'Row Level Security enabled with proper policies.';
END $$;