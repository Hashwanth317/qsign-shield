const configuredApiUrl = import.meta.env.VITE_API_BASE_URL?.trim()

export const API_BASE_URL = configuredApiUrl
  ? configuredApiUrl.replace(/\/+$/, '')
  : import.meta.env.DEV ? 'http://127.0.0.1:8000' : ''

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

async function request(path, options = {}) {
  let response

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      ...options,
    })
  } catch {
    throw new ApiError('Unable to contact Q-Sign Security Engine.')
  }

  const data = await response.json().catch(() => ({}))

  if (!response.ok) {
    throw new ApiError(errorMessage(data.detail), response.status)
  }

  return data
}

export function checkHealth(options = {}) {
  return request('/health', options)
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
