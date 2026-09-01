"""图片上传链路自测：上传 → 静态访问 → 上架带图商品 → 商城返回图片 URL。"""
import json
import urllib.request
import urllib.error
import uuid

BASE = "http://127.0.0.1:8000"


def call(method, path, body=None, token=None, raw=False, headers=None):
    _headers = dict(headers or {})
    data = None
    if token:
        _headers["Authorization"] = f"Bearer {token}"
    if body is not None and not raw:
        data = json.dumps(body).encode("utf-8")
        _headers["Content-Type"] = "application/json"
    elif raw:
        data = body
    req = urllib.request.Request(BASE + path, data=data, headers=_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read()
            try:
                return json.loads(content)
            except Exception:
                return content
    except urllib.error.HTTPError as e:
        print(f"  [HTTP {e.code}] {e.read().decode('utf-8', 'ignore')}")
        raise


# 1. admin 登录
print("1. admin 登录")
login = call("POST", "/api/auth/login", {"username": "admin", "password": "admin123"})
TOKEN = login["token"]
print("   token ok")

# 2. 构造一张最小 PNG 并上传
print("2. 上传图片")
png = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
    "0000000d4944415478da63f8cf500f0003e001c2000018a8f75b0d0000000049454e44ae426082"
)
boundary = "----wb" + uuid.uuid4().hex
body = (
    b"--" + boundary.encode() +
    b'\r\nContent-Disposition: form-data; name="file"; filename="test.png"\r\n'
    b"Content-Type: image/png\r\n\r\n" + png +
    b"\r\n--" + boundary.encode() + b"--\r\n"
)
res = call("POST", "/api/admin/upload", body=body,
           token=TOKEN, raw=True, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
url = res["url"]
print(f"   返回 url: {url}")

# 3. 静态访问该图片
print("3. 静态访问图片")
req = urllib.request.Request(BASE + url)
with urllib.request.urlopen(req, timeout=30) as resp:
    got = resp.read()
print(f"   状态 {resp.status}, 字节数 {len(got)}, 与上传一致: {got == png}")

# 4. 上架带图商品
print("4. 上架带图商品")
p = call("POST", "/api/admin/products", {
    "name": "自测-带图商品", "price": 9.9, "stock": 3,
    "description": "验证图片上传", "image_url": url,
}, token=TOKEN)
print(f"   商品 id={p['id']} image_url={p['image_url']}")

# 5. 商城列表确认能取到图片
print("5. 商城列表")
products = call("GET", "/api/products", token=TOKEN)
hit = [x for x in products if x["id"] == p["id"]][0]
print(f"   商城返回该商品 image_url={hit['image_url']}")

# 6. 清理测试商品
print("6. 清理测试商品")
call("DELETE", f"/api/admin/products/{p['id']}", token=TOKEN)
print("   已删除")

print("\n全部通过 ✅")
