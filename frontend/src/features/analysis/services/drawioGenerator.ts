/**
 * Draw.io Generator Utility
 * Converts workflow analysis data to Draw.io compatible XML format
 * Enables professional workflow documentation and sharing
 */

interface WorkflowStep {
  step_number?: number
  action: string
  application: string
  purpose?: string
  time_estimate_seconds?: number
  time_formatted?: string
  visible_in_frames?: number[]
  data_involved?: string[]
}

export class DrawioGenerator {
  /**
   * Generate Draw.io compatible XML from workflow steps
   */
  generateXML(workflowSteps: WorkflowStep[], title?: string): string {
    const nodes = this.createNodes(workflowSteps)
    const edges = this.createEdges(workflowSteps)
    const titleNode = title ? this.createTitleNode(title) : ''
    
    return this.wrapInMxGraphModel(titleNode + nodes + edges)
  }

  /**
   * Create nodes with professional smart grid layout
   */
  private createNodes(steps: WorkflowStep[]): string {
    const layout = this.calculateSmartLayout(steps)
    
    return steps.map((step, index) => {
      const stepId = `step${index + 1}`
      const position = layout.positions[index]
      
      // Create clean, professional label
      const lines = this.createProfessionalLabel(step)
      const label = lines.join('&#xa;') // &#xa; is newline in XML
      
      // Choose color and style based on step type
      const style = this.getProfessionalStyle(step)
      
      return `
    <mxCell id="${stepId}" value="${this.escapeXML(label)}" 
           style="${style}" 
           vertex="1" parent="1">
      <mxGeometry x="${position.x}" y="${position.y}" width="${position.width}" height="${position.height}" as="geometry"/>
    </mxCell>`
    }).join('')
  }

  /**
   * Calculate smart grid layout for professional appearance
   */
  private calculateSmartLayout(steps: WorkflowStep[]): {
    positions: Array<{x: number, y: number, width: number, height: number}>,
    canvasWidth: number,
    canvasHeight: number
  } {
    const positions = []
    const baseWidth = 180
    const baseHeight = 100
    const horizontalSpacing = 250
    const verticalSpacing = 150
    const startX = 50
    const startY = 100
    
    // Group steps by application for better visual organization
    const appGroups = this.groupStepsByApplication(steps)
    
    let currentX = startX
    let currentY = startY
    let maxY = startY
    const maxStepsPerRow = 4 // Professional looking grid
    
    steps.forEach((step, index) => {
      // Calculate dynamic width based on content length
      const contentLength = step.action.length + step.application.length
      const width = Math.max(baseWidth, Math.min(300, baseWidth + (contentLength * 2)))
      
      // Calculate height based on content lines
      const lines = this.createProfessionalLabel(step)
      const height = Math.max(baseHeight, baseHeight + ((lines.length - 3) * 20))
      
      // Position in grid with smart wrapping
      if (index > 0 && index % maxStepsPerRow === 0) {
        currentX = startX
        currentY = maxY + verticalSpacing
      }
      
      positions.push({
        x: currentX,
        y: currentY,
        width: width,
        height: height
      })
      
      // Update position tracking
      currentX += width + horizontalSpacing
      maxY = Math.max(maxY, currentY + height)
    })
    
    return {
      positions,
      canvasWidth: Math.max(1000, currentX + 200),
      canvasHeight: maxY + 200
    }
  }

  /**
   * Group steps by application for visual organization
   */
  private groupStepsByApplication(steps: WorkflowStep[]): Map<string, WorkflowStep[]> {
    const groups = new Map<string, WorkflowStep[]>()
    
    steps.forEach(step => {
      const app = step.application || 'Unknown'
      if (!groups.has(app)) {
        groups.set(app, [])
      }
      groups.get(app)!.push(step)
    })
    
    return groups
  }

