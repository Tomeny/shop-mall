import { defineStore } from 'pinia'
import { apiLogin } from '../api'
import { TOKEN_KEY } from '../api/request'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem(TOKEN_KEY) || '',
    username: localStorage.getItem('shop_mall_username') || '',
    role: localStorage.getItem('shop_mall_role') || '',
  }),
  getters: {
    isLoggedIn: (state) => !!state.token,
    isAdmin: (state) => state.role === 'admin',
  },
  actions: {
    async login(username, password) {
      const data = await apiLogin({ username, password })
      this.token = data.token
      this.username = data.username
      this.role = data.role
      localStorage.setItem(TOKEN_KEY, data.token)
      localStorage.setItem('shop_mall_username', data.username)
      localStorage.setItem('shop_mall_role', data.role)
    },
    logout() {
      this.token = ''
      this.username = ''
      this.role = ''
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem('shop_mall_username')
      localStorage.removeItem('shop_mall_role')
    },
  },
})
