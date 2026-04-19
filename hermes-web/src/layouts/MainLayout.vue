<template>
  <el-container class="main-layout">
    <el-aside :width="isCollapsed ? '64px' : '220px'" class="aside">
      <div class="logo">
        <span v-if="!isCollapsed">Hermes</span>
        <span v-else>H</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapsed"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409eff"
      >
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <template #title>仪表盘</template>
        </el-menu-item>
        <el-menu-item index="/projects">
          <el-icon><Folder /></el-icon>
          <template #title>项目管理</template>
        </el-menu-item>
        <el-menu-item index="/test-cases">
          <el-icon><Document /></el-icon>
          <template #title>测试用例</template>
        </el-menu-item>
        <el-menu-item index="/test-suites">
          <el-icon><Files /></el-icon>
          <template #title>测试套件</template>
        </el-menu-item>
        <el-menu-item index="/executions">
          <el-icon><VideoPlay /></el-icon>
          <template #title>执行管理</template>
        </el-menu-item>
        <el-menu-item index="/scheduled-tasks">
          <el-icon><Timer /></el-icon>
          <template #title>定时任务</template>
        </el-menu-item>
        <el-menu-item index="/notifications">
          <el-icon><Bell /></el-icon>
          <template #title>通知配置</template>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="isCollapsed = !isCollapsed">
            <Fold v-if="!isCollapsed" />
            <Expand v-else />
          </el-icon>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-icon><User /></el-icon>
              <span class="username">{{ userStore.userInfo?.username || '用户' }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '../store/user'
import {
  Odometer,
  Folder,
  Document,
  Files,
  VideoPlay,
  Timer,
  Bell,
  User,
  Fold,
  Expand,
} from '@element-plus/icons-vue'

const route = useRoute()
const userStore = useUserStore()
const isCollapsed = ref(false)

const activeMenu = computed(() => {
  const path = route.path
  if (path.startsWith('/projects')) return '/projects'
  if (path.startsWith('/test-cases')) return '/test-cases'
  if (path.startsWith('/test-suites')) return '/test-suites'
  if (path.startsWith('/executions')) return '/executions'
  if (path.startsWith('/reports')) return '/executions'
  if (path.startsWith('/scheduled-tasks')) return '/scheduled-tasks'
  if (path.startsWith('/notifications')) return '/notifications'
  return path
})

const handleCommand = (command) => {
  if (command === 'logout') {
    userStore.logout()
  }
}
</script>

<style scoped>
.main-layout {
  min-height: 100vh;
}

.aside {
  background-color: #304156;
  transition: width 0.3s;
  overflow: hidden;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #409eff;
  font-size: 20px;
  font-weight: bold;
  background-color: #263445;
}

.el-menu {
  border-right: none;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
}

.collapse-btn {
  font-size: 20px;
  cursor: pointer;
  color: #606266;
}

.collapse-btn:hover {
  color: #409eff;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: #606266;
}

.user-info:hover {
  color: #409eff;
}

.username {
  margin-left: 6px;
  font-size: 14px;
}

.main-content {
  background-color: #f0f2f5;
  min-height: calc(100vh - 60px);
}
</style>
