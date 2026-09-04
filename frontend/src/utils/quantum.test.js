import assert from 'node:assert/strict'
import test from 'node:test'
import {
  boundedPercent,
  displayPercent,
  scenarioLabel,
  validShotCount,
} from './quantum.js'

test('quantum shots accept only the API range and integers', () => {
  assert.equal(validShotCount(128), true)
  assert.equal(validShotCount('1024'), true)
  assert.equal(validShotCount(8192), true)
  assert.equal(validShotCount(127), false)
  assert.equal(validShotCount(8193), false)
  assert.equal(validShotCount(128.5), false)
  assert.equal(validShotCount(''), false)
})

test('display helpers preserve raw values while formatting presentation', () => {
  assert.equal(displayPercent(51.953125), '51.95%')
  assert.equal(boundedPercent(110), 100)
  assert.equal(boundedPercent(-3), 0)
  assert.equal(scenarioLabel('phase_flip'), 'Phase Flip')
})

