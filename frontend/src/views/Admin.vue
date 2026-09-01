<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  apiListProducts,
  apiAdminCreateProduct,
  apiAdminUpdateProduct,
  apiAdminDeleteProduct,
  apiAdminListUsers,
  apiAdminResetPassword,
  apiAdminUpload,
} from '../api'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()

const activeTab = ref('products')

// ---------- 商品管理 ----------
const products = ref([])
const productsLoading = ref(false)
const dialogVisible = ref(false)
const editingId = ref(null) // null = 新增，非 null = 编辑
const productFormRef = ref()
const productForm = reactive({ name: '', price: null, stock: 0, description: '', image_url: '' })
const uploading = ref(false)

const productRules = {
  name: [{ required: true, message: '请输入商品名', trigger: 'blur' }],
  price: [
    { required: true, message: '请输入价格', trigger: 'blur' },
    { type: 'number', message: '价格必须是数字', trigger: 'blur' },
  ],
  stock: [{ type: 'number', message: '库存必须是数字', trigger: 'blur' }],
}

async function loadProducts() {
  productsLoading.value = true
  try {
    products.value = await apiListProducts()
  } catch {
    // 错误提示已在 axios 拦截器统一弹出
  } finally {
    productsLoading.value = false
  }
}

function openCreate() {
  editingId.value = null
  Object.assign(productForm, { name: '', price: null, stock: 0, description: '', image_url: '' })
  dialogVisible.value = true
}

function openEdit(row) {
  editingId.value = row.id
  Object.assign(productForm, {
    name: row.name,
    price: Number(row.price),
    stock: row.stock,
    description: row.description,
    image_url: row.image_url,
  })
  dialogVisible.value = true
}

// el-upload 的自定义上传：走 axios 封装（自动带 token）
async function handleUpload(options) {
  uploading.value = true
  try {
    const res = await apiAdminUpload(options.file)
    productForm.image_url = res.url
    ElMessage.success('图片上传成功')
  } catch {
    // 错误提示已在 axios 拦截器统一弹出
  } finally {
    uploading.value = false
  }
}

async function submitProduct() {
  await productFormRef.value.validate()
  try {
    if (editingId.value === null) {
      await apiAdminCreateProduct({ ...productForm })
      ElMessage.success('上架成功')
    } else {
      await apiAdminUpdateProduct(editingId.value, { ...productForm })
      ElMessage.success('修改成功')
    }
    dialogVisible.value = false
    loadProducts()
  } catch {
    // 错误提示已在 axios 拦截器统一弹出
  }
}

async function handleDelete(row) {
  await ElMessageBox.confirm(`确定下架「${row.name}」？`, '警告', { type: 'warning' })
  try {
    await apiAdminDeleteProduct(row.id)
    ElMessage.success('已下架')
    loadProducts()
  } catch {
    // 错误提示已在 axios 拦截器统一弹出
  }
}

// ---------- 用户管理 ----------
const users = ref([])
const usersLoading = ref(false)
const resetDialogVisible = ref(false)
const resetTarget = ref(null)
const newPassword = ref('')
const resetFormRef = ref()
const resetRules = {
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 位', trigger: 'blur' },
  ],
}

async function loadUsers() {
  usersLoading.value = true
  try {
    users.value = await apiAdminListUsers()
  } catch {
    // 错误提示已在 axios 拦截器统一弹出
  } finally {
    usersLoading.value = false
  }
}

function openReset(row) {
  resetTarget.value = row
  newPassword.value = ''
  resetDialogVisible.value = true
}

async function submitReset() {
  await resetFormRef.value.validate()
  try {
    await apiAdminResetPassword(resetTarget.value.id, newPassword.value)
    ElMessage.success(`用户 ${resetTarget.value.username} 的密码已重置`)
    resetDialogVisible.value = false
  } catch {
    // 错误提示已在 axios 拦截器统一弹出
  }
}

function handleLogout() {
  userStore.logout()
  router.push('/login')
}

onMounted(() => {
  loadProducts()
  loadUsers()
})
</script>

