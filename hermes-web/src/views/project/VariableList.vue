<template>
  <div class="variable-list">
    <div class="toolbar">
      <el-page-header @back="goBack" :content="'变量管理 - ' + projectName" />
      <el-button type="primary" @click="openDialog()">
        <el-icon><Plus /></el-icon>新建变量
      </el-button>
    </div>

    <el-table :data="variables" stripe v-loading="loading">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="key" label="变量名" />
      <el-table-column prop="value" label="变量值" show-overflow-tooltip />
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

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑变量' : '新建变量'" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="变量名" prop="key">
          <el-input v-model="form.key" placeholder="请输入变量名" />
        </el-form-item>
        <el-form-item label="变量值" prop="value">
          <el-input v-model="form.value" placeholder="请输入变量值" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="请输入描述" />
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
import { getVariables, createVariable, updateVariable, deleteVariable } from '../../api/variables'

const route = useRoute()
const router = useRouter()
const projectId = route.params.id
const projectName = ref('')
const loading = ref(false)
const submitting = ref(false)
const variables = ref([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const formRef = ref(null)

const form = reactive({
  key: '',
  value: '',
  description: '',
})

const rules = {
  key: [{ required: true, message: '请输入变量名', trigger: 'blur' }],
  value: [{ required: true, message: '请输入变量值', trigger: 'blur' }],
}

const goBack = () => {
  router.push('/projects')
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getVariables(projectId, { page: page.value, pageSize: pageSize.value })
    variables.value = res.data?.list || []
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
    form.key = row.key
    form.value = row.value
    form.description = row.description || ''
  } else {
    isEdit.value = false
    editId.value = null
    form.key = ''
    form.value = ''
    form.description = ''
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    if (isEdit.value) {
      await updateVariable(projectId, editId.value, form)
      ElMessage.success('更新成功')
    } else {
      await createVariable(projectId, form)
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
    await ElMessageBox.confirm(`确定删除变量「${row.key}」？`, '删除确认', { type: 'warning' })
    await deleteVariable(projectId, row.id)
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
.variable-list {
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
