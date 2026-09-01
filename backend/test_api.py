"""shop-mall 后端接口自测脚本：直接对 http://127.0.0.1:8000 跑全链路。"""
import json
import urllib.request
import urllib.error
from urllib.parse import quote

BASE = "http://127.0.0.1:8000"


def call(method, path, body=None, token=None, expect=None):
    req = urllib.request.Request(
        BASE + quote(path, safe="/?&="),
        data=json.dumps(body).encode() if body is not None else None,
        headers={
            "Content-Type": "application/json",
            **({"Authorization": f"Bearer {token}"} if token else {}),
        },
        method=method,
    )
    try:
        with urllib.request.urlopen(req) as resp:
            status, data = resp.status, resp.read()
    except urllib.error.HTTPError as e:
        status, data = e.code, e.read()
    parsed = json.loads(data) if data else None
    ok = expect is None or status == expect
    print(f"{'PASS' if ok else 'FAIL'}  {method:6} {path:40} -> {status} (期望 {expect})")
    if not ok:
        print("      响应:", parsed)
        raise SystemExit(1)
    return parsed


print("== 认证链路 ==")
call("POST", "/api/auth/login", {"username": "admin", "password": "admin123"}, expect=200)
admin = call("POST", "/api/auth/login", {"username": "admin", "password": "admin123"}, expect=200)
ADMIN = admin["token"]
assert admin["role"] == "admin", "admin 角色错误"

call("POST", "/api/auth/login", {"username": "admin", "password": "wrong"}, expect=401)
call("GET", "/api/products", expect=401)  # 无 token

reg = call("POST", "/api/auth/register", {"username": "oky", "password": "123456"}, expect=None)
if reg and reg.get("detail") == "用户名已被注册":
    print("PASS  POST   /api/auth/register                       -> 400（已注册，幂等跳过）")
else:
    assert reg is not None and "注册成功" in reg.get("message", ""), f"注册失败: {reg}"
    print("PASS  POST   /api/auth/register                       -> 201")
call("POST", "/api/auth/register", {"username": "oky", "password": "123456"}, expect=400)
# oky 的密码可能被上一轮自测重置过，两个都试
oky = None
for pwd in ("123456", "abcdef"):
    oky = call("POST", "/api/auth/login", {"username": "oky", "password": pwd}, expect=None)
    if oky and "token" in oky:
        print(f"PASS  POST   /api/auth/login                        -> 200（密码 {pwd}）")
        break
assert oky and "token" in oky, "oky 无法登录"
OKY = oky["token"]
assert oky["role"] == "user"

print("== 权限分支 ==")
call("GET", "/api/admin/users", token=OKY, expect=403)  # 普通用户 -> 403

print("== 商品链路 ==")
products = call("GET", "/api/products", token=OKY, expect=200)
print(f"      共 {len(products)} 件商品在架")
new = call("POST", "/api/admin/products", {
    "name": "自测商品-鼠标垫", "price": 49.9, "stock": 10, "description": "自测上架",
}, token=ADMIN, expect=201)
pid = new["id"]
call("GET", f"/api/products/{pid}", token=OKY, expect=200)
call("PUT", f"/api/admin/products/{pid}", {"price": 39.9}, token=ADMIN, expect=200)
call("GET", f"/api/products/{pid}", token=OKY, expect=200)
search = call("GET", "/api/products?keyword=自测", token=OKY, expect=200)
assert any(p["id"] == pid for p in search), "搜索没搜到自测商品"
call("DELETE", f"/api/admin/products/{pid}", token=ADMIN, expect=200)
call("GET", f"/api/products/{pid}", token=OKY, expect=404)

print("== 用户管理链路 ==")
users = call("GET", "/api/admin/users", token=ADMIN, expect=200)
assert all("password" not in k for u in users for k in u), "用户列表泄露了密码相关字段"
print(f"      共 {len(users)} 个用户:", [u["username"] for u in users])
oky_id = next(u["id"] for u in users if u["username"] == "oky")
call("PUT", f"/api/admin/users/{oky_id}/reset-password",
     {"new_password": "abcdef"}, token=ADMIN, expect=200)
# 重置后旧密码失效、新密码可登录
call("POST", "/api/auth/login", {"username": "oky", "password": "123456"}, expect=401)
call("POST", "/api/auth/login", {"username": "oky", "password": "abcdef"}, expect=200)

print("\n全部通过 ✅")
