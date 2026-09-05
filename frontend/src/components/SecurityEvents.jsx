import { Clock3, ExternalLink, ShieldAlert } from 'lucide-react'

function SecurityEvents({ events, compact = false, onViewAll }) {
  return (
    <section className="panel events-panel">
      <div className="panel-heading">
        <div>
          <p className="section-kicker">CURRENT FRONTEND SESSION</p>
          <h2>{compact ? 'Recent Security Events' : 'Security Event Log'}</h2>
        </div>
        {onViewAll
          ? <button className="panel-link" type="button" onClick={onViewAll}>View all <ExternalLink size={14} /></button>
          : <Clock3 className="heading-icon" size={22} />}
      </div>

      {events.length === 0 ? (
        <div className="empty-events"><ShieldAlert size={20} /> No security events recorded yet.</div>
      ) : (
        <div className="events-table-wrap">
          <table>
            <thead>
              <tr>
                <th>Time</th>
                <th>Event Type</th>
                <th>Transaction ID</th>
                <th>Sender</th>
                <th>Receiver</th>
                <th>Risk</th>
                <th>Status</th>
                {!compact && <th>Details</th>}
              </tr>
            </thead>
            <tbody>
              {events.map((event) => {
                const eventType = event.attackType?.replaceAll('_', ' ') ?? event.category
                const safe = event.status === 'ACCEPTED' || event.status === 'SECURE'
                return (
                  <tr key={event.id}>
                    <td>{event.time}</td>
                    <td><span className={`event-type ${safe ? 'none' : 'attack'}`}>{eventType}</span></td>
                    <td><code>{event.transactionId}</code></td>
                    <td>{event.sender}</td>
                    <td>{event.receiver}</td>
                    <td><span className={`risk-badge ${event.risk?.toLowerCase()}`}>{event.risk}</span></td>
                    <td><span className={safe ? 'pass' : 'fail'}>{event.status}</span></td>
                    {!compact && (
                      <td>
                        <details className="event-details">
                          <summary>View</summary>
                          <div>
                            <span><strong>Decision</strong>{event.decision}</span>
                            <span><strong>Reason</strong>{event.reason}</span>
                            {event.qber && <span><strong>QBER</strong>{event.qber}</span>}
                            <span><strong>Timestamp</strong>{new Date(event.timestamp).toLocaleString()}</span>
                          </div>
                        </details>
                      </td>
                    )}
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
