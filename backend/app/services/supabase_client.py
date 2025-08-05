"""
Supabase client for storage and database operations
Handles video upload, storage management, and authentication
"""

import asyncio
from typing import Optional, Dict, Any, List, BinaryIO
from uuid import UUID
import logging
from supabase import create_client, Client
from app.core.config import settings

logger = logging.getLogger(__name__)

class SupabaseClient:
    """Supabase client wrapper for NewSystem.AI operations"""
    
    def __init__(self):
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
            raise ValueError("Supabase credentials not configured")
        
        self.client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY
        )
    
    # Storage Operations
    async def upload_video_chunk(
        self,
        session_id: UUID,
        chunk_index: int,
        file_content: bytes,
        content_type: str = "video/webm"
    ) -> Dict[str, Any]:
        """
        Upload a video chunk to Supabase Storage
        
        Args:
            session_id: Recording session ID
            chunk_index: Index of the chunk
            file_content: Binary content of the chunk
            content_type: MIME type of the content
            
        Returns:
            Dict with upload result information
        """
        try:
            # Construct file path: recordings/{session_id}/chunk_{index}.webm
            file_path = f"recordings/{session_id}/chunk_{chunk_index:04d}.webm"
            
            # Upload to Supabase Storage
            result = self.client.storage.from_(settings.SUPABASE_STORAGE_BUCKET).upload(
                path=file_path,
                file=file_content,
                file_options={
                    "content-type": content_type,
                    "cache-control": "3600"
                }
            )
            
            if result.get("error"):
                logger.error(f"Chunk upload failed: {result['error']}")
                return {
                    "success": False,
                    "error": result["error"],
                    "file_path": None
                }
            
            logger.info(f"Chunk uploaded successfully: {file_path}")
            return {
                "success": True,
                "file_path": file_path,
                "public_url": self.get_public_url(file_path)
            }
            
        except Exception as e:
            logger.error(f"Error uploading chunk: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_path": None
            }
    
    def get_public_url(self, file_path: str) -> str:
        """Get public URL for a stored file"""
        try:
            result = self.client.storage.from_(settings.SUPABASE_STORAGE_BUCKET).get_public_url(file_path)
            return result
        except Exception as e:
            logger.error(f"Error getting public URL: {e}")
            return ""
    
    def get_signed_upload_url(self, file_path: str, expires_in: int = 3600) -> Optional[str]:
        """
        Get a signed URL for direct client upload
        
        Args:
            file_path: Path where file will be stored
            expires_in: URL expiration time in seconds
            
        Returns:
            Signed upload URL or None if failed
        """
        try:
            result = self.client.storage.from_(settings.SUPABASE_STORAGE_BUCKET).create_signed_upload_url(
                path=file_path,
                expires_in=expires_in
            )
            
            if result.get("error"):
                logger.error(f"Failed to create signed URL: {result['error']}")
                return None
                
            return result.get("signedURL")
            
        except Exception as e:
            logger.error(f"Error creating signed upload URL: {e}")
            return None
    
    async def delete_recording_files(self, session_id: UUID) -> bool:
        """
        Delete all files associated with a recording session
        
        Args:
            session_id: Recording session ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # List all files for this session
            folder_path = f"recordings/{session_id}/"
            
            # List files in the folder
            files_result = self.client.storage.from_(settings.SUPABASE_STORAGE_BUCKET).list(
                path=folder_path
            )
            
            if files_result and not files_result.get("error"):
                # Delete all files
                file_paths = [f"{folder_path}{file['name']}" for file in files_result]
                if file_paths:
                    delete_result = self.client.storage.from_(settings.SUPABASE_STORAGE_BUCKET).remove(
                        paths=file_paths
                    )
                    
                    if delete_result.get("error"):
                        logger.error(f"Error deleting files: {delete_result['error']}")
                        return False
            
            logger.info(f"Successfully deleted files for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting recording files: {e}")
            return False
    
    # Database Operations (using direct SQL for complex queries)
    async def execute_sql(self, query: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute raw SQL query
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Query result
        """
        try:
            result = self.client.rpc("execute_sql", {
                "query": query,
                "params": params or {}
            })
            
            return {
                "success": True,
                "data": result.data,
                "error": result.error
            }
            
        except Exception as e:
            logger.error(f"SQL execution error: {e}")
            return {
                "success": False,
                "data": None,
                "error": str(e)
            }
    
    # Authentication helpers
    def get_user_from_jwt(self, jwt_token: str) -> Optional[Dict[str, Any]]:
        """
        Get user information from JWT token
        
        Args:
            jwt_token: JWT token from client
            
        Returns:
            User information or None
        """
        try:
            # Set the session with the JWT token
            self.client.auth.set_session(jwt_token, jwt_token)  # Both access and refresh token
            user = self.client.auth.get_user()
            
            if user and user.user:
                return {
                    "id": user.user.id,
                    "email": user.user.email,
                    "metadata": user.user.user_metadata
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user from JWT: {e}")
            return None
    
    # Health check
    def test_connection(self) -> bool:
        """Test connection to Supabase"""
        try:
            # Try to access a simple endpoint
            result = self.client.table("leads").select("count", count="exact").limit(0).execute()
            return result is not None
        except Exception as e:
            logger.error(f"Supabase connection test failed: {e}")
            return False

# Global Supabase client instance
_supabase_client: Optional[SupabaseClient] = None

def get_supabase_client() -> SupabaseClient:
    """Get global Supabase client instance"""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = SupabaseClient()
    return _supabase_client

# Async context manager for database operations
class SupabaseSession:
    """Context manager for Supabase operations"""
    
    def __init__(self):
        self.client = get_supabase_client()
    
    async def __aenter__(self):
        return self.client
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Cleanup if needed
        pass