import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Home, Calendar, Settings, Package } from 'lucide-react'

export default function Layout({ children }) {
  const location = useLocation()
  
  const navItems = [
    { path: '/', label: 'Dashboard', icon: Home },
    { path: '/events', label: 'Events', icon: Calendar },
    { path: '/dependencies', label: 'Dependencies', icon: Package },
    { path: '/settings', label: 'Settings', icon: Settings },
  ]
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="px-6 py-4">
          <h1 className="text-2xl font-bold text-gray-900">
            ⛪ Church Media Automation
          </h1>
        </div>
      </header>
      
      <div className="flex">
        {/* Sidebar */}
        <aside className="w-64 bg-white border-r border-gray-200 min-h-[calc(100vh-73px)]">
          <nav className="p-4 space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.path
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center gap-3 px-4 py-2 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-blue-50 text-blue-600'
                      : 'text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <Icon size={20} />
                  <span className="font-medium">{item.label}</span>
                </Link>
              )
            })}
          </nav>
        </aside>
        
        {/* Main Content */}
        <main className="flex-1 p-8">
          {children}
        </main>
      </div>
    </div>
  )
}
