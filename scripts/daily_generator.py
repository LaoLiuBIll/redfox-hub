#!/usr/bin/env python3
"""
每日内容生成器 v2 - 一群胖子网站
只使用验证可用的数据源，失败的自动跳过
"""
import os
import sys
import json
import subprocess
import argparse
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
DIST_DIR = PROJECT_ROOT / 'dist'
HISTORY_DIR = DIST_DIR / 'history'

# 验证可用的数据源（不可用的已注释）
DATA_SOURCES = [
    {'script': 'fetch_gzh.py', 'name': '公众号', 'args': ['--count', '50']},
    {'script': 'fetch_channels.py', 'name': '视频号', 'args': ['--page-size', '50']},
    # 以下数据源API Key权限不足，暂时禁用
    # {'script': 'fetch_hotspot.py', 'name': '全网热点', 'args': []},
    # {'script': 'fetch_douyin.py', 'name': '抖音', 'args': ['--limit', '50']},
]

def ensure_dirs():
    DATA_DIR.mkdir(exist_ok=True)
    DIST_DIR.mkdir(exist_ok=True)
    HISTORY_DIR.mkdir(exist_ok=True)

def fetch_source(script, name, date_str, extra_args=None):
    """抓取单个数据源"""
    script_path = Path(__file__).parent / script
    output_path = DATA_DIR / f'{script.replace(".py","").replace("fetch_","")}_{date_str}.json'
    
    cmd = ['python3', str(script_path), '--output', str(output_path)]
    if extra_args:
        cmd.extend(extra_args)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=45, 
                              env={**os.environ, 'REDFOX_API_KEY': os.environ.get('REDFOX_API_KEY', '')})
        if result.returncode == 0 and output_path.exists():
            print(f"  ✓ {name}: {output_path.name}")
            return output_path
        else:
            print(f"  ✗ {name}: {result.stderr[:100] if result.stderr else 'unknown error'}")
            return None
    except subprocess.TimeoutExpired:
        print(f"  ✗ {name}: timeout")
        return None
    except Exception as e:
        print(f"  ✗ {name}: {e}")
        return None

def generate_site(date_str):
    """生成网站HTML"""
    script = Path(__file__).parent / 'generate_site.py'
    if not script.exists():
        print("  ✗ generate_site.py not found")
        return False
    
    result = subprocess.run(['python3', str(script), '--date', date_str],
                          capture_output=True, text=True, timeout=30)
    if result.returncode == 0:
        print(f"  ✓ 网站已生成")
        return True
    else:
        print(f"  ✗ 生成失败: {result.stderr[:200]}")
        return False

def push_to_github():
    """推送到GitHub"""
    try:
        os.chdir(PROJECT_ROOT)
        subprocess.run(['git', 'add', '-A'], capture_output=True, timeout=10)
        
        result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
        if not result.stdout.strip():
            print("  ✓ 无变更")
            return True
        
        date_str = datetime.now().strftime('%Y-%m-%d')
        subprocess.run(['git', 'commit', '-m', f'Daily update: {date_str}'], capture_output=True, timeout=10)
        
        result = subprocess.run(['git', 'push'], capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("  ✓ 已推送到GitHub")
            return True
        else:
            print(f"  ✗ 推送失败: {result.stderr[:100]}")
            return False
    except Exception as e:
        print(f"  ✗ Git错误: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='每日内容生成器 v2')
    parser.add_argument('--date', help='指定日期 YYYY-MM-DD')
    parser.add_argument('--skip-fetch', action='store_true')
    parser.add_argument('--skip-push', action='store_true')
    args = parser.parse_args()
    
    date_str = args.date or datetime.now().strftime('%Y-%m-%d')
    print(f"\n{'='*50}")
    print(f"  一群胖子 · 每日内容生成器")
    print(f"  日期: {date_str}")
    print(f"{'='*50}\n")
    
    ensure_dirs()
    
    # 检查API Key
    api_key = os.environ.get('REDFOX_API_KEY', '')
    if not api_key:
        print("⚠️  REDFOX_API_KEY 未设置，跳过数据抓取\n")
    elif not args.skip_fetch:
        print("📡 抓取数据源:")
        success = 0
        for src in DATA_SOURCES:
            if fetch_source(src['script'], src['name'], date_str, src.get('args')):
                success += 1
        print(f"\n  成功: {success}/{len(DATA_SOURCES)}\n")
    
    # 生成网站
    print("🔨 生成网站:")
    generate_site(date_str)
    
    # 推送
    if not args.skip_push:
        print("\n📤 推送更新:")
        push_to_github()
    
    # 统计
    history_count = len(list(HISTORY_DIR.glob('*.json')))
    print(f"\n{'='*50}")
    print(f"  完成！历史数据: {history_count} 天")
    print(f"  网站: https://laoliubill.github.io/redfox-hub/")
    print(f"{'='*50}\n")

if __name__ == '__main__':
    main()
