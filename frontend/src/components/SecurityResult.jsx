import { CheckCircle2, ShieldAlert, ShieldCheck } from 'lucide-react'

function Flag({ label, value, positive }) {
  return (
    <div className="result-metric">
      <span>{label}</span>
      <strong className={positive ? 'pass' : 'fail'}>{value}</strong>
    </div>
  )
}

function SecurityResult({ result }) {
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
  const attackLabel = result.attack_type?.replaceAll('_', ' ') || 'NONE'

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

      {!secure && <div className="attack-callout">Attack Type: <strong>{attackLabel}</strong></div>}
      {!secure && (
        <div className="threat-detail-grid">
          <div><span>Risk Level</span><strong className="fail">{result.risk_level}</strong></div>
          <div><span>Transaction ID</span><code>{result.transaction_id}</code></div>
          <div><span>Sender</span><strong>{result.sender_identity}</strong></div>
          <div><span>Receiver</span><strong>{result.receiver}</strong></div>
          <div><span>Amount</span><strong>{result.amount}</strong></div>
          <div><span>Verification Result</span><strong className="fail">{result.overall_verification}</strong></div>
          <div><span>System Action</span><strong className="fail">{result.system_action}</strong></div>
          <div><span>Timestamp</span><strong>{result.timestamp}</strong></div>
          <div className="threat-detail-wide"><span>Reason</span><strong>{result.reason}</strong></div>
          <div className="threat-detail-wide"><span>Recommended Action</span><strong>{result.recommended_action}</strong></div>
        </div>
      )}
      {result.attack_context?.type === 'FORGERY' && (
        <div className="forgery-evidence">
          <div><span>Original Amount</span><strong>{result.attack_context.originalAmount}</strong></div>
          <div><span>Forged Amount</span><strong>{result.attack_context.forgedAmount}</strong></div>
          <div><span>Original Transaction</span><code>{result.attack_context.originalMessage}</code></div>
          <div><span>Forged Transaction</span><code>{result.attack_context.forgedMessage}</code></div>
        </div>
      )}
      <div className="result-grid">
        <Flag label="Cryptographic Signature" value={result.cryptographic_signature} positive={result.cryptographic_signature === 'PASS'} />
        <Flag label="Identity Match" value={result.identity_match ? 'PASS' : 'FAIL'} positive={result.identity_match} />
        <Flag label="Overall Verification" value={result.overall_verification} positive={secure} />
        <Flag label="Matching Bits" value={`${result.matching_bits} / ${result.total_bits}`} positive={result.matching_bits === result.total_bits} />
        <Flag label="Verification Percentage" value={`${result.verification_percentage}%`} positive={result.verification_percentage === 100} />
      </div>
      <div className="decision-text">{result.security_decision}</div>
    </section>
  )
}

export default SecurityResult
