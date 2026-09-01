"""购买链路自测：验证购买后库存自动减少 + 库存不足拦截。"""
import json
import time
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
    print(f"{'PASS' if ok else 'FAIL'}  {method:6} {path:44} -> {status} (期望 {expect})")
    if not ok:
        print("      响应:", parsed)
        raise SystemExit(1)
    return parsed


# 1. 登录 admin + 普通用户 oky
admin = call("POST", "/api/auth/login", {"username": "admin", "password": "admin123"}, expect=200)
ADMIN = admin["token"]

oky = call("POST", "/api/auth/login", {"username": "oky", "password": "abcdef"}, expect=200)
OKY = oky["token"]

# 2. 管理员上架一件库存 5 的商品
new = call("POST", "/api/admin/products", {
    "name": "购买自测-库存扣减", "price": 10.0, "stock": 5, "description": "自测",
}, token=ADMIN, expect=201)
pid = new["id"]
print(f"      新建商品 #{pid}，初始库存 5")

# 3. 普通用户购买 2 件 -> 库存应变为 3
r = call("POST", f"/api/products/{pid}/buy", {"quantity": 2}, token=OKY, expect=200)
assert r["stock"] == 3, f"购买后库存应为 3，实际 {r['stock']}"
print(f"      购买 2 件后剩余库存 = {r['stock']} ✓")

# 4. 再买 3 件 -> 库存变 0
r = call("POST", f"/api/products/{pid}/buy", {"quantity": 3}, token=OKY, expect=200)
assert r["stock"] == 0, f"购买后库存应为 0，实际 {r['stock']}"
print(f"      再买 3 件后剩余库存 = {r['stock']} ✓")

# 5. 再买 1 件 -> 库存不足，应 400
call("POST", f"/api/products/{pid}/buy", {"quantity": 1}, token=OKY, expect=400)

# 6. 未登录购买 -> 401
call("POST", f"/api/products/{pid}/buy", {"quantity": 1}, expect=401)

# 7. 商品详情应反映库存 0
detail = call("GET", f"/api/products/{pid}", token=OKY, expect=200)
assert detail["stock"] == 0, f"详情库存应为 0，实际 {detail['stock']}"
print(f"      详情接口库存 = {detail['stock']} ✓")

# 8. 清理：下架自测商品
call("DELETE", f"/api/admin/products/{pid}", token=ADMIN, expect=200)

print("\n购买链路全部通过 ✅")