  /**
   * Create professional, clean labels for steps
   */
  private createProfessionalLabel(step: WorkflowStep): string[] {
    const lines: string[] = []
    
    // Main action (title)
    lines.push(step.action)
    
    // Application with clean formatting
    if (step.application) {
      lines.push(`📱 ${step.application}`)
    }
    
    // Timing information with better formatting
    const timeInfo = step.time_formatted || 
                    (step.time_estimate_seconds ? `⏱️ ${step.time_estimate_seconds}s` : '')
    if (timeInfo) {
      lines.push(timeInfo)
    }
    
    // Purpose/description (if short enough)
    if (step.purpose && step.purpose.length < 50) {
      lines.push(`💡 ${step.purpose}`)
    }
    
    // Frame count for transparency (optional)
    if (step.visible_in_frames && step.visible_in_frames.length > 0) {
      lines.push(`📊 ${step.visible_in_frames.length} frames`)
    }
    
    return lines
  }

  /**
   * Get professional styling for different step types
   */
  private getProfessionalStyle(step: WorkflowStep): string {
    const baseStyle = 'rounded=1;whiteSpace=wrap;html=1;fontFamily=Arial;fontSize=11;spacing=4;'
    const fillColor = this.getNodeColor(step.application)
    const strokeColor = this.getStrokeColor(fillColor)
    
    // Enhanced styling for professional appearance
    return `${baseStyle}fillColor=${fillColor};strokeColor=${strokeColor};strokeWidth=2;shadow=1;glass=0;`
  }

  /**
   * Get appropriate stroke color for fill color
   */
  private getStrokeColor(fillColor: string): string {
    const strokeMap: Record<string, string> = {
      '#fff2cc': '#d6b656', // Yellow - Email
      '#d5e8d4': '#82b366', // Green - Spreadsheets  
      '#dae8fc': '#6c8ebf', // Blue - Browsers
      '#f8cecc': '#b85450', // Red - Databases
      '#e1d5e7': '#9673a6', // Purple - Other
    }
    
    return strokeMap[fillColor] || '#666666'
  }

  /**
   * Create professional edges between workflow steps
   */
  private createEdges(steps: WorkflowStep[]): string {
    if (steps.length <= 1) return ''
    
    const edges: string[] = []
    
    // Create sequential flow connections
    steps.slice(0, -1).forEach((step, index) => {
      const edgeId = `edge${index + 1}`
      const sourceId = `step${index + 1}`
      const targetId = `step${index + 2}`
      
      // Determine edge style based on relationship
      const edgeStyle = this.getEdgeStyle(step, steps[index + 1])
      
      edges.push(`
    <mxCell id="${edgeId}" style="${edgeStyle}" 
           source="${sourceId}" target="${targetId}" edge="1" parent="1">
      <mxGeometry relative="1" as="geometry"/>
    </mxCell>`)
    })
    
    // Add parallel process indicators if detected
    const parallelEdges = this.detectParallelProcesses(steps)
    edges.push(...parallelEdges)
    
    return edges.join('')
  }

  /**
   * Get appropriate edge style based on step relationship
   */
  private getEdgeStyle(fromStep: WorkflowStep, toStep: WorkflowStep): string {
    const baseStyle = 'edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;'
    
    // Different styles for different relationships
    if (fromStep.application === toStep.application) {
      // Same application - dashed line
      return `${baseStyle}strokeColor=#82b366;strokeWidth=2;dashed=1;dashPattern=5 5;`
    } else {
      // Different applications - solid line with arrow
      return `${baseStyle}strokeColor=#666666;strokeWidth=2;endArrow=classic;endFill=1;`
    }
  }

