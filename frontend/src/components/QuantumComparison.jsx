import { ArrowRightLeft } from 'lucide-react'
import { boundedPercent, displayPercent, scenarioLabel } from '../utils/quantum'

const comparisonMetrics = [
  ['qber', 'QBER'],
  ['z_basis_error_rate', 'Z-Basis Error'],
  ['x_basis_error_rate', 'X-Basis Error'],
  ['correlation_rate', 'Correlation Rate'],
]

function ComparisonSummary({ title, result }) {
  return (
    <article className={`comparison-summary ${result.forensics.channel_status.toLowerCase()}`}>
      <span>{title}</span>
      <strong>{result.forensics.channel_status}</strong>
      <small>{result.forensics.probable_attack ?? 'No probable threat'}</small>
    </article>
  )
}

function QuantumComparison({ comparison }) {
  if (!comparison) return null
  const { baseline, selected } = comparison

  return (
    <section className="quantum-comparison" aria-label="Normal and selected scenario comparison">
      <div className="comparison-title">
        <div>
          <p className="section-kicker">CLEAN REFERENCE</p>
          <h3>Normal vs Selected Scenario</h3>
        </div>
        <ArrowRightLeft size={21} aria-hidden="true" />
      </div>

      <div className="comparison-summaries">
        <ComparisonSummary title="Normal Channel" result={baseline} />
        <span className="versus">VS</span>
        <ComparisonSummary title={scenarioLabel(selected.scenario)} result={selected} />
      </div>

      <div className="comparison-chart">
        {comparisonMetrics.map(([key, label]) => {
          const normalValue = baseline.measurements[key]
          const selectedValue = selected.measurements[key]
          return (
            <div className="comparison-metric" key={key}>
              <div className="comparison-metric-label">
                <span>{label}</span>
                <small>Normal {displayPercent(normalValue)} · Selected {displayPercent(selectedValue)}</small>
              </div>
              <div className="comparison-pair">
                <span className="comparison-bar normal" style={{ width: `${boundedPercent(normalValue)}%` }} />
              </div>
              <div className="comparison-pair">
                <span className="comparison-bar selected" style={{ width: `${boundedPercent(selectedValue)}%` }} />
              </div>
            </div>
          )
        })}
      </div>
      <div className="comparison-legend"><span className="normal">Normal channel</span><span className="selected">Selected scenario</span></div>
    </section>
  )
}

export default QuantumComparison

