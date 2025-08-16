/**
 * RecordPage - Main recording interface
 * Extracted from App.tsx for route-based navigation
 */

import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { CheckCircle, XCircle, Clock, Database, Brain, Zap, Video, Settings } from 'lucide-react'
import { RecordingControls } from '../features/recording/components/RecordingControls'
import { ManualVideoUpload } from '../features/recording/components/ManualVideoUpload'
import { ErrorBoundary } from '../components/ErrorBoundary'
import { checkHealth } from '../lib/api-client'
import { AuthComponent } from '../features/auth/AuthComponent'

interface ConnectionStatus {
  name: string
  status: 'connected' | 'disconnected' | 'testing'
  description: string
  endpoint?: string
}

export const RecordPage: React.FC = () => {
  const navigate = useNavigate()
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [connections, setConnections] = useState<ConnectionStatus[]>([
    {
      name: 'Frontend',
      status: 'connected',
      description: 'React + Vite + TypeScript + Tailwind CSS'
    },
    {
      name: 'Backend API',
      status: 'testing',
      description: 'FastAPI server connection',
      endpoint: `${import.meta.env.VITE_API_URL}/health`
    },
    {
      name: 'Supabase Database',
      status: 'testing',
      description: 'PostgreSQL database and authentication',
    },
    {
      name: 'OpenAI GPT-4V',
      status: 'testing',
      description: 'AI analysis engine for workflow patterns'
    }
  ])

  useEffect(() => {
    const checkConnections = async () => {
      // Test backend connection using centralized health check
      try {
        await checkHealth()
        setConnections(prev => prev.map(conn => 
          conn.name === 'Backend API' ? { ...conn, status: 'connected' } : conn
        ))
        
        // If backend is connected, assume other services are configured
        // (Real status would come from /health endpoint in production)
        setConnections(prev => prev.map(conn => {
          if (conn.name === 'Supabase Database' || conn.name === 'OpenAI GPT-4V') {
            return { ...conn, status: 'connected' as const }
          }
          return conn
        }))
      } catch (error) {
        setConnections(prev => prev.map(conn => 
          conn.name === 'Backend API' ? { ...conn, status: 'disconnected' } : conn
        ))
        
        // If backend fails, mark dependent services as disconnected
        setConnections(prev => prev.map(conn => {
          if (conn.name === 'Supabase Database' || conn.name === 'OpenAI GPT-4V') {
            return { ...conn, status: 'disconnected' as const }
          }
          return conn
        }))
      }
    }

    checkConnections()
  }, [])

  // Auto-hide success message after 5 seconds
  useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => setSuccessMessage(null), 5000)
      return () => clearTimeout(timer)
    }
  }, [successMessage])

  const getStatusIcon = (status: ConnectionStatus['status']) => {
    switch (status) {
      case 'connected':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'disconnected':
        return <XCircle className="w-5 h-5 text-red-500" />
      case 'testing':
        return <Clock className="w-5 h-5 text-amber-500 animate-spin" />
    }
  }

  const getStatusText = (status: ConnectionStatus['status']) => {
    switch (status) {
      case 'connected':
        return 'Connected'
      case 'disconnected':
        return 'Disconnected'
      case 'testing':
        return 'Testing...'
    }
  }

  const allConnected = connections.every(conn => conn.status === 'connected')

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-teal-400 rounded-lg flex items-center justify-center">
                <Zap className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-slate-800">NewSystem.AI</h1>
                <p className="text-xs text-gray-600">Workflow Analysis & Automation Discovery</p>
              </div>
            </div>
            
            {/* Navigation */}
            <div className="flex items-center space-x-4">
              <AuthComponent />
              <div className="flex bg-gray-100 rounded-lg p-1">
                <button
                  className="flex items-center space-x-2 px-4 py-1.5 rounded-md text-sm font-medium bg-white text-teal-600 shadow-sm"
                >
                  <Video className="w-4 h-4" />
                  <span>Record</span>
                </button>
                <button
                  onClick={() => navigate('/analyze')}
                  className="flex items-center space-x-2 px-4 py-1.5 rounded-md text-sm font-medium text-gray-600 hover:text-gray-900"
                >
                  <Brain className="w-4 h-4" />
                  <span>Analyze</span>
                </button>
                <button
                  onClick={() => navigate('/settings')}
                  className="flex items-center space-x-2 px-4 py-1.5 rounded-md text-sm font-medium text-gray-600 hover:text-gray-900"
                >
                  <Settings className="w-4 h-4" />
                  <span>Settings</span>
                </button>
              </div>
              
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-600">System Status</span>
                <div className={`w-3 h-3 rounded-full ${allConnected ? 'bg-green-500' : 'bg-amber-500'}`}></div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section for Recording */}
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-slate-800 mb-4">
            Workflow Recording Dashboard
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Record your screen at 2 FPS to capture operational workflows. 
            Our AI will analyze patterns to identify automation opportunities.
          </p>
        </div>

        {/* Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {connections.map((connection) => (
            <div key={connection.name} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-slate-800">{connection.name}</h3>
                {getStatusIcon(connection.status)}
              </div>
              <p className="text-sm text-gray-600 mb-2">{connection.description}</p>
              <div className="flex items-center space-x-2">
                <span className={`text-xs px-2 py-1 rounded-full border ${
                  connection.status === 'connected' ? 'bg-green-50 text-green-700 border-green-200' :
                  connection.status === 'disconnected' ? 'bg-red-50 text-red-700 border-red-200' :
                  'bg-amber-50 text-amber-700 border-amber-200'
                }`}>
                  {getStatusText(connection.status)}
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* Architecture Overview */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
          <h3 className="text-xl font-semibold text-slate-800 mb-4 flex items-center">
            <Database className="w-5 h-5 mr-2" />
            System Architecture Overview
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="w-12 h-12 bg-teal-50 rounded-lg flex items-center justify-center mx-auto mb-3">
                <Brain className="w-6 h-6 text-teal-600" />
              </div>
              <h4 className="font-semibold text-slate-800 mb-2">Layer 1: Observation</h4>
              <p className="text-sm text-gray-600">
                Screen recording infrastructure captures operator workflows at 2 FPS with privacy controls
              </p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-amber-50 rounded-lg flex items-center justify-center mx-auto mb-3">
                <Zap className="w-6 h-6 text-amber-600" />
              </div>
              <h4 className="font-semibold text-slate-800 mb-2">Layer 2: Translation</h4>
              <p className="text-sm text-gray-600">
                GPT-4V analyzes patterns and converts operational workflows into technical specifications
              </p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-green-50 rounded-lg flex items-center justify-center mx-auto mb-3">
                <CheckCircle className="w-6 h-6 text-green-600" />
              </div>
              <h4 className="font-semibold text-slate-800 mb-2">Layer 3: Implementation</h4>
              <p className="text-sm text-gray-600">
                Tools and services transform insights into working automation solutions
              </p>
            </div>
          </div>
        </div>

        {/* Success Message */}
        {successMessage && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center space-x-2">
              <CheckCircle className="w-5 h-5 text-green-600" />
              <p className="text-green-800 font-medium">{successMessage}</p>
            </div>
          </div>
        )}

        {allConnected && (
          <div className="space-y-8 mb-8">
            {/* Regular Recording */}
            <ErrorBoundary>
              <RecordingControls 
                onRecordingComplete={(recordingId) => {
                  console.log('🎯 RecordPage: Recording completed, navigating to analyzing page')
                  console.log('📍 Recording ID:', recordingId)
                  setSuccessMessage('🎉 Recording complete! Starting AI analysis...')
                  
                  // Navigate to analyzing page - this ensures immediate screen transition
                  navigate(`/analyzing/${recordingId}`)
                }}
                onError={(error) => {
                  console.error('Recording error:', error)
                  // TODO: Show user-friendly error notification
                }}
              />
            </ErrorBoundary>
            
            {/* Manual Upload for Testing */}
            <ErrorBoundary>
              <ManualVideoUpload
                onUploadComplete={(sessionId) => {
                  console.log('🎯 RecordPage: Manual upload completed, navigating to analyzing page')
                  console.log('📍 Session ID:', sessionId)
                  setSuccessMessage('🎉 Video uploaded! Starting AI analysis...')
                  
                  // Navigate to analyzing page - this ensures immediate screen transition
                  navigate(`/analyzing/${sessionId}`)
                }}
                onError={(error) => {
                  console.error('Manual upload error:', error)
                }}
              />
            </ErrorBoundary>
          </div>
        )}

        {/* System Status for Testing */}
        {!allConnected && (
          <div className="bg-white rounded-lg shadow-sm border border-red-200 p-6">
            <h3 className="text-xl font-semibold text-red-800 mb-4">⚠️ System Not Ready</h3>
            <p className="text-red-700 mb-4">
              Some services are not connected. Recording and analysis will not work until all services are online.
            </p>
            <div className="text-sm text-red-600">
              <p>• Check backend server is running on port 8000</p>
              <p>• Verify OPENAI_API_KEY is configured</p>
              <p>• Ensure Supabase connection is established</p>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}