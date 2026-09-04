export const MIN_QUANTUM_SHOTS = 128
export const MAX_QUANTUM_SHOTS = 8192

export const QUANTUM_SCENARIOS = [
  { value: 'normal', label: 'Normal Channel' },
  { value: 'bit_flip', label: 'Bit Flip' },
  { value: 'phase_flip', label: 'Phase Flip' },
  { value: 'bit_phase_flip', label: 'Bit + Phase Flip' },
  { value: 'intercept_resend', label: 'Intercept-Resend' },
  { value: 'channel_noise', label: 'Channel Noise' },
]

export function validShotCount(value) {
  const shots = Number(value)
  return Number.isInteger(shots)
    && shots >= MIN_QUANTUM_SHOTS
    && shots <= MAX_QUANTUM_SHOTS
}

export function displayPercent(value) {
  return `${Number(value).toFixed(2)}%`
}

export function boundedPercent(value) {
  return Math.max(0, Math.min(Number(value), 100))
}

export function scenarioLabel(value) {
  return QUANTUM_SCENARIOS.find((scenario) => scenario.value === value)?.label
    ?? value?.replaceAll('_', ' ')
    ?? 'Unknown'
}

