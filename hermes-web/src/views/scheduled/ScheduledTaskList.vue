<template>
  <div class="scheduled-task-list">
    <div class="toolbar">
      <el-input
        v-model="keyword"
        placeholder="搜索定时任务"
        clearable
        style="width: 240px"
        @clear="fetchData"
        @keyup.enter="fetchData"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <el-button type="primary" @click="openDialog()">
        <el-icon><Plus /></el-icon>新建定时任务
      </el-button>
    </div>

    <el-table :data="tasks" stripe v-loading="loading">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="任务名称" />
      <el-table-column prop="suiteName" label="关联套件" />
      <el-table-column prop="cronExpression" label="Cron表达式" width="140" />
      <el-table-column prop="environmentName" label="执行环境" width="120" />
      <el-table-column prop="enabled" label="状态" width="100">
        <template #default="{ row }">
          <el-switch :model-value="row.enabled" @change="handleToggle(row)" />
        </template>
      </el-table-column>
      <el-table-column prop="lastRunTime" label="上次执行" width="170" />
      <el-table-column prop="nextRunTime" label="下次执行" width="170" />
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="viewHistory(row)">历史</el-button>
          <el-button type="primary" link @click="openDialog(row)">编辑</el-button>
          <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
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

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑定时任务' : '新建定时任务'" width="550px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="任务名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入任务名称" />
        </el-form-item>
        <el-form-item label="关联套件" prop="suiteId">
          <el-select v-model="form.suiteId" placeholder="请选择套件" style="width: 100%">
            <el-option v-for="s in suiteOptions" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="执行环境" prop="environmentId">
          <el-select v-model="form.environmentId" placeholder="请选择环境" style="width: 100%">
            <el-option v-for="e in envOptions" :key="e.id" :label="e.name" :value="e.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Cron表达式" prop="cronExpression">
          <el-input v-model="form.cronExpression" placeholder="如: 0 0 8 * * ?">
            <template #append>
              <el-tooltip content="秒 分 时 日 月 周" placement="top">
                <el-icon><QuestionFilled /></el-icon>
              </el-tooltip>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="form.enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="historyVisible" title="执行历史" width="700px">
      <el-table :data="history" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="passRate" label="通过率" width="100">
          <template #default="{ row }">
            <span>{{ row.passRate != null ? row.passRate + '%' : '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="startTime" label="执行时间" />
        <el-table-column prop="duration" label="耗时" width="100" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus, QuestionFilled } from '@element-plus/icons-vue'
import {
  getScheduledTasks,
  createScheduledTask,
  updateScheduledTask,
  deleteScheduledTask,
  toggleScheduledTask,
  getScheduledTaskHistory,
} from '../../api/scheduledTasks'
import { getTestSuites } from '../../api/testSuites'
import { getEnvironments } from '../../api/environments'

const loading = ref(false)
const submitting = ref(false)
const tasks = ref([])
const keyword = ref('')
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const dialogVisible = ref(false)
const historyVisible = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const formRef = ref(null)
const suiteOptions = ref([])
const envOptions = ref([])
const history = ref([])

const form = reactive({
  name: '',
  suiteId: '',
  environmentId: '',
  cronExpression: '',
  enabled: true,
})

const rules = {
  name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
  suiteId: [{ required: true, message: '请选择套件', trigger: 'change' }],
  environmentId: [{ required: true, message: '请选择环境', trigger: 'change' }],
  cronExpression: [{ required: true, message: '请输入Cron表达式', trigger: 'blur' }],
}

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
    const res = await getScheduledTasks({ keyword: keyword.value, page: page.value, pageSize: pageSize.value })
    tasks.value = res.data?.list || []
    total.value = res.data?.total || 0
  } catch (error) {
    // ignore
  } finally {
    loading.value = false
  }
}

const fetchOptions = async () => {
  try {
    const [suiteRes, envRes] = await Promise.all([
      getTestSuites({ page: 1, pageSize: 100 }),
      getEnvironments('', { page: 1, pageSize: 100 }).catch(() => ({ data: { list: [] } })),
    ])
    suiteOptions.value = suiteRes.data?.list || []
    envOptions.value = envRes.data?.list || []
  } catch (error) {
    // ignore
  }
}

const openDialog = (row) => {
  if (row) {
    isEdit.value = true
    editId.value = row.id
    form.name = row.name
    form.suiteId = row.suiteId
    form.environmentId = row.environmentId
    form.cronExpression = row.cronExpression
    form.enabled = row.enabled
  } else {
    isEdit.value = false
    editId.value = null
    form.name = ''
    form.suiteId = ''
    form.environmentId = ''
    form.cronExpression = ''
    form.enabled = true
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    if (isEdit.value) {
      await updateScheduledTask(editId.value, form)
      ElMessage.success('更新成功')
    } else {
      await createScheduledTask(form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch (error) {
    // ignore
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除定时任务「${row.name}」？`, '删除确认', { type: 'warning' })
    await deleteScheduledTask(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    // ignore
  }
}

const handleToggle = async (row) => {
  try {
    await toggleScheduledTask(row.id, { enabled: !row.enabled })
    fetchData()
  } catch (error) {
    // ignore
  }
}

const viewHistory = async (row) => {
  try {
    const res = await getScheduledTaskHistory(row.id)
    history.value = res.data || []
    historyVisible.value = true
  } catch (error) {
    // ignore
  }
}

onMounted(() => {
  fetchData()
  fetchOptions()
})
</script>

<style scoped>
.scheduled-task-list {
  padding: 20px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
