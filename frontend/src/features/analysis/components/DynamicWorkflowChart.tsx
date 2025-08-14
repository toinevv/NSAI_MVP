/**
 * Dynamic Workflow Chart Component
 * Visualizes workflows using React Flow
 * Adapts to any workflow pattern discovered
 */

import React, { useCallback, useMemo } from 'react'
import ReactFlow, {
  type Node,
  type Edge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  type Connection,
  ConnectionMode,
  MarkerType,
  Position,
  Handle
} from 'reactflow'
import 'reactflow/dist/style.css'
import { 
  Monitor, 
  MousePointer, 
  Database,
  FileText,
  Mail,
  Globe,
  Layers,
  Clock
} from 'lucide-react'

// Custom node types for different workflow elements
const ApplicationNode = ({ data }: any) => {
  const Icon = data.icon || Monitor
  const colors = getApplicationColors(data.application)
  
  return (
    <div className={`px-4 py-3 shadow-lg rounded-lg ${colors.bg} border-2 ${colors.border} min-w-[220px] relative`}>
      {/* Input handle at the top - centered */}
      <Handle 
        type="target" 
        position={Position.Top} 
        className="w-3 h-3"
        style={{ left: '50%', transform: 'translateX(-50%)' }}
      />
      
      <div className="space-y-2">
        {/* Header with icon and action */}
        <div className="flex items-center space-x-2">
          <Icon className={`w-5 h-5 ${colors.text} flex-shrink-0`} />
          <div className="text-sm font-bold text-gray-900 leading-tight">{data.label}</div>
        </div>
        
        {/* Purpose if available */}
        {data.purpose && (
          <div className={`text-xs text-gray-600 italic border-l-2 ${colors.accent} pl-2`}>
            {data.purpose}
          </div>
        )}
        
        {/* Timing and application info */}
        <div className="flex items-center justify-between text-xs text-gray-500">
          {data.time && (
            <div className="flex items-center">
              <Clock className="w-3 h-3 mr-1" />
              {data.time}
            </div>
          )}
          {data.application && (
            <div className={`text-right ${colors.text} font-medium truncate max-w-[100px]`}>
              {data.application}
            </div>
          )}
        </div>
      </div>
      
      {/* Output handle at the bottom - centered */}
      <Handle 
        type="source" 
        position={Position.Bottom} 
        className="w-3 h-3"
        style={{ left: '50%', transform: 'translateX(-50%)' }}
      />
    </div>
  )
}

const ActionNode = ({ data }: any) => {
  const colors = getApplicationColors(data.application)
  
  return (
    <div className={`px-4 py-3 shadow-md rounded-md ${colors.bg} border ${colors.border} min-w-[220px] relative`}>
      {/* Input handle at the top - centered */}
      <Handle 
        type="target" 
        position={Position.Top} 
        className="w-3 h-3"
        style={{ left: '50%', transform: 'translateX(-50%)' }}
      />
      
      <div className="space-y-2">
        {/* Header with icon and action */}
        <div className="flex items-center space-x-2">
          <MousePointer className={`w-4 h-4 ${colors.text} flex-shrink-0`} />
          <div className="text-sm font-bold text-gray-800 leading-tight">{data.label}</div>
        </div>
        
        {/* Purpose if available */}
        {data.purpose && (
          <div className={`text-xs text-gray-600 italic border-l-2 ${colors.accent} pl-2`}>
            {data.purpose}
          </div>
        )}
        
        {/* Timing and application info */}
        <div className="flex items-center justify-between text-xs text-gray-500">
          {data.time && (
            <div className="flex items-center">
              <Clock className="w-3 h-3 mr-1" />
              {data.time}
            </div>
          )}
          {data.application && (
            <div className={`text-right ${colors.text} font-medium truncate max-w-[100px]`}>
              {data.application}
            </div>
          )}
        </div>
      </div>
      
      {/* Output handle at the bottom - centered */}
      <Handle 
        type="source" 
        position={Position.Bottom} 
        className="w-3 h-3"
        style={{ left: '50%', transform: 'translateX(-50%)' }}
      />
    </div>
  )
}

const DataNode = ({ data }: any) => {
  const colors = getApplicationColors(data.application)
  
  return (
    <div className={`px-4 py-3 shadow-md rounded ${colors.bg} border ${colors.border} min-w-[220px] relative`}>
      {/* Input handle at the top - centered */}
      <Handle 
        type="target" 
        position={Position.Top} 
        className="w-3 h-3"
        style={{ left: '50%', transform: 'translateX(-50%)' }}
      />
      
      <div className="space-y-2">
        {/* Header with icon and action */}
        <div className="flex items-center space-x-2">
          <Database className={`w-4 h-4 ${colors.text} flex-shrink-0`} />
          <div className="text-sm font-bold text-gray-800 leading-tight">{data.label}</div>
        </div>
        
        {/* Purpose if available */}
        {data.purpose && (
          <div className={`text-xs text-gray-600 italic border-l-2 ${colors.accent} pl-2`}>
            {data.purpose}
          </div>
        )}
        
        {/* Timing and application info */}
        <div className="flex items-center justify-between text-xs text-gray-500">
          {data.time && (
            <div className="flex items-center">
              <Clock className="w-3 h-3 mr-1" />
              {data.time}
            </div>
          )}
          {data.application && (
            <div className={`text-right ${colors.text} font-medium truncate max-w-[100px]`}>
              {data.application}
            </div>
          )}
        </div>
      </div>
      
      {/* Output handle at the bottom - centered */}
      <Handle 
        type="source" 
        position={Position.Bottom} 
        className="w-3 h-3"
        style={{ left: '50%', transform: 'translateX(-50%)' }}
      />
    </div>
  )
}

