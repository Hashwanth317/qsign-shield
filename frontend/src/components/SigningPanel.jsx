import { Copy, KeyRound, LoaderCircle, ShieldPlus } from 'lucide-react'
import { useState } from 'react'

function SigningPanel({ onSign, signedTransaction, isLoading, backendOnline, onFeedback }) {
  const [sender, setSender] = useState('Alice')
  const [message, setMessage] = useState('TRANSFER 10000 TO BOB')

  async function handleSubmit(event) {
    event.preventDefault()
    await onSign({ sender, message })
  }

  async function copySignatureId() {
    if (!signedTransaction) return

    try {
      await navigator.clipboard.writeText(signedTransaction.signature_id)
      onFeedback({ type: 'success', message: 'Signature ID copied to clipboard.' })
    } catch {
      onFeedback({ type: 'error', message: 'Unable to copy the Signature ID.' })
    }
  }

  return (
    <section className="panel signing-panel">
      <div className="panel-heading">
        <div>
          <p className="section-kicker">TRANSACTION ORIGIN</p>
          <h2>Create Secure Transaction</h2>
        </div>
        <ShieldPlus className="heading-icon" size={22} />
      </div>

      <form onSubmit={handleSubmit} className="form-stack">
        <label>
          Sender
          <input value={sender} onChange={(event) => setSender(event.target.value)} placeholder="Alice" required />
        </label>
        <label>
          Message
          <textarea value={message} onChange={(event) => setMessage(event.target.value)} rows="3" required />
        </label>
        <button className="primary-button" type="submit" disabled={isLoading || !backendOnline}>
          {isLoading ? <LoaderCircle size={17} className="spin" /> : <KeyRound size={17} />}
          {isLoading ? 'Generating Signature…' : 'Generate Quantum Signature'}
        </button>
      </form>

      {!backendOnline && <p className="inline-warning">Backend must be online before a signature can be generated.</p>}

      {signedTransaction && (
        <div className="signature-card">
          <div className="signature-status"><span className="status-dot online" /> Status: <strong>SIGNED</strong></div>
          <div className="signature-detail">
            <span>Signature ID</span>
            <code>{signedTransaction.signature_id}</code>
            <button className="copy-button" type="button" onClick={copySignatureId} aria-label="Copy Signature ID">
              <Copy size={15} /> Copy
            </button>
          </div>
          <div className="signature-detail"><span>Owner</span><strong>{signedTransaction.signature_owner}</strong></div>
          <div className="signature-detail"><span>Message Hash</span><code>{signedTransaction.message_hash}</code></div>
        </div>
      )}
    </section>
  )
}

export default SigningPanel
