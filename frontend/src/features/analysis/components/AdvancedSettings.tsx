/**
 * Advanced Frame Extraction Settings Panel
 * Allows users to configure frame extraction parameters for optimal analysis
 */

import React, { useState, useEffect } from 'react'
import { Settings, Info, DollarSign, Clock, Film } from 'lucide-react'

interface FrameExtractionSettings {
  fps: number
  max_frames: number
  scene_threshold: number
  preset?: string
}

interface AdvancedSettingsProps {
  videoDuration?: number // in seconds
  onSettingsChange: (settings: FrameExtractionSettings) => void
  defaultSettings?: FrameExtractionSettings
}

// Predefined quality presets
const QUALITY_PRESETS = {
  quick: { fps: 0.33, max_frames: 50, scene_threshold: 0.3, label: "Quick", description: "Cost-efficient for basic workflow understanding" },
  standard: { fps: 1.0, max_frames: 120, scene_threshold: 0.2, label: "Standard", description: "Balanced quality and cost - 1 frame per second" },
  detailed: { fps: 2.0, max_frames: 200, scene_threshold: 0.15, label: "Detailed", description: "High-quality analysis for training and compliance" },
  forensic: { fps: 3.0, max_frames: 300, scene_threshold: 0.1, label: "Forensic", description: "Maximum detail for process optimization" }
} as const

type PresetKey = keyof typeof QUALITY_PRESETS

