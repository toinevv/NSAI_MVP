/**
 * Recording API Service
 * Integrates with NewSystem.AI backend for recording management
 * Handles session creation, chunk upload, and completion with enhanced retry logic
 * Uses centralized API client with authentication
 */

import { UploadQueue } from './uploadQueue'
import type { UploadProgress, UploadEvent } from './uploadQueue'
import { apiClient, get, post, put, del } from '../../../lib/api-client'
import { auth } from '../../../lib/supabase'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const API_VERSION = import.meta.env.VITE_API_VERSION || 'v1'

export interface PrivacySettings {
  blur_passwords: boolean
  exclude_personal_info: boolean
  custom_exclusions: string[]
}

export interface RecordingStartRequest {
  title: string
  description?: string
  workflow_type?: string
  privacy_settings?: PrivacySettings
  metadata?: Record<string, any>
}

export interface RecordingStartResponse {
  id: string
  status: string
  message: string
  upload_url?: string
  chunk_settings: {
    chunk_size_seconds: number
    max_file_size_mb: number
    allowed_formats: string[]
    recording_fps: number
  }
}

export interface ChunkUploadResponse {
  chunk_id: string
  status: string
  message: string
  upload_url?: string
  next_chunk_index: number
}

export interface SignedUrlResponse {
  signed_url: string
  file_path: string
  expires_at: number
  chunk_index: number
  content_type: string
  upload_method: string
  instructions: {
    method: string
    headers: Record<string, string>
    body: string
  }
}

export interface ChunkVerificationResponse {
  verified: boolean
  chunk_id?: string
  file_path?: string
  file_size?: number
  public_url?: string
  message: string
  error?: string
}

export interface RecordingCompleteRequest {
  duration_seconds: number
  total_file_size_bytes: number
  chunk_count: number
  metadata?: Record<string, any>
}

export interface RecordingCompleteResponse {
  id: string
  status: string
  message: string
  analysis_queued: boolean
  estimated_processing_time_minutes: number
}

export interface RecordingResponse {
  id: string
  user_id: string
  title: string
  description?: string
  status: string
  duration_seconds: number
  file_size_bytes: number
  workflow_type?: string
  privacy_settings: Record<string, any>
  recording_metadata: Record<string, any>
  analysis_cost: number
  created_at: string
  completed_at?: string
  updated_at: string
}

export class RecordingAPIError extends Error {
  public status?: number
  public details?: any
  
  constructor(
    message: string,
    status?: number,
    details?: any
  ) {
    super(message)
    this.name = 'RecordingAPIError'
    this.status = status
    this.details = details
  }
}

class RecordingAPI {
  private baseUrl: string
  private uploadQueue: UploadQueue
  
  constructor() {
    this.baseUrl = `${API_BASE_URL}/api/${API_VERSION}/recordings`
    this.uploadQueue = new UploadQueue({
      maxRetries: 3,
      concurrency: 3,
      retryDelayMs: 1000,
      maxRetryDelayMs: 8000,
      timeoutMs: 30000,
    })
    
    // Set the proxied upload function for the queue (default)
    this.uploadQueue.setUploadFunction((sessionId, chunk, chunkIndex) => 
      this.uploadChunkDirect(sessionId, chunk, chunkIndex)
    )
  }

  /**
   * Switch upload queue to use direct Supabase uploads
   */
  enableDirectUploads(): void {
    this.uploadQueue.setUploadFunction(async (sessionId, chunk, chunkIndex) => {
      const verification = await this.uploadChunkWithSignedUrl(sessionId, chunk, chunkIndex)
      if (!verification.verified) {
        throw new Error(`Direct upload verification failed: ${verification.error}`)
      }
      return verification
    })
  }

  /**
   * Switch upload queue to use proxied uploads through backend
   */
  enableProxiedUploads(): void {
    this.uploadQueue.setUploadFunction((sessionId, chunk, chunkIndex) => 
      this.uploadChunkDirect(sessionId, chunk, chunkIndex)
    )
  }

  /**
   * Get upload queue for progress monitoring
   */
  getUploadQueue(): UploadQueue {
    return this.uploadQueue
  }

  /**
   * Add event listener for upload events
   */
  onUploadEvent(callback: (event: UploadEvent) => void): void {
    this.uploadQueue.addEventListener(callback)
  }

  /**
   * Remove upload event listener
   */
  offUploadEvent(callback: (event: UploadEvent) => void): void {
    this.uploadQueue.removeEventListener(callback)
  }

  /**
   * Get current upload progress
   */
  getUploadProgress(): UploadProgress {
    return this.uploadQueue.getProgress()
  }
  
