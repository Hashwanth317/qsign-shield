import { ArrowRight, CheckCircle2, FileText, Fingerprint, KeyRound, Repeat2, ScanSearch, UserCheck } from 'lucide-react'

const flowSteps = [
  ['Sender', UserCheck],
  ['Message', FileText],
  ['SHA-256\nFingerprint', Fingerprint],
  ['Quantum\nSignature', KeyRound],
  ['Verification\nEngine', ScanSearch],
  ['Identity\nCheck', UserCheck],
  ['Replay\nGuard', Repeat2],
  ['Secure /\nBlocked', CheckCircle2],
]

function SecurityFlow() {
  return (
    <section className="flow-section">
      <div className="section-header compact">
        <div>
          <p className="section-kicker">VERIFICATION PIPELINE</p>
          <h2>Q-Sign Security Flow</h2>
        </div>
      </div>
      <div className="flow-track">
        {flowSteps.map(([label, Icon], index) => (
          <div className="flow-item" key={label}>
            <div className="flow-node"><Icon size={18} /></div>
            <span>{label.split('\n').map((line) => <span key={line}>{line}</span>)}</span>
            {index < flowSteps.length - 1 && <ArrowRight className="flow-arrow" size={17} aria-hidden="true" />}
          </div>
        ))}
      </div>
    </section>
  )
}

export default SecurityFlow
