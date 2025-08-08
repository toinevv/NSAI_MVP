import { useState, useEffect, useCallback, useRef } from 'react'

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

      const response = await fetch(`http://localhost:8000/api/v1/analysis/${recordingId}/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ analysis_type: 'full' })
      })

      if (!response.ok) {
        throw new Error(`Failed to start analysis: ${response.statusText}`)
      }

      const data = await response.json()
      console.log('Analysis started:', data)

      return data.id
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to start analysis'
      setError(errorMessage)
      onError?.(errorMessage)
      return null
    }
  }, [onError])

  const pollAnalysisStatus = useCallback(async (analysisId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/analysis/${analysisId}/status`)
      
      if (!response.ok) {
        throw new Error(`Failed to get analysis status: ${response.statusText}`)
      }

      const status: AnalysisStatus = await response.json()
      setAnalysisStatus(status)

      console.log(`Analysis ${analysisId} status:`, status.status, '-', status.message)

      if (status.status === 'completed') {
        // Analysis is complete, get the full results
        console.log('Analysis completed, fetching results...')
        await getAnalysisResults(analysisId)
        return 'completed'
      } else if (status.status === 'failed') {
        const errorMessage = `Analysis failed: ${status.message}`
        setError(errorMessage)
        onError?.(errorMessage)
        return 'failed'
      }

      return 'processing'
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to check analysis status'
      setError(errorMessage)
      onError?.(errorMessage)
      return 'failed'
    }
  }, [onError])

  const getAnalysisResults = useCallback(async (analysisId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/analysis/${analysisId}/results`)
      
      if (!response.ok) {
        throw new Error(`Failed to get analysis results: ${response.statusText}`)
      }

      const results: AnalysisResult = await response.json()
      setAnalysisResults(results)
      console.log('Analysis results retrieved:', results)
      
      onComplete?.(results)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to get analysis results'
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
      } else {
        // Analysis complete or failed
        setIsPolling(false)
        pollStartTimeRef.current = null
      }
    }

    // Start the polling loop
    pollingTimeoutRef.current = setTimeout(poll, pollingInterval)
  }, [startAnalysis, pollAnalysisStatus, pollingInterval, maxPollingDuration, onError])

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