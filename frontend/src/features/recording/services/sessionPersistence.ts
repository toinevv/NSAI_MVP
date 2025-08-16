/**
 * Session Persistence Service
 * Handles localStorage-based recording session recovery and persistence
 * Enables recovery of incomplete recordings after page reloads or crashes
 */

export interface PersistedRecordingState {
  sessionId: string
  title: string
  status: 'recording' | 'paused' | 'stopping' | 'uploading'
  startTime: number
  duration: number
  chunkCount: number
  totalSize: number
  lastChunkIndex: number
  uploadProgress: {
    totalChunks: number
    completedChunks: number
    failedChunks: number
    uploadedBytes: number
    totalBytes: number
    percentage: number
  }
  settings: {
    useEnhancedUpload: boolean
    useDirectStorage: boolean
  }
  metadata: Record<string, any>
  persistedAt: number
}

export interface SessionRecoveryInfo {
  hasRecoverableSession: boolean
  sessionData?: PersistedRecordingState
  timeElapsed?: number
  shouldAutoRecover?: boolean
}

class SessionPersistenceService {
  private readonly STORAGE_KEY = 'nsai_recording_session'
  private readonly MAX_SESSION_AGE_MS = 24 * 60 * 60 * 1000 // 24 hours
  private readonly AUTO_RECOVERY_THRESHOLD_MS = 5 * 60 * 1000 // 5 minutes
  
