import json, requests, time, os, re
from concurrent.futures import ThreadPoolExecutor

# 扩充后的全网顶级接口池（涵盖了目前市面上 90% 的源）
POOL_URLS = [
    "https://raw.githubusercontent.com/gaotianliuyun/gao/master/0827.json",
    "https://itvbox.top/tv",
    "http://cdn.qiaoji8.com/tvbox.json",
    "http://120.79.4.185/new.json",
    "https://ghproxy.com/https://raw.githubusercontent.com/ssili126/tv/main/itvbox.json",
    "http://meitv.top/itvbox.json",
    "https://pastebin.com/raw/gtVfs9wh",
    "https://any666.com/tvbox/m.json"
]

def check_source(name, api):
    """
    测速逻辑优化：
    1. 允许 12 秒的高延迟加载（为了保留那些服务器在海外的高带宽重型源）
    2. 只要能连通，就视为有效源
    """
    try:
        start = time.time()
        res = requests.get(api, timeout=12, headers={'User-Agent': 'Mozilla/5.0'})
        if res.status_code == 200:
            return {"name": name, "api": api, "delay": time.time() - start}
    except:
        pass
    return None

def generate():
    all_found = {}
    print("🚀 开始执行全网暴力搜刮...")
    
    # 1. 从接口池疯狂抓取
    for url in POOL_URLS:
        try:
            r = requests.get(url, timeout=8)
            # 使用更广的正则，匹配所有格式的 api.php/provide/vod
            links = re.findall(r'"(https?://[^"]+/api\.php/provide/vod[^"]*)"', r.text)
            for link in links:
                # 使用域名去重，防止重复
                domain = re.search(r'//([^/]+)', link).group(1)
                if domain not in all_found:
                    all_found[domain] = link
        except:
            continue
    
    print(f"📡 共搜寻到 {len(all_found)} 个潜在源，开始测速筛选...")

    # 2. 多线程并行测速（提速）
    valid_results = []
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(check_source, f"源_{i}", url) for i, url in enumerate(all_found.values())]
        for f in futures:
            res = f.result()
            if res:
                valid_results.append(res)

    # 3. 排序逻辑：优先保留延迟在 1s-8s 之间的“高延迟大带宽”源
    valid_results.sort(key=lambda x: x['delay'])
    
    # 4. 强制截取前 50-60 个，确保订阅列表内容充实
    final_list = valid_results[:60] 

    api_site = {}
    for i, item in enumerate(final_list):
        key = f"auto_source_{i}"
        api_site[key] = {
            "api": item['api'],
            "name": f"🚀 全网急速_{i+1} | {int(item['delay']*1000)}ms",
            "detail": item['api'].split('api.php')[0]
        }

    # 5. 生成 DecoTV 格式 JSON
    config = {
        "cache_time": 9200,
        "api_site": api_site,
        "custom_category": [
            {"name": "极速·4K重型源", "type": "movie", "query": "4K"},
            {"name": "全网搜刮精选", "type": "movie", "query": "华语"}
        ]
    }

    with open("tv.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    print(f"✅ 任务完成！已集成 {len(api_site)} 个优质地址到 tv.json")

if __name__ == "__main__":
    generate()
