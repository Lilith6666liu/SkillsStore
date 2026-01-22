# AI资讯抓取系统 - 使用指南

## 🎯 快速开始

### 方式1: 使用启动脚本（推荐）

```bash
cd ai_news_crawler
./start.sh
```

然后根据菜单选择操作即可。

### 方式2: 直接使用命令

```bash
# 1. 进入项目目录
cd ai_news_crawler

# 2. 安装依赖（首次使用）
pip3 install -r requirements.txt

# 3. 抓取资讯
python3 main.py
```

## 📋 常用命令

### 基础抓取

```bash
# 抓取所有源的最新资讯
python3 main.py

# 只抓取最近24小时的内容
python3 main.py --hours 24

# 只抓取指定的数据源
python3 main.py --sources openai huggingface techcrunch_ai

# 导出为CSV格式
python3 main.py --output csv --file ai_news.csv
```

### 定时自动抓取

```bash
# 每小时自动抓取一次
python3 scheduler.py --interval 1h

# 每30分钟抓取一次
python3 scheduler.py --interval 30m

# 每天早上9点抓取
python3 scheduler.py --cron "0 9 * * *"

# 只执行一次（用于测试）
python3 scheduler.py --once
```

### Web界面查看

```bash
# 启动Web服务器
python3 web_viewer.py

# 然后在浏览器访问: http://127.0.0.1:5000
```

## ⚙️ 配置说明

编辑 `config.yaml` 文件可以自定义配置：

### 数据源配置

```yaml
sources:
  update_interval: 3600  # 更新间隔（秒）
  max_articles_per_source: 20  # 每个源最多抓取文章数
```

### 过滤配置

```yaml
filter:
  deduplication: true  # 是否去重
  keywords:  # 关键词过滤（包含这些词的文章会被保留）
    - AI
    - 人工智能
    - machine learning
    - GPT
  time_range_hours: 0  # 时间范围（0表示不限制）
```

### 存储配置

```yaml
storage:
  type: json  # 存储类型: json, sqlite, csv
  path: ./data/ai_news.json  # JSON文件路径
```

## 📊 数据源列表

### 国际源（10个）
- OpenAI Blog
- Google AI Blog
- Hugging Face Blog
- TechCrunch AI
- VentureBeat AI
- MIT Technology Review
- arXiv (AI/ML/CL)
- AWS Machine Learning Blog
- DeepMind Blog

### 国内源（5个）
- 机器之心
- 量子位
- 雷锋网AI
- 36氪AI
- AI科技评论

## 🔍 查看数据

### 方式1: Web界面（推荐）

```bash
python3 web_viewer.py
```

访问 http://127.0.0.1:5000 查看精美的Web界面

### 方式2: 直接查看JSON文件

```bash
cat data/ai_news.json
```

### 方式3: 使用jq工具（需安装jq）

```bash
# 查看最新10篇文章标题
cat data/ai_news.json | jq -r '.[:10] | .[] | .title'

# 按分类统计
cat data/ai_news.json | jq 'group_by(.category) | map({category: .[0].category, count: length})'

# 查看中文文章
cat data/ai_news.json | jq '.[] | select(.language=="zh")'
```

## 🤖 自动化运行

### 使用cron定时任务（Mac/Linux）

```bash
# 编辑crontab
crontab -e

# 添加以下行（每小时执行一次）
0 * * * * cd /path/to/ai_news_crawler && python3 main.py >> logs/cron.log 2>&1
```

### 使用launchd（Mac推荐）

创建 `~/Library/LaunchAgents/com.ai.news.crawler.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.ai.news.crawler</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/ai_news_crawler/main.py</string>
    </array>
    <key>StartInterval</key>
    <integer>3600</integer>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
```

加载任务：
```bash
launchctl load ~/Library/LaunchAgents/com.ai.news.crawler.plist
```

## 🎨 输出格式

每篇文章包含以下字段：

```json
{
  "id": "唯一ID",
  "title": "文章标题",
  "url": "文章链接",
  "source_name": "数据源名称",
  "language": "语言(en/zh)",
  "category": "分类(news/research/tutorial/interview/product)",
  "summary": "文章摘要",
  "tags": ["标签1", "标签2"],
  "publish_time": "发布时间",
  "fetch_time": "抓取时间"
}
```

## 🔧 常见问题

### Q: 某些源抓取失败？
A: 部分RSS源可能暂时不可用或格式有问题，系统会自动跳过并继续抓取其他源。

### Q: 如何添加新的数据源？
A: 编辑 `src/sources/rss_sources.py` 文件，在 `RSS_SOURCES` 字典中添加新源。

### Q: 如何修改抓取频率？
A: 使用 `scheduler.py` 时通过 `--interval` 参数指定，如 `--interval 2h` 表示每2小时。

### Q: 数据存储在哪里？
A: 默认存储在 `data/ai_news.json`，可在 `config.yaml` 中修改。

### Q: 如何清空历史数据？
A: 删除 `data/ai_news.json` 文件即可。

## 📝 日志查看

日志文件位置：`logs/crawler.log`

```bash
# 查看最新日志
tail -f logs/crawler.log

# 查看错误日志
grep ERROR logs/crawler.log
```

## 🚀 进阶使用

### 只抓取研究类文章

修改 `config.yaml`:
```yaml
filter:
  keywords:
    - paper
    - research
    - arxiv
    - 论文
    - 研究
```

### 集成到其他系统

可以通过读取JSON文件或使用SQLite数据库集成到其他系统：

```python
import json

# 读取数据
with open('data/ai_news.json', 'r') as f:
    articles = json.load(f)

# 处理数据
for article in articles:
    print(f"{article['title']} - {article['url']}")
```

## 📧 通知功能（待开发）

未来版本将支持：
- 邮件通知
- Webhook通知
- 微信/钉钉机器人通知

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License
