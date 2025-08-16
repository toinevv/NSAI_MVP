#!/usr/bin/env python3
"""
Quick test script to verify the Native Supabase conversion worked
Tests import statements and basic connectivity
"""

import sys
import os

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

def test_imports():
    """Test that all converted modules import correctly"""
    print("🧪 TESTING IMPORTS...")
    
    try:
        # Test core imports
        print("  ✓ Testing Supabase client...")
        from app.services.supabase_client import get_supabase_client
        
        print("  ✓ Testing config...")
        from app.core.config import settings
        
        print("  ✓ Testing auth API...")
        from app.api.v1.auth import router as auth_router, get_current_user_from_token
        
        print("  ✓ Testing recordings API...")
        from app.api.v1.recordings import router as recordings_router
        
        print("  ✓ Testing analysis API...")
        from app.api.v1.analysis import router as analysis_router
        
        print("✅ ALL IMPORTS SUCCESSFUL")
        return True
        
    except ImportError as e:
        print(f"❌ IMPORT FAILED: {e}")
        return False
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        return False

def test_supabase_connection():
    """Test Supabase client initialization"""
    print("\n🔌 TESTING SUPABASE CONNECTION...")
    
    try:
        from app.services.supabase_client import get_supabase_client
        
        supabase = get_supabase_client()
        if supabase and supabase.client:
            print("✅ SUPABASE CLIENT INITIALIZED SUCCESSFULLY")
            return True
        else:
            print("❌ SUPABASE CLIENT FAILED TO INITIALIZE")
            return False
            
    except Exception as e:
        print(f"❌ SUPABASE CONNECTION ERROR: {e}")
        return False

def test_removed_dependencies():
    """Verify that SQLAlchemy dependencies were removed"""
    print("\n🗑️  TESTING REMOVED DEPENDENCIES...")
    
    # These should NOT import anymore
    removed_modules = [
        'app.core.database',
        'app.models.database'
    ]
    
    for module in removed_modules:
        try:
            __import__(module)
            print(f"❌ FAILED: {module} still exists (should be deleted)")
            return False
        except ImportError:
            print(f"✅ CONFIRMED: {module} properly removed")
    
    return True

def test_fastapi_app():
    """Test that FastAPI app can be created with new routers"""
    print("\n🚀 TESTING FASTAPI APP CREATION...")
    
    try:
        from fastapi import FastAPI
        from app.api.v1.auth import router as auth_router
        from app.api.v1.recordings import router as recordings_router
        from app.api.v1.analysis import router as analysis_router
        
        app = FastAPI()
        app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
        app.include_router(recordings_router, prefix="/api/v1/recordings", tags=["recordings"])
        app.include_router(analysis_router, prefix="/api/v1/analysis", tags=["analysis"])
        
        print("✅ FASTAPI APP CREATED SUCCESSFULLY WITH ALL ROUTERS")
        return True
        
    except Exception as e:
        print(f"❌ FASTAPI APP CREATION FAILED: {e}")
        return False

def main():
    """Run all tests"""
    print("🎯 NATIVE SUPABASE CONVERSION TEST")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_supabase_connection, 
        test_removed_dependencies,
        test_fastapi_app
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 TEST RESULTS: {passed}/{total} PASSED")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - CONVERSION SUCCESSFUL!")
        print("\n✅ NEXT STEPS:")
        print("1. Run the database migration in Supabase SQL Editor")
        print("2. Start the backend with: cd backend && python -m app.main")
        print("3. Test user registration and recording creation")
        return True
    else:
        print("❌ SOME TESTS FAILED - CHECK ERRORS ABOVE")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)