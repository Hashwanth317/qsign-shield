import { BadgeCheck, BarChart3, RadioTower, ShieldAlert } from 'lucide-react'

const cardDefinitions = [
  { key: 'transactions', label: 'Transactions Checked', icon: BarChart3, tone: 'blue' },
  { key: 'legitimate', label: 'Legitimate Transactions', icon: BadgeCheck, tone: 'green' },
  { key: 'blocked', label: 'Threats Blocked', icon: ShieldAlert, tone: 'red' },
  { key: 'quantumAlerts', label: 'Quantum Alerts', icon: RadioTower, tone: 'violet' },
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
