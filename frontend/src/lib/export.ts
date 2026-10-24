interface Prediction {
  id: number
  sequenceGroup: string
  predictedSpecies: string
  rank: string
  confidence: number
  readCount: number
  isZeroShot: boolean
}

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

export function exportCSV(predictions: Prediction[], filename: string = "predictions.csv") {
  const headers = ["Sequence Group", "Prediction", "Rank", "Confidence", "Confidence Level", "Reads", "Zero-Shot"]
  const rows = predictions.map(p => [
    p.sequenceGroup,
    p.predictedSpecies,
    p.rank,
    p.confidence.toFixed(3),
    p.confidence >= 0.7 ? "High" : p.confidence >= 0.5 ? "Medium" : "Low",
    p.readCount,
    p.isZeroShot ? "Yes" : "No"
  ])

  const csvContent = [
    headers.join(","),
    ...rows.map(row => row.map(cell => `"${cell}"`).join(","))
  ].join("\n")

  downloadFile(csvContent, filename, "text/csv")
}

export function exportJSON(
  predictions: Prediction[],
  provenance: ProvenanceData,
  filename: string = "results.json"
) {
  const jsonContent = JSON.stringify({
    provenance,
    predictions,
    exportedAt: new Date().toISOString()
  }, null, 2)

  downloadFile(jsonContent, filename, "application/json")
}

function downloadFile(content: string, filename: string, mimeType: string) {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const link = document.createElement("a")
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}
