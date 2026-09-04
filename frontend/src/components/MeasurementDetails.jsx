import { displayPercent } from '../utils/quantum'

function CountList({ label, counts }) {
  return (
    <div className="count-group">
      <h4>{label}</h4>
      <dl>
        {['00', '01', '10', '11'].map((outcome) => (
          <div key={outcome}><dt>{outcome}</dt><dd>{counts?.[outcome] ?? 0}</dd></div>
        ))}
      </dl>
    </div>
  )
}

function MeasurementDetails({ result }) {
  if (!result) return null
  const { measurements } = result

  return (
    <details className="measurement-details">
      <summary>Measurement Details</summary>
      <div className="measurement-content">
        <dl className="measurement-summary">
          <div><dt>Shots per basis</dt><dd>{result.shots}</dd></div>
          <div><dt>Total measurements</dt><dd>{measurements.total_measurements}</dd></div>
          <div><dt>Matching</dt><dd>{measurements.matching_measurements}</dd></div>
          <div><dt>Mismatching</dt><dd>{measurements.mismatching_measurements}</dd></div>
          <div><dt>Bell correlation score</dt><dd>{measurements.bell_correlation_score.toFixed(4)}</dd></div>
          <div><dt>Measurement fidelity</dt><dd>{displayPercent(measurements.measurement_fidelity)}</dd></div>
        </dl>
        <div className="count-grid">
          <CountList label="Z Basis Counts" counts={measurements.z_basis_counts} />
          <CountList label="X Basis Counts" counts={measurements.x_basis_counts} />
        </div>
      </div>
    </details>
  )
}

export default MeasurementDetails

