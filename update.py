import json

# 这里就是你要求的 2026 高带宽源格式
config = {
    "cache_time": 9200,
    "api_site": {
        "sn_2026": {"api": "https://suoniapi.com/api.php/provide/vod", "name": "💎索尼4K", "detail": "https://suoniapi.com"},
        "lz_2026": {"api": "https://cj.lziapi.com/api.php/provide/vod", "name": "💎量子4K", "detail": "https://cj.lziapi.com"},
        "cy_2026": {"api": "https://盒子迷.top/春盈天下", "name": "🔥春盈4K", "detail": "https://盒子迷.top"}
    },
    "custom_category": [{"name": "华语", "type": "movie", "query": "华语"}]
}

with open("tv.json", "w", encoding="utf-8") as f:
    json.dump(config, f, ensure_ascii=False, indent=2)