  /**
   * Detect and create edges for parallel processes
   */
  private detectParallelProcesses(steps: WorkflowStep[]): string[] {
    const parallelEdges: string[] = []
    
    // Look for steps that might happen simultaneously
    // (This is a simplified version - can be enhanced based on timing overlap)
    for (let i = 0; i < steps.length - 1; i++) {
      const currentStep = steps[i]
      const nextStep = steps[i + 1]
      
      // If steps have overlapping frames, they might be parallel
      if (this.hasOverlappingFrames(currentStep, nextStep)) {
        const edgeId = `parallel_${i}_${i + 1}`
        parallelEdges.push(`
    <mxCell id="${edgeId}" style="edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#ff6b6b;strokeWidth=1;dashed=1;dashPattern=3 3;" 
           source="step${i + 1}" target="step${i + 2}" edge="1" parent="1">
      <mxGeometry relative="1" as="geometry"/>
    </mxCell>`)
      }
    }
    
    return parallelEdges
  }

  /**
   * Check if two steps have overlapping execution frames
   */
  private hasOverlappingFrames(step1: WorkflowStep, step2: WorkflowStep): boolean {
    const frames1 = step1.visible_in_frames || []
    const frames2 = step2.visible_in_frames || []
    
    if (frames1.length === 0 || frames2.length === 0) return false
    
    // Check for any overlapping frame numbers
    return frames1.some(frame => frames2.includes(frame))
  }

  /**
   * Create title node for the workflow
   */
  private createTitleNode(title: string): string {
    return `
    <mxCell id="title" value="${this.escapeXML(title)}" 
           style="text;html=1;align=center;verticalAlign=middle;fontFamily=Arial;fontSize=14;fontStyle=1;fillColor=#f8f9fa;strokeColor=#dee2e6;" 
           vertex="1" parent="1">
      <mxGeometry x="40" y="10" width="200" height="30" as="geometry"/>
    </mxCell>`
  }

  /**
   * Get node color based on application type
   */
  private getNodeColor(application: string): string {
    const app = application.toLowerCase()
    
    if (app.includes('mail') || app.includes('outlook') || app.includes('gmail')) {
      return '#fff2cc' // Yellow for email
    }
    if (app.includes('excel') || app.includes('sheets') || app.includes('spreadsheet')) {
      return '#d5e8d4' // Green for spreadsheets
    }
    if (app.includes('chrome') || app.includes('browser') || app.includes('web')) {
      return '#dae8fc' // Blue for browsers
    }
    if (app.includes('database') || app.includes('wms') || app.includes('erp')) {
      return '#f8cecc' // Light red for databases
    }
    
    return '#e1d5e7' // Purple for other applications
  }

  /**
   * Wrap nodes and edges in professional mxGraphModel structure
   */
  private wrapInMxGraphModel(content: string): string {
    return `<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net">
  <diagram id="workflow" name="NewSystem.AI Workflow Analysis">
    <mxGraphModel dx="1800" dy="1200" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>${content}
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>`
  }

  /**
   * Escape special XML characters
   */
  private escapeXML(text: string): string {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;')
  }

  /**
   * Encode XML for URL parameter
   */
  encodeForURL(xml: string): string {
    // Base64 encode and make URL safe
    const base64 = btoa(unescape(encodeURIComponent(xml)))
    return encodeURIComponent(base64)
  }

  /**
   * Generate Draw.io editor URL with length validation
   */
  generateEditorURL(xml: string): { url: string; isLengthSafe: boolean; length: number } {
    const encoded = this.encodeForURL(xml)
    const url = `https://app.diagrams.net/#U${encoded}`
    const isLengthSafe = url.length <= 8000 // Conservative limit for browser compatibility
    
    return {
      url,
      isLengthSafe,
      length: url.length
    }
  }

  /**
   * Generate Draw.io viewer URL (read-only) with length validation
   */
  generateViewerURL(xml: string): { url: string; isLengthSafe: boolean; length: number } {
    const encoded = this.encodeForURL(xml)
    const url = `https://viewer.diagrams.net/#U${encoded}`
    const isLengthSafe = url.length <= 8000 // Conservative limit for browser compatibility
    
    return {
      url,
      isLengthSafe,
      length: url.length
    }
  }

