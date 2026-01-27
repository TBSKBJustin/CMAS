import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { createEvent } from '../api'

export default function EventCreate() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    title: '',
    speaker: '',
    series: '',
    scripture: '',
    language: 'auto',
    modules: {
      thumbnail_ai: true,
      thumbnail_compose: true,
      subtitles: true,
      publish_youtube: false,
      publish_website: false,
    }
  })
  
  const createMutation = useMutation({
    mutationFn: createEvent,
    onSuccess: (data) => {
      navigate(`/events/${data.event_id}`)
    }
  })
  
  const handleSubmit = (e) => {
    e.preventDefault()
    createMutation.mutate(formData)
  }
  
  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }
  
  const handleModuleToggle = (moduleName) => {
    setFormData(prev => ({
      ...prev,
      modules: {
        ...prev.modules,
        [moduleName]: !prev.modules[moduleName]
      }
    }))
  }
  
  return (
    <div className="max-w-3xl">
      <h2 className="text-3xl font-bold text-gray-900 mb-6">Create New Event</h2>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="bg-white rounded-lg shadow p-6 space-y-4">
          <h3 className="text-lg font-semibold">Event Details</h3>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Title *
            </label>
            <input
              type="text"
              name="title"
              required
              value={formData.title}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Sermon title"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Speaker *
            </label>
            <input
              type="text"
              name="speaker"
              required
              value={formData.speaker}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Pastor name"
            />
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Series
              </label>
              <input
                type="text"
                name="series"
                value={formData.series}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Optional"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Scripture
              </label>
              <input
                type="text"
                name="scripture"
                value={formData.scripture}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="e.g., John 3:16"
              />
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Workflow Modules</h3>
          <div className="space-y-3">
            <ModuleToggle
              name="thumbnail_ai"
              label="Generate Thumbnail (AI)"
              checked={formData.modules.thumbnail_ai}
              onChange={() => handleModuleToggle('thumbnail_ai')}
            />
            <ModuleToggle
              name="thumbnail_compose"
              label="Compose Final Thumbnail"
              checked={formData.modules.thumbnail_compose}
              onChange={() => handleModuleToggle('thumbnail_compose')}
            />
            <ModuleToggle
              name="subtitles"
              label="Generate Subtitles"
              checked={formData.modules.subtitles}
              onChange={() => handleModuleToggle('subtitles')}
            />
            <ModuleToggle
              name="publish_youtube"
              label="Publish to YouTube"
              checked={formData.modules.publish_youtube}
              onChange={() => handleModuleToggle('publish_youtube')}
            />
            <ModuleToggle
              name="publish_website"
              label="Publish to Website"
              checked={formData.modules.publish_website}
              onChange={() => handleModuleToggle('publish_website')}
            />
          </div>
        </div>
        
        <div className="flex gap-3">
          <button
            type="submit"
            disabled={createMutation.isPending}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {createMutation.isPending ? 'Creating...' : 'Create Event'}
          </button>
          <button
            type="button"
            onClick={() => navigate('/events')}
            className="px-6 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  )
}

function ModuleToggle({ name, label, checked, onChange }) {
  return (
    <label className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50 cursor-pointer">
      <input
        type="checkbox"
        name={name}
        checked={checked}
        onChange={onChange}
        className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
      />
      <span className="text-sm font-medium text-gray-700">{label}</span>
    </label>
  )
}
