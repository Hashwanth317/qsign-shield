import { boundedPercent, displayPercent } from '../utils/quantum'

const anomalyFields = [
  ['x_anomaly', 'X Anomaly', 'x'],
  ['y_anomaly', 'Y Anomaly', 'y'],
  ['z_anomaly', 'Z Anomaly', 'z'],
]

function PauliSyndrome({ forensics }) {
  if (!forensics) return null

  return (
    <article className="quantum-subpanel syndrome-panel">
      <div className="subpanel-heading">
        <p className="section-kicker">STATISTICAL SIGNATURE</p>
        <h3>Pauli Security Syndrome</h3>
      </div>

      <div className="syndrome-bars">
        {anomalyFields.map(([key, label, tone]) => {
          const score = Number(forensics.pauli_anomalies?.[key] ?? 0) * 100
          return (
            <div className="syndrome-row" key={key}>
              <span>{label}</span>
              <div className="syndrome-track" aria-hidden="true">
                <span className={`syndrome-fill ${tone}`} style={{ width: `${boundedPercent(score)}%` }} />
              </div>
              <strong>{displayPercent(score)}</strong>
            </div>
          )
        })}
      </div>

      <dl className="syndrome-summary">
        <div><dt>Dominant Syndrome</dt><dd>{forensics.dominant_pauli_syndrome}</dd></div>
        <div><dt>Probable Threat</dt><dd>{forensics.probable_attack ?? 'NONE'}</dd></div>
      </dl>
    </article>
  )
}

export default PauliSyndrome

