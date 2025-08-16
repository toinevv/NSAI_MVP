/**
 * AnalyzingPage - Dedicated route for analysis progress
 * Shows immediate loading feedback and handles analysis lifecycle
 */

import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { RefreshCw, AlertCircle, CheckCircle, Brain } from 'lucide-react'
import { apiClient } from '../lib/api-client'

interface AnalysisStatus {
  id: string
  status: string
  phase?: string
  message: string
  confidence_score?: number
  processing_cost?: number
}

export const AnalyzingPage: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>()
  const navigate = useNavigate()
  
  // Simple state for backend-driven job status
  const [analysisId, setAnalysisId] = useState<string | null>(null)
  const [analysisStatus, setAnalysisStatus] = useState<AnalysisStatus | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isPolling, setIsPolling] = useState(false)

  // Start analysis and begin polling
  useEffect(() => {
    if (!sessionId) {
      console.error('❌ No sessionId in URL, redirecting to record page')
      navigate('/')
      return
    }

    console.log('🚀 AnalyzingPage mounted for session:', sessionId)
    startAnalysis()
  }, [sessionId])

  // Start analysis via API call
  const startAnalysis = async () => {
    try {
      console.log('🤖 Starting analysis for session:', sessionId)
      setError(null)
      
      const analysisResponse = await apiClient<AnalysisStatus>(`analysis/${sessionId}/start`, {
        method: 'POST',
        body: JSON.stringify({
          analysis_type: 'natural'
        })
      })

      console.log('✅ Analysis started, analysis_id:', analysisResponse.id)
      
      setAnalysisId(analysisResponse.id)
      setAnalysisStatus(analysisResponse)
      
      // Handle already completed case with minimum display time
      if (analysisResponse.status === 'completed') {
        console.log('🎯 Analysis already completed, showing completion state briefly')
        setTimeout(() => {
          navigate(`/results/${sessionId}`)
        }, 1000) // Minimum display time to prevent jarring navigation
        return
      }
      
      // Start polling for status updates
      startPolling(analysisResponse.id)
      
    } catch (error: any) {
      console.error('❌ Failed to start analysis:', error)
      setError(`Failed to start analysis: ${error.message || error}`)
    }
  }

  // Simple polling function that checks backend job status every 2 seconds
  const startPolling = (analysisId: string) => {
    console.log('🔄 Starting status polling for analysis:', analysisId)
    setIsPolling(true)

    const pollStatus = async () => {
      try {
        const status = await apiClient<AnalysisStatus>(`analysis/${analysisId}/status`)
        console.log('📊 Status update:', status.status, 'phase:', status.phase)
        
        setAnalysisStatus(status)
        
        // Navigate to results when completed
        if (status.status === 'completed') {
          console.log('✅ Analysis completed, navigating to results')
          setIsPolling(false)
          
          // Brief delay to show completion state
          setTimeout(() => {
            navigate(`/results/${sessionId}`)
          }, 1000)
          return
        }
        
        // Handle failures
        if (status.status === 'failed') {
          console.error('❌ Analysis failed:', status.message)
          setError(status.message)
          setIsPolling(false)
          return
        }
        
        // Continue polling if still processing
        if (status.status === 'processing') {
          setTimeout(pollStatus, 2000) // Poll every 2 seconds
        }
        
      } catch (error: any) {
        console.error('❌ Status polling error:', error)
        setError(`Status check failed: ${error.message || error}`)
        setIsPolling(false)
      }
    }

    // Start first poll immediately
    pollStatus()
  }

  // Redirect if no sessionId
  if (!sessionId) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h1 className="text-xl font-semibold text-gray-900 mb-2">No Recording Session</h1>
          <p className="text-gray-600 mb-4">Redirecting to record page...</p>
        </div>
      </div>
    )
  }

  const getStatusIcon = () => {
    if (error) {
      return <AlertCircle className="w-8 h-8 text-red-500" />
    }
    if (analysisStatus?.status === 'completed') {
      return <CheckCircle className="w-8 h-8 text-green-500" />
    }
    return <RefreshCw className="w-8 h-8 text-blue-500 animate-spin" />
  }

  const getStatusMessage = () => {
    if (error) {
      return error
    }
    if (analysisStatus?.message) {
      return analysisStatus.message
    }
    return '🚀 Initializing AI analysis...'
  }

  const getCurrentPhase = () => {
    // For now, derive phase from status since phase column doesn't exist yet
    if (analysisStatus?.status === 'completed') return 'completed'
    if (analysisStatus?.status === 'failed') return 'failed'
    return 'processing'  // Default to processing for active analysis
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-teal-400 rounded-lg flex items-center justify-center">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-slate-800">NewSystem.AI</h1>
                <p className="text-xs text-gray-600">AI Workflow Analysis in Progress</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-slate-800 mb-4">
            AI Analysis in Progress
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Our GPT-4V engine is analyzing your workflow recording to identify automation opportunities. 
            This typically takes 30-60 seconds.
          </p>
        </div>

        {/* Analysis Status */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 mb-8 text-center">
          <div className="flex justify-center mb-6">
            <div className="p-4 bg-blue-100 rounded-full">
              {getStatusIcon()}
            </div>
          </div>
          
          <h3 className="text-xl font-semibold text-gray-900 mb-4">
            {getStatusMessage()}
          </h3>

          {/* Error Handling */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
              <div className="flex items-start space-x-3">
                <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <p className="text-red-700 mb-3">{error}</p>
                  
                  <div className="flex flex-wrap gap-2">
                    <button
                      onClick={() => {
                        console.log('🔄 Retrying analysis for session:', sessionId)
                        startAnalysis()
                      }}
                      className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                    >
                      Retry Analysis
                    </button>
                    <button
                      onClick={() => navigate('/')}
                      className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                    >
                      Back to Recording
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Simple Progress Indicators - will enhance with phases later */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
            <div className="flex flex-col items-center">
              <div className={`w-3 h-3 rounded-full mb-2 transition-colors ${
                isPolling ? 'bg-blue-500' : 'bg-gray-300'
              }`}></div>
              <p className="text-sm text-gray-600">Extracting frames</p>
            </div>
            <div className="flex flex-col items-center">
              <div className={`w-3 h-3 rounded-full mb-2 transition-colors ${
                isPolling ? 'bg-blue-500 animate-pulse' : 'bg-gray-300'
              }`}></div>
              <p className="text-sm text-gray-600">AI pattern analysis</p>
            </div>
            <div className="flex flex-col items-center">
              <div className={`w-3 h-3 rounded-full mb-2 transition-colors ${
                analysisStatus?.status === 'completed' ? 'bg-green-500' : 'bg-gray-300'
              }`}></div>
              <p className="text-sm text-gray-600">Generating insights</p>
            </div>
          </div>

          <p className="text-sm text-gray-500 mt-6">
            Session ID: {sessionId}
          </p>
        </div>

        {/* Analysis Details */}
        <div className="bg-blue-50 rounded-lg border border-blue-200 p-6">
          <h4 className="font-semibold text-blue-900 mb-3">What's happening now?</h4>
          <div className="space-y-2 text-sm text-blue-800">
            <p>• GPT-4V is examining each frame of your workflow recording</p>
            <p>• Identifying repetitive patterns and manual tasks</p>
            <p>• Calculating time savings and automation opportunities</p>
            <p>• Generating actionable insights and recommendations</p>
          </div>
        </div>
      </main>
    </div>
  )
}