<template>
  <div class="testcase-list">
    <div class="content-wrapper">
      <div class="left-panel">
        <el-tree
          :data="treeData"
          :props="treeProps"
          node-key="id"
          highlight-current
          default-expand-all
          @node-click="handleNodeClick"
        >
          <template #default="{ node, data }">
            <span class="tree-node">
              <el-icon v-if="data.type === 'project'"><Folder /></el-icon>
              <el-icon v-else><Document /></el-icon>
              <span>{{ node.label }}</span>
            </span>
          </template>
        </el-tree>
      </div>

      <div class="right-panel">
        <div class="toolbar">
          <div class="toolbar-left">
            <el-input
              v-model="keyword"
              placeholder="搜索用例"
              clearable
              style="width: 200px"
              @clear="fetchCases"
              @keyup.enter="fetchCases"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-select v-model="priority" placeholder="优先级" clearable style="width: 120px" @change="fetchCases">
              <el-option label="P0" value="P0" />
              <el-option label="P1" value="P1" />
              <el-option label="P2" value="P2" />
              <el-option label="P3" value="P3" />
            </el-select>
          </div>
          <div class="toolbar-right">
            <el-button type="primary" @click="goEditor()">
              <el-icon><Plus /></el-icon>新建用例
            </el-button>
            <el-button @click="handleBatchDelete" :disabled="!selectedIds.length">批量删除</el-button>
          </div>
        </div>

        <el-table :data="testCases" stripe v-loading="loading" @selection-change="handleSelectionChange">
          <el-table-column type="selection" width="50" />
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="name" label="用例名称" show-overflow-tooltip />
          <el-table-column prop="module" label="模块" width="120" />
          <el-table-column prop="priority" label="优先级" width="80">
            <template #default="{ row }">
              <el-tag :type="priorityType(row.priority)" size="small">{{ row.priority }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="method" label="方法" width="80">
            <template #default="{ row }">
              <span :class="'method-' + row.method?.toLowerCase()">{{ row.method }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="url" label="URL" show-overflow-tooltip />
          <el-table-column prop="updatedAt" label="更新时间" width="160" />
          <el-table-column label="操作" width="220" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="goEditor(row.id)">编辑</el-button>
              <el-button type="primary" link @click="handleCopy(row)">复制</el-button>
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
          @size-change="fetchCases"
          @current-change="fetchCases"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus, Folder, Document } from '@element-plus/icons-vue'
import { getTestCases, deleteTestCase, copyTestCase, getModules } from '../../api/testCases'
import { getProjects } from '../../api/projects'

const router = useRouter()
const loading = ref(false)
const testCases = ref([])
const treeData = ref([])
const keyword = ref('')
const priority = ref('')
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const selectedIds = ref([])
const currentModule = ref('')

const treeProps = {
  children: 'children',
  label: 'name',
}

const priorityType = (p) => {
  const map = { P0: 'danger', P1: 'warning', P2: '', P3: 'info' }
  return map[p] || 'info'
}

const handleNodeClick = (data) => {
  if (data.type === 'project') {
    currentModule.value = ''
  } else {
    currentModule.value = data.name
  }
  page.value = 1
  fetchCases()
}

const handleSelectionChange = (rows) => {
  selectedIds.value = rows.map((r) => r.id)
}

const fetchTree = async () => {
  try {
    const projectRes = await getProjects({ page: 1, pageSize: 100 })
    const projects = projectRes.data?.list || []
    const tree = []
    for (const project of projects) {
      const node = { id: 'project-' + project.id, name: project.name, type: 'project', projectId: project.id, children: [] }
      try {
        const moduleRes = await getModules(project.id)
        const modules = moduleRes.data || []
        node.children = modules.map((m) => ({
          id: 'module-' + project.id + '-' + m,
          name: m,
          type: 'module',
          projectId: project.id,
        }))
      } catch (e) {
        // ignore
      }
      tree.push(node)
    }
    treeData.value = tree
  } catch (error) {
    // ignore
  }
}

const fetchCases = async () => {
  loading.value = true
  try {
    const params = { keyword: keyword.value, priority: priority.value, module: currentModule.value, page: page.value, pageSize: pageSize.value }
    const res = await getTestCases(params)
    testCases.value = res.data?.list || []
    total.value = res.data?.total || 0
  } catch (error) {
    // ignore
  } finally {
    loading.value = false
  }
}

const goEditor = (id) => {
  if (id) {
    router.push(`/test-cases/${id}/edit`)
  } else {
    router.push('/test-cases/new/edit')
  }
}

const handleCopy = async (row) => {
  try {
    await copyTestCase(row.id)
    ElMessage.success('复制成功')
    fetchCases()
  } catch (error) {
    // ignore
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除用例「${row.name}」？`, '删除确认', { type: 'warning' })
    await deleteTestCase(row.id)
    ElMessage.success('删除成功')
    fetchCases()
  } catch (error) {
    // ignore
  }
}

const handleBatchDelete = async () => {
  try {
    await ElMessageBox.confirm(`确定删除选中的 ${selectedIds.value.length} 条用例？`, '批量删除', { type: 'warning' })
    for (const id of selectedIds.value) {
      await deleteTestCase(id)
    }
    ElMessage.success('批量删除成功')
    fetchCases()
  } catch (error) {
    // ignore
  }
}

onMounted(() => {
  fetchTree()
  fetchCases()
})
</script>

<style scoped>
.testcase-list {
  padding: 20px;
  height: calc(100vh - 100px);
}

.content-wrapper {
  display: flex;
  gap: 16px;
  height: 100%;
}

.left-panel {
  width: 240px;
  background: #fff;
  border-radius: 4px;
  padding: 12px;
  overflow-y: auto;
  flex-shrink: 0;
}

.right-panel {
  flex: 1;
  background: #fff;
  border-radius: 4px;
  padding: 16px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.toolbar-left {
  display: flex;
  gap: 12px;
}

.toolbar-right {
  display: flex;
  gap: 8px;
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
}

.pagination {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}

.method-get { color: #67c23a; }
.method-post { color: #409eff; }
.method-put { color: #e6a23c; }
.method-delete { color: #f56c6c; }
.method-patch { color: #909399; }
</style>
