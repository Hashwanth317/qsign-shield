import { ArrowRight, Bug, Fingerprint, LoaderCircle, Repeat2, ShieldAlert, UserRoundX } from 'lucide-react'

const attackCards = [
  {
    key: 'forgery',
    title: 'Message Forgery',
    description: 'Modify the transaction while reusing the original signature.',
    icon: Bug,
    button: 'Simulate Forgery',
  },
  {
    key: 'tampering',
    title: 'Signature Tampering',
    description: 'Modify signature bits while keeping the message unchanged.',
    icon: Fingerprint,
    button: 'Simulate Signature Tampering',
  },
  {
    key: 'replay',
    title: 'Replay Attack',
    description: 'Submit the same valid transaction twice to trigger replay protection.',
    icon: Repeat2,
    button: 'Simulate Replay',
  },
  {
    key: 'impersonation',
    title: 'Impersonation',
    description: 'Reuse the current sender’s valid signature while claiming to be Attacker.',
    icon: UserRoundX,
    button: 'Simulate Impersonation',
  },
]

function AttackLab({ activeSignature, activeAction, onRunAttack, backendOnline, onGoToTransactions }) {
  if (!activeSignature) {
    return (
      <section className="empty-workspace">
        <span className="empty-workspace-icon"><ShieldAlert size={28} /></span>
        <div>
          <p className="section-kicker">SIGNED TRANSACTION REQUIRED</p>
          <h2>Attack simulations are locked</h2>
          <p>Create and sign a transaction in Transaction Center before running attack simulations.</p>
        </div>
        <button className="primary-button" type="button" onClick={onGoToTransactions}>Go to Transaction Center <ArrowRight size={17} /></button>
      </section>
    )
  }

  return (
    <section className="attack-lab">
      <div className="section-header">
        <div>
          <p className="section-kicker">ACTIVE ATTACK SURFACE</p>
          <h2>Transaction Attack Simulations</h2>
          <p>Each simulation sends a real request to the Q-Sign security engine.</p>
        </div>
      </div>

      <dl className="active-transaction-grid">
        <div><dt>Sender</dt><dd>{activeSignature.sender}</dd></div>
        <div><dt>Receiver</dt><dd>{activeSignature.receiver}</dd></div>
        <div><dt>Amount</dt><dd>{activeSignature.amount}</dd></div>
        <div><dt>Signature ID</dt><dd><code>{activeSignature.signature_id}</code></dd></div>
        <div className="transaction-message"><dt>Transaction Message</dt><dd><code>{activeSignature.message}</code></dd></div>
      </dl>

      <div className="attack-grid">
        {attackCards.map(({ key, title, description, icon: Icon, button }) => {
          const loading = activeAction === key
          return (
            <article className="attack-card" key={key}>
              <div className="attack-icon"><Icon size={20} /></div>
              <h3>{title}</h3>
              <p>{description}</p>
              <button
                className="attack-button"
                type="button"
                onClick={() => onRunAttack(key)}
                disabled={!backendOnline || Boolean(activeAction)}
              >
                {loading && <LoaderCircle size={15} className="spin" />}
                {loading ? 'Running Simulation…' : button}
              </button>
            </article>
          )
        })}
      </div>
    </section>
  )
}

export default AttackLab
