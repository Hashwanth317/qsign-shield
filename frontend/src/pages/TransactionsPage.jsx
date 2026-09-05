import SecurityResult from '../components/SecurityResult'
import SigningPanel from '../components/SigningPanel'
import VerificationPanel from '../components/VerificationPanel'
import useSecurity from '../context/useSecurity'

function TransactionsPage() {
  const {
    backendOnline,
    handleSign,
    handleVerify,
    latestResult,
    showFeedback,
    signedTransaction,
    signing,
    verifying,
  } = useSecurity()

  return (
    <>
      <section className="page-intro">
        <div><p className="section-kicker">TRANSACTION SECURITY</p><h1>Transaction Center</h1></div>
        <p>Secure Digital Transaction Signing &amp; Verification</p>
      </section>
      <section className="work-grid transaction-work-grid">
        <SigningPanel
          onSign={handleSign}
          signedTransaction={signedTransaction}
          isLoading={signing}
          backendOnline={backendOnline}
          onFeedback={showFeedback}
        />
        <VerificationPanel
          key={signedTransaction?.signature_id ?? 'new-transaction'}
          activeSignature={signedTransaction}
          onVerify={handleVerify}
          isLoading={verifying}
          backendOnline={backendOnline}
        />
      </section>
      <SecurityResult result={latestResult} signedTransaction={signedTransaction} />
    </>
  )
}

export default TransactionsPage
