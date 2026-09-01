<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { apiListProducts, apiBuyProduct } from '../api'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const products = ref([])
const search = reactive({ keyword: '' })

async function loadProducts() {
  loading.value = true
  try {
    const list = await apiListProducts(search.keyword)
    // 每个商品补一个购买数量（默认 1），供数量选择器使用
    products.value = list.map((p) => ({ ...p, quantity: 1 }))
  } catch {
    // 错误提示已在 axios 拦截器统一弹出
  } finally {
    loading.value = false
  }
}

function doSearch() {
  loadProducts()
}

async function handleBuy(product) {
  if (product.stock <= 0) {
    ElMessage.warning('该商品已售罄')
    return
  }
  const qty = product.quantity || 1
  try {
    await ElMessageBox.confirm(
      `确定购买「${product.name}」× ${qty} 件（合计 ¥${(Number(product.price) * qty).toFixed(2)}）？`,
      '确认购买',
      { type: 'info' },
    )
  } catch {
    return // 用户点了取消
  }
  try {
    const res = await apiBuyProduct(product.id, qty)
    ElMessage.success(`购买成功，剩余库存 ${res.stock} 件 🎉`)
    await loadProducts() // 刷新，库存数字立即更新
  } catch {
    // 错误提示已在 axios 拦截器统一弹出
  }
}

function handleLogout() {
  userStore.logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}

onMounted(loadProducts)
</script>

<template>
  <div class="shop-page">
    <header class="header">
      <div class="header-left">
        <h1>奇迹商城</h1>
        <span class="slogan">精选好物，等你带走</span>
      </div>
      <div class="header-right">
        <el-input
          v-model="search.keyword"
          placeholder="搜索商品"
          clearable
          style="width: 240px"
          @keyup.enter="doSearch"
          @clear="doSearch"
        >
          <template #append>
            <el-button @click="doSearch">搜索</el-button>
          </template>
        </el-input>
        <el-button v-if="userStore.isAdmin" type="warning" @click="router.push('/admin')">
          后台管理
        </el-button>
        <el-dropdown>
          <span class="user-chip">👤 {{ userStore.username }}</span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </header>

    <main v-loading="loading" class="product-grid">
      <el-empty v-if="!loading && products.length === 0" description="暂无商品" />
      <el-card v-for="p in products" :key="p.id" class="product-card" shadow="hover">
        <div class="product-image">
          <img v-if="p.image_url" :src="p.image_url" :alt="p.name" />
          <div v-else class="product-image-empty">暂无图片</div>
        </div>
        <div class="product-name">{{ p.name }}</div>
        <div class="product-desc">{{ p.description || '暂无介绍' }}</div>
        <div class="product-footer">
          <span class="price">¥{{ Number(p.price).toFixed(2) }}</span>
          <el-tag :type="p.stock > 0 ? 'success' : 'danger'" size="small">
            {{ p.stock > 0 ? `库存 ${p.stock}` : '已售罄' }}
          </el-tag>
        </div>
        <div class="buy-row">
          <el-input-number
            v-model="p.quantity"
            :min="1"
            :max="p.stock"
            size="small"
            style="width: 90px"
          />
          <el-button
            type="primary"
            :disabled="p.stock <= 0"
            @click="handleBuy(p)"
          >
            购买
          </el-button>
        </div>
      </el-card>
    </main>
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
  position: sticky;
  top: 0;
  z-index: 10;
}

.header-left h1 {
  font-size: 20px;
  color: #409eff;
  display: inline;
  margin-right: 12px;
}

.slogan {
  color: #909399;
  font-size: 13px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-chip {
  cursor: pointer;
  color: #606266;
  font-size: 14px;
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 20px;
  padding: 24px 32px;
  min-height: 60vh;
}

.product-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-image {
  width: 100%;
  height: 160px;
  margin-bottom: 12px;
  border-radius: 6px;
  overflow: hidden;
  background: #f5f7fa;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.product-image-empty {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #c0c4cc;
  font-size: 13px;
}

.product-desc {
  font-size: 13px;
  color: #909399;
  height: 36px;
  line-height: 18px;
  overflow: hidden;
}

.product-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}

.price {
  color: #f56c6c;
  font-size: 20px;
  font-weight: 700;
}

.buy-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
}

.buy-row .el-button {
  flex: 1;
}
</style>
