-- NewSystem.AI - Complete Multi-Tenant Migration
-- Adds organization_id to remaining tables for complete multi-tenant isolation
-- Supplement to bulletproof migration 004

-- ============================================
-- PHASE 1: PREPARE FOUNDATION
-- ============================================

DO $$
BEGIN
  RAISE NOTICE '🚀 Starting NewSystem.AI Complete Multi-Tenant Migration';
  RAISE NOTICE '📋 Phase 1: Adding organization_id to remaining tables...';
END $$;

-- ============================================
-- PHASE 2: ADD COLUMNS TO REMAINING TABLES
-- ============================================

-- Add organization_id to workflow_visualizations (nullable, no FK constraint yet)
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                 WHERE table_name = 'workflow_visualizations' AND column_name = 'organization_id') THEN
    ALTER TABLE workflow_visualizations ADD COLUMN organization_id UUID;
    RAISE NOTICE '✅ Added organization_id column to workflow_visualizations';
  ELSE
    RAISE NOTICE '✅ organization_id already exists in workflow_visualizations';
  END IF;
END $$;

-- Add organization_id to workflow_insights (nullable, no FK constraint yet)
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                 WHERE table_name = 'workflow_insights' AND column_name = 'organization_id') THEN
    ALTER TABLE workflow_insights ADD COLUMN organization_id UUID;
    RAISE NOTICE '✅ Added organization_id column to workflow_insights';
  ELSE
    RAISE NOTICE '✅ organization_id already exists in workflow_insights';
  END IF;
END $$;

-- Add organization_id to cost_analyses (nullable, no FK constraint yet)
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                 WHERE table_name = 'cost_analyses' AND column_name = 'organization_id') THEN
    ALTER TABLE cost_analyses ADD COLUMN organization_id UUID;
    RAISE NOTICE '✅ Added organization_id column to cost_analyses';
  ELSE
    RAISE NOTICE '✅ organization_id already exists in cost_analyses';
  END IF;
END $$;

-- Add organization_id to generated_reports (nullable, no FK constraint yet)
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                 WHERE table_name = 'generated_reports' AND column_name = 'organization_id') THEN
    ALTER TABLE generated_reports ADD COLUMN organization_id UUID;
    RAISE NOTICE '✅ Added organization_id column to generated_reports';
  ELSE
    RAISE NOTICE '✅ organization_id already exists in generated_reports';
  END IF;
END $$;

-- ============================================
-- PHASE 3: POPULATE DATA
-- ============================================

DO $$
BEGIN
  RAISE NOTICE '📋 Phase 3: Populating organization_id values in remaining tables...';
END $$;

-- Populate organization_id in workflow_visualizations via analysis_results
DO $$
DECLARE
  updated_visualizations INTEGER;
BEGIN
  UPDATE workflow_visualizations 
  SET organization_id = ar.organization_id
  FROM analysis_results ar
  WHERE workflow_visualizations.analysis_id = ar.id
    AND workflow_visualizations.organization_id IS NULL;
    
  GET DIAGNOSTICS updated_visualizations = ROW_COUNT;
  RAISE NOTICE '✅ Updated organization_id for % workflow visualizations', updated_visualizations;
END $$;

-- Populate organization_id in workflow_insights via recording_sessions
DO $$
DECLARE
  updated_insights INTEGER;
BEGIN
  UPDATE workflow_insights 
  SET organization_id = rs.organization_id
  FROM recording_sessions rs
  WHERE workflow_insights.session_id = rs.id
    AND workflow_insights.organization_id IS NULL;
    
  GET DIAGNOSTICS updated_insights = ROW_COUNT;
  RAISE NOTICE '✅ Updated organization_id for % workflow insights', updated_insights;
END $$;

-- Populate organization_id in cost_analyses via analysis_results
DO $$
DECLARE
  updated_costs INTEGER;
BEGIN
  UPDATE cost_analyses 
  SET organization_id = ar.organization_id
  FROM analysis_results ar
  WHERE cost_analyses.analysis_id = ar.id
    AND cost_analyses.organization_id IS NULL;
    
  GET DIAGNOSTICS updated_costs = ROW_COUNT;
  RAISE NOTICE '✅ Updated organization_id for % cost analyses', updated_costs;