const DecisionNode = ({ data }: any) => {
  const colors = getApplicationColors(data.application)
  
  return (
    <div className={`w-[180px] h-[180px] shadow-md transform rotate-45 ${colors.bg} border-2 ${colors.border} flex items-center justify-center relative`}>
      {/* Input handle at the top - centered for diamond */}
      <Handle 
        type="target" 
        position={Position.Top} 
        className="w-3 h-3" 
        style={{ 
          top: '-6px', 
          left: '50%', 
          transform: 'translateX(-50%) rotate(-45deg)' 
        }} 
      />
      
      <div className="transform -rotate-45 text-center px-4 max-w-[160px]">
        {/* Main action/question */}
        <div className="text-sm font-bold text-gray-800 leading-tight mb-1">{data.label}</div>
        
        {/* Purpose if available - simplified for diamond shape */}
        {data.purpose && (
          <div className="text-xs text-gray-600 italic mb-1 line-clamp-2">
            {data.purpose}
          </div>
        )}
        
        {/* Timing info */}
        {data.time && (
          <div className="text-xs text-gray-500 flex items-center justify-center">
            <Clock className="w-3 h-3 mr-1" />
            {data.time}
          </div>
        )}
      </div>
      
      {/* Output handle at the bottom - centered for diamond */}
      <Handle 
        type="source" 
        position={Position.Bottom} 
        className="w-3 h-3" 
        style={{ 
          bottom: '-6px', 
          left: '50%', 
          transform: 'translateX(-50%) rotate(-45deg)' 
        }} 
      />
    </div>
  )
}

// Memoized node types to prevent ReactFlow warnings about object recreation
const nodeTypes = {
  application: ApplicationNode,
  action: ActionNode,
  data: DataNode,
  decision: DecisionNode
}

interface WorkflowNode {
  id: string
  label: string
  type: 'application' | 'action' | 'data' | 'decision'
  metadata?: {
    time?: string
    icon?: any
    application?: string
  }
}

interface WorkflowEdge {
  source: string
  target: string
  label?: string
  type?: string
}

interface FlowChartData {
  nodes: WorkflowNode[]
  edges: WorkflowEdge[]
}

interface DynamicWorkflowChartProps {
  data: FlowChartData
  className?: string
  onNodeClick?: (node: any) => void
}

export interface DynamicWorkflowChartRef {
  exportToPNG: () => Promise<void>
}

// Helper function to get icon for application
const getAppIcon = (appName: string) => {
  const name = appName.toLowerCase()
  if (name.includes('mail') || name.includes('outlook') || name.includes('gmail')) return Mail
  if (name.includes('excel') || name.includes('sheets')) return FileText
  if (name.includes('chrome') || name.includes('browser') || name.includes('web')) return Globe
  if (name.includes('database') || name.includes('wms') || name.includes('erp')) return Database
  return Monitor
}

// Helper function to get application-based colors for professional flow distinction
const getApplicationColors = (appName: string) => {
  if (!appName) return { bg: 'bg-gray-50', border: 'border-gray-300', text: 'text-gray-600', accent: 'border-gray-200' }
  
  const app = appName.toLowerCase()
  
  if (app.includes('mail') || app.includes('outlook') || app.includes('gmail')) {
    return { 
      bg: 'bg-yellow-50', 
      border: 'border-yellow-400', 
      text: 'text-yellow-700', 
      accent: 'border-yellow-200' 
    }
  }
  if (app.includes('excel') || app.includes('sheets') || app.includes('spreadsheet')) {
    return { 
      bg: 'bg-green-50', 
      border: 'border-green-400', 
      text: 'text-green-700', 
      accent: 'border-green-200' 
    }
  }
  if (app.includes('chrome') || app.includes('browser') || app.includes('web') || app.includes('wms')) {
    return { 
      bg: 'bg-blue-50', 
      border: 'border-blue-400', 
      text: 'text-blue-700', 
      accent: 'border-blue-200' 
    }
  }
  if (app.includes('database') || app.includes('erp')) {
    return { 
      bg: 'bg-red-50', 
      border: 'border-red-400', 
      text: 'text-red-700', 
      accent: 'border-red-200' 
    }
  }
  
  return { 
    bg: 'bg-purple-50', 
    border: 'border-purple-400', 
    text: 'text-purple-700', 
    accent: 'border-purple-200' 
  }
}

