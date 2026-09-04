import { Activity, Gauge, RadioTower, ScanLine, Waves } from 'lucide-react'
import { boundedPercent, displayPercent } from '../utils/quantum'

const metrics = [
  ['qber', 'QBER', Gauge],
  ['z_basis_error_rate', 'Z-Basis Error', ScanLine],
  ['x_basis_error_rate', 'X-Basis Error', RadioTower],
  ['correlation_rate', 'Correlation Rate', Activity],
  ['measurement_fidelity', 'Measurement Fidelity', Waves],
]

function QuantumMetrics({ measurements, status }) {
  if (!measurements) return null

  return (
    <div className="quantum-metrics-area">
      <div className="quantum-metric-grid" aria-label="Quantum channel metrics">
        {metrics.map(([key, label, Icon]) => (
          <article className="quantum-metric-card" key={key}>
            <div className="quantum-metric-icon"><Icon size={17} /></div>
            <span>{label}</span>
            <strong>{displayPercent(measurements[key])}</strong>
          </article>
        ))}
      </div>

      <article className="qber-panel">
        <div className="metric-panel-heading">
          <div>
            <p className="section-kicker">OBSERVED ERROR</p>
            <h3>Quantum Bit Error Rate</h3>
          </div>
          <strong>{displayPercent(measurements.qber)}</strong>
        </div>
        <div
          className="metric-track"
          role="progressbar"
          aria-label="Observed quantum bit error rate"
          aria-valuemin="0"
          aria-valuemax="100"
          aria-valuenow={boundedPercent(measurements.qber)}
        >
          <span
            className={`metric-fill ${status?.toLowerCase() ?? ''}`}
            style={{ width: `${boundedPercent(measurements.qber)}%` }}
          />
        </div>
        <div className="track-labels"><span>0%</span><span>Measured QBER</span><span>100%</span></div>
        <p className="metric-caption">The scale shows the returned measurement only; no frontend threshold is applied.</p>
      </article>
    </div>
  )
}

export default QuantumMetrics

