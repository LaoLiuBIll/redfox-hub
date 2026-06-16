# RedFox Hub - 每日热点聚合网站

自动聚合全网热点、AI资讯、抖音热榜的静态网站。

## 数据源

| 模块 | 来源 | 更新频率 |
|------|------|---------|
| 🔥 全网热点 | 7大平台聚合 (微博/抖音/B站/快手/知乎/头条/百度) | 每小时 |
| 📰 公众号AI | 200+ AI公众号爆款文章 | 每日 |
| 🎬 视频号AI | AI相关热门视频 | 每日 |
| 🎵 抖音热榜 | 全平台点赞TOP50 | 每日06:00 |

## 本地测试

```bash
# 1. 安装依赖
pip install python-dateutil requests

# 2. 设置API密钥
export REDFOX_API_KEY=your_api_key

# 3. 获取数据
python scripts/fetch_hotspot.py --output data/hotspot_raw.json
python scripts/fetch_gzh.py --output data/gzh_feed.json
python scripts/fetch_channels.py --output data/channels_feed.json
python scripts/fetch_douyin.py --output data/douyin_hot.json

# 4. 生成网站
python scripts/generate_site.py

# 5. 本地预览
cd dist && python -m http.server 8080
# 打开 http://localhost:8080
```

## GitHub Actions 自动部署

1. Fork 本仓库
2. 设置 Secrets: `REDFOX_API_KEY`
3. 启用 GitHub Pages (Settings > Pages > Source: GitHub Actions)
4. 每天自动更新，或手动触发 Workflow

## 技术栈

- Python 3.11 - 数据获取与处理
- GitHub Actions - 定时构建
- GitHub Pages - 静态托管
- 纯HTML/CSS/JS - 前端展示

## License

MIT
