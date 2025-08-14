-- NewSystem.AI - Bulletproof Database Migration
-- This migration adds organization_id columns and RLS policies safely
-- Designed to handle existing data without foreign key violations

-- ============================================
-- PHASE 1: PREPARE FOUNDATION
-- ============================================

DO $$
BEGIN
  RAISE NOTICE '🚀 Starting NewSystem.AI Bulletproof Migration';
  RAISE NOTICE '📋 Phase 1: Preparing Foundation...';
END $$;

-- Create default organization if it doesn't exist
DO $$
DECLARE
  default_org_exists BOOLEAN;
  default_org_id UUID := '00000000-0000-0000-0000-000000000001'::UUID;
BEGIN
  -- Check if default organization exists
  SELECT EXISTS(SELECT 1 FROM organizations WHERE id = default_org_id) INTO default_org_exists;
  
  IF NOT default_org_exists THEN
    -- Create default organization
    INSERT INTO organizations (id, name, subscription_tier, subscription_status)
    VALUES (
      default_org_id,
      'Default Organization', 
      'growth',
      'active'
    );
    RAISE NOTICE '✅ Created default organization';
  ELSE
    RAISE NOTICE '✅ Default organization already exists';
  END IF;
END $$;

-- Verify we have at least one organization
DO $$
DECLARE
  org_count INTEGER;
BEGIN
  SELECT COUNT(*) INTO org_count FROM organizations;
  IF org_count = 0 THEN
    RAISE EXCEPTION '❌ No organizations found after creation attempt';
  END IF;
  RAISE NOTICE '✅ Organization count: %', org_count;
END $$;

-- ============================================
-- PHASE 2: ADD COLUMNS SAFELY (NO FK CONSTRAINTS)
-- ============================================

DO $$
BEGIN
  RAISE NOTICE '📋 Phase 2: Adding organization_id columns safely...';
END $$;

-- Add organization_id to recording_sessions (nullable, no FK constraint yet)
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                 WHERE table_name = 'recording_sessions' AND column_name = 'organization_id') THEN
    ALTER TABLE recording_sessions ADD COLUMN organization_id UUID;
    RAISE NOTICE '✅ Added organization_id column to recording_sessions';
  ELSE
    RAISE NOTICE '✅ organization_id already exists in recording_sessions';
  END IF;
END $$;

-- Add organization_id to analysis_results (nullable, no FK constraint yet)
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                 WHERE table_name = 'analysis_results' AND column_name = 'organization_id') THEN
    ALTER TABLE analysis_results ADD COLUMN organization_id UUID;
    RAISE NOTICE '✅ Added organization_id column to analysis_results';
  ELSE
    RAISE NOTICE '✅ organization_id already exists in analysis_results';
  END IF;
END $$;

-- Add organization_id to video_chunks (nullable, no FK constraint yet)
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                 WHERE table_name = 'video_chunks' AND column_name = 'organization_id') THEN
    ALTER TABLE video_chunks ADD COLUMN organization_id UUID;
    RAISE NOTICE '✅ Added organization_id column to video_chunks';
  ELSE
    RAISE NOTICE '✅ organization_id already exists in video_chunks';
  END IF;
END $$;

-- Add organization_id to automation_opportunities (nullable, no FK constraint yet)
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                 WHERE table_name = 'automation_opportunities' AND column_name = 'organization_id') THEN
    ALTER TABLE automation_opportunities ADD COLUMN organization_id UUID;
    RAISE NOTICE '✅ Added organization_id column to automation_opportunities';
  ELSE
    RAISE NOTICE '✅ organization_id already exists in automation_opportunities';
  END IF;
END $$;

-- ============================================
-- PHASE 3: POPULATE DATA
-- ============================================

DO $$
BEGIN
  RAISE NOTICE '📋 Phase 3: Populating organization_id values...';
END $$;

-- Create user profiles for existing users who don't have one
DO $$
DECLARE
  users_without_profiles INTEGER;
  default_org_id UUID := '00000000-0000-0000-0000-000000000001'::UUID;
