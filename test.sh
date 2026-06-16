#!/bin/bash
# 本地测试脚本

set -e

echo "🚀 RedFox Hub 本地测试"
echo "======================="

# 检查API密钥
if [ -z "$REDFOX_API_KEY" ]; then
    echo "❌ 请设置 REDFOX_API_KEY 环境变量"
    exit 1
fi

# 创建数据目录
mkdir -p data dist

echo "📡 获取全网热点..."
python3 scripts/fetch_hotspot.py --output data/hotspot_raw.json

echo "📰 获取公众号AI资讯..."
python3 scripts/fetch_gzh.py --count 20 --output data/gzh_feed.json

echo "🎬 获取视频号AI资讯..."
python3 scripts/fetch_channels.py --page-size 20 --output data/channels_feed.json

echo "🎵 获取抖音热榜..."
python3 scripts/fetch_douyin.py --limit 20 --output data/douyin_hot.json

echo "🏗️ 生成网站..."
python3 scripts/generate_site.py

echo "✅ 完成！网站已生成到 dist/ 目录"
echo ""
echo "预览命令: cd dist && python -m http.server 8080"
echo "然后打开: http://localhost:8080"
