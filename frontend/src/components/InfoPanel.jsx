import { Atom, ShieldCheck } from 'lucide-react'

function InfoPanel() {
  const steps = [
    'Transaction message is converted into a SHA-256 fingerprint.',
    'A quantum-signature simulation protects the selected fingerprint bits.',
    'The receiver verifies signature integrity and bit alignment.',
    'Sender identity and replay history are checked before acceptance.',
    'Any mismatch is classified and blocked by the security engine.',
  ]

  return (
    <aside className="info-panel">
      <div className="info-title"><Atom size={22} /><h2>How Q-Sign Shield Works</h2></div>
      <ol>
        {steps.map((step, index) => <li key={step}><span>{String(index + 1).padStart(2, '0')}</span>{step}</li>)}
      </ol>
      <div className="education-note"><ShieldCheck size={18} /> Educational quantum-security simulation. Not production quantum cryptography.</div>
    </aside>
  )
}

export default InfoPanel
