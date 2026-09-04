import { CircleGauge, ShieldAlert, ShieldCheck, TriangleAlert } from 'lucide-react'

function QuantumStatusCard({ result }) {
  if (!result) {
    return (
      <article className="quantum-status-card waiting">
        <CircleGauge size={28} aria-hidden="true" />
        <div>
          <p className="section-kicker">QUANTUM CHANNEL</p>
          <h3>Awaiting analysis</h3>
          <p>Choose a simulated channel condition and run the backend forensics engine.</p>
        </div>
      </article>
    )
  }

  const { forensics } = result
  const secure = forensics.channel_status === 'SECURE'
  const degraded = forensics.channel_status === 'DEGRADED'
  const Icon = secure ? ShieldCheck : degraded ? TriangleAlert : ShieldAlert
  const tone = secure ? 'secure' : degraded ? 'degraded' : 'compromised'

  return (
    <article className={`quantum-status-card ${tone}`}>
      <div className="quantum-status-lead">
        <Icon size={30} aria-hidden="true" />
        <div>
          <p className="section-kicker">QUANTUM CHANNEL</p>
          <h3>{forensics.channel_status}</h3>
        </div>
      </div>
      <dl className="quantum-status-facts">
        <div>
          <dt>Attack Detected</dt>
          <dd>{forensics.attack_detected ? 'YES' : 'NO'}</dd>
        </div>
        <div>
          <dt>Risk Level</dt>
          <dd>{forensics.risk_level}</dd>
        </div>
        <div>
          <dt>Probable Threat</dt>
          <dd>{forensics.probable_attack ?? 'NONE'}</dd>
        </div>
      </dl>
    </article>
  )
}

export default QuantumStatusCard

