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
                <th>Transaction ID</th>
                <th>Sender</th>
                <th>Attack Type</th>
                <th>Verification</th>
                <th>Decision</th>
              </tr>
            </thead>
            <tbody>
              {events.map((event) => (
                <tr key={event.id}>
                  <td>{event.time}</td>
                  <td><code>{event.transactionId}</code></td>
                  <td>{event.sender}</td>
                  <td><span className={`event-type ${event.attackType === 'NONE' ? 'none' : 'attack'}`}>{event.attackType}</span></td>
                  <td><span className={event.verification === 'PASS' ? 'pass' : 'fail'}>{event.verification}</span></td>
                  <td>{event.decision}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}

export default SecurityEvents
