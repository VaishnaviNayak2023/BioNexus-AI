import { useState } from "react"
import { Upload } from "lucide-react"
import { cn } from "../../lib/utils"

interface FileDropzoneProps {
  onFileSelect: (file: File) => void
  className?: string
}

export function FileDropzone({ onFileSelect, className }: FileDropzoneProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    
    const file = e.dataTransfer.files[0]
    validateAndSelectFile(file)
  }

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      validateAndSelectFile(file)
    }
  }

  const validateAndSelectFile = (file: File) => {
    setError(null)
    
    // Check file extension
    const validExtensions = ['.fasta', '.fa', '.fastq', '.gz']
    const hasValidExtension = validExtensions.some(ext => 
      file.name.toLowerCase().endsWith(ext)
    )
    
    if (!hasValidExtension) {
      setError("Invalid file type. Please upload a FASTA or FASTQ file.")
      return
    }
    
    // Check file size (500 MB max)
    const maxSize = 500 * 1024 * 1024
    if (file.size > maxSize) {
      setError("File too large. Maximum size is 500 MB.")
      return
    }
    
    onFileSelect(file)
  }

  return (
    <div className={cn("w-full", className)}>
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={cn(
          "border-2 border-dashed rounded-lg p-8 text-center transition-colors",
          isDragging ? "border-primary-500 bg-primary-50" : "border-gray-300 hover:border-gray-400"
        )}
      >
        <Upload className="h-12 w-12 mx-auto text-gray-400 mb-4" />
        <p className="text-gray-700 mb-2">
          Drag a FASTA or FASTQ file here, or{" "}
          <label className="text-primary-600 cursor-pointer hover:underline">
            Browse
            <input
              type="file"
              className="hidden"
              accept=".fasta,.fa,.fastq,.gz"
              onChange={handleFileInput}
            />
          </label>
        </p>
        <p className="text-sm text-gray-500">
          Accepted: .fasta .fa .fastq .gz Max size: 500 MB
        </p>
      </div>
      
      {error && (
        <div className="mt-2 text-sm text-red-600">
          {error}
        </div>
      )}
    </div>
  )
}
