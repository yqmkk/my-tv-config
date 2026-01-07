import json, requests, time, os, re
from concurrent.futures import ThreadPoolExecutor

# 极度扩张的接口池，涵盖了目前全网最活跃的资源站
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
        # 宽容测速：允许 15 秒加载时间。很多蓝光源握手慢，但只要连通了，拖动就飞快。
        res = requests.get(api, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
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
            r = requests.get(url, timeout=10)
            # 使用更宽的正则匹配所有 api.php/provide/vod 接口
            found = re.findall(r'"(https?://[^"]+/api\.php/provide/vod[^"]*)"', r.text)
            for link in found:
                raw_links.add(link)
        except:
            continue
    
    print(f"找到潜在接口 {len(raw_links)} 个，开始筛选有效源...")

    # 多线程并行检测
    valid_results = []
    with ThreadPoolExecutor(max_workers=50) as exe:
        futures = [exe.submit(check_source, f"源_{i}", url) for i, url in enumerate(list(raw_links))]
        for f in futures:
            res = f.result()
            if res:
                valid_results.append(res)
    
    # 按照响应速度排序，但保留前 80 个（哪怕稍微慢点的也要，为了凑够数）
    valid_results.sort(key=lambda x: x['delay'])
    final_list = valid_results[:80] # 设定上限为 80 个，确保订阅非常丰富

    api_site = {}
    for i, item in enumerate(final_list):
        key = f"auto_{i}"
        api_site[key] = {
            "api": item['api'],
            "name": f"🚀 极速源_{i+1:02d} | {int(item['delay']*1000)}ms",
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

    # 写入文件
    with open("tv.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    print(f"✅ 生成完成！当前 tv.json 包含 {len(api_site)} 个有效源。")

if __name__ == "__main__":
    generate()
