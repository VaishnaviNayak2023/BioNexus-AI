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

export function generateHTMLReport(
  analysisName: string,
  predictions: Prediction[],
  provenance: ProvenanceData,
  summary: { total: number; high: number; medium: number; low: number }
): string {
  const date = new Date().toLocaleDateString()
  
  const predictionsTable = predictions.map(p => `
    <tr>
      <td>${p.sequenceGroup}</td>
      <td>${p.isZeroShot ? '<span class="zero-shot">Possible:</span> ' : ''}${p.predictedSpecies}</td>
      <td>${p.rank}</td>
      <td>
        <span class="confidence-badge ${p.confidence >= 0.7 ? 'high' : p.confidence >= 0.5 ? 'medium' : 'low'}">
          ${Math.round(p.confidence * 100)}%
        </span>
      </td>
      <td>${p.readCount.toLocaleString()}</td>
    </tr>
  `).join('')

  return `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>eDNA Analysis Report - ${analysisName}</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      line-height: 1.6;
      color: #333;
      max-width: 1200px;
      margin: 0 auto;
      padding: 40px 20px;
    }
    h1 { color: #0d9488; border-bottom: 2px solid #0d9488; padding-bottom: 10px; }
    h2 { color: #1f2937; margin-top: 30px; }
    .summary { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 20px 0; }
    .summary-card { background: #f9fafb; padding: 20px; border-radius: 8px; text-align: center; }
    .summary-card .number { font-size: 2em; font-weight: bold; }
    .summary-card .label { color: #6b7280; font-size: 0.9em; }
    .high { color: #22c55e; }
    .medium { color: #f59e0b; }
    .low { color: #ef4444; }
    table { width: 100%; border-collapse: collapse; margin: 20px 0; }
    th, td { padding: 12px; text-align: left; border-bottom: 1px solid #e5e7eb; }
    th { background: #f9fafb; font-weight: 600; }
    .confidence-badge { padding: 4px 8px; border-radius: 12px; font-size: 0.85em; font-weight: 600; }
    .confidence-badge.high { background: #dcfce7; color: #166534; }
    .confidence-badge.medium { background: #fef3c7; color: #92400e; }
    .confidence-badge.low { background: #fee2e2; color: #991b1b; }
    .zero-shot { color: #f59e0b; font-style: italic; }
    .provenance { background: #f9fafb; padding: 20px; border-radius: 8px; margin: 20px 0; }
    .provenance-row { display: flex; padding: 8px 0; border-bottom: 1px solid #e5e7eb; }
    .provenance-label { width: 200px; font-weight: 600; color: #374151; }
    .provenance-value { flex: 1; color: #6b7280; }
    .caveat { background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 30px 0; }
    .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #e5e7eb; color: #6b7280; font-size: 0.9em; }
  </style>
</head>
<body>
  <h1>eDNA Taxonomy Analysis Report</h1>
  <p><strong>Analysis:</strong> ${analysisName}</p>
  <p><strong>Date:</strong> ${date}</p>

  <h2>Summary</h2>
  <div class="summary">
    <div class="summary-card">
      <div class="number">${summary.total}</div>
      <div class="label">Total species</div>
    </div>
    <div class="summary-card">
      <div class="number high">${summary.high}</div>
      <div class="label">High confidence</div>
    </div>
    <div class="summary-card">
      <div class="number medium">${summary.medium}</div>
      <div class="label">Medium confidence</div>
    </div>
    <div class="summary-card">
      <div class="number low">${summary.low}</div>
      <div class="label">Low confidence</div>
    </div>
  </div>

  <h2>Predictions</h2>
  <table>
    <thead>
      <tr>
        <th>Sequence Group</th>
        <th>Prediction</th>
        <th>Rank</th>
        <th>Confidence</th>
        <th>Reads</th>
      </tr>
    </thead>
    <tbody>
      ${predictionsTable}
    </tbody>
  </table>

  <h2>Provenance</h2>
  <div class="provenance">
    <div class="provenance-row">
      <span class="provenance-label">Model</span>
      <span class="provenance-value">${provenance.modelName} v${provenance.modelVersion}</span>
    </div>
    <div class="provenance-row">
      <span class="provenance-label">Reference Database</span>
      <span class="provenance-value">${provenance.referenceDbName} v${provenance.referenceDbVersion} (${provenance.referenceDbDate})</span>
    </div>
    <div class="provenance-row">
      <span class="provenance-label">Phylogeny</span>
      <span class="provenance-value">${provenance.phylogenyVersion}</span>
    </div>
    <div class="provenance-row">
      <span class="provenance-label">Co-occurrence Sources</span>
      <span class="provenance-value">${provenance.cooccurrenceSources.join(", ")}</span>
    </div>
    <div class="provenance-row">
      <span class="provenance-label">Marker</span>
      <span class="provenance-value">${provenance.settings.marker || "teleo"}</span>
    </div>
    <div class="provenance-row">
      <span class="provenance-label">Confidence Threshold</span>
      <span class="provenance-value">${provenance.settings.confidenceThreshold || 0.5}</span>
    </div>
    <div class="provenance-row">
      <span class="provenance-label">File Checksum</span>
      <span class="provenance-value">${provenance.fileChecksum}</span>
    </div>
    <div class="provenance-row">
      <span class="provenance-label">App Version</span>
      <span class="provenance-value">${provenance.appVersion}</span>
    </div>
    <div class="provenance-row">
      <span class="provenance-label">Run Date</span>
      <span class="provenance-value">${new Date(provenance.runDate).toLocaleString()}</span>
    </div>
  </div>

  <div class="caveat">
    <strong>Important Note:</strong> Predictions for species missing from reference databases (marked as "Possible:") are based on zero-shot learning and should be confirmed with additional evidence. Confidence scores reflect the model's estimated probability and are not guarantees of accuracy.
  </div>

  <div class="footer">
    <p>Generated by eDNA Taxonomy Workbench v${provenance.appVersion}</p>
    <p>This report includes all information needed to reproduce the analysis.</p>
  </div>
</body>
</html>
  `
}

export function downloadHTMLReport(html: string, filename: string) {
  const blob = new Blob([html], { type: "text/html" })
  const url = URL.createObjectURL(blob)
  const link = document.createElement("a")
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

export function generateShareableLink(analysisId: string): string {
  // In production, this would create a unique shareable token
  // For now, return a mock link
  return `${window.location.origin}/shared/${analysisId}`
}
