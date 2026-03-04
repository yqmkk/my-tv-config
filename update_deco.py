import json, requests, time, os, re, base58
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

# 1. 锁定“高延迟但高带宽”的大厂重型源 (115/4K 核心)
WHITELIST = [
    {"api": "https://cj.lziapi.com/api.php/provide/vod", "name": "💎量子4K(重型)"},
    {"api": "https://api.ffzyapi.com/api.php/provide/vod", "name": "💎非凡直连(重型)"},
    {"api": "https://jszyapi.com/api.php/provide/vod", "name": "💎极速资源"},
    {"api": "https://api.guangsuapi.com/api.php/provide/vod", "name": "💎光速蓝光"},
    {"api": "https://suoniapi.com/api.php/provide/vod", "name": "💎索尼直连"},
    {"api": "https://bfzyapi.com/api.php/provide/vod", "name": "💎暴风高清"},
    {"api": "https://api.1080zyku.com/inc/api_mac10.php", "name": "💎1080P重型"},
    {"api": "https://api.kkzy.tv/api.php/provide/vod", "name": "💎快看直连"},
    {"api": "https://api.tianyiapi.com/api.php/provide/vod", "name": "💎天翼影视"},
    {"api": "https://api.123zy.com/api.php/provide/vod", "name": "💎123高带宽"},
    {"api": "https://dbzy.tv/api.php/provide/vod", "name": "💎豆瓣电影"},
    {"api": "https://www.605zy.cc/api.php/provide/vod", "name": "💎605直连"}
]

POOL_URLS = [
    "https://raw.githubusercontent.com/gaotianliuyun/gao/master/0827.json",
    "https://itvbox.top/tv",
    "http://cdn.qiaoji8.com/tvbox.json",
    "https://raw.liucn.cc/box/m.json",
    "http://120.79.4.185/new.json"
]

def check_source(name, api):
    try:
        # 允许长达 20 秒的连接时间，专门为了捕捉你截图里那种 1500ms+ 的优质重型源
        start_time = time.time()
        res = requests.get(api, timeout=20, headers={'User-Agent': 'Mozilla/5.0'}, verify=False)
        if res.status_code == 200 and ("vod" in res.text or "total" in res.text):
            delay = (time.time() - start_time)
            return {"api": api, "name": name, "delay": delay}
    except:
        pass
    return None

def generate():
    raw_links = []
    for item in WHITELIST:
        raw_links.append((item['name'], item['api']))
    
    print("正在搜刮潜在接口...")
    for url in POOL_URLS:
        try:
            r = requests.get(url, timeout=10, verify=False)
            matches = re.findall(r'"name"\s*:\s*"([^"]+)"[^}]+"(https?://[^"]+/api\.php/[^"]+)"', r.text)
            for m_name, m_api in matches:
                raw_links.append((m_name, m_api))
        except:
            continue
    
    # 域名去重
    unique_dict = {}
    for name, api in raw_links:
        domain = urlparse(api).netloc
        if domain not in unique_dict:
            unique_dict[domain] = {"name": name, "api": api}
    
    print(f"开始对 {len(unique_dict)} 个独立域名进行深度扫描...")

    valid_results = []
    with ThreadPoolExecutor(max_workers=50) as exe:
        futures = [exe.submit(check_source, v['name'], v['api']) for v in unique_dict.values()]
        for f in futures:
            res = f.result()
            if res:
                valid_results.append(res)
    
    # 核心策略：不再单纯按延迟排！
    # 1. 带有 💎 的白名单强制最前
    # 2. 延迟在 1s-3s 之间的源（通常是优质直连站）也赋予较高优先级
    def sort_strategy(x):
        priority = 0
        if "💎" in x['name']: priority = -10
        elif 0.8 < x['delay'] < 3.0: priority = -5 # 你喜欢的“高延迟”优质源
        return (priority, x['delay'])

    valid_results.sort(key=sort_strategy)
    final_list = valid_results[:100] # 扩容到 100 个

    api_site = {}
    for i, item in enumerate(final_list):
        clean_name = re.sub(r'\(.*?\)|\[.*?\]|资源|采集', '', item['name']).strip()
        key = f"api_{i+1}"
        api_site[key] = {
            "api": item['api'],
            "name": f"{clean_name} | {int(item['delay']*1000)}ms",
            "detail": item['api'].split('api.php')[0]
        }

    config = {
        "cache_time": 9200,
        "api_site": api_site,
        "custom_category": [
            { "name": "🎞️ 重型蓝光专区", "type": "movie", "query": "115" },
            { "name": "📺 华语精选", "type": "movie", "query": "华语" }
        ]
    }

    # 写入文件
    with open("tv.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    compact_json = json.dumps(config, ensure_ascii=False).encode('utf-8')
    b58_text = base58.b58encode(compact_json).decode('utf-8')
    with open("deco_b58.txt", "w", encoding="utf-8") as f:
        f.write(b58_text)
    
    print(f"✅ 深度优化完成！当前包含 {len(api_site)} 个源。")

if __name__ == "__main__":
    requests.packages.urllib3.disable_warnings()
    generate()