  private async fetchWithErrorHandling<T>(
    url: string,
    options: RequestInit = {}
  ): Promise<T> {
    try {
      // Use centralized API client with authentication
      const endpoint = url.replace(`${API_BASE_URL}/api/${API_VERSION}/`, '')
      
      if (options.method === 'POST') {
        return await post<T>(endpoint, options.body ? JSON.parse(options.body as string) : undefined)
      } else if (options.method === 'PUT') {
        return await put<T>(endpoint, options.body ? JSON.parse(options.body as string) : undefined)
      } else if (options.method === 'DELETE') {
        return await del<T>(endpoint)
      } else {
        // Default to GET
        return await get<T>(endpoint)
      }
    } catch (error: any) {
      // Convert API errors to RecordingAPIError for backward compatibility
      throw new RecordingAPIError(
        error.message || 'API request failed',
        error.status || 0,
        error.details || error
      )
    }
  }
  
  /**
   * Start a new recording session
   */
  async startRecording(request: RecordingStartRequest): Promise<RecordingStartResponse> {
    return this.fetchWithErrorHandling<RecordingStartResponse>(
      `${this.baseUrl}/start`,
      {
        method: 'POST',
        body: JSON.stringify(request),
      }
    )
  }
  
  /**
   * Upload a video chunk during recording (legacy single chunk method)
   */
  async uploadChunk(
    recordingId: string,
    chunkFile: Blob,
    chunkIndex: number
  ): Promise<ChunkUploadResponse> {
    return this.uploadChunkDirect(recordingId, chunkFile, chunkIndex)
  }

  /**
   * Direct chunk upload without queue (for immediate uploads)
   * Uses authenticated fetch with JWT token for FormData uploads
   */
  private async uploadChunkDirect(
    recordingId: string,
    chunkFile: Blob,
    chunkIndex: number
  ): Promise<ChunkUploadResponse> {
    const formData = new FormData()
    formData.append('chunk_file', chunkFile, `chunk_${chunkIndex}.webm`)
    // Note: chunk_index is now sent as query parameter instead of FormData
    
    // Get authentication token from Supabase
    const accessToken = await auth.getAccessToken()
    
    // Build headers with authentication (don't set Content-Type for FormData)
    const headers: Record<string, string> = {}
    if (accessToken) {
      headers['Authorization'] = `Bearer ${accessToken}`
    }
    
    // Create AbortController for timeout handling
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 300000) // 5 minutes timeout for large uploads
    
