# AI资讯实时抓取系统

## 📋 概述

AI资讯实时抓取系统是一个综合性工具，用于实时抓取AI领域的动态、新闻、知识、访谈等内容。该系统覆盖国内外头部AI公司的最新资讯，包括OpenAI、Google、Anthropic、Meta、百度、阿里巴巴、腾讯、字节跳动、智谱AI、月之暗面等。

## ✨ 功能特性

- **实时抓取**：快速获取最新AI资讯
- **多源聚合**：整合多个信息源，包括官方博客、科技媒体、学术论文等
- **智能分类**：自动将资讯分类为新闻、产品发布、技术解读、学术突破、人物访谈等
- **中英文支持**：支持国内外内容区分和双语搜索
- **搜索筛选**：支持按关键词、公司、类别、时间范围等筛选
- **数据导出**：支持JSON和CSV格式导出
- **增量更新**：自动跳过已抓取内容，避免重复

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 基本使用

#### 1. 获取最新AI资讯

```bash
python main.py --mode latest --days 7 --limit 50
```

#### 2. 获取特定公司动态

```bash
python main.py --mode company --companies OpenAI Google --days 7
```

#### 3. 获取特定类别资讯

```bash
python main.py --mode category --category research --days 7
```

#### 4. 获取国际AI资讯

```bash
python main.py --mode international --days 7
```

#### 5. 获取国内AI资讯

```bash
python main.py --mode domestic --days 7
```

#### 6. 自定义搜索

```bash
python main.py --mode search --keywords "GPT-5" "Claude 3" --days 7
```

#### 7. 生成统计报告

```bash
python main.py --mode report --days 7
```

## 📖 Python API 使用

### 基础用法

```python
import asyncio
from src.main import AINewsScraper

async def main():
    # 创建抓取器
    scraper = AINewsScraper()
    
    # 获取最新资讯
    items = await scraper.fetch_latest_news(days=7, limit=50)
    
    # 显示统计报告
    scraper.display_report(items)
    
    # 显示新闻列表
    scraper.display_news(items, max_items=20)
    
    # 导出数据
    scraper.export_data(items, format="json")
    
    return items

# 运行
items = asyncio.run(main())
```

### 高级用法

```python
import asyncio
from src.main import AINewsScraper

async def advanced_demo():
    scraper = AINewsScraper()
    
    # 1. 按公司获取动态
    openai_news = await scraper.fetch_by_company(
        companies=["OpenAI", "Anthropic"],
        days=7,
        limit=20
    )
    
    # 2. 按类别获取资讯
    research_news = await scraper.fetch_by_category(
        category="research",
        days=30,
        limit=20
    )
    
    # 3. 自定义搜索
    custom_news = await scraper.custom_search(
        keywords=["多模态", "视觉语言模型"],
        days=14,
        limit=30
    )
    
    # 4. 提取详细内容
    detailed_news = await scraper.fetch_latest_news(
        days=7,
        limit=10,
        extract_content=True,  # 提取详细内容
        save=True
    )
    
    return openai_news, research_news, custom_news, detailed_news

items = asyncio.run(advanced_demo())
```

### 使用各个模块

#### 搜索模块

```python
from src.searcher import NewsSearcher
import asyncio

async def search_demo():
    searcher = NewsSearcher()
    
    # 搜索最新资讯
    result = await searcher.search_latest_news(days=7, limit=20)
    print(f"找到 {result.total_results} 条新闻")
    
    # 按公司搜索
    result = await searcher.search_by_companies(["OpenAI", "Google"], days=7)
    
    # 按类别搜索
    result = await searcher.search_by_category("research", days=30)
    
    # 搜索国际新闻
    result = await searcher.search_international_news(days=7)
    
    # 搜索国内新闻
    result = await scraper.search_domestic_news(days=7)
    
    return result.items

items = asyncio.run(search_demo())
```

#### 数据处理模块

```python
from src.processor import NewsProcessor
from src.models import AINewsItem

def processing_demo():
    processor = NewsProcessor()
    
    # 假设已有新闻列表
    items = []
    
    # 处理新闻
    processed_items = processor.process_items(items)
    
    # 生成报告
    report = processor.generate_report(processed_items, days=7)
    
    print(f"总新闻数: {report.total_news}")
    print(f"国际新闻: {report.international_count}")
    print(f"国内新闻: {report.domestic_count}")
    
    # 过滤
    filtered = processor.filter_by_date(items, days=7)
    filtered = processor.filter_by_category(items, ["news", "product"])
    filtered = processor.filter_by_source_type(items, "international")
    
    # 排序
    sorted_by_importance = processor.sort_by_importance(items)
    sorted_by_date = processor.sort_by_date(items)
    
    # 分组
    by_category = processor.group_by_category(items)
    by_company = processor.group_by_company(items)
    
    # 保存
    processor.save_processed_data(items)
    
    return processed_items
```

