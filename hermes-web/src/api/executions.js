import api from './index'

export const createExecution = (data) => api.post('/executions', data)

export const getExecution = (id) => api.get(`/executions/${id}`)

export const getExecutions = (params) => api.get('/executions', { params })
