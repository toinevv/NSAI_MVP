"""
Supabase client for storage and database operations
Handles video upload, storage management, and authentication
"""

import asyncio
from typing import Optional, Dict, Any, List, BinaryIO
from uuid import UUID
import logging
from datetime import datetime, timezone
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions
from app.core.config import settings

logger = logging.getLogger(__name__)

class SupabaseClient:
    """Supabase client wrapper for NewSystem.AI operations"""
    
    def __init__(self):
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
            raise ValueError("Supabase credentials not configured")
        
        # Create client with timeout configuration
        options = ClientOptions(
            schema='public',
            auto_refresh_token=True,
            persist_session=True,
            storage_client_timeout=300,  # 5 minute timeout for storage operations
            postgrest_client_timeout=300  # Also increase database operation timeout
        )
        
        self.client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY,
            options=options
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
            # Construct file path: recordings/{session_id}/chunks/chunk_{index}.webm
            file_path = f"recordings/{session_id}/chunks/chunk_{chunk_index:04d}.webm"
            
            # Log upload attempt
            file_size_mb = len(file_content) / (1024 * 1024)
            logger.info(f"Uploading chunk {chunk_index} for session {session_id}: {file_size_mb:.2f} MB")
            
            # Upload to Supabase Storage with upsert mode to handle existing files
            result = self.client.storage.from_(settings.SUPABASE_STORAGE_BUCKET).upload(
                path=file_path,
                file=file_content,
                file_options={
                    "content-type": content_type,
                    "cache-control": "3600",
                    "upsert": "true"
                }
            )
            
            # Check if upload failed - Supabase Python client returns Response object
            if hasattr(result, 'status_code') and result.status_code >= 400:
                error_msg = f"Upload failed with status {result.status_code}"
                is_duplicate_error = False
                
                if hasattr(result, 'json'):
                    try:
                        error_data = result.json()
                        if isinstance(error_data, dict):
                            # Handle both nested and flat error structures
                            if 'error' in error_data:
                                if isinstance(error_data['error'], dict):
                                    error_msg = error_data['error'].get('message', error_msg)
                                    error_code = error_data['error'].get('error', '')
                                else:
                                    error_code = error_data.get('error', '')
                                    error_msg = error_data.get('message', error_msg)
                            else:
                                error_code = error_data.get('statusCode', '')
                                error_msg = error_data.get('message', error_msg)
                            
                            # Check if this is a duplicate error - can happen even with upsert
                            duplicate_indicators = [
                                error_code == 'Duplicate',
                                'already exists' in error_msg.lower(),
                                'duplicate' in error_msg.lower(),
                                result.status_code == 409  # Conflict status
                            ]
                            is_duplicate_error = any(duplicate_indicators)
                    except Exception as json_error:
                        logger.warning(f"Could not parse error response: {json_error}")
                
                # Treat duplicate errors as success when using upsert mode
                if is_duplicate_error:
                    logger.info(f"Chunk already exists (handling as success with upsert): {file_path}")
                    return {
                        "success": True,
                        "file_path": file_path,
                        "public_url": self.get_public_url(file_path),
                        "note": "File already existed - upsert successful"
                    }
                
                logger.error(f"Chunk upload failed: {error_msg} (status: {result.status_code})")
                return {
                    "success": False,
                    "error": error_msg,
                    "file_path": None,
                    "status_code": result.status_code
                }
            
            logger.info(f"Chunk uploaded successfully: {file_path}")
            return {
                "success": True,
                "file_path": file_path,
                "public_url": self.get_public_url(file_path)
            }
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error uploading chunk: {error_msg}")
            
            # Check for timeout errors
            if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                file_size_mb = len(file_content) / (1024 * 1024) if 'file_content' in locals() else 0
                logger.warning(f"Upload timeout for chunk {chunk_index} ({file_size_mb:.2f} MB). Consider chunking into smaller pieces.")
                return {
                    "success": False,
                    "error": f"Upload timeout - file too large ({file_size_mb:.2f} MB). Try smaller chunks or check network.",
                    "file_path": None
                }
            
            return {
                "success": False,
                "error": error_msg,
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
    
    def get_signed_upload_url(self, file_path: str, expires_in: int = 3600) -> Optional[Dict[str, str]]:
        """
        Get a signed URL for direct client upload with enhanced metadata
        
        Args:
            file_path: Path where file will be stored
            expires_in: URL expiration time in seconds
            
        Returns:
            Dict with signed URL info or None if failed
        """
        try:
            result = self.client.storage.from_(settings.SUPABASE_STORAGE_BUCKET).create_signed_upload_url(
                path=file_path
            )
            
            # Handle Response object from Supabase Python client
            if hasattr(result, 'status_code') and result.status_code >= 400:
                error_msg = f"Failed to create signed URL: status {result.status_code}"
                if hasattr(result, 'json'):
                    try:
                        error_data = result.json()
                        error_msg = error_data.get('error', {}).get('message', error_msg)
                    except:
                        pass
                logger.error(error_msg)
                return None
            
            # Extract signed URL from response
            signed_url = None
            if hasattr(result, 'json'):
                try:
                    response_data = result.json()
                    signed_url = response_data.get("signedURL") or response_data.get("signed_url")
                except:
                    pass
            
            if not signed_url:
                logger.error("No signed URL returned from Supabase")
                return None
                
            return {
                "signed_url": signed_url,
                "file_path": file_path,
                "expires_in": expires_in,
                "expires_at": (datetime.now(timezone.utc).timestamp() + expires_in),
                "bucket": settings.SUPABASE_STORAGE_BUCKET
            }
            
        except Exception as e:
            logger.error(f"Error creating signed upload URL: {e}")
            return None

    def create_chunk_signed_url(self, session_id: UUID, chunk_index: int, expires_in: int = 3600) -> Optional[Dict[str, str]]:
        """
        Create a signed URL specifically for chunk upload with proper naming convention
        
        Args:
            session_id: Recording session ID
            chunk_index: Index of the chunk (0-based)
            expires_in: URL expiration time in seconds
            
        Returns:
            Dict with signed URL info and metadata
        """
        try:
            # Construct file path with proper organization
            file_path = f"recordings/{session_id}/chunks/chunk_{chunk_index:04d}.webm"
            
            signed_url_info = self.get_signed_upload_url(file_path, expires_in)
            if not signed_url_info:
                return None
                
            # Add chunk-specific metadata
            signed_url_info.update({
                "session_id": str(session_id),
                "chunk_index": chunk_index,
                "content_type": "video/webm",
                "file_extension": "webm"
            })
            
            logger.info(f"Created signed URL for chunk {chunk_index} of session {session_id}")
            return signed_url_info
            
        except Exception as e:
            logger.error(f"Error creating chunk signed URL: {e}")
            return None

    async def verify_chunk_upload(self, session_id: UUID, chunk_index: int) -> Dict[str, Any]:
        """
        Verify that a chunk was successfully uploaded to storage
        
        Args:
            session_id: Recording session ID
            chunk_index: Index of the chunk to verify
            
        Returns:
            Dict with verification results
        """
        try:
            file_path = f"recordings/{session_id}/chunks/chunk_{chunk_index:04d}.webm"
            
            # Check if file exists and get metadata
            result = self.client.storage.from_(settings.SUPABASE_STORAGE_BUCKET).list(
                path=f"recordings/{session_id}/chunks",
                search=f"chunk_{chunk_index:04d}.webm"
            )
            
            if result and len(result) > 0:
                file_info = result[0]
                return {
                    "exists": True,
                    "file_path": file_path,
                    "size": file_info.get("metadata", {}).get("size", 0),
                    "last_modified": file_info.get("updated_at"),
                    "public_url": self.get_public_url(file_path)
                }
            else:
                return {
                    "exists": False,
                    "file_path": file_path,
                    "error": "File not found in storage"
                }
                
        except Exception as e:
            logger.error(f"Error verifying chunk upload: {e}")
            return {
                "exists": False,
                "file_path": f"recordings/{session_id}/chunks/chunk_{chunk_index:04d}.webm",
                "error": str(e)
            }
    
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
            
            # Check if files_result is successful - handle Response object
            files_list = []
            if hasattr(files_result, 'status_code'):
                if files_result.status_code >= 400:
                    logger.error(f"Failed to list files: status {files_result.status_code}")
                    return False
                if hasattr(files_result, 'json'):
                    try:
                        files_list = files_result.json() or []
                    except:
                        files_list = []
            else:
                files_list = files_result or []
            
            if files_list:
                # Delete all files
                file_paths = [f"{folder_path}{file['name']}" for file in files_list if isinstance(file, dict) and 'name' in file]
                if file_paths:
                    delete_result = self.client.storage.from_(settings.SUPABASE_STORAGE_BUCKET).remove(
                        paths=file_paths
                    )
                    
                    # Check delete result - handle Response object
                    if hasattr(delete_result, 'status_code') and delete_result.status_code >= 400:
                        error_msg = f"Error deleting files: status {delete_result.status_code}"
                        if hasattr(delete_result, 'json'):
                            try:
                                error_data = delete_result.json()
                                error_msg = error_data.get('error', {}).get('message', error_msg)
                            except:
                                pass
                        logger.error(error_msg)
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