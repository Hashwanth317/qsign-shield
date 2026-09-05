import { KeyRound, LoaderCircle, LockKeyhole, ShieldCheck, UserRound } from 'lucide-react'
import { useState } from 'react'

function LoginPage({ onSignIn, isLoading, error, validatingSession = false }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')

  async function handleSubmit(event) {
    event.preventDefault()
    if (!username.trim() || !password) return
    await onSignIn({ username: username.trim(), password })
  }

  return (
    <main className="login-shell">
      <section className="login-card" aria-labelledby="login-title">
        <div className="login-brand-mark" aria-hidden="true"><ShieldCheck size={34} /></div>
        <p className="eyebrow">SIH26141 · QUANTUM SECURITY</p>
        <h1 id="login-title">Q-SIGN SHIELD</h1>
        <p className="login-subtitle">Secure Transaction Access</p>

        <form className="login-form" onSubmit={handleSubmit}>
          <label>
            Username
            <span className="login-input-wrap">
              <UserRound size={17} aria-hidden="true" />
              <input
                autoComplete="username"
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                disabled={isLoading || validatingSession}
                required
              />
            </span>
          </label>
          <label>
            Password
            <span className="login-input-wrap">
              <LockKeyhole size={17} aria-hidden="true" />
              <input
                type="password"
                autoComplete="current-password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                disabled={isLoading || validatingSession}
                required
              />
            </span>
          </label>

          {error && <p className="login-error" role="alert">{error}</p>}

          <button
            className="primary-button login-button"
            type="submit"
            disabled={isLoading || validatingSession || !username.trim() || !password}
          >
            {isLoading || validatingSession ? <LoaderCircle size={18} className="spin" /> : <KeyRound size={18} />}
            {validatingSession ? 'Restoring Session…' : isLoading ? 'Signing In…' : 'Sign In'}
          </button>
        </form>

        <p className="prototype-access">Prototype Secure Access</p>
      </section>
    </main>
  )
}

export default LoginPage
