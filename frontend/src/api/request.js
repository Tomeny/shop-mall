import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'

const TOKEN_KEY = 'shop_mall_token'

/**
 * 统一 axios 封装：
 * - 请求拦截器：自动带 Authorization: Bearer <token>
 * - 响应拦截器：所有错误都弹提示，绝不静默吞掉
 */
const request = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

request.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    let message = '网络异常，请稍后重试'
    if (error.response) {
      const status = error.response.status
      const detail = error.response.data?.detail
      if (status === 401) {
        message = detail || '请先登录'
        // 登录失效：清掉本地 token 并跳回登录页
        localStorage.removeItem(TOKEN_KEY)
        if (router.currentRoute.value.path !== '/login') {
          router.push('/login')
        }
      } else if (status === 403) {
        message = detail || '没有权限执行该操作'
      } else {
        message = detail || `请求失败（${status}）`
      }
    }
    ElMessage.error(message)
    return Promise.reject(new Error(message))
  },
)

export { TOKEN_KEY }
export default request
