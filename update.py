import json
import requests
import time
import os
import re
from concurrent.futures import ThreadPoolExecutor

# --- 配置区 ---
# 全网接口池（2026年主流聚合地址）
POOL_URLS = [
    "https://raw.githubusercontent.com/gaotianliuyun/gao/master/0827.json",
    "https://itvbox.top/tv",
    "http://cdn.qiaoji8.com/tvbox.json"
]

def check_quality(name, key, api):
    """
    测速逻辑：针对“高延迟但高带宽”的源优化
    """
    start_time = time.time()
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        # 允许最多 8 秒的响应时间，专门容忍那些响应慢但带宽大的重型站
        res = requests.get(api, timeout=8, headers=headers)
        if res.status_code == 200:
            delay = time.time() - start_time
            # 返回连接耗时，后续我们会根据这个排序，但只要能通的都会被标记为有效
            return (key, name, api, delay)
    except:
        pass
    return None

def fetch_sources():
    """全网搜刮潜在的 api 接口"""
    found_map = {}
    for url in POOL_URLS:
        try:
            r = requests.get(url, timeout=5)
            # 提取所有包含 vod 的 api 地址
            links = re.findall(r'"(https?://[^"]+/api\.php/provide/vod[^"]*)"', r.text)
            for i, link in enumerate(links):
                # 以域名作为去重 key，防止重复添加同一个源
                domain = re.search(r'//([^/]+)', link).group(1)
                found_map[domain] = [f"🌊 发现_{i}", link]
        except:
            continue
    return found_map

def generate_config():
    # 1. 搜刮源
    all_raw = fetch_sources()
    
    # 2. 强力加入你指定的“4K重型站”作为必选项
    priority_sources = {
        "sn_4k": ["💎 索尼·4K原生", "https://suoniapi.com/api.php/provide/vod"],
        "lz_4k": ["💎 量子·骨干加速", "https://cj.lziapi.com/api.php/provide/vod"],
        "nfc_hd": ["💎 网飞猫·4K加速", "https://www.ncat3.com/api.php/provide/vod"]
    }
    all_raw.update(priority_sources)

    # 3. 并行测速
    valid_list = []
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = [executor.submit(check_quality, val[0], key, val[1]) for key, val in all_raw.items()]
        for f in futures:
            res = f.result()
            if res:
                valid_list.append(res)

    # 4. 排序逻辑优化：
    # 虽然我们要包含高延迟源，但为了排序，我们依然按延迟排序。
    # 只要在有效名单里的，都会进入最终的 50 个席位。
    valid_list.sort(key=lambda x: x[3])
    final_50 = valid_list[:50]

    api_site = {}
    for key, name, api, delay in final_50:
        api_site[key] = {
            "api": api,
            "name": f"{name} | {int(delay*1000)}ms", # 标出延迟，方便你在电视上观察
            "detail": api.split('api.php')[0] if 'api.php' in api else api
        }

    # 5. 按照你的 DecoTV/LunaTV 嵌套格式输出
    config = {
        "cache_time": 9200,
        "api_site": api_site,
        "custom_category": [
            {"name": "极速·自动优选", "type": "movie", "query": "4K"},
            {"name": "华语精选", "type": "movie", "query": "华语"}
        ]
    }

    # 6. 保存到 dist 目录适配 Cloudflare Pages
    os.makedirs("dist", exist_ok=True)
    with open("dist/tv.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    # 生成解决跨域和识别问题的 headers
    with open("dist/_headers", "w", encoding="utf-8") as f:
        f.write("/tv.json\n  Access-Control-Allow-Origin: *\n  Content-Type: application/json; charset=utf-8")

if __name__ == "__main__":
    generate_config()
