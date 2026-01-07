import json
import requests
import time
import os
from concurrent.futures import ThreadPoolExecutor

def check_speed(name, key, api):
    start_time = time.time()
    try:
        # 增加 headers 模拟浏览器，防止被某些源屏蔽
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(api, timeout=3, headers=headers)
        if res.status_code == 200:
            delay = time.time() - start_time
            return (key, name, api, delay)
    except Exception:
        pass
    return None

def generate_config():
    raw_sources = {
        "sn_4k": ["💎 索尼·4K原生", "https://suoniapi.com/api.php/provide/vod"],
        "lz_4k": ["💎 量子·骨干加速", "https://cj.lziapi.com/api.php/provide/vod"],
        "nfc_hd": ["💎 网飞猫·全球加速", "https://www.ncat3.com/api.php/provide/vod"],
        "cy_hd": ["🔥 春盈·4K蓝光霸主", "https://盒子迷.top/春盈天下"],
        # ... 其他源保持不变 ...
    }

    valid_results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(check_speed, val[0], key, val[1]) for key, val in raw_sources.items()]
        for future in futures:
            res = future.result()
            if res:
                valid_results.append(res)

    valid_results.sort(key=lambda x: x[3])

    api_site = {}
    for key, name, api, delay in valid_results:
        api_site[key] = {
            "api": api,
            "name": name,
            "detail": api.split('api.php')[0] if 'api.php' in api else api
        }

    config = {
        "cache_time": 9200,
        "api_site": api_site,
        "custom_category": [
            {"name": "4K重型专区", "type": "movie", "query": "4K"},
            {"name": "华语精选", "type": "movie", "query": "华语"}
        ]
    }

    # --- 关键修复：确保目录存在 ---
    output_dir = "dist"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 写入 JSON
    with open(os.path.join(output_dir, "tv.json"), "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    # 写入 Headers 解决跨域
    with open(os.path.join(output_dir, "_headers"), "w", encoding="utf-8") as f:
        f.write("/tv.json\n  Access-Control-Allow-Origin: *\n  Content-Type: application/json")

if __name__ == "__main__":
    generate_config()
