/**
 * useScreenRecording Hook
 * Implements MediaRecorder API for screen capture at 2 FPS
 * Handles permissions, recording state, error management, and session persistence
 */

import { useState, useRef, useCallback, useEffect } from 'react'
import { sessionPersistence } from '../services/sessionPersistence'
import type { PersistedRecordingState, SessionRecoveryInfo } from '../services/sessionPersistence'

export type RecordingStatus = 'idle' | 'requesting-permission' | 'recording' | 'paused' | 'stopping' | 'error'

export interface RecordingState {
  status: RecordingStatus
  duration: number
  mediaStream: MediaStream | null
  error: string | null
  recordingId: string | null
  isRecoveredSession: boolean
  recoveryInfo: SessionRecoveryInfo | null
}

export interface UseScreenRecordingOptions {
  frameRate?: number
  videoBitsPerSecond?: number
  audioBitsPerSecond?: number
  mimeType?: string
  onChunkReady?: (chunk: Blob, timestamp: number) => void
  onRecordingComplete?: (recordingId: string) => void
  onError?: (error: string) => void
  onRecoveryDetected?: (recoveryInfo: SessionRecoveryInfo) => void
  onSessionPersisted?: (sessionData: PersistedRecordingState) => void
  enablePersistence?: boolean
}

export interface UseScreenRecordingReturn {
  state: RecordingState
  startRecording: () => Promise<void>
  stopRecording: () => Promise<void>
  pauseRecording: () => void
  resumeRecording: () => void
  requestPermission: () => Promise<MediaStream | null>
  recoverSession: (recoveryInfo: SessionRecoveryInfo) => Promise<boolean>
  clearRecoveryData: () => void
  getRecoveryInfo: () => SessionRecoveryInfo | null
}

const DEFAULT_OPTIONS = {
  frameRate: 2, // 2 FPS as per architecture
  videoBitsPerSecond: 3500000, // 3.5 Mbps - optimized for GPT-4V text readability
  audioBitsPerSecond: 128000, // 128 kbps for audio
  mimeType: 'video/webm;codecs=vp9,opus',
  onChunkReady: () => {},
  onRecordingComplete: () => {},
  onError: () => {},
  onRecoveryDetected: () => {},
  onSessionPersisted: () => {},
  enablePersistence: true,
}

