import { useState, useEffect, useCallback, useRef } from 'react'
import { analysisAPI, getAnalysisErrorMessage } from '../services/analysisAPI'

interface AnalysisStatus {
  id: string
  status: 'processing' | 'completed' | 'failed'
  message: string
  confidence_score?: number
  processing_cost?: number
}

interface AnalysisResult {
  analysis_id: string
  status: string
  message: string
  results: {
    session_id: string
    status: string
    recording_info: {
      title: string
      duration_seconds: number
      created_at: string
    }
    analysis_info: {
      frames_analyzed: number
      confidence_score: number
      processing_time_seconds: number
      analysis_cost: number
    }
    summary: {
      total_time_analyzed: number
      automation_opportunities: number
      estimated_time_savings: number
      confidence_score: number
      annual_cost_savings: number
    }
    workflows: any[]
    automation_opportunities: any[]
    time_analysis: any
    insights: any[]
  } | null
}

interface UseAnalysisPollingOptions {
  pollingInterval?: number
  maxPollingDuration?: number
  onComplete?: (results: AnalysisResult) => void
  onError?: (error: string) => void
}

export const useAnalysisPolling = (options: UseAnalysisPollingOptions = {}) => {
  const {
    pollingInterval = 3000, // 3 seconds
    maxPollingDuration = 300000, // 5 minutes
    onComplete,
    onError
  } = options

  const [analysisStatus, setAnalysisStatus] = useState<AnalysisStatus | null>(null)
  const [analysisResults, setAnalysisResults] = useState<AnalysisResult | null>(null)
  const [isPolling, setIsPolling] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const pollingTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const pollStartTimeRef = useRef<number | null>(null)

  const startAnalysis = useCallback(async (recordingId: string): Promise<string | null> => {
    try {
      setError(null)
      console.log(`Starting analysis for recording ${recordingId}`)

      const data = await analysisAPI.startAnalysis(recordingId, { analysis_type: 'full' })
      console.log('Analysis started:', data)

      return data.id
    } catch (err) {
      const errorMessage = getAnalysisErrorMessage(err)
      setError(errorMessage)
      onError?.(errorMessage)
      return null
    }
  }, [onError])

  const pollAnalysisStatus = useCallback(async (analysisId: string) => {
    try {
      const statusResponse = await analysisAPI.getAnalysisStatus(analysisId)
      
      const status: AnalysisStatus = {
        id: statusResponse.id,
        status: statusResponse.status as 'processing' | 'completed' | 'failed',
        message: `Analysis ${statusResponse.status} - ${statusResponse.current_stage}`,
        confidence_score: statusResponse.progress_percentage / 100,
        processing_cost: 0
      }
      
      setAnalysisStatus(status)

      console.log(`Analysis ${analysisId} status:`, status.status, '-', status.message)

      if (status.status === 'completed') {
        // Analysis is complete, get the full results
        console.log('Analysis completed, fetching results...')
        await getAnalysisResults(analysisId)
        return 'completed'
      } else if (status.status === 'failed') {
        const errorMessage = statusResponse.error_message || 'Analysis failed'
        setError(errorMessage)
        onError?.(errorMessage)
        return 'failed'
      }

      return 'processing'
    } catch (err) {
      const errorMessage = getAnalysisErrorMessage(err)
      setError(errorMessage)
      onError?.(errorMessage)
      return 'failed'
    }
  }, [onError])

  const getAnalysisResults = useCallback(async (sessionId: string) => {
    try {
      const resultsResponse = await analysisAPI.getResults(sessionId)
      
      const results: AnalysisResult = {
        analysis_id: sessionId,
        status: 'completed',
        message: resultsResponse.message,
        results: resultsResponse.results
      }
      
      setAnalysisResults(results)
      console.log('Analysis results retrieved:', results)
      
      onComplete?.(results)
    } catch (err) {
      const errorMessage = getAnalysisErrorMessage(err)
      setError(errorMessage)
      onError?.(errorMessage)
    }
  }, [onComplete, onError])

  const startPolling = useCallback(async (recordingId: string) => {
    // Start the analysis
    const analysisId = await startAnalysis(recordingId)
    if (!analysisId) {
      return
    }

    setIsPolling(true)
    setAnalysisStatus({
      id: analysisId,
      status: 'processing',
      message: 'Analysis started - processing your workflow...'
    })
    
    pollStartTimeRef.current = Date.now()

    const poll = async () => {
      // Check if we've exceeded maximum polling duration
      if (pollStartTimeRef.current && Date.now() - pollStartTimeRef.current > maxPollingDuration) {
        setIsPolling(false)
        const errorMessage = 'Analysis timeout - taking longer than expected'
        setError(errorMessage)
        onError?.(errorMessage)
        return
      }

      const status = await pollAnalysisStatus(analysisId)

      if (status === 'processing') {
        // Continue polling
        pollingTimeoutRef.current = setTimeout(poll, pollingInterval)
      } else if (status === 'completed') {
        // Analysis complete - get results using the recordingId (sessionId)
        await getAnalysisResults(recordingId)
        setIsPolling(false)
        pollStartTimeRef.current = null
      } else {
        // Analysis failed
        setIsPolling(false)
        pollStartTimeRef.current = null
      }
    }

    // Start the polling loop
    pollingTimeoutRef.current = setTimeout(poll, pollingInterval)
  }, [startAnalysis, pollAnalysisStatus, getAnalysisResults, pollingInterval, maxPollingDuration, onError])

  const stopPolling = useCallback(() => {
    if (pollingTimeoutRef.current) {
      clearTimeout(pollingTimeoutRef.current)
      pollingTimeoutRef.current = null
    }
    setIsPolling(false)
    pollStartTimeRef.current = null
  }, [])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopPolling()
    }
  }, [stopPolling])

  return {
    // State
    analysisStatus,
    analysisResults,
    isPolling,
    error,

    // Actions
    startPolling,
    stopPolling,

    // Utilities
    isAnalysisComplete: analysisStatus?.status === 'completed',
    isAnalysisFailed: analysisStatus?.status === 'failed',
    isAnalysisProcessing: analysisStatus?.status === 'processing'
  }
}