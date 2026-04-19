import api from './index'

export const getReport = (executionId) => api.get(`/executions/${executionId}/report`)

export const getTrend = (params) => api.get('/reports/trend', { params })

export const exportReport = (executionId) => api.get(`/executions/${executionId}/report/export`, { responseType: 'blob' })
