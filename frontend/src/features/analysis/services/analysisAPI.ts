/**
 * Analysis API Service
 * Integrates with NewSystem.AI backend for GPT-4V workflow analysis
 * Handles analysis orchestration, status polling, and results retrieval
 */

import { get, post, getBaseUrl, APIError, isAPIError, getErrorMessage } from '../../../lib/api-client'

export interface AnalysisStartRequest {
  analysis_type?: 'full' | 'quick'
  options?: {
    frame_sampling_rate?: number
    focus_areas?: string[]
    cost_limit?: number
  }
}

export interface AnalysisStartResponse {
  id: string
  status: string
  message: string
  estimated_processing_time_minutes: number
  analysis_cost_estimate?: number
}

export interface AnalysisStatusResponse {
  id: string
  recording_id: string
  status: 'queued' | 'processing' | 'completed' | 'failed'
  progress_percentage: number
  current_stage: string
  processing_time_seconds?: number
  error_message?: string
  frames_analyzed?: number
  estimated_completion_minutes?: number
}

export interface AutomationOpportunity {
  id: string
  workflow_type: string
  priority: 'high' | 'medium' | 'low'
  time_saved_weekly_hours: number
  implementation_complexity: 'quick_win' | 'strategic' | 'consider' | 'defer'
  roi_score: number
  description: string
  confidence_score?: number
}

export interface WorkflowStep {
  id: string
  sequence: number
  action: string
  screen_context: string
  time_spent_seconds: number
  automation_potential: number
  notes?: string
}

export interface TimeAnalysis {
  total_workflow_time_seconds: number
  repetitive_actions_time_seconds: number
  automation_potential_time_seconds: number
  manual_decision_time_seconds: number
  break_down_by_action: Array<{
    action_type: string
    time_seconds: number
    frequency: number
  }>
}

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
    workflows: WorkflowStep[]
    automation_opportunities: AutomationOpportunity[]
    time_analysis: TimeAnalysis
    insights: string[]
  } | null
  message: string
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

export class AnalysisAPIError extends APIError {
  constructor(
    message: string,
    status?: number,
    details?: any,
    endpoint?: string
  ) {
    super(message, status, details, endpoint)
    this.name = 'AnalysisAPIError'
  }
}

class AnalysisAPI {
  /**
   * Helper method to convert APIError to AnalysisAPIError for backwards compatibility
   */
  private handleError(error: any, endpoint?: string): never {
    if (isAPIError(error)) {
      throw new AnalysisAPIError(error.message, error.status, error.details, endpoint)
    }
    throw error
  }
  
  /**
   * Start analysis for a completed recording
   */
  async startAnalysis(
    recordingId: string,
    request: AnalysisStartRequest = {}
  ): Promise<AnalysisStartResponse> {
    try {
      return await post<AnalysisStartResponse>(`analysis/${recordingId}/start`, request)
    } catch (error) {
      this.handleError(error, `analysis/${recordingId}/start`)
    }
  }
  
  /**
   * Get analysis status and progress
   */
  async getAnalysisStatus(analysisId: string): Promise<AnalysisStatusResponse> {
    try {
      return await get<AnalysisStatusResponse>(`analysis/${analysisId}/status`)
    } catch (error) {
      this.handleError(error, `analysis/${analysisId}/status`)
    }
  }
  
  /**
   * Retry failed analysis
   */
  async retryAnalysis(analysisId: string): Promise<AnalysisStartResponse> {
    try {
      return await post<AnalysisStartResponse>(`analysis/${analysisId}/retry`)
    } catch (error) {
      this.handleError(error, `analysis/${analysisId}/retry`)
    }
  }
  
  /**
   * Get complete analysis results
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
  async getResultsSummary(sessionId: string): Promise<{
    session_id: string
    total_time_analyzed: number
    automation_opportunities: number
    estimated_time_savings: number
    confidence_score: number
  }> {
    try {
      return await get(`results/${sessionId}/summary`)
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
   * Poll analysis status until completion or failure
   */
  async pollAnalysisStatus(
    analysisId: string,
    options?: {
      intervalMs?: number
      timeoutMs?: number
      onProgress?: (status: AnalysisStatusResponse) => void
    }
  ): Promise<AnalysisStatusResponse> {
    const intervalMs = options?.intervalMs || 2000  // 2 seconds
    const timeoutMs = options?.timeoutMs || 300000  // 5 minutes
    const startTime = Date.now()
    
    return new Promise((resolve, reject) => {
      const poll = async () => {
        try {
          const status = await this.getAnalysisStatus(analysisId)
          
          // Call progress callback if provided
          options?.onProgress?.(status)
          
          // Check if analysis is complete
          if (status.status === 'completed') {
            resolve(status)
            return
          }
          
          // Check if analysis failed
          if (status.status === 'failed') {
            reject(new AnalysisAPIError(
              `Analysis failed: ${status.error_message || 'Unknown error'}`,
              500,
              status
            ))
            return
          }
          
          // Check timeout
          if (Date.now() - startTime > timeoutMs) {
            reject(new AnalysisAPIError(
              'Analysis polling timed out',
              408,
              { timeout: timeoutMs, elapsed: Date.now() - startTime }
            ))
            return
          }
          
          // Continue polling
          setTimeout(poll, intervalMs)
          
        } catch (error) {
          reject(error)
        }
      }
      
      poll()
    })
  }
  
  /**
   * Check API health for analysis service
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
export const analysisAPI = new AnalysisAPI()

// Export utilities for error handling
export const isAnalysisAPIError = (error: any): error is AnalysisAPIError => {
  return error instanceof AnalysisAPIError || isAPIError(error)
}

export const getAnalysisErrorMessage = (error: any): string => {
  return getErrorMessage(error)
}