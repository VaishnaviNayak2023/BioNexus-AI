import { cn } from "../../lib/utils"
import { CheckCircle, AlertCircle, HelpCircle } from "lucide-react"

interface ConfidenceBadgeProps {
  confidence: number
  className?: string
}

export function ConfidenceBadge({ confidence, className }: ConfidenceBadgeProps) {
  let level: "high" | "medium" | "low"
  let label: string
  let Icon: typeof CheckCircle | typeof AlertCircle | typeof HelpCircle
  let bgColor: string
  let textColor: string

  if (confidence >= 0.7) {
    level = "high"
    label = "High"
    Icon = CheckCircle
    bgColor = "bg-green-100"
    textColor = "text-green-800"
  } else if (confidence >= 0.5) {
    level = "medium"
    label = "Medium"
    Icon = AlertCircle
    bgColor = "bg-amber-100"
    textColor = "text-amber-800"
  } else {
    level = "low"
    label = "Low"
    Icon = HelpCircle
    bgColor = "bg-red-100"
    textColor = "text-red-800"
  }

  return (
    <div className={cn("inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium", bgColor, textColor, className)}>
      <Icon className="h-3.5 w-3.5" />
      <span>{label}</span>
      <span className="font-semibold">{Math.round(confidence * 100)}%</span>
    </div>
  )
}
