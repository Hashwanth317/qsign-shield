import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { checkHealth, securityCheck, signMessage, verifyTransaction } from '../services/api'
import { buildTransactionMessage, forgedTransactionAmount } from '../utils/transaction'
import SecurityContext from './security-context'

const ATTACK_BY_DECISION = {
  'FORGERY ATTACK DETECTED': 'FORGERY',
  'SIGNATURE TAMPERING DETECTED': 'SIGNATURE_TAMPERING',
  'REPLAY ATTACK DETECTED': 'REPLAY',
  'IMPERSONATION ATTACK DETECTED': 'IMPERSONATION',
}

const ATTACK_REASONS = {
  FORGERY: 'Transaction data was modified after signing.',
  SIGNATURE_TAMPERING: 'Signature data does not match the original signature.',
  REPLAY: 'This valid transaction has already been processed.',
  IMPERSONATION: 'Claimed sender does not match the signature owner.',
}

function normalizeResult(data, context = {}) {
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
    evaluated_at: data.evaluated_at ?? new Date().toISOString(),
  }
}

function tamperedBits(bits) {
  return bits
    .split('')
    .map((bit, index) => (index < 2 ? (bit === '0' ? '1' : '0') : bit))
    .join('')
}

function wait(milliseconds) {
  return new Promise((resolve) => window.setTimeout(resolve, milliseconds))
}