// Professional flowchart layout function
const getLayoutedElements = (nodes: Node[], edges: Edge[]) => {
  // Enhanced spacing for professional flowchart appearance
  const verticalSpacing = 180   // Consistent vertical spacing between steps
  const startY = 80             // Top margin
  const centerX = 400           // Center all nodes horizontally for straight vertical flow
  
  // For small workflows (≤8 steps): single vertical column
  // For larger workflows: still single column but with tighter spacing if needed
  const layoutedNodes = nodes.map((node, index) => {
    return {
      ...node,
      position: {
        x: centerX - 110,  // Center the 220px wide nodes
        y: startY + (index * verticalSpacing)
      },
      targetPosition: Position.Top,    // Top-to-bottom flow
      sourcePosition: Position.Bottom
    }
  })

  return { nodes: layoutedNodes, edges }
}

export const DynamicWorkflowChart: React.FC<DynamicWorkflowChartProps> = ({
  data,
  className = '',
  onNodeClick
}) => {
  // Convert workflow data to React Flow format
  const initialNodes = useMemo(() => {
    if (!data?.nodes) return []
    
    return data.nodes.map((node, index) => ({
      id: node.id,
      type: node.type || 'application',
      position: { x: 0, y: 0 }, // Will be calculated by layout
      data: {
        label: node.label,
        time: node.metadata?.time,
        icon: node.metadata?.application ? getAppIcon(node.metadata.application) : undefined,
        ...node.metadata
      }
    }))
  }, [data])

  const initialEdges = useMemo(() => {
    if (!data?.edges) return []
    
    return data.edges.map((edge, index) => ({
      id: `edge-${index}`,
      source: edge.source,
      target: edge.target,
      label: edge.label,
      type: 'straight',  // Straight edges for clean vertical flowchart arrows
      animated: edge.type === 'repeat',
      markerEnd: {
        type: MarkerType.ArrowClosed,
        width: 20,    // Slightly smaller for cleaner look
        height: 20,
        color: '#374151'
      },
      style: {
        strokeWidth: 2,  // Clean professional thickness
        stroke: edge.type === 'bottleneck' ? '#ef4444' : '#374151',
        strokeDasharray: edge.type === 'parallel' ? '5 5' : undefined
      }
    }))
  }, [data])

  // Apply auto-layout
  const { nodes: layoutedNodes, edges: layoutedEdges } = useMemo(
    () => getLayoutedElements(initialNodes, initialEdges),
    [initialNodes, initialEdges]
  )

  const [nodes, setNodes, onNodesChange] = useNodesState(layoutedNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(layoutedEdges)

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  )

  const handleNodeClick = useCallback((event: React.MouseEvent, node: any) => {
    if (onNodeClick) {
      onNodeClick(node)
    }
  }, [onNodeClick])

  if (!data?.nodes || data.nodes.length === 0) {
    return (
      <div className={`flex items-center justify-center h-96 bg-gray-50 rounded-lg ${className}`}>
        <div className="text-center">
          <Layers className="w-12 h-12 text-gray-400 mx-auto mb-3" />
          <p className="text-gray-600">No workflow data to visualize</p>
        </div>
      </div>
    )
  }

  return (
    <div className={`h-[500px] bg-white rounded-lg overflow-hidden border border-gray-200 shadow-sm ${className}`} style={{ width: '100%', height: '500px' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={handleNodeClick}
        nodeTypes={nodeTypes}
        connectionMode={ConnectionMode.Loose}
        fitView
        fitViewOptions={{
          padding: 0.15,  // Tighter padding for more professional look
          maxZoom: 1.2,   // Slightly less zoom for better readability
          minZoom: 0.3    // Allow zooming out more for large workflows
        }}
        style={{ width: '100%', height: '100%' }}
      >
        <Background 
          color="#e5e7eb" 
          gap={20}        // Larger grid for cleaner appearance
        />
        <Controls />
        <MiniMap 
          nodeColor={(node) => {
            // Use application-based colors in minimap too
            const appColors = {
              'mail': '#fbbf24',      // Yellow
              'excel': '#10b981',     // Green  
              'chrome': '#3b82f6',    // Blue
              'database': '#ef4444',  // Red
              'default': '#8b5cf6'    // Purple
            }
            
            const nodeData = node.data || {}
            const app = (nodeData.application || '').toLowerCase()
            
            if (app.includes('mail') || app.includes('outlook')) return appColors.mail
            if (app.includes('excel') || app.includes('sheets')) return appColors.excel
            if (app.includes('chrome') || app.includes('browser') || app.includes('wms')) return appColors.chrome
            if (app.includes('database') || app.includes('erp')) return appColors.database
            return appColors.default
          }}
          style={{
            backgroundColor: '#ffffff',
            border: '1px solid #d1d5db',
            borderRadius: '6px'
          }}
        />
      </ReactFlow>
    </div>
  )
}