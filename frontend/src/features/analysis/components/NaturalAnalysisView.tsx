/**
 * Natural Analysis View Component
 * Displays GPT-4V analysis in natural language format
 * Focus: Clear, conversational understanding of workflows
 */

import React from 'react'
import { 
  Monitor, 
  Clock, 
  Zap, 
  TrendingUp,
  CheckCircle,
  ChevronRight,
  Layers
} from 'lucide-react'

interface ApplicationUsage {
  name: string
  purpose: string
  timePercentage: number
  actions: string[]
}

interface AutomationOpportunity {
  what: string
  how: string
  timeSaved: string
  complexity: 'simple' | 'moderate' | 'complex'
}

interface NaturalAnalysisData {
  naturalDescription: string
  applications: Record<string, ApplicationUsage>
  patterns: string[]
  automationOpportunities: AutomationOpportunity[]
  metrics?: {
    totalTimeSeconds: number
    repetitionsObserved: number
    applicationsUsed: number
    potentialTimeSavedDailyHours: number
  }
  confidence?: number
}

interface NaturalAnalysisViewProps {
  data: NaturalAnalysisData
  className?: string
}

export const NaturalAnalysisView: React.FC<NaturalAnalysisViewProps> = ({
  data,
  className = ''
}) => {
  const getComplexityColor = (complexity: string) => {
    const colors = {
      simple: 'text-green-600 bg-green-50',
      moderate: 'text-yellow-600 bg-yellow-50',
      complex: 'text-red-600 bg-red-50'
    }
    return colors[complexity as keyof typeof colors] || colors.moderate
  }

  // Sort applications by time percentage
  const sortedApps = Object.entries(data.applications).sort(
    ([, a], [, b]) => b.timePercentage - a.timePercentage
  )

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Natural Description Section */}
      <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Layers className="w-5 h-5 mr-2 text-blue-600" />
          What's Happening in Your Workflow
        </h3>
        <div className="prose prose-sm max-w-none">
          <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
            {data.naturalDescription}
          </p>
        </div>
      </div>

      {/* Applications Used */}
      <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Monitor className="w-5 h-5 mr-2 text-purple-600" />
          Applications Used
        </h3>
        <div className="space-y-3">
          {sortedApps.map(([name, app]) => (
            <div key={name} className="border-l-4 border-purple-200 pl-4">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900">{name}</h4>
                  <p className="text-sm text-gray-600">{app.purpose}</p>
                  {app.actions && app.actions.length > 0 && (
                    <div className="mt-1 flex flex-wrap gap-1">
                      {app.actions.map((action, idx) => (
                        <span
                          key={idx}
                          className="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded"
                        >
                          {action}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                <div className="ml-4 text-right">
                  <div className="text-2xl font-bold text-purple-600">
                    {app.timePercentage}%
                  </div>
                  <div className="text-xs text-gray-500">of time</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Patterns Found */}
      {data.patterns && data.patterns.length > 0 && (
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <TrendingUp className="w-5 h-5 mr-2 text-orange-600" />
            Patterns We Found
          </h3>
          <ul className="space-y-2">
            {data.patterns.map((pattern, idx) => (
              <li key={idx} className="flex items-start">
                <ChevronRight className="w-4 h-4 text-orange-400 mt-0.5 mr-2 flex-shrink-0" />
                <span className="text-gray-700">{pattern}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Automation Opportunities */}
      {data.automationOpportunities && data.automationOpportunities.length > 0 && (
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Zap className="w-5 h-5 mr-2 text-green-600" />
            Automation Opportunities
          </h3>
          <div className="space-y-4">
            {data.automationOpportunities.map((opp, idx) => (
              <div key={idx} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900">{opp.what}</h4>
                    <p className="text-sm text-gray-600 mt-1">{opp.how}</p>
                    <div className="mt-2 flex items-center space-x-4">
                      <span className="text-sm text-gray-500 flex items-center">
                        <Clock className="w-4 h-4 mr-1" />
                        {opp.timeSaved}
                      </span>
                      <span className={`text-xs px-2 py-1 rounded-full ${getComplexityColor(opp.complexity)}`}>
                        {opp.complexity} to implement
                      </span>
                    </div>
                  </div>
                  <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0 ml-3" />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Metrics Summary */}
      {data.metrics && (
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 border border-blue-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Impact Summary
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {data.metrics.potentialTimeSavedDailyHours.toFixed(1)}h
              </div>
              <div className="text-xs text-gray-600">Daily Time Savings</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {data.metrics.repetitionsObserved}
              </div>
              <div className="text-xs text-gray-600">Repetitions Found</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {data.metrics.applicationsUsed}
              </div>
              <div className="text-xs text-gray-600">Applications Used</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">
                {((data.confidence || 0) * 100).toFixed(0)}%
              </div>
              <div className="text-xs text-gray-600">Confidence</div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}