import React, { useEffect, useState, useMemo } from 'react'
import { CheckCircle, AlertCircle, Brain, ArrowLeft, RefreshCw, GitBranch, FileText, Code, BarChart3, Monitor, MousePointer, Database, Mail, Globe, Clock, ArrowDown, ExternalLink, Share2, Download, ChevronDown, Image } from 'lucide-react'
import { resultsAPI, type ResultsApiResponse, type RawAnalysisResponse, getResultsErrorMessage } from '../../results/services/resultsAPI'
import { DynamicWorkflowChart } from './DynamicWorkflowChart'
import { exportWorkflowToDrawio } from '../services/drawioGenerator'

interface MinimalResultsPageProps {
  sessionId: string
  onBack: () => void
}

type TabType = 'overview' | 'natural' | 'raw' | 'chart'

export const MinimalResultsPage: React.FC<MinimalResultsPageProps> = ({ sessionId, onBack }) => {
  const [apiResponse, setApiResponse] = useState<ResultsApiResponse | null>(null)
  const [rawData, setRawData] = useState<RawAnalysisResponse | null>(null)
  const [activeTab, setActiveTab] = useState<TabType>('overview')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null)
  const [showExportDropdown, setShowExportDropdown] = useState(false)

  const fetchResults = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Fetch both processed results and raw data in parallel
      const [processedData, rawAnalysisData] = await Promise.all([
        resultsAPI.getResults(sessionId),
        resultsAPI.getRawAnalysisData(sessionId).catch(err => {
          console.warn('Raw data not available:', err)
          return null
        })
      ])
      
      setApiResponse(processedData)
      setRawData(rawAnalysisData)
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

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement
      if (showExportDropdown && !target.closest('[data-dropdown="export"]')) {
        setShowExportDropdown(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [showExportDropdown])

  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  // Helper functions for enhanced workflow steps
  const getStepIcon = (step: any) => {
    const application = step.application?.toLowerCase() || ''
    const action = step.action?.toLowerCase() || ''
    
    // Application-based icons
    if (application.includes('mail') || application.includes('outlook') || application.includes('gmail')) return Mail
    if (application.includes('excel') || application.includes('sheets')) return FileText
    if (application.includes('chrome') || application.includes('browser') || application.includes('web')) return Globe
    if (application.includes('database') || application.includes('wms') || application.includes('erp')) return Database
    
    // Action-based icons
    if (action.includes('click') || action.includes('select') || action.includes('navigate')) return MousePointer
    if (action.includes('open') || action.includes('switch') || action.includes('access')) return Monitor
    if (action.includes('copy') || action.includes('paste') || action.includes('enter') || action.includes('input')) return MousePointer
    
    return Monitor // default
  }

  const getStepType = (step: any) => {
    const action = step.action?.toLowerCase() || ''
    if (action.includes('open') || action.includes('switch') || action.includes('access')) return 'application'
    if (action.includes('copy') || action.includes('paste') || action.includes('enter') || action.includes('input')) return 'action'
    if (action.includes('data') || action.includes('information')) return 'data'
    if (action.includes('check') || action.includes('verify') || action.includes('review')) return 'decision'
    return 'action'
  }

  const getStepTypeColor = (stepType: string) => {
    switch (stepType) {
      case 'application': return 'bg-blue-50 border-blue-200 text-blue-800'
      case 'action': return 'bg-orange-50 border-orange-200 text-orange-800'
      case 'data': return 'bg-green-50 border-green-200 text-green-800'
      case 'decision': return 'bg-purple-50 border-purple-200 text-purple-800'
      default: return 'bg-gray-50 border-gray-200 text-gray-800'
    }
  }

  const extractDataInvolved = (step: any) => {
    // Extract data types from step purpose or action
    const text = `${step.action || ''} ${step.purpose || ''}`.toLowerCase()
    const dataTypes = []
    
    if (text.includes('order') || text.includes('orders')) dataTypes.push('order data')
    if (text.includes('customer') || text.includes('client')) dataTypes.push('customer info')
    if (text.includes('email') || text.includes('message')) dataTypes.push('email content')
    if (text.includes('inventory') || text.includes('stock')) dataTypes.push('inventory data')
    if (text.includes('number') || text.includes('id') || text.includes('code')) dataTypes.push('identifiers')
    if (text.includes('address') || text.includes('location')) dataTypes.push('address data')
    if (text.includes('price') || text.includes('cost') || text.includes('amount')) dataTypes.push('pricing info')
    
    return dataTypes.length > 0 ? dataTypes : step.data_involved || []
  }

  // Handle Draw.io export
  const handleDrawioExport = (workflowSteps: any[]) => {
    try {
      const result = exportWorkflowToDrawio(workflowSteps, {
        title: `Workflow Analysis - ${formatDuration(recording_info.duration_seconds)}`
      })
      
      if (result.success) {
        showToast('Opening workflow in Draw.io...', 'success')
      }
    } catch (error) {
      console.error('Failed to export to Draw.io:', error)
      showToast('Failed to export workflow. Please try again.', 'error')
    }
  }

  // Handle sharing URL
  const handleShareURL = async (workflowSteps: any[]) => {
    try {
      const { drawioGenerator } = await import('../services/drawioGenerator')
      const title = `Workflow Analysis - ${formatDuration(recording_info.duration_seconds)}`
      const xml = drawioGenerator.generateXML(workflowSteps, title)
      const shareURL = drawioGenerator.generateViewerURL(xml)
      
      // Copy to clipboard
      await navigator.clipboard.writeText(shareURL.url)
      showToast('Share link copied to clipboard!', 'success')
    } catch (error) {
      console.error('Failed to create share URL:', error)
      showToast('Failed to create share link. Please try again.', 'error')
    }
  }

  // Handle .drawio file download
  const handleDownloadDrawio = async (workflowSteps: any[]) => {
    try {
      const { drawioGenerator } = await import('../services/drawioGenerator')
      const title = `Workflow Analysis - ${formatDuration(recording_info.duration_seconds)}`
      const xml = drawioGenerator.generateXML(workflowSteps, title)
      const blob = drawioGenerator.createDownloadBlob(xml)
      
      // Create download link
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `workflow-analysis-${new Date().toISOString().slice(0, 10)}.drawio`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
      
      showToast('Workflow downloaded successfully!', 'success')
    } catch (error) {
      console.error('Failed to download workflow:', error)
      showToast('Failed to download workflow. Please try again.', 'error')
    }
  }

  // Handle PNG export from ReactFlow - REAL implementation
  const handleExportPNG = async () => {
    try {
      // Show loading state
      showToast('Generating PNG export...', 'success')
      
      // Find the ReactFlow viewport (the actual chart content)
      const chartViewport = document.querySelector('.react-flow__viewport') as HTMLElement
      const chartContainer = document.querySelector('.react-flow') as HTMLElement
      
      if (!chartContainer || !chartViewport) {
        showToast('Chart not found. Please ensure the workflow chart is visible.', 'error')
        return
      }

      // Dynamic import of html2canvas for code splitting
      const { default: html2canvas } = await import('html2canvas')
      
      // Configure html2canvas options for high quality
      const canvas = await html2canvas(chartContainer, {
        background: '#ffffff',
        logging: false,
        useCORS: true,
        allowTaint: true
      })
      
      // Convert to high-quality PNG
      const dataUrl = canvas.toDataURL('image/png', 1.0)
      
      // Create download link
      const link = document.createElement('a')
      link.href = dataUrl
      link.download = `workflow-chart-${new Date().toISOString().slice(0, 10)}.png`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      
      showToast('PNG exported successfully!', 'success')
      
    } catch (error) {
      console.error('Failed to export PNG:', error)
      showToast('Failed to export PNG. Please try screenshot tool as backup.', 'error')
    }
  }

  // Show toast notification
  const showToast = (message: string, type: 'success' | 'error') => {
    setToast({ message, type })
    setTimeout(() => setToast(null), 3000)
  }

  // Transform workflow_steps to ReactFlow chart format
  const transformWorkflowStepsToChart = (workflowSteps: any[]): { nodes: any[], edges: any[] } => {
    if (!workflowSteps || workflowSteps.length === 0) {
      return { nodes: [], edges: [] }
    }

    // Create nodes from workflow steps - ensure exact format match for DynamicWorkflowChart
    const nodes = workflowSteps.map((step, index) => {
      const stepType = getStepType(step)
      
      return {
        id: `step-${index + 1}`,
        label: step.action || `Step ${index + 1}`,
        type: stepType as 'application' | 'action' | 'data' | 'decision',
        metadata: {
          time: step.time_formatted || (step.time_estimate_seconds ? `${step.time_estimate_seconds}s` : ''),
          application: step.application,
          purpose: step.purpose,
          frames: step.visible_in_frames?.length || 0
        }
      }
    })

    // Create edges between sequential steps - ensure proper format
    const edges = workflowSteps.slice(0, -1).map((_, index) => ({
      source: `step-${index + 1}`,
      target: `step-${index + 2}`,
      label: undefined, // Use undefined instead of empty string
      type: undefined   // Use undefined to let DynamicWorkflowChart handle defaults
    }))

    return { nodes, edges }
  }

  // Get workflow chart data with fallback transformation (memoized to prevent recreations)
  const workflowChartData = useMemo(() => {
    // First, try to use the existing workflow_chart if available
    if (apiResponse?.results?.workflow_chart?.nodes && apiResponse.results.workflow_chart.nodes.length > 0) {
      return apiResponse.results.workflow_chart
    }
    
    // Fallback: transform workflow_steps to chart format
    if (rawData?.raw_gpt_response?.analysis?.workflow_steps) {
      const transformedData = transformWorkflowStepsToChart(rawData.raw_gpt_response.analysis.workflow_steps)
      
      // Debug logging to help troubleshoot
      console.log('Transformed workflow data:', {
        nodeCount: transformedData.nodes.length,
        edgeCount: transformedData.edges.length,
        nodeIds: transformedData.nodes.map(n => n.id),
        edges: transformedData.edges.map(e => `${e.source} -> ${e.target}`)
      })
      
      return transformedData
    }
    
    return null
  }, [apiResponse?.results?.workflow_chart, rawData?.raw_gpt_response?.analysis?.workflow_steps])


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
  const { recording_info, analysis_info, insights } = analysisResults

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
        
        {/* Tab Navigation */}
        <div className="mb-8">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8" aria-label="Tabs">
              <button
                onClick={() => setActiveTab('overview')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'overview'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <BarChart3 className="w-4 h-4" />
                  <span>Analysis Overview</span>
                </div>
              </button>
              
              <button
                onClick={() => setActiveTab('natural')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'natural'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <FileText className="w-4 h-4" />
                  <span>Natural Language</span>
                </div>
              </button>
              
              <button
                onClick={() => setActiveTab('raw')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'raw'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <Code className="w-4 h-4" />
                  <span>Raw JSON</span>
                </div>
              </button>
              
              <button
                onClick={() => setActiveTab('chart')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'chart'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <GitBranch className="w-4 h-4" />
                  <span>Workflow Chart</span>
                </div>
              </button>
            </nav>
          </div>
        </div>
        
        {/* Tab Content */}
        {activeTab === 'overview' && (
          <div className="space-y-8">
            {/* Analysis Summary - Layer 2 Focus */}
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-200 p-8 text-center">
          <div className="flex justify-center mb-4">
            <div className="p-3 bg-blue-100 rounded-full">
              <Brain className="w-8 h-8 text-blue-600" />
            </div>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Workflow Analysis Complete
          </h2>
          <p className="text-lg text-gray-700 mb-6">AI has processed your workflow recording</p>
          
          {/* Core Analysis Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <div className="text-2xl font-bold text-blue-600 mb-1">
                {analysis_info.frames_analyzed || 0}
              </div>
              <div className="text-sm text-gray-600">Frames analyzed</div>
            </div>
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <div className="text-2xl font-bold text-indigo-600 mb-1">
                {formatDuration(recording_info.duration_seconds)}
              </div>
              <div className="text-sm text-gray-600">Recording duration</div>
            </div>
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <div className="text-2xl font-bold text-purple-600 mb-1">
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

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
              <div className="flex items-center space-x-2 mb-6">
                <GitBranch className="w-6 h-6 text-purple-600" />
                <h3 className="text-xl font-semibold text-gray-900">Workflow Visualization</h3>
              </div>
              
              {workflowChartData && workflowChartData.nodes.length > 0 ? (
                <div>
                  <div className="min-h-[400px] rounded-lg border border-gray-200 overflow-hidden mb-4">
                    <DynamicWorkflowChart
                      data={workflowChartData}
                      className="h-full w-full"
                    />
                  </div>
                  <p className="text-sm text-gray-500">
                    Interactive workflow map showing your process flow and automation opportunities
                  </p>
                </div>
              ) : (
                <div className="text-center py-12 text-gray-500">
                  <GitBranch className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                  <p className="text-lg mb-2">No workflow chart available</p>
                  <p className="text-sm">Workflow visualization data was not generated for this analysis</p>
                </div>
              )}
            </div>
            
            {/* Automation Opportunities - Removed for Layer 2 focus */}
            {/* Will add back in Layer 3 once analysis is solid */}
          </div>
        )}
        
        {/* Natural Language Tab */}
        {activeTab === 'natural' && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
            <div className="flex items-center space-x-2 mb-6">
              <FileText className="w-6 h-6 text-green-600" />
              <h3 className="text-xl font-semibold text-gray-900">Natural Language Analysis</h3>
            </div>
            
            {rawData?.raw_gpt_response?.analysis?.natural_description ? (
              <div className="space-y-6">
                {/* Natural Description */}
                <div>
                  <h4 className="text-lg font-medium text-gray-900 mb-3">📝 What Happened</h4>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-gray-800 leading-relaxed">
                      {rawData.raw_gpt_response.analysis.natural_description}
                    </p>
                  </div>
                </div>
                
                {/* Enhanced Workflow Steps */}
                {rawData.raw_gpt_response.analysis.workflow_steps && (
                  <div>
                    <h4 className="text-lg font-medium text-gray-900 mb-3 flex items-center">
                      <GitBranch className="w-5 h-5 mr-2 text-blue-600" />
                      📋 Step-by-Step Workflow
                    </h4>
                    <div className="space-y-2">
                      {rawData.raw_gpt_response.analysis.workflow_steps.map((step: any, index: number) => {
                        const stepType = getStepType(step)
                        const StepIcon = getStepIcon(step)
                        const dataInvolved = extractDataInvolved(step)
                        const nextStep = rawData.raw_gpt_response.analysis.workflow_steps[index + 1]
                        
                        return (
                          <div key={index}>
                            {/* Main Step */}
                            <div className={`relative flex items-start space-x-4 p-4 rounded-lg border-2 transition-all hover:shadow-md ${getStepTypeColor(stepType)}`}>
                              {/* Step Number & Icon */}
                              <div className="flex flex-col items-center space-y-1 flex-shrink-0">
                                <div className="w-8 h-8 bg-white rounded-full flex items-center justify-center border-2 border-current shadow-sm">
                                  <span className="text-sm font-bold">{step.step_number || index + 1}</span>
                                </div>
                                <StepIcon className="w-4 h-4 opacity-60" />
                              </div>
                              
                              {/* Step Content */}
                              <div className="flex-1 min-w-0">
                                <div className="flex items-start justify-between">
                                  <div className="flex-1">
                                    <p className="font-medium text-gray-900 mb-1">{step.action}</p>
                                    <div className="flex items-center space-x-3 text-sm text-gray-600">
                                      <span className="flex items-center">
                                        <Monitor className="w-3 h-3 mr-1" />
                                        {step.application}
                                      </span>
                                      {step.time_estimate_seconds && (
                                        <span className="flex items-center">
                                          <Clock className="w-3 h-3 mr-1" />
                                          {step.time_formatted || `${step.time_estimate_seconds}s`}
                                        </span>
                                      )}
                                    </div>
                                    <p className="text-sm text-gray-600 mt-1">{step.purpose}</p>
                                  </div>
                                  
                                  {/* Step Type Badge */}
                                  <span className="px-2 py-1 text-xs font-medium bg-white bg-opacity-80 rounded-full border border-current">
                                    {stepType}
                                  </span>
                                </div>
                                
                                {/* Data Involved */}
                                {dataInvolved && dataInvolved.length > 0 && (
                                  <div className="mt-2 flex flex-wrap gap-1">
                                    {dataInvolved.map((dataType: string, dataIndex: number) => (
                                      <span 
                                        key={dataIndex} 
                                        className="inline-flex items-center px-2 py-1 text-xs bg-white bg-opacity-60 text-gray-700 rounded border"
                                      >
                                        <Database className="w-3 h-3 mr-1" />
                                        {dataType}
                                      </span>
                                    ))}
                                  </div>
                                )}
                              </div>
                            </div>
                            
                            {/* Flow Arrow to Next Step */}
                            {nextStep && (
                              <div className="flex justify-center py-2">
                                <div className="flex items-center space-x-2 px-3 py-1 bg-gray-100 rounded-full text-xs text-gray-500">
                                  <ArrowDown className="w-3 h-3" />
                                  <span>then</span>
                                </div>
                              </div>
                            )}
                          </div>
                        )
                      })}
                    </div>
                    
                    {/* Chart Preview Hint */}
                    <div className="mt-4 p-3 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200">
                      <div className="flex items-center space-x-2 text-sm text-gray-700">
                        <GitBranch className="w-4 h-4 text-blue-600" />
                        <span>💡 <strong>Tip:</strong> Switch to the "Workflow Chart" tab to see this flow visualized as an interactive diagram</span>
                      </div>
                      <div className="mt-2 text-xs text-gray-500">
                        ⏱️ Time estimates are calculated from frame-by-frame analysis (1 frame = 1 second)
                      </div>
                    </div>
                  </div>
                )}
                
                {/* Applications Used */}
                {rawData.raw_gpt_response.analysis.applications && (
                  <div>
                    <h4 className="text-lg font-medium text-gray-900 mb-3">💻 Applications Used</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {Object.entries(rawData.raw_gpt_response.analysis.applications).map(([appName, appData]: [string, any]) => (
                        <div key={appName} className="bg-indigo-50 rounded-lg p-4">
                          <h5 className="font-medium text-gray-900">{appName}</h5>
                          <p className="text-sm text-gray-600 mt-1">{appData.purpose}</p>
                          {appData.timePercentage && (
                            <div className="mt-2">
                              <div className="flex justify-between text-xs text-gray-500 mb-1">
                                <span>Time spent</span>
                                <span>{appData.timeFormatted || `${appData.timeSeconds}s`} ({appData.timePercentage}%)</span>
                              </div>
                              <div className="w-full bg-gray-200 rounded-full h-2">
                                <div 
                                  className="bg-indigo-600 h-2 rounded-full" 
                                  style={{ width: `${appData.timePercentage}%` }}
                                />
                              </div>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* Patterns Observed */}
                {rawData.raw_gpt_response.analysis.patterns && (
                  <div>
                    <h4 className="text-lg font-medium text-gray-900 mb-3">🔄 Patterns Observed</h4>
                    <div className="space-y-2">
                      {rawData.raw_gpt_response.analysis.patterns.map((pattern: string, index: number) => (
                        <div key={index} className="flex items-start space-x-3 p-3 bg-amber-50 rounded-lg">
                          <div className="w-2 h-2 bg-amber-500 rounded-full mt-2 flex-shrink-0" />
                          <p className="text-gray-800">{pattern}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* Confidence */}
                <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
                  <span className="text-green-800 font-medium">🎯 Analysis Confidence</span>
                  <span className="text-green-600 font-bold text-lg">
                    {((rawData.raw_gpt_response.analysis.confidence || 0) * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            ) : (
              <div className="text-center py-12 text-gray-500">
                <FileText className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                <p className="text-lg mb-2">No natural language analysis available</p>
                <p className="text-sm">This analysis may not include natural language formatting</p>
              </div>
            )}
          </div>
        )}
        
        {/* Raw JSON Tab */}
        {activeTab === 'raw' && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
            <div className="flex items-center space-x-2 mb-6">
              <Code className="w-6 h-6 text-purple-600" />
              <h3 className="text-xl font-semibold text-gray-900">Raw GPT-4V Response</h3>
            </div>
            
            {rawData ? (
              <div className="space-y-6">
                {/* Processing Info */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-gray-900 mb-3">📊 Processing Information</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500">Model:</span>
                      <p className="font-medium">{rawData.processing_info.gpt_version}</p>
                    </div>
                    <div>
                      <span className="text-gray-500">Frames:</span>
                      <p className="font-medium">{rawData.processing_info.frames_analyzed}</p>
                    </div>
                    <div>
                      <span className="text-gray-500">Tokens:</span>
                      <p className="font-medium">{rawData.metadata.token_usage.total_tokens || 'N/A'}</p>
                    </div>
                    <div>
                      <span className="text-gray-500">Cost:</span>
                      <p className="font-medium">${rawData.processing_info.analysis_cost.toFixed(3)}</p>
                    </div>
                  </div>
                </div>
                
                {/* Raw JSON Display */}
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="text-sm font-medium text-gray-900">🔍 Complete GPT-4V Response</h4>
                    <button
                      onClick={() => navigator.clipboard.writeText(JSON.stringify(rawData.raw_gpt_response, null, 2))}
                      className="text-sm px-3 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
                    >
                      📋 Copy JSON
                    </button>
                  </div>
                  <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm overflow-auto max-h-96">
                    <pre>{JSON.stringify(rawData.raw_gpt_response, null, 2)}</pre>
                  </div>
                </div>
                
                {/* Structured Insights */}
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="text-sm font-medium text-gray-900">🏗️ Structured Insights (Parsed)</h4>
                    <button
                      onClick={() => navigator.clipboard.writeText(JSON.stringify(rawData.structured_insights, null, 2))}
                      className="text-sm px-3 py-1 bg-green-100 text-green-700 rounded hover:bg-green-200"
                    >
                      📋 Copy Parsed
                    </button>
                  </div>
                  <div className="bg-gray-900 text-blue-400 p-4 rounded-lg font-mono text-sm overflow-auto max-h-96">
                    <pre>{JSON.stringify(rawData.structured_insights, null, 2)}</pre>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-12 text-gray-500">
                <Code className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                <p className="text-lg mb-2">Raw data not available</p>
                <p className="text-sm">Analysis may still be processing or raw data was not stored</p>
              </div>
            )}
          </div>
        )}
        
        {/* Workflow Chart Tab */}
        {activeTab === 'chart' && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-2">
                <GitBranch className="w-6 h-6 text-purple-600" />
                <h3 className="text-xl font-semibold text-gray-900">Workflow Visualization</h3>
              </div>
              
              {/* Export Options Dropdown */}
              {rawData?.raw_gpt_response?.analysis?.workflow_steps && (
                <div className="relative" data-dropdown="export">
                  <button
                    onClick={() => setShowExportDropdown(!showExportDropdown)}
                    className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    title="Export workflow options"
                  >
                    <ExternalLink className="w-4 h-4" />
                    <span>Export Workflow</span>
                    <ChevronDown className="w-4 h-4" />
                  </button>
                  
                  {/* Dropdown Menu */}
                  {showExportDropdown && (
                    <div className="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50">
                      <button
                        onClick={() => {
                          handleDrawioExport(rawData.raw_gpt_response.analysis.workflow_steps)
                          setShowExportDropdown(false)
                        }}
                        className="w-full text-left px-4 py-2 hover:bg-gray-50 flex items-center space-x-3"
                      >
                        <ExternalLink className="w-4 h-4 text-blue-600" />
                        <div>
                          <div className="font-medium text-gray-900">Edit in Draw.io</div>
                          <div className="text-sm text-gray-500">Open for professional editing</div>
                        </div>
                      </button>
                      
                      <button
                        onClick={() => {
                          handleShareURL(rawData.raw_gpt_response.analysis.workflow_steps)
                          setShowExportDropdown(false)
                        }}
                        className="w-full text-left px-4 py-2 hover:bg-gray-50 flex items-center space-x-3"
                      >
                        <Share2 className="w-4 h-4 text-green-600" />
                        <div>
                          <div className="font-medium text-gray-900">Share Link</div>
                          <div className="text-sm text-gray-500">Copy shareable viewer URL</div>
                        </div>
                      </button>
                      
                      <button
                        onClick={() => {
                          handleDownloadDrawio(rawData.raw_gpt_response.analysis.workflow_steps)
                          setShowExportDropdown(false)
                        }}
                        className="w-full text-left px-4 py-2 hover:bg-gray-50 flex items-center space-x-3"
                      >
                        <Download className="w-4 h-4 text-purple-600" />
                        <div>
                          <div className="font-medium text-gray-900">Download .drawio</div>
                          <div className="text-sm text-gray-500">Save for offline editing</div>
                        </div>
                      </button>
                      
                      <button
                        onClick={() => {
                          handleExportPNG()
                          setShowExportDropdown(false)
                        }}
                        className="w-full text-left px-4 py-2 hover:bg-gray-50 flex items-center space-x-3"
                      >
                        <Image className="w-4 h-4 text-orange-600" />
                        <div>
                          <div className="font-medium text-gray-900">Export as PNG</div>
                          <div className="text-sm text-gray-500">Save chart as image</div>
                        </div>
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
            
{workflowChartData && workflowChartData.nodes.length > 0 ? (
              <div>
                <div className="min-h-[400px] rounded-lg border border-gray-200 overflow-hidden mb-4">
                  <DynamicWorkflowChart
                    data={workflowChartData}
                    className="h-full w-full"
                  />
                </div>
                <p className="text-sm text-gray-500">
                  Interactive workflow map showing your process flow and automation opportunities
                </p>
              </div>
            ) : (
              <div className="text-center py-12 text-gray-500">
                <GitBranch className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                <p className="text-lg mb-2">No workflow chart available</p>
                <p className="text-sm">Workflow visualization data was not generated for this analysis</p>
              </div>
            )}
          </div>
        )}
        
        {/* Simple Analysis Info - Only show on overview tab */}
        {activeTab === 'overview' && (
          <div className="bg-gray-100 rounded-lg p-6 mt-8">
            <div className="flex items-center justify-between text-sm text-gray-600">
              <div className="flex items-center space-x-4">
                <span>Cost: ${(analysis_info.analysis_cost || 0).toFixed(2)}</span>
                <span>•</span>
                <span>Frames: {analysis_info.frames_analyzed || 0}</span>
                <span>•</span>
                <span>Time: {analysis_info.processing_time_seconds || 0}s</span>
                {rawData?.metadata.token_usage.total_tokens && (
                  <>
                    <span>•</span>
                    <span>Tokens: {rawData.metadata.token_usage.total_tokens}</span>
                  </>
                )}
              </div>
              <span className="text-teal-600 font-medium">
                {(analysis_info.confidence_score * 100).toFixed(0)}% confident
              </span>
            </div>
          </div>
        )}
        
      </div>
      
      {/* Toast Notification */}
      {toast && (
        <div className={`fixed top-4 right-4 z-50 px-6 py-3 rounded-lg shadow-lg transition-all duration-300 ${
          toast.type === 'success' 
            ? 'bg-green-600 text-white' 
            : 'bg-red-600 text-white'
        }`}>
          <div className="flex items-center space-x-2">
            {toast.type === 'success' ? (
              <CheckCircle className="w-4 h-4" />
            ) : (
              <AlertCircle className="w-4 h-4" />
            )}
            <span className="text-sm">{toast.message}</span>
          </div>
        </div>
      )}
    </div>
  )
}