export const useScreenRecording = (options: UseScreenRecordingOptions = {}): UseScreenRecordingReturn => {
  const opts = { ...DEFAULT_OPTIONS, ...options }
  
  // State management
  const [state, setState] = useState<RecordingState>({
    status: 'idle',
    duration: 0,
    mediaStream: null,
    error: null,
    recordingId: null,
    isRecoveredSession: false,
    recoveryInfo: null,
  })
  
  // Refs for MediaRecorder and timing
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const startTimeRef = useRef<number>(0)
  const durationIntervalRef = useRef<NodeJS.Timeout | null>(null)
  const chunkIntervalRef = useRef<NodeJS.Timeout | null>(null)
  
  // Refs for accumulating chunks during pause/resume cycles
  const accumulatedChunksRef = useRef<Blob[]>([])
  const totalPausedTimeRef = useRef<number>(0)
  const pauseStartTimeRef = useRef<number>(0)
  
  // Refs for accurate duration tracking across pause/resume
  const recordingStartTimeRef = useRef<number>(0)
  const lastDurationRef = useRef<number>(0)
  
  // Refs for persistence tracking
  const sessionDataRef = useRef<PersistedRecordingState | null>(null)
  const lastPersistedTimeRef = useRef<number>(0)
  const persistenceIntervalRef = useRef<NodeJS.Timeout | null>(null)
  const recoveryProcessedRef = useRef<boolean>(false)
  
  // Ref to handle stream ending without circular dependency
  const stopRecordingRef = useRef<(() => Promise<void>) | null>(null)
  
  // Update duration timer - accounts for pause/resume cycles
  const updateDuration = useCallback(() => {
    if (startTimeRef.current > 0) {
      const currentSegmentElapsed = Date.now() - startTimeRef.current
      const totalRecordingTime = lastDurationRef.current + Math.floor(currentSegmentElapsed / 1000)
      setState(prev => ({ ...prev, duration: totalRecordingTime }))
    }
  }, [])
  
  // Start duration tracking
  const startDurationTracking = useCallback(() => {
    startTimeRef.current = Date.now()
    durationIntervalRef.current = setInterval(updateDuration, 1000)
  }, [updateDuration])
  
  // Stop duration tracking
  const stopDurationTracking = useCallback(() => {
    if (durationIntervalRef.current) {
      clearInterval(durationIntervalRef.current)
      durationIntervalRef.current = null
    }
    startTimeRef.current = 0
  }, [])

  // Persistence helper functions
  const updatePersistedSession = useCallback(() => {
    if (!opts.enablePersistence || !sessionDataRef.current) return

    const now = Date.now()
    // Only persist every 5 seconds to avoid excessive localStorage writes
    if (now - lastPersistedTimeRef.current < 5000) return

    const updatedSession: Partial<PersistedRecordingState> = {
      duration: state.duration,
      status: state.status as any,
      persistedAt: now
    }

    sessionPersistence.updateSession(updatedSession)
    lastPersistedTimeRef.current = now
  }, [opts.enablePersistence, state.duration, state.status])

  const startPersistenceTracking = useCallback(() => {
    if (!opts.enablePersistence) return
    
    persistenceIntervalRef.current = setInterval(updatePersistedSession, 5000)
  }, [opts.enablePersistence, updatePersistedSession])

  const stopPersistenceTracking = useCallback(() => {
    if (persistenceIntervalRef.current) {
      clearInterval(persistenceIntervalRef.current)
      persistenceIntervalRef.current = null
    }
  }, [])

  // Recovery functions
  const getRecoveryInfo = useCallback((): SessionRecoveryInfo | null => {
    if (!opts.enablePersistence) return null
    return sessionPersistence.checkRecovery()
  }, [opts.enablePersistence])

  const clearRecoveryData = useCallback(() => {
    sessionPersistence.clearSession()
    sessionDataRef.current = null
    setState(prev => ({ 
      ...prev, 
      isRecoveredSession: false, 
      recoveryInfo: null 
    }))
  }, [])

  const recoverSession = useCallback(async (recoveryInfo: SessionRecoveryInfo): Promise<boolean> => {
    if (!recoveryInfo.hasRecoverableSession || !recoveryInfo.sessionData) {
      return false
    }

    try {
      const sessionData = recoveryInfo.sessionData
      sessionDataRef.current = sessionData

      // Restore state from persisted data
      setState(prev => ({
        ...prev,
        status: 'idle', // Will be updated when recording resumes
        duration: sessionData.duration,
        recordingId: sessionData.sessionId,
        isRecoveredSession: true,
        recoveryInfo,
        error: null
      }))

      console.log(`Session recovered: ${sessionData.sessionId}`)
      return true

    } catch (error) {
      console.error('Failed to recover session:', error)
      opts.onError?.(`Session recovery failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
      return false
    }
  }, [opts])
  
  // Request screen capture permission
  const requestPermission = useCallback(async (): Promise<MediaStream | null> => {
    try {
      setState(prev => ({ ...prev, status: 'requesting-permission', error: null }))
      
      // Check if browser supports screen capture
      if (!navigator.mediaDevices || !navigator.mediaDevices.getDisplayMedia) {
        throw new Error('Screen capture is not supported in this browser')
      }
      
      // Request screen capture permission with improved UX
      const stream = await navigator.mediaDevices.getDisplayMedia({
        video: {
          frameRate: opts.frameRate,
          // Let user choose resolution, but provide hints
          width: { ideal: 1920 },
          height: { ideal: 1080 },
          // Use type assertion for display media specific constraints
          ...(({ cursor: 'always', displaySurface: 'monitor' }) as any)
        },
        audio: {
          sampleRate: 44100,
          sampleSize: 16,
          channelCount: 2,
          echoCancellation: true,
          noiseSuppression: true,
        }
      })
      
      setState(prev => ({ 
        ...prev, 
        status: 'idle', 
        mediaStream: stream,
        error: null 
      }))
      
      return stream
      
    } catch (error) {
      let errorMessage = 'Failed to access screen recording'
      
      if (error instanceof Error) {
        if (error.name === 'NotAllowedError') {
          errorMessage = '🚫 Screen recording permission was denied. Please click "Share screen" when the browser asks for permission.'
        } else if (error.name === 'NotSupportedError') {
          errorMessage = '❌ Screen recording is not supported in this browser. Please use Chrome, Firefox, or Safari.'
        } else if (error.name === 'NotFoundError') {
          errorMessage = '📺 No screen available to record. Please ensure you have a display connected.'
        } else if (error.name === 'AbortError') {
          errorMessage = '⏹️ Screen recording was cancelled. Click "Start Recording" to try again.'
        } else {
          errorMessage = `❌ Screen recording failed: ${error.message}`
        }
      }
      
      setState(prev => ({ 
        ...prev, 
        status: 'error', 
        error: errorMessage,
        mediaStream: null 
      }))
      opts.onError(errorMessage)
      return null
    }
  }, [opts])
  
  // Start recording
  const startRecording = useCallback(async (): Promise<void> => {
    try {
      // Get permission if not already granted
      let stream = state.mediaStream
      if (!stream) {
        stream = await requestPermission()
        if (!stream) return
      }
      
      // Check MediaRecorder support
      if (!MediaRecorder.isTypeSupported(opts.mimeType)) {
        // Fallback to basic WebM
        const fallbackMimeType = 'video/webm'
        if (!MediaRecorder.isTypeSupported(fallbackMimeType)) {
          throw new Error('WebM recording is not supported in this browser')
        }
        opts.mimeType = fallbackMimeType
      }
      
      // Create MediaRecorder with validation
      console.log('Creating MediaRecorder with stream:', stream)
      console.log('Stream tracks:', stream.getTracks().map(t => ({ kind: t.kind, readyState: t.readyState })))
      
      if (!stream || stream.getTracks().length === 0) {
        throw new Error('Invalid media stream: no tracks available')
      }
      
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: opts.mimeType,
        videoBitsPerSecond: opts.videoBitsPerSecond,
        audioBitsPerSecond: opts.audioBitsPerSecond,
      })
      
      console.log('MediaRecorder created successfully:', mediaRecorder.state)
      
      mediaRecorderRef.current = mediaRecorder
      
      // Generate recording ID and reset accumulation state
      const recordingId = `recording_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      
      // Reset chunk accumulation and duration tracking for new recording
      accumulatedChunksRef.current = []
      totalPausedTimeRef.current = 0
      pauseStartTimeRef.current = 0
      recordingStartTimeRef.current = Date.now()
      lastDurationRef.current = 0
      
      // Handle data available - only collect final complete recording
      mediaRecorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          console.log(`Final recording data received: ${event.data.size} bytes`)
          // Send the complete recording immediately - no need to accumulate since we're not chunking
          opts.onChunkReady(event.data, Date.now())
        }
      }
      
      // Handle recording stop
      mediaRecorder.onstop = () => {
        stopDurationTracking()
        if (chunkIntervalRef.current) {
          clearInterval(chunkIntervalRef.current)
          chunkIntervalRef.current = null
        }
        
        // Calculate final duration including any current segment
        if (startTimeRef.current > 0) {
          const finalSegmentDuration = Math.floor((Date.now() - startTimeRef.current) / 1000)
          lastDurationRef.current += finalSegmentDuration
          console.log(`Final duration calculation: ${lastDurationRef.current}s total`)
        }
        
        // Note: MediaRecorder will automatically call ondataavailable with complete recording when stopped
        
        setState(prev => ({ 
          ...prev, 
          status: 'idle',
          recordingId: null 
        }))
        
        if (recordingId) {
          opts.onRecordingComplete(recordingId)
        }
      }
      
      // Handle errors
      mediaRecorder.onerror = (event) => {
        const errorMessage = `Recording error: ${event.error?.message || 'Unknown error'}`
        setState(prev => ({ 
          ...prev, 
          status: 'error', 
          error: errorMessage 
        }))
        opts.onError(errorMessage)
      }
      
      // Start recording - single video mode for MVP
      mediaRecorder.start()
      
      // DISABLED FOR MVP: Chunking every 5 seconds
      // Re-enable this when we need chunking for larger recordings
      // chunkIntervalRef.current = setInterval(() => {
      //   if (mediaRecorder.state === 'recording') {
      //     mediaRecorder.requestData()
      //   }
      // }, 5000) // 5-second chunks as per architecture
      
      // Handle stream ending (user stops sharing) - use ref to avoid circular dependency
      const videoTracks = stream.getVideoTracks()
      if (videoTracks.length > 0) {
        videoTracks[0].addEventListener('ended', () => {
          console.log('Stream ended by user (clicked browser stop button)')
          // Immediately update UI to show processing state to prevent freeze
          setState(prev => ({ ...prev, status: 'stopping' }))
          // Properly stop recording when user clicks browser's stop sharing button
          if (stopRecordingRef.current && mediaRecorderRef.current?.state === 'recording') {
            console.log('Stopping recording due to stream end')
            stopRecordingRef.current()
          }
        })
        console.log('Stream ended event listener added to video track')
      } else {
        console.warn('No video tracks found in stream')
      }
      
      // Update state
      setState(prev => ({ 
        ...prev, 
        status: 'recording', 
        error: null,
        recordingId 
      }))
      
      console.log('Recording state updated to: recording')
      
      // Start duration tracking
      startDurationTracking()

      // Start session persistence
      if (opts.enablePersistence) {
        const sessionData = sessionPersistence.createSessionState(
          recordingId,
          `Workflow Recording - ${new Date().toLocaleString()}`,
          'recording',
          0, // initial duration
          0, // initial chunk count  
          0, // initial total size
          -1, // initial chunk index
          {
            totalChunks: 0,
            completedChunks: 0,
            failedChunks: 0,
            uploadedBytes: 0,
            totalBytes: 0,
            percentage: 0
          },
          {
            useEnhancedUpload: true,
            useDirectStorage: true
          },
          {
            browser: navigator.userAgent,
            screen_resolution: `${screen.width}x${screen.height}`,
            recording_start_time: new Date().toISOString()
          }
        )

        sessionDataRef.current = sessionData
        sessionPersistence.saveSession(sessionData)
        startPersistenceTracking()
        lastPersistedTimeRef.current = Date.now()

        opts.onSessionPersisted?.(sessionData)
      }
      
    } catch (error) {
      let errorMessage = '❌ Failed to start recording'
      
      if (error instanceof Error) {
        if (error.message.includes('MediaRecorder')) {
          errorMessage = '🎥 Recording setup failed. Your browser may not support the required video format. Try refreshing the page.'
        } else if (error.message.includes('Invalid media stream')) {
          errorMessage = '📺 No valid screen capture available. Please grant screen recording permission and try again.'
        } else {
          errorMessage = `❌ Recording failed: ${error.message}. Click "Start Recording" to try again.`
        }
      }
      
      setState(prev => ({ 
        ...prev, 
        status: 'error', 
        error: errorMessage 
      }))
      opts.onError(errorMessage)
    }
  }, [state.mediaStream, opts, requestPermission, startDurationTracking, stopDurationTracking])
  
  // Stop recording
  const stopRecording = useCallback(async (): Promise<void> => {
    try {
      setState(prev => ({ ...prev, status: 'stopping' }))
      
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop()
      }
      
      // Stop all tracks
      if (state.mediaStream) {
        state.mediaStream.getTracks().forEach(track => {
          track.stop()
        })
        setState(prev => ({ ...prev, mediaStream: null }))
      }
      
      stopDurationTracking()
      stopPersistenceTracking()

      // Clear session persistence on successful completion
      if (opts.enablePersistence && state.recordingId) {
        sessionPersistence.markSessionCompleted(state.recordingId)
      }
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to stop recording'
      setState(prev => ({ 
        ...prev, 
        status: 'error', 
        error: errorMessage 
      }))
      opts.onError(errorMessage)
    }
  }, [state.mediaStream, state.recordingId, stopDurationTracking, stopPersistenceTracking, opts])
  
  // Update ref when stopRecording changes
  stopRecordingRef.current = stopRecording
  
  // Pause recording (UI-only pause - MediaRecorder continues to capture screen)
  const pauseRecording = useCallback(() => {
    try {
      if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
        console.log('Pausing recording (UI only - MediaRecorder continues)...')
        
        // Record pause start time for duration tracking
        pauseStartTimeRef.current = Date.now()
        
        // Save current recording time before pausing
        if (startTimeRef.current > 0) {
          const currentSegmentDuration = Math.floor((Date.now() - startTimeRef.current) / 1000)
          lastDurationRef.current += currentSegmentDuration
          console.log(`Saving duration: previous=${lastDurationRef.current - currentSegmentDuration}s + current=${currentSegmentDuration}s = total=${lastDurationRef.current}s`)
        }
        
        // Don't pause MediaRecorder - just update UI state and stop duration tracking
        setState(prev => ({ ...prev, status: 'paused' }))
        stopDurationTracking()
        
        // Update persistence
        if (opts.enablePersistence) {
          sessionPersistence.updateSession({ status: 'paused' })
        }
        console.log('Recording paused successfully (UI state only)')
      } else {
        console.warn('Cannot pause - MediaRecorder state:', mediaRecorderRef.current?.state)
      }
    } catch (error) {
      console.error('Failed to pause recording:', error)
      opts.onError?.(`Failed to pause recording: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }, [stopDurationTracking, opts.enablePersistence, opts])
  
  // Resume recording (UI-only resume - MediaRecorder was never paused)
  const resumeRecording = useCallback(() => {
    try {
      if (state.status === 'paused') {
        console.log('Resuming recording (UI only)...')
        
        // Calculate paused time and add to total
        if (pauseStartTimeRef.current > 0) {
          const pausedDuration = Date.now() - pauseStartTimeRef.current
          totalPausedTimeRef.current += pausedDuration
          console.log(`Added ${pausedDuration}ms to total paused time: ${totalPausedTimeRef.current}ms`)
          pauseStartTimeRef.current = 0
        }
        
        // Resume UI state and duration tracking
        setState(prev => ({ ...prev, status: 'recording' }))
        startDurationTracking()
        
        // Update persistence
        if (opts.enablePersistence) {
          sessionPersistence.updateSession({ status: 'recording' })
        }
        console.log('Recording resumed successfully (UI state only)')
      } else {
        console.warn('Cannot resume - current status:', state.status)
      }
    } catch (error) {
      console.error('Failed to resume recording:', error)
      opts.onError?.(`Failed to resume recording: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }, [startDurationTracking, opts.enablePersistence, opts, state.status])

  // Recovery detection on mount
  useEffect(() => {
    if (!opts.enablePersistence || recoveryProcessedRef.current) return

    const checkForRecovery = async () => {
      try {
        recoveryProcessedRef.current = true // Prevent duplicate processing
        
        sessionPersistence.cleanup() // Clean up old/invalid sessions first
        
        const recoveryInfo = sessionPersistence.checkRecovery()
        
        if (recoveryInfo.hasRecoverableSession && recoveryInfo.sessionData) {
          setState(prev => ({
            ...prev,
            recoveryInfo
          }))
          
          opts.onRecoveryDetected?.(recoveryInfo)
          
          // Auto-recover if session is recent and shouldAutoRecover is true
          if (recoveryInfo.shouldAutoRecover) {
            console.log('Auto-recovering recent session...')
            await recoverSession(recoveryInfo)
          }
        }
      } catch (error) {
        console.error('Error checking for session recovery:', error)
      }
    }

    checkForRecovery()
  }, [opts.enablePersistence, opts.onRecoveryDetected, recoverSession])
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (state.status === 'recording') {
        stopRecording()
      }
      stopDurationTracking()
      stopPersistenceTracking()
      if (chunkIntervalRef.current) {
        clearInterval(chunkIntervalRef.current)
      }
    }
  }, []) // Only run on unmount
  
  return {
    state,
    startRecording,
    stopRecording,
    pauseRecording,
    resumeRecording,
    requestPermission,
    recoverSession,
    clearRecoveryData,
    getRecoveryInfo,
  }
}