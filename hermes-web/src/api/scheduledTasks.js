import api from './index'

export const getScheduledTasks = (params) => api.get('/scheduled-tasks', { params })

export const createScheduledTask = (data) => api.post('/scheduled-tasks', data)

export const getScheduledTask = (id) => api.get(`/scheduled-tasks/${id}`)

export const updateScheduledTask = (id, data) => api.put(`/scheduled-tasks/${id}`, data)

export const deleteScheduledTask = (id) => api.delete(`/scheduled-tasks/${id}`)

export const toggleScheduledTask = (id, data) => api.put(`/scheduled-tasks/${id}/toggle`, data)

export const getScheduledTaskHistory = (id) => api.get(`/scheduled-tasks/${id}/history`)
