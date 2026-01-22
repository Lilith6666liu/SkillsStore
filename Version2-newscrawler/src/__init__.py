"""
AI资讯实时抓取系统

实时抓取AI动态、新闻、知识、访谈的综合性系统

功能：
- 实时抓取最新AI资讯
- 聚合多个信息源
- 按类别分类（新闻/知识/访谈等）
- 支持国内外内容区分
- 提供搜索和筛选功能

作者: Matrix Agent
版本: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Matrix Agent"

from .models import AINewsItem, SearchResult, CategoryStats, CompanyStats, ReportData, DataStore
from .searcher import NewsSearcher
from .extractor import ContentExtractor, IncrementalExtractor
from .processor import NewsProcessor, DataSearcher
from .main import AINewsScraper

__all__ = [
    "AINewsItem",
    "SearchResult", 
    "CategoryStats",
    "CompanyStats",
    "ReportData",
    "DataStore",
    "NewsSearcher",
    "ContentExtractor",
    "IncrementalExtractor",
    "NewsProcessor",
    "DataSearcher",
    "AINewsScraper",
]
