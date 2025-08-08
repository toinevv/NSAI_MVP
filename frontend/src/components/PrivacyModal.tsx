/**
 * Privacy Settings Modal Component
 * Provides UI for configuring recording privacy settings
 * Integrates with PUT /recordings/{id}/privacy API endpoint
 */

import React, { useState, useEffect } from 'react'
import { X, Shield, Eye, EyeOff, AlertTriangle, Check, Loader2 } from 'lucide-react'
import { recordingAPI, type PrivacySettings } from '../features/recording/services/recordingAPI'

interface PrivacyModalProps {
  isOpen: boolean
  onClose: () => void
  recordingId: string
  recordingTitle: string
  currentSettings?: Partial<PrivacySettings>
}

export const PrivacyModal: React.FC<PrivacyModalProps> = ({
  isOpen,
  onClose,
  recordingId,
  recordingTitle,
  currentSettings = {}
}) => {
  const [settings, setSettings] = useState<PrivacySettings>({
    blur_passwords: currentSettings.blur_passwords ?? true,
    exclude_personal_info: currentSettings.exclude_personal_info ?? true,
    custom_exclusions: currentSettings.custom_exclusions ?? []
  })
  
  const [customExclusionInput, setCustomExclusionInput] = useState('')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  // Reset form when modal opens/closes
  useEffect(() => {
    if (isOpen) {
      setSettings({
        blur_passwords: currentSettings.blur_passwords ?? true,
        exclude_personal_info: currentSettings.exclude_personal_info ?? true,
        custom_exclusions: currentSettings.custom_exclusions ?? []
      })
      setCustomExclusionInput('')
      setError(null)
      setSuccess(false)
    }
  }, [isOpen, currentSettings])

  const handleSaveSettings = async () => {
    try {
      setSaving(true)
      setError(null)

      await recordingAPI.updatePrivacySettings(recordingId, settings)
      
      setSuccess(true)
      setTimeout(() => {
        onClose()
      }, 1500) // Close after showing success message

    } catch (err: any) {
      console.error('Failed to update privacy settings:', err)
      setError(err.message || 'Failed to update privacy settings')
    } finally {
      setSaving(false)
    }
  }

  const addCustomExclusion = () => {
    const trimmed = customExclusionInput.trim()
    if (trimmed && !settings.custom_exclusions.includes(trimmed)) {
      setSettings(prev => ({
        ...prev,
        custom_exclusions: [...prev.custom_exclusions, trimmed]
      }))
      setCustomExclusionInput('')
    }
  }

  const removeCustomExclusion = (exclusion: string) => {
    setSettings(prev => ({
      ...prev,
      custom_exclusions: prev.custom_exclusions.filter(e => e !== exclusion)
    }))
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      addCustomExclusion()
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Shield className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Privacy Settings</h2>
                <p className="text-sm text-gray-600">{recordingTitle}</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X className="w-5 h-5 text-gray-500" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Success Message */}
          {success && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-center space-x-2">
                <Check className="w-5 h-5 text-green-600" />
                <p className="text-green-800 font-medium">Privacy settings updated successfully!</p>
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-start space-x-2">
                <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-red-800 font-medium">Failed to update privacy settings</p>
                  <p className="text-red-700 text-sm">{error}</p>
                </div>
              </div>
            </div>
          )}

          {/* Privacy Settings Form */}
          <div className="space-y-6">
            {/* Automatic Password Blurring */}
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <EyeOff className="w-4 h-4 text-gray-600" />
                    <h3 className="font-medium text-gray-900">Blur Passwords & Sensitive Fields</h3>
                  </div>
                  <p className="text-sm text-gray-600 mb-3">
                    Automatically detect and blur password fields, credit card numbers, and other sensitive input during analysis.
                  </p>
                  <div className="text-xs text-gray-500">
                    <strong>Recommended:</strong> Enabled for all workflows to protect sensitive information
                  </div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer ml-4">
                  <input
                    type="checkbox"
                    checked={settings.blur_passwords}
                    onChange={(e) => setSettings(prev => ({
                      ...prev,
                      blur_passwords: e.target.checked
                    }))}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>
            </div>

            {/* Personal Information Exclusion */}
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <Eye className="w-4 h-4 text-gray-600" />
                    <h3 className="font-medium text-gray-900">Exclude Personal Information</h3>
                  </div>
                  <p className="text-sm text-gray-600 mb-3">
                    Filter out emails, phone numbers, addresses, and names from AI analysis to maintain privacy.
                  </p>
                  <div className="text-xs text-gray-500">
                    <strong>Note:</strong> May reduce analysis accuracy for workflows involving personal data entry
                  </div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer ml-4">
                  <input
                    type="checkbox"
                    checked={settings.exclude_personal_info}
                    onChange={(e) => setSettings(prev => ({
                      ...prev,
                      exclude_personal_info: e.target.checked
                    }))}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>
            </div>

            {/* Custom Exclusions */}
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="mb-4">
                <h3 className="font-medium text-gray-900 mb-2">Custom Exclusions</h3>
                <p className="text-sm text-gray-600 mb-3">
                  Add specific words, URLs, or patterns to exclude from analysis (e.g., company names, project codes).
                </p>
              </div>

              {/* Add Custom Exclusion Input */}
              <div className="flex space-x-2 mb-4">
                <input
                  type="text"
                  placeholder="e.g., internal-system.com, ProjectX, ABC123"
                  value={customExclusionInput}
                  onChange={(e) => setCustomExclusionInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <button
                  onClick={addCustomExclusion}
                  disabled={!customExclusionInput.trim()}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Add
                </button>
              </div>

              {/* Current Exclusions */}
              {settings.custom_exclusions.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Current Exclusions:</h4>
                  <div className="flex flex-wrap gap-2">
                    {settings.custom_exclusions.map((exclusion, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                      >
                        {exclusion}
                        <button
                          onClick={() => removeCustomExclusion(exclusion)}
                          className="ml-1.5 inline-flex items-center justify-center w-3 h-3 rounded-full hover:bg-blue-200 transition-colors"
                        >
                          <X className="w-2 h-2" />
                        </button>
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {settings.custom_exclusions.length === 0 && (
                <p className="text-xs text-gray-500 italic">No custom exclusions added</p>
              )}
            </div>
          </div>

          {/* Privacy Notice */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start space-x-2">
              <Shield className="w-4 h-4 text-blue-600 flex-shrink-0 mt-0.5" />
              <div className="text-sm">
                <p className="text-blue-800 font-medium mb-1">Privacy Commitment</p>
                <p className="text-blue-700">
                  Your recordings are processed securely and never shared with third parties. 
                  Privacy settings are applied before any AI analysis begins.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-200">
          <div className="flex items-center justify-end space-x-3">
            <button
              onClick={onClose}
              disabled={saving}
              className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              onClick={handleSaveSettings}
              disabled={saving || success}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {saving && <Loader2 className="w-4 h-4 animate-spin" />}
              <span>{saving ? 'Saving...' : success ? 'Saved!' : 'Save Settings'}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}