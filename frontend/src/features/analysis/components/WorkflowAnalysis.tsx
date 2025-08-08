/**
 * Workflow Analysis Component
 * Container with tabs for different analysis views
 * Combines natural language, flow chart, and raw data
 */

import React, { useState, useEffect } from 'react'
import { 
  FileText, 
  GitBranch, 
  Code,
  Brain,
  ChevronRight,
  AlertCircle,
  RefreshCw
} from 'lucide-react'
import axios from 'axios'
import { NaturalAnalysisView } from './NaturalAnalysisView'
import { DynamicWorkflowChart } from './DynamicWorkflowChart'

interface TabProps {
  label: string
  icon: React.ElementType
  value: string
  active: boolean
  onClick: () => void
}

const Tab: React.FC<TabProps> = ({ label, icon: Icon, active, onClick }) => (
  <button
    onClick={onClick}
    className={`
      flex items-center space-x-2 px-4 py-2 font-medium text-sm rounded-t-lg
      transition-colors duration-200
      ${active 
        ? 'bg-white text-blue-600 border-b-2 border-blue-600' 
        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
      }
    `}
  >
    <Icon className="w-4 h-4" />
    <span>{label}</span>
  </button>
)

interface WorkflowAnalysisProps {
  analysisId?: string
  sessionId?: string
  className?: string
  onClose?: () => void
}