## 📁 项目结构

```
ai-news-scraper/
├── src/
│   ├── __init__.py          # 包初始化
│   ├── config.py            # 配置文件
│   ├── models.py            # 数据模型
│   ├── searcher.py          # 搜索模块
│   ├── extractor.py         # 内容提取模块
│   ├── processor.py         # 数据处理模块
│   └── main.py              # 主程序
├── data/
│   ├── raw/                 # 原始数据
│   ├── processed/
│   │   ├── by_category/     # 按类别分类
│   │   └── by_company/      # 按公司分类
│   └── index/               # 索引文件
├── docs/
│   └── research_plan_ai_news_scraper.md
├── examples/
│   ├── basic_usage.py       # 基础用法示例
│   └── advanced_usage.py    # 高级用法示例
├── requirements.txt
└── README.md
```

## ⚙️ 配置说明

### 搜索配置 (SEARCH_CONFIG)

```python
SEARCH_CONFIG = {
    "max_results_per_query": 10,    # 每个搜索关键词返回的最大结果数
    "max_concurrent_searches": 3,   # 最大并发搜索数
    "timeout": 30,                   # 搜索超时时间（秒）
    "retry_times": 2,                # 重试次数
}
```

### 内容提取配置 (EXTRACT_CONFIG)

```python
EXTRACT_CONFIG = {
    "max_content_length": 5000,     # 提取内容的最大长度
    "timeout": 15,                   # 提取超时时间（秒）
    "retry_times": 2,                # 重试次数
    "batch_size": 5,                 # 批量提取大小
}
```

### 类别配置 (CATEGORIES)

系统支持以下类别：

- `news` - 新闻
- `product` - 产品发布
- `technical` - 技术解读
- `research` - 学术突破
- `interview` - 人物访谈
- `opinion` - 观点分析

### 公司配置 (COMPANIES)

系统支持以下公司：

**国际公司**：
- OpenAI
- Google
- Anthropic
- Meta
- Microsoft
- Apple
- Amazon
- NVIDIA

**国内公司**：
- 百度
- 阿里巴巴
- 腾讯
- 字节跳动
- 智谱AI
- 月之暗面
- 华为
- 科大讯飞

## 📊 数据模型

### AINewsItem

```python
{
    "id": "unique_id",
    "title": "新闻标题",
    "source": "来源名称",
    "source_type": "international|domestic",
    "category": "news|product|technical|research|interview|opinion",
    "publish_time": "发布时间",
    "url": "原文链接",
    "summary": "摘要",
    "content": "详细内容（可选）",
    "keywords": ["关键词1", "关键词2"],
    "fetch_time": "抓取时间",
    "companies": ["OpenAI", "Google"],
    "language": "zh|en|mixed",
    "importance": 1-10
}
```

## 🔧 高级功能

### 增量更新

```python
from src.extractor import IncrementalExtractor

async def incremental_demo():
    extractor = IncrementalExtractor()
    
    # 加载已处理URL
    extractor.load_processed_urls("data/index/processed_urls.json")
    
    # 增量提取（只提取新内容）
    items = await extractor.extract_new_items(all_items, show_progress=True)
    
    # 保存已处理URL
    extractor.save_processed_urls("data/index/processed_urls.json")
    
    return items
```

### 数据搜索

```python
from src.processor import DataSearcher

def search_demo():
    searcher = DataSearcher()
    
    # 加载数据
    items = searcher.load_latest()
    
    # 搜索
    results = searcher.search_items(
        items,
        query="GPT",                    # 关键词搜索
        categories=["news", "product"], # 类别过滤
        companies=["OpenAI"],           # 公司过滤
        source_type="international",    # 来源类型
        days=7                          # 日期过滤
    )
    
    return results
```

## 📝 命令行参数

```
--mode            运行模式 (latest|company|category|international|domestic|search|demo|report)
--keywords        搜索关键词
--companies       指定公司
--category        新闻类别
--days            时间范围（天），默认7天
--limit           最大数量限制，默认50
--extract         是否提取详细内容
--no-save         不保存数据
--output          输出格式 (json|csv)
--display         显示内容 (news|report|all)
```

## ⚠️ 注意事项

1. **API限制**：系统使用模拟数据进行演示，实际使用需要配置MCP工具
2. **频率限制**：请勿过于频繁抓取，建议每次间隔至少5分钟
3. **数据验证**：抓取的数据需要验证，建议人工审核
4. **存储空间**：大量抓取会占用存储空间，建议定期清理

## 📦 依赖

- Python 3.8+
- 异步支持 (asyncio)
- MCP工具（可选）

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 👨‍💻 作者

Matrix Agent

---

创建时间: 2026-01-22
版本: 1.0.0
