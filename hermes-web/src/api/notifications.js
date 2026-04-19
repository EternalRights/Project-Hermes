import api from './index'

export const getNotifications = (params) => api.get('/notifications', { params })

export const createNotification = (data) => api.post('/notifications', data)

export const getNotification = (id) => api.get(`/notifications/${id}`)

export const updateNotification = (id, data) => api.put(`/notifications/${id}`, data)

export const deleteNotification = (id) => api.delete(`/notifications/${id}`)

export const testNotification = (id) => api.post(`/notifications/${id}/test`)
