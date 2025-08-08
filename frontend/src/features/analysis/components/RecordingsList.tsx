/**
 * Recordings List Component
 * Shows completed recordings and allows triggering analysis
 * Phase 2A: Testing frame extraction on recorded sessions
 */

import React, { useState, useEffect } from 'react'
import { Film, Clock, HardDrive, Calendar, ChevronRight, RefreshCw, Eye, Trash2, Shield, BarChart3 } from 'lucide-react'
import { AnalysisButton } from './AnalysisButton'
import { WorkflowAnalysis } from './WorkflowAnalysis'
import { PrivacyModal } from '../../../components/PrivacyModal'
import { recordingAPI } from '../../recording/services/recordingAPI'

interface Recording {
  id: string
  title: string
  status: string
  duration_seconds: number
  file_size_bytes: number
  created_at: string
  completed_at?: string
  privacy_settings?: Record<string, any>
  has_analysis?: boolean
}

export const RecordingsList: React.FC = () => {
  const [recordings, setRecordings] = useState<Recording[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedRecording, setSelectedRecording] = useState<string | null>(null)
  const [activeAnalysisId, setActiveAnalysisId] = useState<string | null>(null)
  const [showResults, setShowResults] = useState(false)
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const [privacyModalId, setPrivacyModalId] = useState<string | null>(null)

  const fetchRecordings = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await recordingAPI.listRecordings({
        status: 'completed',
        page_size: 10
      })
      
      if (response?.recordings) {
        setRecordings(response.recordings)
      } else {
        setRecordings([])
      }
    } catch (err: any) {
      console.error('Failed to fetch recordings:', err)
      setError(err.message || 'Failed to load recordings')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchRecordings()
  }, [])

  const handleDeleteRecording = async (recordingId: string) => {
    if (!confirm('Are you sure you want to delete this recording? This action cannot be undone.')) {
      return
    }

    setDeletingId(recordingId)
    try {
      await recordingAPI.deleteRecording(recordingId)
      setRecordings(prev => prev.filter(r => r.id !== recordingId))
    } catch (err: any) {
      console.error('Failed to delete recording:', err)
      setError(err.message || 'Failed to delete recording')
    } finally {
      setDeletingId(null)
    }
  }

  const handleViewResults = (recordingId: string) => {
    // Navigate to results - this would integrate with the main app routing
    console.log('View results for recording:', recordingId)
    // For now, just show the analysis button
    setSelectedRecording(recordingId)
  }

  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const formatFileSize = (bytes: number): string => {
    const mb = bytes / (1024 * 1024)
    return `${mb.toFixed(1)} MB`
  }

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString)
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
  }

  const getStatusBadge = (status: string) => {
    const statusColors = {
      'completed': 'bg-green-100 text-green-800',
      'recording': 'bg-blue-100 text-blue-800',
      'processing': 'bg-yellow-100 text-yellow-800',
      'failed': 'bg-red-100 text-red-800',
      'uploading': 'bg-purple-100 text-purple-800'
    }
    
    const colorClass = statusColors[status as keyof typeof statusColors] || 'bg-gray-100 text-gray-800'
    
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colorClass}`}>
        {status}
      </span>
    )
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-8">
        <div className="flex items-center justify-center space-x-3">
          <RefreshCw className="w-5 h-5 animate-spin text-blue-600" />
          <span className="text-gray-600">Loading recordings...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-lg border border-red-200 p-8">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={fetchRecordings}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  if (recordings.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-8">
        <div className="text-center">
          <Film className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 mb-4">No completed recordings found</p>
          <p className="text-sm text-gray-500">
            Complete a screen recording first, then come back to analyze it
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900">Completed Recordings</h2>
          <button
            onClick={fetchRecordings}
            className="flex items-center space-x-2 px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm text-gray-700 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Refresh</span>
          </button>
        </div>
        
        <p className="text-sm text-gray-600">
          Select a recording below to extract frames and prepare for GPT-4V analysis
        </p>
      </div>

      {/* Recordings List */}
      <div className="space-y-4">
        {recordings.map((recording) => (
          <div
            key={recording.id}
            className={`bg-white rounded-lg shadow-lg border transition-all ${
              selectedRecording === recording.id
                ? 'border-blue-500 ring-2 ring-blue-200'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div
              className="p-6 cursor-pointer"
              onClick={() => setSelectedRecording(
                selectedRecording === recording.id ? null : recording.id
              )}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-start space-x-4">
                  <div className="bg-blue-100 rounded-lg p-3">
                    <Film className="w-6 h-6 text-blue-600" />
                  </div>
                  
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 mb-1">
                      {recording.title}
                    </h3>
                    
                    <div className="flex items-center space-x-4 text-sm text-gray-600">
                      <div className="flex items-center space-x-1">
                        <Clock className="w-4 h-4" />
                        <span>{formatDuration(recording.duration_seconds)}</span>
                      </div>
                      
                      <div className="flex items-center space-x-1">
                        <HardDrive className="w-4 h-4" />
                        <span>{formatFileSize(recording.file_size_bytes)}</span>
                      </div>
                      
                      <div className="flex items-center space-x-1">
                        <Calendar className="w-4 h-4" />
                        <span>{formatDate(recording.created_at)}</span>
                      </div>
                    </div>
                    
                    <div className="mt-3 flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        {getStatusBadge(recording.status)}
                        {recording.has_analysis && (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-teal-100 text-teal-800">
                            <BarChart3 className="w-3 h-3 mr-1" />
                            Analyzed
                          </span>
                        )}
                      </div>
                      
                      {/* Action Buttons */}
                      <div className="flex items-center space-x-2">
                        {recording.has_analysis && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              handleViewResults(recording.id)
                            }}
                            className="flex items-center space-x-1 px-3 py-1.5 text-xs bg-teal-100 hover:bg-teal-200 text-teal-800 rounded-lg transition-colors"
                          >
                            <Eye className="w-3 h-3" />
                            <span>View Results</span>
                          </button>
                        )}
                        
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            setPrivacyModalId(recording.id)
                          }}
                          className="flex items-center space-x-1 px-3 py-1.5 text-xs bg-blue-100 hover:bg-blue-200 text-blue-800 rounded-lg transition-colors"
                        >
                          <Shield className="w-3 h-3" />
                          <span>Privacy</span>
                        </button>
                        
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            handleDeleteRecording(recording.id)
                          }}
                          disabled={deletingId === recording.id}
                          className="flex items-center space-x-1 px-3 py-1.5 text-xs bg-red-100 hover:bg-red-200 text-red-800 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          <Trash2 className="w-3 h-3" />
                          <span>{deletingId === recording.id ? 'Deleting...' : 'Delete'}</span>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
                
                <ChevronRight
                  className={`w-5 h-5 text-gray-400 transition-transform ${
                    selectedRecording === recording.id ? 'rotate-90' : ''
                  }`}
                />
              </div>
            </div>
            
            {/* Analysis Panel (Expanded) */}
            {selectedRecording === recording.id && (
              <div className="border-t border-gray-200 p-6 bg-gray-50">
                <AnalysisButton
                  recordingId={recording.id}
                  onAnalysisComplete={(analysisId) => {
                    console.log(`Analysis ${analysisId} started for recording ${recording.id}`)
                    setActiveAnalysisId(analysisId)
                    setShowResults(true)
                  }}
                />
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Instructions for Testing */}
      {recordings.length > 0 && (
        <div className="bg-blue-50 rounded-lg border border-blue-200 p-6">
          <h3 className="font-semibold text-blue-900 mb-2">
            📋 Testing Instructions
          </h3>
          <div className="text-sm text-blue-800 space-y-1">
            <p>• Select a recording above to expand analysis options</p>
            <p>• Click "Full Analysis" for complete GPT-4V workflow analysis</p>
            <p>• Results will show real automation opportunities (no mock data)</p>
            <p>• If analysis fails, error messages will be displayed transparently</p>
          </div>
        </div>
      )}

      {/* Analysis Results Modal */}
      {showResults && activeAnalysisId && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="max-w-6xl w-full max-h-[90vh] overflow-y-auto">
            <WorkflowAnalysis
              analysisId={activeAnalysisId}
              onClose={() => {
                setShowResults(false)
                setActiveAnalysisId(null)
              }}
            />
          </div>
        </div>
      )}

      {/* Privacy Settings Modal */}
      {privacyModalId && (
        <PrivacyModal
          isOpen={true}
          onClose={() => setPrivacyModalId(null)}
          recordingId={privacyModalId}
          recordingTitle={recordings.find(r => r.id === privacyModalId)?.title || 'Recording'}
          currentSettings={recordings.find(r => r.id === privacyModalId)?.privacy_settings}
        />
      )}
    </div>
  )
}