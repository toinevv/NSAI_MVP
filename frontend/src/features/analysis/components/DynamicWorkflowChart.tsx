/**
 * Dynamic Workflow Chart Component
 * Visualizes workflows using React Flow
 * Adapts to any workflow pattern discovered
 */

import React, { useCallback, useMemo, useEffect, useState } from 'react'
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
  Handle,
  type ReactFlowInstance
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

// Helper functions matching Step-by-Step Workflow exactly
const getStepIcon = (step: any) => {
  const application = step.application?.toLowerCase() || ''
  const action = step.action?.toLowerCase() || ''
  
  // Application-based icons
  if (application.includes('mail') || application.includes('outlook') || application.includes('gmail')) return Mail
  if (application.includes('excel') || application.includes('sheets')) return FileText
  if (application.includes('chrome') || application.includes('browser') || application.includes('web')) return Globe
  if (application.includes('database') || application.includes('wms') || application.includes('erp')) return Database
  
  // Action-based icons
  if (action.includes('click') || action.includes('select') || action.includes('navigate')) return MousePointer
  if (action.includes('open') || action.includes('switch') || action.includes('access')) return Monitor
  if (action.includes('copy') || action.includes('paste') || action.includes('enter') || action.includes('input')) return MousePointer
  
  return Monitor // default
}

const getStepType = (step: any) => {
  const action = step.action?.toLowerCase() || ''
  if (action.includes('open') || action.includes('switch') || action.includes('access')) return 'application'
  if (action.includes('copy') || action.includes('paste') || action.includes('enter') || action.includes('input')) return 'action'
  if (action.includes('data') || action.includes('information')) return 'data'
  if (action.includes('check') || action.includes('verify') || action.includes('review')) return 'decision'
  return 'action'
}

const getStepTypeColor = (stepType: string) => {
  switch (stepType) {
    case 'application': return 'bg-blue-50 border-blue-200 text-blue-800'
    case 'action': return 'bg-orange-50 border-orange-200 text-orange-800'
    case 'data': return 'bg-green-50 border-green-200 text-green-800'
    case 'decision': return 'bg-purple-50 border-purple-200 text-purple-800'
    default: return 'bg-gray-50 border-gray-200 text-gray-800'
  }
}

const extractDataInvolved = (step: any) => {
  const text = `${step.action || ''} ${step.purpose || ''}`.toLowerCase()
  const dataTypes = []
  
  if (text.includes('order') || text.includes('orders')) dataTypes.push('order data')
  if (text.includes('customer') || text.includes('client')) dataTypes.push('customer info')
  if (text.includes('email') || text.includes('message')) dataTypes.push('email content')
  if (text.includes('inventory') || text.includes('stock')) dataTypes.push('inventory data')
  if (text.includes('number') || text.includes('id') || text.includes('code')) dataTypes.push('identifiers')
  if (text.includes('address') || text.includes('location')) dataTypes.push('address data')
  if (text.includes('price') || text.includes('cost') || text.includes('amount')) dataTypes.push('pricing info')
  
  return dataTypes
}

