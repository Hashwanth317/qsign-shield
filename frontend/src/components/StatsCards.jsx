import { BadgeCheck, BarChart3, RadioTower, ShieldAlert, Target } from 'lucide-react'

const cardDefinitions = [
  { key: 'transactions', label: 'Transactions Checked', icon: BarChart3, tone: 'blue' },
  { key: 'legitimate', label: 'Secure Transactions', icon: BadgeCheck, tone: 'green' },
  { key: 'blocked', label: 'Classical Attacks Blocked', icon: ShieldAlert, tone: 'red' },
  { key: 'quantumAlerts', label: 'Quantum Channel Alerts', icon: RadioTower, tone: 'cyan' },
  { key: 'securityRate', label: 'Security Rate', icon: Target, tone: 'violet' },
]

function StatsCards({ stats }) {
  return (
    <section className="stats-grid" aria-label="Session security statistics">
      {cardDefinitions.map(({ key, label, icon: Icon, tone }) => (
        <article className="stat-card" key={key}>
          <div className={`stat-icon ${tone}`}><Icon size={20} /></div>
          <div>
            <p>{label}</p>
            <strong>{stats[key]}</strong>
          </div>
        </article>
      ))}
    </section>
  )
}

export default StatsCards
