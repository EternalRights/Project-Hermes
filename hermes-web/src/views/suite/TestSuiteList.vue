<template>
  <div class="suite-list">
    <div class="toolbar">
      <el-input
        v-model="keyword"
        placeholder="搜索套件"
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
        <el-icon><Plus /></el-icon>新建套件
      </el-button>
    </div>

    <el-table :data="suites" stripe v-loading="loading">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="套件名称" />
      <el-table-column prop="description" label="描述" show-overflow-tooltip />
      <el-table-column prop="caseCount" label="用例数" width="100" />
      <el-table-column prop="createdAt" label="创建时间" width="180" />
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="goDetail(row)">详情</el-button>
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

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑套件' : '新建套件'" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入套件名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入描述" />
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
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import { getTestSuites, createTestSuite, updateTestSuite, deleteTestSuite } from '../../api/testSuites'

const router = useRouter()
const loading = ref(false)
const submitting = ref(false)
const suites = ref([])
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
  description: '',
})

const rules = {
  name: [{ required: true, message: '请输入套件名称', trigger: 'blur' }],
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getTestSuites({ keyword: keyword.value, page: page.value, pageSize: pageSize.value })
    suites.value = res.data?.list || []
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
    form.description = row.description || ''
  } else {
    isEdit.value = false
    editId.value = null
    form.name = ''
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
      await updateTestSuite(editId.value, form)
      ElMessage.success('更新成功')
    } else {
      await createTestSuite(form)
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
    await ElMessageBox.confirm(`确定删除套件「${row.name}」？`, '删除确认', { type: 'warning' })
    await deleteTestSuite(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    // ignore
  }
}

const goDetail = (row) => {
  router.push(`/test-suites/${row.id}`)
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.suite-list {
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
