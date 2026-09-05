import QuantumForensics from '../components/QuantumForensics'
import useSecurity from '../context/useSecurity'

function QuantumForensicsPage() {
  const { backendOnline, recordQuantumEvent } = useSecurity()
  return (
    <>
      <section className="page-intro">
        <div><p className="section-kicker">MEASUREMENT-BASED ANALYSIS</p><h1>Quantum Forensics Lab</h1></div>
        <p>Quantum Channel Threat Analysis</p>
      </section>
      <QuantumForensics backendOnline={backendOnline} onRecordEvent={recordQuantumEvent} />
    </>
  )
}

export default QuantumForensicsPage
