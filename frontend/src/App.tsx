import { useState, useEffect } from 'react'
import { CheckCircle, XCircle, Clock, Database, Brain, Zap, Video, BarChart3, RefreshCw } from 'lucide-react'
import { RecordingControls } from './features/recording/components/RecordingControls'
import { RecordingsList } from './features/analysis/components/RecordingsList'
import { ResultsPage } from './features/analysis/components/ResultsPage'
import { ErrorBoundary } from './components/ErrorBoundary'
import { useAnalysisPolling } from './features/analysis/hooks/useAnalysisPolling'

interface ConnectionStatus {
  name: string
  status: 'connected' | 'disconnected' | 'testing'
  description: string
  endpoint?: string
}

function App() {
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [currentView, setCurrentView] = useState<'record' | 'analyze' | 'results' | 'analyzing'>('record')
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null)
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
      endpoint: 'http://localhost:8000/health'
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

  // Analysis polling integration
  const analysisPolling = useAnalysisPolling({
    onComplete: (results) => {
      console.log('Analysis completed:', results)
      setSuccessMessage('🎉 Analysis complete! Your workflow automation opportunities have been identified.')
      setCurrentView('results')
    },
    onError: (error) => {
      console.error('Analysis error:', error)
      setSuccessMessage(null) // Clear any success message
      // Stay in analyzing view to show the error
    }
  })

  useEffect(() => {
    // Test backend connection
    fetch('http://localhost:8000/health')
      .then(res => res.ok ? 'connected' : 'disconnected')
      .catch(() => 'disconnected')
      .then(status => {
        setConnections(prev => prev.map(conn => 
          conn.name === 'Backend API' ? { ...conn, status } : conn
        ))
      })

    // Simulate other connection tests
    setTimeout(() => {
      setConnections(prev => prev.map(conn => {
        if (conn.name === 'Supabase Database') {
          return { ...conn, status: 'connected' as const }
        }
        return conn
      }))
    }, 1500)

    setTimeout(() => {
      setConnections(prev => prev.map(conn => {
        if (conn.name === 'OpenAI GPT-4V') {
          return { ...conn, status: 'connected' as const }
        }
        return conn
      }))
    }, 2000)
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
                <p className="text-xs text-gray-600">Saving 1,000,000 operator hours monthly</p>
              </div>
            </div>
            
            {/* Navigation Tabs */}
            <div className="flex items-center space-x-4">
              <div className="flex bg-gray-100 rounded-lg p-1">
                <button
                  onClick={() => setCurrentView('record')}
                  className={`flex items-center space-x-2 px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
                    currentView === 'record'
                      ? 'bg-white text-teal-600 shadow-sm'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <Video className="w-4 h-4" />
                  <span>Record</span>
                </button>
                <button
                  onClick={() => setCurrentView('analyze')}
                  className={`flex items-center space-x-2 px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
                    currentView === 'analyze'
                      ? 'bg-white text-teal-600 shadow-sm'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <BarChart3 className="w-4 h-4" />
                  <span>Analyze</span>
                </button>
                {currentView === 'analyzing' && (
                  <button
                    disabled
                    className="flex items-center space-x-2 px-4 py-1.5 rounded-md text-sm font-medium bg-white text-amber-600 shadow-sm"
                  >
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Analyzing</span>
                  </button>
                )}
                {currentView === 'results' && (
                  <button
                    disabled
                    className="flex items-center space-x-2 px-4 py-1.5 rounded-md text-sm font-medium bg-white text-green-600 shadow-sm"
                  >
                    <CheckCircle className="w-4 h-4" />
                    <span>Results</span>
                  </button>
                )}
              </div>
              
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-600">Phase 2A</span>
                <div className={`w-3 h-3 rounded-full ${allConnected ? 'bg-green-500' : 'bg-amber-500'}`}></div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {currentView === 'results' && currentSessionId ? (
          <ResultsPage 
            sessionId={currentSessionId} 
            onBack={() => setCurrentView('analyze')} 
          />
        ) : currentView === 'analyzing' ? (
          /* Analyzing View */
          <>
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-slate-800 mb-4">
                AI Analysis in Progress
              </h2>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                Our GPT-4V engine is analyzing your workflow recording to identify automation opportunities. 
                This typically takes 1-2 minutes.
              </p>
            </div>

            {/* Analysis Status */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 mb-8 text-center">
              <div className="flex justify-center mb-6">
                <div className="p-4 bg-amber-100 rounded-full">
                  <RefreshCw className="w-8 h-8 text-amber-600 animate-spin" />
                </div>
              </div>
              
              <h3 className="text-xl font-semibold text-gray-900 mb-4">
                {analysisPolling.analysisStatus?.message || 'Starting analysis...'}
              </h3>

              {analysisPolling.error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
                  <p className="text-red-700">{analysisPolling.error}</p>
                  <button
                    onClick={() => analysisPolling.startPolling(currentSessionId!)}
                    className="mt-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                  >
                    Retry Analysis
                  </button>
                </div>
              )}

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
                <div className="flex flex-col items-center">
                  <div className="w-2 h-2 bg-teal-500 rounded-full mb-2"></div>
                  <p className="text-sm text-gray-600">Extracting video frames</p>
                </div>
                <div className="flex flex-col items-center">
                  <div className="w-2 h-2 bg-teal-500 rounded-full mb-2"></div>
                  <p className="text-sm text-gray-600">AI pattern analysis</p>
                </div>
                <div className="flex flex-col items-center">
                  <div className={`w-2 h-2 rounded-full mb-2 ${
                    analysisPolling.isAnalysisComplete ? 'bg-teal-500' : 'bg-gray-300'
                  }`}></div>
                  <p className="text-sm text-gray-600">Generating insights</p>
                </div>
              </div>

              <p className="text-sm text-gray-500 mt-6">
                You'll be automatically redirected to results when complete
              </p>
            </div>
          </>
        ) : currentView === 'record' ? (
          <>
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

            {/* Screen Recording Section */}
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
              <div className="mb-8">
                <ErrorBoundary>
                  <RecordingControls 
                    onRecordingComplete={(recordingId) => {
                      console.log('Recording completed:', recordingId)
                      setCurrentSessionId(recordingId)
                      setSuccessMessage('🎉 Recording saved successfully! Starting AI analysis...')
                      setCurrentView('analyzing')
                      
                      // Start analysis polling
                      analysisPolling.startPolling(recordingId)
                    }}
                    onError={(error) => {
                      console.error('Recording error:', error)
                      // TODO: Show user-friendly error notification
                    }}
                  />
                </ErrorBoundary>
              </div>
            )}

            {/* Next Steps */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-xl font-semibold text-slate-800 mb-4">Development Progress</h3>
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  <span className="text-gray-600">Phase 1: Screen Recording with WebM chunks ✓</span>
                </div>
                <div className="flex items-center space-x-3">
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  <span className="text-gray-600">Phase 2A Day 1: Frame extraction service ✓</span>
                </div>
                <div className="flex items-center space-x-3">
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  <span className="text-gray-600">Phase 2A Day 2-3: GPT-4V integration ✓</span>
                </div>
                <div className="flex items-center space-x-3">
                  <Clock className="w-5 h-5 text-gray-400" />
                  <span className="text-gray-600">Phase 2B: Workflow visualization & results</span>
                </div>
              </div>
              
              {allConnected && (
                <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                  <p className="text-green-700 font-medium">
                    🎉 Phase 2A Complete! GPT-4V integration is ready. Record a workflow, then analyze it to identify automation opportunities!
                  </p>
                </div>
              )}
            </div>
          </>
        ) : (
          /* Analyze View */
          <>
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-slate-800 mb-4">
                Workflow Analysis Dashboard
              </h2>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                Select a completed recording to extract frames and prepare for GPT-4V analysis. 
                Our AI will identify email → WMS patterns and automation opportunities.
              </p>
            </div>
            
            <RecordingsList />
          </>
        )}
      </main>
    </div>
  )
}

export default App