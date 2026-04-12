import { useEffect, useState } from 'react'
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import MetricCard from '../components/MetricCard'
import { getAnalytics, getTrades, type AnalyticsSummary, type Trade } from '../api/client'

export default function Dashboard() {
  const [analytics, setAnalytics] = useState<AnalyticsSummary | null>(null)
  const [trades, setTrades] = useState<Trade[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([getAnalytics(), getTrades()])
      .then(([a, t]) => { setAnalytics(a); setTrades(t) })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  // Build equity curve from closed trades
  const equityCurve = trades
    .filter(t => t.status === 'CLOSED' && t.exit_price)
    .map((t, i) => {
      const pnl = t.direction === 'LONG'
        ? (t.exit_price! - t.entry_price) * t.quantity
        : (t.entry_price - t.exit_price!) * t.quantity
      return { trade: i + 1, pnl: Math.round(pnl * 100) / 100 }
    })
    .reduce((acc, curr, i) => {
      const prev = i > 0 ? acc[i - 1].cumulative : 0
      return [...acc, { ...curr, cumulative: Math.round((prev + curr.pnl) * 100) / 100 }]
    }, [] as any[])

  if (loading) return (
    <div className="flex items-center justify-center h-full">
      <p className="text-gray-500">Loading...</p>
    </div>
  )

  return (
    <div className="p-6 space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white">Dashboard</h2>
        <p className="text-sm text-gray-500 mt-0.5">Portfolio overview</p>
      </div>

      {/* Metrics */}
      {analytics && analytics.total_trades > 0 ? (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            label="Win Rate"
            value={`${analytics.win_rate}%`}
            sub={`${analytics.wins}W / ${analytics.losses}L`}
            color={analytics.win_rate >= 50 ? 'green' : 'red'}
          />
          <MetricCard
            label="Total P&L"
            value={`$${analytics.total_pnl}`}
            sub={`${analytics.total_trades} trades`}
            color={analytics.total_pnl >= 0 ? 'green' : 'red'}
          />
          <MetricCard
            label="Expectancy"
            value={`$${analytics.expectancy}`}
            sub="per trade avg"
            color={analytics.expectancy >= 0 ? 'green' : 'red'}
          />
          <MetricCard
            label="Max Drawdown"
            value={`$${analytics.max_drawdown}`}
            sub="peak to trough"
            color="amber"
          />
        </div>
      ) : (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 text-center">
          <p className="text-gray-500">No closed trades yet. Log your first trade to see metrics.</p>
        </div>
      )}

      {/* Equity Curve */}
      {equityCurve.length > 0 && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
          <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-4">
            Equity Curve
          </h3>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={equityCurve}>
              <defs>
                <linearGradient id="pnlGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="trade" tick={{ fill: '#6b7280', fontSize: 12 }} />
              <YAxis tick={{ fill: '#6b7280', fontSize: 12 }} />
              <Tooltip
                contentStyle={{ background: '#111827', border: '1px solid #374151', borderRadius: 8 }}
                labelStyle={{ color: '#9ca3af' }}
              />
              <Area
                type="monotone"
                dataKey="cumulative"
                stroke="#3b82f6"
                strokeWidth={2}
                fill="url(#pnlGrad)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Recent Trades */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
        <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-4">
          Recent Trades
        </h3>
        {trades.length === 0 ? (
          <p className="text-gray-600 text-sm">No trades logged yet.</p>
        ) : (
          <div className="space-y-2">
            {trades.slice(0, 5).map(trade => {
              const pnl = trade.exit_price
                ? trade.direction === 'LONG'
                  ? (trade.exit_price - trade.entry_price) * trade.quantity
                  : (trade.entry_price - trade.exit_price) * trade.quantity
                : null
              return (
                <div key={trade.id} className="flex items-center gap-3 py-2 border-b border-gray-800 last:border-0">
                  <span className="font-bold text-white w-14">{trade.symbol}</span>
                  <span className={`text-xs px-2 py-0.5 rounded font-medium ${
                    trade.direction === 'LONG' ? 'bg-green-900 text-green-400' : 'bg-red-900 text-red-400'
                  }`}>
                    {trade.direction}
                  </span>
                  <span className="text-gray-500 text-sm flex-1">{trade.strategy || 'no strategy'}</span>
                  <span className={`text-xs px-2 py-0.5 rounded ${
                    trade.status === 'OPEN' ? 'bg-blue-900 text-blue-400' : 'bg-gray-800 text-gray-400'
                  }`}>
                    {trade.status}
                  </span>
                  {pnl !== null && (
                    <span className={`font-medium text-sm ${pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {pnl >= 0 ? '+' : ''}${pnl.toFixed(2)}
                    </span>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}