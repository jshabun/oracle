import { Outlet, Link, useLocation } from 'react-router-dom'
import { Home, Users, TrendingUp, Target, Settings } from 'lucide-react'

export default function Layout() {
  const location = useLocation()
  
  const isActive = (path) => location.pathname === path
  
  const navItems = [
    { path: '/', label: 'Dashboard', icon: Home },
    { path: '/draft', label: 'Draft Mode', icon: Target },
    { path: '/team', label: 'My Team', icon: Users },
    { path: '/recommendations', label: 'Recommendations', icon: TrendingUp },
    { path: '/players', label: 'Players', icon: Users },
  ]
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-oracle-dark text-white shadow-lg">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="text-3xl">🏀</div>
              <div>
                <h1 className="text-2xl font-bold">Fantasy Basketball Oracle</h1>
                <p className="text-sm text-gray-300">Your AI-powered fantasy assistant</p>
              </div>
            </div>
            <button className="p-2 hover:bg-gray-700 rounded-lg transition">
              <Settings size={24} />
            </button>
          </div>
        </div>
      </header>
      
      {/* Navigation */}
      <nav className="bg-white shadow-md">
        <div className="container mx-auto px-4">
          <div className="flex space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon
              const active = isActive(item.path)
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center space-x-2 px-4 py-3 border-b-2 transition ${
                    active
                      ? 'border-oracle-orange text-oracle-orange font-semibold'
                      : 'border-transparent text-gray-600 hover:text-oracle-orange'
                  }`}
                >
                  <Icon size={20} />
                  <span>{item.label}</span>
                </Link>
              )
            })}
          </div>
        </div>
      </nav>
      
      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <Outlet />
      </main>
      
      {/* Footer */}
      <footer className="bg-oracle-dark text-white mt-12">
        <div className="container mx-auto px-4 py-6 text-center">
          <p className="text-sm text-gray-400">
            Fantasy Basketball Oracle v0.1.0 | 9-Cat League Assistant
          </p>
        </div>
      </footer>
    </div>
  )
}
