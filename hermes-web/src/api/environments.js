import api from './index'

export const getEnvironments = (projectId, params) => api.get(`/projects/${projectId}/environments`, { params })

export const createEnvironment = (projectId, data) => api.post(`/projects/${projectId}/environments`, data)

export const updateEnvironment = (projectId, id, data) => api.put(`/projects/${projectId}/environments/${id}`, data)

export const deleteEnvironment = (projectId, id) => api.delete(`/projects/${projectId}/environments/${id}`)
