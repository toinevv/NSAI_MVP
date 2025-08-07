/**
 * Analysis Results Component
 * Displays GPT-4V analysis results with automation opportunities
 * Phase 2A: Complete results visualization
 */

import React, { useEffect, useState } from 'react'
import { 
  Brain, 
  Clock, 
  DollarSign, 
  TrendingUp, 
  Package,
  Mail,
  Database,
  AlertCircle,
  CheckCircle,
  ChevronRight,
  Download,
  Share2,
  ChevronDown,
  Code,
  Zap
} from 'lucide-react'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface AnalysisResultsProps {
  analysisId: string
  onClose?: () => void
  className?: string
}

interface WorkflowData {
  type: string
  description: string
  applications: string[]
  steps: string[]
  duration_seconds: number
  is_email_to_wms: boolean
}

interface OpportunityData {
  workflow_type: string
  description: string
  frequency_daily: number
  time_per_occurrence_minutes: number
  time_saved_daily_minutes: number
  time_saved_weekly_hours: number
  time_saved_annually_hours: number
  cost_saved_annually: number
  automation_potential: string
  implementation_complexity: string
  recommendation: string
  priority_score: number
}

interface ResultsData {
  workflows: WorkflowData[]
  automation_opportunities: OpportunityData[]
  summary: {
    total_workflows_detected: number
    email_to_wms_workflows: number
    total_opportunities: number
    time_savings_daily_minutes: number
    time_savings_weekly_hours: number
    cost_savings_annual_usd: number
    roi_multiplier: number
  }
  raw_gpt_response?: any  // Raw GPT-4V response for verification
  time_analysis: {
    total_seconds: number
    email_percentage?: number
    wms_percentage?: number
    productive_percentage?: number
  }
  insights: string[]
  confidence_score: number
  analysis_cost: number
}

