import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi } from '../api/auth'
import api from '../api/index'
import router from '../router'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const refreshTokenVal = ref(localStorage.getItem('refreshToken') || '')
  const userInfo = ref(null)

  const isLoggedIn = computed(() => !!token.value)

  const login = async (credentials) => {
    const res = await loginApi(credentials)
    token.value = res.data.token
    refreshTokenVal.value = res.data.refreshToken
    localStorage.setItem('token', res.data.token)
    localStorage.setItem('refreshToken', res.data.refreshToken)
    userInfo.value = res.data.user
  }

  const logout = () => {
    token.value = ''
    refreshTokenVal.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    router.push('/login')
  }

  const fetchUserInfo = async () => {
    const res = await api.get('/auth/me')
    userInfo.value = res.data
  }

  return {
    token,
    refreshToken: refreshTokenVal,
    userInfo,
    isLoggedIn,
    login,
    logout,
    fetchUserInfo,
  }
})
