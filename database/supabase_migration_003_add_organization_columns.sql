-- NewSystem.AI - Add Organization Columns Migration
-- This adds the missing organization_id columns to existing tables
-- Run this in Supabase SQL Editor

-- ============================================
-- ADD MISSING ORGANIZATION_ID COLUMNS
-- ============================================

-- Add organization_id to recording_sessions (if missing)
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'recording_sessions' AND column_name = 'organization_id') THEN
    ALTER TABLE recording_sessions ADD COLUMN organization_id UUID REFERENCES organizations(id);
    RAISE NOTICE 'Added organization_id column to recording_sessions';
  END IF;
END $$;

-- Add organization_id to analysis_results (if missing)
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'analysis_results' AND column_name = 'organization_id') THEN
    ALTER TABLE analysis_results ADD COLUMN organization_id UUID REFERENCES organizations(id);
    RAISE NOTICE 'Added organization_id column to analysis_results';
  END IF;
END $$;

-- Add organization_id to video_chunks (if missing)
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'video_chunks' AND column_name = 'organization_id') THEN
    ALTER TABLE video_chunks ADD COLUMN organization_id UUID REFERENCES organizations(id);
    RAISE NOTICE 'Added organization_id column to video_chunks';
  END IF;
END $$;

-- Add organization_id to automation_opportunities (if missing)
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'automation_opportunities' AND column_name = 'organization_id') THEN
    ALTER TABLE automation_opportunities ADD COLUMN organization_id UUID REFERENCES organizations(id);
    RAISE NOTICE 'Added organization_id column to automation_opportunities';
  END IF;
END $$;

-- ============================================
-- POPULATE ORGANIZATION_ID VALUES
-- ============================================

-- First, let's create a default organization if none exists
INSERT INTO organizations (id, name, subscription_tier)
SELECT 
  '00000000-0000-0000-0000-000000000001'::uuid,
  'Default Organization',
  'growth'
WHERE NOT EXISTS (SELECT 1 FROM organizations LIMIT 1);

-- Create a default user profile for existing users without one
-- This ensures all users have an organization_id
INSERT INTO user_profiles (id, organization_id, role, first_name, last_name)
SELECT 
  u.id,
  '00000000-0000-0000-0000-000000000001'::uuid,
  'owner',
  'Default',
  'User'
FROM auth.users u
WHERE NOT EXISTS (SELECT 1 FROM user_profiles WHERE id = u.id);

-- Update recording_sessions with organization_id from user_profiles
UPDATE recording_sessions 
SET organization_id = (
  SELECT organization_id 
  FROM user_profiles 
  WHERE user_profiles.id = recording_sessions.user_id
)
WHERE organization_id IS NULL;

-- Update analysis_results with organization_id via recording_sessions
UPDATE analysis_results 
SET organization_id = (
  SELECT rs.organization_id 
  FROM recording_sessions rs 
  WHERE rs.id = analysis_results.session_id
)
WHERE organization_id IS NULL;

-- Update video_chunks with organization_id via recording_sessions
UPDATE video_chunks 
SET organization_id = (
  SELECT rs.organization_id 
  FROM recording_sessions rs 
  WHERE rs.id = video_chunks.session_id
)
WHERE organization_id IS NULL;

-- Update automation_opportunities with organization_id via recording_sessions
UPDATE automation_opportunities 
SET organization_id = (
  SELECT rs.organization_id 
  FROM recording_sessions rs 
  WHERE rs.id = automation_opportunities.session_id
)
WHERE organization_id IS NULL;

-- ============================================
-- MAKE ORGANIZATION_ID NOT NULL (after populating)
-- ============================================

-- Make organization_id NOT NULL for recording_sessions
ALTER TABLE recording_sessions ALTER COLUMN organization_id SET NOT NULL;

-- Make organization_id NOT NULL for analysis_results
ALTER TABLE analysis_results ALTER COLUMN organization_id SET NOT NULL;

-- Make organization_id NOT NULL for video_chunks
ALTER TABLE video_chunks ALTER COLUMN organization_id SET NOT NULL;

-- Make organization_id NOT NULL for automation_opportunities
ALTER TABLE automation_opportunities ALTER COLUMN organization_id SET NOT NULL;

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
-- CREATE RLS POLICIES
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
CREATE INDEX IF NOT EXISTS idx_video_chunks_organization ON video_chunks(organization_id);
CREATE INDEX IF NOT EXISTS idx_analysis_results_org_status ON analysis_results(organization_id, status);
CREATE INDEX IF NOT EXISTS idx_automation_opportunities_analysis ON automation_opportunities(analysis_id);
CREATE INDEX IF NOT EXISTS idx_automation_opportunities_org ON automation_opportunities(organization_id);

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

DO $$
BEGIN
  RAISE NOTICE '✅ NewSystem.AI organization columns migration completed successfully!';
  RAISE NOTICE '📊 All tables now have organization_id columns for multi-tenancy';
  RAISE NOTICE '🔒 Row Level Security enabled with proper organization isolation';
  RAISE NOTICE '🔧 Helper functions and indexes created for optimal performance';
END $$;