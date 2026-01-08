import json, requests, time, os, re, base58
from concurrent.futures import ThreadPoolExecutor

# 1. 极度扩张的接口池
POOL_URLS = [
    "https://raw.githubusercontent.com/gaotianliuyun/gao/master/0827.json",
    "https://itvbox.top/tv",
    "http://cdn.qiaoji8.com/tvbox.json",
    "http://bbk.888tv.tv/itvbox.json",
    "http://meitv.top/itvbox.json",
    "http://120.79.4.185/new.json",
    "https://ghproxy.com/https://raw.githubusercontent.com/ssili126/tv/main/itvbox.json",
    "https://raw.githubusercontent.com/FongMi/Release/main/levon.json",
    "http://home.jundie.top:81/top98.json",
    "https://t-v.me/tv.json",
    "http://pandown.pro/tvbox/m.json"
]

def check_source(name, api):
    """检测源是否通畅"""
    try:
        # 针对 115/蓝光源，放宽到 15 秒超时
        res = requests.get(api, timeout=15, headers={'User-Agent': 'Mozilla/5.0'}, verify=False)
        if res.status_code == 200:
            return {"api": api, "name": name, "delay": res.elapsed.total_seconds()}
    except:
        pass
    return None

def generate():
    """主生成函数"""
    raw_links = set()
    print("开始从全网聚合地址抓取接口...")
    
    for url in POOL_URLS:
        try:
            r = requests.get(url, timeout=10, verify=False)
            # 提取符合 CMS 接口特征的链接
            found = re.findall(r'"(https?://[^"]+/api\.php/provide/vod[^"]*)"', r.text)
            for link in found:
                raw_links.add(link)
        except:
            continue
    
    print(f"搜刮到 {len(raw_links)} 个潜在接口，正在并行测速...")

    valid_results = []
    # 使用 50 线程并行检测
    with ThreadPoolExecutor(max_workers=50) as exe:
        futures = [exe.submit(check_source, f"源_{i}", url) for i, url in enumerate(list(raw_links))]
        for f in futures:
            res = f.result()
            if res:
                valid_results.append(res)
    
    # 排序：按延迟排序
    valid_results.sort(key=lambda x: x['delay'])
    # 取前 80 个最稳的站
    final_list = valid_results[:80] 

    api_site = {}
    for i, item in enumerate(final_list):
        key = f"api_{i+1}"
        api_site[key] = {
            "api": item['api'],
            "name": f"🚀 源_{i+1:02d} | {int(item['delay']*1000)}ms",
            "detail": item['api'].split('api.php')[0]
        }

    # 构造符合 DecoTV 专用格式的配置对象
    config = {
        "cache_time": 9200,
        "api_site": api_site,
        "custom_category": [
            { "name": "华语", "type": "movie", "query": "华语" },
            { "name": "4K重型", "type": "movie", "query": "4K" }
        ]
    }

    # --- 输出流程 ---

    # 1. 保存原始 JSON
    with open("tv.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    print(f"✅ 已生成 tv.json (包含 {len(api_site)} 个源)")
    
    # 2. 核心：将 config 字典转换为 Base58 编码
    # 先序列化成紧凑的字符串，再编码
    json_bytes = json.dumps(config, ensure_ascii=False).encode('utf-8')
    b58_text = base58.b58encode(json_bytes).decode('utf-8')

    with open("deco_b58.txt", "w", encoding="utf-8") as f:
        f.write(b58_text)
    print("✅ 已生成 deco_b58.txt (Base58 编码完成)")

if __name__ == "__main__":
    # 禁用 HTTPS 警告（防止脚本因某些源证书问题中断）
    try:
        requests.packages.urllib3.disable_warnings()
    except:
        pass
    generate()