    try {
      const response = await fetch(
        `${this.baseUrl}/${recordingId}/chunks?chunk_index=${chunkIndex}`,
        {
          method: 'POST',
          headers,
          body: formData, // Don't set Content-Type header for FormData
          signal: controller.signal,
        }
      )
      
      clearTimeout(timeoutId)
      
      if (!response.ok) {
        let errorMessage = `Chunk upload failed: HTTP ${response.status}`
        try {
          const errorData = await response.json()
          errorMessage = errorData.detail || errorMessage
        } catch {
          // Response wasn't JSON
        }
        throw new RecordingAPIError(errorMessage, response.status)
      }
      
      return await response.json()
      
    } catch (error) {
      if (error instanceof RecordingAPIError) {
        throw error
      }
      throw new RecordingAPIError(
        `Chunk upload failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
        0,
        error
      )
    }
  }

  /**
   * Add chunk to upload queue for enhanced retry handling
   */
  queueChunkUpload(recordingId: string, chunkFile: Blob, chunkIndex: number): string {
    return this.uploadQueue.addChunk(recordingId, chunkIndex, chunkFile)
  }

  /**
   * Start batch upload of all queued chunks
   */
  startBatchUpload(): void {
    // The upload queue will automatically start processing when chunks are added
    // This method is here for explicit control if needed
  }

  /**
   * Cancel all pending uploads
   */
  cancelUploads(): void {
    this.uploadQueue.cancelAll()
  }

  /**
   * Retry failed uploads
   */
  retryFailedUploads(): void {
    this.uploadQueue.retryFailed()
  }

  /**
   * Get signed URL for direct chunk upload to Supabase Storage
   */
  async getChunkSignedUrl(
    recordingId: string,
    chunkIndex: number,
    expiresIn: number = 3600
  ): Promise<SignedUrlResponse> {
    const params = new URLSearchParams({
      chunk_index: chunkIndex.toString(),
      expires_in: expiresIn.toString()
    })

    return this.fetchWithErrorHandling<SignedUrlResponse>(
      `${this.baseUrl}/${recordingId}/chunks/signed-url?${params.toString()}`,
      {
        method: 'POST'
      }
    )
  }

  /**
   * Upload chunk directly to Supabase Storage using signed URL
   */
  async uploadChunkToStorage(
    signedUrlInfo: SignedUrlResponse,
    chunkFile: Blob
  ): Promise<void> {
    try {
      const response = await fetch(signedUrlInfo.signed_url, {
        method: 'PUT',
        headers: {
          'Content-Type': signedUrlInfo.content_type
        },
        body: chunkFile
      })

      if (!response.ok) {
        let errorMessage = `Direct upload failed: HTTP ${response.status}`
        try {
          const errorText = await response.text()
          if (errorText) {
            errorMessage += ` - ${errorText}`
          }
        } catch {
          // Response wasn't readable
        }
        throw new RecordingAPIError(errorMessage, response.status)
      }

      // Supabase returns 200 OK for successful uploads
      console.log(`Direct upload successful for chunk ${signedUrlInfo.chunk_index}`)
      
    } catch (error) {
      if (error instanceof RecordingAPIError) {
        throw error
      }
      throw new RecordingAPIError(
        `Direct upload failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
        0,
        error
      )
    }
  }

  /**
   * Verify chunk upload in Supabase Storage
   */
  async verifyChunkUpload(
    recordingId: string,
    chunkIndex: number
  ): Promise<ChunkVerificationResponse> {
    const params = new URLSearchParams({
      chunk_index: chunkIndex.toString()
    })

    return this.fetchWithErrorHandling<ChunkVerificationResponse>(
      `${this.baseUrl}/${recordingId}/chunks/verify?${params.toString()}`,
      {
        method: 'POST'
      }
    )
  }

  /**
   * Complete upload process for direct uploads (get signed URL, upload, verify)
   */
  async uploadChunkWithSignedUrl(
    recordingId: string,
    chunkFile: Blob,
    chunkIndex: number
  ): Promise<ChunkVerificationResponse> {
    try {
      // Step 1: Get signed URL
      const signedUrlInfo = await this.getChunkSignedUrl(recordingId, chunkIndex)
      
      // Step 2: Upload directly to Supabase
      await this.uploadChunkToStorage(signedUrlInfo, chunkFile)
      
      // Step 3: Verify upload and update database
      const verification = await this.verifyChunkUpload(recordingId, chunkIndex)
      
      if (!verification.verified) {
        throw new RecordingAPIError(
          `Upload verification failed: ${verification.error || 'Unknown error'}`,
          500
        )
      }
      
      return verification
      
    } catch (error) {
      if (error instanceof RecordingAPIError) {
        throw error
      }
      throw new RecordingAPIError(
        `Signed URL upload failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
        0,
        error
      )
    }
  }
  
  /**
   * Complete a recording session
   */
  async completeRecording(
    recordingId: string,
    request: RecordingCompleteRequest
  ): Promise<RecordingCompleteResponse> {
    return this.fetchWithErrorHandling<RecordingCompleteResponse>(
      `${this.baseUrl}/${recordingId}/complete`,
      {
        method: 'POST',
        body: JSON.stringify(request),
      }
    )
  }
  
  /**
   * Get recording details
   */
  async getRecording(recordingId: string, includeChunks = false): Promise<RecordingResponse> {
    const params = new URLSearchParams()
    if (includeChunks) {
      params.append('include_chunks', 'true')
    }
    
    const url = `${this.baseUrl}/${recordingId}${params.toString() ? `?${params.toString()}` : ''}`
    
    return this.fetchWithErrorHandling<RecordingResponse>(url)
  }
  
  /**
   * List user's recordings
   */
  async listRecordings(
    page = 1,
    pageSize = 10,
    status?: string
  ): Promise<{
    recordings: RecordingResponse[]
    total: number
    page: number
    page_size: number
    has_more: boolean
  }> {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    })
    
    if (status) {
      params.append('status', status)
    }
    
    return this.fetchWithErrorHandling(
      `${this.baseUrl}/?${params.toString()}`
    )
  }
  
  /**
   * Delete a recording
   */
  async deleteRecording(recordingId: string): Promise<{ message: string }> {
    return this.fetchWithErrorHandling(
      `${this.baseUrl}/${recordingId}`,
      {
        method: 'DELETE',
      }
    )
  }
  
  /**
   * Update privacy settings for a recording
   */
  async updatePrivacySettings(
    recordingId: string,
    privacySettings: Partial<PrivacySettings>
  ): Promise<{ message: string }> {
    return this.fetchWithErrorHandling(
      `${this.baseUrl}/${recordingId}/privacy`,
      {
        method: 'PUT',
        body: JSON.stringify(privacySettings),
      }
    )
  }
  
  /**
   * Check API health
   */
  async checkHealth(): Promise<{
    status: string
    service: string
    version: string
    environment: string
    components: Record<string, string>
    configuration: Record<string, any>
  }> {
    return this.fetchWithErrorHandling(
      `${API_BASE_URL}/health`
    )
  }
}

// Export singleton instance
export const recordingAPI = new RecordingAPI()

// Export utilities for error handling
export const isRecordingAPIError = (error: any): error is RecordingAPIError => {
  return error instanceof RecordingAPIError
}

export const getErrorMessage = (error: any): string => {
  if (isRecordingAPIError(error)) {
    return error.message
  }
  return error instanceof Error ? error.message : 'An unknown error occurred'
}