  /**
   * Create downloadable .drawio file blob
   */
  createDownloadBlob(xml: string): Blob {
    return new Blob([xml], { type: 'application/xml' })
  }

  /**
   * Generate professional workflow title
   */
  generateTitle(steps: WorkflowStep[], duration?: string): string {
    const stepCount = steps.length
    const totalTime = steps.reduce((sum, step) => 
      sum + (step.time_estimate_seconds || 0), 0
    )
    
    const timeDisplay = duration || (totalTime > 0 ? this.formatDuration(totalTime) : '')
    const uniqueApps = new Set(steps.map(s => s.application)).size
    
    return `NewSystem.AI Workflow Analysis\n${stepCount} Steps • ${uniqueApps} Applications${timeDisplay ? ` • ${timeDisplay}` : ''}`
  }

  /**
   * Format duration in a professional way
   */
  private formatDuration(seconds: number): string {
    if (seconds < 60) {
      return `${seconds}s`
    } else if (seconds < 3600) {
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = seconds % 60
      return remainingSeconds > 0 ? `${minutes}m ${remainingSeconds}s` : `${minutes}m`
    } else {
      const hours = Math.floor(seconds / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)
      return minutes > 0 ? `${hours}h ${minutes}m` : `${hours}h`
    }
  }

  /**
   * Get smart export options based on workflow complexity
   * Provides fallback strategies for large workflows that exceed URL limits
   */
  getSmartExportOptions(workflowSteps: WorkflowStep[]): {
    canUseDirectURL: boolean
    recommendedMethod: 'url' | 'download' | 'share'
    estimatedURLLength: number
    fallbackOptions: Array<{
      method: string
      description: string
      recommended: boolean
    }>
  } {
    // Estimate URL length without generating full XML (for performance)
    const estimatedXMLLength = workflowSteps.length * 800 // ~800 chars per step average
    const estimatedURLLength = Math.ceil(estimatedXMLLength * 1.37) + 50 // Base64 overhead + base URL
    
    const canUseDirectURL = estimatedURLLength <= 8000
    const recommendedMethod = canUseDirectURL ? 'url' : 'download'
    
    const fallbackOptions = [
      {
        method: 'editor_url',
        description: 'Open directly in Draw.io editor',
        recommended: canUseDirectURL
      },
      {
        method: 'download_drawio',
        description: 'Download .drawio file for offline editing',
        recommended: !canUseDirectURL
      },
      {
        method: 'share_url',
        description: 'Copy shareable viewer link',
        recommended: canUseDirectURL
      },
      {
        method: 'png_export',
        description: 'Export as high-resolution PNG image',
        recommended: true
      }
    ].filter(option => option.recommended)

    return {
      canUseDirectURL,
      recommendedMethod,
      estimatedURLLength,
      fallbackOptions
    }
  }

