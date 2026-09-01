import { createRouter, createWebHistory } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../stores/user'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/shop' },
    { path: '/login', component: () => import('../views/Login.vue') },
    { path: '/shop', component: () => import('../views/Shop.vue') },
    { path: '/admin', component: () => import('../views/Admin.vue') },
  ],
})

// 路由守卫：没登录一律踢回 /login；非 admin 不能进 /admin
router.beforeEach((to) => {
  const user = useUserStore()
  if (to.path !== '/login' && !user.isLoggedIn) {
    return '/login'
  }
  if (to.path === '/admin' && !user.isAdmin) {
    ElMessage.warning('只有管理员能进入后台')
    return '/shop'
  }
})

export default router
