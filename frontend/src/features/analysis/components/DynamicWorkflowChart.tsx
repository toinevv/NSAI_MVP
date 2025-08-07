/**
 * Dynamic Workflow Chart Component
 * Visualizes workflows using React Flow
 * Adapts to any workflow pattern discovered
 */

import React, { useCallback, useMemo } from 'react'
import ReactFlow, {
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  ConnectionMode,
  MarkerType,
  Position
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
  
  return (
    <div className="px-4 py-3 shadow-lg rounded-lg bg-white border-2 border-blue-400">
      <div className="flex items-center space-x-2">
        <Icon className="w-5 h-5 text-blue-600" />
        <div>
          <div className="text-sm font-bold text-gray-900">{data.label}</div>
          {data.time && (
            <div className="text-xs text-gray-500 flex items-center mt-1">
              <Clock className="w-3 h-3 mr-1" />
              {data.time}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

const ActionNode = ({ data }: any) => {
  return (
    <div className="px-3 py-2 shadow-md rounded-md bg-orange-50 border border-orange-300">
      <div className="flex items-center space-x-2">
        <MousePointer className="w-4 h-4 text-orange-600" />
        <div className="text-sm text-gray-800">{data.label}</div>
      </div>
    </div>
  )
}

const DataNode = ({ data }: any) => {
  return (
    <div className="px-3 py-2 shadow-md rounded bg-green-50 border border-green-300">
      <div className="flex items-center space-x-2">
        <Database className="w-4 h-4 text-green-600" />
        <div className="text-sm text-gray-800">{data.label}</div>
      </div>
    </div>
  )
}

const DecisionNode = ({ data }: any) => {
  return (
    <div className="px-3 py-2 shadow-md transform rotate-45 bg-purple-50 border-2 border-purple-400">
      <div className="transform -rotate-45">
        <div className="text-sm font-medium text-gray-800">{data.label}</div>
      </div>
    </div>
  )
}

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

// Helper function to get icon for application
const getAppIcon = (appName: string) => {
  const name = appName.toLowerCase()
  if (name.includes('mail') || name.includes('outlook') || name.includes('gmail')) return Mail
  if (name.includes('excel') || name.includes('sheets')) return FileText
  if (name.includes('chrome') || name.includes('browser') || name.includes('web')) return Globe
  if (name.includes('database') || name.includes('wms') || name.includes('erp')) return Database
  return Monitor
}

// Auto-layout function using Dagre
const getLayoutedElements = (nodes: Node[], edges: Edge[]) => {
  const nodeWidth = 150
  const nodeHeight = 60
  const horizontalSpacing = 200
  const verticalSpacing = 100

  // Simple left-to-right layout
  const layoutedNodes = nodes.map((node, index) => {
    const column = index % 4
    const row = Math.floor(index / 4)
    
    return {
      ...node,
      position: {
        x: column * horizontalSpacing,
        y: row * verticalSpacing
      },
      targetPosition: Position.Left,
      sourcePosition: Position.Right
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
      type: 'smoothstep',
      animated: edge.type === 'repeat',
      markerEnd: {
        type: MarkerType.ArrowClosed,
        width: 20,
        height: 20
      },
      style: {
        strokeWidth: 2,
        stroke: edge.type === 'bottleneck' ? '#ef4444' : '#94a3b8'
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
    <div className={`h-96 bg-gray-50 rounded-lg overflow-hidden ${className}`}>
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
          padding: 0.2,
          maxZoom: 1.5,
          minZoom: 0.5
        }}
      >
        <Background color="#94a3b8" gap={16} />
        <Controls />
        <MiniMap 
          nodeColor={(node) => {
            switch (node.type) {
              case 'application': return '#3b82f6'
              case 'action': return '#f97316'
              case 'data': return '#10b981'
              case 'decision': return '#a855f7'
              default: return '#6b7280'
            }
          }}
          style={{
            backgroundColor: '#f3f4f6',
            border: '1px solid #d1d5db'
          }}
        />
      </ReactFlow>
    </div>
  )
}