  /**
   * Save recording session state to localStorage
   */
  saveSession(state: PersistedRecordingState): void {
    try {
      const sessionData = {
        ...state,
        persistedAt: Date.now()
      }
      
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(sessionData))
      // Only log session creation, not updates
      if (state.status === 'recording' && state.duration === 0) {
        console.log(`Session persisted: ${state.sessionId}`)
      }
      
    } catch (error) {
      console.error('Failed to persist recording session:', error)
      // Non-critical error - recording can continue without persistence
    }
  }

  /**
   * Update existing session with new state data
   */
  updateSession(updates: Partial<PersistedRecordingState>): void {
    try {
      const existingSession = this.getSession()
      if (!existingSession) {
        console.warn('Attempted to update non-existent session')
        return
      }

      const updatedSession = {
        ...existingSession,
        ...updates,
        persistedAt: Date.now()
      }

      this.saveSession(updatedSession)
      
    } catch (error) {
      console.error('Failed to update persisted session:', error)
    }
  }

  /**
   * Get current persisted session from localStorage
   */
  getSession(): PersistedRecordingState | null {
    try {
      const stored = localStorage.getItem(this.STORAGE_KEY)
      if (!stored) return null

      const sessionData: PersistedRecordingState = JSON.parse(stored)
      
      // Check if session is too old
      const sessionAge = Date.now() - sessionData.persistedAt
      if (sessionAge > this.MAX_SESSION_AGE_MS) {
        this.clearSession()
        return null
      }

      return sessionData
      
    } catch (error) {
      console.error('Failed to retrieve persisted session:', error)
      this.clearSession() // Clear corrupted data
      return null
    }
  }

  /**
   * Check for recoverable recording sessions
   */
  checkRecovery(): SessionRecoveryInfo {
    const sessionData = this.getSession()
    
    if (!sessionData) {
      return { hasRecoverableSession: false }
    }

    // Only recover sessions that were actively recording or uploading
    const recoverableStatuses = ['recording', 'paused', 'stopping', 'uploading']
    if (!recoverableStatuses.includes(sessionData.status)) {
      this.clearSession()
      return { hasRecoverableSession: false }
    }

    const timeElapsed = Date.now() - sessionData.persistedAt
    const shouldAutoRecover = timeElapsed < this.AUTO_RECOVERY_THRESHOLD_MS

    return {
      hasRecoverableSession: true,
      sessionData,
      timeElapsed,
      shouldAutoRecover
    }
  }

  /**
   * Clear persisted session data
   */
  clearSession(): void {
    try {
      localStorage.removeItem(this.STORAGE_KEY)
      console.log('Recording session cleared from persistence')
    } catch (error) {
      console.error('Failed to clear persisted session:', error)
    }
  }

  /**
   * Mark session as completed (clean exit)
   */
  markSessionCompleted(sessionId: string): void {
    const session = this.getSession()
    if (session && session.sessionId === sessionId) {
      this.updateSession({
        status: 'uploading', // Will be cleared when uploads complete
        duration: session.duration
      })
    }
  }

  /**
   * Get session statistics for recovery UI
   */
  getRecoveryStats(sessionData: PersistedRecordingState): {
    durationFormatted: string
    chunksGenerated: number
    sizeFormatted: string
    uploadProgress: string
    timeAgoFormatted: string
  } {
    const duration = Math.floor(sessionData.duration)
    const durationFormatted = `${Math.floor(duration / 60)}:${(duration % 60).toString().padStart(2, '0')}`
    
    const sizeInMB = (sessionData.totalSize / 1024 / 1024).toFixed(1)
    const sizeFormatted = `${sizeInMB}MB`
    
    const uploadPercentage = sessionData.uploadProgress.percentage || 0
    const uploadProgress = `${Math.round(uploadPercentage)}%`
    
    const timeElapsed = Date.now() - sessionData.persistedAt
    const minutes = Math.floor(timeElapsed / (1000 * 60))
    const timeAgoFormatted = minutes < 1 ? 'Just now' : 
                            minutes === 1 ? '1 minute ago' : 
                            `${minutes} minutes ago`

    return {
      durationFormatted,
      chunksGenerated: sessionData.chunkCount,
      sizeFormatted,
      uploadProgress,
      timeAgoFormatted
    }
  }

  /**
   * Validate that a session can be recovered (backend session still exists)
   */
  async validateSessionRecovery(sessionId: string, recordingAPI: any): Promise<boolean> {
    try {
      // Check if the backend session still exists and is in a recoverable state
      const recording = await recordingAPI.getRecording(sessionId)
      
      // Session is recoverable if it exists and is still in recording state
      return recording && recording.status === 'recording'
      
    } catch (error) {
      console.error('Failed to validate session recovery:', error)
      return false
    }
  }

  /**
   * Create session state from current recording data
   */
  createSessionState(
    sessionId: string,
    title: string,
    status: PersistedRecordingState['status'],
    duration: number,
    chunkCount: number,
    totalSize: number,
    lastChunkIndex: number,
    uploadProgress: PersistedRecordingState['uploadProgress'],
    settings: PersistedRecordingState['settings'],
    metadata: Record<string, any> = {}
  ): PersistedRecordingState {
    return {
      sessionId,
      title,
      status,
      startTime: Date.now() - (duration * 1000),
      duration,
      chunkCount,
      totalSize,
      lastChunkIndex,
      uploadProgress,
      settings,
      metadata,
      persistedAt: Date.now()
    }
  }

  /**
   * Clean up old or invalid sessions (maintenance function)
   */
  cleanup(): void {
    const session = this.getSession()
    if (!session) return

    const sessionAge = Date.now() - session.persistedAt
    
    // Clear sessions older than max age
    if (sessionAge > this.MAX_SESSION_AGE_MS) {
      console.log('Cleaning up expired recording session')
      this.clearSession()
      return
    }

    // Clear completed sessions that weren't properly cleaned up
    if (session.status === 'uploading' && session.uploadProgress.percentage >= 100) {
      console.log('Cleaning up completed recording session')
      this.clearSession()
    }
  }

  /**
   * Export session data for debugging
   */
  exportSessionData(): string | null {
    const session = this.getSession()
    return session ? JSON.stringify(session, null, 2) : null
  }

  /**
   * Get session health status
   */
  getSessionHealth(): {
    hasSession: boolean
    isHealthy: boolean
    issues: string[]
  } {
    const issues: string[] = []
    const session = this.getSession()
    
    if (!session) {
      return {
        hasSession: false,
        isHealthy: true,
        issues: []
      }
    }

    // Check session age
    const sessionAge = Date.now() - session.persistedAt
    if (sessionAge > this.MAX_SESSION_AGE_MS) {
      issues.push('Session is too old')
    }

    // Check for data consistency
    if (session.chunkCount < 0 || session.totalSize < 0) {
      issues.push('Invalid session data')
    }

    if (session.uploadProgress.totalChunks < session.uploadProgress.completedChunks) {
      issues.push('Inconsistent upload progress')
    }

    return {
      hasSession: true,
      isHealthy: issues.length === 0,
      issues
    }
  }
}

// Export singleton instance
export const sessionPersistence = new SessionPersistenceService()
export default sessionPersistence