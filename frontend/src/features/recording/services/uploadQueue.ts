/**
 * Enhanced Upload Queue System
 * Handles chunked video uploads with retry logic, progress tracking, and error recovery
 */

export interface ChunkUploadTask {
  id: string
  sessionId: string
  chunkIndex: number
  chunk: Blob
  status: 'pending' | 'uploading' | 'completed' | 'failed'
  retryCount: number
  error?: string
  startTime?: number
  completedTime?: number
  uploadProgress: number
}

export interface UploadQueueConfig {
  maxRetries: number
  concurrency: number
  retryDelayMs: number
  maxRetryDelayMs: number
  timeoutMs: number
}

export interface UploadProgress {
  totalChunks: number
  completedChunks: number
  failedChunks: number
  uploadedBytes: number
  totalBytes: number
  percentage: number
  estimatedTimeRemaining: number
  averageUploadSpeed: number
}

export type UploadEventType = 'progress' | 'chunk_completed' | 'chunk_failed' | 'queue_completed' | 'queue_failed'

export interface UploadEvent {
  type: UploadEventType
  data: {
    task?: ChunkUploadTask
    progress?: UploadProgress
    error?: string
  }
}

export type UploadEventCallback = (event: UploadEvent) => void

const DEFAULT_CONFIG: UploadQueueConfig = {
  maxRetries: 3,
  concurrency: 3,
  retryDelayMs: 1000,
  maxRetryDelayMs: 8000,
  timeoutMs: 30000, // 30 seconds per chunk
}

export class UploadQueue {
  private config: UploadQueueConfig
  private tasks: Map<string, ChunkUploadTask> = new Map()
  private activeUploads: Set<string> = new Set()
  private eventCallbacks: UploadEventCallback[] = []
  private isProcessing = false
  private startTime?: number
  private uploadFunction?: (sessionId: string, chunk: Blob, chunkIndex: number) => Promise<any>

