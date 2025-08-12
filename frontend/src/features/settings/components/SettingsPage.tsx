/**
 * Settings Page Component
 * Centralized configuration for recording and analysis settings
 */

import React, { useState } from 'react'
import { Settings, Video, Brain, Save, RotateCcw, Info, DollarSign, Clock, Film, Sliders } from 'lucide-react'
import { useSettings } from '../../../contexts/SettingsContext'
import { FramePresetKey, RecordingPresetKey } from '../../../types/settings'
import { FRAME_EXTRACTION_PRESETS, RECORDING_QUALITY_PRESETS } from '../../../constants/settings'

export const SettingsPage: React.FC = () => {
  // Use global settings context
  const { settings, updateFrameExtractionSettings, updateRecordingSettings, resetToDefaults, getEstimatedFrames, getEstimatedCost } = useSettings()
  
  // Local state for UI presets
  const [selectedFramePreset, setSelectedFramePreset] = useState<FramePresetKey | 'custom'>(
    settings.frameExtraction.preset as FramePresetKey || 'custom'
  )
  const [selectedRecordingPreset, setSelectedRecordingPreset] = useState<RecordingPresetKey>('standard')

  const handleFramePresetChange = (preset: FramePresetKey | 'custom') => {
    setSelectedFramePreset(preset)
    if (preset !== 'custom') {
      const presetSettings = FRAME_EXTRACTION_PRESETS[preset]
      updateFrameExtractionSettings({
        fps: presetSettings.fps,
        max_frames: presetSettings.max_frames,
        scene_threshold: presetSettings.scene_threshold,
        preset
      })
    }
  }

  const handleRecordingPresetChange = (preset: RecordingPresetKey) => {
    setSelectedRecordingPreset(preset)
    const presetSettings = RECORDING_QUALITY_PRESETS[preset]
    updateRecordingSettings({
      quality: presetSettings.quality,
      fps: presetSettings.fps,
      chunk_duration: presetSettings.chunk_duration,
      max_duration: presetSettings.max_duration
    })
  }

  const handleCustomFrameSettingChange = (field: keyof typeof settings.frameExtraction, value: number) => {
    setSelectedFramePreset('custom')
    updateFrameExtractionSettings({ [field]: value, preset: undefined })
  }

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center">
        <div className="flex items-center justify-center space-x-3 mb-4">
          <div className="bg-teal-100 p-3 rounded-lg">
            <Settings className="w-8 h-8 text-teal-600" />
          </div>
        </div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Settings</h1>
        <p className="text-lg text-gray-600">
          Configure recording and analysis parameters for optimal results
        </p>
      </div>

      {/* Frame Extraction Settings */}
      <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-6">
        <div className="flex items-center space-x-3 mb-6">
          <Brain className="w-6 h-6 text-purple-600" />
          <h2 className="text-xl font-semibold text-gray-900">Frame Extraction Settings</h2>
        </div>

        {/* Quality Presets */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Analysis Quality Preset
          </label>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            {(Object.keys(FRAME_EXTRACTION_PRESETS) as FramePresetKey[]).map((preset) => {
              const presetData = FRAME_EXTRACTION_PRESETS[preset]
              return (
                <button
                  key={preset}
                  onClick={() => handleFramePresetChange(preset)}
                  className={`p-4 rounded-lg border text-left transition-colors ${
                    selectedFramePreset === preset
                      ? 'border-blue-500 bg-blue-50 text-blue-900'
                      : 'border-gray-200 bg-white hover:border-gray-300'
                  }`}
                >
                  <div className="font-medium text-sm">{presetData.label}</div>
                  <div className="text-xs text-gray-600 mt-1">{presetData.fps} FPS</div>
                  <div className="text-xs text-gray-500 mt-2">{presetData.description}</div>
                </button>
              )
            })}
            <button
              onClick={() => handleFramePresetChange('custom')}
              className={`p-4 rounded-lg border text-left transition-colors ${
                selectedFramePreset === 'custom'
                  ? 'border-blue-500 bg-blue-50 text-blue-900'
                  : 'border-gray-200 bg-white hover:border-gray-300'
              }`}
            >
              <div className="font-medium text-sm">Custom</div>
              <div className="text-xs text-gray-600 mt-1">Manual settings</div>
              <div className="text-xs text-gray-500 mt-2">Configure manually</div>
            </button>
          </div>
        </div>

        {/* Custom Frame Settings */}
        <div className="grid md:grid-cols-3 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Frames Per Second: {settings.frameExtraction.fps.toFixed(1)}
            </label>
            <input
              type="range"
              min="0.1"
              max="3.0"
              step="0.1"
              value={settings.frameExtraction.fps}
              onChange={(e) => handleCustomFrameSettingChange('fps', parseFloat(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>0.1</span>
              <span>3.0</span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Maximum Frames: {settings.frameExtraction.max_frames}
            </label>
            <input
              type="range"
              min="20"
              max="300"
              step="10"
              value={settings.frameExtraction.max_frames}
              onChange={(e) => handleCustomFrameSettingChange('max_frames', parseInt(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>20</span>
              <span>300</span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Scene Sensitivity: {Math.round((1 - settings.frameExtraction.scene_threshold) * 100)}%
            </label>
            <input
              type="range"
              min="0.1"
              max="0.5"
              step="0.05"
              value={settings.frameExtraction.scene_threshold}
              onChange={(e) => handleCustomFrameSettingChange('scene_threshold', parseFloat(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>High</span>
              <span>Low</span>
            </div>
          </div>
        </div>

        {/* Cost Estimates */}
        <div className="mt-6 bg-gray-50 rounded-lg p-4">
          <h4 className="font-medium text-gray-900 mb-3 flex items-center">
            <DollarSign className="w-4 h-4 mr-2" />
            Cost Estimates
          </h4>
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div className="text-center">
              <div className="font-medium">60s video</div>
              <div className="text-gray-600">{getEstimatedFrames(60)} frames</div>
              <div className="text-green-600 font-medium">${getEstimatedCost(60).toFixed(2)}</div>
            </div>
            <div className="text-center">
              <div className="font-medium">120s video</div>
              <div className="text-gray-600">{getEstimatedFrames(120)} frames</div>
              <div className="text-green-600 font-medium">${getEstimatedCost(120).toFixed(2)}</div>
            </div>
            <div className="text-center">
              <div className="font-medium">300s video</div>
              <div className="text-gray-600">{getEstimatedFrames(300)} frames</div>
              <div className="text-green-600 font-medium">${getEstimatedCost(300).toFixed(2)}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Recording Settings */}
      <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-6">
        <div className="flex items-center space-x-3 mb-6">
          <Video className="w-6 h-6 text-red-600" />
          <h2 className="text-xl font-semibold text-gray-900">Recording Settings</h2>
        </div>

        {/* Recording Presets */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Recording Quality Preset
          </label>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {(Object.keys(RECORDING_QUALITY_PRESETS) as RecordingPresetKey[]).map((preset) => {
              const presetData = RECORDING_QUALITY_PRESETS[preset]
              return (
                <button
                  key={preset}
                  onClick={() => handleRecordingPresetChange(preset)}
                  className={`p-4 rounded-lg border text-left transition-colors ${
                    selectedRecordingPreset === preset
                      ? 'border-green-500 bg-green-50 text-green-900'
                      : 'border-gray-200 bg-white hover:border-gray-300'
                  }`}
                >
                  <div className="font-medium text-sm">{presetData.label}</div>
                  <div className="text-xs text-gray-600 mt-1">{presetData.quality}, {presetData.fps} FPS</div>
                  <div className="text-xs text-gray-500 mt-2">{presetData.description}</div>
                </button>
              )
            })}
          </div>
        </div>

        {/* Recording Details */}
        <div className="grid md:grid-cols-4 gap-4 text-sm">
          <div className="bg-gray-50 rounded p-3 text-center">
            <div className="font-medium">Quality</div>
            <div className="text-gray-600">{settings.recording.quality}</div>
          </div>
          <div className="bg-gray-50 rounded p-3 text-center">
            <div className="font-medium">Frame Rate</div>
            <div className="text-gray-600">{settings.recording.fps} FPS</div>
          </div>
          <div className="bg-gray-50 rounded p-3 text-center">
            <div className="font-medium">Chunk Duration</div>
            <div className="text-gray-600">{settings.recording.chunk_duration}s</div>
          </div>
          <div className="bg-gray-50 rounded p-3 text-center">
            <div className="font-medium">Max Duration</div>
            <div className="text-gray-600">{formatDuration(settings.recording.max_duration * 60)}</div>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-between">
        <button
          onClick={resetToDefaults}
          className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
        >
          <RotateCcw className="w-4 h-4" />
          <span>Reset to Defaults</span>
        </button>

        <div className="flex space-x-3">
          <button
            className="flex items-center space-x-2 px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
          >
            <Save className="w-4 h-4" />
            <span>Save Settings</span>
          </button>
        </div>
      </div>

      {/* Info Box */}
      <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
        <div className="flex items-start space-x-3">
          <Info className="w-5 h-5 text-blue-600 mt-0.5" />
          <div className="text-sm text-blue-800">
            <p className="font-medium mb-1">Settings Information</p>
            <p>These settings will be applied to new recordings and analyses. Higher frame rates provide more detailed analysis but increase processing costs. Recording quality affects storage size and upload time.</p>
          </div>
        </div>
      </div>
    </div>
  )
}