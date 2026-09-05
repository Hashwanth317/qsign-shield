import { Activity, Menu, RefreshCw } from 'lucide-react'

function Header({ pageTitle, backendStatus, onRefresh, onMenu }) {
  const online = backendStatus === 'online'
  const connecting = backendStatus === 'connecting'

  return (
    <header className="topbar">
      <button className="mobile-menu-button" type="button" onClick={onMenu} aria-label="Open navigation">
        <Menu size={22} />
      </button>
      <div className="page-heading">
        <p className="eyebrow">Q-SIGN SHIELD PLATFORM</p>
        <h1>{pageTitle}</h1>
      </div>

      <div className="system-status" aria-live="polite">
        <span className={`status-dot ${online ? 'online' : backendStatus === 'offline' ? 'offline' : ''}`} />
        <Activity size={16} />
        <div>
          <small>Security Engine</small>
          <strong>{online ? 'Online' : connecting ? 'Connecting' : 'Offline'}</strong>
        </div>
        <button
          className="icon-button"
          type="button"
          onClick={onRefresh}
          aria-label="Refresh backend status"
          disabled={connecting}
        >
          <RefreshCw size={16} className={connecting ? 'spin' : ''} />
        </button>
      </div>
    </header>
  )
}

export default Header
