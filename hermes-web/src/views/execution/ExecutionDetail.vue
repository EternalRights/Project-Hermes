<template>
  <div class="execution-detail">
    <div class="detail-header">
      <el-page-header @back="goBack" :content="'执行详情 #' + executionId" />
      <el-button type="primary" @click="goReport" v-if="execution.status !== 'running'">查看报告</el-button>
    </div>

    <el-card class="summary-card">
      <template #header><span>执行概要</span></template>
      <el-descriptions :column="4" border>
        <el-descriptions-item label="状态">
          <el-tag :type="statusType(execution.status)">{{ statusLabel(execution.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="通过率">
          <span>{{ execution.passRate != null ? execution.passRate + '%' : '-' }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="耗时">{{ execution.duration || '-' }}</el-descriptions-item>
        <el-descriptions-item label="环境">{{ execution.environmentName || '-' }}</el-descriptions-item>
        <el-descriptions-item label="套件">{{ execution.suiteName || '-' }}</el-descriptions-item>
        <el-descriptions-item label="开始时间">{{ execution.startTime || '-' }}</el-descriptions-item>
        <el-descriptions-item label="结束时间">{{ execution.endTime || '-' }}</el-descriptions-item>
        <el-descriptions-item label="总用例数">{{ execution.totalCases ?? '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card class="steps-card">
      <template #header><span>步骤结果</span></template>
      <el-table :data="execution.steps || []" stripe>
        <el-table-column prop="id" label="序号" width="80" />
        <el-table-column prop="caseName" label="用例名称" />
        <el-table-column prop="method" label="方法" width="80">
          <template #default="{ row }">
            <span :class="'method-' + row.method?.toLowerCase()">{{ row.method }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="url" label="URL" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="耗时" width="100" />
        <el-table-column prop="errorMessage" label="错误信息" show-overflow-tooltip />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getExecution } from '../../api/executions'

const route = useRoute()
const router = useRouter()
const executionId = route.params.id
const execution = ref({})

const statusType = (s) => {
  const map = { running: 'warning', passed: 'success', failed: 'danger', completed: 'info' }
  return map[s] || 'info'
}

const statusLabel = (s) => {
  const map = { running: '运行中', passed: '通过', failed: '失败', completed: '完成' }
  return map[s] || s
}

const goBack = () => {
  router.push('/executions')
}

const goReport = () => {
  router.push(`/reports/${executionId}`)
}

const fetchExecution = async () => {
  try {
    const res = await getExecution(executionId)
    execution.value = res.data || {}
  } catch (error) {
    // ignore
  }
}

onMounted(() => {
  fetchExecution()
})
</script>

<style scoped>
.execution-detail {
  padding: 20px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.summary-card {
  margin-bottom: 16px;
}

.steps-card {
  margin-bottom: 16px;
}

.method-get { color: #67c23a; }
.method-post { color: #409eff; }
.method-put { color: #e6a23c; }
.method-delete { color: #f56c6c; }
.method-patch { color: #909399; }
</style>
