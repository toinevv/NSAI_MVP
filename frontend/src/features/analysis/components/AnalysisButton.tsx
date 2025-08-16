/**
 * Analysis Button Component
 * Triggers GPT-4V analysis pipeline for recorded workflows
 * Phase 2A: Frame extraction testing
 */

import React, { useState } from 'react'
import { Brain, Loader2, AlertCircle, CheckCircle, Image, Settings } from 'lucide-react'
import { useSettings } from '../../../contexts/SettingsContext'
import { apiClient } from '../../../lib/api-client'

interface FrameExtractionSettings {
  fps: number
  max_frames: number
  scene_threshold: number
  preset?: string
}

interface AnalysisButtonProps {
  recordingId: string
  onAnalysisComplete?: (analysisId: string) => void
  className?: string
  videoDuration?: number // Pass video duration for settings calculations
  onNavigateToSettings?: () => void // Navigate to settings tab
}

export const AnalysisButton: React.FC<AnalysisButtonProps> = ({
  recordingId,
  onAnalysisComplete,
  className = '',
  videoDuration = 100,
  onNavigateToSettings
}) => {
  // Use global settings instead of local hardcoded values
  const { settings, getEstimatedFrames, getEstimatedCost } = useSettings()
  
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [status, setStatus] = useState<'idle' | 'extracting' | 'analyzing' | 'completed' | 'error'>('idle')
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const startAnalysis = async (analysisType = 'full') => {
    setIsAnalyzing(true)
    setStatus('analyzing')
    setError(null)
    setResult(null)

    try {
      const response = await apiClient.post(
        `/api/v1/analysis/${recordingId}/start`,
        {
          analysis_type: analysisType,
          frame_extraction_settings: settings.frameExtraction
        }
      )

      if (response.data) {
        setResult(response.data)
        setStatus('completed')
        
        if (response.data.id && onAnalysisComplete) {
          onAnalysisComplete(response.data.id)
        }
        
        console.log('Analysis result:', response.data)
      }
    } catch (err: any) {
      console.error('Analysis failed:', err)
      setStatus('error')
      setError(err.response?.data?.detail || err.message || 'Analysis failed')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const getStatusIcon = () => {
    switch (status) {
      case 'extracting':
        return <Loader2 className="w-5 h-5 animate-spin text-blue-500" />
      case 'analyzing':
        return <Loader2 className="w-5 h-5 animate-spin text-purple-500" />
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-500" />
      default:
        return <Brain className="w-5 h-5" />
    }
  }

  const getStatusMessage = () => {
    switch (status) {
      case 'extracting':
        return 'Extracting key frames from recording...'
      case 'analyzing':
        return 'GPT-4V is analyzing your workflow for automation opportunities...'
      case 'completed':
        return result?.message || 'Analysis completed - automation opportunities identified!'
      case 'error':
        return error || 'Analysis failed'
      default:
        return 'Ready to identify automation opportunities in your workflow'
    }
  }

  return (
    <div className={`bg-white rounded-lg shadow-lg border border-gray-200 p-6 ${className}`}>
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">
            AI Workflow Analysis
          </h3>
          <div className="flex items-center space-x-2">
            {getStatusIcon()}
            <span className={`text-sm ${
              status === 'error' ? 'text-red-600' : 
              status === 'completed' ? 'text-green-600' : 
              'text-gray-600'
            }`}>
              {status === 'idle' ? 'Ready' : status.charAt(0).toUpperCase() + status.slice(1)}
            </span>
          </div>
        </div>

        {/* Settings Link */}
        {status === 'idle' && onNavigateToSettings && (
          <div className="bg-blue-50 rounded-lg p-3 border border-blue-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Settings className="w-4 h-4 text-blue-600" />
                <span className="text-sm text-blue-800">
                  Using {settings.frameExtraction.fps} FPS extraction (~{getEstimatedFrames(videoDuration)} frames, ${getEstimatedCost(videoDuration).toFixed(2)})
                </span>
              </div>
              <button
                onClick={onNavigateToSettings}
                className="text-xs bg-blue-100 hover:bg-blue-200 text-blue-800 px-2 py-1 rounded transition-colors"
              >
                Configure
              </button>
            </div>
          </div>
        )}

        {/* Status Message */}
        <div className="bg-gray-50 rounded-lg p-3">
          <p className="text-sm text-gray-700">{getStatusMessage()}</p>
        </div>

        {/* Results (if available) */}
        {result && status === 'completed' && (
          <div className="bg-blue-50 rounded-lg p-4 space-y-2">
            <h4 className="font-medium text-blue-900">Analysis Results</h4>
            
            {result.frame_count !== undefined && (
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-blue-600">Frames Extracted:</span>
                  <span className="ml-2 font-medium">{result.frame_count}</span>
                </div>
                <div>
                  <span className="text-blue-600">Estimated Cost:</span>
                  <span className="ml-2 font-medium">
                    ${result.estimated_gpt4v_cost?.toFixed(2) || '0.00'}
                  </span>
                </div>
              </div>
            )}
            
            {result.extraction_strategy && (
              <div className="mt-2 text-xs text-blue-700">
                <p>Strategy: {result.extraction_strategy.method}</p>
                <p>Interval: Every {result.extraction_strategy.interval_seconds}s</p>
                <p>Target: {result.extraction_strategy.target_frames} frames</p>
              </div>
            )}
            
            {result.id && (
              <div className="mt-3 pt-3 border-t border-blue-200">
                <p className="text-xs text-blue-600">
                  Analysis ID: {result.id}
                </p>
              </div>
            )}
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex space-x-3">
          {/* Full Analysis - NOW ENABLED! */}
          <button
            onClick={() => startAnalysis('full')}
            disabled={isAnalyzing || !recordingId}
            className={`
              flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all
              ${isAnalyzing || !recordingId
                ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                : 'bg-purple-600 hover:bg-purple-700 text-white hover:shadow-md'
              }
            `}
            title="Full GPT-4V workflow analysis"
          >
            <Brain className="w-4 h-4" />
            <span>Full Analysis</span>
          </button>

          {/* Quick Analysis */}
          <button
            onClick={() => startAnalysis('quick')}
            disabled={isAnalyzing || !recordingId}
            className={`
              flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all
              ${isAnalyzing || !recordingId
                ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700 text-white hover:shadow-md'
              }
            `}
            title="Quick analysis with fewer frames"
          >
            <Image className="w-4 h-4" />
            <span>Quick Analysis</span>
          </button>
        </div>

        {/* Analysis Options */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
          <div className="flex items-start space-x-2">
            <Brain className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
            <div className="text-xs text-blue-800">
              <p className="font-medium mb-1">Analysis Options</p>
              <p>
                <strong>Full Analysis:</strong> Complete GPT-4V workflow analysis (may take 30-60 seconds)
              </p>
              <p className="mt-1">
                <strong>Quick Analysis:</strong> Faster processing with fewer frames (15-30 seconds)
              </p>
              <p className="mt-2 text-blue-600">
                ⚠️ Actual analysis results will be displayed - no mock data
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}