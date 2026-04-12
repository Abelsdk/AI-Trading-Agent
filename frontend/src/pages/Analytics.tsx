import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import MetricCard from '../components/MetricCard'
import { getAnalytics, getStrategyBreakdown, type AnalyticsSummary } from '../api/client'

export default function Analytics() {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null)
  const [strategies, setStrategies] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([getAnalytics(), getStrategyBreakdown()])
      .then(([s, st]) => { setSummary(s); setStrategies(st) })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div className="flex items-center justify-center h-full">
      <p className="text-gray-500">Loading...</p>
    </div>
  )

  return (
    <div className="p-6 space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white">Analytics</h2>
        <p className="text-sm text-gray-500 mt-0.5">Performance breakdown</p>
      </div>

      {summary && summary.total_trades > 0 ? (
        <>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <MetricCard label="Sharpe Ratio" value={summary.sharpe_ratio} color="blue" />
            <MetricCard label="Profit Factor" value={summary.profit_factor} color={summary.profit_factor >= 1.5 ? 'green' : 'amber'} />
            <MetricCard label="Avg Win" value={`$${summary.avg_win}`} color="green" />
            <MetricCard label="Avg Loss" value={`$${summary.avg_loss}`} color="red" />
            <MetricCard label="R Expectancy" value={summary.r_expectancy ? `${summary.r_expectancy}R` : 'N/A'} color="blue" />
            <MetricCard label="Win Streak" value={summary.max_win_streak} sub="best" color="green" />
            <MetricCard label="Loss Streak" value={summary.max_loss_streak} sub="worst" color="red" />
            <MetricCard label="Total Trades" value={summary.total_trades} color="default" />
          </div>

          {strategies.length > 0 && (
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
              <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-4">
                Strategy Comparison — Win Rate %
              </h3>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={strategies}>
                  <XAxis dataKey="strategy" tick={{ fill: '#6b7280', fontSize: 12 }} />
                  <YAxis tick={{ fill: '#6b7280', fontSize: 12 }} />
                  <Tooltip
                    contentStyle={{ background: '#111827', border: '1px solid #374151', borderRadius: 8 }}
                  />
                  <Bar dataKey="win_rate" radius={[4, 4, 0, 0]}>
                    {strategies.map((s, i) => (
                      <Cell key={i} fill={s.win_rate >= 50 ? '#22c55e' : '#ef4444'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </>
      ) : (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 text-center">
          <p className="text-gray-500">No closed trades yet. Close some trades to see analytics.</p>
        </div>
      )}
    </div>
  )
}