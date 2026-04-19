<template>
  <div class="testcase-editor">
    <div class="editor-header">
      <el-page-header @back="goBack" content="用例编辑" />
      <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
    </div>

    <div class="editor-body">
      <el-card class="section-card">
        <template #header><span>基本信息</span></template>
        <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="名称" prop="name">
                <el-input v-model="form.name" placeholder="请输入用例名称" />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="模块" prop="module">
                <el-input v-model="form.module" placeholder="模块名" />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="优先级" prop="priority">
                <el-select v-model="form.priority" style="width: 100%">
                  <el-option label="P0" value="P0" />
                  <el-option label="P1" value="P1" />
                  <el-option label="P2" value="P2" />
                  <el-option label="P3" value="P3" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="标签">
            <el-select v-model="form.tags" multiple filterable allow-create placeholder="添加标签" style="width: 100%">
            </el-select>
          </el-form-item>
        </el-form>
      </el-card>

      <el-card class="section-card">
        <template #header><span>请求配置</span></template>
        <el-form label-width="80px">
          <el-row :gutter="20">
            <el-col :span="4">
              <el-form-item label="方法">
                <el-select v-model="form.method" style="width: 100%">
                  <el-option label="GET" value="GET" />
                  <el-option label="POST" value="POST" />
                  <el-option label="PUT" value="PUT" />
                  <el-option label="DELETE" value="DELETE" />
                  <el-option label="PATCH" value="PATCH" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="20">
              <el-form-item label="URL">
                <el-input v-model="form.url" placeholder="请输入请求URL" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-tabs v-model="requestTab">
            <el-tab-pane label="Headers" name="headers">
              <el-table :data="form.headers" border size="small">
                <el-table-column label="Key" width="200">
                  <template #default="{ row }">
                    <el-input v-model="row.key" placeholder="Header名" />
                  </template>
                </el-table-column>
                <el-table-column label="Value">
                  <template #default="{ row }">
                    <el-input v-model="row.value" placeholder="Header值" />
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="80">
                  <template #default="{ $index }">
                    <el-button type="danger" link @click="form.headers.splice($index, 1)">删除</el-button>
                  </template>
                </el-table-column>
              </el-table>
              <el-button type="primary" link @click="form.headers.push({ key: '', value: '' })" style="margin-top: 8px">+ 添加Header</el-button>
            </el-tab-pane>

            <el-tab-pane label="Params" name="params">
              <el-table :data="form.params" border size="small">
                <el-table-column label="Key" width="200">
                  <template #default="{ row }">
                    <el-input v-model="row.key" placeholder="参数名" />
                  </template>
                </el-table-column>
                <el-table-column label="Value">
                  <template #default="{ row }">
                    <el-input v-model="row.value" placeholder="参数值" />
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="80">
                  <template #default="{ $index }">
                    <el-button type="danger" link @click="form.params.splice($index, 1)">删除</el-button>
                  </template>
                </el-table-column>
              </el-table>
              <el-button type="primary" link @click="form.params.push({ key: '', value: '' })" style="margin-top: 8px">+ 添加Param</el-button>
            </el-tab-pane>

            <el-tab-pane label="Body" name="body">
              <el-select v-model="form.bodyType" style="margin-bottom: 12px">
                <el-option label="none" value="none" />
                <el-option label="JSON" value="json" />
                <el-option label="Form Data" value="form" />
                <el-option label="Raw" value="raw" />
              </el-select>
              <el-input
                v-if="form.bodyType === 'json' || form.bodyType === 'raw'"
                v-model="form.body"
                type="textarea"
                :rows="8"
                placeholder="请输入请求体"
              />
              <div v-if="form.bodyType === 'form'">
                <el-table :data="form.formData" border size="small">
                  <el-table-column label="Key" width="200">
                    <template #default="{ row }">
                      <el-input v-model="row.key" placeholder="字段名" />
                    </template>
                  </el-table-column>
                  <el-table-column label="Value">
                    <template #default="{ row }">
                      <el-input v-model="row.value" placeholder="字段值" />
                    </template>
                  </el-table-column>
                  <el-table-column label="操作" width="80">
                    <template #default="{ $index }">
                      <el-button type="danger" link @click="form.formData.splice($index, 1)">删除</el-button>
                    </template>
                  </el-table-column>
                </el-table>
                <el-button type="primary" link @click="form.formData.push({ key: '', value: '' })" style="margin-top: 8px">+ 添加字段</el-button>
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-form>
      </el-card>

      <el-card class="section-card">
        <template #header><span>断言配置</span></template>
        <el-table :data="form.assertions" border size="small">
          <el-table-column label="类型" width="140">
            <template #default="{ row }">
              <el-select v-model="row.type" placeholder="类型">
                <el-option label="状态码" value="status" />
                <el-option label="响应体" value="body" />
                <el-option label="Header" value="header" />
                <el-option label="响应时间" value="responseTime" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="路径/表达式" width="200">
            <template #default="{ row }">
              <el-input v-model="row.path" placeholder="如 $.data.id" />
            </template>
          </el-table-column>
          <el-table-column label="比较方式" width="140">
            <template #default="{ row }">
              <el-select v-model="row.comparator" placeholder="比较方式">
                <el-option label="等于" value="equals" />
                <el-option label="不等于" value="notEquals" />
                <el-option label="包含" value="contains" />
                <el-option label="大于" value="greaterThan" />
                <el-option label="小于" value="lessThan" />
                <el-option label="存在" value="exists" />
                <el-option label="不存在" value="notExists" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="期望值">
            <template #default="{ row }">
              <el-input v-model="row.expected" placeholder="期望值" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="80">
            <template #default="{ $index }">
              <el-button type="danger" link @click="form.assertions.splice($index, 1)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-button type="primary" link @click="form.assertions.push({ type: 'status', path: '', comparator: 'equals', expected: '' })" style="margin-top: 8px">+ 添加断言</el-button>
      </el-card>

      <el-card class="section-card">
        <template #header><span>参数化配置</span></template>
        <el-form label-width="80px">
          <el-form-item label="数据源">
            <el-select v-model="form.paramSource" placeholder="选择数据源" clearable style="width: 300px">
              <el-option label="手动输入" value="manual" />
              <el-option label="CSV文件" value="csv" />
            </el-select>
          </el-form-item>
          <el-form-item label="变量定义" v-if="form.paramSource === 'manual'">
            <el-table :data="form.paramVariables" border size="small">
              <el-table-column label="变量名" width="200">
                <template #default="{ row }">
                  <el-input v-model="row.name" placeholder="变量名" />
                </template>
              </el-table-column>
              <el-table-column label="值列表(逗号分隔)">
                <template #default="{ row }">
                  <el-input v-model="row.values" placeholder="值1,值2,值3" />
                </template>
              </el-table-column>
              <el-table-column label="操作" width="80">
                <template #default="{ $index }">
                  <el-button type="danger" link @click="form.paramVariables.splice($index, 1)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
            <el-button type="primary" link @click="form.paramVariables.push({ name: '', values: '' })" style="margin-top: 8px">+ 添加变量</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <el-card class="section-card">
        <template #header><span>钩子配置</span></template>
        <el-form label-width="80px">
          <el-form-item label="前置脚本">
            <el-input v-model="form.preScript" type="textarea" :rows="4" placeholder="前置脚本（JavaScript）" />
          </el-form-item>
          <el-form-item label="后置脚本">
            <el-input v-model="form.postScript" type="textarea" :rows="4" placeholder="后置脚本（JavaScript）" />
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getTestCase, createTestCase, updateTestCase } from '../../api/testCases'

