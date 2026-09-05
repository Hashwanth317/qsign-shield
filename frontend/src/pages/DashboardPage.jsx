import { Activity, Atom, FlaskConical, ReceiptText } from 'lucide-react'
import SecurityEvents from '../components/SecurityEvents'
import StatsCards from '../components/StatsCards'
import useSecurity from '../context/useSecurity'

const actions = [
  ['/transactions', 'Create Transaction', 'Sign and verify a secure transfer.', ReceiptText, 'cyan'],
  ['/attack-lab', 'Open Attack Lab', 'Run controlled transaction attacks.', FlaskConical, 'red'],
  ['/quantum-forensics', 'Open Quantum Forensics', 'Analyze simulated channel disturbances.', Atom, 'violet'],
  ['/security-events', 'View Security Events', 'Inspect evidence from this session.', Activity, 'green'],
]

function DashboardPage({ navigate }) {
  const { backendStatus, events, stats } = useSecurity()
  return (
    <>
      <section className="dashboard-hero">
        <div>
          <p className="section-kicker">QUANTUM-SIGNATURE DEFENSE PLATFORM</p>
          <h1>Quantum-Secure Transaction Protection</h1>
          <p>Sign transactions, validate integrity, and investigate simulated quantum-channel threats from one security workspace.</p>
        </div>
        <div className={`hero-status ${backendStatus}`}>
          <span className="status-dot" />
          <div><small>Backend Status</small><strong>{backendStatus}</strong></div>
        </div>
      </section>
      <StatsCards stats={stats} />
      <section className="dashboard-section">
        <div className="page-section-heading"><div><p className="section-kicker">SECURITY WORKSPACES</p><h2>Choose an operation</h2></div></div>
        <div className="action-grid">
          {actions.map(([path, title, description, Icon, tone]) => (
            <button className={`action-card ${tone}`} type="button" key={path} onClick={() => navigate(path)}>
              <span className="action-icon"><Icon size={23} /></span>
              <span><strong>{title}</strong><small>{description}</small></span>
              <span className="action-arrow">→</span>
            </button>
          ))}
        </div>
      </section>
      <SecurityEvents events={events.slice(0, 5)} compact onViewAll={() => navigate('/security-events')} />
    </>
  )
}

export default DashboardPage
