import React, { useState, useRef } from 'react'
import { Upload, File, X, CheckCircle, AlertCircle } from 'lucide-react'
import { recordingAPI } from '../services/recordingAPI'

interface ManualVideoUploadProps {
  onUploadComplete?: (sessionId: string) => void
  onError?: (error: string) => void
}

export const ManualVideoUpload: React.FC<ManualVideoUploadProps> = ({
  onUploadComplete,
  onError
}) => {
  const [isUploading, setIsUploading] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      if (file.type.startsWith('video/')) {
        setSelectedFile(file)
        setUploadStatus('idle')
      } else {
        onError?.('Please select a video file')
      }
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) return

    setIsUploading(true)
    setUploadStatus('uploading')
    setUploadProgress(0)

    try {
      // Create recording session
      const session = await recordingAPI.startRecording({
        title: `Manual Upload: ${selectedFile.name}`,
        description: 'Manually uploaded video for testing',
        workflow_type: 'test_upload',
        metadata: {
          original_filename: selectedFile.name,
          file_size: selectedFile.size,
          file_type: selectedFile.type,
          upload_type: 'manual_test'
        }
      })

      console.log('Recording session created for manual upload:', session.id)

      // Simulate progress for better UX
      setUploadProgress(25)

      // Upload the video as a single chunk
      const blob = new Blob([selectedFile], { type: selectedFile.type })
      
      setUploadProgress(50)
      
      // Use the recording API to upload
      await recordingAPI.uploadChunk(session.id, blob, 0)
      
      setUploadProgress(75)

      // Complete the recording session
      const videoDuration = await getVideoDuration(selectedFile)
      await recordingAPI.completeRecording(session.id, {
        duration_seconds: Math.round(videoDuration),
        total_file_size_bytes: selectedFile.size,
        chunk_count: 1,
        metadata: {
          upload_method: 'manual',
          original_filename: selectedFile.name
        }
      })

      setUploadProgress(100)
      setUploadStatus('success')
      setSelectedFile(null)
      
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }

      onUploadComplete?.(session.id)
    } catch (error) {
      console.error('Upload failed:', error)
      setUploadStatus('error')
      onError?.(error instanceof Error ? error.message : 'Upload failed')
    } finally {
      setIsUploading(false)
    }
  }

  const getVideoDuration = (file: File): Promise<number> => {
    return new Promise((resolve) => {
      const video = document.createElement('video')
      video.preload = 'metadata'
      video.onloadedmetadata = () => {
        window.URL.revokeObjectURL(video.src)
        resolve(video.duration)
      }
      video.onerror = () => {
        resolve(60) // Default to 60 seconds if we can't get duration
      }
      video.src = URL.createObjectURL(file)
    })
  }

  const formatFileSize = (bytes: number): string => {
    const mb = bytes / (1024 * 1024)
    return `${mb.toFixed(2)} MB`
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          Manual Video Upload (Testing)
        </h3>
        <span className="px-2 py-1 bg-amber-100 text-amber-700 text-xs font-medium rounded">
          Test Mode
        </span>
      </div>

      <p className="text-sm text-gray-600 mb-6">
        Upload a pre-recorded video file for testing the analysis pipeline. 
        This is useful for comparing results across multiple analysis runs.
      </p>

      <div className="space-y-4">
        {/* File Input Area */}
        <div 
          onClick={() => fileInputRef.current?.click()}
          className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-teal-400 transition-colors"
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="video/*"
            onChange={handleFileSelect}
            className="hidden"
          />
          
          {selectedFile ? (
            <div className="space-y-2">
              <File className="w-12 h-12 text-teal-600 mx-auto" />
              <p className="font-medium text-gray-900">{selectedFile.name}</p>
              <p className="text-sm text-gray-500">{formatFileSize(selectedFile.size)}</p>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  setSelectedFile(null)
                  setUploadStatus('idle')
                  if (fileInputRef.current) {
                    fileInputRef.current.value = ''
                  }
                }}
                className="text-red-600 hover:text-red-700 text-sm"
              >
                Remove file
              </button>
            </div>
          ) : (
            <div className="space-y-2">
              <Upload className="w-12 h-12 text-gray-400 mx-auto" />
              <p className="font-medium text-gray-700">Click to select a video file</p>
              <p className="text-sm text-gray-500">or drag and drop</p>
              <p className="text-xs text-gray-400">MP4, WebM, MOV up to 500MB</p>
            </div>
          )}
        </div>

        {/* Upload Progress */}
        {uploadStatus === 'uploading' && (
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Uploading...</span>
              <span className="text-gray-900 font-medium">{uploadProgress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-teal-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
          </div>
        )}

        {/* Status Messages */}
        {uploadStatus === 'success' && (
          <div className="flex items-center space-x-2 p-3 bg-green-50 text-green-700 rounded-lg">
            <CheckCircle className="w-5 h-5" />
            <span className="text-sm font-medium">Video uploaded successfully!</span>
          </div>
        )}

        {uploadStatus === 'error' && (
          <div className="flex items-center space-x-2 p-3 bg-red-50 text-red-700 rounded-lg">
            <AlertCircle className="w-5 h-5" />
            <span className="text-sm font-medium">Upload failed. Please try again.</span>
          </div>
        )}

        {/* Upload Button */}
        <button
          onClick={handleUpload}
          disabled={!selectedFile || isUploading}
          className={`w-full px-4 py-2 rounded-lg font-medium transition-colors ${
            !selectedFile || isUploading
              ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
              : 'bg-teal-600 hover:bg-teal-700 text-white'
          }`}
        >
          {isUploading ? 'Uploading...' : 'Upload Video'}
        </button>
      </div>

      {/* Test Instructions */}
      <div className="mt-6 p-4 bg-amber-50 rounded-lg">
        <h4 className="text-sm font-medium text-amber-900 mb-2">Testing Tips:</h4>
        <ul className="text-xs text-amber-700 space-y-1">
          <li>• Use the same video file to compare analysis results</li>
          <li>• Ideal test videos: 2-10 minutes of workflow recording</li>
          <li>• Include multiple applications and repetitive tasks</li>
          <li>• Save test videos locally for consistent testing</li>
        </ul>
      </div>
    </div>
  )
}