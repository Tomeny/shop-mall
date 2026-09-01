import request from './request'

// ---------- 认证 ----------
export const apiRegister = (data) => request.post('/auth/register', data)
export const apiLogin = (data) => request.post('/auth/login', data)

// ---------- 商品浏览 ----------
export const apiListProducts = (keyword = '') =>
  request.get('/products', { params: { keyword } })

// ---------- 后台管理 ----------
export const apiAdminCreateProduct = (data) => request.post('/admin/products', data)
export const apiAdminUpdateProduct = (id, data) => request.put(`/admin/products/${id}`, data)
export const apiAdminDeleteProduct = (id) => request.delete(`/admin/products/${id}`)
export const apiAdminListUsers = () => request.get('/admin/users')
export const apiAdminResetPassword = (id, newPassword) =>
  request.put(`/admin/users/${id}/reset-password`, { new_password: newPassword })

// ---------- 图片上传 ----------
export const apiAdminUpload = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/admin/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
