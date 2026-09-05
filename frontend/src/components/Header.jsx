import { Activity, RefreshCw, ShieldCheck } from 'lucide-react'

function Header({ backendStatus, onRefresh }) {
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
    </header>
  )
}

export default Header
