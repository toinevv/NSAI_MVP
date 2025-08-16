-- ============================================
-- SUPABASE MIGRATION 005: Analysis Metrics Columns
-- ============================================
-- Adds missing summary metrics columns to analysis_results table
-- These columns are required by the backend analysis and results APIs

DO $$
BEGIN
  RAISE NOTICE '🎯 Migration 005: Adding Analysis Metrics Columns to analysis_results';
END $$;

-- Add missing summary metrics columns to analysis_results
DO $$
BEGIN
  -- Check if automation_opportunities_count column exists
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                 WHERE table_name='analysis_results' AND column_name='automation_opportunities_count') THEN
    ALTER TABLE analysis_results ADD COLUMN automation_opportunities_count INTEGER DEFAULT 0;
    RAISE NOTICE '✅ Added automation_opportunities_count column';
  ELSE
    RAISE NOTICE '✅ automation_opportunities_count column already exists';
  END IF;

  -- Check if time_savings_hours_weekly column exists
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                 WHERE table_name='analysis_results' AND column_name='time_savings_hours_weekly') THEN
    ALTER TABLE analysis_results ADD COLUMN time_savings_hours_weekly DECIMAL(8,2) DEFAULT 0.00;
    RAISE NOTICE '✅ Added time_savings_hours_weekly column';
  ELSE
    RAISE NOTICE '✅ time_savings_hours_weekly column already exists';
  END IF;

  -- Check if cost_savings_annual column exists  
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                 WHERE table_name='analysis_results' AND column_name='cost_savings_annual') THEN
    ALTER TABLE analysis_results ADD COLUMN cost_savings_annual DECIMAL(12,2) DEFAULT 0.00;
    RAISE NOTICE '✅ Added cost_savings_annual column';
  ELSE
    RAISE NOTICE '✅ cost_savings_annual column already exists';
  END IF;
END $$;

-- Verify all required columns exist
DO $$
DECLARE
  missing_columns INTEGER := 0;
BEGIN
  -- Count missing columns
  SELECT COUNT(*) INTO missing_columns
  FROM (
    VALUES 
      ('automation_opportunities_count'),
      ('time_savings_hours_weekly'), 
      ('cost_savings_annual')
  ) AS required_cols(col_name)
  WHERE NOT EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name='analysis_results' AND column_name=required_cols.col_name
  );
  
  IF missing_columns = 0 THEN
    RAISE NOTICE '🎉 Migration 005 completed successfully - all analysis metrics columns present';
  ELSE
    RAISE EXCEPTION 'Migration 005 failed - % columns still missing', missing_columns;
  END IF;
END $$;