#!/usr/bin/env python3
"""
公众号AI资讯 - 数据获取脚本 (修正版)
"""
import os
import sys
import json
import argparse
from urllib.request import Request, urlopen

def fetch_gzh(keywords="AI,人工智能,大模型,GPT,Agent,AI绘画", count=200, date=None):
    """从RedFox API获取公众号文章"""
    api_key = os.environ.get('REDFOX_API_KEY')
    if not api_key:
        print("Error: REDFOX_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    API_URL = "https://redfox.hk/story/api/parseWork/queryAiMsgs"
    
    # 解析关键词
    kw_list = [k.strip() for k in keywords.split(",") if k.strip()]
    
    all_articles = []
    seen_ids = set()
    
    for kw in kw_list:
        if len(all_articles) >= count:
            break
            
        for page in range(1, 3):  # 每关键词查2页
            if len(all_articles) >= count:
                break
                
            body = {
                "keyword": kw,
                "pageNum": page,
                "pageSize": 20,
                "source": "redfox-site"
            }
            
            body_bytes = json.dumps(body, ensure_ascii=False).encode("utf-8")
            
            req = Request(
                API_URL,
                data=body_bytes,
                headers={
                    "Content-Type": "application/json",
                    "X-API-KEY": api_key
                },
                method="POST"
            )
            
            try:
                with urlopen(req, timeout=15) as resp:
                    result = json.loads(resp.read().decode("utf-8"))
                    
                    if result.get("code") not in (200, 2000):
                        continue
                    
                    data = result.get("data", {})
                    articles = data.get("list", [])
                    
                    for article in articles:
                        pid = article.get("photoId", "")
                        if pid and pid not in seen_ids:
                            seen_ids.add(pid)
                            all_articles.append(article)
                            
            except Exception as e:
                print(f"Warning: fetch error for {kw} page {page}: {e}", file=sys.stderr)
                continue
    
    return {
        "status": "success",
        "total": len(all_articles),
        "articles": all_articles[:count]
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--keywords', default='AI,人工智能,大模型,GPT,Agent,AI绘画')
    parser.add_argument('--count', type=int, default=50)
    parser.add_argument('--date', help='指定日期 YYYY-MM-DD')
    parser.add_argument('--output', '-o', default='-', help='输出文件')
    args = parser.parse_args()
    
    data = fetch_gzh(args.keywords, args.count, args.date)
    
    output = json.dumps(data, ensure_ascii=False, indent=2)
    if args.output == '-':
        print(output)
    else:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Saved to {args.output}")

if __name__ == '__main__':
    main()
