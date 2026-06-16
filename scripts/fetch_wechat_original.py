#!/usr/bin/env python3
"""
公众号原创热门文章 - 数据获取脚本
"""
import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from urllib.request import Request, urlopen

def fetch_original_articles(article_type="总排名", start_date=None, limit=50):
    """从RedFox API获取公众号原创热门文章"""
    api_key = os.environ.get('REDFOX_API_KEY')
    if not api_key:
        print("Error: REDFOX_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    API_URL = "https://redfox.hk/story/api/cozeSkill/getWxDataByCategoryAndTime"
    
    # 日期处理
    if not start_date:
        now = datetime.now()
        if now.hour < 19:
            start_date = (now - timedelta(days=2)).strftime("%Y-%m-%d")
        else:
            start_date = (now - timedelta(days=1)).strftime("%Y-%m-%d")
    
    end_date = (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    
    body = {
        "type": article_type,
        "startDate": start_date,
        "endDate": end_date,
        "source": "公众号文章原创之王"
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
        with urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            
            if result.get("code") not in (200, 2000):
                print(f"API error: {result.get('msg', 'unknown')}", file=sys.stderr)
                sys.exit(1)
            
            data = result.get("data", {})
            articles = data.get("list", [])[:limit]
            
            return {
                "status": "success",
                "article_type": article_type,
                "start_date": start_date,
                "total": len(articles),
                "articles": articles
            }
            
    except Exception as e:
        print(f"Error fetching original articles: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--type', default='总排名', help='文章分类')
    parser.add_argument('--start-date', help='开始日期 YYYY-MM-DD')
    parser.add_argument('--limit', type=int, default=50)
    parser.add_argument('--output', '-o', default='-', help='输出文件')
    args = parser.parse_args()
    
    data = fetch_original_articles(args.type, args.start_date, args.limit)
    
    output = json.dumps(data, ensure_ascii=False, indent=2)
    if args.output == '-':
        print(output)
    else:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Saved to {args.output}")

if __name__ == '__main__':
    main()
