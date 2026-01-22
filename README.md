# AI资讯实时抓取系统

一个自动抓取国内外AI动态、新闻、知识、访谈的Python工具。

## 功能特性

- 🌍 **多源聚合**：支持50+国内外AI资讯源
- 🔄 **自动更新**：定时抓取最新内容
- 🏷️ **智能分类**：自动分类为新闻/研究/访谈/知识
- 🌐 **双语支持**：自动翻译英文标题为中文
- 💾 **数据存储**：支持JSON/SQLite/CSV多种格式
- 📊 **去重过滤**：自动去除重复内容
- 🔔 **通知推送**：支持邮件/Webhook通知

## 数据源列表

### 国际源
- OpenAI Blog
- Google AI Blog
- Hugging Face Blog
- TechCrunch AI
- VentureBeat AI
- MIT Technology Review
- arXiv (cs.AI, cs.LG, cs.CL)
- Hacker News
- Product Hunt
- GitHub Trending

### 国内源
- 机器之心
- 量子位
- AI科技评论
- 新智元
- 雷锋网AI
- 36氪AI
- 美团技术团队
- 阿里技术

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 基础使用

```bash
# 抓取所有源的最新资讯
python main.py

# 抓取指定源
python main.py --sources openai google_ai

# 指定时间范围（最近N小时）
python main.py --hours 24

# 导出为CSV
python main.py --output csv --file ai_news.csv
```

### 定时运行

```bash
# 每小时自动抓取
python scheduler.py --interval 1h

# 每天早上9点抓取
python scheduler.py --cron "0 9 * * *"
```

## 配置说明

编辑 `config.yaml` 文件自定义配置：

```yaml
# 数据源配置
sources:
  enabled: true
  update_interval: 3600  # 秒
  
# 翻译配置
translation:
  enabled: true
  target_lang: zh-CN
  
# 存储配置
storage:
  type: sqlite  # json, sqlite, csv
  path: ./data/ai_news.db
  
# 通知配置
notification:
  email:
    enabled: false
    smtp_server: smtp.gmail.com
    recipients: []
```

## 项目结构

```
ai_news_crawler/
├── main.py              # 主程序入口
├── scheduler.py         # 定时任务调度器
├── config.yaml          # 配置文件
├── requirements.txt     # 依赖列表
├── README.md           # 说明文档
├── src/
│   ├── __init__.py
│   ├── crawler.py      # 爬虫核心逻辑
│   ├── parser.py       # 内容解析器
│   ├── classifier.py   # 内容分类器
│   ├── translator.py   # 翻译模块
│   ├── storage.py      # 数据存储
│   └── sources/        # 数据源定义
│       ├── __init__.py
│       ├── rss_sources.py
│       └── api_sources.py
├── data/               # 数据存储目录
└── logs/              # 日志目录
```

## 输出格式

```json
{
  "id": "unique_id",
  "title": "文章标题",
  "title_en": "Article Title",
  "url": "https://...",
  "source": "OpenAI Blog",
  "category": "research",
  "publish_time": "2026-01-22T10:00:00",
  "summary": "文章摘要...",
  "tags": ["GPT", "LLM", "AI"],
  "fetch_time": "2026-01-22T12:00:00"
}
```

## 许可证

MIT License
