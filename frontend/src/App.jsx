import { useEffect, useState } from 'react'
import AppLayout from './components/AppLayout'
import { SecurityProvider } from './context/SecurityContext'
import { PAGE_TITLES } from './navigation'
import AttackLabPage from './pages/AttackLabPage'
import DashboardPage from './pages/DashboardPage'
import QuantumForensicsPage from './pages/QuantumForensicsPage'
import SecurityEventsPage from './pages/SecurityEventsPage'
import TransactionsPage from './pages/TransactionsPage'
import './platform.css'

const DEFAULT_PATH = '/dashboard'

function normalizePath(pathname) {
  const cleanPath = pathname.length > 1 ? pathname.replace(/\/$/, '') : pathname
  return PAGE_TITLES[cleanPath] ? cleanPath : DEFAULT_PATH
}

function App() {
  const [currentPath, setCurrentPath] = useState(() => normalizePath(window.location.pathname))

  useEffect(() => {
    const normalized = normalizePath(window.location.pathname)
    if (window.location.pathname !== normalized) window.history.replaceState({}, '', normalized)
    const onPopState = () => setCurrentPath(normalizePath(window.location.pathname))
    window.addEventListener('popstate', onPopState)
    return () => window.removeEventListener('popstate', onPopState)
  }, [])

  function navigate(path) {
    const normalized = normalizePath(path)
    if (normalized !== currentPath) window.history.pushState({}, '', normalized)
    setCurrentPath(normalized)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const pages = {
    '/dashboard': <DashboardPage navigate={navigate} />,
    '/transactions': <TransactionsPage />,
    '/attack-lab': <AttackLabPage navigate={navigate} />,
    '/quantum-forensics': <QuantumForensicsPage />,
    '/security-events': <SecurityEventsPage />,
  }

  return (
    <SecurityProvider>
      <AppLayout currentPath={currentPath} navigate={navigate}>
        {pages[currentPath]}
      </AppLayout>
    </SecurityProvider>
  )
}

export default App
