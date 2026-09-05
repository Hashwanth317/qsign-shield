import { Activity, LogOut, RefreshCw, ShieldCheck, UserRound } from 'lucide-react'

function roleLabel(role) {
  return role === 'security_operator' ? 'Security Operator' : 'Transaction User'
}

function Header({ backendStatus, onRefresh, currentUser, onLogout }) {
  const online = backendStatus === 'online'
  const checking = backendStatus === 'checking'

  return (
    <header className="topbar">
      <div className="brand">
        <div className="brand-mark" aria-hidden="true">
          <ShieldCheck size={27} />
        </div>
        <div>
          <p className="eyebrow">SIH26141 · QUANTUM SECURITY</p>
          <h1>Q-Sign Shield</h1>
          <p className="subtitle">Quantum Signature Security &amp; Attack Detection</p>
        </div>
      </div>

      <div className="topbar-actions">
        <div className="system-status" aria-live="polite">
          <span className={`status-dot ${online ? 'online' : 'offline'}`} />
          <Activity size={16} />
          <span>{online ? 'System Online' : checking ? 'Checking Backend' : 'Backend Offline'}</span>
          <button
            className="icon-button"
            type="button"
            onClick={onRefresh}
            aria-label="Refresh backend status"
            disabled={checking}
          >
            <RefreshCw size={16} className={checking ? 'spin' : ''} />
          </button>
        </div>
        <div className="user-menu">
          <UserRound size={18} aria-hidden="true" />
          <div>
            <strong>{currentUser.username}</strong>
            <span>{roleLabel(currentUser.role)}</span>
          </div>
          <button className="logout-button" type="button" onClick={onLogout}>
            <LogOut size={15} /> Logout
          </button>
        </div>
      </div>
    </header>
  )
}

export default Header
