<template>
  <div class="report-view">
    <div class="report-header">
      <el-page-header @back="goBack" content="测试报告" />
      <el-button type="primary" @click="handleExport">导出报告</el-button>
    </div>

    <el-row :gutter="20" class="stat-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ report.totalCases || 0 }}</div>
            <div class="stat-label">总用例数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-value" style="color: #67c23a">{{ report.passedCases || 0 }}</div>
            <div class="stat-label">通过</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-value" style="color: #f56c6c">{{ report.failedCases || 0 }}</div>
            <div class="stat-label">失败</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-value" style="color: #e6a23c">{{ report.skippedCases || 0 }}</div>
            <div class="stat-label">跳过</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="progress-card">
      <template #header><span>通过率</span></template>
      <el-progress
        :percentage="report.passRate || 0"
        :color="progressColor"
        :stroke-width="20"
        :text-inside="true"
        style="margin-bottom: 12px"
      />
      <el-descriptions :column="3" border size="small">
        <el-descriptions-item label="执行耗时">{{ report.duration || '-' }}</el-descriptions-item>
        <el-descriptions-item label="开始时间">{{ report.startTime || '-' }}</el-descriptions-item>
        <el-descriptions-item label="结束时间">{{ report.endTime || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card class="steps-card">
      <template #header><span>步骤结果</span></template>
      <el-table :data="report.steps || []" stripe>
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
      </el-table>
    </el-card>

    <el-card class="failed-card" v-if="failedCases.length">
      <template #header><span>失败用例详情</span></template>
      <el-collapse>
        <el-collapse-item v-for="item in failedCases" :key="item.id" :title="item.caseName" :name="item.id">
          <el-descriptions :column="1" border size="small">
            <el-descriptions-item label="URL">{{ item.url }}</el-descriptions-item>
            <el-descriptions-item label="方法">{{ item.method }}</el-descriptions-item>
            <el-descriptions-item label="错误信息">
              <pre class="error-msg">{{ item.errorMessage }}</pre>
            </el-descriptions-item>
            <el-descriptions-item label="期望值">{{ item.expected || '-' }}</el-descriptions-item>
            <el-descriptions-item label="实际值">{{ item.actual || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-collapse-item>
      </el-collapse>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getReport, exportReport } from '../../api/reports'

const route = useRoute()
const router = useRouter()
const executionId = route.params.id
const report = ref({})

const failedCases = computed(() => {
  return (report.value.steps || []).filter((s) => s.status === 'failed')
})

const progressColor = computed(() => {
  const rate = report.value.passRate || 0
  if (rate >= 80) return '#67c23a'
  if (rate >= 50) return '#e6a23c'
  return '#f56c6c'
})

const statusType = (s) => {
  const map = { running: 'warning', passed: 'success', failed: 'danger', completed: 'info', skipped: 'info' }
  return map[s] || 'info'
}

const statusLabel = (s) => {
  const map = { running: '运行中', passed: '通过', failed: '失败', completed: '完成', skipped: '跳过' }
  return map[s] || s
}

const goBack = () => {
  router.push('/executions')
}

const fetchReport = async () => {
  try {
    const res = await getReport(executionId)
    report.value = res.data || {}
  } catch (error) {
    // ignore
  }
}

const handleExport = async () => {
  try {
    const res = await exportReport(executionId)
    const blob = new Blob([res], { type: 'application/pdf' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `report-${executionId}.pdf`
    link.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    // ignore
  }
}

onMounted(() => {
  fetchReport()
})
</script>

<style scoped>
.report-view {
  padding: 20px;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.stat-row {
  margin-bottom: 16px;
}

.stat-card :deep(.el-card__body) {
  text-align: center;
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

.progress-card {
  margin-bottom: 16px;
}

.steps-card {
  margin-bottom: 16px;
}

.failed-card {
  margin-bottom: 16px;
}

.error-msg {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
  font-size: 13px;
  color: #f56c6c;
}

.method-get { color: #67c23a; }
.method-post { color: #409eff; }
.method-put { color: #e6a23c; }
.method-delete { color: #f56c6c; }
.method-patch { color: #909399; }
</style>
