export const DEFAULT_TRANSACTION = {
  sender: 'Alice',
  receiver: 'Bob',
  amount: '10000',
}

export function normalizePartyName(value) {
  return String(value ?? '').trim().replace(/\s+/g, ' ')
}

export function normalizeAmount(value) {
  const amount = String(value ?? '').trim()
  if (!/^\d+$/.test(amount)) return ''
  return amount.replace(/^0+(?=\d)/, '')
}

export function isValidAmount(value) {
  const amount = normalizeAmount(value)
  return Boolean(amount) && /^\d+$/.test(amount) && BigInt(amount) > 0n
}

export function buildTransactionMessage(amount, receiver) {
  const normalizedAmount = normalizeAmount(amount)
  const normalizedReceiver = normalizePartyName(receiver)
  if (!normalizedAmount || !normalizedReceiver || !isValidAmount(normalizedAmount)) {
    return ''
  }
  return `TRANSFER ${normalizedAmount} TO ${normalizedReceiver.toUpperCase()}`
}

export function transactionFieldsAreValid({ sender, receiver, amount }) {
  return Boolean(normalizePartyName(sender))
    && Boolean(normalizePartyName(receiver))
    && isValidAmount(amount)
}

export function forgedTransactionAmount(originalAmount) {
  return normalizeAmount(originalAmount) === '90000' ? '90001' : '90000'
}

