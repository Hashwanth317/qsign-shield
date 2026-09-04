import { boundedPercent, displayPercent } from '../utils/quantum'

function BasisBar({ basis, value, tone }) {
  return (
    <div className="basis-row">
      <span>{basis} Basis</span>
      <div className="basis-track" aria-hidden="true">
        <span className={`basis-fill ${tone}`} style={{ width: `${boundedPercent(value)}%` }} />
      </div>
      <strong>{displayPercent(value)}</strong>
    </div>
  )
}

function BasisComparison({ measurements }) {
  if (!measurements) return null

  return (
    <article className="quantum-subpanel basis-panel">
      <div className="subpanel-heading">
        <p className="section-kicker">COMPLEMENTARY CHECKS</p>
        <h3>Basis Error Comparison</h3>
      </div>
      <div className="basis-bars">
        <BasisBar basis="Z" value={measurements.z_basis_error_rate} tone="z" />
        <BasisBar basis="X" value={measurements.x_basis_error_rate} tone="x" />
      </div>
      <p className="metric-caption">Higher bars represent more <code>01</code> and <code>10</code> mismatch outcomes observed by the backend.</p>
    </article>
  )
}

export default BasisComparison
