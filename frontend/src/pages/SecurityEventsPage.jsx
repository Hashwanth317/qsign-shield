import SecurityEvents from '../components/SecurityEvents'
import useSecurity from '../context/useSecurity'

function SecurityEventsPage() {
  const { events } = useSecurity()
  return (
    <>
      <section className="page-intro">
        <div><p className="section-kicker">CURRENT BROWSER SESSION</p><h1>Security Events</h1></div>
        <p>Review transaction and simulated quantum-channel evidence recorded during this session.</p>
      </section>
      <SecurityEvents events={events} />
    </>
  )
}

export default SecurityEventsPage
