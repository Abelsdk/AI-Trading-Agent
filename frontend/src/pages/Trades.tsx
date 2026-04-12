import { useEffect, useState } from 'react'
import { getTrades, type Trade } from '../api/client'

export default function Trades() {
  const [trades, setTrades] = useState<Trade[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getTrades()
      .then(setTrades)
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
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white">Trade Journal</h2>
          <p className="text-sm text-gray-500 mt-0.5">{trades.length} trades logged</p>
        </div>
        
        <a
          href="http://127.0.0.1:8000/docs#/trades/create_trade_api_v1_trades__post"
          target="_blank"
          rel="noreferrer"
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg transition-colors"
        >
          Log Trade
        </a>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-800">
              {['Symbol', 'Direction', 'Entry', 'Exit', 'Strategy', 'Status', 'P&L'].map(h => (
                <th key={h} className="text-left px-4 py-3 text-xs text-gray-500 uppercase tracking-wider">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {trades.map(trade => {
              const pnl = trade.exit_price
                ? trade.direction === 'LONG'
                  ? (trade.exit_price - trade.entry_price) * trade.quantity
                  : (trade.entry_price - trade.exit_price) * trade.quantity
                : null
              return (
                <tr key={trade.id} className="border-b border-gray-800 hover:bg-gray-800/50 transition-colors">
                  <td className="px-4 py-3 font-bold text-white">{trade.symbol}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                      trade.direction === 'LONG' ? 'bg-green-900 text-green-400' : 'bg-red-900 text-red-400'
                    }`}>
                      {trade.direction}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-300">${trade.entry_price}</td>
                  <td className="px-4 py-3 text-gray-300">{trade.exit_price ? `$${trade.exit_price}` : '—'}</td>
                  <td className="px-4 py-3 text-gray-500">{trade.strategy || '—'}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded text-xs ${
                      trade.status === 'OPEN' ? 'bg-blue-900 text-blue-400' : 'bg-gray-800 text-gray-400'
                    }`}>
                      {trade.status}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    {pnl !== null ? (
                      <span className={`font-medium ${pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {pnl >= 0 ? '+' : ''}${pnl.toFixed(2)}
                      </span>
                    ) : '—'}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )

}