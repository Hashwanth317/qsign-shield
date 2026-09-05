import AttackLab from '../components/AttackLab'
import SecurityResult from '../components/SecurityResult'
import useSecurity from '../context/useSecurity'

function AttackLabPage({ navigate }) {
  const { activeAttack, backendOnline, handleAttack, latestResult, signedTransaction } = useSecurity()
  return (
    <>
      <section className="page-intro">
        <div><p className="section-kicker">CONTROLLED SECURITY TESTING</p><h1>Q-Sign Attack Lab</h1></div>
        <p>Controlled Transaction Security Simulation</p>
      </section>
      <div className="education-banner">Educational security simulation environment. Every result is classified by the existing backend detector.</div>
      <AttackLab
        activeSignature={signedTransaction}
        activeAction={activeAttack}
        onRunAttack={handleAttack}
        backendOnline={backendOnline}
        onGoToTransactions={() => navigate('/transactions')}
      />
      {signedTransaction && <SecurityResult result={latestResult} signedTransaction={signedTransaction} />}
    </>
  )
}

export default AttackLabPage
