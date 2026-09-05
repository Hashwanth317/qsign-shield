import { useEffect, useMemo, useState } from 'react'
import {
  GitCompareArrows,
  LoaderCircle,
  Microscope,
  RadioTower,
  TriangleAlert,
} from 'lucide-react'
import { analyzeQuantumChannel, getQuantumStatus } from '../services/api'
import {
  MAX_QUANTUM_SHOTS,
  MIN_QUANTUM_SHOTS,
  QUANTUM_SCENARIOS,
  validShotCount,
} from '../utils/quantum'
import BasisComparison from './BasisComparison'
import MeasurementDetails from './MeasurementDetails'
import PauliSyndrome from './PauliSyndrome'
import QuantumComparison from './QuantumComparison'
import QuantumMetrics from './QuantumMetrics'
import QuantumStatusCard from './QuantumStatusCard'

function QuantumForensics({ backendOnline, onRecordEvent }) {
  const [engineStatus, setEngineStatus] = useState('checking')
  const [supportedScenarios, setSupportedScenarios] = useState([])
  const [scenario, setScenario] = useState('normal')
  const [shots, setShots] = useState('1024')
  const [result, setResult] = useState(null)
  const [comparison, setComparison] = useState(null)
  const [loadingAction, setLoadingAction] = useState(null)
  const [error, setError] = useState(null)

  const shotsValid = validShotCount(shots)
  const engineReady = backendOnline && engineStatus === 'ready'
  const scenarioOptions = useMemo(() => {
    if (!supportedScenarios.length) return QUANTUM_SCENARIOS
    return QUANTUM_SCENARIOS.filter(({ value }) => supportedScenarios.includes(value))
  }, [supportedScenarios])

  useEffect(() => {
    let active = true

    async function loadStatus() {
      if (!backendOnline) {
        setEngineStatus('offline')
        setResult(null)
        setComparison(null)
        return
      }

      setEngineStatus('checking')
      try {
        const response = await getQuantumStatus()
        if (!active) return
        setSupportedScenarios(response.supported_scenarios)
        setEngineStatus(response.status === 'ready' ? 'ready' : 'offline')
      } catch {
        if (!active) return
        setEngineStatus('offline')
        setResult(null)
        setComparison(null)
      }
    }

    loadStatus()
    return () => { active = false }
  }, [backendOnline])

  async function runAnalysis() {
    if (!shotsValid || !engineReady) return
    setLoadingAction('analyze')
    setError(null)
    try {
      const response = await analyzeQuantumChannel(scenario, Number(shots))
      setResult(response)
      setComparison(null)
      onRecordEvent(response)
    } catch (requestError) {
      setError(requestError.message)
      setEngineStatus('offline')
      setResult(null)
      setComparison(null)
    } finally {
      setLoadingAction(null)
    }
  }

  async function compareWithNormal() {
    if (!shotsValid || !engineReady || scenario === 'normal') return
    setLoadingAction('compare')
    setError(null)
    try {
      const [baseline, selected] = await Promise.all([
        analyzeQuantumChannel('normal', Number(shots)),
        analyzeQuantumChannel(scenario, Number(shots)),
      ])
      setResult(selected)
      setComparison({ baseline, selected })
      onRecordEvent(selected)
    } catch (requestError) {
      setError(requestError.message)
      setEngineStatus('offline')
      setResult(null)
      setComparison(null)
    } finally {
      setLoadingAction(null)
    }
  }

  const busy = Boolean(loadingAction)

  return (
    <section className="quantum-forensics-section">
      <div className="quantum-section-header">
        <div className="quantum-title-mark"><RadioTower size={24} /></div>
        <div>
          <p className="section-kicker">SIMULATED QUANTUM CHANNEL</p>
          <h2>Measurement-Based Channel Analysis</h2>
          <p>Analyze simulated disturbances using backend multi-basis measurement statistics.</p>
        </div>
        <span className={`engine-badge ${engineStatus}`}>
          <span className="status-dot" />
          {engineStatus === 'ready' ? 'Forensics Ready' : engineStatus === 'checking' ? 'Checking Engine' : 'Engine Offline'}
        </span>
      </div>

      {!engineReady && engineStatus === 'offline' ? (
        <div className="quantum-offline" role="alert">
          <TriangleAlert size={24} />
          <div>
            <strong>Quantum Forensics Engine Offline</strong>
            <span>Start the FastAPI backend to request live channel measurements.</span>
          </div>
        </div>
      ) : (
        <>
          <div className="quantum-controls">
            <label>
              Simulated channel scenario
              <select value={scenario} onChange={(event) => setScenario(event.target.value)} disabled={busy || !engineReady}>
                {scenarioOptions.map(({ value, label }) => <option value={value} key={value}>{label}</option>)}
              </select>
            </label>
            <label>
              Shots per basis
              <input
                type="number"
                min={MIN_QUANTUM_SHOTS}
                max={MAX_QUANTUM_SHOTS}
                step="128"
                value={shots}
                onChange={(event) => setShots(event.target.value)}
                aria-invalid={!shotsValid}
                disabled={busy || !engineReady}
              />
            </label>
            <button className="primary-button quantum-run-button" type="button" onClick={runAnalysis} disabled={!engineReady || !shotsValid || busy}>
              {loadingAction === 'analyze' ? <LoaderCircle size={17} className="spin" /> : <Microscope size={17} />}
              {loadingAction === 'analyze' ? 'Analyzing Quantum Channel…' : 'Run Quantum Forensics'}
            </button>
            <button className="secondary-button quantum-compare-button" type="button" onClick={compareWithNormal} disabled={!engineReady || !shotsValid || scenario === 'normal' || busy}>
              {loadingAction === 'compare' ? <LoaderCircle size={17} className="spin" /> : <GitCompareArrows size={17} />}
              {loadingAction === 'compare' ? 'Building Comparison…' : 'Compare With Normal'}
            </button>
          </div>

          {!shotsValid && (
            <p className="quantum-validation" role="alert">Shots must be a whole number from {MIN_QUANTUM_SHOTS} to {MAX_QUANTUM_SHOTS}.</p>
          )}
          {error && <p className="quantum-api-error" role="alert">{error}</p>}

          <QuantumStatusCard result={result} />
          <QuantumMetrics measurements={result?.measurements} status={result?.forensics.channel_status} />

          {result && (
            <div className="quantum-analysis-grid">
              <BasisComparison measurements={result.measurements} />
              <PauliSyndrome forensics={result.forensics} />
            </div>
          )}

          {result && (
            <article className="detection-explanation">
              <p className="section-kicker">WHY WAS THIS DETECTED?</p>
              <p>{result.forensics.classification_reason}</p>
              <dl>
                <div><dt>Probable Threat</dt><dd>{result.forensics.probable_attack ?? 'NONE'}</dd></div>
                <div><dt>Likely Disturbance</dt><dd>{result.forensics.dominant_pauli_syndrome}</dd></div>
              </dl>
              <span>Probable classification supplied by the backend quantum forensics engine; this does not claim absolute certainty.</span>
            </article>
          )}

          <QuantumComparison comparison={comparison} />
          <MeasurementDetails result={result} />
        </>
      )}

      <p className="quantum-education-note">Educational Qiskit-based quantum-security simulation. Measurements represent Aer simulator runs, not a physical quantum network.</p>
    </section>
  )
}

export default QuantumForensics
