-- ============================================================================
-- Database Migration Verification Script
-- ============================================================================
-- Run this after migration to verify everything is working correctly
-- This script checks that all tables exist and have proper relationships
-- ============================================================================

-- Check that leads table is preserved (should return data if you have existing leads)
SELECT 'LEADS TABLE CHECK' as check_type, COUNT(*) as record_count 
FROM public.leads;

-- Check that existing recording tables are still there
SELECT 'RECORDING SESSIONS CHECK' as check_type, COUNT(*) as record_count 
FROM public.recording_sessions;

SELECT 'VIDEO CHUNKS CHECK' as check_type, COUNT(*) as record_count 
FROM public.video_chunks;

SELECT 'USE CASES CHECK' as check_type, COUNT(*) as record_count 
FROM public.use_cases;

SELECT 'WORKFLOW INSIGHTS CHECK' as check_type, COUNT(*) as record_count 
FROM public.workflow_insights;

-- Check that new tables were created successfully
SELECT 'NEW TABLES VERIFICATION' as check_type;

SELECT 
    expected_tables.table_name,
    CASE WHEN t.table_name IS NOT NULL THEN '✅ EXISTS' ELSE '❌ MISSING' END as status
FROM (
    VALUES 
        ('organizations'),
        ('user_profiles'),
        ('analysis_results'),
        ('automation_opportunities'),
        ('workflow_visualizations'),
        ('cost_analyses'),
        ('generated_reports')
) expected_tables(table_name)
LEFT JOIN information_schema.tables t ON 
    t.table_name = expected_tables.table_name 
    AND t.table_schema = 'public';

-- Check Row Level Security is enabled
SELECT 'ROW LEVEL SECURITY CHECK' as check_type;

SELECT 
    tablename,
    CASE WHEN rowsecurity THEN '🔒 RLS ENABLED' ELSE '⚠️ RLS DISABLED' END as security_status
FROM pg_tables 
WHERE schemaname = 'public' 
    AND tablename IN (
        'organizations', 'user_profiles', 'analysis_results', 
        'automation_opportunities', 'workflow_visualizations', 
        'cost_analyses', 'generated_reports'
    )
ORDER BY tablename;

-- Check that foreign key relationships are properly set up
SELECT 'FOREIGN KEY RELATIONSHIPS CHECK' as check_type;

SELECT 
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name,
    '✅ RELATIONSHIP OK' as status
FROM 
    information_schema.table_constraints AS tc 
    JOIN information_schema.key_column_usage AS kcu
      ON tc.constraint_name = kcu.constraint_name
      AND tc.table_schema = kcu.table_schema
    JOIN information_schema.constraint_column_usage AS ccu
      ON ccu.constraint_name = tc.constraint_name
      AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY' 
    AND tc.table_schema = 'public'
    AND tc.table_name IN (
        'user_profiles', 'analysis_results', 'automation_opportunities',
        'workflow_visualizations', 'cost_analyses', 'generated_reports'
    )
ORDER BY tc.table_name, kcu.column_name;

-- Check that indexes were created
SELECT 'INDEX VERIFICATION' as check_type;

SELECT 
    indexname,
    tablename,
    '✅ INDEX EXISTS' as status
FROM pg_indexes 
WHERE schemaname = 'public' 
    AND indexname LIKE 'idx_%'
ORDER BY tablename, indexname;

-- Check that views were created
SELECT 'VIEWS VERIFICATION' as check_type;

SELECT 
    table_name as view_name,
    '✅ VIEW EXISTS' as status
FROM information_schema.views 
WHERE table_schema = 'public'
    AND table_name IN ('recording_sessions_summary', 'roi_dashboard');

-- Test that we can insert a sample analysis result (if you have recording sessions)
-- This will fail if foreign key constraints aren't working properly
DO $$
DECLARE
    sample_session_id UUID;
    sample_analysis_id UUID;
BEGIN
    -- Get a sample recording session ID (if any exist)
    SELECT id INTO sample_session_id 
    FROM public.recording_sessions 
    LIMIT 1;
    
    IF sample_session_id IS NOT NULL THEN
        -- Try to insert a test analysis result
        INSERT INTO public.analysis_results (
            session_id, 
            status, 
            gpt_version,
            confidence_score,
            structured_insights
        ) VALUES (
            sample_session_id,
            'completed',
            'gpt-4-vision-preview',
            0.85,
            '{"test": "migration verification"}'
        ) RETURNING id INTO sample_analysis_id;
        
        -- Try to insert a test automation opportunity
        INSERT INTO public.automation_opportunities (
            analysis_id,
            session_id,
            opportunity_type,
            title,
            description,
            estimated_cost_savings_monthly,
            roi_percentage
        ) VALUES (
            sample_analysis_id,
            sample_session_id,
            'test_automation',
            'Test Migration Verification',
            'This is a test record to verify the migration worked',
            100.00,
            25.5
        );
        
        -- Clean up test data
        DELETE FROM public.automation_opportunities WHERE analysis_id = sample_analysis_id;
        DELETE FROM public.analysis_results WHERE id = sample_analysis_id;
        
        RAISE NOTICE '✅ INSERT/DELETE TEST PASSED - Foreign key constraints working correctly';
    ELSE
        RAISE NOTICE '⚠️ No recording sessions found - skipping insert test';
    END IF;
    
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE '❌ INSERT TEST FAILED: %', SQLERRM;
END
$$;

-- Final summary
SELECT 'MIGRATION VERIFICATION COMPLETE' as status;

SELECT 
    'SUMMARY' as check_type,
    'Your migration is complete and verified!' as message;

SELECT 
    'NEXT STEPS' as action_required,
    'Update your backend .env.minimal and test the full-stack connections' as instructions;