export const WorkflowAnalysis: React.FC<WorkflowAnalysisProps> = ({
  analysisId,
  sessionId,
  className = '',
  onClose
}) => {
  const [activeTab, setActiveTab] = useState('overview')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [analysisData, setAnalysisData] = useState<any>(null)
  const [status, setStatus] = useState<string>('Loading analysis...')

  useEffect(() => {
    if (analysisId || sessionId) {
      fetchAnalysis()
    }
  }, [analysisId, sessionId])

  const fetchAnalysis = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Fetch analysis results
      const endpoint = analysisId 
        ? `/api/v1/analysis/${analysisId}/results`
        : `/api/v1/recordings/${sessionId}/analysis`
      
      const response = await axios.get(`${import.meta.env.VITE_API_URL}${endpoint}`)
      
      if (response.data) {
        // Transform data for our components
        const transformedData = transformAnalysisData(response.data)
        setAnalysisData(transformedData)
      } else {
        throw new Error('No analysis data received')
      }
    } catch (err: any) {
      console.error('Failed to fetch analysis:', err)
      setError(err.message || 'Failed to load analysis')
    } finally {
      setLoading(false)
    }
  }

  const transformAnalysisData = (rawData: any) => {
    // Handle both old and new response formats
    const analysis = rawData.raw_gpt_response || rawData.analysis || rawData
    
    // For natural language format
    if (analysis.natural_description) {
      return {
        natural: {
          naturalDescription: analysis.natural_description,
          applications: analysis.applications || {},
          patterns: analysis.patterns || [],
          automationOpportunities: analysis.automation_opportunities || [],
          metrics: analysis.metrics,
          confidence: analysis.confidence
        },
        flowChart: analysis.flow_chart_data || {
          nodes: analysis.workflow_steps?.map((step: any, idx: number) => ({
            id: String(idx + 1),
            label: step.action || step.description,
            type: step.application ? 'application' : 'action',
            metadata: {
              time: step.time_estimate_seconds ? `${step.time_estimate_seconds}s` : undefined,
              application: step.application
            }
          })) || [],
          edges: analysis.workflow_steps?.slice(0, -1).map((step: any, idx: number) => ({
            source: String(idx + 1),
            target: String(idx + 2),
            label: step.purpose
          })) || []
        },
        raw: analysis
      }
    }
    
    // For legacy format - convert to natural language structure
    return {
      natural: {
        naturalDescription: generateNaturalDescription(rawData),
        applications: extractApplications(rawData),
        patterns: extractPatterns(rawData),
        automationOpportunities: extractOpportunities(rawData),
        metrics: extractMetrics(rawData),
        confidence: rawData.confidence_score || 0.8
      },
      flowChart: generateFlowChart(rawData),
      raw: rawData
    }
  }

  // Helper functions to convert legacy format
  const generateNaturalDescription = (data: any) => {
    const workflows = data.workflows || []
    const opportunities = data.automation_opportunities || []
    
    if (workflows.length === 0) {
      return "No specific workflows were detected in this recording. The analysis is still processing or the recording may be too short."
    }
    
    let description = "Based on the recording, here's what we observed:\n\n"
    
    workflows.forEach((workflow: any, idx: number) => {
      description += `${idx + 1}. ${workflow.description || workflow.type}\n`
      if (workflow.applications) {
        description += `   Applications involved: ${workflow.applications.join(', ')}\n`
      }
      if (workflow.duration_seconds) {
        description += `   Time spent: ${workflow.duration_seconds} seconds\n`
      }
      description += '\n'
    })
    
    if (opportunities.length > 0) {
      description += "\nWe identified opportunities to automate these workflows, "
      description += `which could save approximately ${opportunities[0].time_saved_daily_minutes || 0} minutes daily.`
    }
    
    return description
  }

  const extractApplications = (data: any) => {
    const apps: any = {}
    const workflows = data.workflows || []
    
    workflows.forEach((workflow: any) => {
      (workflow.applications || []).forEach((app: string) => {
        if (!apps[app]) {
          apps[app] = {
            name: app,
            purpose: 'Workflow processing',
            timePercentage: 25, // Estimate
            actions: workflow.steps || []
          }
        }
      })
    })
    
    return apps
  }

  const extractPatterns = (data: any) => {
    return data.insights || data.key_insights || []
  }

  const extractOpportunities = (data: any) => {
    return (data.automation_opportunities || []).map((opp: any) => ({
      what: opp.description || opp.workflow_type,
      how: opp.recommendation || opp.specific_recommendation || 'Automate this workflow',
      timeSaved: `${opp.time_saved_daily_minutes || 0} minutes daily`,
      complexity: opp.implementation_complexity || 'moderate'
    }))
  }

  const extractMetrics = (data: any) => {
    const summary = data.summary || {}
    return {
      totalTimeSeconds: data.time_analysis?.total_seconds || 0,
      repetitionsObserved: summary.total_workflows_detected || 0,
      applicationsUsed: Object.keys(extractApplications(data)).length,
      potentialTimeSavedDailyHours: (summary.time_savings_daily_minutes || 0) / 60
    }
  }

  const generateFlowChart = (data: any) => {
    const workflows = data.workflows || []
    const nodes: any[] = []
    const edges: any[] = []
    
    workflows.forEach((workflow: any, wIdx: number) => {
      (workflow.steps || []).forEach((step: string, sIdx: number) => {
        const nodeId = `w${wIdx}-s${sIdx}`
        nodes.push({
          id: nodeId,
          label: step,
          type: 'action'
        })
        
        if (sIdx > 0) {
          edges.push({
            source: `w${wIdx}-s${sIdx - 1}`,
            target: nodeId
          })
        }
      })
    })
    
    return { nodes, edges }
  }

  if (loading) {
    return (
      <div className={`bg-white rounded-lg shadow-lg p-8 ${className}`}>
        <div className="flex flex-col items-center justify-center space-y-4">
          <Brain className="w-12 h-12 text-purple-600 animate-pulse" />
          <h3 className="text-lg font-semibold text-gray-900">Analyzing Workflow...</h3>
          <p className="text-sm text-gray-600">{status}</p>
          <RefreshCw className="w-5 h-5 text-gray-400 animate-spin" />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className={`bg-white rounded-lg shadow-lg p-8 ${className}`}>
        <div className="flex flex-col items-center justify-center space-y-4">
          <AlertCircle className="w-12 h-12 text-red-500" />
          <h3 className="text-lg font-semibold text-gray-900">Analysis Error</h3>
          <p className="text-sm text-gray-600">{error}</p>
          <button
            onClick={fetchAnalysis}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Retry Analysis
          </button>
        </div>
      </div>
    )
  }

  if (!analysisData) {
    return null
  }

  return (
    <div className={`bg-white rounded-lg shadow-lg ${className}`}>
      {/* Header */}
      <div className="border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-gray-900">Workflow Analysis</h2>
          {onClose && (
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 px-6">
        <div className="flex space-x-2">
          <Tab
            label="Overview"
            icon={FileText}
            value="overview"
            active={activeTab === 'overview'}
            onClick={() => setActiveTab('overview')}
          />
          <Tab
            label="Workflow Map"
            icon={GitBranch}
            value="flowchart"
            active={activeTab === 'flowchart'}
            onClick={() => setActiveTab('flowchart')}
          />
          <Tab
            label="Raw Analysis"
            icon={Code}
            value="raw"
            active={activeTab === 'raw'}
            onClick={() => setActiveTab('raw')}
          />
        </div>
      </div>

      {/* Tab Content */}
      <div className="p-6">
        {activeTab === 'overview' && analysisData.natural && (
          <NaturalAnalysisView data={analysisData.natural} />
        )}
        
        {activeTab === 'flowchart' && analysisData.flowChart && (
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Workflow Visualization
            </h3>
            <DynamicWorkflowChart 
              data={analysisData.flowChart}
              onNodeClick={(node) => console.log('Node clicked:', node)}
            />
            <p className="text-sm text-gray-600 mt-4">
              Click and drag to pan, scroll to zoom, click nodes for details
            </p>
          </div>
        )}
        
        {activeTab === 'raw' && analysisData.raw && (
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">
                Raw GPT-4V Analysis
              </h3>
              <button
                onClick={() => {
                  navigator.clipboard.writeText(JSON.stringify(analysisData.raw, null, 2))
                }}
                className="text-sm text-blue-600 hover:text-blue-800"
              >
                Copy JSON
              </button>
            </div>
            <div className="bg-gray-100 rounded-lg p-4 overflow-auto max-h-96">
              <pre className="text-xs text-gray-700 whitespace-pre-wrap font-mono">
                {JSON.stringify(analysisData.raw, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}