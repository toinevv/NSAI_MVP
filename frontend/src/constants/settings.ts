/**
 * Settings Constants
 * Runtime values, presets, and default configurations
 */

// Preset data constants
export const FRAME_EXTRACTION_PRESETS = {
  quick: { 
    fps: 0.33, 
    max_frames: 50, 
    scene_threshold: 0.3, 
    label: "Quick", 
    description: "Cost-efficient for basic workflow understanding" 
  },
  standard: { 
    fps: 1.0, 
    max_frames: 120, 
    scene_threshold: 0.2, 
    label: "Standard", 
    description: "Balanced quality and cost - 1 frame per second" 
  },
  detailed: { 
    fps: 2.0, 
    max_frames: 200, 
    scene_threshold: 0.15, 
    label: "Detailed", 
    description: "High-quality analysis for training and compliance" 
  },
  forensic: { 
    fps: 3.0, 
    max_frames: 300, 
    scene_threshold: 0.1, 
    label: "Forensic", 
    description: "Maximum detail for process optimization" 
  }
}

export const RECORDING_QUALITY_PRESETS = {
  performance: { 
    quality: "480p", 
    fps: 24, 
    chunk_duration: 10, 
    max_duration: 15, 
    label: "Performance", 
    description: "480p, 24fps - Faster processing" 
  },
  standard: { 
    quality: "720p", 
    fps: 30, 
    chunk_duration: 5, 
    max_duration: 30, 
    label: "Standard", 
    description: "720p, 30fps - Good balance" 
  },
  high: { 
    quality: "1080p", 
    fps: 60, 
    chunk_duration: 3, 
    max_duration: 60, 
    label: "High", 
    description: "1080p, 60fps - Better quality" 
  }
}

// Default settings
export const DEFAULT_SETTINGS = {
  frameExtraction: {
    fps: 1.0,
    max_frames: 120,
    scene_threshold: 0.2,
    preset: 'standard'
  },
  recording: {
    quality: "720p",
    fps: 30,
    chunk_duration: 5,
    max_duration: 30
  }
}