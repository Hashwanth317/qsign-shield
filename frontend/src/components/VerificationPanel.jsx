import { CheckCircle2, LoaderCircle, SearchCheck } from 'lucide-react'
import { useMemo, useState } from 'react'
import {
  buildTransactionMessage,
  DEFAULT_TRANSACTION,
  normalizeAmount,
  normalizePartyName,
  transactionFieldsAreValid,
} from '../utils/transaction'

function VerificationPanel({ activeSignature, onVerify, isLoading, backendOnline }) {
  const [claimedSender, setClaimedSender] = useState(
    () => activeSignature?.sender ?? DEFAULT_TRANSACTION.sender,
  )
  const [receiver, setReceiver] = useState(
    () => activeSignature?.receiver ?? DEFAULT_TRANSACTION.receiver,
  )
  const [amount, setAmount] = useState(
    () => activeSignature?.amount ?? DEFAULT_TRANSACTION.amount,
  )
  const [signatureId, setSignatureId] = useState(
    () => activeSignature?.signature_id ?? '',
  )
  const generatedMessage = useMemo(
    () => buildTransactionMessage(amount, receiver),
    [amount, receiver],
  )
  const valid = transactionFieldsAreValid({
    sender: claimedSender,
    receiver,
    amount,
  }) && Boolean(signatureId.trim())

  async function handleSubmit(event) {
    event.preventDefault()
    if (!valid) return
    await onVerify({
      message: generatedMessage,
      claimed_sender: normalizePartyName(claimedSender),
      signature_id: signatureId.trim(),
      receiver: normalizePartyName(receiver),
      amount: normalizeAmount(amount),
    })
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
          Claimed Sender
          <input value={claimedSender} onChange={(event) => setClaimedSender(event.target.value)} placeholder="Hashwanth" maxLength="64" required />
        </label>
        <div className="transaction-field-row">
          <label>
            Receiver
            <input value={receiver} onChange={(event) => setReceiver(event.target.value)} placeholder="Kavin" maxLength="64" required />
          </label>
          <label>
            Amount
            <input value={amount} onChange={(event) => setAmount(event.target.value)} inputMode="numeric" pattern="[0-9]+" placeholder="10000" maxLength="32" required />
          </label>
        </div>
        <label>
          Signature ID
          <input value={signatureId} onChange={(event) => setSignatureId(event.target.value)} placeholder="QS-XXXXXXXX" required />
        </label>
        <div className={`transaction-preview ${generatedMessage ? '' : 'invalid'}`} aria-live="polite">
          <span>Generated Verification Transaction</span>
          <code>{generatedMessage || 'Enter a valid receiver and amount'}</code>
        </div>
        <button className="secondary-button" type="submit" disabled={isLoading || !backendOnline || !valid}>
          {isLoading ? <LoaderCircle size={17} className="spin" /> : <CheckCircle2 size={17} />}
          {isLoading ? 'Verifying…' : 'Verify Transaction'}
        </button>
      </form>
    </section>
  )
}

export default VerificationPanel