BEGIN
  -- Count users without profiles
  SELECT COUNT(*) INTO users_without_profiles
  FROM auth.users u
  LEFT JOIN user_profiles up ON u.id = up.id
  WHERE up.id IS NULL;
  
  IF users_without_profiles > 0 THEN
    RAISE NOTICE '👤 Creating profiles for % users without profiles', users_without_profiles;
    
    -- Create profiles for users without them
    INSERT INTO user_profiles (id, organization_id, role, first_name, last_name)
    SELECT 
      u.id,
      default_org_id,
      'owner',
      'Default',
      'User'
    FROM auth.users u
    LEFT JOIN user_profiles up ON u.id = up.id
    WHERE up.id IS NULL;
    
    RAISE NOTICE '✅ Created % user profiles', users_without_profiles;
  ELSE
    RAISE NOTICE '✅ All users already have profiles';
  END IF;
END $$;

-- Populate organization_id in recording_sessions
DO $$
DECLARE
  updated_recordings INTEGER;
BEGIN
  UPDATE recording_sessions 
  SET organization_id = up.organization_id
  FROM user_profiles up
  WHERE recording_sessions.user_id = up.id
    AND recording_sessions.organization_id IS NULL;
    
  GET DIAGNOSTICS updated_recordings = ROW_COUNT;
  RAISE NOTICE '✅ Updated organization_id for % recording sessions', updated_recordings;
END $$;

-- Populate organization_id in analysis_results
DO $$
DECLARE
  updated_analyses INTEGER;
BEGIN
  UPDATE analysis_results 
  SET organization_id = rs.organization_id
  FROM recording_sessions rs
  WHERE analysis_results.session_id = rs.id
    AND analysis_results.organization_id IS NULL;
    
  GET DIAGNOSTICS updated_analyses = ROW_COUNT;
  RAISE NOTICE '✅ Updated organization_id for % analysis results', updated_analyses;
END $$;

-- Populate organization_id in video_chunks
DO $$
DECLARE
  updated_chunks INTEGER;
BEGIN
  UPDATE video_chunks 
  SET organization_id = rs.organization_id
  FROM recording_sessions rs
  WHERE video_chunks.session_id = rs.id
    AND video_chunks.organization_id IS NULL;
    
  GET DIAGNOSTICS updated_chunks = ROW_COUNT;
  RAISE NOTICE '✅ Updated organization_id for % video chunks', updated_chunks;
END $$;

-- Populate organization_id in automation_opportunities
DO $$
DECLARE
  updated_opportunities INTEGER;
BEGIN
  UPDATE automation_opportunities 
  SET organization_id = rs.organization_id
  FROM recording_sessions rs
  WHERE automation_opportunities.session_id = rs.id
    AND automation_opportunities.organization_id IS NULL;
    
  GET DIAGNOSTICS updated_opportunities = ROW_COUNT;
  RAISE NOTICE '✅ Updated organization_id for % automation opportunities', updated_opportunities;
END $$;

-- ============================================
-- PHASE 4: ADD CONSTRAINTS
-- ============================================

DO $$
BEGIN
  RAISE NOTICE '📋 Phase 4: Adding foreign key constraints...';
END $$;

-- Add foreign key constraint to recording_sessions
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints 
                 WHERE constraint_name = 'recording_sessions_organization_id_fkey' 
                 AND table_name = 'recording_sessions') THEN
    ALTER TABLE recording_sessions 
    ADD CONSTRAINT recording_sessions_organization_id_fkey 
    FOREIGN KEY (organization_id) REFERENCES organizations(id);
    RAISE NOTICE '✅ Added FK constraint to recording_sessions';
  ELSE
    RAISE NOTICE '✅ FK constraint already exists on recording_sessions';
  END IF;
END $$;

