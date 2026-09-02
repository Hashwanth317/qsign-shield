import { CheckCircle2, LoaderCircle, SearchCheck } from 'lucide-react'
import { useState } from 'react'

function VerificationPanel({ activeSignature, onVerify, isLoading, backendOnline }) {
  const [message, setMessage] = useState(
    () => activeSignature?.message ?? 'TRANSFER 10000 TO BOB',
  )
  const [claimedSender, setClaimedSender] = useState(
    () => activeSignature?.sender ?? 'Alice',
  )
  const [signatureId, setSignatureId] = useState(
    () => activeSignature?.signature_id ?? '',
  )

  async function handleSubmit(event) {
    event.preventDefault()
    await onVerify({ message, claimed_sender: claimedSender, signature_id: signatureId })
  }

  return (
    <section className="panel verification-panel">
      <div className="panel-heading">
        <div>
          <p className="section-kicker">RECEIVER VALIDATION</p>
          <h2>Verify Transaction</h2>
        </div>
        <SearchCheck className="heading-icon" size={22} />
      </div>

      <form onSubmit={handleSubmit} className="form-stack">
        <label>
          Message
          <textarea value={message} onChange={(event) => setMessage(event.target.value)} rows="3" required />
        </label>
        <label>
          Claimed Sender
          <input value={claimedSender} onChange={(event) => setClaimedSender(event.target.value)} placeholder="Alice" required />
        </label>
        <label>
          Signature ID
          <input value={signatureId} onChange={(event) => setSignatureId(event.target.value)} placeholder="QS-XXXXXXXX" required />
        </label>
        <button className="secondary-button" type="submit" disabled={isLoading || !backendOnline}>
          {isLoading ? <LoaderCircle size={17} className="spin" /> : <CheckCircle2 size={17} />}
          {isLoading ? 'Verifying…' : 'Verify Transaction'}
        </button>
      </form>
    </section>
  )
}

export default VerificationPanel
