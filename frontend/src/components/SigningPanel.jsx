import { Copy, KeyRound, LoaderCircle, ShieldPlus } from 'lucide-react'
import { useMemo, useState } from 'react'
import {
  buildTransactionMessage,
  DEFAULT_TRANSACTION,
  normalizeAmount,
  normalizePartyName,
  transactionFieldsAreValid,
} from '../utils/transaction'

function SigningPanel({ onSign, signedTransaction, isLoading, backendOnline, onFeedback }) {
  const [sender, setSender] = useState(DEFAULT_TRANSACTION.sender)
  const [receiver, setReceiver] = useState(DEFAULT_TRANSACTION.receiver)
  const [amount, setAmount] = useState(DEFAULT_TRANSACTION.amount)
  const generatedMessage = useMemo(
    () => buildTransactionMessage(amount, receiver),
    [amount, receiver],
  )
  const valid = transactionFieldsAreValid({ sender, receiver, amount })

  async function handleSubmit(event) {
    event.preventDefault()
    if (!valid) {
      onFeedback({ type: 'error', message: 'Enter a sender, receiver, and whole-number amount greater than zero.' })
      return
    }
    await onSign({
      sender: normalizePartyName(sender),
      receiver: normalizePartyName(receiver),
      amount: normalizeAmount(amount),
      message: generatedMessage,
    })
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
          <input value={sender} onChange={(event) => setSender(event.target.value)} placeholder="Alice" maxLength="64" required />
        </label>
        <div className="transaction-field-row">
          <label>
            Receiver
            <input value={receiver} onChange={(event) => setReceiver(event.target.value)} placeholder="Bob" maxLength="64" required />
          </label>
          <label>
            Amount
            <input
              value={amount}
              onChange={(event) => setAmount(event.target.value)}
              inputMode="numeric"
              pattern="[0-9]+"
              placeholder="10000"
              aria-invalid={!valid && Boolean(amount)}
              maxLength="32"
              required
            />
          </label>
        </div>
        <div className={`transaction-preview ${generatedMessage ? '' : 'invalid'}`} aria-live="polite">
          <span>Generated Transaction</span>
          <code>{generatedMessage || 'Enter a valid receiver and amount'}</code>
        </div>
        <button className="primary-button" type="submit" disabled={isLoading || !backendOnline || !valid}>
          {isLoading ? <LoaderCircle size={17} className="spin" /> : <KeyRound size={17} />}
          {isLoading ? 'Generating Signature…' : 'Generate Quantum Signature'}
        </button>
      </form>

      {!backendOnline && <p className="inline-warning">Backend must be online before a signature can be generated.</p>}

      {signedTransaction && (
        <div className="signature-card">
          <div className="signature-status"><span className="status-dot online" /> Status: <strong>SIGNED</strong></div>
          <div className="signature-detail"><span>Sender</span><strong>{signedTransaction.sender}</strong></div>
          <div className="signature-detail"><span>Receiver</span><strong>{signedTransaction.receiver}</strong></div>
          <div className="signature-detail"><span>Amount</span><strong>{signedTransaction.amount}</strong></div>
          <div className="signature-detail"><span>Transaction</span><code>{signedTransaction.message}</code></div>
          <div className="signature-detail"><span>Signature Owner</span><strong>{signedTransaction.signature_owner}</strong></div>
          <div className="signature-detail">
            <span>Signature ID</span>
            <code>{signedTransaction.signature_id}</code>
            <button className="copy-button" type="button" onClick={copySignatureId} aria-label="Copy Signature ID">
              <Copy size={15} /> Copy
            </button>
          </div>
          <div className="signature-detail"><span>Message Hash</span><code>{signedTransaction.message_hash}</code></div>
        </div>
      )}
    </section>
  )
}

export default SigningPanel
