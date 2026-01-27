import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Plus } from 'lucide-react'
import { getEvents } from '../api'

export default function Events() {
  const { data: events, isLoading } = useQuery({
    queryKey: ['events'],
    queryFn: getEvents
  })
  
  if (isLoading) {
    return <div>Loading...</div>
  }
  
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Events</h2>
          <p className="text-gray-600 mt-1">Manage church media events</p>
        </div>
        <Link
          to="/events/create"
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus size={20} />
          New Event
        </Link>
      </div>
      
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Title
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Speaker
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Date
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {events?.map((event) => (
              <tr key={event.event_id} className="hover:bg-gray-50">
                <td className="px-6 py-4">
                  <Link
                    to={`/events/${event.event_id}`}
                    className="text-blue-600 hover:text-blue-800 font-medium"
                  >
                    {event.title}
                  </Link>
                </td>
                <td className="px-6 py-4 text-sm text-gray-900">{event.speaker}</td>
                <td className="px-6 py-4 text-sm text-gray-900">{event.date}</td>
                <td className="px-6 py-4">
                  <StatusBadge status={event.status} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
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
