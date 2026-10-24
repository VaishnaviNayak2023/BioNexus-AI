import { Copy, Check } from "lucide-react"
import { useState } from "react"

interface ProvenanceData {
  modelName: string
  modelVersion: string
  referenceDbName: string
  referenceDbVersion: string
  referenceDbDate: string
  phylogenyVersion: string
  cooccurrenceSources: string[]
  settings: Record<string, any>
  fileChecksum: string
  appVersion: string
  runDate: string
}

interface ProvenanceTabProps {
  data: ProvenanceData
}

export function ProvenanceTab({ data }: ProvenanceTabProps) {
  const [copied, setCopied] = useState(false)

  const copyAll = () => {
    const text = Object.entries(data)
      .map(([key, value]) => {
        if (Array.isArray(value)) {
          return `${key}: ${value.join(", ")}`
        }
        if (typeof value === "object") {
          return `${key}: ${JSON.stringify(value, null, 2)}`
        }
        return `${key}: ${value}`
      })
      .join("\n")
    
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const renderValue = (value: any): string => {
    if (Array.isArray(value)) {
      return value.join(", ")
    }
    if (typeof value === "object") {
      return JSON.stringify(value, null, 2)
    }
    return String(value)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-medium text-gray-900">Provenance</h2>
        <button
          onClick={copyAll}
          className="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
        >
          {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
          {copied ? "Copied!" : "Copy all"}
        </button>
      </div>

      <div className="bg-gray-50 rounded-lg p-6">
        <table className="w-full">
          <tbody>
            {Object.entries(data).map(([key, value]) => (
              <tr key={key} className="border-b border-gray-200 last:border-0">
                <td className="py-3 pr-4 text-sm font-medium text-gray-700 align-top w-1/3">
                  {key
                    .replace(/([A-Z])/g, " $1")
                    .replace(/^./, (str) => str.toUpperCase())
                    .trim()}
                </td>
                <td className="py-3 text-sm text-gray-900 font-mono">
                  {renderValue(value)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
        <p className="text-sm text-amber-800">
          <strong>Note:</strong> This provenance information ensures your results are fully reproducible. 
          All model versions, database versions, and settings are recorded.
        </p>
      </div>
    </div>
  )
}
