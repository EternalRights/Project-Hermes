import api from './index'

export const login = (data) => api.post('/auth/login', data)

export const register = (data) => api.post('/auth/register', data)

export const refreshToken = () => {
  const refreshToken = localStorage.getItem('refreshToken')
  return api.post('/auth/refresh', { refreshToken })
}
