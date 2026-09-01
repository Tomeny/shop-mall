# 奇迹商城（shop-mall）

Vue3 + FastAPI 前后端分离的商品城演示项目。

- **前端**：Vue 3 + Vite + Element Plus + Pinia + Vue Router + axios（端口 5173）
- **后端**：FastAPI + SQLAlchemy + PyMySQL（端口 8000）
- **数据库**：MySQL（首次启动自动建库 `shop_mall`、建表、灌种子数据）
- **鉴权**：JWT（Bearer token）+ bcrypt 密码哈希

## 功能

1. **登录/注册**：任意用户可注册账号并登录
2. **商品浏览**：登录后浏览/搜索上架商品
3. **后台管理**（仅管理员）：
   - 上架 / 编辑 / 下架商品
   - 查看注册用户列表（账号、角色、注册时间）
   - 帮用户重置密码（密码为 bcrypt 单向哈希，**任何人无法查看明文**）

演示账号：`admin / admin123`（管理员）

## 目录结构

```
shop-mall/
├── backend/
│   ├── main.py        # 入口：建库建表 + 注册路由
│   ├── config.py      # 读取 .env
│   ├── database.py    # engine / Session / get_db
│   ├── models.py      # users / products 表
│   ├── schemas.py     # Pydantic 出入参
│   ├── security.py    # bcrypt + JWT
│   ├── deps.py        # get_current_user → require_admin（Depends 链）
│   ├── seed.py        # 种子数据
│   └── routers/       # auth.py · products.py · admin.py
└── frontend/
    └── src/
        ├── api/       # axios 封装（自动带 token，401/403 弹错）
        ├── router/    # 路由守卫（未登录踢回 /login，非 admin 挡 /admin）
        ├── stores/    # Pinia 用户状态
        └── views/     # Login.vue · Shop.vue · Admin.vue
```

## 启动

### 0. 前置

- MySQL 已运行（默认 `127.0.0.1:3306`，root 密码写在 `backend/.env`）
- `.env` 已配置（首次部署参考 `backend/.env` 内容自行创建）

### 1. 后端

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

- 首次启动自动完成：建库 `shop_mall`（utf8mb4）→ 建表 → 写入 admin/演示商品
- 交互式 API 文档：http://127.0.0.1:8000/docs

### 2. 前端

```bash
cd frontend
npm install
npm run dev
```

打开 http://127.0.0.1:5173 ，用 `admin / admin123` 登录。

> Vite 已把 `/api` 代理到 `http://127.0.0.1:8000`，无跨域问题。

## API 一览

| 方法 | 路径 | 权限 | 说明 |
|---|---|---|---|
| POST | `/api/auth/register` | 公开 | 注册 |
| POST | `/api/auth/login` | 公开 | 登录，返回 JWT |
| GET | `/api/products` | 登录 | 商品列表（?keyword= 搜索） |
| GET | `/api/products/{id}` | 登录 | 商品详情 |
| POST | `/api/admin/products` | 管理员 | 上架商品 |
| PUT | `/api/admin/products/{id}` | 管理员 | 编辑商品 |
| DELETE | `/api/admin/products/{id}` | 管理员 | 下架商品 |
| GET | `/api/admin/users` | 管理员 | 用户列表 |
| PUT | `/api/admin/users/{id}/reset-password` | 管理员 | 重置用户密码 |

## 设计要点

- **Depends 子依赖链**：`get_current_user`（解析 JWT → 查库）→ `require_admin`（检查 role），路由只写 `Depends(require_admin)`，FastAPI 自动执行整条链
- **错误不静默**：前端 axios 拦截器统一弹出 401/403/4xx 提示；401 自动清 token 跳登录页
- **密码安全**：bcrypt 单向哈希入库，登录接口不区分"用户不存在/密码错误"，管理员只能重置不能查看
