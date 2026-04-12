import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Trades from './pages/Trades'
import Analytics from './pages/Analytics'
import AIInsights from './pages/AIInsights'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="trades" element={<Trades />} />
        <Route path="analytics" element={<Analytics />} />
        <Route path="ai" element={<AIInsights />} />
      </Route>
    </Routes>
  )
}

export default App