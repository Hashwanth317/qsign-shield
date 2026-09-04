import { Bug, Fingerprint, LoaderCircle, Repeat2, UserRoundX } from 'lucide-react'

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

function AttackLab({ activeSignature, activeAction, onRunAttack, backendOnline }) {
  return (
    <section className="attack-lab">
      <div className="section-header">
        <div>
          <p className="section-kicker">SIH DEMONSTRATION ENVIRONMENT</p>
          <h2>Attack Lab</h2>
          <p>Each simulation sends a real request to the Q-Sign security engine.</p>
        </div>
        {!activeSignature && <span className="setup-note">Generate a signature to unlock simulations</span>}
      </div>

      {activeSignature && (
        <div className="attack-transaction-summary">
          <span>Active signed transaction</span>
          <strong>{activeSignature.sender} → {activeSignature.receiver}</strong>
          <code>{activeSignature.message}</code>
        </div>
      )}

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
                disabled={!activeSignature || !backendOnline || Boolean(activeAction)}
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