export const AnalysisResults: React.FC<AnalysisResultsProps> = ({
  analysisId,
  onClose,
  className = ''
}) => {
  const [loading, setLoading] = useState(true)
  const [results, setResults] = useState<ResultsData | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [status, setStatus] = useState<string>('loading')
  const [showRawResponse, setShowRawResponse] = useState(false)

  useEffect(() => {
    if (analysisId) {
      pollForResults()
    }
  }, [analysisId])

  const pollForResults = async () => {
    let attempts = 0
    const maxAttempts = 30 // 30 attempts * 2 seconds = 60 seconds max

    const poll = async () => {
      try {
        // Check status first
        const statusResponse = await axios.get(
          `${API_BASE_URL}/api/v1/analysis/${analysisId}/status`
        )

        setStatus(statusResponse.data.status)

        if (statusResponse.data.status === 'completed') {
          // Get full results
          const resultsResponse = await axios.get(
            `${API_BASE_URL}/api/v1/analysis/${analysisId}/results`
          )

          if (resultsResponse.data.results) {
            setResults(resultsResponse.data.results)
            setLoading(false)
          }
        } else if (statusResponse.data.status === 'failed') {
          setError(statusResponse.data.message || 'Analysis failed')
          setLoading(false)
        } else if (attempts < maxAttempts) {
          // Continue polling
          attempts++
          setTimeout(poll, 2000) // Poll every 2 seconds
        } else {
          setError('Analysis timed out')
          setLoading(false)
        }
      } catch (err: any) {
        console.error('Failed to get results:', err)
        setError(err.response?.data?.detail || 'Failed to load results')
        setLoading(false)
      }
    }

    poll()
  }

  const getPotentialBadge = (potential: string) => {
    const colors = {
      high: 'bg-green-100 text-green-800',
      medium: 'bg-yellow-100 text-yellow-800',
      low: 'bg-gray-100 text-gray-800'
    }
    return colors[potential.toLowerCase() as keyof typeof colors] || colors.low
  }

  const getComplexityBadge = (complexity: string) => {
    const colors = {
      low: 'bg-blue-100 text-blue-800',
      medium: 'bg-orange-100 text-orange-800',
      high: 'bg-red-100 text-red-800'
    }
    return colors[complexity.toLowerCase() as keyof typeof colors] || colors.medium
  }

  if (loading) {
    return (
      <div className={`bg-white rounded-lg shadow-lg p-8 ${className}`}>
        <div className="flex flex-col items-center justify-center space-y-4">
          <Brain className="w-12 h-12 text-purple-600 animate-pulse" />
          <h3 className="text-lg font-semibold text-gray-900">
            Analyzing Workflow...
          </h3>
          <p className="text-sm text-gray-600">
            GPT-4V is identifying automation opportunities
          </p>
          <div className="w-full max-w-xs bg-gray-200 rounded-full h-2">
            <div className="bg-purple-600 h-2 rounded-full animate-pulse" style={{ width: '60%' }}></div>
          </div>
          <p className="text-xs text-gray-500">
            Status: {status}
          </p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className={`bg-white rounded-lg shadow-lg p-8 ${className}`}>
        <div className="flex flex-col items-center justify-center space-y-4">
          <AlertCircle className="w-12 h-12 text-red-500" />
          <h3 className="text-lg font-semibold text-gray-900">
            Analysis Error
          </h3>
          <p className="text-sm text-gray-600">{error}</p>
          {onClose && (
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
            >
              Close
            </button>
          )}
        </div>
      </div>
    )
  }

  if (!results) {
    return null
  }

  return (
    <div className={`bg-white rounded-lg shadow-lg ${className}`}>
      {/* Header */}
      <div className="border-b border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <CheckCircle className="w-8 h-8 text-green-500" />
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                Analysis Complete
              </h2>
              <p className="text-sm text-gray-600">
                {results.summary.total_opportunities} automation opportunities identified
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button className="p-2 text-gray-600 hover:text-gray-900">
              <Download className="w-5 h-5" />
            </button>
            <button className="p-2 text-gray-600 hover:text-gray-900">
              <Share2 className="w-5 h-5" />
            </button>
            {onClose && (
              <button
                onClick={onClose}
                className="ml-2 px-4 py-2 text-gray-600 hover:text-gray-900"
              >
                ✕
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 p-6">
        <div className="bg-blue-50 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-blue-600">Time Savings</p>
              <p className="text-2xl font-bold text-blue-900">
                {results.summary.time_savings_weekly_hours.toFixed(1)}h
              </p>
              <p className="text-xs text-blue-700">per week</p>
            </div>
            <Clock className="w-8 h-8 text-blue-400" />
          </div>
        </div>

        <div className="bg-green-50 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-green-600">Annual Savings</p>
              <p className="text-2xl font-bold text-green-900">
                ${results.summary.cost_savings_annual_usd.toLocaleString()}
              </p>
              <p className="text-xs text-green-700">per year</p>
            </div>
            <DollarSign className="w-8 h-8 text-green-400" />
          </div>
        </div>

        <div className="bg-purple-50 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-purple-600">ROI Multiple</p>
              <p className="text-2xl font-bold text-purple-900">
                {results.summary.roi_multiplier.toFixed(1)}x
              </p>
              <p className="text-xs text-purple-700">return</p>
            </div>
            <TrendingUp className="w-8 h-8 text-purple-400" />
          </div>
        </div>

        <div className="bg-orange-50 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-orange-600">Workflows</p>
              <p className="text-2xl font-bold text-orange-900">
                {results.summary.email_to_wms_workflows}
              </p>
              <p className="text-xs text-orange-700">email → WMS</p>
            </div>
            <Mail className="w-8 h-8 text-orange-400" />
          </div>
        </div>
      </div>

      {/* Automation Opportunities */}
      <div className="p-6 border-t border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          🎯 Automation Opportunities
        </h3>
        <div className="space-y-4">
          {results.automation_opportunities.map((opp, idx) => (
            <div key={idx} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    {opp.workflow_type === 'email_to_wms' && (
                      <div className="flex items-center space-x-1">
                        <Mail className="w-4 h-4 text-blue-600" />
                        <ChevronRight className="w-3 h-3 text-gray-400" />
                        <Database className="w-4 h-4 text-green-600" />
                      </div>
                    )}
                    <h4 className="font-medium text-gray-900">
                      {opp.description}
                    </h4>
                  </div>

                  <div className="flex flex-wrap gap-2 mb-3">
                    <span className={`px-2 py-1 text-xs rounded-full ${getPotentialBadge(opp.automation_potential)}`}>
                      {opp.automation_potential} potential
                    </span>
                    <span className={`px-2 py-1 text-xs rounded-full ${getComplexityBadge(opp.implementation_complexity)}`}>
                      {opp.implementation_complexity} complexity
                    </span>
                    <span className="px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-700">
                      {opp.frequency_daily}x daily
                    </span>
                  </div>

                  <p className="text-sm text-gray-600 mb-2">
                    {opp.recommendation}
                  </p>

                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500">Time saved:</span>
                      <span className="ml-1 font-medium">{opp.time_saved_daily_minutes} min/day</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Weekly:</span>
                      <span className="ml-1 font-medium">{opp.time_saved_weekly_hours.toFixed(1)} hours</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Annual value:</span>
                      <span className="ml-1 font-medium text-green-600">
                        ${opp.cost_saved_annually.toLocaleString()}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="ml-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-600">
                      {opp.priority_score.toFixed(0)}
                    </div>
                    <div className="text-xs text-gray-500">Priority</div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Insights */}
      {results.insights && results.insights.length > 0 && (
        <div className="p-6 border-t border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            💡 Key Insights
          </h3>
          <ul className="space-y-2">
            {results.insights.map((insight, idx) => (
              <li key={idx} className="flex items-start space-x-2">
                <Zap className="w-4 h-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                <span className="text-sm text-gray-700">{insight}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Time Analysis */}
      {results.time_analysis && (
        <div className="p-6 border-t border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            ⏱️ Time Breakdown
          </h3>
          <div className="space-y-3">
            {results.time_analysis.email_percentage !== undefined && (
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Email</span>
                  <span>{results.time_analysis.email_percentage}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full" 
                    style={{ width: `${results.time_analysis.email_percentage}%` }}
                  ></div>
                </div>
              </div>
            )}
            {results.time_analysis.wms_percentage !== undefined && (
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>WMS</span>
                  <span>{results.time_analysis.wms_percentage}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-green-600 h-2 rounded-full" 
                    style={{ width: `${results.time_analysis.wms_percentage}%` }}
                  ></div>
                </div>
              </div>
            )}
            {results.time_analysis.productive_percentage !== undefined && (
              <div className="mt-2 text-sm text-gray-600">
                Productive time: {results.time_analysis.productive_percentage}%
              </div>
            )}
          </div>
        </div>
      )}

      {/* Raw GPT-4V Response Section */}
      {results.raw_gpt_response && (
        <div className="px-6 py-4 border-t">
          <button
            onClick={() => setShowRawResponse(!showRawResponse)}
            className="flex items-center space-x-2 text-sm font-medium text-gray-700 hover:text-gray-900 transition-colors"
          >
            <Code className="w-4 h-4" />
            <span>View Raw GPT-4V Analysis</span>
            <ChevronDown 
              className={`w-4 h-4 transform transition-transform ${showRawResponse ? 'rotate-180' : ''}`}
            />
          </button>
          
          {showRawResponse && (
            <div className="mt-4 p-4 bg-gray-100 rounded-lg overflow-auto max-h-96">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-medium text-gray-600">
                  Raw GPT-4V Response (for verification)
                </span>
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(JSON.stringify(results.raw_gpt_response, null, 2))
                  }}
                  className="text-xs text-blue-600 hover:text-blue-800"
                >
                  Copy JSON
                </button>
              </div>
              <pre className="text-xs text-gray-700 whitespace-pre-wrap font-mono">
                {JSON.stringify(results.raw_gpt_response, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}

      {/* Footer */}
      <div className="bg-gray-50 px-6 py-4 rounded-b-lg">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <div>
            Confidence: {(results.confidence_score * 100).toFixed(0)}%
          </div>
          <div>
            Analysis cost: ${results.analysis_cost.toFixed(2)}
          </div>
        </div>
      </div>
    </div>
  )
}