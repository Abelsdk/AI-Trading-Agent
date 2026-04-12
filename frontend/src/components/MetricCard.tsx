interface Props {
  label: string
  value: string | number
  sub?: string
  color?: 'green' | 'red' | 'amber' | 'blue' | 'default'
}

const colors = {
  green: 'text-green-400',
  red: 'text-red-400',
  amber: 'text-amber-400',
  blue: 'text-blue-400',
  default: 'text-white',
}

export default function MetricCard({ label, value, sub, color = 'default' }: Props) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
      <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">{label}</p>
      <p className={`text-2xl font-bold ${colors[color]}`}>{value}</p>
      {sub && <p className="text-xs text-gray-600 mt-1">{sub}</p>}
    </div>
  )
}