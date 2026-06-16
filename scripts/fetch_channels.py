#!/usr/bin/env python3
"""
视频号AI资讯 - 数据获取脚本 (修正版)
"""
import os
import sys
import json
import argparse
from urllib.request import Request, urlopen

def fetch_channels(keyword="AI", page_size=200, date=None):
    """从RedFox API获取视频号作品"""
    api_key = os.environ.get('REDFOX_API_KEY')
    if not api_key:
        print("Error: REDFOX_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    API_URL = "https://redfox.hk/story/api/parseWork/queryAiMsgs"
    
    all_videos = []
    seen_ids = set()
    
    for page in range(1, (page_size // 20) + 2):
        if len(all_videos) >= page_size:
            break
            
        body = {
            "keyword": keyword,
            "pageNum": page,
            "pageSize": 20,
            "source": "redfox-site-channels"
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
                    break
                
                data = result.get("data", {})
                videos = data.get("list", [])
                
                if not videos:
                    break
                
                for video in videos:
                    pid = video.get("photoId", "")
                    if pid and pid not in seen_ids:
                        seen_ids.add(pid)
                        all_videos.append(video)
                        
        except Exception as e:
            print(f"Warning: fetch error page {page}: {e}", file=sys.stderr)
            break
    
    return {
        "status": "success",
        "total": len(all_videos),
        "videos": all_videos[:page_size]
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--keyword', default='AI')
    parser.add_argument('--page-size', type=int, default=50)
    parser.add_argument('--date', help='指定日期 YYYY-MM-DD')
    parser.add_argument('--output', '-o', default='-', help='输出文件')
    args = parser.parse_args()
    
    data = fetch_channels(args.keyword, args.page_size, args.date)
    
    output = json.dumps(data, ensure_ascii=False, indent=2)
    if args.output == '-':
        print(output)
    else:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Saved to {args.output}")

if __name__ == '__main__':
    main()
