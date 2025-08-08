import React, { useEffect, useState } from 'react'
import { CheckCircle, Clock, AlertCircle, Brain, Zap, TrendingUp, DollarSign, ArrowLeft, RefreshCw } from 'lucide-react'
import { resultsAPI, type ResultsApiResponse, getResultsErrorMessage } from '../../results/services/resultsAPI'

interface ResultsPageProps {
  sessionId: string
  onBack: () => void
}

export const ResultsPage: React.FC<ResultsPageProps> = ({ sessionId, onBack }) => {
  const [apiResponse, setApiResponse] = useState<ResultsApiResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchResults = async () => {
    try {
      setLoading(true)
      setError(null)

      const data = await resultsAPI.getResults(sessionId)
      setApiResponse(data)
    } catch (err) {
      const errorMessage = getResultsErrorMessage(err)
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchResults()
  }, [sessionId])

  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 text-teal-600 animate-spin mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Loading Results...</h2>
          <p className="text-gray-600">Retrieving your workflow analysis</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-8 h-8 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Results</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <div className="space-x-4">
            <button
              onClick={fetchResults}
              className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors"
            >
              Retry
            </button>
            <button
              onClick={onBack}
              className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors"
            >
              Go Back
            </button>
          </div>
        </div>
      </div>
    )
  }

  if (!apiResponse || !apiResponse.results) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-8 h-8 text-gray-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">No Results Found</h2>
          <p className="text-gray-600 mb-4">Analysis results are not available for this session</p>
          <button
            onClick={onBack}
            className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors"
          >
            Go Back
          </button>
        </div>
      </div>
    )
  }

  const { results: analysisResults } = apiResponse
  const { recording_info, analysis_info, summary, automation_opportunities, insights } = analysisResults

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <button
                onClick={onBack}
                className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors"
              >
                <ArrowLeft className="w-5 h-5" />
                <span>Back</span>
              </button>
              <div>
                <h1 className="text-xl font-bold text-slate-800">Analysis Results</h1>
                <p className="text-sm text-gray-600">{recording_info.title}</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircle className="w-5 h-5 text-green-500" />
              <span className="text-sm text-gray-600">Analysis Complete</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="p-2 bg-teal-100 rounded-lg">
                <Clock className="w-6 h-6 text-teal-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Recording Duration</p>
                <p className="text-2xl font-bold text-gray-900">
                  {formatDuration(recording_info.duration_seconds)}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Brain className="w-6 h-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Frames Analyzed</p>
                <p className="text-2xl font-bold text-gray-900">
                  {analysis_info.frames_analyzed || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="p-2 bg-amber-100 rounded-lg">
                <Zap className="w-6 h-6 text-amber-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Opportunities Found</p>
                <p className="text-2xl font-bold text-gray-900">
                  {summary.automation_opportunities}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <TrendingUp className="w-6 h-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Weekly Time Savings</p>
                <p className="text-2xl font-bold text-gray-900">
                  {summary.estimated_time_savings.toFixed(1)}h
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* ROI Summary */}
        <div className="bg-gradient-to-r from-green-50 to-teal-50 rounded-lg border border-green-200 p-8 mb-8">
          <div className="text-center">
            <div className="flex justify-center mb-4">
              <div className="p-3 bg-green-100 rounded-full">
                <DollarSign className="w-8 h-8 text-green-600" />
              </div>
            </div>
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
              {formatCurrency(summary.annual_cost_savings)}
            </h2>
            <p className="text-lg text-gray-700 mb-4">Estimated Annual Savings</p>
            <div className="flex items-center justify-center space-x-6 text-sm">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span className="text-gray-600">
                  {summary.estimated_time_savings.toFixed(1)} hours/week saved
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                <span className="text-gray-600">
                  {(summary.confidence_score * 100).toFixed(0)}% confidence
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Analysis Results */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Automation Opportunities */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Automation Opportunities</h3>
              <p className="text-sm text-gray-600">AI-identified areas for workflow optimization</p>
            </div>
            <div className="p-6">
              {automation_opportunities.length > 0 ? (
                <div className="space-y-4">
                  {automation_opportunities.slice(0, 3).map((opp: any, index: number) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="font-medium text-gray-900">
                          {opp.workflow_type || 'Workflow Optimization'}
                        </h4>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          opp.priority === 'high' 
                            ? 'bg-red-100 text-red-800'
                            : opp.priority === 'medium'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-green-100 text-green-800'
                        }`}>
                          {opp.priority || 'medium'}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mb-3">
                        {opp.description || 'Automation opportunity identified through workflow analysis'}
                      </p>
                      <div className="flex justify-between text-xs text-gray-500">
                        <span>
                          💰 ROI Score: {(opp.roi_score || 0).toFixed(1)}
                        </span>
                        <span>
                          ⏱️ {(opp.time_saved_weekly_hours || 0).toFixed(1)}h/week
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <Zap className="w-8 h-8 mx-auto mb-2 text-gray-400" />
                  <p>No specific automation opportunities identified</p>
                  <p className="text-sm">The analysis will improve with more workflow data</p>
                </div>
              )}
            </div>
          </div>

          {/* Insights */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">AI Insights</h3>
              <p className="text-sm text-gray-600">Key observations from workflow analysis</p>
            </div>
            <div className="p-6">
              {insights.length > 0 ? (
                <div className="space-y-4">
                  {insights.slice(0, 5).map((insight: any, index: number) => (
                    <div key={index} className="flex items-start space-x-3">
                      <div className="w-2 h-2 bg-teal-500 rounded-full mt-2 flex-shrink-0"></div>
                      <p className="text-sm text-gray-700">
                        {typeof insight === 'string' ? insight : insight.description || 'Workflow insight identified'}
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <Brain className="w-8 h-8 mx-auto mb-2 text-gray-400" />
                  <p>Insights are being processed</p>
                  <p className="text-sm">Check back soon for detailed workflow analysis</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Analysis Metadata */}
        <div className="mt-8 bg-gray-100 rounded-lg p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div>
              <span className="text-gray-600">Analysis Cost:</span>
              <span className="ml-2 font-medium">${(analysis_info.analysis_cost || 0).toFixed(2)}</span>
            </div>
            <div>
              <span className="text-gray-600">Processing Time:</span>
              <span className="ml-2 font-medium">{analysis_info.processing_time_seconds || 0}s</span>
            </div>
            <div>
              <span className="text-gray-600">Confidence Score:</span>
              <span className="ml-2 font-medium">{(analysis_info.confidence_score * 100).toFixed(0)}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}