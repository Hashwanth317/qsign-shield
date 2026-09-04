import assert from 'node:assert/strict'
import test from 'node:test'
import {
  buildTransactionMessage,
  forgedTransactionAmount,
  normalizeAmount,
  normalizePartyName,
  transactionFieldsAreValid,
} from './transaction.js'

test('dynamic transaction messages normalize amount and receiver', () => {
  assert.equal(
    buildTransactionMessage('25000', '  Harini  '),
    'TRANSFER 25000 TO HARINI',
  )
  assert.equal(buildTransactionMessage('00100', 'Bob'), 'TRANSFER 100 TO BOB')
})

test('transaction validation rejects empty parties and invalid amounts', () => {
  assert.equal(transactionFieldsAreValid({ sender: 'Hashwanth', receiver: 'Harini', amount: '10000' }), true)
  assert.equal(transactionFieldsAreValid({ sender: ' ', receiver: 'Harini', amount: '10000' }), false)
  assert.equal(transactionFieldsAreValid({ sender: 'Hashwanth', receiver: '', amount: '10000' }), false)
  assert.equal(transactionFieldsAreValid({ sender: 'Hashwanth', receiver: 'Harini', amount: '0' }), false)
  assert.equal(transactionFieldsAreValid({ sender: 'Hashwanth', receiver: 'Harini', amount: '10.5' }), false)
  assert.equal(normalizeAmount('abc'), '')
})

test('party names and forgery values are deterministic', () => {
  assert.equal(normalizePartyName('  Mary   Jane '), 'Mary Jane')
  assert.equal(forgedTransactionAmount('10000'), '90000')
  assert.equal(forgedTransactionAmount('90000'), '90001')
})

