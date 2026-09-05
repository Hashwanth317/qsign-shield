import { CheckCircle2, ShieldAlert, ShieldCheck } from 'lucide-react'

const REASONS = {
  FORGERY: 'Transaction data was modified after signing.',
  SIGNATURE_TAMPERING: 'Signature data does not match the original signature.',
  REPLAY: 'This valid transaction has already been processed.',
  IMPERSONATION: 'Claimed sender does not match the signature owner.',
}

function Flag({ label, value, positive }) {
  return (
    <div className="result-metric">
      <span>{label}</span>
      <strong className={positive ? 'pass' : 'fail'}>{value}</strong>
    </div>
  )
}

function SecurityResult({ result, signedTransaction }) {
  if (!result) {
    return (
      <section className="security-result empty-result">
        <ShieldCheck size={30} />
        <div>
          <p className="section-kicker">SECURITY DECISION</p>
          <h2>Awaiting a transaction</h2>
          <p>Generate a signature or verify an existing transaction to view the security outcome.</p>
        </div>
      </section>
    )
  }

  const secure = result.overall_verification === 'PASS'
  const attackType = result.attack_type ?? 'LEGITIMATE'
  const attackLabel = attackType.replaceAll('_', ' ')
  const messageIntegrity = attackType === 'FORGERY' ? 'FAIL' : 'PASS'
  const signatureIntegrity = result.cryptographic_signature
  const replayCheck = attackType === 'REPLAY' ? 'FAIL' : 'PASS'
  const reason = REASONS[attackType] ?? 'All integrity, identity, and signature checks passed.'
  const timestamp = result.evaluated_at
    ? new Date(result.evaluated_at).toLocaleString()
    : new Date().toLocaleString()

  return (
    <section className={`security-result ${secure ? 'secure' : 'threat'}`}>
      <div className="result-topline">
        {secure ? <CheckCircle2 size={26} /> : <ShieldAlert size={26} />}
        <div>
          <p className="section-kicker">SECURITY DECISION</p>
          <h2>{secure ? 'Secure Transaction' : 'Threat Detected'}</h2>
        </div>
        <span className={`decision-badge ${secure ? 'safe' : 'danger'}`}>{secure ? 'ACCEPTED' : 'BLOCKED'}</span>
      </div>

      {!secure && <div className="attack-callout">Threat Type: <strong>{attackLabel}</strong></div>}
      {result.attack_context?.type === 'FORGERY' && (
        <div className="forgery-evidence">
          <div><span>Original Amount</span><strong>{result.attack_context.originalAmount}</strong></div>
          <div><span>Forged Amount</span><strong>{result.attack_context.forgedAmount}</strong></div>
          <div><span>Original Transaction</span><code>{result.attack_context.originalMessage}</code></div>
          <div><span>Forged Transaction</span><code>{result.attack_context.forgedMessage}</code></div>
        </div>
      )}
      {result.attack_context?.type === 'REPLAY' && (
        <div className="replay-evidence">
          <div><span>First Submission</span><strong>{result.attack_context.firstSubmission}</strong></div>
          <div><span>Repeated Submission</span><strong className="fail">{result.attack_context.repeatedSubmission}</strong></div>
        </div>
      )}
      <div className="result-grid">
        <Flag label="Message Integrity" value={messageIntegrity} positive={messageIntegrity === 'PASS'} />
        <Flag label="Signature Integrity" value={signatureIntegrity} positive={signatureIntegrity === 'PASS'} />
        <Flag label="Identity Match" value={result.identity_match ? 'PASS' : 'FAIL'} positive={result.identity_match} />
        <Flag label="Replay Check" value={replayCheck} positive={replayCheck === 'PASS'} />
        <Flag label="Overall Verification" value={result.overall_verification} positive={secure} />
        <Flag label="Matching Bits" value={`${result.matching_bits} / ${result.total_bits}`} positive={result.matching_bits === result.total_bits} />
        <Flag label="Verification Percentage" value={`${result.verification_percentage}%`} positive={result.verification_percentage === 100} />
      </div>
      {attackType === 'IMPERSONATION' && (
        <div className="identity-evidence">
          <div><span>Cryptographic Signature</span><strong className={signatureIntegrity === 'PASS' ? 'pass' : 'fail'}>{signatureIntegrity}</strong></div>
          <div><span>Claimed Sender</span><strong>{result.sender_identity}</strong></div>
          <div><span>Signature Owner</span><strong>{result.signature_owner}</strong></div>
        </div>
      )}
      <div className="decision-text"><span>Security Decision</span><strong>{result.security_decision}</strong></div>

      {!secure && (
        <div className="threat-detail-card">
          <div><span>Risk Level</span><strong className="risk-high">HIGH</strong></div>
          <div><span>Reason</span><strong>{reason}</strong></div>
          <div><span>Transaction ID</span><code>{result.transaction_id}</code></div>
          <div><span>Sender</span><strong>{result.sender_identity}</strong></div>
          <div><span>Receiver</span><strong>{signedTransaction?.receiver ?? '—'}</strong></div>
          <div><span>Amount</span><strong>{signedTransaction?.amount ?? '—'}</strong></div>
          <div><span>Verification Result</span><strong className="fail">{result.overall_verification}</strong></div>
          <div><span>System Action</span><strong className="fail">BLOCKED</strong></div>
          <div><span>Recommended Action</span><strong>Do not process this transaction.</strong></div>
          <div><span>Timestamp</span><strong>{timestamp}</strong></div>
        </div>
      )}
    </section>
  )
}

export default SecurityResult
