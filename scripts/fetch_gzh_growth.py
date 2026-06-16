#!/usr/bin/env python3
"""
公众号黑马账号推荐 - 数据获取脚本
"""
import os
import sys
import json
import argparse
from datetime import datetime, timedelta

def fetch_growth_rank(date_str="yesterday", top_n=50):
    """从RedFox API获取公众号阅读增长率排行榜"""
    api_key = os.environ.get('REDFOX_API_KEY')
    if not api_key:
        print("Error: REDFOX_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    API_URL = "https://redfox.hk/story/api/cozeSkill/getGzhCozeSkillDataRaise"
    
    # 解析日期
    date_str = date_str.strip().lower()
    if date_str == "yesterday":
        rank_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    elif date_str == "today":
        rank_date = datetime.now().strftime("%Y-%m-%d")
    else:
        rank_date = date_str
    
    try:
        import urllib.request
        import urllib.parse
        
        params = {
            "skillId": "7633629455969337344",
            "rankDate": rank_date,
            "topN": top_n,
            "source": "redfox-site"
        }
        
        url = f"{API_URL}?{urllib.parse.urlencode(params)}"
        
        # 创建请求，使用bytes类型的header值避免编码问题
        req = urllib.request.Request(url)
        req.add_header("X-API-KEY", api_key.encode('utf-8').decode('latin-1'))
        req.add_header("User-Agent", "RedFox-Site-Bot/1.0")
        
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            
            if result.get("code") not in (200, 2000):
                print(f"API error: {result.get('msg', 'unknown')}", file=sys.stderr)
                sys.exit(1)
            
            data = result.get("data", {})
            accounts = data.get("list", [])
            
            return {
                "status": "success",
                "rank_date": rank_date,
                "total": len(accounts),
                "accounts": accounts
            }
            
    except Exception as e:
        print(f"Error fetching growth rank: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', default='yesterday', help='日期: yesterday/today/YYYY-MM-DD')
    parser.add_argument('--top-n', type=int, default=50)
    parser.add_argument('--output', '-o', default='-', help='输出文件')
    args = parser.parse_args()
    
    data = fetch_growth_rank(args.date, args.top_n)
    
    output = json.dumps(data, ensure_ascii=False, indent=2)
    if args.output == '-':
        print(output)
    else:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Saved to {args.output}")

if __name__ == '__main__':
    main()
