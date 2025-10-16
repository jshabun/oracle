import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import DraftMode from './pages/DraftMode'
import TeamManagement from './pages/TeamManagement'
import Players from './pages/Players'
import Recommendations from './pages/Recommendations'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="draft" element={<DraftMode />} />
        <Route path="team" element={<TeamManagement />} />
        <Route path="players" element={<Players />} />
        <Route path="recommendations" element={<Recommendations />} />
      </Route>
    </Routes>
  )
}

export default App
