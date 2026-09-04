import { useEffect, useMemo, useState } from 'react'
import AttackLab from './components/AttackLab'
import Header from './components/Header'
import InfoPanel from './components/InfoPanel'
import QuantumForensics from './components/QuantumForensics'
import QuantumSecurityFlow from './components/QuantumSecurityFlow'
import SecurityEvents from './components/SecurityEvents'
import SecurityFlow from './components/SecurityFlow'
import SecurityResult from './components/SecurityResult'
import SigningPanel from './components/SigningPanel'
import StatsCards from './components/StatsCards'
import VerificationPanel from './components/VerificationPanel'
import { checkHealth, securityCheck, signMessage, verifyTransaction } from './services/api'

const ATTACK_BY_DECISION = {
  'FORGERY ATTACK DETECTED': 'FORGERY',
  'SIGNATURE TAMPERING DETECTED': 'SIGNATURE_TAMPERING',
  'REPLAY ATTACK DETECTED': 'REPLAY',
  'IMPERSONATION ATTACK DETECTED': 'IMPERSONATION',
}

function normalizeResult(data, context) {
  const overallVerification = data.overall_verification ?? data.verification
  const attackType = data.attack_type ?? ATTACK_BY_DECISION[data.security_decision] ?? null

  return {
    ...data,
    attack_type: attackType,
    overall_verification: overallVerification,
    status: data.status ?? (overallVerification === 'PASS' ? 'ACCEPTED' : 'BLOCKED'),
    sender_identity: data.sender_identity ?? context.claimed_sender,
    signature_owner: data.signature_owner ?? context.signature_owner,
    transaction_id: data.transaction_id ?? context.signature_id,
  }
}

function forgedMessage(message) {
  const altered = message.replace('TRANSFER 10000 TO BOB', 'TRANSFER 90000 TO BOB')
  return altered === message ? `${message} [MODIFIED]` : altered
}

function tamperedBits(bits) {
  return bits
    .split('')
    .map((bit, index) => (index < 2 ? (bit === '0' ? '1' : '0') : bit))
    .join('')
}

