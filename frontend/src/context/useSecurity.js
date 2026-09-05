import { useContext } from 'react'
import SecurityContext from './security-context'

export default function useSecurity() {
  const value = useContext(SecurityContext)
  if (!value) throw new Error('useSecurity must be used within SecurityProvider')
  return value
}
