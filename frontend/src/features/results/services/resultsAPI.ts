/**
 * Results API Service
 * Integrates with NewSystem.AI backend for retrieving analysis results
 * Handles results fetching, flow chart data, and cost analysis
 */

import { get, getBaseUrl, APIError, isAPIError, getErrorMessage } from '../../../lib/api-client'

export interface ResultsApiResponse {
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
  message: string
}

export interface AutomationOpportunity {
  id?: string
  workflow_type: string
  priority: 'high' | 'medium' | 'low'
  time_saved_weekly_hours: number
  implementation_complexity: 'quick_win' | 'strategic' | 'consider' | 'defer'
  roi_score: number
  description: string
  confidence_score?: number
}

export interface FlowChartData {
  nodes: Array<{
    id: string
    type: 'start' | 'process' | 'decision' | 'end'
    label: string
    timeSpent: number
    automationPotential?: number
    position?: { x: number; y: number }
  }>
  edges: Array<{
    source: string
    target: string
    label?: string
    condition?: string
  }>
}

export interface FlowChartResponse {
  flow_chart: FlowChartData
  message: string
}

export interface CostAnalysisMetrics {
  current_monthly_cost: number
  projected_monthly_cost: number
  implementation_cost: number
  payback_period_days: number
  annual_savings: number
  hourly_rate_used: number
  time_savings_weekly_hours: number
  confidence_score: number
}

export interface CostAnalysisResponse {
  cost_analysis: CostAnalysisMetrics
  roi_metrics: {
    time_savings: {
      weekly_hours: number
      current_monthly_hours: number
    }
    cost_savings: {
      monthly_usd: number
      annual_usd: number
    }
    implementation: {
      estimated_cost_usd: number
      payback_period_days: number
    }
  }
  message: string
}

export interface ResultsSummary {
  session_id: string
  total_time_analyzed: number
  automation_opportunities: number
  estimated_time_savings: number
  confidence_score: number
}

export class ResultsAPIError extends APIError {
  constructor(
    message: string,
    status?: number,
    details?: any,
    endpoint?: string
  ) {
    super(message, status, details, endpoint)
    this.name = 'ResultsAPIError'
  }
}

class ResultsAPI {
  /**
   * Helper method to convert APIError to ResultsAPIError for backwards compatibility
   */
  private handleError(error: any, endpoint?: string): never {
    if (isAPIError(error)) {
      throw new ResultsAPIError(error.message, error.status, error.details, endpoint)
    }
    throw error
  }
  
  /**
   * Get complete analysis results for a session
   */
  async getResults(sessionId: string): Promise<ResultsApiResponse> {
    try {
      return await get<ResultsApiResponse>(`results/${sessionId}`)
    } catch (error) {
      this.handleError(error, `results/${sessionId}`)
    }
  }
  
  /**
   * Get results summary (executive overview)
   */
  async getResultsSummary(sessionId: string): Promise<ResultsSummary> {
    try {
      return await get<ResultsSummary>(`results/${sessionId}/summary`)
    } catch (error) {
      this.handleError(error, `results/${sessionId}/summary`)
    }
  }
  
  /**
   * Get workflow flow chart data
   */
  async getFlowChart(sessionId: string): Promise<FlowChartResponse> {
    try {
      return await get<FlowChartResponse>(`results/${sessionId}/flow`)
    } catch (error) {
      this.handleError(error, `results/${sessionId}/flow`)
    }
  }
  
  /**
   * Get automation opportunities list
   */
  async getAutomationOpportunities(sessionId: string): Promise<{
    opportunities: AutomationOpportunity[]
    message: string
  }> {
    try {
      return await get(`results/${sessionId}/opportunities`)
    } catch (error) {
      this.handleError(error, `results/${sessionId}/opportunities`)
    }
  }
  
  /**
   * Get cost-benefit analysis
   */
  async getCostAnalysis(
    sessionId: string,
    options?: {
      hourly_rate?: number
      implementation_budget?: number
    }
  ): Promise<CostAnalysisResponse> {
    try {
      const params = new URLSearchParams()
      
      if (options?.hourly_rate) {
        params.append('hourly_rate', options.hourly_rate.toString())
      }
      if (options?.implementation_budget) {
        params.append('implementation_budget', options.implementation_budget.toString())
      }
      
      const endpoint = `results/${sessionId}/cost${params.toString() ? `?${params.toString()}` : ''}`
      return await get<CostAnalysisResponse>(endpoint)
    } catch (error) {
      this.handleError(error, `results/${sessionId}/cost`)
    }
  }
  
  /**
   * Check API health for results service
   */
  async checkHealth(): Promise<{
    status: string
    service: string
    version: string
    environment: string
    components: Record<string, string>
  }> {
    try {
      const response = await fetch(getBaseUrl('health'))
      if (!response.ok) {
        throw new Error(`Health check failed: ${response.statusText}`)
      }
      return await response.json()
    } catch (error) {
      this.handleError(error, 'health')
    }
  }
}

// Export singleton instance
export const resultsAPI = new ResultsAPI()

// Export utilities for error handling
export const isResultsAPIError = (error: any): error is ResultsAPIError => {
  return error instanceof ResultsAPIError || isAPIError(error)
}

export const getResultsErrorMessage = (error: any): string => {
  return getErrorMessage(error)
}