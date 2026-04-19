<template>
  <div class="environment-list">
    <div class="toolbar">
      <el-page-header @back="goBack" :content="'环境管理 - ' + projectName" />
      <el-button type="primary" @click="openDialog()">
        <el-icon><Plus /></el-icon>新建环境
      </el-button>
    </div>

    <el-table :data="environments" stripe v-loading="loading">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="环境名称" />
      <el-table-column prop="baseUrl" label="基础URL" />
      <el-table-column prop="description" label="描述" show-overflow-tooltip />
      <el-table-column prop="createdAt" label="创建时间" width="180" />
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
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

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑环境' : '新建环境'" width="600px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入环境名称" />
        </el-form-item>
        <el-form-item label="基础URL" prop="baseUrl">
          <el-input v-model="form.baseUrl" placeholder="请输入基础URL" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="变量">
          <el-table :data="form.variables" border size="small">
            <el-table-column label="Key" width="200">
              <template #default="{ row }">
                <el-input v-model="row.key" placeholder="变量名" />
              </template>
            </el-table-column>
            <el-table-column label="Value">
              <template #default="{ row }">
                <el-input v-model="row.value" placeholder="变量值" />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="80">
              <template #default="{ $index }">
                <el-button type="danger" link @click="form.variables.splice($index, 1)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-button type="primary" link @click="form.variables.push({ key: '', value: '' })" style="margin-top: 8px">
            + 添加变量
          </el-button>
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
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getEnvironments, createEnvironment, updateEnvironment, deleteEnvironment } from '../../api/environments'

const route = useRoute()
const router = useRouter()
const projectId = route.params.id
const projectName = ref('')
const loading = ref(false)
const submitting = ref(false)
const environments = ref([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const formRef = ref(null)

const form = reactive({
  name: '',
  baseUrl: '',
  description: '',
  variables: [],
})

const rules = {
  name: [{ required: true, message: '请输入环境名称', trigger: 'blur' }],
  baseUrl: [{ required: true, message: '请输入基础URL', trigger: 'blur' }],
}

const goBack = () => {
  router.push('/projects')
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getEnvironments(projectId, { page: page.value, pageSize: pageSize.value })
    environments.value = res.data?.list || []
    total.value = res.data?.total || 0
    projectName.value = res.data?.projectName || ''
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
    form.baseUrl = row.baseUrl || ''
    form.description = row.description || ''
    form.variables = row.variables ? row.variables.map((v) => ({ ...v })) : []
  } else {
    isEdit.value = false
    editId.value = null
    form.name = ''
    form.baseUrl = ''
    form.description = ''
    form.variables = []
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    const payload = { ...form }
    if (isEdit.value) {
      await updateEnvironment(projectId, editId.value, payload)
      ElMessage.success('更新成功')
    } else {
      await createEnvironment(projectId, payload)
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
    await ElMessageBox.confirm(`确定删除环境「${row.name}」？`, '删除确认', { type: 'warning' })
    await deleteEnvironment(projectId, row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    // ignore
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.environment-list {
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