// Enhanced workflow node - matches Step-by-Step Workflow exactly
const WorkflowNode = ({ data }: any) => {
  const stepType = getStepType(data)
  const StepIcon = getStepIcon(data)
  const dataInvolved = extractDataInvolved(data)
  
  return (
    <div className={`relative flex items-start space-x-3 p-3 rounded-lg border-2 transition-all hover:shadow-md min-w-[280px] ${getStepTypeColor(stepType)}`}>
      {/* Input handle at the top - centered */}
      <Handle 
        type="target" 
        position={Position.Top} 
        className="w-3 h-3"
        style={{ left: '50%', transform: 'translateX(-50%)' }}
      />
      
      {/* Step Number & Icon */}
      <div className="flex flex-col items-center space-y-1 flex-shrink-0">
        <div className="w-7 h-7 bg-white rounded-full flex items-center justify-center border-2 border-current shadow-sm">
          <span className="text-xs font-bold">{data.stepNumber}</span>
        </div>
        <StepIcon className="w-3.5 h-3.5 opacity-60" />
      </div>
      
      {/* Step Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between mb-1">
          <div className="flex-1">
            <p className="font-medium text-gray-900 text-sm leading-tight mb-1">{data.label}</p>
            <div className="flex items-center space-x-2 text-xs text-gray-600">
              <span className="flex items-center">
                <Monitor className="w-3 h-3 mr-1" />
                {data.application}
              </span>
              {data.time && (
                <span className="flex items-center">
                  <Clock className="w-3 h-3 mr-1" />
                  {data.time}
                </span>
              )}
            </div>
            {data.purpose && (
              <p className="text-xs text-gray-600 mt-1 leading-tight">{data.purpose}</p>
            )}
          </div>
          
          {/* Step Type Badge */}
          <span className="px-1.5 py-0.5 text-xs font-medium bg-white bg-opacity-80 rounded-full border border-current ml-2 flex-shrink-0">
            {stepType}
          </span>
        </div>
        
        {/* Data Involved */}
        {dataInvolved && dataInvolved.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-1">
            {dataInvolved.map((dataType: string, dataIndex: number) => (
              <span 
                key={dataIndex} 
                className="inline-flex items-center px-1.5 py-0.5 text-xs bg-white bg-opacity-60 text-gray-700 rounded border"
              >
                <Database className="w-2.5 h-2.5 mr-1" />
                {dataType}
              </span>
            ))}
          </div>
        )}
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


// Simplified node types - use one type for all workflow steps
const nodeTypes = {
  workflow: WorkflowNode,
  application: WorkflowNode,
  action: WorkflowNode,
  data: WorkflowNode,
  decision: WorkflowNode
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


// Enhanced vertical layout function - centered workflow
const getLayoutedElements = (nodes: Node[], edges: Edge[]) => {
  const verticalSpacing = 160   // More spacing for enhanced nodes
  const startY = 50             
  const nodeWidth = 280         // Width of our enhanced nodes
  
  // Calculate the total workflow height
  const totalHeight = (nodes.length - 1) * verticalSpacing
  
  // Center the workflow both horizontally and vertically
  const centerX = -nodeWidth / 2  // Center horizontally around x=0
  const centerY = -totalHeight / 2  // Center vertically around y=0
  
  // Vertical column layout matching Step-by-Step Workflow
  const layoutedNodes = nodes.map((node, index) => {
    return {
      ...node,
      position: {
        x: centerX,  // Centered horizontally
        y: centerY + startY + (index * verticalSpacing)  // Centered vertically
      },
      targetPosition: Position.Top,
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
  const [reactFlowInstance, setReactFlowInstance] = useState<ReactFlowInstance | null>(null)
  // Convert workflow data to React Flow format
  const initialNodes = useMemo(() => {
    if (!data?.nodes) return []
    
    return data.nodes.map((node, index) => ({
      id: node.id,
      type: 'workflow', // Use single workflow type
      position: { x: 0, y: 0 }, // Will be calculated by layout
      data: {
        // Pass all the data that Step-by-Step Workflow uses
        label: node.label,
        stepNumber: node.metadata?.step_number || index + 1,
        action: node.label, // action is the main label
        application: node.metadata?.application,
        time: node.metadata?.time,
        time_formatted: node.metadata?.time_formatted,
        time_estimate_seconds: node.metadata?.time_estimate_seconds,
        purpose: node.metadata?.purpose,
        visible_in_frames: node.metadata?.visible_in_frames,
        data_involved: node.metadata?.data_involved
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
      type: 'straight',  // Straight edges for clean vertical arrows
      animated: edge.type === 'repeat',
      markerEnd: {
        type: MarkerType.ArrowClosed,
        width: 20,    // Clean size for professional look
        height: 20,
        color: '#374151'  // Clean professional color
      },
      style: {
        strokeWidth: 2,  // Clean professional thickness
        stroke: edge.type === 'bottleneck' ? '#ef4444' : '#374151',  // Clean color
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
  
  // Force re-center after nodes are loaded (this fixes the centering issue!)
  useEffect(() => {
    if (reactFlowInstance && nodes.length > 0) {
      setTimeout(() => {
        reactFlowInstance.fitView({ 
          padding: 0.2,
          duration: 200
        })
      }, 100)
    }
  }, [nodes, reactFlowInstance])

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
        onInit={(instance) => {
          console.log('React Flow initialized')
          setReactFlowInstance(instance)
          // Initial fitView
          instance.fitView({ padding: 0.2 })
        }}
        fitView
        fitViewOptions={{
          padding: 0.2,
          includeHiddenNodes: false,
          minZoom: 0.8,
          maxZoom: 1.0
        }}
        minZoom={0.3}
        maxZoom={1.2}
        style={{ width: '100%', height: '100%' }}
      >
        <Background 
          color="#e5e7eb" 
          gap={20}        // Larger grid for cleaner appearance
        />
        <Controls />
        <MiniMap 
          nodeColor="#6b7280"
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