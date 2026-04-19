import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../layouts/MainLayout.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/dashboard',
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/DashboardView.vue'),
      },
      {
        path: 'projects',
        name: 'ProjectList',
        component: () => import('../views/project/ProjectList.vue'),
      },
      {
        path: 'projects/:id/environments',
        name: 'EnvironmentList',
        component: () => import('../views/project/EnvironmentList.vue'),
      },
      {
        path: 'projects/:id/variables',
        name: 'VariableList',
        component: () => import('../views/project/VariableList.vue'),
      },
      {
        path: 'test-cases',
        name: 'TestCaseList',
        component: () => import('../views/testcase/TestCaseList.vue'),
      },
      {
        path: 'test-cases/:id/edit',
        name: 'TestCaseEditor',
        component: () => import('../views/testcase/TestCaseEditor.vue'),
      },
      {
        path: 'test-suites',
        name: 'TestSuiteList',
        component: () => import('../views/suite/TestSuiteList.vue'),
      },
      {
        path: 'test-suites/:id',
        name: 'TestSuiteDetail',
        component: () => import('../views/suite/TestSuiteDetail.vue'),
      },
      {
        path: 'executions',
        name: 'ExecutionList',
        component: () => import('../views/execution/ExecutionList.vue'),
      },
      {
        path: 'executions/:id',
        name: 'ExecutionDetail',
        component: () => import('../views/execution/ExecutionDetail.vue'),
      },
      {
        path: 'reports/:id',
        name: 'ReportView',
        component: () => import('../views/report/ReportView.vue'),
      },
      {
        path: 'scheduled-tasks',
        name: 'ScheduledTaskList',
        component: () => import('../views/scheduled/ScheduledTaskList.vue'),
      },
      {
        path: 'notifications',
        name: 'NotificationList',
        component: () => import('../views/notification/NotificationList.vue'),
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.matched.some((record) => record.meta.requiresAuth !== false)) {
    if (!token) {
      next({ path: '/login', query: { redirect: to.fullPath } })
    } else {
      next()
    }
  } else {
    if (token && to.path === '/login') {
      next({ path: '/dashboard' })
    } else {
      next()
    }
  }
})

export default router
