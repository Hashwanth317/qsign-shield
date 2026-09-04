import {
  Activity,
  ArrowRight,
  Atom,
  Binary,
  GitCompareArrows,
  Radar,
  ShieldCheck,
  Waves,
} from 'lucide-react'

const flowSteps = [
  ['Bell Pair', Atom],
  ['Quantum\nChannel', Waves],
  ['Possible\nDisturbance', Radar],
  ['Z + X Basis\nMeasurement', GitCompareArrows],
  ['QBER +\nCorrelation', Activity],
  ['Pauli\nSyndrome', Binary],
  ['Forensics\nDecision', ShieldCheck],
]

function QuantumSecurityFlow() {
  return (
    <section className="flow-section quantum-flow-section">
      <div className="section-header compact">
        <div>
          <p className="section-kicker">QUANTUM FORENSICS PIPELINE</p>
          <h2>Quantum Security Flow</h2>
        </div>
      </div>
      <div className="flow-track quantum-flow-track">
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

export default QuantumSecurityFlow

