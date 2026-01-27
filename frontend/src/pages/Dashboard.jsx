import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Calendar, Play, CheckCircle, AlertCircle } from 'lucide-react'
import { getEvents, getSystemStatus } from '../api'

export default function Dashboard() {
  const { data: events } = useQuery({
    queryKey: ['events'],
    queryFn: getEvents
  })
  
  const { data: status } = useQuery({
    queryKey: ['status'],
    queryFn: getSystemStatus
  })
  
  const recentEvents = events?.slice(0, 5) || []
  
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Dashboard</h2>
        <p className="text-gray-600 mt-1">Workflow overview and recent activity</p>
      </div>
      
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatsCard
          title="Total Events"
          value={events?.length || 0}
          icon={Calendar}
          color="blue"
        />
        <StatsCard
          title="Processing"
          value={events?.filter(e => e.status === 'processing').length || 0}
          icon={Play}
          color="yellow"
        />
        <StatsCard
          title="Completed"
          value={events?.filter(e => e.status === 'completed').length || 0}
          icon={CheckCircle}
          color="green"
        />
      </div>
      
      {/* System Status */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">System Status</h3>
        <div className="space-y-3">
          {status?.dependencies?.map((dep) => (
            <DependencyStatus key={dep.name} {...dep} />
          ))}
        </div>
      </div>
      
      {/* Recent Events */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">Recent Events</h3>
            <Link to="/events" className="text-blue-600 hover:text-blue-700 text-sm font-medium">
              View all
            </Link>
          </div>
        </div>
        <div className="divide-y divide-gray-200">
          {recentEvents.map((event) => (
            <Link
              key={event.event_id}
              to={`/events/${event.event_id}`}
              className="block p-6 hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h4 className="font-medium text-gray-900">{event.title}</h4>
                  <p className="text-sm text-gray-600 mt-1">
                    {event.speaker} • {event.date}
                  </p>
                </div>
                <StatusBadge status={event.status} />
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  )
}

function StatsCard({ title, value, icon: Icon, color }) {
  const colorClasses = {
    blue: 'bg-blue-100 text-blue-600',
    yellow: 'bg-yellow-100 text-yellow-600',
    green: 'bg-green-100 text-green-600',
  }
  
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600">{title}</p>
          <p className="text-3xl font-bold text-gray-900 mt-1">{value}</p>
        </div>
        <div className={`p-3 rounded-full ${colorClasses[color]}`}>
          <Icon size={24} />
        </div>
      </div>
    </div>
  )
}

function DependencyStatus({ name, installed, required }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-sm text-gray-700">{name}</span>
      <div className="flex items-center gap-2">
        {installed ? (
          <CheckCircle size={16} className="text-green-600" />
        ) : (
          <AlertCircle size={16} className={required ? 'text-red-600' : 'text-gray-400'} />
        )}
        <span className={`text-sm ${installed ? 'text-green-600' : required ? 'text-red-600' : 'text-gray-400'}`}>
          {installed ? 'Installed' : 'Not installed'}
        </span>
      </div>
    </div>
  )
}

function StatusBadge({ status }) {
  const statusConfig = {
    pending: { label: 'Pending', className: 'bg-gray-100 text-gray-700' },
    processing: { label: 'Processing', className: 'bg-yellow-100 text-yellow-700' },
    completed: { label: 'Completed', className: 'bg-green-100 text-green-700' },
    failed: { label: 'Failed', className: 'bg-red-100 text-red-700' },
  }
  
  const config = statusConfig[status] || statusConfig.pending
  
  return (
    <span className={`px-3 py-1 rounded-full text-xs font-medium ${config.className}`}>
      {config.label}
    </span>
  )
}
