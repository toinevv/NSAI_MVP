import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { SettingsProvider } from './contexts/SettingsContext'
import { AuthProvider, useAuth } from './features/auth/AuthContext'
import { AuthComponent } from './features/auth/AuthComponent'
import { RecordPage } from './pages/RecordPage'
import { AnalyzingPage } from './pages/AnalyzingPage'
import { ResultsPage } from './pages/ResultsPage'
import { RecordingsList } from './features/analysis/components/RecordingsList'
import { SettingsPage } from './features/settings/components/SettingsPage'

function AppContent() {
  const { isAuthenticated, loading } = useAuth()

  // If auth is loading, show loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Initializing authentication...</p>
        </div>
      </div>
    )
  }
  
  // If not authenticated, show auth component
  if (!isAuthenticated) {
    return (
      <SettingsProvider>
        <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
          <main className="container mx-auto px-4 py-8">
            <div className="max-w-4xl mx-auto">
              <div className="text-center mb-8">
                <h1 className="text-4xl font-bold text-slate-800 mb-4">
                  🎯 NewSystem.AI
                </h1>
                <p className="text-lg text-gray-600">
                  Sign in to access workflow analysis and automation tools
                </p>
              </div>
              <AuthComponent />
            </div>
          </main>
        </div>
      </SettingsProvider>
    )
  }

  return (
    <SettingsProvider>
      <Router>
        <Routes>
          {/* Main recording page */}
          <Route path="/" element={<RecordPage />} />
          
          {/* Analysis progress page - shows immediately after recording */}
          <Route path="/analyzing/:sessionId" element={<AnalyzingPage />} />
          
          {/* Results display page */}
          <Route path="/results/:sessionId" element={<ResultsPage />} />
          
          {/* Analysis list page */}
          <Route 
            path="/analyze" 
            element={
              <div className="min-h-screen bg-gray-50">
                <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                  <div className="text-center mb-12">
                    <h2 className="text-3xl font-bold text-slate-800 mb-4">
                      Workflow Analysis Dashboard
                    </h2>
                    <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                      Select a completed recording to extract frames and prepare for GPT-4V analysis. 
                      Our AI will identify email → WMS patterns and automation opportunities.
                    </p>
                  </div>
                  
                  <RecordingsList 
                    onViewResults={(sessionId) => window.location.href = `/results/${sessionId}`}
                    onNavigateToSettings={() => window.location.href = '/settings'}
                  />
                </main>
              </div>
            } 
          />
          
          {/* Settings page */}
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </Router>
    </SettingsProvider>
  )
}

// Root App component with AuthProvider
function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}

export default App