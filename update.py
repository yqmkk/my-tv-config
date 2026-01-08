import json, requests, time, os, re, base58
from concurrent.futures import ThreadPoolExecutor

# 极度扩张的接口池
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
    try:
        # 宽容测速：15秒。针对蓝光源优化
        res = requests.get(api, timeout=15, headers={'User-Agent': 'Mozilla/5.0'}, verify=False)
        if res.status_code == 200:
            return {"api": api, "name": name, "delay": res.elapsed.total_seconds()}
    except:
        pass
    return None

def generate():
    raw_links = set()
    print("正在搜刮全网资源，请稍后...")
    
    for url in POOL_URLS:
        try:
            r = requests.get(url, timeout=10, verify=False)
            # 兼容更多格式的正则
            found = re.findall(r'"(https?://[^"]+/api\.php/provide/vod[^"]*)"', r.text)
            for link in found:
                raw_links.add(link)
        except:
            continue
    
    print(f"找到潜在接口 {len(raw_links)} 个，开始筛选有效源...")

    valid_results = []
    with ThreadPoolExecutor(max_workers=50) as exe:
        futures = [exe.submit(check_source, f"源_{i}", url) for i, url in enumerate(list(raw_links))]
        for f in futures:
            res = f.result()
            if res:
                valid_results.append(res)
    
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

    # 符合 DecoTV 专用的嵌套 JSON 格式
    config = {
        "cache_time": 9200,
        "api_site": api_site,
        "custom_category": [
            { "name": "华语", "type": "movie", "query": "华语" },
            { "name": "4K重型", "type": "movie", "query": "4K" }
        ]
    }

    # 1. 保存为普通的 JSON 文件
    with open("tv.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    # 2. 核心修改：将刚才生成的 config 编码为 Base58
    compact_json = json.dumps(config, ensure_ascii=False).encode('utf-8')
    b58_encoded_text = base58.b58encode(compact_json).decode('utf-8')

    with open("deco_b58.txt", "w", encoding="utf-8") as f:
        f.write(b58_encoded_text)

    print(f"✅ 生成完成！")
    print(f"- tv.json (包含 {len(api_site)} 个源)")
    print(f"- deco_b58.txt (已完成 Base58 编码)")

if __name__ == "__main__":
    # 禁用不安全请求警告
    requests.packages.urllib3.disable_warnings()
    generate()
