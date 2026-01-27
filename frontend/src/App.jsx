import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Events from './pages/Events'
import EventCreate from './pages/EventCreate'
import EventDetail from './pages/EventDetail'
import Settings from './pages/Settings'
import Dependencies from './pages/Dependencies'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/events" element={<Events />} />
        <Route path="/events/create" element={<EventCreate />} />
        <Route path="/events/:eventId" element={<EventDetail />} />
        <Route path="/dependencies" element={<Dependencies />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Layout>
  )
}

export default App
