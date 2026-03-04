import json, requests, time, os, re, base58
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

# 1. 强制加入的顶级大厂白名单（这些是目前 115 和 4K 播放最稳的）
WHITELIST = [
    {"api": "https://cj.lziapi.com/api.php/provide/vod", "name": "💎量子资源"},
    {"api": "https://api.ffzyapi.com/api.php/provide/vod", "name": "💎非凡影视"},
    {"api": "https://jszyapi.com/api.php/provide/vod", "name": "💎极速资源"},
    {"api": "https://api.guangsuapi.com/api.php/provide/vod", "name": "💎光速资源"},
    {"api": "https://suoniapi.com/api.php/provide/vod", "name": "💎索尼资源"},
    {"api": "https://bfzyapi.com/api.php/provide/vod", "name": "💎暴风高清"},
    {"api": "https://api.1080zyku.com/inc/api_mac10.php", "name": "💎1080P库"},
    {"api": "https://api.kkzy.tv/api.php/provide/vod", "name": "💎快看资源"},
    {"api": "https://snzypm.com/api.php/provide/vod", "name": "💎索尼PM"},
    {"api": "https://api.tianyiapi.com/api.php/provide/vod", "name": "💎天翼影视"},
    {"api": "https://api.123zy.com/api.php/provide/vod", "name": "💎123资源"},
    {"api": "https://cj.yayazy.net/api.php/provide/vod", "name": "💎鸭鸭资源"},
    {"api": "https://www.605zy.cc/api.php/provide/vod", "name": "💎605资源"},
    {"api": "https://ikunzyapi.com/api.php/provide/vod", "name": "💎IKUN资源"},
    {"api": "https://dbzy.tv/api.php/provide/vod", "name": "💎豆瓣资源"}
]

# 2. 搜刮池
POOL_URLS = [
    "https://raw.githubusercontent.com/gaotianliuyun/gao/master/0827.json",
    "https://itvbox.top/tv",
    "http://cdn.qiaoji8.com/tvbox.json",
    "https://raw.liucn.cc/box/m.json",
    "http://120.79.4.185/new.json",
    "https://itvbox.cc/tvbox/sources/my.json"
]

def check_source(name, api):
    try:
        # 针对高峰期优化：只要能连通，不计较延迟
        start_time = time.time()
        res = requests.get(api, timeout=10, headers={'User-Agent': 'Mozilla/5.0'}, verify=False)
        if res.status_code == 200 and "vod" in res.text:
            return {"api": api, "name": name, "delay": time.time() - start_time}
    except:
        pass
    return None

def generate():
    raw_links = []
    
    # 首先把白名单加进去
    for item in WHITELIST:
        raw_links.append((item['name'], item['api']))
    
    print("Step 1: 正在从搜刮池提取新地址...")
    for url in POOL_URLS:
        try:
            r = requests.get(url, timeout=10, verify=False)
            # 改进正则，提取包含 api.php 的地址和可能的站点名称
            matches = re.findall(r'"name"\s*:\s*"([^"]+)"[^}]+"(https?://[^"]+/api\.php/[^"]+)"', r.text)
            for m_name, m_api in matches:
                raw_links.append((m_name, m_api))
        except:
            continue
    
    # 域名去重：同一个服务器只保留一个接口，防止重复
    unique_dict = {}
    for name, api in raw_links:
        domain = urlparse(api).netloc
        if domain not in unique_dict:
            unique_dict[domain] = {"name": name, "api": api}
    
    print(f"去重后剩余 {len(unique_dict)} 个独立接口，正在筛选...")

    valid_results = []
    with ThreadPoolExecutor(max_workers=50) as exe:
        futures = [exe.submit(check_source, v['name'], v['api']) for v in unique_dict.values()]
        for f in futures:
            res = f.result()
            if res:
                valid_results.append(res)
    
    # 排序逻辑：白名单站点强行排在最前面，剩下的按延迟排
    valid_results.sort(key=lambda x: (0 if "💎" in x['name'] else 1, x['delay']))
    
    # 最终取前 80 个
    final_list = valid_results[:80]

    api_site = {}
    for i, item in enumerate(final_list):
        # 清理名称中的干扰字符
        clean_name = re.sub(r'\(.*?\)|\[.*?\]|资源|采集', '', item['name']).strip()
        key = f"api_{i+1}"
        api_site[key] = {
            "api": item['api'],
            "name": f"{clean_name}",
            "detail": item['api'].split('api.php')[0]
        }

    config = {
        "cache_time": 9200,
        "api_site": api_site,
        "custom_category": [
            { "name": "🎞️ 115/4K", "type": "movie", "query": "115" },
            { "name": "📺 华语", "type": "movie", "query": "华语" }
        ]
    }

    # 写入 JSON
    with open("tv.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    # 生成 Base58
    compact_json = json.dumps(config, ensure_ascii=False).encode('utf-8')
    b58_text = base58.b58encode(compact_json).decode('utf-8')

    with open("deco_b58.txt", "w", encoding="utf-8") as f:
        f.write(b58_text)
    
    print(f"✅ 更新成功！有效独立源: {len(api_site)}")

if __name__ == "__main__":
    requests.packages.urllib3.disable_warnings()
    generate()
