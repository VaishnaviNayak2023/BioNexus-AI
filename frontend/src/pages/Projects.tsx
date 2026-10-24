import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { Button } from "../components/ui/Button"
import { Plus, Search } from "lucide-react"
import { getProjects, createProject } from "../lib/api"

interface Project {
  id: number
  name: string
  description: string | null
  created_at: string
  updated_at: string
  sample_count: number
}

export function Projects() {
  const navigate = useNavigate()
  const [projects, setProjects] = useState<Project[]>([])
  const [showNewProject, setShowNewProject] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getProjects().then(setProjects).catch(console.error).finally(() => setLoading(false))
  }, [])

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Your projects</h1>
          <p className="text-gray-600 mt-1">Manage your eDNA analysis projects</p>
        </div>
        <div className="flex gap-3">
          <Button variant="secondary" onClick={() => navigate("/new-analysis")}>
            <Plus className="h-4 w-4 mr-2" />
            New analysis
          </Button>
          <Button onClick={() => setShowNewProject(true)}>
            <Plus className="h-4 w-4 mr-2" />
            New project
          </Button>
        </div>
      </div>

      {projects.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16 bg-white rounded-lg border border-gray-200">
          <div className="text-center">
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Start by uploading a sequence file
            </h3>
            <p className="text-gray-600 mb-4">
              Create a project to begin analyzing your eDNA samples
            </p>
            <Button onClick={() => setShowNewProject(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Create your first project
            </Button>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project) => (
            <div
              key={project.id}
              className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer"
            >
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                {project.name}
              </h3>
              <p className="text-sm text-gray-600 mb-4">
                {project.sample_count} {project.sample_count === 1 ? 'analysis' : 'analyses'}
              </p>
              <p className="text-xs text-gray-500">
                Edited {new Date(project.updated_at).toLocaleDateString()}
              </p>
            </div>
          ))}
        </div>
      )}

      {showNewProject && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-semibold mb-4">Create new project</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Project name
                </label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="My eDNA study"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description (optional)
                </label>
                <textarea
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  rows={3}
                  placeholder="Brief description of your project..."
                />
              </div>
              <div className="flex justify-end gap-3 pt-4">
                <Button variant="secondary" onClick={() => setShowNewProject(false)}>
                  Cancel
                </Button>
                <Button onClick={async () => {
                  const name = (document.querySelector('input[type="text"]') as HTMLInputElement)?.value || ""
                  if (!name) return
                  await createProject({ name })
                  setShowNewProject(false)
                  const updated = await getProjects()
                  setProjects(updated)
                }}>
                  Create project
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
