import { useState } from 'react'
import { ShieldCheck, X } from 'lucide-react'
import Header from './Header'
import useSecurity from '../context/useSecurity'
import { NAVIGATION, PAGE_TITLES } from '../navigation'

function AppLayout({ currentPath, navigate, children }) {
  const [menuOpen, setMenuOpen] = useState(false)
  const { backendOnline, backendStatus, connectBackend, feedback } = useSecurity()

  function goTo(path) {
    setMenuOpen(false)
    navigate(path)
  }

  return (
    <div className="platform-shell">
      <aside className={`sidebar ${menuOpen ? 'open' : ''}`}>
        <div className="sidebar-brand">
          <span className="sidebar-brand-mark"><ShieldCheck size={25} /></span>
          <div><strong>Q-SIGN</strong><span>SHIELD</span></div>
          <button className="sidebar-close" type="button" onClick={() => setMenuOpen(false)} aria-label="Close navigation"><X size={20} /></button>
        </div>
        <nav aria-label="Primary navigation">
          {NAVIGATION.map(([path, label, Icon]) => (
            <a href={path} className={currentPath === path ? 'active' : ''} key={path} onClick={(event) => { event.preventDefault(); goTo(path) }}>
              <Icon size={19} /><span>{label}</span>
            </a>
          ))}
        </nav>
        <div className="sidebar-foot">
          <span className={`status-dot ${backendOnline ? 'online' : backendStatus === 'offline' ? 'offline' : ''}`} />
          <div><strong>Security Engine</strong><span>{backendStatus}</span></div>
        </div>
      </aside>

      {menuOpen && <button className="sidebar-scrim" type="button" aria-label="Close navigation" onClick={() => setMenuOpen(false)} />}

      <div className="platform-main">
        <Header pageTitle={PAGE_TITLES[currentPath] ?? 'Dashboard'} backendStatus={backendStatus} onRefresh={connectBackend} onMenu={() => setMenuOpen(true)} />
        {feedback && <div className={`feedback ${feedback.type}`} role="status">{feedback.message}</div>}
        {backendStatus === 'connecting' && <div className="connection-banner"><span className="connection-pulse" />Waking Q-Sign Security Engine...</div>}
        {backendStatus === 'offline' && (
          <div className="offline-banner">
            <span>Backend Offline. Security actions are temporarily unavailable.</span>
            <button type="button" onClick={connectBackend}>Retry Connection</button>
          </div>
        )}
        <main className="page-content">{children}</main>
        <footer>Q-Sign Shield · Qiskit-based quantum security simulation · SIH26141</footer>
      </div>
    </div>
  )
}

export default AppLayout
