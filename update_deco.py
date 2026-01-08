import json, requests, time, os, re, base58
from concurrent.futures import ThreadPoolExecutor

# 抓取池：2026年活跃的高吞吐量数据源
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
    """检测接口是否有效，宽容度设为 15 秒以保留高吞吐量蓝光源"""
    try:
        res = requests.get(api, timeout=15, headers={'User-Agent': 'Mozilla/5.0'}, verify=False)
        if res.status_code == 200:
            return {"api": api, "name": name, "delay": res.elapsed.total_seconds()}
    except:
        pass
    return None

def generate():
    raw_links = set()
    print("Step 1: 正在从全网搜刮接口...")
    
    for url in POOL_URLS:
        try:
            r = requests.get(url, timeout=10, verify=False)
            # 兼容正则匹配 API 接口
            found = re.findall(r'"(https?://[^"]+/api\.php/provide/vod[^"]*)"', r.text)
            for link in found:
                raw_links.add(link)
        except:
            continue
    
    print(f"找到潜在接口 {len(raw_links)} 个，开始并行检测...")

    valid_results = []
    with ThreadPoolExecutor(max_workers=50) as exe:
        futures = [exe.submit(check_source, f"源_{i}", url) for i, url in enumerate(list(raw_links))]
        for f in futures:
            res = f.result()
            if res:
                valid_results.append(res)
    
    # 按照响应速度排序，取前 80 个
    valid_results.sort(key=lambda x: x['delay'])
    final_list = valid_results[:80]

    api_site = {}
    for i, item in enumerate(final_list):
        key = f"api_{i+1}"
        api_site[key] = {
            "api": item['api'],
            "name": f"🚀 源_{i+1:02d} | {int(item['delay']*1000)}ms",
            "detail": item['api'].split('api.php')[0]
        }

    # 构造标准 DecoTV 嵌套格式
    config = {
        "cache_time": 9200,
        "api_site": api_site,
        "custom_category": [
            { "name": "华语精选", "type": "movie", "query": "华语" },
            { "name": "4K极清", "type": "movie", "query": "4K" }
        ]
    }

    # --- 保存 JSON 文件 ---
    with open("tv.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    print(f"✅ tv.json 已更新")

    # --- 生成 Base58 编码文件 ---
    # 直接使用当前内存中的 config 对象，确保数据一致
    compact_json = json.dumps(config, ensure_ascii=False).encode('utf-8')
    b58_text = base58.b58encode(compact_json).decode('utf-8')

    with open("deco_b58.txt", "w", encoding="utf-8") as f:
        f.write(b58_text)
    print("✅ deco_b58.txt 已更新")

if __name__ == "__main__":
    # 禁用 HTTPS 警告
    try:
        requests.packages.urllib3.disable_warnings()
    except:
        pass
    generate()
