import { useState } from "react"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts"
import { ChevronDown, ChevronRight, TreeDeciduous } from "lucide-react"

interface SpeciesNode {
  name: string
  rank: "order" | "family" | "genus" | "species"
  confidence: number
  readCount: number
  children?: SpeciesNode[]
  expanded?: boolean
}

export function CommunityView() {
  const [viewMode, setViewMode] = useState<"reads" | "groups">("reads")
  const [selectedRank, setSelectedRank] = useState<"order" | "family" | "genus" | "species">("species")

  // Mock data for bar chart
  const barChartData = [
    { name: "Sparus aurata", reads: 14230, confidence: 92 },
    { name: "Labrus bergylta", reads: 1250, confidence: 85 },
    { name: "Mullus surmuletus", reads: 980, confidence: 78 },
    { name: "Sardina pilchardus", reads: 890, confidence: 72 },
    { name: "Gadus sp.", reads: 720, confidence: 57 },
    { name: "Sparidae", reads: 3410, confidence: 61 },
    { name: "Other", reads: 1200, confidence: 45 },
  ]

  // Mock data for taxonomic tree
  const [treeData, setTreeData] = useState<SpeciesNode[]>([
    {
      name: "Perciformes",
      rank: "order",
      confidence: 0,
      readCount: 0,
      expanded: true,
      children: [
        {
          name: "Sparidae",
          rank: "family",
          confidence: 0,
          readCount: 0,
          expanded: true,
          children: [
            {
              name: "Sparus",
              rank: "genus",
              confidence: 0,
              readCount: 0,
              expanded: true,
              children: [
                { name: "Sparus aurata", rank: "species", confidence: 0.92, readCount: 14230 },
                { name: "Sparus sp.", rank: "species", confidence: 0.65, readCount: 230 },
              ]
            },
            {
              name: "Pagrus",
              rank: "genus",
              confidence: 0,
              readCount: 0,
              expanded: false,
              children: [
                { name: "Pagrus pagrus", rank: "species", confidence: 0.78, readCount: 560 },
              ]
            }
          ]
        },
        {
          name: "Labridae",
          rank: "family",
          confidence: 0,
          readCount: 0,
          expanded: false,
          children: [
            { name: "Labrus bergylta", rank: "species", confidence: 0.85, readCount: 1250 },
          ]
        }
      ]
    },
    {
      name: "Gadiformes",
      rank: "order",
      confidence: 0,
      readCount: 0,
      expanded: true,
      children: [
        {
          name: "Gadidae",
          rank: "family",
          confidence: 0,
          readCount: 0,
          expanded: true,
          children: [
            { name: "Gadus", rank: "genus", confidence: 0, readCount: 0, expanded: true, children: [
              { name: "Gadus sp.", rank: "species", confidence: 0.57, readCount: 720 },
            ]}
          ]
        }
      ]
    }
  ])

  const toggleNode = (path: number[]) => {
    const newData = [...treeData]
    let current = newData as any
    
    for (let i = 0; i < path.length; i++) {
      current = current[path[i]]
      if (i < path.length - 1 && current.children) {
        current = current.children
      }
    }
    
    if (current.children) {
      current.expanded = !current.expanded
    }
    
    setTreeData(newData)
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.7) return "#22c55e"
    if (confidence >= 0.5) return "#f59e0b"
    return "#ef4444"
  }

  const renderTreeNode = (node: SpeciesNode, path: number[] = []) => {
    const hasChildren = node.children && node.children.length > 0
    const isLeaf = node.rank === "species"
    
    return (
      <div key={node.name} className="ml-4">
        <div 
          className="flex items-center gap-2 py-1 hover:bg-gray-50 rounded cursor-pointer"
          onClick={() => hasChildren && toggleNode([...path, path.length])}
        >
          {hasChildren ? (
            node.expanded ? (
              <ChevronDown className="h-4 w-4 text-gray-400" />
            ) : (
              <ChevronRight className="h-4 w-4 text-gray-400" />
            )
          ) : (
            <div className="w-4" />
          )}
          
          <TreeDeciduous className="h-4 w-4 text-gray-400" />
          
          <span className={`text-sm ${isLeaf ? "text-gray-900" : "font-medium text-gray-700"}`}>
            {node.name}
          </span>
          
          {isLeaf && (
            <>
              <span 
                className="text-xs px-2 py-0.5 rounded-full"
                style={{ 
                  backgroundColor: getConfidenceColor(node.confidence) + "20",
                  color: getConfidenceColor(node.confidence)
                }}
              >
                {Math.round(node.confidence * 100)}%
              </span>
              <span className="text-xs text-gray-500">
                {node.readCount.toLocaleString()} reads
              </span>
            </>
          )}
        </div>
        
        {hasChildren && node.expanded && node.children && (
          <div className="ml-2 border-l border-gray-200 pl-2">
            {node.children.map((child, index) => renderTreeNode(child, [...path, index]))}
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Bar Chart */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Species Distribution</h3>
          <div className="flex gap-2">
            <button
              onClick={() => setViewMode("reads")}
              className={`px-3 py-1 text-sm rounded-md ${
                viewMode === "reads" 
                  ? "bg-primary-100 text-primary-700" 
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              By reads
            </button>
            <button
              onClick={() => setViewMode("groups")}
              className={`px-3 py-1 text-sm rounded-md ${
                viewMode === "groups" 
                  ? "bg-primary-100 text-primary-700" 
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              By groups
            </button>
          </div>
        </div>
        
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={barChartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="name" 
              angle={-45}
              textAnchor="end"
              height={100}
              interval={0}
              fontSize={12}
            />
            <YAxis />
            <Tooltip 
              formatter={(value: any, name: string) => [
                value.toLocaleString(),
                name === "reads" ? "Reads" : "Confidence %"
              ]}
            />
            <Bar 
              dataKey={viewMode === "reads" ? "reads" : "confidence"} 
              fill="#0d9488"
            >
              {barChartData.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  fill={entry.confidence >= 70 ? "#22c55e" : entry.confidence >= 50 ? "#f59e0b" : "#ef4444"}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
        
        <button className="mt-4 text-sm text-primary-600 hover:underline">
          View as table
        </button>
      </div>

      {/* Taxonomic Tree */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Taxonomic Tree</h3>
          <div className="flex gap-2">
            {(["order", "family", "genus", "species"] as const).map((rank) => (
              <button
                key={rank}
                onClick={() => setSelectedRank(rank)}
                className={`px-3 py-1 text-sm rounded-md capitalize ${
                  selectedRank === rank 
                    ? "bg-primary-100 text-primary-700" 
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
              >
                {rank}
              </button>
            ))}
          </div>
        </div>
        
        <div className="h-[300px] overflow-y-auto">
          {treeData.map((node, index) => renderTreeNode(node, [index]))}
        </div>
        
        <button className="mt-4 text-sm text-primary-600 hover:underline">
          View as table
        </button>
      </div>
    </div>
  )
}
