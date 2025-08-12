/**
 * Settings Types
 * Pure type definitions for recording and analysis settings
 * NO runtime constants - those are in constants/settings.ts
 */

// Core settings interfaces
export interface FrameExtractionSettings {
  fps: number
  max_frames: number
  scene_threshold: number
  preset?: string
}

export interface RecordingSettings {
  quality: string
  fps: number
  chunk_duration: number
  max_duration: number
}

export interface AppSettings {
  frameExtraction: FrameExtractionSettings
  recording: RecordingSettings
}

// Preset configuration interfaces
export interface FrameExtractionPreset {
  fps: number
  max_frames: number
  scene_threshold: number
  label: string
  description: string
}

export interface RecordingQualityPreset {
  quality: string
  fps: number
  chunk_duration: number
  max_duration: number
  label: string
  description: string
}

// Preset collections
export interface FrameExtractionPresets {
  quick: FrameExtractionPreset
  standard: FrameExtractionPreset
  detailed: FrameExtractionPreset
  forensic: FrameExtractionPreset
}

export interface RecordingQualityPresets {
  performance: RecordingQualityPreset
  standard: RecordingQualityPreset
  high: RecordingQualityPreset
}

// Preset key types
export type FramePresetKey = keyof FrameExtractionPresets
export type RecordingPresetKey = keyof RecordingQualityPresets

// Settings context interface
export interface SettingsContextType {
  settings: AppSettings
  updateFrameExtractionSettings: (settings: Partial<FrameExtractionSettings>) => void
  updateRecordingSettings: (settings: Partial<RecordingSettings>) => void
  resetToDefaults: () => void
  getEstimatedFrames: (videoDuration: number) => number
  getEstimatedCost: (videoDuration: number) => number
}