import json
import requests
import time
from concurrent.futures import ThreadPoolExecutor

def check_speed(name, key, api):
    """测试接口延迟"""
    start_time = time.time()
    try:
        # 设置3秒超时，如果3秒连不上直接pass
        res = requests.get(api, timeout=3)
        if res.status_code == 200:
            delay = time.time() - start_time
            return (key, name, api, delay)
    except:
        pass
    return None

def generate_config():
    # 待检测的 50 个重型源池
    raw_sources = {
        "sn_4k": ["💎 索尼·4K原生", "https://suoniapi.com/api.php/provide/vod"],
        "lz_4k": ["💎 量子·骨干加速", "https://cj.lziapi.com/api.php/provide/vod"],
        "nfc_hd": ["💎 网飞猫·全球加速", "https://www.ncat3.com/api.php/provide/vod"],
        "cy_hd": ["🔥 春盈·4K蓝光霸主", "https://盒子迷.top/春盈天下"],
        "muyu_hd": ["🔥 摸鱼儿·蓝光直连", "http://muyu.top"],
        "yz_hd": ["🔥 优质·1080P特线", "https://api.yzzy-api.com/inc/ldg_api_all.php/provide/vod"],
        "ff_zy": ["🎬 非凡·全能老牌", "https://api.ffzyapi.com/api.php/provide/vod"],
        "zd_zy": ["🎬 最大·资源储备", "https://api.zuidapi.com/api.php/provide/vod"],
        "bf_cdn": ["📡 暴风·CDN分发版", "https://bfzyapi.com/api.php/provide/vod"],
        "js_zy": ["⚡ 极速·节点优化", "https://jszyapi.com/api.php/provide/vod"],
        "hh_zy": ["🎬 豪华·新剧专场", "https://hhzyapi.com/api.php/provide/vod"],
        "md_dm": ["🌸 魔都·动漫高频宽", "https://www.mdzyapi.com/api.php/provide/vod"],
        "yh_dm": ["🌸 樱花·动漫专线", "https://m3u8.apiyhzy.com/api.php/provide/vod"],
        "sd_zy": ["⚡ 闪电·直连大带宽", "https://sdzyapi.com/api.php/provide/vod"],
        "hn_zy": ["⚡ 红牛·全能加载", "https://www.hongniuzy2.com/api.php/provide/vod"],
        "gs_zy": ["🚀 光速·极速响应", "https://api.guangsuapi.com/api.php/provide/vod"],
        "sb_zy": ["🐯 速博·极速专线", "https://subocaiji.com/api.php/provide/vod"],
        "db_zy": ["🎬 豆瓣·高分原片", "https://caiji.dbzy.tv/api.php/provide/vod"],
        "xmm_zy": ["🐾 小猫咪·海外BGP", "https://zy.xmm.hk/api.php/provide/vod"],
        "mt_zy": ["🐾 茅台·醇厚资源", "https://caiji.maotaizy.cc/api.php/provide/vod"],
        "jy_zy": ["🎖 金鹰·稳定链路", "https://jyzyapi.com/api.php/provide/vod"],
        "wj_zy": ["🎖 无尽·高频宽", "https://api.wujinapi.cc/api.php/provide/vod"],
        "hy_zy": ["🐯 虎牙·视频采集", "https://www.huyaapi.com/api.php/provide/vod"],
        "yy_zy": ["🍎 丫丫·画质修复", "https://cj.yayazy.net/api.php/provide/vod"],
        "uk_zy": ["🍎 U酷·带宽大户", "https://api.ukuapi.com/api.php/provide/vod"],
        "dytt_zy": ["🎞 电影天堂·镜像", "http://caiji.dyttzyapi.com/api.php/provide/vod"],
        "ck_zy": ["🎞 CK·稳定重型", "https://ckzy.me/api.php/provide/vod"],
        "q360_zy": ["🔒 360·影视安全", "https://360zy.com/api.php/provide/vod"],
        "ry_zy": ["🔒 如意·长线稳定", "https://cj.rycjapi.com/api.php/provide/vod"],
        "fty_zy": ["✨ 饭太硬·多线分发", "http://fty.888484.xyz/tv"],
        "dh_zy": ["✨ 毒盒·主力机房", "https://毒盒.com/tv"],
        "qx_zy": ["✨ 七星·超级解析", "https://qixing.myhkw.com/QX/api.json"],
        "xz_zy": ["🏮 祥子·精品直连", "http://www.xzwl.top/祥子影视/main/xzysdm.json"],
        "wxe_zy": ["🏮 王小二·高码率", "http://tvbox.xn--4kq62z5rby2qupq9ub.top/"],
        "ty_zy": ["🌈 天涯·极清影视", "https://tyyszy.com/api.php/provide/vod"],
        "ik_zy": ["🌈 iKun·专线加速", "https://ikunzyapi.com/api.php/provide/vod"],
        "js_scan": ["🚀 极速扫描·全网", "https://itvbox.top/tv"],
        "ht_zy": ["🚀 海棠·2026综合", "http://yuan.haitangw.net/tv/"],
        "fm_zy": ["📡 肥猫·防堵特线", "https://like.肥猫.com/PandaQ"],
        "mz_zy": ["🎬 魔爪·稀缺高清", "https://mozhuazy.com/api.php/provide/vod"],
        "ok_zy": ["⚡ OK·大带宽专区", "http://ok321.top/tv"],
        "nn_zy": ["🥤 牛牛·稳定吞吐", "https://api.niuniuzy.me/api.php/provide/vod"],
        "ww_zy": ["🥤 旺旺·高清短剧", "https://api.wwzy.tv/api.php/provide/vod"],
        "xl_zy": ["☁ 新浪·即时采集", "https://api.xinlangapi.com/xinlangapi.php/provide/vod"],
        "bd_zy": ["📡 百度云·大带宽", "https://api.apibdzy.com/api.php/provide/vod"],
        "qj_zy": ["🎞 巧技·CDN中心", "http://cdn.qiaoji8.com/tvbox.json"],
        "k4_zy": ["💎 4K·重型特线", "https://api.zuidapi.com/api.php/provide/vod"],
        "sn_alt": ["💎 索尼·备用线", "https://suoniapi.com/api.php/provide/vod"],
        "my_dom": ["💎 摸鱼·国内直连", "http://muyu.top"],
        "itv_js": ["📺 iTV·高保真专线", "https://itvbox.top/tv"]
    }

    # 使用多线程并行测速，提高效率
    valid_results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(check_speed, val[0], key, val[1]) for key, val in raw_sources.items()]
        for future in futures:
            res = future.result()
            if res:
                valid_results.append(res)

    # 按延迟从小到大排序（最快的排在前面）
    valid_results.sort(key=lambda x: x[3])

    # 构造符合你要求的 api_site 结构
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
            {"name": "华语精选", "type": "movie", "query": "华语"},
            {"name": "Netflix", "type": "movie", "query": "网飞"}
        ]
    }

    with open("tv.json", "w", encoding="utf-8") as f:
        # --- 以下是优化后的保存逻辑 ---
    import os

    # 1. 确保创建 dist 文件夹
    if not os.path.exists("dist"):
        os.makedirs("dist")

    # 2. 将 tv.json 存入 dist 文件夹
    json_path = os.path.join("dist", "tv.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    # 3. 自动生成 _headers 文件，解决 DecoTV 拉取失败的兼容性问题
    headers_path = os.path.join("dist", "_headers")
    with open(headers_path, "w", encoding="utf-8") as f:
        f.write("/tv.json\n")
        f.write("  Content-Type: application/json; charset=utf-8\n")
        f.write("  Access-Control-Allow-Origin: *\n")

    print(f"✅ 配置已生成至 dist/tv.json，共 {len(api_site)} 个有效源")

if __name__ == "__main__":
    generate_config()
