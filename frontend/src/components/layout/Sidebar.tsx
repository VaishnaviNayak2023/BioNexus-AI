import { Link, useLocation } from "react-router-dom"
import { cn } from "../../lib/utils"
import { 
  FolderKanban, 
  Database, 
  FlaskConical, 
  HelpCircle,
  ChevronRight 
} from "lucide-react"

interface NavItem {
  label: string
  path: string
  icon: React.ElementType
}

const navItems: NavItem[] = [
  { label: "Projects", path: "/", icon: FolderKanban },
  { label: "Reference data", path: "/reference", icon: Database },
  { label: "Research mode", path: "/research", icon: FlaskConical },
  { label: "Help", path: "/help", icon: HelpCircle },
]

export function Sidebar() {
  const location = useLocation()

  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col h-screen">
      <div className="p-4 border-b border-gray-200">
        <h1 className="text-lg font-semibold text-gray-900">eDNA Taxonomy Workbench</h1>
      </div>
      
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname === item.path
          
          return (
            <Link
              key={item.path}
              to={item.path}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary-50 text-primary-700"
                  : "text-gray-700 hover:bg-gray-100"
              )}
            >
              <Icon className="h-5 w-5" />
              {item.label}
              {isActive && <ChevronRight className="ml-auto h-4 w-4" />}
            </Link>
          )
        })}
      </nav>
      
      <div className="p-4 border-t border-gray-200">
        <div className="text-xs text-gray-500">
          Project switcher
        </div>
      </div>
    </aside>
  )
}
