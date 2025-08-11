import React, { useEffect, useState } from 'react'
import { CheckCircle, Clock, AlertCircle, Brain, Zap, DollarSign, ArrowLeft, RefreshCw, TrendingUp } from 'lucide-react'
import { resultsAPI, type ResultsApiResponse, getResultsErrorMessage } from '../../results/services/resultsAPI'

interface MinimalResultsPageProps {
  sessionId: string
  onBack: () => void
}

export const MinimalResultsPage: React.FC<MinimalResultsPageProps> = ({ sessionId, onBack }) => {
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
        <div className="text-center max-w-md mx-auto">
          <AlertCircle className="w-8 h-8 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Analysis Error</h2>
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
              Back
            </button>
          </div>
        </div>
      </div>
    )
  }

  if (!apiResponse || !apiResponse.results) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md mx-auto">
          <AlertCircle className="w-8 h-8 text-gray-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">No Results Available</h2>
          <p className="text-gray-600 mb-4">Analysis results are not yet available for this session</p>
          <button
            onClick={onBack}
            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            Back to Recordings
          </button>
        </div>
      </div>
    )
  }

  const { results: analysisResults } = apiResponse
  const { recording_info, analysis_info, summary, automation_opportunities, insights } = analysisResults

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Simple Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
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
                <h1 className="text-lg font-bold text-slate-800">Workflow Analysis</h1>
                <p className="text-sm text-gray-500">{formatDuration(recording_info.duration_seconds)} recording</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircle className="w-4 h-4 text-green-500" />
              <span className="text-sm text-gray-600">Complete</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* ROI Summary - Primary Focus */}
        <div className="bg-gradient-to-r from-green-50 to-teal-50 rounded-xl border border-green-200 p-8 mb-8 text-center">
          <div className="flex justify-center mb-4">
            <div className="p-3 bg-green-100 rounded-full">
              <DollarSign className="w-8 h-8 text-green-600" />
            </div>
          </div>
          <h2 className="text-4xl font-bold text-gray-900 mb-2">
            {formatCurrency(summary.annual_cost_savings)}
          </h2>
          <p className="text-xl text-gray-700 mb-6">Potential Annual Savings</p>
          
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <div className="text-2xl font-bold text-teal-600 mb-1">
                {summary.estimated_time_savings.toFixed(1)}h
              </div>
              <div className="text-sm text-gray-600">Hours saved per week</div>
            </div>
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <div className="text-2xl font-bold text-amber-600 mb-1">
                {summary.automation_opportunities}
              </div>
              <div className="text-sm text-gray-600">Automation opportunities</div>
            </div>
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <div className="text-2xl font-bold text-blue-600 mb-1">
                {(analysis_info.confidence_score * 100).toFixed(0)}%
              </div>
              <div className="text-sm text-gray-600">Analysis confidence</div>
            </div>
          </div>
        </div>

        {/* Key Insights - Simplified */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 mb-8">
          <div className="flex items-center space-x-2 mb-6">
            <Brain className="w-6 h-6 text-blue-600" />
            <h3 className="text-xl font-semibold text-gray-900">Key Findings</h3>
          </div>
          
          {insights.length > 0 ? (
            <div className="space-y-4">
              {insights.slice(0, 3).map((insight: any, index: number) => (
                <div key={index} className="flex items-start space-x-3 p-4 bg-blue-50 rounded-lg">
                  <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-blue-600 text-sm font-bold">{index + 1}</span>
                  </div>
                  <p className="text-gray-800 leading-relaxed">
                    {typeof insight === 'string' ? insight : insight.description || 'Workflow insight identified'}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">
              <Brain className="w-12 h-12 mx-auto mb-4 text-gray-400" />
              <p className="text-lg mb-2">No specific insights generated</p>
              <p className="text-sm">The AI completed analysis but found limited automation patterns</p>
            </div>
          )}
        </div>

        {/* Top Opportunities - Simplified */}
        {automation_opportunities.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 mb-8">
            <div className="flex items-center space-x-2 mb-6">
              <Zap className="w-6 h-6 text-amber-600" />
              <h3 className="text-xl font-semibold text-gray-900">Top Opportunities</h3>
            </div>
            
            <div className="space-y-4">
              {automation_opportunities.slice(0, 2).map((opp: any, index: number) => (
                <div key={index} className="border border-gray-200 rounded-lg p-6">
                  <div className="flex justify-between items-start mb-3">
                    <h4 className="text-lg font-medium text-gray-900">
                      {opp.workflow_type || `Opportunity ${index + 1}`}
                    </h4>
                    <div className="flex items-center space-x-2">
                      <TrendingUp className="w-4 h-4 text-green-600" />
                      <span className="text-green-600 font-medium">
                        {(opp.time_saved_weekly_hours || 0).toFixed(1)}h/week
                      </span>
                    </div>
                  </div>
                  <p className="text-gray-600 mb-4">
                    {opp.description || 'Automation opportunity identified through workflow analysis'}
                  </p>
                  <div className="flex justify-between items-center text-sm text-gray-500">
                    <span>ROI Score: {(opp.roi_score || 0).toFixed(1)}/10</span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      opp.priority === 'high' 
                        ? 'bg-red-100 text-red-700'
                        : opp.priority === 'medium'
                        ? 'bg-yellow-100 text-yellow-700'
                        : 'bg-green-100 text-green-700'
                    }`}>
                      {opp.priority || 'Medium'} Priority
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Simple Analysis Info */}
        <div className="bg-gray-100 rounded-lg p-6">
          <div className="flex items-center justify-between text-sm text-gray-600">
            <div className="flex items-center space-x-4">
              <span>Cost: ${(analysis_info.analysis_cost || 0).toFixed(2)}</span>
              <span>•</span>
              <span>Frames: {analysis_info.frames_analyzed || 0}</span>
              <span>•</span>
              <span>Time: {analysis_info.processing_time_seconds || 0}s</span>
            </div>
            <span className="text-teal-600 font-medium">
              {(analysis_info.confidence_score * 100).toFixed(0)}% confident
            </span>
          </div>
        </div>
        
      </div>
    </div>
  )
}