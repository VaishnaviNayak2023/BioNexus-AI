import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { Button } from "../components/ui/Button"
import { Check, Clock, X } from "lucide-react"

interface Step {
  id: string
  label: string
  status: "pending" | "running" | "completed" | "failed"
}

export function Progress() {
  const navigate = useNavigate()
  const [steps, setSteps] = useState<Step[]>([
    { id: "reading", label: "Reading file", status: "running" },
    { id: "clustering", label: "Clustering", status: "pending" },
    { id: "embedding", label: "Embedding sequences", status: "pending" },
    { id: "cooccurrence", label: "Applying co-occurrence", status: "pending" },
    { id: "results", label: "Building results", status: "pending" },
  ])
  const [elapsedTime, setElapsedTime] = useState(0)
  const [estimatedTime, setEstimatedTime] = useState(120)

  useEffect(() => {
    // Simulate progress
    const interval = setInterval(() => {
      setElapsedTime((prev) => prev + 1)
      
      setSteps((prevSteps) => {
        const newSteps = [...prevSteps]
        const currentStepIndex = newSteps.findIndex(s => s.status === "running")
        
        if (currentStepIndex !== -1) {
          // Simulate step completion after some time
          if (elapsedTime > 0 && elapsedTime % 3 === 0) {
            newSteps[currentStepIndex].status = "completed"
            if (currentStepIndex < newSteps.length - 1) {
              newSteps[currentStepIndex + 1].status = "running"
            }
          }
        }
        
        return newSteps
      })
    }, 1000)

    return () => clearInterval(interval)
  }, [elapsedTime])

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const allCompleted = steps.every(s => s.status === "completed")

  useEffect(() => {
    if (allCompleted) {
      setTimeout(() => {
        navigate("/results/1")
      }, 1500)
    }
  }, [allCompleted, navigate])

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="bg-white rounded-lg border border-gray-200 p-8">
        <h1 className="text-2xl font-semibold text-gray-900 mb-2">Processing your analysis</h1>
        <p className="text-gray-600 mb-8">
          Elapsed: {formatTime(elapsedTime)} • Estimated: {formatTime(estimatedTime)}
        </p>

        <div className="space-y-4">
          {steps.map((step, index) => {
            const Icon = step.status === "completed" ? Check :
                        step.status === "running" ? Clock :
                        step.status === "failed" ? X : Clock
            
            return (
              <div
                key={step.id}
                className={`flex items-center gap-4 p-4 rounded-lg border ${
                  step.status === "running" ? "border-primary-500 bg-primary-50" :
                  step.status === "completed" ? "border-green-500 bg-green-50" :
                  step.status === "failed" ? "border-red-500 bg-red-50" :
                  "border-gray-200"
                }`}
              >
                <div className={`flex-shrink-0 ${
                  step.status === "completed" ? "text-green-600" :
                  step.status === "running" ? "text-primary-600" :
                  step.status === "failed" ? "text-red-600" :
                  "text-gray-400"
                }`}>
                  <Icon className="h-6 w-6" />
                </div>
                <div className="flex-1">
                  <p className={`font-medium ${
                    step.status === "running" ? "text-primary-900" :
                    step.status === "completed" ? "text-green-900" :
                    step.status === "failed" ? "text-red-900" :
                    "text-gray-700"
                  }`}>
                    {step.label}
                  </p>
                </div>
                {step.status === "running" && (
                  <div className="flex-shrink-0">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
                  </div>
                )}
              </div>
            )
          })}
        </div>

        <div className="flex justify-between mt-8 pt-4 border-t border-gray-200">
          <Button variant="secondary" onClick={() => navigate(-1)}>
            Cancel
          </Button>
          <Button variant="ghost">
            Keep working, we'll notify you
          </Button>
        </div>
      </div>
    </div>
  )
}
