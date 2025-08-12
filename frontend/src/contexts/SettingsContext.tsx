/**
 * Global Settings Context
 * Manages frame extraction and recording settings across the app
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import {
  AppSettings,
  FrameExtractionSettings,
  RecordingSettings,
  SettingsContextType
} from '../types/settings'
import {
  DEFAULT_SETTINGS,
  FRAME_EXTRACTION_PRESETS,
  RECORDING_QUALITY_PRESETS
} from '../constants/settings'

const SettingsContext = createContext<SettingsContextType | undefined>(undefined)

const STORAGE_KEY = 'newsystem-ai-settings'

export const SettingsProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [settings, setSettings] = useState<AppSettings>(DEFAULT_SETTINGS)

  // Load settings from localStorage on mount
  useEffect(() => {
    try {
      const savedSettings = localStorage.getItem(STORAGE_KEY)
      if (savedSettings) {
        const parsed = JSON.parse(savedSettings)
        setSettings({
          ...DEFAULT_SETTINGS,
          ...parsed,
          frameExtraction: { ...DEFAULT_SETTINGS.frameExtraction, ...parsed.frameExtraction },
          recording: { ...DEFAULT_SETTINGS.recording, ...parsed.recording }
        })
        console.log('Loaded settings from storage:', parsed)
      }
    } catch (error) {
      console.error('Failed to load settings from storage:', error)
    }
  }, [])

  // Save settings to localStorage whenever they change
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(settings))
      console.log('Saved settings to storage:', settings)
    } catch (error) {
      console.error('Failed to save settings to storage:', error)
    }
  }, [settings])

  const updateFrameExtractionSettings = (newSettings: Partial<FrameExtractionSettings>) => {
    setSettings(prev => ({
      ...prev,
      frameExtraction: { ...prev.frameExtraction, ...newSettings }
    }))
  }

  const updateRecordingSettings = (newSettings: Partial<RecordingSettings>) => {
    setSettings(prev => ({
      ...prev,
      recording: { ...prev.recording, ...newSettings }
    }))
  }

  const resetToDefaults = () => {
    setSettings(DEFAULT_SETTINGS)
    console.log('Reset settings to defaults')
  }

  const getEstimatedFrames = (videoDuration: number): number => {
    return Math.min(settings.frameExtraction.max_frames, Math.floor(videoDuration * settings.frameExtraction.fps))
  }

  const getEstimatedCost = (videoDuration: number): number => {
    return getEstimatedFrames(videoDuration) * 0.01 // $0.01 per frame
  }

  const contextValue: SettingsContextType = {
    settings,
    updateFrameExtractionSettings,
    updateRecordingSettings,
    resetToDefaults,
    getEstimatedFrames,
    getEstimatedCost
  }

  return (
    <SettingsContext.Provider value={contextValue}>
      {children}
    </SettingsContext.Provider>
  )
}

export const useSettings = (): SettingsContextType => {
  const context = useContext(SettingsContext)
  if (context === undefined) {
    throw new Error('useSettings must be used within a SettingsProvider')
  }
  return context
}

// Re-export preset constants for convenience
export { FRAME_EXTRACTION_PRESETS, RECORDING_QUALITY_PRESETS }