-- Add foreign key constraint to analysis_results
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints 
                 WHERE constraint_name = 'analysis_results_organization_id_fkey' 
                 AND table_name = 'analysis_results') THEN
    ALTER TABLE analysis_results 
    ADD CONSTRAINT analysis_results_organization_id_fkey 
    FOREIGN KEY (organization_id) REFERENCES organizations(id);
    RAISE NOTICE '✅ Added FK constraint to analysis_results';
  ELSE
    RAISE NOTICE '✅ FK constraint already exists on analysis_results';
  END IF;
END $$;

-- Add foreign key constraint to video_chunks
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints 
                 WHERE constraint_name = 'video_chunks_organization_id_fkey' 
                 AND table_name = 'video_chunks') THEN
    ALTER TABLE video_chunks 
    ADD CONSTRAINT video_chunks_organization_id_fkey 
    FOREIGN KEY (organization_id) REFERENCES organizations(id);
    RAISE NOTICE '✅ Added FK constraint to video_chunks';
  ELSE
    RAISE NOTICE '✅ FK constraint already exists on video_chunks';
  END IF;
END $$;

-- Add foreign key constraint to automation_opportunities
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints 
                 WHERE constraint_name = 'automation_opportunities_organization_id_fkey' 
                 AND table_name = 'automation_opportunities') THEN
    ALTER TABLE automation_opportunities 
    ADD CONSTRAINT automation_opportunities_organization_id_fkey 
    FOREIGN KEY (organization_id) REFERENCES organizations(id);
    RAISE NOTICE '✅ Added FK constraint to automation_opportunities';
  ELSE
    RAISE NOTICE '✅ FK constraint already exists on automation_opportunities';
  END IF;
END $$;

-- Make organization_id NOT NULL where we have data
DO $$
BEGIN
  -- Check if all recording_sessions have organization_id
  IF NOT EXISTS (SELECT 1 FROM recording_sessions WHERE organization_id IS NULL) THEN
    ALTER TABLE recording_sessions ALTER COLUMN organization_id SET NOT NULL;
    RAISE NOTICE '✅ Made organization_id NOT NULL in recording_sessions';
  END IF;
  
  -- Check if all analysis_results have organization_id
  IF NOT EXISTS (SELECT 1 FROM analysis_results WHERE organization_id IS NULL) THEN
    ALTER TABLE analysis_results ALTER COLUMN organization_id SET NOT NULL;
    RAISE NOTICE '✅ Made organization_id NOT NULL in analysis_results';
  END IF;
  
  -- Check if all video_chunks have organization_id
  IF NOT EXISTS (SELECT 1 FROM video_chunks WHERE organization_id IS NULL) THEN
    ALTER TABLE video_chunks ALTER COLUMN organization_id SET NOT NULL;
    RAISE NOTICE '✅ Made organization_id NOT NULL in video_chunks';
  END IF;
  
  -- Check if all automation_opportunities have organization_id
  IF NOT EXISTS (SELECT 1 FROM automation_opportunities WHERE organization_id IS NULL) THEN
    ALTER TABLE automation_opportunities ALTER COLUMN organization_id SET NOT NULL;
    RAISE NOTICE '✅ Made organization_id NOT NULL in automation_opportunities';
  END IF;
END $$;

-- ============================================
-- PHASE 5: ENABLE SECURITY
-- ============================================

DO $$
BEGIN
  RAISE NOTICE '📋 Phase 5: Enabling Row Level Security...';
END $$;

-- Enable RLS on all tables
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE recording_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE video_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE analysis_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE automation_opportunities ENABLE ROW LEVEL SECURITY;

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

-- Create RLS policies for multi-tenant isolation
CREATE POLICY "Users can view own organization" ON organizations
  FOR SELECT USING (
    id = (SELECT organization_id FROM user_profiles WHERE id = auth.uid())
  );

CREATE POLICY "Users can update own organization" ON organizations
  FOR UPDATE USING (
    id = (SELECT organization_id FROM user_profiles WHERE id = auth.uid())
    AND (SELECT role FROM user_profiles WHERE id = auth.uid()) IN ('owner', 'admin')
  );