  /**
   * Smart export with automatic fallback handling
   */
  smartExport(workflowSteps: WorkflowStep[], options?: {
    title?: string
    preferredMethod?: 'url' | 'download' | 'auto'
    onUrlTooLong?: (alternatives: string[]) => void
    onSuccess?: (method: string, result: any) => void
    onError?: (error: string) => void
  }): Promise<{
    success: boolean
    method: string
    result?: any
    message: string
  }> {
    return new Promise((resolve) => {
      try {
        const title = options?.title || this.generateTitle(workflowSteps)
        const xml = this.generateXML(workflowSteps, title)
        const exportOptions = this.getSmartExportOptions(workflowSteps)
        
        // Determine method based on preferences and constraints
        let method = options?.preferredMethod || 'auto'
        if (method === 'auto') {
          method = exportOptions.recommendedMethod
        }
        
        if (method === 'url' && !exportOptions.canUseDirectURL) {
          // URL too long - provide alternatives
          const alternatives = exportOptions.fallbackOptions.map(opt => opt.description)
          options?.onUrlTooLong?.(alternatives)
          
          resolve({
            success: false,
            method: 'url',
            message: `Workflow too complex for direct URL (${exportOptions.estimatedURLLength} chars). Try downloading .drawio file instead.`
          })
          return
        }
        
        // Execute the chosen method
        if (method === 'url') {
          const urlResult = this.generateEditorURL(xml)
          if (urlResult.isLengthSafe) {
            window.open(urlResult.url, '_blank', 'noopener,noreferrer')
            options?.onSuccess?.('url', urlResult)
            resolve({
              success: true,
              method: 'url',
              result: urlResult,
              message: 'Opened in Draw.io editor'
            })
          } else {
            resolve({
              success: false,
              method: 'url',
              message: `URL too long (${urlResult.length} chars). Download .drawio file instead.`
            })
          }
        } else if (method === 'download') {
          const blob = this.createDownloadBlob(xml)
          const url = URL.createObjectURL(blob)
          const link = document.createElement('a')
          link.href = url
          link.download = `workflow-analysis-${new Date().toISOString().slice(0, 10)}.drawio`
          document.body.appendChild(link)
          link.click()
          document.body.removeChild(link)
          URL.revokeObjectURL(url)
          
          options?.onSuccess?.('download', { blob, xml })
          resolve({
            success: true,
            method: 'download',
            result: { blob, xml },
            message: 'Downloaded .drawio file successfully'
          })
        }
        
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown export error'
        options?.onError?.(errorMessage)
        resolve({
          success: false,
          method: 'error',
          message: `Export failed: ${errorMessage}`
        })
      }
    })
  }
}

// Export singleton instance
export const drawioGenerator = new DrawioGenerator()

/**
 * Quick export function with smart URL handling
 */
export const exportWorkflowToDrawio = (workflowSteps: WorkflowStep[], options?: {
  title?: string
  openInEditor?: boolean
  onUrlTooLong?: (message: string, alternatives: string[]) => void
}) => {
  const title = options?.title || drawioGenerator.generateTitle(workflowSteps)
  const xml = drawioGenerator.generateXML(workflowSteps, title)
  
  if (options?.openInEditor !== false) {
    const urlResult = drawioGenerator.generateEditorURL(xml)
    
    if (urlResult.isLengthSafe) {
      window.open(urlResult.url, '_blank', 'noopener,noreferrer')
      return { 
        success: true, 
        url: urlResult.url, 
        xml,
        urlLength: urlResult.length,
        method: 'direct_url'
      }
    } else {
      // URL too long - provide fallback info
      const exportOptions = drawioGenerator.getSmartExportOptions(workflowSteps)
      const alternatives = exportOptions.fallbackOptions.map(opt => opt.description)
      
      options?.onUrlTooLong?.(
        `Workflow is too complex for direct URL opening (${urlResult.length} characters). `, 
        alternatives
      )
      
      return { 
        success: false, 
        url: urlResult.url, 
        xml,
        urlLength: urlResult.length,
        method: 'url_too_long',
        message: `URL too long (${urlResult.length} chars). Try downloading .drawio file instead.`,
        alternatives
      }
    }
  }
  
  return { success: true, xml, method: 'xml_only' }
}

/**
 * Smart export function with automatic fallback handling
 */
export const smartExportWorkflow = async (workflowSteps: WorkflowStep[], options?: {
  title?: string
  preferredMethod?: 'url' | 'download' | 'auto'
  onUrlTooLong?: (alternatives: string[]) => void
  onSuccess?: (method: string, message: string) => void
  onError?: (error: string) => void
}) => {
  return await drawioGenerator.smartExport(workflowSteps, {
    title: options?.title,
    preferredMethod: options?.preferredMethod,
    onUrlTooLong: options?.onUrlTooLong,
    onSuccess: (method, result) => {
      const message = method === 'url' ? 'Opened in Draw.io editor' : 'Downloaded .drawio file'
      options?.onSuccess?.(method, message)
    },
    onError: options?.onError
  })
}