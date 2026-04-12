import { Outlet, NavLink } from 'react-router-dom'

const nav = [
  { to: '/', label: 'Dashboard', exact: true },
  { to: '/trades', label: 'Trade Journal' },
  { to: '/analytics', label: 'Analytics' },
  { to: '/ai', label: 'AI Insights' },
]

export default function Layout() {
  return (
    <div className="flex h-screen bg-gray-950 text-gray-100">
      {/* Sidebar */}
      <aside className="w-52 bg-gray-900 border-r border-gray-800 flex flex-col">
        <div className="p-5 border-b border-gray-800">
          <h1 className="text-lg font-bold text-white">MarketMind</h1>
          <p className="text-xs text-gray-500 mt-0.5">AI Trading Research</p>
        </div>
        <nav className="flex-1 p-3 space-y-1">
          {nav.map(({ to, label, exact }) => (
            <NavLink
              key={to}
              to={to}
              end={exact}
              className={({ isActive }) =>
                `block px-3 py-2 rounded-lg text-sm transition-colors ${
                  isActive
                    ? 'bg-blue-600 text-white font-medium'
                    : 'text-gray-400 hover:text-white hover:bg-gray-800'
                }`
              }
            >
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="p-4 border-t border-gray-800">
          <p className="text-xs text-gray-600">Educational use only</p>
          <p className="text-xs text-gray-600">Not financial advice</p>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  )
}