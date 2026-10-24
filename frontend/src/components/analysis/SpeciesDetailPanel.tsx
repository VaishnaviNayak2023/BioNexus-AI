import { X, ExternalLink, Flag } from "lucide-react"
import { ConfidenceBadge } from "../ui/ConfidenceBadge"
import { cn } from "../../lib/utils"

interface SpeciesDetailPanelProps {
  isOpen: boolean
  onClose: () => void
  species: {
    name: string
    commonName: string
    confidence: number
    isZeroShot: boolean
    closestReferenceIdentity?: number
    seenInRegion: boolean
    foundWithCount: number
    nearestRelatives: string[]
    traits: {
      maxLength: string
      trophicLevel: number
      habitat: string
    }
  } | null
}

export function SpeciesDetailPanel({ isOpen, onClose, species }: SpeciesDetailPanelProps) {
  if (!isOpen || !species) return null

  return (
    <div className={cn(
      "fixed inset-y-0 right-0 w-96 bg-white border-l border-gray-200 shadow-lg transform transition-transform duration-300 ease-in-out z-50",
      isOpen ? "translate-x-0" : "translate-x-full"
    )}>
      <div className="h-full flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h2 className="text-xl font-semibold text-gray-900">{species.name}</h2>
              <p className="text-gray-600 mt-1">{species.commonName}</p>
              <div className="mt-3">
                <ConfidenceBadge confidence={species.confidence} />
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="h-6 w-6" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Why this prediction */}
          <div>
            <h3 className="text-sm font-medium text-gray-900 mb-3">Why this prediction</h3>
            <ul className="space-y-2 text-sm text-gray-700">
              {species.isZeroShot ? (
                <li className="text-amber-700">
                  No reference sequence for this species; predicted from relatives and co-occurring species
                </li>
              ) : (
                <>
                  <li>
                    Closest reference: {species.closestReferenceIdentity?.toFixed(1)}% identical
                  </li>
                  <li>
                    Seen in region: {species.seenInRegion ? "Yes (trawl data)" : "No"}
                  </li>
                  <li>
                    Found with: {species.foundWithCount} other species here
                  </li>
                </>
              )}
            </ul>
          </div>

          {/* Nearest relatives */}
          <div>
            <h3 className="text-sm font-medium text-gray-900 mb-3">Nearest relatives in model space</h3>
            <div className="flex flex-wrap gap-2">
              {species.nearestRelatives.map((relative, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-2.5 py-1 rounded-md bg-gray-100 text-sm text-gray-700"
                >
                  {relative}
                </span>
              ))}
            </div>
          </div>

          {/* Traits */}
          <div>
            <h3 className="text-sm font-medium text-gray-900 mb-3">
              Traits {species.isZeroShot && <span className="text-amber-600">(Estimated)</span>}
            </h3>
            <div className="bg-gray-50 rounded-lg p-4">
              <table className="w-full text-sm">
                <tbody>
                  <tr className="border-b border-gray-200">
                    <td className="py-2 text-gray-600">Max length</td>
                    <td className="py-2 text-gray-900 font-medium">{species.traits.maxLength}</td>
                  </tr>
                  <tr className="border-b border-gray-200">
                    <td className="py-2 text-gray-600">Trophic level</td>
                    <td className="py-2 text-gray-900 font-medium">{species.traits.trophicLevel}</td>
                  </tr>
                  <tr>
                    <td className="py-2 text-gray-600">Habitat</td>
                    <td className="py-2 text-gray-900 font-medium">{species.traits.habitat}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-200 space-y-3">
          <button className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors text-sm font-medium">
            <ExternalLink className="h-4 w-4" />
            View on FishBase
          </button>
          <button className="w-full flex items-center justify-center gap-2 px-4 py-2 border border-red-300 text-red-700 rounded-md hover:bg-red-50 transition-colors text-sm font-medium">
            <Flag className="h-4 w-4" />
            Flag as wrong
          </button>
        </div>
      </div>
    </div>
  )
}
