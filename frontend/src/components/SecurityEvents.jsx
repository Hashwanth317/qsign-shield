import { Clock3, ShieldAlert } from 'lucide-react'

function SecurityEvents({ events }) {
  return (
    <section className="panel events-panel">
      <div className="panel-heading">
        <div>
          <p className="section-kicker">CURRENT FRONTEND SESSION</p>
          <h2>Live Security Events</h2>
        </div>
        <Clock3 className="heading-icon" size={22} />
      </div>

      {events.length === 0 ? (
        <div className="empty-events"><ShieldAlert size={20} /> No security events recorded yet.</div>
      ) : (
        <div className="events-table-wrap">
          <table>
            <thead>
              <tr>
                <th>Time</th>
                <th>Category</th>
                <th>Reference</th>
                <th>Subject</th>
                <th>Detected</th>
                <th>Evidence</th>
                <th>Risk</th>
                <th>Decision</th>
              </tr>
            </thead>
            <tbody>
              {events.map((event) => {
                const quantum = event.category === 'QUANTUM'
                const detection = quantum ? event.detected : event.attackType
                return (
                  <tr key={event.id}>
                    <td>{event.time}</td>
                    <td><span className={`event-category ${quantum ? 'quantum' : 'transaction'}`}>{event.category}</span></td>
                    <td><code>{quantum ? event.scenario : event.transactionId}</code></td>
                    <td>{quantum ? 'Simulated channel' : event.sender}</td>
                    <td><span className={`event-type ${detection === 'NONE' ? 'none' : 'attack'}`}>{detection}</span></td>
                    <td><span className={quantum ? '' : event.verification === 'PASS' ? 'pass' : 'fail'}>{quantum ? `QBER ${event.qber}` : event.verification}</span></td>
                    <td>{quantum ? event.risk : '—'}</td>
                    <td>{event.decision}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}

export default SecurityEvents
