/**
 * RecordingControls Component
 * Main recording interface with start/stop controls
 * Integrates MediaRecorder API with backend API
 */

import React, { useState, useCallback, useRef, useEffect } from 'react'
import { Play, Square, Pause, Monitor, AlertCircle, CheckCircle, Upload, RotateCcw, RefreshCw, X, Clock } from 'lucide-react'
import { useScreenRecording } from '../hooks/useScreenRecording'
import { recordingAPI, RecordingAPIError, isRecordingAPIError } from '../services/recordingAPI'
import type { UploadProgress, UploadEvent } from '../services/uploadQueue'
import { sessionPersistence } from '../services/sessionPersistence'
import type { SessionRecoveryInfo } from '../services/sessionPersistence'

interface RecordingControlsProps {
  onRecordingComplete?: (recordingId: string) => void
  onError?: (error: string) => void
  className?: string
}

export const RecordingControls: React.FC<RecordingControlsProps> = ({
  onRecordingComplete,
  onError,
  className = '',
}) => {
  // Component state
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState<UploadProgress>({
    totalChunks: 0,
    completedChunks: 0,
    failedChunks: 0,
    uploadedBytes: 0,
    totalBytes: 0,
    percentage: 0,
    estimatedTimeRemaining: 0,
    averageUploadSpeed: 0,
  })
  const [chunkCount, setChunkCount] = useState(0)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [totalSize, setTotalSize] = useState(0)
  const [uploadErrors, setUploadErrors] = useState<string[]>([])
  const [useEnhancedUpload, setUseEnhancedUpload] = useState(true)
  const [useDirectStorage, setUseDirectStorage] = useState(false) // Temporarily use proxied uploads until backend issue is fixed
  const [showAdvancedSettings, setShowAdvancedSettings] = useState(false)
  
  // Recovery state
  const [showRecoveryBanner, setShowRecoveryBanner] = useState(false)
  const [recoveryInfo, setRecoveryInfo] = useState<SessionRecoveryInfo | null>(null)
  const [isRecovering, setIsRecovering] = useState(false)
  
  // Refs for chunk management and stable callback references
  const chunkIndexRef = useRef(0)
  const chunksRef = useRef<Blob[]>([])
  
  // Create stable callback refs to avoid circular dependency
  const handleChunkReadyRef = useRef<((chunk: Blob, timestamp: number) => Promise<void>) | undefined>()
  const handleRecordingCompleteRef = useRef<((recordingId: string) => Promise<void>) | undefined>()
  const screenRecordingRef = useRef<any>(null)
  
  // Initialize screen recording hook with stable callback references
  const screenRecording = useScreenRecording({
    frameRate: 2, // 2 FPS as per architecture
    onChunkReady: (chunk: Blob, timestamp: number) => handleChunkReadyRef.current?.(chunk, timestamp),
    onRecordingComplete: (recordingId: string) => handleRecordingCompleteRef.current?.(recordingId),
    onError: (error) => {
      console.error('Screen recording error:', error)
      onError?.(error)
    },
    onRecoveryDetected: (info: SessionRecoveryInfo) => {
      console.log('Recovery detected:', info)
      setRecoveryInfo(info)
      setShowRecoveryBanner(true)
    },
    onSessionPersisted: (sessionData) => {
      console.log('Session persisted:', sessionData.sessionId)
    },
    enablePersistence: true
  })
  
  // Store reference for use in callbacks
  screenRecordingRef.current = screenRecording
  
  // Set up upload event listeners
  useEffect(() => {
    const handleUploadEvent = (event: UploadEvent) => {
      switch (event.type) {
        case 'progress':
          if (event.data.progress) {
            setUploadProgress(event.data.progress)
          }
          break
        case 'chunk_completed':
          console.log('Chunk completed:', event.data.task?.chunkIndex)
          break
        case 'chunk_failed':
          console.error('Chunk failed:', event.data.task?.chunkIndex, event.data.error)
          if (event.data.error) {
            setUploadErrors(prev => [...prev, event.data.error!])
          }
          break
        case 'queue_completed':
          console.log('All chunks uploaded successfully')
          // Note: setIsUploading(false) is handled in completeRecordingSession
          break
        case 'queue_failed':
          console.error('Upload queue failed:', event.data.error)
          setIsUploading(false)
          if (event.data.error) {
            onError?.(event.data.error)
          }
          break
      }
    }

    recordingAPI.onUploadEvent(handleUploadEvent)
    
    return () => {
      recordingAPI.offUploadEvent(handleUploadEvent)
    }
  }, [onError])

  // Recovery handlers
  const handleRecoverSession = useCallback(async () => {
    if (!recoveryInfo || !recoveryInfo.hasRecoverableSession) return

    setIsRecovering(true)
    try {
      const success = await screenRecording.recoverSession(recoveryInfo)
      
      if (success && recoveryInfo.sessionData) {
        const sessionData = recoveryInfo.sessionData
        
        // Restore UI state from recovered session
        setSessionId(sessionData.sessionId)
        setChunkCount(sessionData.chunkCount)
        setTotalSize(sessionData.totalSize)
        setUseEnhancedUpload(sessionData.settings.useEnhancedUpload)
        setUseDirectStorage(sessionData.settings.useDirectStorage)
        
        // Restore upload progress
        setUploadProgress(sessionData.uploadProgress)
        
        console.log(`Successfully recovered session: ${sessionData.sessionId}`)
        setShowRecoveryBanner(false)
        
        // Configure upload queue for recovered session if needed
        if (sessionData.uploadProgress.totalChunks > sessionData.uploadProgress.completedChunks) {
          // There are pending uploads from the recovered session
          console.log(`Recovered session has ${sessionData.uploadProgress.totalChunks - sessionData.uploadProgress.completedChunks} pending uploads`)
        }

        // Success notification (using onError for now as success callback)
        const durationText = `${Math.floor(sessionData.duration / 60)}:${(sessionData.duration % 60).toString().padStart(2, '0')}`
        console.log(`✅ Recording session recovered! Duration: ${durationText}, Chunks: ${sessionData.chunkCount}`)
      } else {
        throw new Error('Failed to recover session - session validation failed')
      }
    } catch (error) {
      console.error('Recovery failed:', error)
      onError?.(`Recovery failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setIsRecovering(false)
    }
  }, [recoveryInfo, screenRecording, onError])

  const handleDismissRecovery = useCallback(() => {
    screenRecording.clearRecoveryData()
    setShowRecoveryBanner(false)
    setRecoveryInfo(null)
  }, [screenRecording])

  // Update upload method when storage setting changes
  useEffect(() => {
    if (useDirectStorage) {
      recordingAPI.enableDirectUploads()
      console.log('Enabled direct Supabase uploads')
    } else {
      recordingAPI.enableProxiedUploads()
      console.log('Enabled proxied uploads through backend')
    }
  }, [useDirectStorage])
  
  // Handle chunk ready callback
  handleChunkReadyRef.current = async (chunk: Blob, timestamp: number) => {
    if (!sessionId) return
    
    try {
      // Store video temporarily (MVP: single video instead of chunks)
      chunksRef.current.push(chunk)
      setTotalSize(prev => prev + chunk.size)
      
      // For MVP: This will typically be called once with the complete video
      // We still support multiple chunks if browser provides them
      const chunkIndex = chunkIndexRef.current++
      setChunkCount(chunkIndex + 1)
      
      const sizeKB = Math.round(chunk.size / 1024)
      const sizeMB = Math.round(sizeKB / 1024)
      console.log(`Processing video data (chunk ${chunkIndex}): ${chunk.size} bytes (${sizeMB > 0 ? sizeMB + ' MB' : sizeKB + ' KB'})`)
      
      if (useEnhancedUpload) {
        // Use enhanced upload queue with retry logic
        recordingAPI.queueChunkUpload(sessionId, chunk, chunkIndex)
        if (!isUploading) {
          setIsUploading(true)
        }
      } else {
        // Use direct upload (legacy method)
        await recordingAPI.uploadChunk(sessionId, chunk, chunkIndex)
      }
      
    } catch (error) {
      console.error('Chunk processing failed:', error)
      const errorMessage = isRecordingAPIError(error) 
        ? error.message 
        : 'Failed to process recording chunk'
      onError?.(errorMessage)
    }
  }
  
  // Handle recording completion callback
  handleRecordingCompleteRef.current = async (recordingId: string) => {
    if (!sessionId) return
    
    console.log('Recording stopped - checking upload queue status')
    // Only set isUploading if not already set (avoid double-setting when stop button was used)
    setIsUploading(prev => prev || true)
    
    // Check if we're using enhanced upload queue
    if (useEnhancedUpload) {
      // Wait for upload queue to complete before marking session as completed
      const progress = recordingAPI.getUploadProgress()
      
      if (progress.totalChunks > 0 && progress.completedChunks < progress.totalChunks) {
        console.log(`Waiting for ${progress.totalChunks - progress.completedChunks} remaining uploads to complete`)
        
        // Set up one-time listener for queue completion
        const handleQueueComplete = async (event: UploadEvent) => {
          if (event.type === 'queue_completed') {
            console.log('All uploads completed - now completing recording session')
            recordingAPI.offUploadEvent(handleQueueComplete)
            await completeRecordingSession(recordingId)
          } else if (event.type === 'queue_failed') {
            console.error('Upload queue failed - completing recording with partial data')
            recordingAPI.offUploadEvent(handleQueueComplete)
            await completeRecordingSession(recordingId)
          }
        }
        
        recordingAPI.onUploadEvent(handleQueueComplete)
        return // Wait for queue to complete
      }
    }
    
    // If no uploads pending or not using enhanced upload, complete immediately
    await completeRecordingSession(recordingId)
  }
  
  // Helper function to complete recording session
  const completeRecordingSession = async (recordingId: string) => {
    if (!sessionId) return
    
    try {
      // Get current duration from the screen recording state via ref
      const currentDuration = screenRecordingRef.current?.state?.duration || 0
      
      // Calculate total size from chunks if totalSize is 0
      let finalTotalSize = totalSize
      if (finalTotalSize === 0 && chunksRef.current.length > 0) {
        finalTotalSize = chunksRef.current.reduce((sum, chunk) => sum + chunk.size, 0)
        console.log('Calculated total size from chunks:', finalTotalSize)
      }
      
      // Log file size for debugging
      console.log('Completing recording with:', {
        totalSize: finalTotalSize,
        chunkCount: chunksRef.current.length || chunkCount,
        duration: currentDuration
      })
      
      // Complete the recording session
      const response = await recordingAPI.completeRecording(sessionId, {
        duration_seconds: currentDuration,
        total_file_size_bytes: finalTotalSize,
        chunk_count: chunksRef.current.length || chunkCount,
        metadata: {
          browser: navigator.userAgent,
          screen_resolution: `${screen.width}x${screen.height}`,
          recording_end_time: new Date().toISOString(),
        }
      })
      
      console.log('Recording completed:', response)
      
      // Reset state
      setSessionId(null)
      setChunkCount(0)
      setTotalSize(0)
      chunkIndexRef.current = 0
      chunksRef.current = []
      
      onRecordingComplete?.(sessionId)
      
    } catch (error) {
      console.error('Failed to complete recording:', error)
      const errorMessage = isRecordingAPIError(error)
        ? error.message
        : 'Failed to complete recording'
      onError?.(errorMessage)
    } finally {
      setIsUploading(false)
    }
  }
  
  // Start recording handler
  const handleStartRecording = useCallback(async () => {
    try {
      // Create recording session
      const session = await recordingAPI.startRecording({
        title: `Workflow Recording - ${new Date().toLocaleString()}`,
        description: 'Screen recording for workflow analysis',
        workflow_type: 'general_workflow',
        privacy_settings: {
          blur_passwords: true,
          exclude_personal_info: false,
          custom_exclusions: []
        },
        metadata: {
          browser: navigator.userAgent,
          screen_resolution: `${screen.width}x${screen.height}`,
          recording_start_time: new Date().toISOString(),
        }
      })
      
      console.log('Recording session created:', session)
      setSessionId(session.id)
      
      // Reset counters
      setChunkCount(0)
      setTotalSize(0)
      chunkIndexRef.current = 0
      chunksRef.current = []
      
      // Start screen recording
      await screenRecording.startRecording()
      
    } catch (error) {
      console.error('Failed to start recording:', error)
      const errorMessage = isRecordingAPIError(error)
        ? error.message
        : 'Failed to start recording session'
      onError?.(errorMessage)
    }
  }, [screenRecording, onError])
  
  // Stop recording handler
  const handleStopRecording = useCallback(async () => {
    // Set uploading state immediately to show "Finishing Upload..." message
    setIsUploading(true)
    await screenRecording.stopRecording()
    // Note: isUploading will be reset to false in completeRecordingSession
  }, [screenRecording])
  
  // Format duration as MM:SS
  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  
  // Get status color
  const getStatusColor = () => {
    switch (screenRecording.state.status) {
      case 'recording': return 'text-red-600'
      case 'paused': return 'text-yellow-600'
      case 'error': return 'text-red-600'
      case 'requesting-permission': return 'text-blue-600'
      default: return 'text-gray-600'
    }
  }
  
  // Get status icon
  const getStatusIcon = () => {
    switch (screenRecording.state.status) {
      case 'recording': return <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
      case 'error': return <AlertCircle className="w-5 h-5 text-red-500" />
      case 'requesting-permission': return <Monitor className="w-5 h-5 text-blue-500" />
      default: return <CheckCircle className="w-5 h-5 text-green-500" />
    }
  }
  
  const { status, duration, error } = screenRecording.state
  const isRecording = status === 'recording'
  const canStart = status === 'idle' && !isUploading
  const canStop = status === 'recording' || status === 'paused'
  
  return (
    <div className={`bg-gradient-to-br from-blue-50 to-indigo-100 rounded-xl shadow-xl border border-blue-200 p-8 max-w-4xl mx-auto ${className}`}>
      {/* Recovery Banner */}
      {showRecoveryBanner && recoveryInfo && recoveryInfo.sessionData && (
        <div className="mb-6 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start justify-between">
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0">
                <RefreshCw className="w-6 h-6 text-blue-600" />
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-blue-900 mb-2">
                  Recording Session Recovery Available
                </h3>
                <div className="text-blue-800 text-sm space-y-1">
                  <p>
                    An incomplete recording session was found from{' '}
                    <span className="font-medium">
                      {sessionPersistence.getRecoveryStats(recoveryInfo.sessionData).timeAgoFormatted}
                    </span>
                  </p>
                  <div className="grid grid-cols-3 gap-4 mt-3">
                    <div className="flex items-center space-x-2">
                      <Clock className="w-4 h-4 text-blue-600" />
                      <span className="font-medium">
                        {sessionPersistence.getRecoveryStats(recoveryInfo.sessionData).durationFormatted}
                      </span>
                      <span className="text-xs text-blue-600">recorded</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Upload className="w-4 h-4 text-blue-600" />
                      <span className="font-medium">
                        {sessionPersistence.getRecoveryStats(recoveryInfo.sessionData).chunksGenerated}
                      </span>
                      <span className="text-xs text-blue-600">chunks</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Monitor className="w-4 h-4 text-blue-600" />
                      <span className="font-medium">
                        {sessionPersistence.getRecoveryStats(recoveryInfo.sessionData).sizeFormatted}
                      </span>
                      <span className="text-xs text-blue-600">size</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <button
              onClick={handleDismissRecovery}
              className="flex-shrink-0 text-blue-600 hover:text-blue-800 transition-colors"
              title="Dismiss recovery"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          
          <div className="flex items-center justify-between mt-4 pt-3 border-t border-blue-200">
            <p className="text-blue-700 text-sm">
              Would you like to resume this recording session?
            </p>
            <div className="flex items-center space-x-3">
              <button
                onClick={handleDismissRecovery}
                className="px-3 py-1.5 text-blue-700 hover:text-blue-900 transition-colors text-sm"
              >
                Dismiss
              </button>
              <button
                onClick={handleRecoverSession}
                disabled={isRecovering}
                className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                  isRecovering
                    ? 'bg-blue-300 text-blue-800 cursor-not-allowed'
                    : 'bg-blue-600 hover:bg-blue-700 text-white'
                }`}
              >
                {isRecovering ? (
                  <span className="flex items-center space-x-2">
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Recovering...</span>
                  </span>
                ) : (
                  'Recover Session'
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modern Header */}
      <div className="text-center mb-8">
        <div className="flex items-center justify-center space-x-4 mb-4">
          <div className="bg-white rounded-full p-3 shadow-lg">
            {getStatusIcon()}
          </div>
          <div>
            <h1 className="text-3xl font-bold text-slate-800 mb-1">AI Screen Recorder</h1>
            <p className="text-slate-600">Capture workflows at 2 FPS for AI analysis</p>
          </div>
        </div>
        
        {/* Recording Timer */}
        <div className="bg-white rounded-lg shadow-inner p-4 inline-block">
          <div className={`text-4xl font-mono font-bold ${getStatusColor()} mb-2`}>
            {formatDuration(duration)}
          </div>
          <div className="flex items-center justify-center space-x-3 text-sm text-slate-600">
            <span className="capitalize">
              {status === 'requesting-permission' 
                ? 'Please select your screen to share' 
                : status.replace('-', ' ')
              }
            </span>
            {screenRecording.state.isRecoveredSession && (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                <RefreshCw className="w-3 h-3 mr-1" />
                Recovered Session
              </span>
            )}
          </div>
        </div>
      </div>
      
      {/* Enhanced Recording & Upload Stats */}
      {(isRecording || isUploading) && (
        <div className="bg-gray-50 rounded-lg p-4 mb-6">
          {/* Basic Recording Stats */}
          <div className="grid grid-cols-3 gap-4 text-center mb-4">
            <div>
              <div className="text-2xl font-bold text-teal-600">{chunkCount}</div>
              <div className="text-xs text-gray-600">Chunks Generated</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-teal-600">
                {(totalSize / 1024 / 1024).toFixed(1)}MB
              </div>
              <div className="text-xs text-gray-600">Total Size</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-teal-600">2</div>
              <div className="text-xs text-gray-600">FPS</div>
            </div>
          </div>

          {/* Enhanced Upload Progress */}
          {useEnhancedUpload && isUploading && uploadProgress.totalChunks > 0 && (
            <div className="border-t pt-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">Upload Progress</span>
                <span className="text-sm text-gray-600">
                  {uploadProgress.completedChunks}/{uploadProgress.totalChunks} chunks
                </span>
              </div>
              
              {/* Progress Bar */}
              <div className="w-full bg-gray-200 rounded-full h-2 mb-3">
                <div 
                  className="bg-teal-600 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${uploadProgress.percentage}%` }}
                />
              </div>

              {/* Upload Stats */}
              <div className="grid grid-cols-4 gap-2 text-center">
                <div>
                  <div className="text-lg font-bold text-green-600">
                    {uploadProgress.completedChunks}
                  </div>
                  <div className="text-xs text-gray-600">Completed</div>
                </div>
                <div>
                  <div className="text-lg font-bold text-red-600">
                    {uploadProgress.failedChunks}
                  </div>
                  <div className="text-xs text-gray-600">Failed</div>
                </div>
                <div>
                  <div className="text-lg font-bold text-teal-600">
                    {(uploadProgress.averageUploadSpeed / 1024).toFixed(1)}
                  </div>
                  <div className="text-xs text-gray-600">KB/s</div>
                </div>
                <div>
                  <div className="text-lg font-bold text-gray-600">
                    {Math.ceil(uploadProgress.estimatedTimeRemaining / 1000)}s
                  </div>
                  <div className="text-xs text-gray-600">ETA</div>
                </div>
              </div>

              {/* Retry Button */}
              {uploadProgress.failedChunks > 0 && (
                <div className="mt-3 text-center">
                  <button
                    onClick={() => recordingAPI.retryFailedUploads()}
                    className="inline-flex items-center space-x-2 px-3 py-1 bg-red-600 hover:bg-red-700 text-white text-sm rounded-lg transition-colors"
                  >
                    <RotateCcw className="w-4 h-4" />
                    <span>Retry Failed ({uploadProgress.failedChunks})</span>
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Recovery Success Status */}
      {screenRecording.state.isRecoveredSession && status === 'idle' && (
        <div className="bg-green-50 rounded-lg p-4 mb-6 border border-green-200">
          <div className="flex items-center space-x-3">
            <div className="flex-shrink-0">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-green-900 mb-1">
                Session Successfully Recovered
              </h3>
              <div className="text-green-800 text-sm">
                <p>
                  Previous recording session has been restored. You can continue recording or 
                  review the recovered data before proceeding.
                </p>
                <div className="mt-2 flex items-center space-x-4 text-xs">
                  <span>📹 Duration: {formatDuration(duration)}</span>
                  <span>📦 Chunks: {chunkCount}</span>
                  <span>💾 Size: {(totalSize / 1024 / 1024).toFixed(1)}MB</span>
                </div>
              </div>
            </div>
            <button
              onClick={() => {
                screenRecording.clearRecoveryData()
                // Reset UI state to clean state
                setChunkCount(0)
                setTotalSize(0)
                setSessionId(null)
              }}
              className="flex-shrink-0 text-green-600 hover:text-green-800 transition-colors"
              title="Clear recovery status"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>
      )}
      
      {/* Simplified Controls */}
      <div className="flex items-center justify-center mb-8">
        {!isRecording ? (
          <button
            onClick={handleStartRecording}
            disabled={!canStart}
            className={`
              flex items-center space-x-3 px-8 py-4 rounded-full text-lg font-semibold shadow-lg transform transition-all duration-300
              ${canStart 
                ? 'bg-gradient-to-r from-green-500 to-teal-600 hover:from-green-600 hover:to-teal-700 text-white hover:scale-105 hover:shadow-xl' 
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              }
            `}
          >
            <Play className="w-6 h-6" />
            <span>Start Screen Recording</span>
          </button>
        ) : (
          <div className="flex items-center space-x-4">
            <button
              onClick={screenRecording.pauseRecording}
              className="flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-600 hover:to-orange-600 text-white rounded-full font-medium transition-all duration-300 hover:scale-105 shadow-lg"
            >
              <Pause className="w-5 h-5" />
              <span>Pause</span>
            </button>
            
            <button
              onClick={handleStopRecording}
              disabled={isUploading}
              className="flex items-center space-x-3 px-8 py-4 bg-gradient-to-r from-red-500 to-pink-600 hover:from-red-600 hover:to-pink-700 text-white rounded-full text-lg font-semibold transition-all duration-300 hover:scale-105 shadow-lg disabled:opacity-50 disabled:hover:scale-100"
            >
              <Square className="w-6 h-6" />
              <span>{isUploading ? 'Finishing Upload...' : 'Stop Recording'}</span>
            </button>
          </div>
        )}
      </div>
      
      {/* Enhanced Error Display */}
      {(error || uploadErrors.length > 0) && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center space-x-2 mb-2">
            <AlertCircle className="w-5 h-5 text-red-500" />
            <span className="text-red-700 font-medium">
              {error ? 'Recording Error' : 'Upload Errors'}
            </span>
          </div>
          
          {error && (
            <p className="text-red-600 text-sm mb-2">{error}</p>
          )}
          
          {uploadErrors.length > 0 && (
            <div>
              <p className="text-red-600 text-sm mb-1">
                {uploadErrors.length} upload error(s):
              </p>
              <ul className="text-red-600 text-xs space-y-1 max-h-24 overflow-y-auto">
                {uploadErrors.slice(-5).map((err, idx) => (
                  <li key={idx}>• {err}</li>
                ))}
              </ul>
              {uploadErrors.length > 5 && (
                <p className="text-red-500 text-xs mt-1">
                  ... and {uploadErrors.length - 5} more
                </p>
              )}
              <button
                onClick={() => setUploadErrors([])}
                className="mt-2 text-xs text-red-600 hover:text-red-800 underline"
              >
                Clear errors
              </button>
            </div>
          )}
        </div>
      )}

      {/* Advanced Settings (Collapsible) */}
      {status === 'idle' && (
        <div className="mt-4">
          <button
            onClick={() => setShowAdvancedSettings(!showAdvancedSettings)}
            className="w-full flex items-center justify-center space-x-2 p-3 text-slate-600 hover:text-slate-800 transition-colors"
          >
            <span className="text-sm">Advanced Settings</span>
            <div className={`transform transition-transform ${showAdvancedSettings ? 'rotate-180' : ''}`}>
              ▼
            </div>
          </button>
          
          {showAdvancedSettings && (
            <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg space-y-4">
              {/* Upload Queue Method */}
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium text-slate-900 mb-1">Upload Queue</h3>
                  <p className="text-slate-600 text-sm">
                    {useEnhancedUpload 
                      ? 'Enhanced: Retry logic + progress tracking'
                      : 'Legacy: Direct upload (no retry)'
                    }
                  </p>
                </div>
                <button
                  onClick={() => setUseEnhancedUpload(!useEnhancedUpload)}
                  className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                    useEnhancedUpload
                      ? 'bg-teal-600 text-white hover:bg-teal-700'
                      : 'bg-gray-300 text-gray-700 hover:bg-gray-400'
                  }`}
                >
                  {useEnhancedUpload ? 'Enhanced' : 'Legacy'}
                </button>
              </div>

              {/* Storage Method */}
              <div className="flex items-center justify-between border-t pt-4">
                <div>
                  <h3 className="font-medium text-slate-900 mb-1">Storage Method</h3>
                  <p className="text-slate-600 text-sm">
                    {useDirectStorage 
                      ? 'Direct: Upload to Supabase Storage (optimized)'
                      : 'Proxied: Upload through backend server'
                    }
                  </p>
                </div>
                <button
                  onClick={() => setUseDirectStorage(!useDirectStorage)}
                  className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                    useDirectStorage
                      ? 'bg-green-600 text-white hover:bg-green-700'
                      : 'bg-blue-600 text-white hover:bg-blue-700'
                  }`}
                >
                  {useDirectStorage ? 'Direct' : 'Proxied'}
                </button>
              </div>
            </div>
          )}
        </div>
      )}
      
      {/* Simple Instructions */}
      {status === 'idle' && (
        <div className="bg-white rounded-lg p-6 shadow-inner">
          <div className="text-center">
            <h3 className="text-xl font-semibold text-slate-800 mb-4">Ready to Record!</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-slate-600">
              <div className="flex flex-col items-center p-3">
                <div className="bg-blue-100 rounded-full p-2 mb-2">
                  <Play className="w-5 h-5 text-blue-600" />
                </div>
                <p><strong>Step 1:</strong> Click "Start Screen Recording"</p>
              </div>
              <div className="flex flex-col items-center p-3">
                <div className="bg-green-100 rounded-full p-2 mb-2">
                  <Monitor className="w-5 h-5 text-green-600" />
                </div>
                <p><strong>Step 2:</strong> Choose your screen or window</p>
              </div>
              <div className="flex flex-col items-center p-3">
                <div className="bg-purple-100 rounded-full p-2 mb-2">
                  <Square className="w-5 h-5 text-purple-600" />
                </div>
                <p><strong>Step 3:</strong> Click "Stop" when done</p>
              </div>
            </div>
            <p className="text-xs text-slate-500 mt-4">
              Recording optimized for AI analysis • Automatic cloud upload • Privacy protected
            </p>
          </div>
        </div>
      )}
    </div>
  )
}