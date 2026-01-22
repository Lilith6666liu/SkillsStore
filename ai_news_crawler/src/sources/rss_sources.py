"""
AI资讯RSS源配置
包含国内外主要AI资讯源的RSS地址
"""

RSS_SOURCES = {
    # 国际源
    "openai": {
        "name": "OpenAI Blog",
        "url": "https://openai.com/blog/rss.xml",
        "language": "en",
        "category": "research"
    },
    "google_ai": {
        "name": "Google AI Blog",
        "url": "https://ai.googleblog.com/feeds/posts/default",
        "language": "en",
        "category": "research"
    },
    "huggingface": {
        "name": "Hugging Face Blog",
        "url": "https://huggingface.co/blog/feed.xml",
        "language": "en",
        "category": "research"
    },
    "techcrunch_ai": {
        "name": "TechCrunch AI",
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "language": "en",
        "category": "news"
    },
    "venturebeat_ai": {
        "name": "VentureBeat AI",
        "url": "https://venturebeat.com/category/ai/feed/",
        "language": "en",
        "category": "news"
    },
    "mit_tech_review": {
        "name": "MIT Technology Review AI",
        "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed",
        "language": "en",
        "category": "news"
    },
    "arxiv_ai": {
        "name": "arXiv AI",
        "url": "https://arxiv.org/rss/cs.AI",
        "language": "en",
        "category": "research"
    },
    "arxiv_lg": {
        "name": "arXiv Machine Learning",
        "url": "https://arxiv.org/rss/cs.LG",
        "language": "en",
        "category": "research"
    },
    "arxiv_cl": {
        "name": "arXiv Computation and Language",
        "url": "https://arxiv.org/rss/cs.CL",
        "language": "en",
        "category": "research"
    },
    "aws_ml": {
        "name": "AWS Machine Learning Blog",
        "url": "https://aws.amazon.com/blogs/machine-learning/feed/",
        "language": "en",
        "category": "tutorial"
    },
    "deepmind": {
        "name": "DeepMind Blog",
        "url": "https://deepmind.google/blog/rss.xml",
        "language": "en",
        "category": "research"
    },
    
    # 国内源
    "jiqizhixin": {
        "name": "机器之心",
        "url": "https://www.jiqizhixin.com/rss",
        "language": "zh",
        "category": "news"
    },
    "qbitai": {
        "name": "量子位",
        "url": "https://www.qbitai.com/feed",
        "language": "zh",
        "category": "news"
    },
    "leiphone_ai": {
        "name": "雷锋网AI",
        "url": "https://www.leiphone.com/category/ai/feed",
        "language": "zh",
        "category": "news"
    },
    "36kr_ai": {
        "name": "36氪AI",
        "url": "https://36kr.com/feed/ai",
        "language": "zh",
        "category": "news"
    },
    "aichinese": {
        "name": "AI科技评论",
        "url": "https://www.leiphone.com/category/academic/feed",
        "language": "zh",
        "category": "research"
    }
}


def get_all_sources():
    """获取所有数据源"""
    return RSS_SOURCES


def get_sources_by_language(language):
    """根据语言筛选数据源"""
    return {k: v for k, v in RSS_SOURCES.items() if v["language"] == language}


def get_sources_by_category(category):
    """根据分类筛选数据源"""
    return {k: v for k, v in RSS_SOURCES.items() if v["category"] == category}


def get_source(source_id):
    """获取单个数据源"""
    return RSS_SOURCES.get(source_id)
