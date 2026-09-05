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
        <h3>X-Basis vs Z-Basis Analysis</h3>
      </div>
      <div className="basis-bars">
        <BasisBar basis="Z" value={measurements.z_basis_error_rate} tone="z" />
        <BasisBar basis="X" value={measurements.x_basis_error_rate} tone="x" />
      </div>
      <p className="metric-caption">Higher bars represent more <code>01</code> and <code>10</code> mismatch outcomes observed by the backend.</p>
      <ul className="basis-reference">
        <li><strong>Bit Flip</strong><span>Mainly visible through Z-basis disturbance.</span></li>
        <li><strong>Phase Flip</strong><span>Mainly visible through X-basis disturbance.</span></li>
        <li><strong>Bit + Phase Flip</strong><span>Can affect both measurement bases.</span></li>
      </ul>
    </article>
  )
}

export default BasisComparison
