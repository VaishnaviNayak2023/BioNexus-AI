import { BrowserRouter as Router, Routes, Route } from "react-router-dom"
import { Sidebar } from "./components/layout/Sidebar"
import { Projects } from "./pages/Projects"
import { NewAnalysis } from "./pages/NewAnalysis"
import { Progress } from "./pages/Progress"
import { Results } from "./pages/Results"
import { ReferenceData } from "./pages/ReferenceData"
import { ResearchMode } from "./pages/ResearchMode"
import { Help } from "./pages/Help"

function App() {
  return (
    <Router>
      <div className="flex h-screen bg-gray-50">
        <Sidebar />
        <main className="flex-1 overflow-auto">
          <Routes>
            <Route path="/" element={<Projects />} />
            <Route path="/new-analysis" element={<NewAnalysis />} />
            <Route path="/progress" element={<Progress />} />
            <Route path="/results/:analysisId" element={<Results />} />
            <Route path="/reference" element={<ReferenceData />} />
            <Route path="/research" element={<ResearchMode />} />
            <Route path="/help" element={<Help />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
