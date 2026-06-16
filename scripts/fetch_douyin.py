#!/usr/bin/env python3
"""
抖音每日热榜 - 数据获取脚本 (修正版)
"""
import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from urllib.request import Request, urlopen

def fetch_douyin(start_date=None, end_date=None, type_name="全部", limit=50):
    """从RedFox API获取抖音热榜"""
    api_key = os.environ.get('REDFOX_API_KEY')
    if not api_key:
        print("Error: REDFOX_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    API_URL = "https://redfox.hk/story/api/dy/search/likesRank"
    
    body = {
        "source": "redfox-site",
        "type": type_name
    }
    
    if start_date:
        body["startTime"] = start_date
    if end_date:
        body["endTime"] = end_date
    
    # 默认查询昨天
    if not start_date and not end_date:
        yesterday = datetime.now() - timedelta(days=1)
        body["startTime"] = yesterday.strftime('%Y-%m-%d')
        body["endTime"] = datetime.now().strftime('%Y-%m-%d')
    
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
                print(f"API error: {result.get('msg', 'unknown')}", file=sys.stderr)
                sys.exit(1)
            
            data = result.get("data", [])
            
            # data可能是列表或字典
            if isinstance(data, dict):
                videos = data.get("list", [])[:limit]
            else:
                videos = data[:limit]
            
            return {
                "status": "success",
                "total": len(videos),
                "videos": videos
            }
            
    except Exception as e:
        print(f"Error fetching douyin: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--start', help='开始日期 YYYY-MM-DD')
    parser.add_argument('--end', help='结束日期 YYYY-MM-DD')
    parser.add_argument('--type', default='全部', help='赛道分类')
    parser.add_argument('--limit', type=int, default=50)
    parser.add_argument('--output', '-o', default='-', help='输出文件')
    args = parser.parse_args()
    
    data = fetch_douyin(args.start, args.end, args.type, args.limit)
    
    output = json.dumps(data, ensure_ascii=False, indent=2)
    if args.output == '-':
        print(output)
    else:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Saved to {args.output}")

if __name__ == '__main__':
    main()
