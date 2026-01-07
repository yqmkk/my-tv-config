import json, requests, time, os, re
from concurrent.futures import ThreadPoolExecutor

# 全网接口池
POOL_URLS = [
    "https://raw.githubusercontent.com/gaotianliuyun/gao/master/0827.json",
    "https://itvbox.top/tv",
    "http://cdn.qiaoji8.com/tvbox.json"
]

def check_speed(name, key, api):
    start_time = time.time()
    try:
        # 允许 10s 高延迟，保留重型带宽源
        res = requests.get(api, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        if res.status_code == 200:
            return (key, name, api, time.time() - start_time)
    except: pass
    return (key, name, api, 999) # 失败保底

def generate():
    all_raw = {}
    for url in POOL_URLS:
        try:
            r = requests.get(url, timeout=5)
            links = re.findall(r'"(https?://[^"]+/api\.php/provide/vod[^"]*)"', r.text)
            for i, link in enumerate(links):
                all_raw[f"auto_{hash(link)%10000}"] = [f"🚀 自动源_{i}", link]
        except: continue
    
    # 强制包含高带宽固定源
    all_raw["sn_4k"] = ["💎 索尼·4K重型", "https://suoniapi.com/api.php/provide/vod"]

    results = []
    with ThreadPoolExecutor(max_workers=30) as exe:
        futures = [exe.submit(check_speed, v[0], k, v[1]) for k, v in all_raw.items()]
        results = [f.result() for f in futures]
    
    # 排序并取前 50 个
    results.sort(key=lambda x: x[3])
    top_50 = results[:50]
    
    api_site = {r[0]: {"api": r[2], "name": f"{r[1]} | {int(r[3]*1000) if r[3]<999 else '极速线'}ms", "detail": r[2]} for r in top_50}
    config = {"cache_time": 9200, "api_site": api_site, "custom_category": [{"name": "全网急速·搜刮", "type": "movie", "query": "4K"}]}
    
    # 直接保存在根目录，方便 CDN 拉取
    with open("tv.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

if __name__ == "__main__": generate()
