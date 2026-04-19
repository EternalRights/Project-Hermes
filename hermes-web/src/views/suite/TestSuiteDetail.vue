<template>
  <div class="suite-detail">
    <div class="detail-header">
      <el-page-header @back="goBack" :content="suite.name || '套件详情'" />
      <div class="header-actions">
        <el-select v-model="selectedEnv" placeholder="选择环境" style="width: 180px; margin-right: 12px">
          <el-option v-for="env in environments" :key="env.id" :label="env.name" :value="env.id" />
        </el-select>
        <el-button type="primary" :disabled="!selectedEnv" @click="handleExecute">执行</el-button>
      </div>
    </div>

    <el-card class="info-card">
      <template #header><span>基本信息</span></template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="名称">{{ suite.name }}</el-descriptions-item>
        <el-descriptions-item label="描述">{{ suite.description || '-' }}</el-descriptions-item>
        <el-descriptions-item label="用例数">{{ suite.cases?.length || 0 }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ suite.createdAt }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card class="cases-card">
      <template #header>
        <div class="card-header">
          <span>用例列表</span>
          <el-button type="primary" size="small" @click="caseDialogVisible = true">添加用例</el-button>
        </div>
      </template>
      <el-table :data="suite.cases || []" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="用例名称" />
        <el-table-column prop="method" label="方法" width="80">
          <template #default="{ row }">
            <span :class="'method-' + row.method?.toLowerCase()">{{ row.method }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="url" label="URL" show-overflow-tooltip />
        <el-table-column label="启用" width="100">
          <template #default="{ row }">
            <el-switch
              :model-value="row.enabled"
              @change="handleToggleCase(row)"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button type="danger" link @click="handleRemoveCase(row)">移除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="caseDialogVisible" title="添加用例" width="700px">
      <el-input v-model="caseSearch" placeholder="搜索用例" style="margin-bottom: 12px" @input="fetchAvailableCases" />
      <el-table :data="availableCases" stripe max-height="400" @selection-change="handleCaseSelect">
        <el-table-column type="selection" width="50" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="用例名称" />
        <el-table-column prop="method" label="方法" width="80" />
        <el-table-column prop="url" label="URL" show-overflow-tooltip />
      </el-table>
      <template #footer>
        <el-button @click="caseDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleAddCases">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getTestSuite, addSuiteCase, removeSuiteCase, toggleSuiteCase } from '../../api/testSuites'
import { getTestCases } from '../../api/testCases'
import { createExecution } from '../../api/executions'
import { getEnvironments } from '../../api/environments'

const route = useRoute()
const router = useRouter()
const suiteId = route.params.id
const suite = ref({})
const environments = ref([])
const selectedEnv = ref('')
const caseDialogVisible = ref(false)
const caseSearch = ref('')
const availableCases = ref([])
const selectedCases = ref([])

const goBack = () => {
  router.push('/test-suites')
}

const fetchSuite = async () => {
  try {
    const res = await getTestSuite(suiteId)
    suite.value = res.data || {}
  } catch (error) {
    // ignore
  }
}

const fetchEnvironments = async () => {
  try {
    const res = await getEnvironments(suite.value.projectId, { page: 1, pageSize: 100 })
    environments.value = res.data?.list || []
  } catch (error) {
    // ignore
  }
}

const fetchAvailableCases = async () => {
  try {
    const res = await getTestCases({ keyword: caseSearch.value, page: 1, pageSize: 50 })
    availableCases.value = res.data?.list || []
  } catch (error) {
    // ignore
  }
}

const handleCaseSelect = (rows) => {
  selectedCases.value = rows
}

const handleAddCases = async () => {
  if (!selectedCases.value.length) {
    ElMessage.warning('请选择用例')
    return
  }
  try {
    const caseIds = selectedCases.value.map((c) => c.id)
    await addSuiteCase(suiteId, { caseIds })
    ElMessage.success('添加成功')
    caseDialogVisible.value = false
    fetchSuite()
  } catch (error) {
    // ignore
  }
}

const handleRemoveCase = async (row) => {
  try {
    await ElMessageBox.confirm(`确定移除用例「${row.name}」？`, '移除确认', { type: 'warning' })
    await removeSuiteCase(suiteId, row.id)
    ElMessage.success('移除成功')
    fetchSuite()
  } catch (error) {
    // ignore
  }
}

const handleToggleCase = async (row) => {
  try {
    await toggleSuiteCase(suiteId, row.id, { enabled: !row.enabled })
    fetchSuite()
  } catch (error) {
    // ignore
  }
}

const handleExecute = async () => {
  try {
    const res = await createExecution({ suiteId, environmentId: selectedEnv.value })
    ElMessage.success('执行已创建')
    router.push(`/executions/${res.data?.id}`)
  } catch (error) {
    // ignore
  }
}

onMounted(async () => {
  await fetchSuite()
  fetchEnvironments()
})
</script>

<style scoped>
.suite-detail {
  padding: 20px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.header-actions {
  display: flex;
  align-items: center;
}

.info-card {
  margin-bottom: 16px;
}

.cases-card {
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.method-get { color: #67c23a; }
.method-post { color: #409eff; }
.method-put { color: #e6a23c; }
.method-delete { color: #f56c6c; }
.method-patch { color: #909399; }
</style>