END $$;

-- Populate organization_id in generated_reports via analysis_results
DO $$
DECLARE
  updated_reports INTEGER;
BEGIN
  UPDATE generated_reports 
  SET organization_id = ar.organization_id
  FROM analysis_results ar
  WHERE generated_reports.analysis_id = ar.id
    AND generated_reports.organization_id IS NULL;
    
  GET DIAGNOSTICS updated_reports = ROW_COUNT;
  RAISE NOTICE '✅ Updated organization_id for % generated reports', updated_reports;
END $$;

-- ============================================
-- PHASE 4: ADD CONSTRAINTS
-- ============================================

DO $$
BEGIN
  RAISE NOTICE '📋 Phase 4: Adding foreign key constraints to remaining tables...';
END $$;

-- Add foreign key constraint to workflow_visualizations
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints 
                 WHERE constraint_name = 'workflow_visualizations_organization_id_fkey' 
                 AND table_name = 'workflow_visualizations') THEN
    ALTER TABLE workflow_visualizations 
    ADD CONSTRAINT workflow_visualizations_organization_id_fkey 
    FOREIGN KEY (organization_id) REFERENCES organizations(id);
    RAISE NOTICE '✅ Added FK constraint to workflow_visualizations';
  ELSE
    RAISE NOTICE '✅ FK constraint already exists on workflow_visualizations';
  END IF;
END $$;

-- Add foreign key constraint to workflow_insights
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints 
                 WHERE constraint_name = 'workflow_insights_organization_id_fkey' 
                 AND table_name = 'workflow_insights') THEN
    ALTER TABLE workflow_insights 
    ADD CONSTRAINT workflow_insights_organization_id_fkey 
    FOREIGN KEY (organization_id) REFERENCES organizations(id);
    RAISE NOTICE '✅ Added FK constraint to workflow_insights';
  ELSE
    RAISE NOTICE '✅ FK constraint already exists on workflow_insights';
  END IF;
END $$;

-- Add foreign key constraint to cost_analyses
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints 
                 WHERE constraint_name = 'cost_analyses_organization_id_fkey' 
                 AND table_name = 'cost_analyses') THEN
    ALTER TABLE cost_analyses 
    ADD CONSTRAINT cost_analyses_organization_id_fkey 
    FOREIGN KEY (organization_id) REFERENCES organizations(id);
    RAISE NOTICE '✅ Added FK constraint to cost_analyses';
  ELSE
    RAISE NOTICE '✅ FK constraint already exists on cost_analyses';
  END IF;
END $$;

-- Add foreign key constraint to generated_reports
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints 
                 WHERE constraint_name = 'generated_reports_organization_id_fkey' 
                 AND table_name = 'generated_reports') THEN
    ALTER TABLE generated_reports 
    ADD CONSTRAINT generated_reports_organization_id_fkey 
    FOREIGN KEY (organization_id) REFERENCES organizations(id);
    RAISE NOTICE '✅ Added FK constraint to generated_reports';
  ELSE
    RAISE NOTICE '✅ FK constraint already exists on generated_reports';
  END IF;
END $$;

-- Make organization_id NOT NULL where we have data
DO $$
BEGIN
  -- Check if all workflow_visualizations have organization_id
  IF NOT EXISTS (SELECT 1 FROM workflow_visualizations WHERE organization_id IS NULL) THEN
    ALTER TABLE workflow_visualizations ALTER COLUMN organization_id SET NOT NULL;
    RAISE NOTICE '✅ Made organization_id NOT NULL in workflow_visualizations';
  END IF;
  
  -- Check if all workflow_insights have organization_id
  IF NOT EXISTS (SELECT 1 FROM workflow_insights WHERE organization_id IS NULL) THEN
    ALTER TABLE workflow_insights ALTER COLUMN organization_id SET NOT NULL;
    RAISE NOTICE '✅ Made organization_id NOT NULL in workflow_insights';
  END IF;
  
  -- Check if all cost_analyses have organization_id
  IF NOT EXISTS (SELECT 1 FROM cost_analyses WHERE organization_id IS NULL) THEN
    ALTER TABLE cost_analyses ALTER COLUMN organization_id SET NOT NULL;
    RAISE NOTICE '✅ Made organization_id NOT NULL in cost_analyses';
  END IF;
  
  -- Check if all generated_reports have organization_id
  IF NOT EXISTS (SELECT 1 FROM generated_reports WHERE organization_id IS NULL) THEN
    ALTER TABLE generated_reports ALTER COLUMN organization_id SET NOT NULL;
    RAISE NOTICE '✅ Made organization_id NOT NULL in generated_reports';
  END IF;