const route = useRoute()
const router = useRouter()
const caseId = route.params.id !== 'new' ? route.params.id : null
const saving = ref(false)
const requestTab = ref('headers')
const formRef = ref(null)

const form = reactive({
  name: '',
  module: '',
  priority: 'P2',
  tags: [],
  method: 'GET',
  url: '',
  headers: [],
  params: [],
  bodyType: 'none',
  body: '',
  formData: [],
  assertions: [],
  paramSource: '',
  paramVariables: [],
  preScript: '',
  postScript: '',
})

const rules = {
  name: [{ required: true, message: '请输入用例名称', trigger: 'blur' }],
  url: [{ required: true, message: '请输入请求URL', trigger: 'blur' }],
}

const goBack = () => {
  router.push('/test-cases')
}

const fetchCase = async () => {
  if (!caseId) return
  try {
    const res = await getTestCase(caseId)
    const data = res.data
    Object.assign(form, {
      name: data.name || '',
      module: data.module || '',
      priority: data.priority || 'P2',
      tags: data.tags || [],
      method: data.method || 'GET',
      url: data.url || '',
      headers: data.headers || [],
      params: data.params || [],
      bodyType: data.bodyType || 'none',
      body: data.body || '',
      formData: data.formData || [],
      assertions: data.assertions || [],
      paramSource: data.paramSource || '',
      paramVariables: data.paramVariables || [],
      preScript: data.preScript || '',
      postScript: data.postScript || '',
    })
  } catch (error) {
    // ignore
  }
}

const handleSave = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    if (caseId) {
      await updateTestCase(caseId, form)
      ElMessage.success('保存成功')
    } else {
      await createTestCase(form)
      ElMessage.success('创建成功')
      router.push('/test-cases')
    }
  } catch (error) {
    // ignore
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  fetchCase()
})
</script>

<style scoped>
.testcase-editor {
  padding: 20px;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.editor-body {
  max-width: 1200px;
}

.section-card {
  margin-bottom: 16px;
}
</style>
