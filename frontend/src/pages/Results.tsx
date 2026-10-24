import { useState } from "react"
import { useParams } from "react-router-dom"
import { Button } from "../components/ui/Button"
import { ConfidenceBadge } from "../components/ui/ConfidenceBadge"
import { SpeciesDetailPanel } from "../components/analysis/SpeciesDetailPanel"
import { ProvenanceTab } from "../components/analysis/ProvenanceTab"
import { CommunityView } from "../components/analysis/CommunityView"
import { CompareBaseline } from "../components/analysis/CompareBaseline"
import { exportCSV, exportJSON } from "../lib/export"
import { generateHTMLReport, downloadHTMLReport, generateShareableLink } from "../lib/report"
import { Download, FileText, Filter, Share2 } from "lucide-react"

interface Prediction {
  id: number
  sequenceGroup: string
  predictedSpecies: string
  rank: "Species" | "Genus" | "Family" | "Order"
  confidence: number
  readCount: number
  isZeroShot: boolean
}

export function Results() {
  const { analysisId } = useParams()
  const [activeTab, setActiveTab] = useState<"predictions" | "community" | "compare" | "provenance">("predictions")
  const [showBestReliableRank, setShowBestReliableRank] = useState(false)
  const [selectedSpecies, setSelectedSpecies] = useState<any>(null)
  const [showSpeciesDetail, setShowSpeciesDetail] = useState(false)

  // Mock data
  const predictions: Prediction[] = [
    { id: 1, sequenceGroup: "MOTU_001", predictedSpecies: "Sparus aurata", rank: "Species", confidence: 0.92, readCount: 14230, isZeroShot: false },
    { id: 2, sequenceGroup: "MOTU_002", predictedSpecies: "Sparidae", rank: "Family", confidence: 0.61, readCount: 3410, isZeroShot: false },
    { id: 3, sequenceGroup: "MOTU_003", predictedSpecies: "Gadus sp.", rank: "Genus", confidence: 0.57, readCount: 2880, isZeroShot: false },
    { id: 4, sequenceGroup: "MOTU_004", predictedSpecies: "Pagellus erythrinus", rank: "Species", confidence: 0.18, readCount: 412, isZeroShot: true },
    { id: 5, sequenceGroup: "MOTU_005", predictedSpecies: "Labrus bergylta", rank: "Species", confidence: 0.85, readCount: 1250, isZeroShot: false },
    { id: 6, sequenceGroup: "MOTU_006", predictedSpecies: "Mullus surmuletus", rank: "Species", confidence: 0.78, readCount: 980, isZeroShot: false },
  ]

  const summary = {
    total: predictions.length,
    high: predictions.filter(p => p.confidence >= 0.7).length,
    medium: predictions.filter(p => p.confidence >= 0.5 && p.confidence < 0.7).length,
    low: predictions.filter(p => p.confidence < 0.5).length,
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-gray-900">Station 12</h1>
        <p className="text-gray-600 mt-1">Analysis results</p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="flex gap-4">
          {[
            { id: "predictions", label: "Predictions" },
            { id: "community", label: "Community" },
            { id: "compare", label: "Compare" },
            { id: "provenance", label: "Provenance" },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.id
                  ? "border-primary-500 text-primary-700"
                  : "border-transparent text-gray-600 hover:text-gray-900"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Predictions Tab */}
      {activeTab === "predictions" && (
        <>
          {/* Summary */}
          <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Summary</h2>
            <div className="flex gap-8">
              <div>
                <p className="text-2xl font-semibold text-gray-900">{summary.total}</p>
                <p className="text-sm text-gray-600">Total species</p>
              </div>
              <div>
                <p className="text-2xl font-semibold text-green-600">{summary.high}</p>
                <p className="text-sm text-gray-600">High confidence</p>
              </div>
              <div>
                <p className="text-2xl font-semibold text-amber-600">{summary.medium}</p>
                <p className="text-sm text-gray-600">Medium confidence</p>
              </div>
              <div>
                <p className="text-2xl font-semibold text-red-600">{summary.low}</p>
                <p className="text-sm text-gray-600">Low confidence</p>
              </div>
            </div>
          </div>

          {/* Controls */}
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-700">Show predictions at:</span>
                <label className="flex items-center gap-2">
                  <input
                    type="radio"
                    name="rank"
                    checked={!showBestReliableRank}
                    onChange={() => setShowBestReliableRank(false)}
                    className="text-primary-600 focus:ring-primary-500"
                  />
                  <span className="text-sm">Species</span>
                </label>
                <label className="flex items-center gap-2">
                  <input
                    type="radio"
                    name="rank"
                    checked={showBestReliableRank}
                    onChange={() => setShowBestReliableRank(true)}
                    className="text-primary-600 focus:ring-primary-500"
                  />
                  <span className="text-sm">Best reliable rank</span>
                </label>
              </div>
              <Button variant="ghost" size="sm">
                <Filter className="h-4 w-4 mr-2" />
                Filters
              </Button>
            </div>
            <div className="flex gap-2">
              <Button 
                variant="secondary" 
                size="sm"
                onClick={() => exportCSV(predictions, `station-12-predictions.csv`)}
              >
                <Download className="h-4 w-4 mr-2" />
                Export CSV
              </Button>
              <Button 
                variant="secondary" 
                size="sm"
                onClick={() => exportJSON(
                  predictions,
                  {
                    modelName: "DNA Encoder + Co-occurrence",
                    modelVersion: "v1.2.0",
                    referenceDbName: "NCBI GenBank 12S",
                    referenceDbVersion: "v2.1.0",
                    referenceDbDate: "2024-10-15",
                    phylogenyVersion: "Fish Tree of Life v2",
                    cooccurrenceSources: ["FISHGLOB", "DATRAS"],
                    settings: {
                      marker: "teleo",
                      clusteringThreshold: 0.97,
                      minReadsPerCluster: 10,
                      confidenceThreshold: 0.5,
                    },
                    fileChecksum: "a1b2c3d4e5f6",
                    appVersion: "1.0.0",
                    runDate: new Date().toISOString(),
                  },
                  `station-12-results.json`
                )}
              >
                <Download className="h-4 w-4 mr-2" />
                Export JSON
              </Button>
              <Button 
                variant="secondary" 
                size="sm"
                onClick={() => {
                  const html = generateHTMLReport(
                    "Station 12",
                    predictions,
                    {
                      modelName: "DNA Encoder + Co-occurrence",
                      modelVersion: "v1.2.0",
                      referenceDbName: "NCBI GenBank 12S",
                      referenceDbVersion: "v2.1.0",
                      referenceDbDate: "2024-10-15",
                      phylogenyVersion: "Fish Tree of Life v2",
                      cooccurrenceSources: ["FISHGLOB", "DATRAS"],
                      settings: {
                        marker: "teleo",
                        clusteringThreshold: 0.97,
                        minReadsPerCluster: 10,
                        confidenceThreshold: 0.5,
                      },
                      fileChecksum: "a1b2c3d4e5f6",
                      appVersion: "1.0.0",
                      runDate: new Date().toISOString(),
                    },
                    summary
                  )
                  downloadHTMLReport(html, "station-12-report.html")
                }}
              >
                <FileText className="h-4 w-4 mr-2" />
                Create report
              </Button>
              <Button 
                variant="secondary" 
                size="sm"
                onClick={() => {
                  const link = generateShareableLink(analysisId || "1")
                  navigator.clipboard.writeText(link)
                  alert("Shareable link copied to clipboard!")
                }}
              >
                <Share2 className="h-4 w-4 mr-2" />
                Share
              </Button>
            </div>
          </div>

          {/* Predictions Table */}
          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Sequence group
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Prediction
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Rank
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Confidence
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Reads
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {predictions.map((prediction) => (
                  <tr 
                    key={prediction.id} 
                    className="hover:bg-gray-50 cursor-pointer"
                    onClick={() => {
                      setSelectedSpecies({
                        name: prediction.predictedSpecies,
                        commonName: prediction.predictedSpecies.split(' ')[0] + " (common name)",
                        confidence: prediction.confidence,
                        isZeroShot: prediction.isZeroShot,
                        closestReferenceIdentity: prediction.isZeroShot ? undefined : 99.2,
                        seenInRegion: true,
                        foundWithCount: 6,
                        nearestRelatives: ["Sparus sp.", "Pagrus pagrus", "Dentex dentex"],
                        traits: {
                          maxLength: "70 cm",
                          trophicLevel: 3.2,
                          habitat: "Reef"
                        }
                      })
                      setShowSpeciesDetail(true)
                    }}
                  >
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900">
                      {prediction.sequenceGroup}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {prediction.isZeroShot && (
                        <span className="text-amber-600 mr-1">Possible:</span>
                      )}
                      {prediction.predictedSpecies}
                      {prediction.isZeroShot && (
                        <span className="ml-1 text-gray-400">[?]</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {prediction.rank}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <ConfidenceBadge confidence={prediction.confidence} />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {prediction.readCount.toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-between mt-4">
            <p className="text-sm text-gray-600">Page 1 of 4</p>
            <div className="flex gap-2">
              <Button variant="ghost" size="sm" disabled>
                Previous
              </Button>
              <Button variant="ghost" size="sm">
                Next
              </Button>
            </div>
          </div>
        </>
      )}

      {/* Community Tab */}
      {activeTab === "community" && (
        <CommunityView />
      )}

      {/* Compare Tab */}
      {activeTab === "compare" && (
        <CompareBaseline />
      )}

      {activeTab === "provenance" && (
        <div className="bg-white rounded-lg border border-gray-200 p-8">
          <ProvenanceTab
            data={{
              modelName: "DNA Encoder + Co-occurrence",
              modelVersion: "v1.2.0",
              referenceDbName: "NCBI GenBank 12S",
              referenceDbVersion: "v2.1.0",
              referenceDbDate: "2024-10-15",
              phylogenyVersion: "Fish Tree of Life v2",
              cooccurrenceSources: ["FISHGLOB", "DATRAS"],
              settings: {
                marker: "teleo",
                clusteringThreshold: 0.97,
                minReadsPerCluster: 10,
                confidenceThreshold: 0.5,
              },
              fileChecksum: "a1b2c3d4e5f6",
              appVersion: "1.0.0",
              runDate: new Date().toISOString(),
            }}
          />
        </div>
      )}

      {/* Species Detail Panel */}
      <SpeciesDetailPanel
        isOpen={showSpeciesDetail}
        onClose={() => setShowSpeciesDetail(false)}
        species={selectedSpecies}
      />
    </div>
  )
}
