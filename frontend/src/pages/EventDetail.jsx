import React from 'react'
import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { getEvent } from '../api'

export default function EventDetail() {
  const { eventId } = useParams()
  const { data: event, isLoading } = useQuery({
    queryKey: ['event', eventId],
    queryFn: () => getEvent(eventId)
  })
  
  if (isLoading) {
    return <div>Loading...</div>
  }
  
  if (!event) {
    return <div>Event not found</div>
  }
  
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-gray-900">{event.title}</h2>
        <p className="text-gray-600 mt-1">{event.speaker} • {event.date}</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Event Details</h3>
          <dl className="space-y-2">
            <div>
              <dt className="text-sm text-gray-600">Series</dt>
              <dd className="text-sm font-medium">{event.series || 'N/A'}</dd>
            </div>
            <div>
              <dt className="text-sm text-gray-600">Scripture</dt>
              <dd className="text-sm font-medium">{event.scripture || 'N/A'}</dd>
            </div>
            <div>
              <dt className="text-sm text-gray-600">Language</dt>
              <dd className="text-sm font-medium">{event.language}</dd>
            </div>
          </dl>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Workflow Status</h3>
          <div className="space-y-2">
            {Object.entries(event.modules).map(([name, enabled]) => (
              <div key={name} className="flex items-center justify-between">
                <span className="text-sm text-gray-700">{formatModuleName(name)}</span>
                <span className={`text-sm ${enabled ? 'text-green-600' : 'text-gray-400'}`}>
                  {enabled ? 'Enabled' : 'Disabled'}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

function formatModuleName(name) {
  return name.split('_').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ')
}