export function SecurityProvider({ children }) {
  const [backendStatus, setBackendStatus] = useState('connecting')
  const [signedTransaction, setSignedTransaction] = useState(null)
  const [latestResult, setLatestResult] = useState(null)
  const [events, setEvents] = useState([])
  const [feedback, setFeedback] = useState(null)
  const [signing, setSigning] = useState(false)
  const [verifying, setVerifying] = useState(false)
  const [activeAttack, setActiveAttack] = useState(null)
  const healthRun = useRef(0)

  const backendOnline = backendStatus === 'online'

  const connectBackend = useCallback(async () => {
    const runId = healthRun.current + 1
    healthRun.current = runId
    setBackendStatus('connecting')
    const deadline = Date.now() + 60_000

    while (healthRun.current === runId) {
      try {
        const response = await checkHealth()
        if (healthRun.current !== runId) return
        if (response.status === 'healthy') {
          setBackendStatus('online')
          return
        }
      } catch {
        // Render may be waking. Retry until the connection window expires.
      }

      if (Date.now() >= deadline) {
        if (healthRun.current === runId) setBackendStatus('offline')
        return
      }
      await wait(5_000)
    }
  }, [])

  useEffect(() => {
    const start = window.setTimeout(connectBackend, 0)
    return () => {
      window.clearTimeout(start)
      healthRun.current += 1
    }
  }, [connectBackend])

  useEffect(() => {
    if (!feedback) return undefined
    const timeout = window.setTimeout(() => setFeedback(null), 5_000)
    return () => window.clearTimeout(timeout)
  }, [feedback])

  const showFeedback = useCallback((nextFeedback) => setFeedback(nextFeedback), [])

  const stats = useMemo(() => {
    const transactionEvents = events.filter((event) => event.category === 'TRANSACTION')
    return {
      transactions: transactionEvents.length,
      legitimate: transactionEvents.filter((event) => event.status === 'ACCEPTED').length,
      blocked: transactionEvents.filter((event) => event.status === 'BLOCKED').length,
      quantumAlerts: events.filter((event) => event.category === 'QUANTUM' && event.attackDetected).length,
    }
  }, [events])

  const recordResult = useCallback((result, transaction) => {
    const now = new Date()
    const attackType = result.attack_type ?? 'LEGITIMATE'
    const event = {
      id: globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`,
      timestamp: now.toISOString(),
      time: now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      category: 'TRANSACTION',
      transactionId: result.transaction_id,
      sender: result.sender_identity ?? transaction?.sender,
      receiver: transaction?.receiver ?? '—',
      amount: transaction?.amount ?? '—',
      message: transaction?.message,
      attackType,
      verification: result.overall_verification,
      decision: result.security_decision,
      status: result.status,
      risk: result.status === 'BLOCKED' ? 'HIGH' : 'LOW',
      reason: ATTACK_REASONS[attackType] ?? 'All transaction security checks passed.',
      attackDetected: result.status === 'BLOCKED',
    }
    setEvents((current) => [event, ...current])
  }, [])

  const recordQuantumEvent = useCallback((result) => {
    const now = new Date()
    const event = {
      id: globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`,
      timestamp: now.toISOString(),
      time: now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      category: 'QUANTUM',
      transactionId: 'Quantum Channel',
      sender: 'Simulated channel',
      receiver: '—',
      amount: '—',
      scenario: result.scenario.toUpperCase(),
      attackType: result.forensics.probable_attack ?? 'NORMAL_CHANNEL',
      detected: result.forensics.probable_attack ?? 'NONE',
      qber: `${result.forensics.qber.toFixed(2)}%`,
      risk: result.forensics.risk_level,
      decision: result.forensics.channel_status,
      status: result.forensics.channel_status,
      reason: result.forensics.classification_reason,
      attackDetected: result.forensics.attack_detected,
    }
    setEvents((current) => [event, ...current])
  }, [])

  async function handleSign({ sender, receiver, amount, message }) {
    setSigning(true)
    try {
      const signature = await signMessage({ sender, message })
      const transaction = { ...signature, receiver, amount, transaction_id: signature.signature_id }
      setSignedTransaction(transaction)
      setLatestResult(null)
      showFeedback({ type: 'success', message: `Quantum signature ${signature.signature_id} generated successfully.` })
      return transaction
    } catch (error) {
      showFeedback({ type: 'error', message: error.message })
      return null
    } finally {
      setSigning(false)
    }
  }

  async function handleVerify(payload) {
    setVerifying(true)
    try {
      const response = await verifyTransaction({ message: payload.message, claimed_sender: payload.claimed_sender, signature_id: payload.signature_id })
      const result = normalizeResult(response, { ...payload, signature_owner: signedTransaction?.signature_owner })
      setLatestResult(result)
      recordResult(result, signedTransaction ?? payload)
      showFeedback({
        type: result.overall_verification === 'PASS' ? 'success' : 'error',
        message: result.overall_verification === 'PASS' ? 'Transaction verified successfully.' : result.security_decision,
      })
      return result
    } catch (error) {
      showFeedback({ type: 'error', message: error.message })
      return null
    } finally {
      setVerifying(false)
    }
  }

  async function submitSecurityCheck(payload, attackContext = null) {
    const response = await securityCheck(payload)
    const result = {
      ...normalizeResult(response, { ...payload, signature_owner: signedTransaction?.signature_owner }),
      attack_context: attackContext,
    }
    setLatestResult(result)
    recordResult(result, signedTransaction)
    return result
  }

  async function handleAttack(attack) {
    if (!signedTransaction) return null
    const basePayload = { message: signedTransaction.message, claimed_sender: signedTransaction.sender, signature_id: signedTransaction.signature_id }
    setActiveAttack(attack)
    try {
      let result
      if (attack === 'forgery') {
        const forgedAmount = forgedTransactionAmount(signedTransaction.amount)
        const forgedMessage = buildTransactionMessage(forgedAmount, signedTransaction.receiver)
        result = await submitSecurityCheck(
          { ...basePayload, message: forgedMessage },
          { type: 'FORGERY', originalAmount: signedTransaction.amount, forgedAmount, originalMessage: basePayload.message, forgedMessage },
        )
      } else if (attack === 'tampering') {
        result = await submitSecurityCheck(
          { ...basePayload, signature_bits: tamperedBits(signedTransaction.signature_fingerprint) },
          { type: 'SIGNATURE_TAMPERING' },
        )
      } else if (attack === 'impersonation') {
        result = await submitSecurityCheck(
          { ...basePayload, claimed_sender: 'Attacker' },
          { type: 'IMPERSONATION', claimedSender: 'Attacker' },
        )
      } else {
        const first = await submitSecurityCheck(basePayload)
        const second = await submitSecurityCheck(basePayload, { type: 'REPLAY' })
        result = { ...second, attack_context: { type: 'REPLAY', firstSubmission: first.status, repeatedSubmission: second.status } }
        setLatestResult(result)
      }

      showFeedback({ type: result.status === 'BLOCKED' ? 'threat' : 'success', message: result.status === 'BLOCKED' ? result.security_decision : 'Transaction accepted.' })
      return result
    } catch (error) {
      showFeedback({ type: 'error', message: error.message })
      return null
    } finally {
      setActiveAttack(null)
    }
  }

  const value = {
    activeAttack, backendOnline, backendStatus, connectBackend, events, feedback,
    handleAttack, handleSign, handleVerify, latestResult, recordQuantumEvent,
    showFeedback, signedTransaction, signing, stats, verifying,
  }

  return <SecurityContext.Provider value={value}>{children}</SecurityContext.Provider>
}