<template>
  <div class="admin-page">
    <header class="header">
      <h1>后台管理</h1>
      <div>
        <el-button @click="router.push('/shop')">回到商城</el-button>
        <el-button type="danger" plain @click="handleLogout">退出登录</el-button>
      </div>
    </header>

    <el-tabs v-model="activeTab" class="tabs">
      <el-tab-pane label="商品管理" name="products">
        <div class="toolbar">
          <el-button type="primary" @click="openCreate">上架商品</el-button>
        </div>
        <el-table :data="products" v-loading="productsLoading" border stripe>
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="name" label="商品名" min-width="160" />
          <el-table-column label="价格" width="110">
            <template #default="{ row }">¥{{ Number(row.price).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column prop="stock" label="库存" width="80" />
          <el-table-column prop="description" label="描述" min-width="180" show-overflow-tooltip />
          <el-table-column label="操作" width="160" fixed="right">
            <template #default="{ row }">
              <el-button size="small" @click="openEdit(row)">编辑</el-button>
              <el-button size="small" type="danger" @click="handleDelete(row)">下架</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="用户管理" name="users">
        <el-alert
          type="info"
          :closable="false"
          title="密码使用 bcrypt 单向哈希存储，无法查看明文；忘记密码请使用「重置密码」"
          style="margin-bottom: 16px"
        />
        <el-table :data="users" v-loading="usersLoading" border stripe>
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="username" label="账号" min-width="140" />
          <el-table-column label="角色" width="100">
            <template #default="{ row }">
              <el-tag :type="row.role === 'admin' ? 'danger' : 'info'">
                {{ row.role === 'admin' ? '管理员' : '普通用户' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="注册时间" width="180">
            <template #default="{ row }">
              {{ new Date(row.created_at).toLocaleString('zh-CN') }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="130" fixed="right">
            <template #default="{ row }">
              <el-button
                size="small"
                type="warning"
                :disabled="row.role === 'admin'"
                @click="openReset(row)"
              >
                重置密码
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- 商品 新增/编辑 弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingId === null ? '上架商品' : `编辑商品 #${editingId}`"
      width="480px"
    >
      <el-form ref="productFormRef" :model="productForm" :rules="productRules" label-width="80px">
        <el-form-item label="商品名" prop="name">
          <el-input v-model="productForm.name" />
        </el-form-item>
        <el-form-item label="价格(¥)" prop="price">
          <el-input-number v-model="productForm.price" :precision="2" :min="0.01" style="width: 100%" />
        </el-form-item>
        <el-form-item label="库存" prop="stock">
          <el-input-number v-model="productForm.stock" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="productForm.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="商品图片">
          <el-upload
            :show-file-list="false"
            :http-request="handleUpload"
            accept="image/*"
          >
            <div v-if="productForm.image_url" class="upload-preview">
              <img :src="productForm.image_url" alt="商品图" />
              <div class="upload-mask">点击更换</div>
            </div>
            <el-button v-else :loading="uploading">+ 上传图片</el-button>
          </el-upload>
          <el-button
            v-if="productForm.image_url"
            size="small"
            text
            type="danger"
            style="margin-left: 12px"
            @click="productForm.image_url = ''"
          >
            移除图片
          </el-button>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitProduct">保存</el-button>
      </template>
    </el-dialog>

    <!-- 重置密码 弹窗 -->
    <el-dialog v-model="resetDialogVisible" :title="`重置密码：${resetTarget?.username || ''}`" width="420px">
      <el-form ref="resetFormRef" :model="{ newPassword }" :rules="{ ...resetRules }" label-width="90px">
        <el-form-item label="新密码" prop="newPassword">
          <el-input v-model="newPassword" type="password" show-password placeholder="至少 6 位" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resetDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitReset">确认重置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 32px;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.header h1 {
  font-size: 20px;
  color: #e6a23c;
}

.tabs {
  padding: 16px 32px;
}

.toolbar {
  margin-bottom: 16px;
}

.upload-preview {
  position: relative;
  width: 120px;
  height: 120px;
  border: 1px dashed #dcdfe6;
  border-radius: 6px;
  overflow: hidden;
  cursor: pointer;
}

.upload-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.upload-mask {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 4px 0;
  text-align: center;
  font-size: 12px;
  color: #fff;
  background: rgba(0, 0, 0, 0.5);
  opacity: 0;
  transition: opacity 0.2s;
}

.upload-preview:hover .upload-mask {
  opacity: 1;
}
</style>
