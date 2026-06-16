#!/usr/bin/env python3
"""
网站生成器 - 聚合4个数据源生成静态网站
"""
import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

# 网站模板
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RedFox Hub - 每日热点聚合</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: #0a0a0f;
            color: #e0e0e0;
            line-height: 1.6;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        header {{
            text-align: center;
            padding: 40px 0;
            border-bottom: 1px solid #333;
            margin-bottom: 30px;
        }}
        h1 {{ font-size: 2.5em; color: #ff6b35; margin-bottom: 10px; }}
        .subtitle {{ color: #888; font-size: 1.1em; }}
        .update-time {{ color: #666; font-size: 0.9em; margin-top: 10px; }}
        
        .nav {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }}
        .nav a {{
            color: #ff6b35;
            text-decoration: none;
            padding: 10px 20px;
            border: 1px solid #ff6b35;
            border-radius: 25px;
            transition: all 0.3s;
        }}
        .nav a:hover, .nav a.active {{
            background: #ff6b35;
            color: #fff;
        }}
        
        .section {{
            display: none;
            animation: fadeIn 0.5s;
        }}
        .section.active {{ display: block; }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .card {{
            background: #1a1a2e;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid #2a2a3e;
            transition: transform 0.2s, border-color 0.2s;
        }}
        .card:hover {{
            transform: translateX(5px);
            border-color: #ff6b35;
        }}
        
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        .card-title {{
            font-size: 1.2em;
            color: #fff;
            text-decoration: none;
        }}
        .card-title:hover {{ color: #ff6b35; }}
        
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
        }}
        .badge-hot {{ background: #ff4444; color: #fff; }}
        .badge-new {{ background: #44ff44; color: #000; }}
        .badge-trend {{ background: #ff6b35; color: #fff; }}
        
        .meta {{
            display: flex;
            gap: 15px;
            color: #888;
            font-size: 0.9em;
            margin-top: 10px;
        }}
        .meta span {{ display: flex; align-items: center; gap: 5px; }}
        
        .rank {{
            font-size: 2em;
            font-weight: bold;
            color: #ff6b35;
            min-width: 50px;
        }}
        
        .hotspot-item {{
            display: flex;
            gap: 20px;
            align-items: start;
        }}
        
        .platform-tag {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.75em;
            margin-right: 5px;
        }}
        .plat-weibo {{ background: #e6162d; }}
        .plat-douyin {{ background: #000; color: #fff; }}
        .plat-bilibili {{ background: #00a1d6; }}
        .plat-kuaishou {{ background: #ff5000; }}
        .plat-zhihu {{ background: #0084ff; }}
        .plat-toutiao {{ background: #f04142; }}
        .plat-baidu {{ background: #2932e1; }}
        
        .prediction {{
            margin-top: 10px;
            padding: 10px;
            background: #0f0f1a;
            border-radius: 8px;
            font-size: 0.9em;
            color: #aaa;
        }}
        
        .empty-state {{
            text-align: center;
            padding: 60px 20px;
            color: #666;
        }}
        
        footer {{
            text-align: center;
            padding: 40px 0;
            color: #666;
            border-top: 1px solid #333;
            margin-top: 40px;
        }}
        
        @media (max-width: 768px) {{
            h1 {{ font-size: 1.8em; }}
            .hotspot-item {{ flex-direction: column; }}
            .rank {{ font-size: 1.5em; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔥 RedFox Hub</h1>
            <p class="subtitle">全网热点聚合 · AI资讯日报 · 抖音热榜</p>
            <p class="update-time">更新时间: {{update_time}}</p>
        </header>
        
        <nav class="nav">
            <a href="#hotspot" class="active" onclick="showSection('hotspot')">🔥 全网热点</a>
            <a href="#gzh" onclick="showSection('gzh')">📰 公众号AI</a>
            <a href="#channels" onclick="showSection('channels')">🎬 视频号AI</a>
            <a href="#douyin" onclick="showSection('douyin')">🎵 抖音热榜</a>
        </nav>
        
        <section id="hotspot" class="section active">
            <h2 style="margin-bottom: 20px;">🔥 全网聚合热点 TOP10</h2>
            {{hotspot_content}}
        </section>
        
        <section id="gzh" class="section">
            <h2 style="margin-bottom: 20px;">📰 公众号AI资讯</h2>
            {{gzh_content}}
        </section>
        
        <section id="channels" class="section">
            <h2 style="margin-bottom: 20px;">🎬 视频号AI热门</h2>
            {{channels_content}}
        </section>
        
        <section id="douyin" class="section">
            <h2 style="margin-bottom: 20px;">🎵 抖音每日热榜</h2>
            {{douyin_content}}
        </section>
        
        <footer>
            <p>RedFox Hub · 每日自动更新 · 数据来源: redfox.hk</p>
        </footer>
    </div>
    
    <script>
        function showSection(id) {{
            document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
            document.querySelectorAll('.nav a').forEach(a => a.classList.remove('active'));
            document.getElementById(id).classList.add('active');
            document.querySelector(`a[href="#${{id}}"]`).classList.add('active');
        }}
        
        // 默认显示hash对应的section
        if (location.hash) {{
            showSection(location.hash.slice(1));
        }}
    </script>
</body>
</html>
'''

def load_json(path):
    """加载JSON文件"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None

def format_hotspot(data):
    """格式化热点数据为HTML"""
    if not data or 'hotspots' not in data:
        return '<div class="empty-state">暂无数据</div>'
    
    hotspots = data['hotspots'][:10]
    html = ''
    
    for i, item in enumerate(hotspots, 1):
        title = item.get('title', '未知标题')
        url = item.get('url', '#')
        plat = item.get('platName', '未知平台')
        hot_score = item.get('maxHotScore', 0)
        duration = item.get('topOfTheDayTime', '0')
        
        # 热度格式化
        if hot_score >= 10000:
            hot_display = f"{{hot_score // 10000}}万"
        else:
            hot_display = str(hot_score)
        
        # 平台样式映射
        plat_class = f"plat-{{plat.lower()}}" if plat else ""
        
        html += f'''
        <div class="card">
            <div class="hotspot-item">
                <div class="rank">#{{i}}</div>
                <div style="flex: 1;">
                    <div class="card-header">
                        <a href="{{url}}" target="_blank" class="card-title">{{title}}</a>
                        <span class="badge badge-hot">{{hot_display}}</span>
                    </div>
                    <div class="meta">
                        <span><span class="platform-tag {{plat_class}}">{{plat}}</span></span>
                        <span>⏱️ 在榜{{duration}}小时</span>
                    </div>
                </div>
            </div>
        </div>
        '''
    
    return html

def format_gzh(data):
    """格式化公众号数据为HTML"""
    if not data or 'articles' not in data:
        return '<div class="empty-state">暂无数据</div>'
    
    articles = data['articles'][:20]
    html = ''
    
    for article in articles:
        title = article.get('title', '未知标题')
        url = article.get('url', '#')
        author = article.get('author', '未知作者')
        read_count = article.get('readCount', 0)
        like_count = article.get('likeCount', 0)
        category = article.get('category', 'AI')
        
        html += f'''
        <div class="card">
            <div class="card-header">
                <a href="{{url}}" target="_blank" class="card-title">{{title}}</a>
                <span class="badge badge-trend">{{category}}</span>
            </div>
            <div class="meta">
                <span>✍️ {{author}}</span>
                <span>👁️ {{read_count}}阅读</span>
                <span>👍 {{like_count}}点赞</span>
            </div>
        </div>
        '''
    
    return html

def format_channels(data):
    """格式化视频号数据为HTML"""
    if not data or 'videos' not in data:
        return '<div class="empty-state">暂无数据</div>'
    
    videos = data['videos'][:20]
    html = ''
    
    for video in videos:
        title = video.get('title', '未知标题')
        author = video.get('author', '未知作者')
        likes = video.get('likeCount', 0)
        shares = video.get('shareCount', 0)
        comments = video.get('commentCount', 0)
        category = video.get('category', 'AI')
        
        html += f'''
        <div class="card">
            <div class="card-header">
                <span class="card-title">{{title}}</span>
                <span class="badge badge-trend">{{category}}</span>
            </div>
            <div class="meta">
                <span>🎬 {{author}}</span>
                <span>❤️ {{likes}}赞</span>
                <span>🔄 {{shares}}分享</span>
                <span>💬 {{comments}}评论</span>
            </div>
        </div>
        '''
    
    return html

def format_douyin(data):
    """格式化抖音数据为HTML"""
    if not data or 'videos' not in data:
        return '<div class="empty-state">暂无数据</div>'
    
    videos = data['videos'][:20]
    html = ''
    
    for i, video in enumerate(videos, 1):
        title = video.get('title', '未知标题')
        url = video.get('url', '#')
        author = video.get('authorName', '未知作者')
        fans = video.get('authorFans', '')
        category = video.get('category', '-')
        likes = video.get('likeCount', 0)
        comments = video.get('commentCount', 0)
        shares = video.get('shareCount', 0)
        
        html += f'''
        <div class="card">
            <div class="hotspot-item">
                <div class="rank">#{{i}}</div>
                <div style="flex: 1;">
                    <div class="card-header">
                        <a href="{{url}}" target="_blank" class="card-title">{{title}}</a>
                        <span class="badge badge-hot">{{likes}}赞</span>
                    </div>
                    <div class="meta">
                        <span>👤 {{author}} ({{fans}})</span>
                        <span>🏷️ {{category}}</span>
                        <span>💬 {{comments}}</span>
                        <span>🔄 {{shares}}</span>
                    </div>
                </div>
            </div>
        </div>
        '''
    
    return html

def generate_site(date_str=None):
    """生成完整网站"""
    if not date_str:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    data_dir = Path('data')
    dist_dir = Path('dist')
    dist_dir.mkdir(exist_ok=True)
    
    # 加载数据
    hotspot_data = load_json(data_dir / 'hotspot_structured.json')
    gzh_data = load_json(data_dir / 'gzh_feed.json')
    channels_data = load_json(data_dir / 'channels_feed.json')
    douyin_data = load_json(data_dir / 'douyin_hot.json')
    
    # 生成内容
    hotspot_html = format_hotspot(hotspot_data)
    gzh_html = format_gzh(gzh_data)
    channels_html = format_channels(channels_data)
    douyin_html = format_douyin(douyin_data)
    
    # 生成完整页面
    update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    html = HTML_TEMPLATE.format(
        update_time=update_time,
        hotspot_content=hotspot_html,
        gzh_content=gzh_html,
        channels_content=channels_html,
        douyin_content=douyin_html
    )
    
    # 写入文件
    output_path = dist_dir / 'index.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Site generated: {output_path}")
    return output_path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', help='日期 YYYY-MM-DD')
    args = parser.parse_args()
    
    generate_site(args.date)

if __name__ == '__main__':
    main()
