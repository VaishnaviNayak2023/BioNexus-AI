import { useState } from "react"
import { AlertCircle, Check, X, Minus } from "lucide-react"

interface ComparisonRow {
  sequenceGroup: string
  thisModel: string
  baseline: string
  status: "match" | "genus-level" | "model-only" | "conflict" | "baseline-only"
}

export function CompareBaseline() {
  const [selectedBaseline, setSelectedBaseline] = useState("ecotag")
  
  const [comparisons, setComparisons] = useState<ComparisonRow[]>([
    { sequenceGroup: "MOTU_001", thisModel: "Sparus aurata", baseline: "Sparus aurata", status: "match" },
    { sequenceGroup: "MOTU_005", thisModel: "Labrus bergylta", baseline: "Labridae", status: "genus-level" },
    { sequenceGroup: "MOTU_009", thisModel: "Mullus surmuletus", baseline: "(no assignment)", status: "model-only" },
    { sequenceGroup: "MOTU_014", thisModel: "Sardina pilchardus", baseline: "Engraulis encrasicolus", status: "conflict" },
    { sequenceGroup: "MOTU_018", thisModel: "(no assignment)", baseline: "Gadus morhua", status: "baseline-only" },
    { sequenceGroup: "MOTU_023", thisModel: "Pagellus erythrinus", baseline: "Pagellus erythrinus", status: "match" },
  ])

  const summary = {
    match: comparisons.filter(c => c.status === "match").length,
    genus: comparisons.filter(c => c.status === "genus-level").length,
    family: comparisons.filter(c => c.status === "genus-level").length,
    differ: comparisons.filter(c => c.status === "conflict").length,
    modelOnly: comparisons.filter(c => c.status === "model-only").length,
    baselineOnly: comparisons.filter(c => c.status === "baseline-only").length,
  }

  const agreement = Math.round(((summary.match + summary.genus + summary.family) / comparisons.length) * 100)

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "match": return <Check className="h-4 w-4 text-green-600" />
      case "genus-level": return <Minus className="h-4 w-4 text-amber-600" />
      case "model-only": return <AlertCircle className="h-4 w-4 text-blue-600" />
      case "conflict": return <X className="h-4 w-4 text-red-600" />
      case "baseline-only": return <AlertCircle className="h-4 w-4 text-gray-600" />
      default: return null
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "match": return "bg-green-50 text-green-900"
      case "genus-level": return "bg-amber-50 text-amber-900"
      case "model-only": return "bg-blue-50 text-blue-900"
      case "conflict": return "bg-red-50 text-red-900"
      case "baseline-only": return "bg-gray-50 text-gray-900"
      default: return "bg-gray-50 text-gray-900"
    }
  }

  const getStatusLabel = (status: string) => {
    switch (status) {
      case "match": return "Match"
      case "genus-level": return "Genus-level"
      case "model-only": return "Model only"
      case "conflict": return "Conflict"
      case "baseline-only": return "Baseline only"
      default: return status
    }
  }

  return (
    <div className="space-y-6">
      {/* Baseline Selector */}
      <div className="flex items-center gap-4">
        <label className="text-sm font-medium text-gray-700">Compare with:</label>
        <select
          value={selectedBaseline}
          onChange={(e) => setSelectedBaseline(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <option value="ecotag">ECOTAG (uploaded)</option>
          <option value="blast">BLAST</option>
          <option value="vsearch">VSEARCH</option>
        </select>
        
        <div className="ml-auto flex items-center gap-2">
          <span className="text-sm text-gray-600">Agreement:</span>
          <span className="text-lg font-semibold text-primary-600">{agreement}%</span>
          <button className="text-sm text-primary-600 hover:underline ml-2">
            What does this mean?
          </button>
        </div>
      </div>

      {/* Agreement Summary */}
      <div className="grid grid-cols-5 gap-4">
        <div className="bg-green-50 rounded-lg p-4 border border-green-200">
          <p className="text-2xl font-semibold text-green-600">{summary.match}</p>
          <p className="text-sm text-green-700">Match at species</p>
        </div>
        <div className="bg-amber-50 rounded-lg p-4 border border-amber-200">
          <p className="text-2xl font-semibold text-amber-600">{summary.genus}</p>
          <p className="text-sm text-amber-700">Match at genus</p>
        </div>
        <div className="bg-amber-50 rounded-lg p-4 border border-amber-200">
          <p className="text-2xl font-semibold text-amber-600">{summary.family}</p>
          <p className="text-sm text-amber-700">Match at family</p>
        </div>
        <div className="bg-red-50 rounded-lg p-4 border border-red-200">
          <p className="text-2xl font-semibold text-red-600">{summary.differ}</p>
          <p className="text-sm text-red-700">Differ</p>
        </div>
        <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
          <p className="text-2xl font-semibold text-blue-600">{summary.modelOnly}</p>
          <p className="text-sm text-blue-700">Model only</p>
        </div>
      </div>

      {/* Comparison Table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Sequence group
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                This model
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Baseline
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {comparisons.map((comparison) => (
              <tr 
                key={comparison.sequenceGroup}
                className="hover:bg-gray-50 cursor-pointer"
              >
                <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900">
                  {comparison.sequenceGroup}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {comparison.thisModel}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {comparison.baseline}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${getStatusColor(comparison.status)}`}>
                    {getStatusIcon(comparison.status)}
                    <span>{getStatusLabel(comparison.status)}</span>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Info Box */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-sm text-blue-800">
          <strong>Tip:</strong> Conflicts are sorted to the top by default. Click on any row to see the species detail panel with both predictions.
        </p>
      </div>
    </div>
  )
}
