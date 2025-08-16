/**
 * Centralized API Client with Supabase Authentication
 * Provides shared configuration and utilities for all API services
 * Handles JWT authentication, environment variables, error handling, and request/response processing
 */

import { auth } from './supabase'

// Environment configuration
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  VERSION: import.meta.env.VITE_API_VERSION || 'v1',
  TIMEOUT: parseInt(import.meta.env.VITE_API_TIMEOUT || '300000'), // 5 minutes - GPT-4V analysis can take time
} as const

// Get full API URL for a given path
export const getApiUrl = (path: string): string => {
  const cleanPath = path.startsWith('/') ? path.slice(1) : path
  return `${API_CONFIG.BASE_URL}/api/${API_CONFIG.VERSION}/${cleanPath}`
}

// Get base URL for health checks and other non-versioned endpoints
export const getBaseUrl = (path: string = ''): string => {
  const cleanPath = path.startsWith('/') ? path.slice(1) : path
  return `${API_CONFIG.BASE_URL}/${cleanPath}`.replace(/\/$/, '')
}

// Common API error class
export class APIError extends Error {
  public status?: number
  public details?: any
  public endpoint?: string

  constructor(
    message: string,
    status?: number,
    details?: any,
    endpoint?: string
  ) {
    super(message)
    this.name = 'APIError'
    this.status = status
    this.details = details
    this.endpoint = endpoint
  }

  // Check if error is a network/connection error
  isNetworkError(): boolean {
    return this.status === 0 || !this.status
  }

  // Check if error is a client error (4xx)
  isClientError(): boolean {
    return this.status ? this.status >= 400 && this.status < 500 : false
  }

  // Check if error is a server error (5xx)
  isServerError(): boolean {
    return this.status ? this.status >= 500 : false
  }
}

// Request configuration interface
export interface RequestConfig extends RequestInit {
  timeout?: number
  retries?: number
  retryDelay?: number
}

// Response wrapper interface
export interface APIResponse<T> {
  data: T
  status: number
  statusText: string
  headers: Headers
}

// Enhanced fetch with timeout support
const fetchWithTimeout = async (
  url: string, 
  config: RequestConfig = {}
): Promise<Response> => {
  const { timeout = API_CONFIG.TIMEOUT, ...fetchConfig } = config

  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), timeout)

  try {
    const response = await fetch(url, {
      ...fetchConfig,
      signal: controller.signal,
    })
    clearTimeout(timeoutId)
    return response
  } catch (error) {
    clearTimeout(timeoutId)
    
    if (error instanceof Error && error.name === 'AbortError') {
      throw new APIError('Request timeout', 0, { timeout }, url)
    }
    throw error
  }
}

// Retry logic for failed requests
const fetchWithRetry = async (
  url: string,
  config: RequestConfig = {}
): Promise<Response> => {
  const { retries = 0, retryDelay = 1000, ...fetchConfig } = config
  let lastError: Error = new Error('Request failed')

  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const response = await fetchWithTimeout(url, fetchConfig)
      
      // Don't retry client errors (4xx), only server errors and network issues
      if (response.ok || (response.status >= 400 && response.status < 500)) {
        return response
      }
      
      lastError = new Error(`HTTP ${response.status}: ${response.statusText}`)
      
      // If this was the last attempt, don't wait
      if (attempt < retries) {
        await new Promise(resolve => setTimeout(resolve, retryDelay * Math.pow(2, attempt)))
      }
    } catch (error) {
      lastError = error instanceof Error ? error : new Error('Unknown error')
      
      // If this was the last attempt, don't wait
      if (attempt < retries) {
        await new Promise(resolve => setTimeout(resolve, retryDelay * Math.pow(2, attempt)))
      }
    }
  }

  throw lastError
}

// Main API client function with authentication
export const apiClient = async <T>(
  endpoint: string,
  config: RequestConfig = {}
): Promise<T> => {
  const url = endpoint.startsWith('http') ? endpoint : getApiUrl(endpoint)
  
  // Get authentication token from Supabase
  const accessToken = await auth.getAccessToken()
  
  // Build headers with authentication
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(config.headers as Record<string, string>),
  }
  
  // Add authorization header if we have a token
  if (accessToken) {
    headers['Authorization'] = `Bearer ${accessToken}`
  }
  
  const defaultConfig: RequestConfig = {
    ...config,
    headers,
  }

  try {
    const response = await fetchWithRetry(url, defaultConfig)
    
    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`
      let errorDetails = null
      
      try {
        const errorData = await response.json()
        errorMessage = errorData.detail || errorData.message || errorMessage
        errorDetails = errorData
      } catch {
        // Response wasn't JSON, use status text
      }
      
      throw new APIError(errorMessage, response.status, errorDetails, url)
    }
    
    // Handle empty responses
    const contentType = response.headers.get('Content-Type')
    if (!contentType || !contentType.includes('application/json')) {
      return {} as T
    }
    
    return await response.json()
    
  } catch (error) {
    if (error instanceof APIError) {
      throw error
    }
    
    // Network or other errors
    throw new APIError(
      error instanceof Error ? error.message : 'Network error occurred',
      0,
      error,
      url
    )
  }
}

// Convenience methods for common HTTP verbs
export const get = <T>(endpoint: string, config?: RequestConfig): Promise<T> => {
  return apiClient<T>(endpoint, { ...config, method: 'GET' })
}

export const post = <T>(
  endpoint: string, 
  data?: any, 
  config?: RequestConfig
): Promise<T> => {
  return apiClient<T>(endpoint, {
    ...config,
    method: 'POST',
    body: data ? JSON.stringify(data) : undefined,
  })
}

export const put = <T>(
  endpoint: string, 
  data?: any, 
  config?: RequestConfig
): Promise<T> => {
  return apiClient<T>(endpoint, {
    ...config,
    method: 'PUT',
    body: data ? JSON.stringify(data) : undefined,
  })
}

export const del = <T>(endpoint: string, config?: RequestConfig): Promise<T> => {
  return apiClient<T>(endpoint, { ...config, method: 'DELETE' })
}

// Health check utility
export const checkHealth = async (): Promise<{
  status: string
  service: string
  version: string
  environment: string
  components: Record<string, string>
  configuration?: Record<string, any>
}> => {
  try {
    const response = await fetch(getBaseUrl('health'))
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`)
    }
    return await response.json()
  } catch (error) {
    throw new APIError(
      error instanceof Error ? error.message : 'Health check failed',
      0,
      error,
      'health'
    )
  }
}

// Utility functions for error handling
export const isAPIError = (error: any): error is APIError => {
  return error instanceof APIError
}

export const getErrorMessage = (error: any): string => {
  if (isAPIError(error)) {
    return error.message
  }
  return error instanceof Error ? error.message : 'An unknown error occurred'
}

// Note: RequestConfig and APIResponse types are already exported above as interfaces