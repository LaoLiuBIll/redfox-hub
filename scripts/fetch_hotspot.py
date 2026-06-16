#!/usr/bin/env python3
"""
全网热点聚合 - 数据获取脚本 (修正版)
"""
import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from urllib.request import Request, urlopen

def fetch_hotspot(start_date=None, end_date=None):
    """从RedFox API获取热点数据"""
    api_key = os.environ.get('REDFOX_API_KEY')
    if not api_key:
        print("Error: REDFOX_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    API_URL = "https://redfox.hk/story/api/hotKeyword/list"
    
    # 构建请求体
    body = {"source": "redfox-site"}
    
    if start_date:
        if len(start_date) == 10:
            body["startDate"] = f"{start_date} 00:00:00"
        else:
            body["startDate"] = start_date
    
    if end_date:
        if len(end_date) == 10:
            body["endDate"] = f"{end_date} 00:00:00"
        else:
            body["endDate"] = end_date
    
    # 默认查询最近1小时
    if not start_date and not end_date:
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)
        body["startDate"] = one_hour_ago.strftime("%Y-%m-%d %H:00:00")
        body["endDate"] = now.strftime("%Y-%m-%d %H:00:00")
    
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
            raw_data = json.loads(resp.read().decode("utf-8"))
            
            if raw_data.get("code") != 2000:
                print(f"API error: {raw_data.get('msg', 'unknown')}", file=sys.stderr)
                sys.exit(1)
            
            # 转换为统一格式
            data_list = raw_data.get("data", [])
            all_hotspots = []
            
            for item in data_list:
                keyword = item.get("keyword", "")
                hot_spot_list = item.get("hotSpotList", [])
                
                for spot in hot_spot_list:
                    spot["source_keyword"] = keyword
                    if spot.get("title"):
                        spot["title"] = spot["title"].replace(" ", "")
                    if spot.get("url"):
                        spot["url"] = spot["url"].replace(" ", "%20")
                    all_hotspots.append(spot)
            
            return {
                "status": "success",
                "stat_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "timestamp": datetime.now().isoformat(),
                "source": "api",
                "total_count": len(all_hotspots),
                "hotspots": all_hotspots,
                "query_range": {
                    "start_date": body.get("startDate"),
                    "end_date": body.get("endDate")
                }
            }
            
    except Exception as e:
        print(f"Error fetching hotspot: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--start-date', help='开始时间 YYYY-MM-DD')
    parser.add_argument('--end-date', help='结束时间 YYYY-MM-DD')
    parser.add_argument('--output', '-o', default='-', help='输出文件')
    args = parser.parse_args()
    
    data = fetch_hotspot(args.start_date, args.end_date)
    
    output = json.dumps(data, ensure_ascii=False, indent=2)
    if args.output == '-':
        print(output)
    else:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Saved to {args.output}")

if __name__ == '__main__':
    main()
