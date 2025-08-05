import requests
import base64
import yaml
import os

def parse_ss_link(link):
    if not link.startswith("ss://"):
        return None
    # 移除 "ss://" 前缀
    encoded = link[len("ss://"):]
    # 处理包含 # 的部分（代理名称）
    if "#" in encoded:
        encoded = encoded.split("#")[0]
    try:
        # 解码 base64 编码的链接
        decoded = base64.b64decode(encoded + "==").decode('utf-8')  # 添加 padding
    except:
        return None
    # 分割为认证部分和主机端口部分
    parts = decoded.split("@")
    if len(parts) != 2:
        return None
    auth, hostport = parts
    # 分割主机和端口
    hp = hostport.split(":")
    if len(hp) != 2:
        return None
    server, port = hp
    try:
        port = int(port)
    except ValueError:
        return None
    # 分割认证部分
    a = auth.split(":")
    if len(a) < 2:
        return None
    method = a[0]
    password = ":".join(a[1:])
    return {
        "name": f"SS_{server.replace('.', '-')}_{port}",
        "type": "ss",
        "server": server,
        "port": port,
        "cipher": method,
        "password": password,
        "udp": True
    }

# 定义多个 Shadowsocks 链接来源
sources = [
    "https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub",
    "https://raw.githubusercontent.com/lagzian/SS-Collector/main/Shadowsocks.txt"
]

proxies = []
for url in sources:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        links = response.text.splitlines()
        for link in links:
            if link.startswith("ss://"):
                proxy = parse_ss_link(link)
                if proxy:
                    # 避免重复添加
                    if proxy not in proxies:
                        proxies.append(proxy)
    except requests.RequestException as e:
        print(f"从 {url} 获取链接失败: {e}")
        continue

# 生成 Clash 配置
config = {
    "proxies": proxies,
    "proxy-groups": [
        {
            "name": "🚀 节点选择",
            "type": "url-test",
            "url": "http://www.gstatic.com/generate_204",
            "interval": 300,
            "tolerance": 50,
            "proxies": [p["name"] for p in proxies]
        }
    ]
}

# 确保 docs 目录存在
os.makedirs("docs", exist_ok=True)

# 保存为 proxy.yaml
with open("docs/proxy.yaml", "w", encoding="utf-8") as f:
    yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

# 生成 base64 编码的 sub 文件
with open("docs/proxy.yaml", "rb") as f:
    content = f.read()
    b64 = base64.b64encode(content).decode("utf-8")

with open("docs/sub", "w", encoding="utf-8") as f:
    f.write(b64)

print(f"生成完成，共 {len(proxies)} 个节点")
