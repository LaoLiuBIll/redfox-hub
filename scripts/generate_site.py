#!/usr/bin/env python3
"""
网站生成器 - 聚合多数据源生成静态网站
使用字符串替换避免CSS括号冲突
"""
import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

def load_json(path):
    """加载JSON文件"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: could not load {path}: {e}", file=sys.stderr)
        return None

def format_hotspot(data):
    """格式化热点数据为HTML"""
    if not data or 'hotspots' not in data or not data['hotspots']:
        return '<div class="empty-state">暂无数据</div>'
    
    hotspots = data['hotspots'][:10]
    html = ''
    
    for i, item in enumerate(hotspots, 1):
        title = item.get('title', '未知标题')
        url = item.get('url', '#')
        plat = item.get('platName', '未知平台')
        hot_score = item.get('maxHotScore') or 0
        duration = item.get('topOfTheDayTime') or '0'
        
        # 热度格式化
        if hot_score >= 10000:
            hot_display = f"{hot_score // 10000}万"
        else:
            hot_display = str(hot_score)
        
        # 平台样式映射
        plat_map = {
            '微博': 'plat-weibo',
            '抖音': 'plat-douyin',
            'B站': 'plat-bilibili',
            '哔哩哔哩': 'plat-bilibili',
            '快手': 'plat-kuaishou',
            '知乎': 'plat-zhihu',
            '头条': 'plat-toutiao',
            '百度': 'plat-baidu'
        }
        plat_class = plat_map.get(plat, '')
        
        html += f'''
        <div class="card">
            <div class="hotspot-item">
                <div class="rank">#{i}</div>
                <div style="flex: 1;">
                    <div class="card-header">
                        <a href="{url}" target="_blank" class="card-title">{title}</a>
                        <span class="badge badge-hot">{hot_display}</span>
                    </div>
                    <div class="meta">
                        <span><span class="platform-tag {plat_class}">{plat}</span></span>
                        <span>⏱️ 在榜{duration}小时</span>
                    </div>
                </div>
            </div>
        </div>
        '''
    
    return html

def format_wechat_original(data):
    """格式化公众号原创热门文章为HTML"""
    if not data or 'articles' not in data or not data['articles']:
        return '<div class="empty-state">暂无数据</div>'
    
    articles = data['articles'][:20]
    html = ''
    
    for i, article in enumerate(articles, 1):
        title = article.get('title', '未知标题')
        url = article.get('url', '#')
        author = article.get('userName', article.get('author', '未知作者'))
        read_count = article.get('readCount') or 0
        like_count = article.get('likeCount') or 0
        
        # 格式化数字
        read_str = f"{read_count//10000}w" if read_count >= 10000 else str(read_count)
        like_str = f"{like_count//10000}w" if like_count >= 10000 else str(like_count)
        
        html += f'''
        <div class="card">
            <div class="hotspot-item">
                <div class="rank">#{i}</div>
                <div style="flex: 1;">
                    <div class="card-header">
                        <a href="{url}" target="_blank" class="card-title">{title}</a>
                        <span class="badge badge-trend">原创</span>
                    </div>
                    <div class="meta">
                        <span>✍️ {author}</span>
                        <span>👁️ {read_str}阅读</span>
                        <span>👍 {like_str}赞</span>
                    </div>
                </div>
            </div>
        </div>
        '''
    
    return html

def format_xhs_weekly(data):
    """格式化小红书每周热门笔记为HTML"""
    if not data or 'notes' not in data or not data['notes']:
        return '<div class="empty-state">暂无数据</div>'
    
    notes = data['notes'][:20]
    html = ''
    
    for i, note in enumerate(notes, 1):
        title = note.get('title', note.get('content', '未知笔记'))
        author = note.get('userName', note.get('author', '未知作者'))
        likes = note.get('likeCount') or 0
        comments = note.get('commentCount') or 0
        collects = note.get('collectCount') or 0
        category = note.get('category', '综合')
        
        # 格式化数字
        like_str = f"{likes//10000}w" if likes >= 10000 else str(likes)
        
        html += f'''
        <div class="card">
            <div class="hotspot-item">
                <div class="rank">#{i}</div>
                <div style="flex: 1;">
                    <div class="card-header">
                        <span class="card-title">{title}</span>
                        <span class="badge badge-hot">{like_str}赞</span>
                    </div>
                    <div class="meta">
                        <span>👤 {author}</span>
                        <span>🏷️ {category}</span>
                        <span>💬 {comments}</span>
                        <span>⭐ {collects}</span>
                    </div>
                </div>
            </div>
        </div>
        '''
    
    return html

def format_channels(data):
    """格式化视频号数据为HTML"""
    if not data or 'videos' not in data or not data['videos']:
        return '<div class="empty-state">暂无数据</div>'
    
    videos = data['videos'][:20]
    html = ''
    
    for video in videos:
        title = video.get('title', '未知标题')
        author = video.get('userName', video.get('author', '未知作者'))
        likes = video.get('likeCount') or 0
        shares = video.get('shareCount') or 0
        comments = video.get('commentCount') or 0
        category = video.get('type', video.get('category', 'AI'))
        
        # 格式化数字
        like_str = f"{likes//10000}w" if likes >= 10000 else str(likes)
        share_str = f"{shares//10000}w" if shares >= 10000 else str(shares)
        comment_str = f"{comments//10000}w" if comments >= 10000 else str(comments)
        
        html += f'''
        <div class="card">
            <div class="card-header">
                <span class="card-title">{title}</span>
                <span class="badge badge-trend">{category}</span>
            </div>
            <div class="meta">
                <span>🎬 {author}</span>
                <span>❤️ {like_str}赞</span>
                <span>🔄 {share_str}分享</span>
                <span>💬 {comment_str}评论</span>
            </div>
        </div>
        '''
    
    return html

def format_douyin(data):
    """格式化抖音数据为HTML"""
    if not data or 'videos' not in data or not data['videos']:
        return '<div class="empty-state">暂无数据</div>'
    
    videos = data['videos'][:20]
    html = ''
    
    for i, video in enumerate(videos, 1):
        title = video.get('title', video.get('content', '未知标题'))
        url = video.get('workUrl', video.get('url', '#'))
        author = video.get('accountName', video.get('authorName', '未知作者'))
        fans = video.get('followerCount', '')
        category = video.get('category', '-')
        likes = video.get('likeCount', 0)
        comments = video.get('commentCount', 0)
        shares = video.get('shareCount', 0)
        
        # 格式化粉丝数
        if fans:
            fans_str = f"{fans//10000}w+" if fans >= 10000 else str(fans)
        else:
            fans_str = ''
        
        # 格式化点赞
        like_str = f"{likes//10000}w" if likes >= 10000 else str(likes)
        
        html += f'''
        <div class="card">
            <div class="hotspot-item">
                <div class="rank">#{i}</div>
                <div style="flex: 1;">
                    <div class="card-header">
                        <a href="{url}" target="_blank" class="card-title">{title}</a>
                        <span class="badge badge-hot">{like_str}赞</span>
                    </div>
                    <div class="meta">
                        <span>👤 {author} {fans_str and '(' + fans_str + ')'}</span>
                        <span>🏷️ {category}</span>
                        <span>💬 {comments}</span>
                        <span>🔄 {shares}</span>
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
    hotspot_data = load_json(data_dir / 'hotspot_raw.json') or load_json(data_dir / 'hotspot_structured.json')
    wechat_original_data = load_json(data_dir / 'wechat_original.json')
    xhs_data = load_json(data_dir / 'xhs_weekly.json')
    channels_data = load_json(data_dir / 'channels_feed.json')
    douyin_data = load_json(data_dir / 'douyin_hot.json')
    
    # 如果没有专门的数据文件，使用gzh_feed.json作为备选
    if not wechat_original_data:
        wechat_original_data = load_json(data_dir / 'gzh_feed.json')
    
    # 生成内容
    hotspot_html = format_hotspot(hotspot_data)
    wechat_original_html = format_wechat_original(wechat_original_data)
    xhs_html = format_xhs_weekly(xhs_data)
    channels_html = format_channels(channels_data)
    douyin_html = format_douyin(douyin_data)
    
    # 读取模板
    template_path = Path(__file__).parent / 'site_template.html'
    if template_path.exists():
        template = template_path.read_text(encoding='utf-8')
    else:
        template = get_default_template()
    
    # 字符串替换
    update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    html = template
    html = html.replace('<!--UPDATE_TIME-->', update_time)
    html = html.replace('<!--HOTSPOT_CONTENT-->', hotspot_html)
    html = html.replace('<!--WECHAT_ORIGINAL_CONTENT-->', wechat_original_html)
    html = html.replace('<!--XHS_CONTENT-->', xhs_html)
    html = html.replace('<!--CHANNELS_CONTENT-->', channels_html)
    html = html.replace('<!--DOUYIN_CONTENT-->', douyin_html)
    
    # 写入文件
    output_path = dist_dir / 'index.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Site generated: {output_path}")
    print(f"  - Hotspot items: {len(hotspot_data.get('hotspots', [])) if hotspot_data else 0}")
    print(f"  - WeChat original articles: {len(wechat_original_data.get('articles', [])) if wechat_original_data else 0}")
    print(f"  - XHS notes: {len(xhs_data.get('notes', [])) if xhs_data else 0}")
    print(f"  - Channels videos: {len(channels_data.get('videos', [])) if channels_data else 0}")
    print(f"  - Douyin videos: {len(douyin_data.get('videos', [])) if douyin_data else 0}")
    return output_path

def get_default_template():
    """默认HTML模板"""
    return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RedFox Hub - 每日热点聚合</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: #0a0a0f;
            color: #e0e0e0;
            line-height: 1.6;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        header {
            text-align: center;
            padding: 40px 0;
            border-bottom: 1px solid #333;
            margin-bottom: 30px;
        }
        h1 { font-size: 2.5em; color: #ff6b35; margin-bottom: 10px; }
        .subtitle { color: #888; font-size: 1.1em; }
        .update-time { color: #666; font-size: 0.9em; margin-top: 10px; }
        .nav {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        .nav a {
            color: #ff6b35;
            text-decoration: none;
            padding: 8px 16px;
            border: 1px solid #ff6b35;
            border-radius: 20px;
            transition: all 0.3s;
            font-size: 0.9em;
        }
        .nav a:hover, .nav a.active {
            background: #ff6b35;
            color: #fff;
        }
        .section { display: none; animation: fadeIn 0.5s; }
        .section.active { display: block; }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .card {
            background: #1a1a2e;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            border: 1px solid #2a2a3e;
            transition: transform 0.2s, border-color 0.2s;
        }
        .card:hover {
            transform: translateX(5px);
            border-color: #ff6b35;
        }
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            gap: 10px;
        }
        .card-title {
            font-size: 1.1em;
            color: #fff;
            text-decoration: none;
            flex: 1;
        }
        .card-title:hover { color: #ff6b35; }
        .badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 10px;
            font-size: 0.75em;
            font-weight: bold;
            white-space: nowrap;
        }
        .badge-hot { background: #ff4444; color: #fff; }
        .badge-trend { background: #ff6b35; color: #fff; }
        .meta {
            display: flex;
            gap: 12px;
            color: #888;
            font-size: 0.85em;
            margin-top: 8px;
            flex-wrap: wrap;
        }
        .rank {
            font-size: 1.8em;
            font-weight: bold;
            color: #ff6b35;
            min-width: 45px;
        }
        .hotspot-item {
            display: flex;
            gap: 15px;
            align-items: start;
        }
        .platform-tag {
            display: inline-block;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.7em;
            margin-right: 5px;
        }
        .plat-weibo { background: #e6162d; }
        .plat-douyin { background: #000; color: #fff; }
        .plat-bilibili { background: #00a1d6; }
        .plat-kuaishou { background: #ff5000; }
        .plat-zhihu { background: #0084ff; }
        .plat-toutiao { background: #f04142; }
        .plat-baidu { background: #2932e1; }
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #666;
        }
        footer {
            text-align: center;
            padding: 40px 0;
            color: #666;
            border-top: 1px solid #333;
            margin-top: 40px;
        }
        @media (max-width: 768px) {
            h1 { font-size: 1.8em; }
            .hotspot-item { flex-direction: column; }
            .rank { font-size: 1.5em; }
            .card-header { flex-direction: column; align-items: flex-start; }
            .nav { gap: 8px; }
            .nav a { padding: 6px 12px; font-size: 0.85em; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>RedFox Hub</h1>
            <p class="subtitle">全网热点聚合 · 原创内容 · 每周热榜</p>
            <p class="update-time">更新时间: <!--UPDATE_TIME--></p>
        </header>
        
        <nav class="nav">
            <a href="#hotspot" class="active" onclick="showSection(\'hotspot\')">全网热点</a>
            <a href="#wechat-original" onclick="showSection(\'wechat-original\')">公众号原创</a>
            <a href="#xhs" onclick="showSection(\'xhs\')">小红书热榜</a>
            <a href="#channels" onclick="showSection(\'channels\')">视频号AI</a>
            <a href="#douyin" onclick="showSection(\'douyin\')">抖音热榜</a>
        </nav>
        
        <section id="hotspot" class="section active">
            <h2 style="margin-bottom: 20px;">🔥 全网聚合热点 TOP10</h2>
            <!--HOTSPOT_CONTENT-->
        </section>
        
        <section id="wechat-original" class="section">
            <h2 style="margin-bottom: 20px;">📝 公众号原创热门文章</h2>
            <!--WECHAT_ORIGINAL_CONTENT-->
        </section>
        
        <section id="xhs" class="section">
            <h2 style="margin-bottom: 20px;">📕 小红书每周热门笔记</h2>
            <!--XHS_CONTENT-->
        </section>
        
        <section id="channels" class="section">
            <h2 style="margin-bottom: 20px;">🎬 视频号AI热门</h2>
            <!--CHANNELS_CONTENT-->
        </section>
        
        <section id="douyin" class="section">
            <h2 style="margin-bottom: 20px;">🎵 抖音每日热榜</h2>
            <!--DOUYIN_CONTENT-->
        </section>
        
        <footer>
            <p>RedFox Hub · 每日自动更新 · 数据来源: redfox.hk</p>
        </footer>
    </div>
    
    <script>
        function showSection(id) {
            document.querySelectorAll(\'.section\').forEach(s => s.classList.remove(\'active\'));
            document.querySelectorAll(\'.nav a\').forEach(a => a.classList.remove(\'active\'));
            document.getElementById(id).classList.add(\'active\');
            document.querySelector(\'a[href="#" + id]\').classList.add(\'active\');
        }
        if (location.hash) {
            showSection(location.hash.slice(1));
        }
    </script>
</body>
</html>'''

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', help='日期 YYYY-MM-DD')
    args = parser.parse_args()
    
    generate_site(args.date)

if __name__ == '__main__':
    main()
