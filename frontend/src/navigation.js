import { Activity, Atom, FlaskConical, LayoutDashboard, ReceiptText } from 'lucide-react'

export const NAVIGATION = [
  ['/dashboard', 'Dashboard', LayoutDashboard],
  ['/transactions', 'Transaction Center', ReceiptText],
  ['/attack-lab', 'Attack Lab', FlaskConical],
  ['/quantum-forensics', 'Quantum Forensics', Atom],
  ['/security-events', 'Security Events', Activity],
]

export const PAGE_TITLES = Object.fromEntries(NAVIGATION.map(([path, label]) => [path, label]))
