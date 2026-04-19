import api from './index'

export const getTestSuites = (params) => api.get('/test-suites', { params })

export const createTestSuite = (data) => api.post('/test-suites', data)

export const getTestSuite = (id) => api.get(`/test-suites/${id}`)

export const updateTestSuite = (id, data) => api.put(`/test-suites/${id}`, data)

export const deleteTestSuite = (id) => api.delete(`/test-suites/${id}`)

export const addSuiteCase = (suiteId, data) => api.post(`/test-suites/${suiteId}/cases`, data)

export const removeSuiteCase = (suiteId, caseId) => api.delete(`/test-suites/${suiteId}/cases/${caseId}`)

export const toggleSuiteCase = (suiteId, caseId, data) => api.put(`/test-suites/${suiteId}/cases/${caseId}/toggle`, data)
