"""
数据抓取模块
基于苹果官方 iTunes RSS Feed 接口，合规获取美国区用户评论
多格式自动适配 + 重试机制，兼容不同网络环境下的接口响应
"""
import requests
import pandas as pd
import time
from datetime import datetime
from utils.helpers import extract_app_id, safe_int


def fetch_app_reviews(app_url: str = "", app_id: str = "", max_pages: int = 5) -> pd.DataFrame:
    """
    批量抓取 App Store 用户评论（美国区）
    自动尝试多种接口格式，适配不同网络环境
    """
    if not app_id and app_url:
        app_id = extract_app_id(app_url)
    
    if not app_id:
        raise ValueError("无法提取应用ID，请检查输入的App Store链接")
    
    all_reviews = []
    
    # 通用请求头：极简浏览器特征，兼容性最好
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01"
    }

    # 3种主流接口格式，按优先级依次尝试
    url_patterns = [
        # 格式1：page在前 + 按最新排序（最经典格式）
        f"https://itunes.apple.com/us/rss/customerreviews/page={{page}}/id={app_id}/sortby=mostrecent/json",
        # 格式2：id在前 + 按最新排序
        f"https://itunes.apple.com/us/rss/customerreviews/id={app_id}/page={{page}}/sortby=mostrecent/json",
        # 格式3：无排序参数的基础格式
        f"https://itunes.apple.com/us/rss/customerreviews/page={{page}}/id={app_id}/json"
    ]

    # 找到第一个可用的格式
    working_pattern = None
    for pattern in url_patterns:
        test_url = pattern.format(page=1)
        try:
            print(f"尝试格式: {test_url}")
            resp = requests.get(test_url, headers=headers, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                entries = data.get("feed", {}).get("entry", [])
                if len(entries) > 0:
                    working_pattern = pattern
                    print(f"✅ 找到可用格式，entry数量: {len(entries)}")
                    break
        except Exception as e:
            print(f"格式尝试失败: {str(e)}")
            continue
    
    if not working_pattern:
        raise RuntimeError("所有接口格式均无法获取数据，请检查网络环境或更换应用ID测试")

    print(f"\n===== 开始抓取，应用ID: {app_id}，共{max_pages}页 =====")

    # 正式逐页抓取
    for page in range(1, max_pages + 1):
        try:
            url = working_pattern.format(page=page)
            print(f"\n第{page}页 - 请求URL: {url}")

            # 简单间隔，避免请求过快
            time.sleep(0.5)
            
            response = requests.get(url, headers=headers, timeout=15)
            print(f"第{page}页 - HTTP状态码: {response.status_code}")
            
            if response.status_code != 200:
                print(f"请求失败，返回内容: {response.text[:200]}")
                continue
            
            data = response.json()
            feed = data.get("feed", {})
            entries = feed.get("entry", [])
            print(f"第{page}页 - entry原始数量: {len(entries)}")
            
            if not entries:
                print("已无更多数据，终止抓取")
                break
            
            # 第一页第一条是应用元信息（无评分字段），跳过
            if page == 1 and len(entries) > 0:
                first_entry = entries[0]
                if "im:rating" not in first_entry:
                    entries = entries[1:]
            
            # 逐条解析
            for entry in entries:
                review = _parse_single_review(entry)
                if review:
                    all_reviews.append(review)
            
            print(f"第{page}页解析完成，累计 {len(all_reviews)} 条评论")
                    
        except Exception as e:
            print(f"第 {page} 页抓取异常: {str(e)}")
            continue
    
    # 结果去重
    df = pd.DataFrame(all_reviews)
    if not df.empty:
        df = df.drop_duplicates(subset=["review_id"], keep="first").reset_index(drop=True)
    
    print(f"\n===== 全部抓取完成，共 {len(df)} 条有效评论 =====\n")
    return df


def _parse_single_review(entry: dict) -> dict | None:
    """解析单条评论，标准化字段"""
    try:
        review_id = entry.get("id", {}).get("label", "")
        rating = safe_int(entry.get("im:rating", {}).get("label", 0))
        title = entry.get("title", {}).get("label", "").strip()
        content = entry.get("content", {}).get("label", "").strip()
        author = entry.get("author", {}).get("name", {}).get("label", "").strip()
        version = entry.get("im:version", {}).get("label", "").strip()
        publish_time = entry.get("updated", {}).get("label", "")
        
        return {
            "review_id": review_id,
            "rating": rating,
            "title": title,
            "content": content,
            "author": author,
            "version": version,
            "publish_time": publish_time,
            "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception:
        return None
