import api from './index'

export const getVariables = (projectId, params) => api.get(`/projects/${projectId}/variables`, { params })

export const createVariable = (projectId, data) => api.post(`/projects/${projectId}/variables`, data)

export const updateVariable = (projectId, id, data) => api.put(`/projects/${projectId}/variables/${id}`, data)

export const deleteVariable = (projectId, id) => api.delete(`/projects/${projectId}/variables/${id}`)
