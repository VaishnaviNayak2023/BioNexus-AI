import { useState } from "react"
import { Button } from "../components/ui/Button"
import { Upload, Download, Eye, Plus, AlertCircle } from "lucide-react"

interface ReferenceDataset {
  id: number
  name: string
  datasetType: string
  source: string
  version: string
  date: string
  recordCount: number
  status: "Active" | "Outdated" | "Draft"
  validationReport?: string
}

export function ReferenceData() {
  const [datasets, setDatasets] = useState<ReferenceDataset[]>([
    {
      id: 1,
      name: "NCBI GenBank 12S",
      datasetType: "sequences",
      source: "NCBI",
      version: "v2.1.0",
      date: "2024-10-15",
      recordCount: 9909,
      status: "Active",
      validationReport: "0 unmatched names, 12 duplicates removed"
    },
    {
      id: 2,
      name: "Fish Tree of Life",
      datasetType: "phylogeny",
      source: "Rabosky et al. 2018",
      version: "v2",
      date: "2024-10-15",
      recordCount: 31500,
      status: "Active",
      validationReport: "All species matched"
    },
    {
      id: 3,
      name: "FISHGLOB Trawl Surveys",
      datasetType: "cooccurrence",
      source: "FISHGLOB_data",
      version: "v1.0",
      date: "2024-10-15",
      recordCount: 216548,
      status: "Active",
      validationReport: "29 surveys validated"
    },
    {
      id: 4,
      name: "FishBase Traits",
      datasetType: "traits",
      source: "FishBase",
      version: "v1.2",
      date: "2024-09-01",
      recordCount: 34000,
      status: "Outdated",
      validationReport: "500 species missing trait data"
    },
  ])
  const [selectedDataset, setSelectedDataset] = useState<ReferenceDataset | null>(null)
  const [showUpload, setShowUpload] = useState(false)

  const getStatusColor = (status: string) => {
    switch (status) {
      case "Active": return "bg-green-100 text-green-800"
      case "Outdated": return "bg-amber-100 text-amber-800"
      case "Draft": return "bg-gray-100 text-gray-800"
      default: return "bg-gray-100 text-gray-800"
    }
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Reference data</h1>
          <p className="text-gray-600 mt-1">Manage reference sequences, phylogeny, co-occurrence data, and trait tables</p>
        </div>
        <Button onClick={() => setShowUpload(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Upload dataset
        </Button>
      </div>

      {/* Dataset Table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Name
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Type
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Source
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Version
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Records
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {datasets.map((dataset) => (
              <tr 
                key={dataset.id}
                className="hover:bg-gray-50 cursor-pointer"
                onClick={() => setSelectedDataset(dataset)}
              >
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {dataset.name}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 capitalize">
                  {dataset.datasetType}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {dataset.source}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-mono">
                  {dataset.version}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {dataset.recordCount.toLocaleString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${getStatusColor(dataset.status)}`}>
                    {dataset.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  <div className="flex gap-2">
                    <button 
                      className="text-primary-600 hover:text-primary-900"
                      title="View details"
                    >
                      <Eye className="h-4 w-4" />
                    </button>
                    <button 
                      className="text-gray-600 hover:text-gray-900"
                      title="Download"
                    >
                      <Download className="h-4 w-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Validation Report Panel */}
      {selectedDataset && (
        <div className="mt-6 bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className="text-lg font-medium text-gray-900">{selectedDataset.name}</h3>
              <p className="text-sm text-gray-600 mt-1">Validation Report</p>
            </div>
            <button
              onClick={() => setSelectedDataset(null)}
              className="text-gray-400 hover:text-gray-600"
            >
              ×
            </button>
          </div>
          
          <div className="space-y-4">
            <div className="flex items-start gap-3 p-4 bg-green-50 rounded-lg border border-green-200">
              <AlertCircle className="h-5 w-5 text-green-600 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-green-900">Validation Passed</p>
                <p className="text-sm text-green-700 mt-1">{selectedDataset.validationReport}</p>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-600">Unmatched species names</p>
                <p className="font-medium text-gray-900">0</p>
              </div>
              <div>
                <p className="text-gray-600">Duplicate sequences</p>
                <p className="font-medium text-gray-900">12 (removed)</p>
              </div>
              <div>
                <p className="text-gray-600">Sequences with ambiguous bases</p>
                <p className="font-medium text-gray-900">23</p>
              </div>
              <div>
                <p className="text-gray-600">Species missing from tree</p>
                <p className="font-medium text-gray-900">0</p>
              </div>
            </div>
            
            <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
              <Button variant="secondary" size="sm">
                <Download className="h-4 w-4 mr-2" />
                Download report
              </Button>
              <Button size="sm">
                Publish as new version
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Upload Modal */}
      {showUpload && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-semibold mb-4">Upload reference dataset</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Dataset name
                </label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="My reference database"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Dataset type
                </label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500">
                  <option value="sequences">Sequences</option>
                  <option value="phylogeny">Phylogeny</option>
                  <option value="cooccurrence">Co-occurrence</option>
                  <option value="traits">Traits</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Source
                </label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="e.g., NCBI, FishBase"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  File
                </label>
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                  <Upload className="h-8 w-8 mx-auto text-gray-400 mb-2" />
                  <p className="text-sm text-gray-600">Drag file here or click to browse</p>
                </div>
              </div>
              <div className="flex justify-end gap-3 pt-4">
                <Button variant="secondary" onClick={() => setShowUpload(false)}>
                  Cancel
                </Button>
                <Button>Upload and validate</Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
