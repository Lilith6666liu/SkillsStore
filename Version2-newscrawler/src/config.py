"""
AI资讯抓取系统 - 配置文件
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# ==================== 路径配置 ====================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
INDEX_DIR = os.path.join(DATA_DIR, "index")
BY_CATEGORY_DIR = os.path.join(PROCESSED_DIR, "by_category")
BY_COMPANY_DIR = os.path.join(PROCESSED_DIR, "by_company")

# 确保目录存在
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(BY_CATEGORY_DIR, exist_ok=True)
os.makedirs(BY_COMPANY_DIR, exist_ok=True)
os.makedirs(INDEX_DIR, exist_ok=True)

# ==================== 时间配置 ====================
DEFAULT_DAYS = 7  # 默认抓取最近7天的内容
MAX_DAYS = 30  # 最大抓取时间范围

# ==================== 搜索配置 ====================
SEARCH_CONFIG = {
    "max_results_per_query": 10,  # 每个搜索关键词返回的最大结果数
    "max_concurrent_searches": 3,  # 最大并发搜索数
    "timeout": 30,  # 搜索超时时间（秒）
    "retry_times": 2,  # 重试次数
}

# ==================== 内容提取配置 ====================
EXTRACT_CONFIG = {
    "max_content_length": 5000,  # 提取内容的最大长度
    "timeout": 15,  # 提取超时时间（秒）
    "retry_times": 2,  # 重试次数
    "batch_size": 5,  # 批量提取大小
}

# ==================== 分类配置 ====================
CATEGORIES = {
    "news": {
        "name": "新闻",
        "name_en": "News",
        "keywords_zh": ["新闻", "动态", "报道", "消息"],
        "keywords_en": ["news", "breaking", "report", "update", "announcement"],
        "priority": 1,
    },
    "product": {
        "name": "产品发布",
        "name_en": "Product Launch",
        "keywords_zh": ["发布", "推出", "上线", "发布", "发布"],
        "keywords_en": ["launch", "release", "announce", "unveil", "introduce"],
        "priority": 2,
    },
    "technical": {
        "name": "技术解读",
        "name_en": "Technical Analysis",
        "keywords_zh": ["技术", "解析", "解读", "分析", "原理"],
        "keywords_en": ["technical", "analysis", "explained", "how it works", "deep dive"],
        "priority": 3,
    },
    "research": {
        "name": "学术突破",
        "name_en": "Research Breakthrough",
        "keywords_zh": ["论文", "研究", "突破", "学术", "科学家"],
        "keywords_en": ["research", "paper", "breakthrough", "study", "academic"],
        "priority": 4,
    },
    "interview": {
        "name": "人物访谈",
        "name_en": "Interview",
        "keywords_zh": ["访谈", "采访", "对话", "专访", "对话"],
        "keywords_en": ["interview", "talk", "conversation", "dialogue", "speaks"],
        "priority": 5,
    },
    "opinion": {
        "name": "观点分析",
        "name_en": "Opinion & Analysis",
        "keywords_zh": ["观点", "分析", "评论", "看法", "见解"],
        "keywords_en": ["opinion", "analysis", "commentary", "perspective", "view"],
        "priority": 6,
    },
}

# ==================== 公司配置 ====================
COMPANIES = {
    # 国际公司
    "OpenAI": {"type": "international", "keywords_zh": [], "keywords_en": ["OpenAI", "ChatGPT", "GPT"]},
    "Google": {"type": "international", "keywords_zh": ["谷歌", "Google"], "keywords_en": ["Google", "DeepMind", "Gemini"]},
    "Anthropic": {"type": "international", "keywords_zh": ["Anthropic"], "keywords_en": ["Anthropic", "Claude"]},
    "Meta": {"type": "international", "keywords_zh": ["Meta", "Facebook"], "keywords_en": ["Meta", "Llama", "Facebook"]},
    "Microsoft": {"type": "international", "keywords_zh": ["微软", "Microsoft"], "keywords_en": ["Microsoft", "Copilot"]},
    "Apple": {"type": "international", "keywords_zh": ["苹果", "Apple"], "keywords_en": ["Apple", "iPhone", "Siri"]},
    "Amazon": {"type": "international", "keywords_zh": ["亚马逊", "Amazon"], "keywords_en": ["Amazon", "AWS", "Alexa"]},
    "NVIDIA": {"type": "international", "keywords_zh": ["英伟达", "NVIDIA"], "keywords_en": ["NVIDIA", "GPU"]},
    
    # 国内公司
    "百度": {"type": "domestic", "keywords_zh": ["百度", "文心一言", "ERNIE Bot"], "keywords_en": ["Baidu", "ERNIE"]},
    "阿里巴巴": {"type": "domestic", "keywords_zh": ["阿里巴巴", "阿里", "通义千问"], "keywords_en": ["Alibaba", "Tongyi"]},
    "腾讯": {"type": "domestic", "keywords_zh": ["腾讯", "混元"], "keywords_en": ["Tencent", "Hunyuan"]},
    "字节跳动": {"type": "domestic", "keywords_zh": ["字节跳动", "抖音", "TikTok", "豆包"], "keywords_en": ["ByteDance", "TikTok", "Doubao"]},
    "智谱AI": {"type": "domestic", "keywords_zh": ["智谱AI", "ChatGLM", "GLM"], "keywords_en": ["Zhipu", "ChatGLM"]},
    "月之暗面": {"type": "domestic", "keywords_zh": ["月之暗面", "Kimi", "Moonshot"], "keywords_en": ["Moonshot", "Kimi"]},
    "华为": {"type": "domestic", "keywords_zh": ["华为", "盘古", "昇腾"], "keywords_en": ["Huawei", "Pangu"]},
    "科大讯飞": {"type": "domestic", "keywords_zh": ["科大讯飞", "星火"], "keywords_en": ["iFlytek", "Spark"]},
}

# ==================== 新闻源配置 ====================
NEWS_SOURCES = {
    "international": [
        {"name": "TechCrunch", "url": "https://techcrunch.com/category/artificial-intelligence/", "language": "en"},
        {"name": "The Verge", "url": "https://www.theverge.com/ai-artificial-intelligence", "language": "en"},
        {"name": "Wired", "url": "https://www.wired.com/tag/artificial-intelligence/", "language": "en"},
        {"name": "MIT Technology Review", "url": "https://www.technologyreview.com/topic/artificial-intelligence", "language": "en"},
        {"name": "Arxiv", "url": "https://arxiv.org/list/cs.AI/recent", "language": "en"},
        {"name": "Google Blog", "url": "https://blog.google/technology/ai/", "language": "en"},
        {"name": "OpenAI Blog", "url": "https://openai.com/blog", "language": "en"},
        {"name": "Anthropic Blog", "url": "https://www.anthropic.com/news", "language": "en"},
        {"name": "Meta AI", "url": "https://ai.meta.com/blog/", "language": "en"},
    ],
    "domestic": [
        {"name": "36氪", "url": "https://36kr.com/channel/technology", "language": "zh"},
        {"name": "虎嗅网", "url": "https://www.huxiu.com/channel/tech", "language": "zh"},
        {"name": "雷锋网", "url": "https://www.leiphone.com/", "language": "zh"},
        {"name": "机器之心", "url": "https://www.jiqizhixin.com/", "language": "zh"},
        {"name": "量子位", "url": "https://www.qbitai.com/", "language": "zh"},
        {"name": "新智元", "url": "https://arxiv.org/", "language": "zh"},
        {"name": "InfoQ", "url": "https://www.infoq.cn/", "language": "zh"},
        {"name": "CSDN", "url": "https://www.csdn.net/", "language": "zh"},
    ],
}

# ==================== 搜索关键词配置 ====================
SEARCH_KEYWORDS = {
    "general": {
        "zh": [
            "人工智能最新消息",
            "AI新闻 2024",
            "大模型最新进展",
            "生成式AI动态",
        ],
        "en": [
            "artificial intelligence news",
            "AI latest developments",
            "generative AI news",
            "large language models updates",
        ],
    },
    "companies": {
        "OpenAI": {"zh": ["OpenAI", "ChatGPT", "GPT-4"], "en": ["OpenAI", "ChatGPT", "GPT-4"]},
        "Google": {"zh": ["Google AI", "DeepMind", "Gemini"], "en": ["Google AI", "DeepMind", "Gemini"]},
        "Anthropic": {"zh": ["Anthropic", "Claude AI"], "en": ["Anthropic", "Claude AI"]},
        "Meta": {"zh": ["Meta AI", "Llama"], "en": ["Meta AI", "Llama"]},
        "Microsoft": {"zh": ["Microsoft AI", "Copilot"], "en": ["Microsoft AI", "Copilot"]},
        "百度": {"zh": ["百度AI", "文心一言", "ERNIE Bot"], "en": ["Baidu AI", "ERNIE Bot"]},
        "阿里巴巴": {"zh": ["阿里AI", "通义千问"], "en": ["Alibaba AI", "Tongyi Qwen"]},
        "腾讯": {"zh": ["腾讯AI", "混元大模型"], "en": ["Tencent AI", "Hunyuan"]},
        "字节跳动": {"zh": ["字节AI", "豆包AI"], "en": ["ByteDance AI", "Doubao AI"]},
        "智谱AI": {"zh": ["智谱AI", "ChatGLM"], "en": ["Zhipu AI", "ChatGLM"]},
        "月之暗面": {"zh": ["月之暗面", "Kimi AI"], "en": ["Moonshot AI", "Kimi AI"]},
    },
    "categories": {
        "news": {"zh": ["AI新闻", "人工智能新闻"], "en": ["AI news", "artificial intelligence news"]},
        "product": {"zh": ["AI产品发布", "AI新品发布"], "en": ["AI product launch", "AI release"]},
        "technical": {"zh": ["AI技术解读", "AI技术分析"], "en": ["AI technical analysis", "AI technology explained"]},
        "research": {"zh": ["AI研究", "AI论文突破"], "en": ["AI research", "AI breakthrough research"]},
        "interview": {"zh": ["AI访谈", "AI人物专访"], "en": ["AI interview", "AI expert interview"]},
        "opinion": {"zh": ["AI观点", "AI分析评论"], "en": ["AI opinion", "AI analysis"]},
    },
}

# ==================== 输出配置 ====================
OUTPUT_CONFIG = {
    "max_items_per_category": 50,  # 每个类别最多显示的项目数
    "max_summary_length": 300,  # 摘要最大长度
    "date_format": "%Y-%m-%d %H:%M:%S",  # 日期格式
    "json_indent": 2,  # JSON缩进
}

# ==================== 日志配置 ====================
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": os.path.join(PROJECT_ROOT, "logs", "ai_news_scraper.log"),
}
