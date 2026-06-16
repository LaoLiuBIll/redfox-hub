#!/usr/bin/env python3
"""
公众号热门账号推荐 - 数据获取脚本
"""
import os
import sys
import json
import argparse
from urllib.request import Request, urlopen
from urllib.parse import urlencode

def fetch_top_accounts(rank_type="day", category="总排名", top_n=50, rank_date=None):
    """从RedFox API获取公众号热门账号榜单"""
    api_key = os.environ.get('REDFOX_API_KEY')
    if not api_key:
        print("Error: REDFOX_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    API_URL = "https://redfox.hk/story/api/cozeSkill/getGzhCozeSkillDataIndex"
    
    params = {
        "rankType": rank_type,
        "category": category,
        "topN": top_n,
        "source": "redfox-site"
    }
    
    if rank_date:
        params["rankDate"] = rank_date
    
    url = f"{API_URL}?{urlencode(params)}"
    
    req = Request(url, headers={
        "X-API-KEY": api_key,
        "User-Agent": "RedFox-Site-Bot/1.0"
    })
    
    try:
        with urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            
            if result.get("code") not in (200, 2000):
                print(f"API error: {result.get('msg', 'unknown')}", file=sys.stderr)
                sys.exit(1)
            
            data = result.get("data", {})
            accounts = data.get("list", [])
            
            return {
                "status": "success",
                "rank_type": rank_type,
                "category": category,
                "total": len(accounts),
                "accounts": accounts
            }
            
    except Exception as e:
        print(f"Error fetching top accounts: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--rank-type', default='day', choices=['day', 'week', 'month'])
    parser.add_argument('--category', default='总排名')
    parser.add_argument('--top-n', type=int, default=50)
    parser.add_argument('--rank-date', help='指定日期 YYYY-MM-DD')
    parser.add_argument('--output', '-o', default='-', help='输出文件')
    args = parser.parse_args()
    
    data = fetch_top_accounts(args.rank_type, args.category, args.top_n, args.rank_date)
    
    output = json.dumps(data, ensure_ascii=False, indent=2)
    if args.output == '-':
        print(output)
    else:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Saved to {args.output}")

if __name__ == '__main__':
    main()
