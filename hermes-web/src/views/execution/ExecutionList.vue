<template>
  <div class="execution-list">
    <div class="toolbar">
      <el-select v-model="status" placeholder="状态筛选" clearable style="width: 140px" @change="fetchData">
        <el-option label="运行中" value="running" />
        <el-option label="通过" value="passed" />
        <el-option label="失败" value="failed" />
        <el-option label="完成" value="completed" />
      </el-select>
    </div>

    <el-table :data="executions" stripe v-loading="loading">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="执行名称" />
      <el-table-column prop="suiteName" label="套件" />
      <el-table-column prop="environmentName" label="环境" width="120" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)">{{ statusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="passRate" label="通过率" width="100">
        <template #default="{ row }">
          <span>{{ row.passRate != null ? row.passRate + '%' : '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="startTime" label="开始时间" width="170" />
      <el-table-column prop="duration" label="耗时" width="100" />
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="goDetail(row)">详情</el-button>
          <el-button type="primary" link @click="goReport(row)" v-if="row.status !== 'running'">报告</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-model:current-page="page"
      v-model:page-size="pageSize"
      :total="total"
      :page-sizes="[10, 20, 50]"
      layout="total, sizes, prev, pager, next"
      class="pagination"
      @size-change="fetchData"
      @current-change="fetchData"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getExecutions } from '../../api/executions'

const router = useRouter()
const loading = ref(false)
const executions = ref([])
const status = ref('')
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

const statusType = (s) => {
  const map = { running: 'warning', passed: 'success', failed: 'danger', completed: 'info' }
  return map[s] || 'info'
}

const statusLabel = (s) => {
  const map = { running: '运行中', passed: '通过', failed: '失败', completed: '完成' }
  return map[s] || s
}

const fetchData = async () => {
  loading.value = true
  try {
    const params = { status: status.value, page: page.value, pageSize: pageSize.value }
    const res = await getExecutions(params)
    executions.value = res.data?.list || []
    total.value = res.data?.total || 0
  } catch (error) {
    // ignore
  } finally {
    loading.value = false
  }
}

const goDetail = (row) => {
  router.push(`/executions/${row.id}`)
}

const goReport = (row) => {
  router.push(`/reports/${row.id}`)
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.execution-list {
  padding: 20px;
}

.toolbar {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
