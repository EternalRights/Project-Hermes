import api from './index'

export const getTestCases = (params) => api.get('/test-cases', { params })

export const createTestCase = (data) => api.post('/test-cases', data)

export const getTestCase = (id) => api.get(`/test-cases/${id}`)

export const updateTestCase = (id, data) => api.put(`/test-cases/${id}`, data)

export const deleteTestCase = (id) => api.delete(`/test-cases/${id}`)

export const copyTestCase = (id) => api.post(`/test-cases/${id}/copy`)

export const getModules = (projectId) => api.get(`/projects/${projectId}/modules`)

export const getTags = (projectId) => api.get(`/projects/${projectId}/tags`)

export const exportTestCases = (params) => api.get('/test-cases/export', { params, responseType: 'blob' })

export const importTestCases = (data) => api.post('/test-cases/import', data)
