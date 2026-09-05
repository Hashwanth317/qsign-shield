const configuredApiUrl = import.meta.env.VITE_API_BASE_URL?.trim()

export const API_BASE_URL = configuredApiUrl
  ? configuredApiUrl.replace(/\/+$/, '')
  : import.meta.env.DEV ? 'http://127.0.0.1:8000' : ''

export const AUTH_EXPIRED_EVENT = 'qsign:auth-expired'

const SESSION_KEYS = {
  token: 'qsign_access_token',
  username: 'qsign_username',
  role: 'qsign_role',
}

export class ApiError extends Error {
  constructor(message, status = 0) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

function errorMessage(detail) {
  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg).join(' ')
  }

  return typeof detail === 'string' ? detail : 'Request could not be completed.'
}

function readSessionValue(key) {
  try {
    return globalThis.sessionStorage?.getItem(key) ?? null
  } catch {
    return null
  }
}

export function readAuthSession() {
  const accessToken = readSessionValue(SESSION_KEYS.token)
  const username = readSessionValue(SESSION_KEYS.username)
  const role = readSessionValue(SESSION_KEYS.role)

  if (!accessToken || !username || !role) return null
  return { accessToken, username, role }
}

function storeAuthSession(response) {
  try {
    globalThis.sessionStorage?.setItem(SESSION_KEYS.token, response.access_token)
    globalThis.sessionStorage?.setItem(SESSION_KEYS.username, response.user.username)
    globalThis.sessionStorage?.setItem(SESSION_KEYS.role, response.user.role)
  } catch {
    logout()
    throw new ApiError('Unable to store the secure browser session.')
  }
}

export function logout() {
  try {
    Object.values(SESSION_KEYS).forEach((key) => globalThis.sessionStorage?.removeItem(key))
  } catch {
    // The React state is still cleared if browser storage is unavailable.
  }
}

function announceExpiredSession() {
  logout()
  globalThis.dispatchEvent?.(new Event(AUTH_EXPIRED_EVENT))
}

async function request(path, options = {}) {
  let response
  const { authenticated = true, headers = {}, ...fetchOptions } = options
  const token = authenticated ? readSessionValue(SESSION_KEYS.token) : null

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...fetchOptions,
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...headers,
      },
    })
  } catch {
    throw new ApiError('Unable to contact Q-Sign Security Engine.')
  }

  const data = await response.json().catch(() => ({}))

  if (!response.ok) {
    if (response.status === 401 && authenticated) announceExpiredSession()
    throw new ApiError(errorMessage(data.detail), response.status)
  }

  return data
}

export function checkHealth() {
  return request('/health', { authenticated: false })
}

export async function login(credentials) {
  const response = await request('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify(credentials),
    authenticated: false,
  })
  storeAuthSession(response)
  return response
}

export function registerUser(account) {
  return request('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify(account),
    authenticated: false,
  })
}

export function getCurrentUser() {
  return request('/api/auth/me')
}

export function signMessage({ sender, message }) {
  return request('/api/sign', {
    method: 'POST',
    body: JSON.stringify({ sender, message }),
  })
}

export function verifyTransaction(payload) {
  return request('/api/verify', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function securityCheck(payload) {
  return request('/api/security/check', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function getQuantumStatus() {
  return request('/api/quantum/status')
}

// Keep the V0.8 object form compatible while offering the simpler V0.9 call.
export function analyzeQuantumChannel(scenario, shots = 1024) {
  const payload = typeof scenario === 'object' ? scenario : { scenario, shots }
  return request('/api/quantum/analyze', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export const getQuantumForensicsStatus = getQuantumStatus
