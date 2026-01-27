import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  }
})

// Events
export const getEvents = async () => {
  const { data } = await api.get('/events')
  return data
}

export const getEvent = async (eventId) => {
  const { data } = await api.get(`/events/${eventId}`)
  return data
}

export const createEvent = async (eventData) => {
  const { data } = await api.post('/events', eventData)
  return data
}

export const runWorkflow = async (eventId) => {
  const { data } = await api.post(`/events/${eventId}/run`)
  return data
}

// Dependencies
export const checkDependencies = async () => {
  const { data } = await api.get('/dependencies')
  return data
}

export const installDependency = async (depKey) => {
  const { data } = await api.post(`/dependencies/${depKey}/install`)
  return data
}

export const configureCustomPath = async (depKey, path) => {
  const { data } = await api.post(`/dependencies/${depKey}/configure-path`, { path })
  return data
}

// System
export const getSystemStatus = async () => {
  const { data } = await api.get('/status')
  return data
}

export default api