  constructor(config: Partial<UploadQueueConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config }
  }

  /**
   * Set the upload function that will be used to upload chunks
   */
  setUploadFunction(uploadFn: (sessionId: string, chunk: Blob, chunkIndex: number) => Promise<any>): void {
    this.uploadFunction = uploadFn
  }

  /**
   * Add event listener for upload events
   */
  addEventListener(callback: UploadEventCallback): void {
    this.eventCallbacks.push(callback)
  }

  /**
   * Remove event listener
   */
  removeEventListener(callback: UploadEventCallback): void {
    const index = this.eventCallbacks.indexOf(callback)
    if (index > -1) {
      this.eventCallbacks.splice(index, 1)
    }
  }

  /**
   * Emit upload event to all listeners
   */
  private emit(event: UploadEvent): void {
    this.eventCallbacks.forEach(callback => callback(event))
  }

  /**
   * Add chunk to upload queue
   */
  addChunk(sessionId: string, chunkIndex: number, chunk: Blob): string {
    const taskId = `${sessionId}_${chunkIndex}`
    const task: ChunkUploadTask = {
      id: taskId,
      sessionId,
      chunkIndex,
      chunk,
      status: 'pending',
      retryCount: 0,
      uploadProgress: 0,
    }

    this.tasks.set(taskId, task)
    
    // Start processing if not already running
    if (!this.isProcessing) {
      this.processQueue()
    }

    return taskId
  }

  /**
   * Get current upload progress
   */
  getProgress(): UploadProgress {
    const tasks = Array.from(this.tasks.values())
    const totalChunks = tasks.length
    const completedChunks = tasks.filter(t => t.status === 'completed').length
    const failedChunks = tasks.filter(t => t.status === 'failed').length
    const uploadedBytes = tasks
      .filter(t => t.status === 'completed')
      .reduce((sum, t) => sum + t.chunk.size, 0)
    const totalBytes = tasks.reduce((sum, t) => sum + t.chunk.size, 0)
    
    const percentage = totalChunks > 0 ? (completedChunks / totalChunks) * 100 : 0
    
    // Calculate estimated time remaining
    const elapsedTime = this.startTime ? Date.now() - this.startTime : 0
    const averageTimePerChunk = completedChunks > 0 ? elapsedTime / completedChunks : 0
    const remainingChunks = totalChunks - completedChunks
    const estimatedTimeRemaining = remainingChunks * averageTimePerChunk

    // Calculate average upload speed (bytes per second)
    const averageUploadSpeed = elapsedTime > 0 ? uploadedBytes / (elapsedTime / 1000) : 0

    return {
      totalChunks,
      completedChunks,
      failedChunks,
      uploadedBytes,
      totalBytes,
      percentage,
      estimatedTimeRemaining,
      averageUploadSpeed,
    }
  }

  /**
   * Process upload queue with concurrency control
   */
  private async processQueue(): Promise<void> {
    if (this.isProcessing) return
    
    this.isProcessing = true
    this.startTime = Date.now()

    try {
      while (this.hasTasksToProcess()) {
        const availableSlots = this.config.concurrency - this.activeUploads.size
        const pendingTasks = this.getPendingTasks().slice(0, availableSlots)

        // Start uploads for available slots
        const uploadPromises = pendingTasks.map(task => this.uploadChunk(task))
        
        if (uploadPromises.length > 0) {
          await Promise.allSettled(uploadPromises)
        } else {
          // Wait a bit before checking again
          await this.sleep(100)
        }

        // Emit progress update
        this.emit({
          type: 'progress',
          data: { progress: this.getProgress() }
        })
      }

      // Check final status
      const progress = this.getProgress()
      if (progress.failedChunks > 0) {
        this.emit({
          type: 'queue_failed',
          data: { 
            progress,
            error: `${progress.failedChunks} chunks failed to upload after retries`
          }
        })
      } else {
        this.emit({
          type: 'queue_completed',
          data: { progress }
        })
      }

    } finally {
      this.isProcessing = false
    }
  }

  /**
   * Check if there are tasks that need processing
   */
  private hasTasksToProcess(): boolean {
    return Array.from(this.tasks.values()).some(task => 
      task.status === 'pending' || 
      (task.status === 'failed' && task.retryCount < this.config.maxRetries)
    )
  }

  /**
   * Get pending tasks (including failed tasks that can be retried)
   */
  private getPendingTasks(): ChunkUploadTask[] {
    return Array.from(this.tasks.values()).filter(task => 
      task.status === 'pending' || 
      (task.status === 'failed' && task.retryCount < this.config.maxRetries)
    )
  }

  /**
   * Upload a single chunk with retry logic
   */
  private async uploadChunk(task: ChunkUploadTask): Promise<void> {
    this.activeUploads.add(task.id)
    task.status = 'uploading'
    task.startTime = Date.now()

    try {
      await this.attemptUpload(task)
      
      task.status = 'completed'
      task.completedTime = Date.now()
      task.uploadProgress = 100

      this.emit({
        type: 'chunk_completed',
        data: { task }
      })

    } catch (error) {
      task.retryCount++
      
      if (task.retryCount >= this.config.maxRetries) {
        task.status = 'failed'
        task.error = error instanceof Error ? error.message : 'Upload failed'
        
        this.emit({
          type: 'chunk_failed',
          data: { 
            task,
            error: task.error
          }
        })
      } else {
        // Schedule retry with exponential backoff
        task.status = 'pending'
        const delay = Math.min(
          this.config.retryDelayMs * Math.pow(2, task.retryCount - 1),
          this.config.maxRetryDelayMs
        )
        
        setTimeout(() => {
          if (task.status === 'pending') {
            this.processQueue()
          }
        }, delay)
      }
    } finally {
      this.activeUploads.delete(task.id)
    }
  }

  /**
   * Attempt to upload chunk using the configured upload function
   */
  private async attemptUpload(task: ChunkUploadTask): Promise<void> {
    if (!this.uploadFunction) {
      throw new Error('Upload function not configured')
    }

    // Create a timeout promise
    const timeoutPromise = new Promise<never>((_, reject) => {
      setTimeout(() => {
        reject(new Error(`Upload timeout after ${this.config.timeoutMs}ms`))
      }, this.config.timeoutMs)
    })

    // Race between upload and timeout
    try {
      await Promise.race([
        this.uploadFunction(task.sessionId, task.chunk, task.chunkIndex),
        timeoutPromise
      ])
    } catch (error) {
      // Re-throw with context
      throw new Error(`Chunk ${task.chunkIndex} upload failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }

  /**
   * Sleep utility for async delays
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }

  /**
   * Clear completed tasks from queue
   */
  clearCompleted(): void {
    const completedTasks = Array.from(this.tasks.entries())
      .filter(([_, task]) => task.status === 'completed')
    
    completedTasks.forEach(([taskId]) => {
      this.tasks.delete(taskId)
    })
  }

  /**
   * Get all tasks in queue
   */
  getAllTasks(): ChunkUploadTask[] {
    return Array.from(this.tasks.values())
  }

  /**
   * Cancel all pending uploads
   */
  cancelAll(): void {
    this.tasks.clear()
    this.activeUploads.clear()
    this.isProcessing = false
  }

  /**
   * Retry all failed tasks
   */
  retryFailed(): void {
    const failedTasks = Array.from(this.tasks.values())
      .filter(task => task.status === 'failed')
    
    failedTasks.forEach(task => {
      task.status = 'pending'
      task.retryCount = 0
      task.error = undefined
    })

    if (failedTasks.length > 0 && !this.isProcessing) {
      this.processQueue()
    }
  }
}