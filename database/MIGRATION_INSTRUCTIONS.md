# Database Migration Instructions

## Step 1: Run the Migration in Supabase

1. **Open your Supabase Dashboard** at https://app.supabase.com/project/klhmxzuvfzodmcotsezy

2. **Go to SQL Editor** (left sidebar)

3. **Copy and paste** the entire contents of `supabase_migration_001_auth_foundation.sql`

4. **Click "RUN"** to execute the migration

5. **Verify tables were created** by going to Table Editor and confirming you see:
   - organizations
   - user_profiles  
   - recording_sessions
   - video_chunks
   - analysis_results
   - automation_opportunities

## Step 2: Verify RLS is Enabled

In the Table Editor, each table should show a "RLS Enabled" badge. If not, the migration didn't complete successfully.

## Step 3: Test Organization Creation Function

Run this test query in SQL Editor:

```sql
-- This should work after auth is implemented
SELECT create_organization_and_owner(
  'test-user-id'::UUID, 
  'Test Organization',
  'John',
  'Doe'
);
```

## What This Migration Does

✅ **Creates multi-tenant database structure**
✅ **Enables Row Level Security on all tables** 
✅ **Sets up organization-based isolation**
✅ **Includes helper functions for organization management**
✅ **Adds performance indexes**
✅ **Creates proper foreign key relationships**

## Next Steps

After running this migration, the backend will be updated to use these native Supabase tables instead of SQLAlchemy.