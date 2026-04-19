<template>
  <div class="notification-list">
    <div class="toolbar">
      <el-input
        v-model="keyword"
        placeholder="搜索通知配置"
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
        <el-icon><Plus /></el-icon>新建通知
      </el-button>
    </div>

    <el-table :data="notifications" stripe v-loading="loading">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="type" label="类型" width="120">
        <template #default="{ row }">
          <el-tag size="small">{{ typeLabel(row.type) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="webhook" label="Webhook/地址" show-overflow-tooltip />
      <el-table-column prop="enabled" label="启用" width="80">
        <template #default="{ row }">
          <el-tag :type="row.enabled ? 'success' : 'info'" size="small">{{ row.enabled ? '是' : '否' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="createdAt" label="创建时间" width="170" />
      <el-table-column label="操作" width="260" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="handleTest(row)">测试</el-button>
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

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑通知' : '新建通知'" width="550px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入通知名称" />
        </el-form-item>
        <el-form-item label="类型" prop="type">
          <el-select v-model="form.type" placeholder="请选择类型" style="width: 100%">
            <el-option label="钉钉" value="dingtalk" />
            <el-option label="企业微信" value="wechat" />
            <el-option label="飞书" value="feishu" />
            <el-option label="邮件" value="email" />
            <el-option label="Webhook" value="webhook" />
          </el-select>
        </el-form-item>
        <el-form-item label="Webhook" prop="webhook" v-if="form.type !== 'email'">
          <el-input v-model="form.webhook" placeholder="请输入Webhook地址" />
        </el-form-item>
        <el-form-item label="收件人" prop="recipients" v-if="form.type === 'email'">
          <el-input v-model="form.recipients" placeholder="多个邮箱用逗号分隔" />
        </el-form-item>
        <el-form-item label="SMTP服务器" v-if="form.type === 'email'">
          <el-input v-model="form.smtpServer" placeholder="SMTP服务器地址" />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="form.enabled" />
        </el-form-item>
        <el-form-item label="触发事件">
          <el-checkbox-group v-model="form.events">
            <el-checkbox label="execution_completed" value="execution_completed">执行完成</el-checkbox>
            <el-checkbox label="execution_failed" value="execution_failed">执行失败</el-checkbox>
            <el-checkbox label="scheduled_task_failed" value="scheduled_task_failed">定时任务失败</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import {
  getNotifications,
  createNotification,
  updateNotification,
  deleteNotification,
  testNotification,
} from '../../api/notifications'

const loading = ref(false)
const submitting = ref(false)
const notifications = ref([])
const keyword = ref('')
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const formRef = ref(null)

const form = reactive({
  name: '',
  type: 'dingtalk',
  webhook: '',
  recipients: '',
  smtpServer: '',
  enabled: true,
  events: ['execution_failed'],
})

const rules = {
  name: [{ required: true, message: '请输入通知名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择类型', trigger: 'change' }],
  webhook: [{ required: true, message: '请输入Webhook地址', trigger: 'blur' }],
}

const typeLabel = (type) => {
  const map = { dingtalk: '钉钉', wechat: '企业微信', feishu: '飞书', email: '邮件', webhook: 'Webhook' }
  return map[type] || type
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getNotifications({ keyword: keyword.value, page: page.value, pageSize: pageSize.value })
    notifications.value = res.data?.list || []
    total.value = res.data?.total || 0
  } catch (error) {
    // ignore
  } finally {
    loading.value = false
  }
}

const openDialog = (row) => {
  if (row) {
    isEdit.value = true
    editId.value = row.id
    form.name = row.name
    form.type = row.type
    form.webhook = row.webhook || ''
    form.recipients = row.recipients || ''
    form.smtpServer = row.smtpServer || ''
    form.enabled = row.enabled
    form.events = row.events || []
  } else {
    isEdit.value = false
    editId.value = null
    form.name = ''
    form.type = 'dingtalk'
    form.webhook = ''
    form.recipients = ''
    form.smtpServer = ''
    form.enabled = true
    form.events = ['execution_failed']
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    if (isEdit.value) {
      await updateNotification(editId.value, form)
      ElMessage.success('更新成功')
    } else {
      await createNotification(form)
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
    await ElMessageBox.confirm(`确定删除通知「${row.name}」？`, '删除确认', { type: 'warning' })
    await deleteNotification(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    // ignore
  }
}

const handleTest = async (row) => {
  try {
    await testNotification(row.id)
    ElMessage.success('测试通知已发送')
  } catch (error) {
    // ignore
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.notification-list {
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