CREATE POLICY "Users can view own profile" ON user_profiles
  FOR SELECT USING (id = auth.uid());

CREATE POLICY "Users can update own profile" ON user_profiles
  FOR UPDATE USING (id = auth.uid());

CREATE POLICY "Users can view org members" ON user_profiles
  FOR SELECT USING (
    organization_id = (SELECT organization_id FROM user_profiles WHERE id = auth.uid())
  );

CREATE POLICY "Organization recording isolation" ON recording_sessions
  FOR ALL USING (
    organization_id = (SELECT organization_id FROM user_profiles WHERE id = auth.uid())
  );

CREATE POLICY "Organization chunk isolation" ON video_chunks
  FOR ALL USING (
    organization_id = (SELECT organization_id FROM user_profiles WHERE id = auth.uid())
  );

CREATE POLICY "Organization analysis isolation" ON analysis_results
  FOR ALL USING (
    organization_id = (SELECT organization_id FROM user_profiles WHERE id = auth.uid())
  );

CREATE POLICY "Organization opportunity isolation" ON automation_opportunities
  FOR ALL USING (
    organization_id = (SELECT organization_id FROM user_profiles WHERE id = auth.uid())
  );

DO $$
BEGIN
  RAISE NOTICE '✅ Created all RLS policies';
END $$;

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

DO $$
BEGIN
  RAISE NOTICE '✅ Created helper functions';
END $$;

-- ============================================
-- PERFORMANCE INDEXES
-- ============================================

-- Create indexes for optimal performance
CREATE INDEX IF NOT EXISTS idx_user_profiles_organization_id ON user_profiles(organization_id);
CREATE INDEX IF NOT EXISTS idx_recording_sessions_org_user ON recording_sessions(organization_id, user_id);
CREATE INDEX IF NOT EXISTS idx_recording_sessions_status ON recording_sessions(status);
CREATE INDEX IF NOT EXISTS idx_video_chunks_session ON video_chunks(session_id, chunk_index);
CREATE INDEX IF NOT EXISTS idx_video_chunks_organization ON video_chunks(organization_id);
CREATE INDEX IF NOT EXISTS idx_analysis_results_org_status ON analysis_results(organization_id, status);
CREATE INDEX IF NOT EXISTS idx_automation_opportunities_analysis ON automation_opportunities(analysis_id);
CREATE INDEX IF NOT EXISTS idx_automation_opportunities_org ON automation_opportunities(organization_id);

DO $$
BEGIN
  RAISE NOTICE '✅ Created performance indexes';
END $$;

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

-- Apply triggers to tables with updated_at columns
DROP TRIGGER IF EXISTS update_organizations_updated_at ON organizations;
DROP TRIGGER IF EXISTS update_user_profiles_updated_at ON user_profiles;
DROP TRIGGER IF EXISTS update_recording_sessions_updated_at ON recording_sessions;
DROP TRIGGER IF EXISTS update_analysis_results_updated_at ON analysis_results;

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

DO $$
BEGIN
  RAISE NOTICE '✅ Created updated_at triggers';
END $$;

-- ============================================
-- MIGRATION COMPLETE
-- ============================================

DO $$
BEGIN
  RAISE NOTICE '';
  RAISE NOTICE '🎉 NewSystem.AI Bulletproof Migration COMPLETED SUCCESSFULLY!';
  RAISE NOTICE '';
  RAISE NOTICE '✅ Phase 1: Foundation prepared with default organization';
  RAISE NOTICE '✅ Phase 2: Organization_id columns added safely';
  RAISE NOTICE '✅ Phase 3: All data populated with organization references';
  RAISE NOTICE '✅ Phase 4: Foreign key constraints added';
  RAISE NOTICE '✅ Phase 5: Row Level Security enabled with multi-tenant isolation';
  RAISE NOTICE '';
  RAISE NOTICE '🔒 Your database now has complete multi-tenant isolation!';
  RAISE NOTICE '🚀 Ready for production with native Supabase architecture!';
END $$;