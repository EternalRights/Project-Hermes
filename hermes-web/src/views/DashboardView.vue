<template>
  <div class="dashboard-view">
    <el-row :gutter="20" class="stat-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ stats.todayExecutions }}</div>
            <div class="stat-label">今日执行次数</div>
          </div>
          <el-icon class="stat-icon" :size="48" color="#409eff"><VideoPlay /></el-icon>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ stats.passRate }}%</div>
            <div class="stat-label">通过率</div>
          </div>
          <el-icon class="stat-icon" :size="48" color="#67c23a"><CircleCheck /></el-icon>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ stats.activeCases }}</div>
            <div class="stat-label">活跃用例数</div>
          </div>
          <el-icon class="stat-icon" :size="48" color="#e6a23c"><Document /></el-icon>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ stats.activeSuites }}</div>
            <div class="stat-label">活跃套件数</div>
          </div>
          <el-icon class="stat-icon" :size="48" color="#f56c6c"><Files /></el-icon>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="recent-card">
      <template #header>
        <span>最近执行</span>
      </template>
      <el-table :data="recentExecutions" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="执行名称" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="passRate" label="通过率" width="120">
          <template #default="{ row }">
            <span>{{ row.passRate != null ? row.passRate + '%' : '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="startTime" label="开始时间" width="180" />
        <el-table-column prop="duration" label="耗时" width="120" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewDetail(row)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { VideoPlay, CircleCheck, Document, Files } from '@element-plus/icons-vue'
import { getExecutions } from '../api/executions'

const router = useRouter()

const stats = ref({
  todayExecutions: 0,
  passRate: 0,
  activeCases: 0,
  activeSuites: 0,
})

const recentExecutions = ref([])

const statusType = (status) => {
  const map = { running: 'warning', passed: 'success', failed: 'danger', completed: 'info' }
  return map[status] || 'info'
}

const statusLabel = (status) => {
  const map = { running: '运行中', passed: '通过', failed: '失败', completed: '完成' }
  return map[status] || status
}

const viewDetail = (row) => {
  router.push(`/executions/${row.id}`)
}

const fetchData = async () => {
  try {
    const res = await getExecutions({ page: 1, pageSize: 10 })
    recentExecutions.value = res.data?.list || []
    stats.value.todayExecutions = res.data?.todayExecutions || 0
    stats.value.passRate = res.data?.passRate || 0
    stats.value.activeCases = res.data?.activeCases || 0
    stats.value.activeSuites = res.data?.activeSuites || 0
  } catch (error) {
    // ignore
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.dashboard-view {
  padding: 20px;
}

.stat-row {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.stat-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.stat-icon {
  opacity: 0.8;
}

.recent-card {
  margin-top: 0;
}
</style>
