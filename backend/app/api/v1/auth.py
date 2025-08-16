"""
Authentication endpoints for NewSystem.AI
Handles user registration, login, and token management via Supabase
Replaces mock authentication with full multi-tenant Supabase Auth
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
import logging
from uuid import UUID

from app.services.supabase_client import get_supabase_client
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# ============================================
# REQUEST/RESPONSE MODELS
# ============================================

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    organization_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    success: bool
    message: str
    user_id: Optional[str] = None
    email: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    organization: Optional[Dict[str, Any]] = None
    user_profile: Optional[Dict[str, Any]] = None

class UserResponse(BaseModel):
    id: str
    email: str
    organization_id: Optional[str] = None
    organization: Optional[Dict[str, Any]] = None
    profile: Optional[Dict[str, Any]] = None
    role: str = "operator"

# ============================================
# AUTHENTICATION UTILITIES
# ============================================

async def get_current_user_from_token(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """
    Extract and validate current user from JWT token
    Used as dependency for protected endpoints
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="No authorization header provided")
    
    try:
        # Extract token from "Bearer <token>" format
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header format")
        
        token = authorization.split(" ")[1]
        
        # Get Supabase client and verify token
        supabase = get_supabase_client()
        
        # Set the session with the token to validate it
        user_response = supabase.client.auth.get_user(token)
        
        if not user_response.user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        user = user_response.user
        
        # Get user profile with organization context
        profile_response = supabase.client.table('user_profiles').select(
            '*, organizations(*)'  # Join with organization data
        ).eq('id', user.id).single().execute()
        
        if not profile_response.data:
            # User exists in auth.users but no profile - create basic profile
            logger.warning(f"User {user.id} has no profile, creating basic profile")
            
            # This shouldn't happen in normal flow, but handle gracefully
            return {
                "id": user.id,
                "email": user.email,
                "organization_id": None,
                "organization": None,
                "profile": None,
                "role": "operator"
            }
        
        profile = profile_response.data
        
        return {
            "id": user.id,
            "email": user.email,
            "organization_id": profile.get('organization_id'),
            "organization": profile.get('organizations'),
            "profile": {
                "role": profile.get('role', 'operator'),
                "first_name": profile.get('first_name'),
                "last_name": profile.get('last_name'),
                "job_title": profile.get('job_title'),
                "settings": profile.get('settings', {})
            },
            "role": profile.get('role', 'operator')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating user token: {e}")
        raise HTTPException(status_code=401, detail="Token validation failed")

# ============================================
# AUTHENTICATION ENDPOINTS
# ============================================

@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    """
    Register a new user and create their organization
    This implements the auth-first approach with organization creation
    """
    try:
        logger.info(f"Registration attempt for email: {request.email}")
        
        supabase = get_supabase_client()
        
        # Step 1: Create user in auth.users
        auth_response = supabase.client.auth.sign_up({
            "email": request.email,
            "password": request.password
        })
        
        if not auth_response.user:
            error_msg = "Registration failed"
            if hasattr(auth_response, 'error') and auth_response.error:
                error_msg = auth_response.error.message
            raise HTTPException(status_code=400, detail=error_msg)
        
        user = auth_response.user
        logger.info(f"User created in auth.users: {user.id}")
        
        # Step 2: Create organization and user profile using helper function
        org_creation_response = supabase.client.rpc(
            'create_organization_and_owner',
            {
                'user_id': user.id,
                'org_name': request.organization_name,
                'owner_first_name': request.first_name,
                'owner_last_name': request.last_name
            }
        ).execute()
        
        if org_creation_response.data is None:
            logger.error(f"Failed to create organization: {org_creation_response}")
            raise HTTPException(status_code=500, detail="Failed to create organization")
        
        organization_id = org_creation_response.data
        logger.info(f"Organization created: {organization_id}")
        
        # Step 3: Get the complete user data with organization
        profile_response = supabase.client.table('user_profiles').select(
            '*, organizations(*)'
        ).eq('id', user.id).single().execute()
        
        if not profile_response.data:
            raise HTTPException(status_code=500, detail="Failed to retrieve user profile")
        
        profile = profile_response.data
        
        logger.info(f"Registration successful for {request.email}")
        
        return AuthResponse(
            success=True,
            message="Registration successful",
            user_id=str(user.id),
            email=user.email,
            access_token=auth_response.session.access_token if auth_response.session else None,
            refresh_token=auth_response.session.refresh_token if auth_response.session else None,
            organization=profile.get('organizations'),
            user_profile={
                "role": profile.get('role'),
                "first_name": profile.get('first_name'),
                "last_name": profile.get('last_name')
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """
    Authenticate user and return tokens with organization context
    """
    try:
        logger.info(f"Login attempt for email: {request.email}")
        
        supabase = get_supabase_client()
        
        # Authenticate with Supabase
        auth_response = supabase.client.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        
        if not auth_response.user or not auth_response.session:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        user = auth_response.user
        session = auth_response.session
        
        # Get user profile with organization
        profile_response = supabase.client.table('user_profiles').select(
            '*, organizations(*)'
        ).eq('id', user.id).single().execute()
        
        profile_data = None
        organization_data = None
        
        if profile_response.data:
            profile_data = {
                "role": profile_response.data.get('role', 'operator'),
                "first_name": profile_response.data.get('first_name'),
                "last_name": profile_response.data.get('last_name'),
                "job_title": profile_response.data.get('job_title')
            }
            organization_data = profile_response.data.get('organizations')
        
        logger.info(f"Login successful for {request.email}")
        
        return AuthResponse(
            success=True,
            message="Login successful",
            user_id=str(user.id),
            email=user.email,
            access_token=session.access_token,
            refresh_token=session.refresh_token,
            organization=organization_data,
            user_profile=profile_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(refresh_token: str):
    """
    Refresh access token using refresh token
    """
    try:
        supabase = get_supabase_client()
        
        # Refresh the session
        auth_response = supabase.client.auth.refresh_session(refresh_token)
        
        if not auth_response.session:
            raise HTTPException(status_code=401, detail="Failed to refresh token")
        
        session = auth_response.session
        
        return AuthResponse(
            success=True,
            message="Token refreshed successfully",
            access_token=session.access_token,
            refresh_token=session.refresh_token
        )
        
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(status_code=500, detail="Token refresh failed")

@router.post("/logout")
async def logout(current_user: Dict[str, Any] = Depends(get_current_user_from_token)):
    """
    Logout user (invalidate session)
    """
    try:
        supabase = get_supabase_client()
        
        # Sign out the user
        supabase.client.auth.sign_out()
        
        return {"success": True, "message": "Logout successful"}
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(status_code=500, detail="Logout failed")

@router.get("/me", response_model=UserResponse)
async def get_current_user(current_user: Dict[str, Any] = Depends(get_current_user_from_token)):
    """
    Get current user information with organization context
    This is used by other endpoints to get authenticated user data
    """
    try:
        return UserResponse(
            id=current_user["id"],
            email=current_user["email"],
            organization_id=current_user.get("organization_id"),
            organization=current_user.get("organization"),
            profile=current_user.get("profile"),
            role=current_user.get("role", "operator")
        )
        
    except Exception as e:
        logger.error(f"Get current user error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user information")

# ============================================
# ORGANIZATION MANAGEMENT
# ============================================

@router.get("/organization")
async def get_organization_info(current_user: Dict[str, Any] = Depends(get_current_user_from_token)):
    """
    Get current user's organization information
    """
    try:
        if not current_user.get("organization_id"):
            raise HTTPException(status_code=404, detail="User is not associated with an organization")
        
        supabase = get_supabase_client()
        
        # Get organization with member count
        org_response = supabase.client.table('organizations').select(
            '*, user_profiles(count)'
        ).eq('id', current_user["organization_id"]).single().execute()
        
        if not org_response.data:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        org_data = org_response.data
        
        # Get member count
        members_response = supabase.client.table('user_profiles').select(
            'id, role, first_name, last_name, created_at'
        ).eq('organization_id', current_user["organization_id"]).execute()
        
        return {
            "organization": org_data,
            "member_count": len(members_response.data) if members_response.data else 0,
            "members": members_response.data if members_response.data else [],
            "current_user_role": current_user.get("role")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get organization error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get organization information")

# ============================================
# UTILITY FUNCTIONS FOR OTHER MODULES
# ============================================

# This function can be imported by other API modules
async def get_current_user_id() -> str:
    """
    Simplified function to get current user ID - used as dependency in other endpoints
    This replaces the mock version that returned a hardcoded UUID
    """
    # This is a simplified version for backward compatibility
    # In practice, other endpoints should use get_current_user_from_token directly
    async def _get_user_id(current_user: Dict[str, Any] = Depends(get_current_user_from_token)) -> str:
        return current_user["id"]
    
    return _get_user_id