END $$;

-- ============================================
-- PHASE 5: ENABLE RLS ON REMAINING TABLES
-- ============================================

DO $$
BEGIN
  RAISE NOTICE '📋 Phase 5: Enabling Row Level Security on remaining tables...';
END $$;

-- Enable RLS on remaining tables
ALTER TABLE workflow_visualizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE workflow_insights ENABLE ROW LEVEL SECURITY;
ALTER TABLE cost_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE generated_reports ENABLE ROW LEVEL SECURITY;

-- Drop existing policies to avoid conflicts
DROP POLICY IF EXISTS "Organization workflow visualization isolation" ON workflow_visualizations;
DROP POLICY IF EXISTS "Organization workflow insights isolation" ON workflow_insights;
DROP POLICY IF EXISTS "Organization cost analysis isolation" ON cost_analyses;
DROP POLICY IF EXISTS "Organization report isolation" ON generated_reports;

-- Create RLS policies for remaining tables
CREATE POLICY "Organization workflow visualization isolation" ON workflow_visualizations
  FOR ALL USING (
    organization_id = (SELECT organization_id FROM user_profiles WHERE id = auth.uid())
  );

CREATE POLICY "Organization workflow insights isolation" ON workflow_insights
  FOR ALL USING (
    organization_id = (SELECT organization_id FROM user_profiles WHERE id = auth.uid())
  );

CREATE POLICY "Organization cost analysis isolation" ON cost_analyses
  FOR ALL USING (
    organization_id = (SELECT organization_id FROM user_profiles WHERE id = auth.uid())
  );

CREATE POLICY "Organization report isolation" ON generated_reports
  FOR ALL USING (
    organization_id = (SELECT organization_id FROM user_profiles WHERE id = auth.uid())
  );

DO $$
BEGIN
  RAISE NOTICE '✅ Created RLS policies for remaining tables';
END $$;

-- ============================================
-- PERFORMANCE INDEXES FOR REMAINING TABLES
-- ============================================

-- Create indexes for optimal performance on remaining tables
CREATE INDEX IF NOT EXISTS idx_workflow_visualizations_organization ON workflow_visualizations(organization_id);
CREATE INDEX IF NOT EXISTS idx_workflow_insights_organization ON workflow_insights(organization_id);
CREATE INDEX IF NOT EXISTS idx_cost_analyses_organization ON cost_analyses(organization_id);
CREATE INDEX IF NOT EXISTS idx_generated_reports_organization ON generated_reports(organization_id);

DO $$
BEGIN
  RAISE NOTICE '✅ Created performance indexes for remaining tables';
END $$;

-- ============================================
-- MIGRATION COMPLETE
-- ============================================

DO $$
BEGIN
  RAISE NOTICE '';
  RAISE NOTICE '🎉 NewSystem.AI Complete Multi-Tenant Migration COMPLETED SUCCESSFULLY!';
  RAISE NOTICE '';
  RAISE NOTICE '✅ Added organization_id to all remaining tables:';
  RAISE NOTICE '   - workflow_visualizations';
  RAISE NOTICE '   - workflow_insights';
  RAISE NOTICE '   - cost_analyses';
  RAISE NOTICE '   - generated_reports';
  RAISE NOTICE '✅ Row Level Security enabled on all remaining tables';
  RAISE NOTICE '✅ Performance indexes created';
  RAISE NOTICE '';
  RAISE NOTICE '🔒 Your database now has COMPLETE multi-tenant isolation!';
  RAISE NOTICE '🚀 All tables are secured with native Supabase RLS!';
END $$;