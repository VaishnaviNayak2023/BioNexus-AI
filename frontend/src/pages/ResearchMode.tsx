import { useState } from "react"
import { Button } from "../components/ui/Button"
import { Plus, Play, Download, TrendingUp } from "lucide-react"

interface Experiment {
  id: number
  name: string
  split: string
  speciesAccuracy: number | string
  genusAccuracy: number | string
  familyAccuracy: number | string
  orderAccuracy: number | string
  ece: number | string
  status: "completed" | "running" | "pending"
}

export function ResearchMode() {
  const [experiments, setExperiments] = useState<Experiment[]>([
    {
      id: 1,
      name: "baseline-repro",
      split: "split_v1",
      speciesAccuracy: 24.2,
      genusAccuracy: 56.2,
      familyAccuracy: 80.5,
      orderAccuracy: 89.1,
      ece: 0.08,
      status: "completed"
    },
    {
      id: 2,
      name: "multi-tree",
      split: "split_v1",
      speciesAccuracy: "--",
      genusAccuracy: "--",
      familyAccuracy: "--",
      orderAccuracy: "--",
      ece: "--",
      status: "pending"
    },
    {
      id: 3,
      name: "gated-cooc",
      split: "split_v1",
      speciesAccuracy: "Running",
      genusAccuracy: "--",
      familyAccuracy: "--",
      orderAccuracy: "--",
      ece: "--",
      status: "running"
    },
  ])
  const [selectedExperiments, setSelectedExperiments] = useState<number[]>([])
  const [showNewExperiment, setShowNewExperiment] = useState(false)
  const [activeView, setActiveView] = useState<"table" | "calibration">("table")

  const toggleSelect = (id: number) => {
    setSelectedExperiments(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    )
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Research mode</h1>
          <p className="text-gray-600 mt-1">Compare models, trees and settings; check accuracy on held-out species</p>
        </div>
        <Button onClick={() => setShowNewExperiment(true)}>
          <Plus className="h-4 w-4 mr-2" />
          New experiment
        </Button>
      </div>

      {/* View Toggle */}
      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setActiveView("table")}
          className={`px-4 py-2 rounded-md text-sm font-medium ${
            activeView === "table"
              ? "bg-primary-100 text-primary-700"
              : "bg-gray-100 text-gray-700 hover:bg-gray-200"
          }`}
        >
          Experiments
        </button>
        <button
          onClick={() => setActiveView("calibration")}
          className={`px-4 py-2 rounded-md text-sm font-medium ${
            activeView === "calibration"
              ? "bg-primary-100 text-primary-700"
              : "bg-gray-100 text-gray-700 hover:bg-gray-200"
          }`}
        >
          <TrendingUp className="h-4 w-4 inline mr-2" />
          Calibration plot
        </button>
      </div>

      {/* Experiments Table View */}
      {activeView === "table" && (
        <>
          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden mb-4">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-4 py-3 w-10">
                    <input
                      type="checkbox"
                      checked={selectedExperiments.length === experiments.length}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedExperiments(experiments.map(e => e.id))
                        } else {
                          setSelectedExperiments([])
                        }
                      }}
                    />
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Split
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Species
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Genus
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Family
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Order
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    ECE
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {experiments.map((experiment) => (
                  <tr key={experiment.id} className="hover:bg-gray-50">
                    <td className="px-4 py-4">
                      <input
                        type="checkbox"
                        checked={selectedExperiments.includes(experiment.id)}
                        onChange={() => toggleSelect(experiment.id)}
                      />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {experiment.name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {experiment.split}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {typeof experiment.speciesAccuracy === "number"
                        ? `${experiment.speciesAccuracy.toFixed(1)}%`
                        : experiment.speciesAccuracy}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {typeof experiment.genusAccuracy === "number"
                        ? `${experiment.genusAccuracy.toFixed(1)}%`
                        : experiment.genusAccuracy}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {typeof experiment.familyAccuracy === "number"
                        ? `${experiment.familyAccuracy.toFixed(1)}%`
                        : experiment.familyAccuracy}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {typeof experiment.orderAccuracy === "number"
                        ? `${experiment.orderAccuracy.toFixed(1)}%`
                        : experiment.orderAccuracy}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {typeof experiment.ece === "number"
                        ? experiment.ece.toFixed(3)
                        : experiment.ece}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${
                        experiment.status === "completed"
                          ? "bg-green-100 text-green-800"
                          : experiment.status === "running"
                          ? "bg-blue-100 text-blue-800"
                          : "bg-gray-100 text-gray-800"
                      }`}>
                        {experiment.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3">
            <Button
              variant="secondary"
              disabled={selectedExperiments.length < 2}
              onClick={() => setActiveView("calibration")}
            >
              Compare selected
            </Button>
            <Button variant="secondary">
              <Download className="h-4 w-4 mr-2" />
              Download results
            </Button>
          </div>
        </>
      )}

      {/* Calibration Plot View */}
      {activeView === "calibration" && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Calibration Curve</h3>
          <div className="h-96 flex items-center justify-center bg-gray-50 rounded-lg">
            <p className="text-gray-600">Calibration plot visualization coming soon</p>
            <p className="text-sm text-gray-500 mt-2">
              Shows predicted probability against observed accuracy
            </p>
          </div>
          <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-800">
              <strong>Calibration metrics:</strong> ECE (Expected Calibration Error) measures how well the model's confidence scores match actual accuracy. Lower ECE indicates better calibration.
            </p>
          </div>
        </div>
      )}

      {/* New Experiment Modal */}
      {showNewExperiment && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-semibold mb-4">New experiment</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Experiment name
                </label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="my-experiment"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Split
                </label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500">
                  <option value="split_v1">split_v1</option>
                  <option value="split_v2">split_v2</option>
                  <option value="split_v3">split_v3</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Model configuration
                </label>
                <textarea
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  rows={3}
                  placeholder='{"embedding_dim": 64, "use_cooccurrence": true}'
                />
              </div>
              <div className="flex justify-end gap-3 pt-4">
                <Button variant="secondary" onClick={() => setShowNewExperiment(false)}>
                  Cancel
                </Button>
                <Button>
                  <Play className="h-4 w-4 mr-2" />
                  Run experiment
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
