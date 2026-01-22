# AI资讯实时抓取系统 - 技术方案与实现计划

## 项目概述
创建一个实时抓取AI动态、新闻、知识、访谈的综合性系统，覆盖国内外AI领域的最新资讯。

## 技术架构

### 核心组件
1. **数据采集层**：使用MCP工具进行网页搜索和内容提取
2. **数据处理层**：对抓取的内容进行清洗、分类、格式化
3. **数据存储层**：使用JSON文件进行本地存储，支持增量更新
4. **数据展示层**：提供API接口和命令行展示功能

### 技术栈
- Python 3.8+
- MCP Tools (batch_web_search, extract_content_from_websites)
- JSON (数据存储)
- 定时任务支持（可选）

## 功能模块

### 1. 搜索模块
- 使用batch_web_search进行并行搜索
- 支持按关键词、时间范围、来源筛选
- 支持中英文搜索

### 2. 内容提取模块
- 使用extract_content_from_websites提取详细页面内容
- 智能提取标题、来源、时间、摘要、链接
- 支持增量更新，避免重复抓取

### 3. 数据分类模块
- 新闻(News)
- 产品发布(Product)
- 技术解读(Technical)
- 学术突破(Research)
- 人物访谈(Interview)
- 观点分析(Opinion)

### 4. 数据存储模块
- 按类别组织数据
- 支持时间索引
- 自动去重

### 5. 展示模块
- 命令行输出
- API接口
- 统计报告

## 实现步骤

### 阶段1：基础架构（已完成）
- [x] 创建项目结构
- [x] 制定技术方案
- [x] 设计数据模型

### 阶段2：核心模块开发
- [ ] 1.1 创建配置模块（config.py）
- [ ] 1.2 创建数据模型（models.py）
- [ ] 1.3 实现搜索模块（searcher.py）
- [ ] 1.4 实现内容提取模块（extractor.py）
- [ ] 1.5 实现数据处理模块（processor.py）

### 阶段3：主程序开发
- [ ] 2.1 创建主入口（main.py）
- [ ] 2.2 实现命令行参数
- [ ] 2.3 实现增量更新逻辑
- [ ] 2.4 实现数据展示功能

### 阶段4：测试和文档
- [ ] 3.1 编写使用示例
- [ ] 3.2 创建README文档
- [ ] 3.3 性能测试和优化

## 数据模型设计

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
    "companies": ["OpenAI", "Google"]  # 提到的公司
}
```

### 数据存储结构
```
data/
├── raw/
│   ├── 2024/
│   │   ├── 01/
│   │   │   ├── search_results.json
│   │   │   └── extracted_content.json
├── processed/
│   ├── by_category/
│   │   ├── news.json
│   │   ├── product.json
│   │   ├── technical.json
│   │   ├── research.json
│   │   ├── interview.json
│   │   └── opinion.json
│   ├── by_company/
│   │   ├── openai.json
│   │   ├── google.json
│   │   └── ...
│   └── latest.json
└── index/
    └── search_index.json
```

## 搜索策略

### 国际动态关键词
- "OpenAI news latest"
- "Google AI latest developments"
- "Anthropic Claude news"
- "Meta AI research"
- "AI breakthrough 2024"

### 国内动态关键词
- "百度 AI 最新消息"
- "阿里巴巴 AI 动态"
- "腾讯 AI 人工智能"
- "字节跳动 AI 进展"
- "智谱AI 最新"
- "月之暗面 AI"

### 分类关键词
- AI新闻: "AI news", "人工智能新闻"
- 产品发布: "AI product launch", "AI产品发布"
- 技术解读: "AI technical analysis", "AI技术解读"
- 学术突破: "AI research paper", "AI学术突破"
- 人物访谈: "AI interview", "AI人物访谈"

## API设计

### 命令行接口
```bash
python main.py --mode search --keywords "OpenAI" --days 7
python main.py --mode fetch --url "https://..."
python main.py --mode report --category news --limit 20
python main.py --mode serve --port 8080
```

### Python API
```python
from ai_news_scraper import AINewsScraper

scraper = AINewsScraper()
news = scraper.search(keywords="AI news", days=7)
scraper.process_and_save(news)
scraper.display(news)
```

## 质量控制
1. **去重**：基于标题和URL去重
2. **验证**：验证链接有效性
3. **分类**：使用关键词和规则进行分类
4. **排序**：按时间和重要性排序

## 性能优化
1. **并发搜索**：同时搜索多个关键词
2. **增量更新**：只抓取新内容
3. **缓存机制**：缓存已抓取的内容
4. **批量处理**：批量提取和处理

## 监控和日志
- 详细的日志记录
- 错误处理和重试机制
- 统计信息展示
- 进度显示

## 扩展性
- 支持更多数据源
- 支持更多分类
- 支持机器学习分类
- 支持定时任务
- 支持API服务

---
创建时间: 2026-01-22
预计完成时间: 2-3小时