export const AdvancedSettings: React.FC<AdvancedSettingsProps> = ({
  videoDuration = 100,
  onSettingsChange,
  defaultSettings = { fps: 1.0, max_frames: 120, scene_threshold: 0.2 }
}) => {
  const [isExpanded, setIsExpanded] = useState(false)
  const [selectedPreset, setSelectedPreset] = useState<PresetKey | 'custom'>('standard')
  const [settings, setSettings] = useState<FrameExtractionSettings>(defaultSettings)

  // Calculate real-time estimates
  const estimatedFrames = Math.min(settings.max_frames, Math.floor(videoDuration * settings.fps))
  const estimatedCost = estimatedFrames * 0.01 // $0.01 per frame
  const analysisTime = Math.ceil(estimatedFrames / 10) // ~10 frames per minute processing

  // Update parent when settings change
  useEffect(() => {
    onSettingsChange(settings)
  }, [settings, onSettingsChange])

  const handlePresetChange = (preset: PresetKey | 'custom') => {
    setSelectedPreset(preset)
    if (preset !== 'custom') {
      const presetSettings = QUALITY_PRESETS[preset]
      setSettings({
        fps: presetSettings.fps,
        max_frames: presetSettings.max_frames,
        scene_threshold: presetSettings.scene_threshold,
        preset
      })
    }
  }

  const handleCustomSettingChange = (field: keyof FrameExtractionSettings, value: number) => {
    setSelectedPreset('custom')
    setSettings(prev => ({ ...prev, [field]: value, preset: undefined }))
  }

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className="bg-gray-50 rounded-lg border border-gray-200">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-gray-100 transition-colors"
      >
        <div className="flex items-center space-x-2">
          <Settings className="w-4 h-4 text-gray-600" />
          <span className="font-medium text-gray-900">Advanced Frame Extraction</span>
          <span className="text-sm text-gray-500">
            ({estimatedFrames} frames, ~${estimatedCost.toFixed(2)})
          </span>
        </div>
        <div className={`transform transition-transform ${isExpanded ? 'rotate-180' : ''}`}>
          ↓
        </div>
      </button>

      {isExpanded && (
        <div className="px-4 pb-4 space-y-6">
          {/* Quality Presets */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Quality Preset
            </label>
            <div className="grid grid-cols-2 gap-2">
              {(Object.keys(QUALITY_PRESETS) as PresetKey[]).map((preset) => (
                <button
                  key={preset}
                  onClick={() => handlePresetChange(preset)}
                  className={`p-3 rounded-lg border text-left transition-colors ${
                    selectedPreset === preset
                      ? 'border-blue-500 bg-blue-50 text-blue-900'
                      : 'border-gray-200 bg-white hover:border-gray-300'
                  }`}
                >
                  <div className="font-medium text-sm">{QUALITY_PRESETS[preset].label}</div>
                  <div className="text-xs text-gray-600 mt-1">{QUALITY_PRESETS[preset].fps} FPS</div>
                </button>
              ))}
              <button
                onClick={() => handlePresetChange('custom')}
                className={`p-3 rounded-lg border text-left transition-colors ${
                  selectedPreset === 'custom'
                    ? 'border-blue-500 bg-blue-50 text-blue-900'
                    : 'border-gray-200 bg-white hover:border-gray-300'
                }`}
              >
                <div className="font-medium text-sm">Custom</div>
                <div className="text-xs text-gray-600 mt-1">Manual settings</div>
              </button>
            </div>
          </div>

          {/* Custom Settings */}
          <div className="space-y-4">
            {/* Frames Per Second */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Frames Per Second: {settings.fps.toFixed(1)} FPS
              </label>
              <input
                type="range"
                min="0.1"
                max="3.0"
                step="0.1"
                value={settings.fps}
                onChange={(e) => handleCustomSettingChange('fps', parseFloat(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>0.1 FPS (Minimal)</span>
                <span>3.0 FPS (Maximum)</span>
              </div>
            </div>

            {/* Maximum Frames */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Maximum Frames: {settings.max_frames}
              </label>
              <input
                type="range"
                min="20"
                max="300"
                step="10"
                value={settings.max_frames}
                onChange={(e) => handleCustomSettingChange('max_frames', parseInt(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>20 frames</span>
                <span>300 frames</span>
              </div>
            </div>

            {/* Scene Change Threshold */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Scene Change Sensitivity: {Math.round((1 - settings.scene_threshold) * 100)}%
              </label>
              <input
                type="range"
                min="0.1"
                max="0.5"
                step="0.05"
                value={settings.scene_threshold}
                onChange={(e) => handleCustomSettingChange('scene_threshold', parseFloat(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>High (Skip similar frames)</span>
                <span>Low (Keep all frames)</span>
              </div>
            </div>
          </div>

          {/* Real-time Estimates */}
          <div className="bg-white rounded-lg p-4 border border-gray-200">
            <h4 className="font-medium text-gray-900 mb-3 flex items-center">
              <Info className="w-4 h-4 mr-2" />
              Analysis Estimates ({formatDuration(videoDuration)} video)
            </h4>
            
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div className="text-center">
                <Film className="w-5 h-5 text-blue-600 mx-auto mb-1" />
                <div className="font-medium">{estimatedFrames}</div>
                <div className="text-gray-600">Frames</div>
              </div>
              
              <div className="text-center">
                <DollarSign className="w-5 h-5 text-green-600 mx-auto mb-1" />
                <div className="font-medium">${estimatedCost.toFixed(2)}</div>
                <div className="text-gray-600">Cost</div>
              </div>
              
              <div className="text-center">
                <Clock className="w-5 h-5 text-orange-600 mx-auto mb-1" />
                <div className="font-medium">~{analysisTime} min</div>
                <div className="text-gray-600">Analysis Time</div>
              </div>
            </div>

            {selectedPreset !== 'custom' && (
              <div className="mt-3 p-2 bg-blue-50 rounded text-xs text-blue-800">
                <strong>{QUALITY_PRESETS[selectedPreset as PresetKey].label}:</strong> {QUALITY_PRESETS[selectedPreset as PresetKey].description}
              </div>
            )}

            {estimatedCost > 2.0 && (
              <div className="mt-3 p-2 bg-amber-50 rounded text-xs text-amber-800 border border-amber-200">
                <strong>High Cost Warning:</strong> This configuration will result in higher analysis costs. 
                Consider using a lower frame rate or preset for routine analysis.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}