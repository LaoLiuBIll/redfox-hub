#!/usr/bin/env python3
"""
小红书每周热门 - 数据获取脚本
"""
import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from urllib.request import Request, urlopen

def fetch_xhs_weekly(keyword="综合全部", category=None, rank_date=None, top_n=50):
    """从RedFox API获取小红书每周热门笔记"""
    api_key = os.environ.get('REDFOX_API_KEY')
    if not api_key:
        print("Error: REDFOX_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    API_URL = "https://redfox.hk/story/api/cozeSkill/getXhsCozeSkillDataIndex"
    
    # 日期处理
    if not rank_date:
        now = datetime.now()
        if now.hour < 19:
            rank_date = (now - timedelta(days=2)).strftime("%Y-%m-%d")
        else:
            rank_date = (now - timedelta(days=1)).strftime("%Y-%m-%d")
    
    # 构建请求体
    body = {
        "keyword": keyword,
        "rankDate": rank_date,
        "topN": top_n,
        "source": "redfox-site"
    }
    
    if category:
        body["category"] = category
    
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
            notes = data.get("list", [])[:top_n]
            
            return {
                "status": "success",
                "keyword": keyword,
                "rank_date": rank_date,
                "total": len(notes),
                "notes": notes
            }
            
    except Exception as e:
        print(f"Error fetching xhs weekly: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--keyword', default='综合全部', help='关键词')
    parser.add_argument('--category', help='分类')
    parser.add_argument('--rank-date', help='日期 YYYY-MM-DD')
    parser.add_argument('--top-n', type=int, default=50)
    parser.add_argument('--output', '-o', default='-', help='输出文件')
    args = parser.parse_args()
    
    data = fetch_xhs_weekly(args.keyword, args.category, args.rank_date, args.top_n)
    
    output = json.dumps(data, ensure_ascii=False, indent=2)
    if args.output == '-':
        print(output)
    else:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Saved to {args.output}")

if __name__ == '__main__':
    main()
