import api from './index'

export const login = (data) => api.post('/auth/login', data)

export const register = (data) => api.post('/auth/register', data)

export const refreshToken = () => {
  const token = localStorage.getItem('refreshToken')
  return api.post('/auth/refresh', {}, {
    headers: { Authorization: `Bearer ${token}` }
  })
}
