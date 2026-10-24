import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { Button } from "../components/ui/Button"
import { FileDropzone } from "../components/analysis/FileDropzone"
import { ChevronLeft, ChevronRight } from "lucide-react"

export function NewAnalysis() {
  const navigate = useNavigate()
  const [step, setStep] = useState(1)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [marker, setMarker] = useState("teleo")
  const [taxon, setTaxon] = useState("Ray-finned fish")
  const [region, setRegion] = useState("")
  const [showAdvanced, setShowAdvanced] = useState(false)

  const handleFileSelect = (file: File) => {
    setSelectedFile(file)
  }

  const handleRun = () => {
    // TODO: Submit to backend
    navigate("/progress")
  }

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="mb-8">
        <button
          onClick={() => navigate(-1)}
          className="text-gray-600 hover:text-gray-900 flex items-center gap-2 mb-4"
        >
          <ChevronLeft className="h-4 w-4" />
          Back
        </button>
        <h1 className="text-2xl font-semibold text-gray-900">New analysis</h1>
        <p className="text-gray-600 mt-1">Step {step} of 3</p>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 p-8">
        {/* Step 1: File Upload */}
        <div className="mb-8">
          <h2 className="text-lg font-medium text-gray-900 mb-4">1. Sequence file</h2>
          <FileDropzone onFileSelect={handleFileSelect} />
        </div>

        {/* Step 2: What did you sample? */}
        <div className="mb-8">
          <h2 className="text-lg font-medium text-gray-900 mb-4">2. What did you sample?</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Marker
              </label>
              <select
                value={marker}
                onChange={(e) => setMarker(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="teleo">teleo (12S)</option>
                <option value="mifish">MiFish (12S)</option>
                <option value="16s">16S rRNA</option>
                <option value="coi">COI</option>
                <option value="its">ITS</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Taxon group
              </label>
              <select
                value={taxon}
                onChange={(e) => setTaxon(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="Ray-finned fish">Ray-finned fish</option>
                <option value="Marine mammals">Marine mammals</option>
                <option value="Birds">Birds</option>
                <option value="Insects">Insects</option>
                <option value="Plants">Plants</option>
                <option value="Fungi">Fungi</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Region <span className="text-gray-500 font-normal">(improves species matching)</span>
              </label>
              <select
                value={region}
                onChange={(e) => setRegion(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="">Select a region</option>
                <option value="north-atlantic">North Atlantic</option>
                <option value="mediterranean">Mediterranean</option>
                <option value="pacific">Pacific</option>
                <option value="arctic">Arctic</option>
              </select>
            </div>
          </div>
        </div>

        {/* Step 3: Settings */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-medium text-gray-900">3. Settings</h2>
            <button
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="text-sm text-primary-600 hover:underline"
            >
              {showAdvanced ? "Hide" : "Advanced"}
            </button>
          </div>

          {showAdvanced && (
            <div className="space-y-4 p-4 bg-gray-50 rounded-md">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Clustering threshold
                </label>
                <input
                  type="number"
                  step="0.01"
                  defaultValue="0.97"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Minimum reads per cluster
                </label>
                <input
                  type="number"
                  defaultValue="10"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Confidence threshold
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  max="1"
                  defaultValue="0.5"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Reference database version
                </label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500">
                  <option value="latest">Latest (v2.1.0)</option>
                  <option value="v2.0.0">v2.0.0</option>
                  <option value="v1.9.0">v1.9.0</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Model version
                </label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500">
                  <option value="latest">Latest (v1.2.0)</option>
                  <option value="v1.1.0">v1.1.0</option>
                  <option value="v1.0.0">v1.0.0</option>
                </select>
              </div>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
          <Button variant="secondary" onClick={() => navigate(-1)}>
            Cancel
          </Button>
          <Button onClick={handleRun} disabled={!selectedFile}>
            Run analysis
            <ChevronRight className="h-4 w-4 ml-2" />
          </Button>
        </div>
      </div>
    </div>
  )
}