function App() {
  const [backendStatus, setBackendStatus] = useState('checking')
  const [signedTransaction, setSignedTransaction] = useState(null)
  const [latestResult, setLatestResult] = useState(null)
  const [events, setEvents] = useState([])
  const [feedback, setFeedback] = useState(null)
  const [signing, setSigning] = useState(false)
  const [verifying, setVerifying] = useState(false)
  const [activeAttack, setActiveAttack] = useState(null)

  const backendOnline = backendStatus === 'online'

  const stats = useMemo(() => {
    const transactionEvents = events.filter((event) => event.category === 'TRANSACTION')
    const quantumEvents = events.filter((event) => event.category === 'QUANTUM')
    const legitimate = transactionEvents.filter((event) => event.decision === 'LEGITIMATE').length
    const blocked = transactionEvents.filter((event) => event.status === 'BLOCKED').length
    const processed = legitimate + blocked

    return {
      transactions: transactionEvents.length,
      legitimate,
      blocked,
      quantumAlerts: quantumEvents.filter((event) => event.attackDetected).length,
      securityRate: transactionEvents.length ? `${Math.round((processed / transactionEvents.length) * 100)}%` : '—',
    }
  }, [events])

  useEffect(() => {
    refreshHealth()
  }, [])

  useEffect(() => {
    if (!feedback) return undefined
    const timeout = window.setTimeout(() => setFeedback(null), 5000)
    return () => window.clearTimeout(timeout)
  }, [feedback])

  async function refreshHealth() {
    setBackendStatus('checking')
    try {
      const response = await checkHealth()
      setBackendStatus(response.status === 'healthy' ? 'online' : 'offline')
    } catch {
      setBackendStatus('offline')
    }
  }

  function showFeedback(nextFeedback) {
    setFeedback(nextFeedback)
  }

  function recordResult(result) {
    const event = {
      id: globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      category: 'TRANSACTION',
      transactionId: result.transaction_id,
      sender: result.sender_identity,
      attackType: result.attack_type ?? 'NONE',
      verification: result.overall_verification,
      decision: result.security_decision,
      status: result.status,
    }
    setEvents((current) => [event, ...current])
  }

  function recordQuantumEvent(result) {
    const event = {
      id: globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      category: 'QUANTUM',
      scenario: result.scenario.toUpperCase(),
      detected: result.forensics.probable_attack ?? 'NONE',
      qber: `${result.forensics.qber.toFixed(2)}%`,
      risk: result.forensics.risk_level,
      decision: result.forensics.channel_status,
      attackDetected: result.forensics.attack_detected,
    }
    setEvents((current) => [event, ...current])
  }

  function contextFor(payload) {
    return {
      ...payload,
      signature_owner: signedTransaction?.signature_owner,
    }
  }

  async function handleSign({ sender, message }) {
    setSigning(true)
    try {
      const signature = await signMessage({ sender, message })
      setSignedTransaction(signature)
      setLatestResult(null)
      showFeedback({ type: 'success', message: `Quantum signature ${signature.signature_id} generated successfully.` })
    } catch (error) {
      showFeedback({ type: 'error', message: error.message })
    } finally {
      setSigning(false)
    }
  }

  async function handleVerify(payload) {
    setVerifying(true)
    try {
      const response = await verifyTransaction(payload)
      const result = normalizeResult(response, contextFor(payload))
      setLatestResult(result)
      recordResult(result)
      showFeedback({
        type: result.overall_verification === 'PASS' ? 'success' : 'error',
        message: result.overall_verification === 'PASS' ? 'Transaction verified successfully.' : result.security_decision,
      })
    } catch (error) {
      showFeedback({ type: 'error', message: error.message })
    } finally {
      setVerifying(false)
    }
  }

  async function submitSecurityCheck(payload) {
    const response = await securityCheck(payload)
    const result = normalizeResult(response, contextFor(payload))
    setLatestResult(result)
    recordResult(result)
    return result
  }

  async function handleAttack(attack) {
    if (!signedTransaction) return

    const basePayload = {
      message: signedTransaction.message,
      claimed_sender: signedTransaction.sender,
      signature_id: signedTransaction.signature_id,
    }

    setActiveAttack(attack)
    try {
      let result
      if (attack === 'forgery') {
        result = await submitSecurityCheck({ ...basePayload, message: forgedMessage(basePayload.message) })
      } else if (attack === 'tampering') {
        result = await submitSecurityCheck({ ...basePayload, signature_bits: tamperedBits(signedTransaction.signature_fingerprint) })
      } else if (attack === 'impersonation') {
        result = await submitSecurityCheck({ ...basePayload, claimed_sender: 'Attacker' })
      } else {
        const first = await submitSecurityCheck(basePayload)
        const second = await submitSecurityCheck(basePayload)
        result = second
        if (first.status !== 'ACCEPTED') {
          showFeedback({ type: 'error', message: 'This signature was already used. Generate a fresh signature for a new replay demonstration.' })
        }
      }

      if (result.status === 'BLOCKED') {
        showFeedback({ type: 'threat', message: result.security_decision })
      } else {
        showFeedback({ type: 'success', message: 'First transaction accepted. Replaying it will now be blocked.' })
      }
    } catch (error) {
      showFeedback({ type: 'error', message: error.message })
    } finally {
      setActiveAttack(null)
    }
  }

  return (
    <div className="app-shell">
      <Header backendStatus={backendStatus} onRefresh={refreshHealth} />

      {feedback && <div className={`feedback ${feedback.type}`} role="status">{feedback.message}</div>}
      {!backendOnline && backendStatus === 'offline' && (
        <div className="offline-banner">Unable to contact Q-Sign Security Engine. Start the FastAPI backend at <code>http://127.0.0.1:8000</code>.</div>
      )}

      <main>
        <section className="hero-strip">
          <div>
            <p className="section-kicker">LIVE SECURITY WORKSPACE</p>
            <h2>Validate quantum-signature transactions and demonstrate defensive controls.</h2>
          </div>
          <p>All results below are returned by the existing Q-Sign Shield backend.</p>
        </section>

        <StatsCards stats={stats} />

        <section className="security-layer-heading transaction-layer">
          <span>01</span>
          <div>
            <p className="section-kicker">SECURITY LAYER 01 · TRANSACTION</p>
            <h2>Quantum Signature Transaction Security</h2>
            <p>Sign and verify messages, then test forgery, tampering, replay, and identity controls.</p>
          </div>
        </section>

        <section className="work-grid">
          <SigningPanel
            onSign={handleSign}
            signedTransaction={signedTransaction}
            isLoading={signing}
            backendOnline={backendOnline}
            onFeedback={showFeedback}
          />
          <VerificationPanel
            key={signedTransaction?.signature_id ?? 'new-transaction'}
            activeSignature={signedTransaction}
            onVerify={handleVerify}
            isLoading={verifying}
            backendOnline={backendOnline}
          />
        </section>

        <SecurityResult result={latestResult} />
        <AttackLab activeSignature={signedTransaction} activeAction={activeAttack} onRunAttack={handleAttack} backendOnline={backendOnline} />
        <QuantumForensics backendOnline={backendOnline} onRecordEvent={recordQuantumEvent} />
        <SecurityEvents events={events} />
        <SecurityFlow />
        <QuantumSecurityFlow />
        <InfoPanel />
      </main>

      <footer>Q-Sign Shield V0.9 · Educational Qiskit-based quantum-security simulation for SIH26141</footer>
    </div>
  )
}

export default App
