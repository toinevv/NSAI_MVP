/**
 * ResultsPage - Route for displaying analysis results
 * Wraps the existing MinimalResultsPage component
 */

import React from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { AlertCircle } from 'lucide-react'
import { MinimalResultsPage } from '../features/analysis/components/MinimalResultsPage'

export const ResultsPage: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>()
  const navigate = useNavigate()

  // Redirect if no sessionId
  if (!sessionId) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h1 className="text-xl font-semibold text-gray-900 mb-2">No Session ID</h1>
          <p className="text-gray-600 mb-4">Unable to display results without a session ID.</p>
          <button
            onClick={() => navigate('/')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Back to Recording
          </button>
        </div>
      </div>
    )
  }

  return (
    <MinimalResultsPage 
      sessionId={sessionId} 
      onBack={() => navigate('/')} 
    />
  )
}