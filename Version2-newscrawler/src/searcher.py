"""
AI资讯抓取系统 - 搜索模块

功能：
- 使用MCP工具进行并行搜索
- 支持按关键词、时间范围、来源筛选
- 支持中英文搜索
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    SEARCH_CONFIG, 
    SEARCH_KEYWORDS, 
    COMPANIES, 
    CATEGORIES,
    NEWS_SOURCES
)
from models import AINewsItem, SearchResult


class NewsSearcher:
    """AI新闻搜索器"""

    def __init__(self, use_mcp: bool = True):
        """
        初始化搜索器
        
        Args:
            use_mcp: 是否使用MCP工具
        """
        self.use_mcp = use_mcp
        self.mcp_client = None
        if use_mcp:
            try:
                # 尝试导入MCP工具
                from mcp.client import MCPClient
                self.mcp_client = MCPClient()
                print("✓ MCP客户端已初始化")
            except ImportError:
                print("⚠ MCP工具未安装，将使用模拟搜索")
                self.use_mcp = False

    def _build_search_queries(self, keywords: List[str], days: int = 7, 
                              language: str = "all") -> List[Dict[str, Any]]:
        """
        构建搜索查询列表
        
        Args:
            keywords: 关键词列表
            days: 时间范围（天）
            language: 语言（all/zh/en）
            
        Returns:
            搜索查询列表
        """
        queries = []
        date_str = datetime.now().strftime("%Y-%m-%d")
        
        for keyword in keywords:
            if language in ["all", "zh"]:
                # 中文搜索
                queries.append({
                    "query": f"{keyword} 最新消息",
                    "language": "zh",
                    "date_range": f"d{days}",
                    "num_results": SEARCH_CONFIG["max_results_per_query"]
                })
            
            if language in ["all", "en"]:
                # 英文搜索
                queries.append({
                    "query": f"{keyword} latest news",
                    "language": "en",
                    "date_range": f"d{days}",
                    "num_results": SEARCH_CONFIG["max_results_per_query"]
                })
        
        return queries

    def _parse_search_result(self, result: Dict[str, Any], query: str) -> List[AINewsItem]:
        """
        解析搜索结果
        
        Args:
            result: 搜索结果
            query: 搜索关键词
            
        Returns:
            新闻列表
        """
        items = []
        
        # 尝试解析MCP搜索结果
        if "results" in result:
            for r in result["results"]:
                try:
                    # 提取关键信息
                    title = r.get("title", "")
                    url = r.get("url", "")
                    snippet = r.get("snippet", "")
                    source = r.get("source", "")
                    publish_time = r.get("publish_time", "")
                    
                    # 如果没有时间，使用当前时间
                    if not publish_time:
                        publish_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # 创建新闻条目
                    item = AINewsItem(
                        title=title,
                        source=source or "Unknown",
                        source_type=self._detect_source_type(url),
                        category="news",  # 默认为新闻，后续会重新分类
                        publish_time=publish_time,
                        url=url,
                        summary=snippet[:300] if snippet else "",
                        keywords=[query],
                    )
                    
                    # 检测提到的公司
                    item.companies = self._detect_companies(title + " " + snippet)
                    
                    # 检测语言
                    item.language = self._detect_language(title)
                    
                    items.append(item)
                except Exception as e:
                    print(f"解析搜索结果失败: {e}")
                    continue
        
        return items

    def _detect_source_type(self, url: str) -> str:
        """检测来源类型（国际/国内）"""
        domestic_keywords = [
            "36kr.com", "huxiu.com", "leiphone.com", "jiqizhixin.com",
            "qbitai.com", "infoq.cn", "csdn.net", "baidu.com", "alibaba.com",
            "tencent.com", "bytedance.com", "163.com", "sina.com.cn"
        ]
        
        for keyword in domestic_keywords:
            if keyword in url.lower():
                return "domestic"
        
        return "international"

    def _detect_companies(self, text: str) -> List[str]:
        """检测文本中提到的公司"""
        companies = []
        text_lower = text.lower()
        
        for company, info in COMPANIES.items():
            # 检查英文关键词
            for keyword in info.get("keywords_en", []):
                if keyword.lower() in text_lower:
                    companies.append(company)
                    break
            
            # 检查中文关键词
            for keyword in info.get("keywords_zh", []):
                if keyword in text:
                    if company not in companies:
                        companies.append(company)
                    break
        
        return companies

    def _detect_language(self, text: str) -> str:
        """检测语言"""
        chinese_chars = 0
        english_words = 0
        
        for char in text:
            if '\u4e00' <= char <= '\u9fff':
                chinese_chars += 1
            elif char.isalpha():
                english_words += 1
        
        if chinese_chars > english_words:
            return "zh"
        elif english_words > chinese_chars:
            return "en"
        else:
            return "mixed"

    async def search(self, keywords: List[str], days: int = 7, 
                    language: str = "all", max_results: int = 50) -> SearchResult:
        """
        搜索AI新闻
        
        Args:
            keywords: 关键词列表
            days: 时间范围（天）
            language: 语言
            max_results: 最大结果数
            
        Returns:
            搜索结果
        """
        print(f"\n🔍 开始搜索...")
        print(f"   关键词: {keywords}")
        print(f"   时间范围: 最近{days}天")
        print(f"   语言: {language}")
        
        all_items = []
        
        if self.use_mcp:
            # 使用MCP工具搜索
            queries = self._build_search_queries(keywords, days, language)
            
            try:
                # 使用MCP batch_web_search工具
                from mcp.tools import batch_web_search
                
                # 限制并发数
                results = []
                for i in range(0, len(queries), SEARCH_CONFIG["max_concurrent_searches"]):
                    batch = queries[i:i + SEARCH_CONFIG["max_concurrent_searches"]]
                    batch_results = await batch_web_search(queries=batch)
                    results.extend(batch_results)
                
                # 解析结果
                for query, result in zip(queries, results):
                    items = self._parse_search_result(result, query["query"])
                    all_items.extend(items)
                    
            except Exception as e:
                print(f"⚠ MCP搜索失败: {e}")
                print("   使用模拟数据进行演示...")
                all_items = self._generate_mock_results(keywords)
        else:
            # 使用模拟搜索
            print("   使用模拟搜索...")
            all_items = self._generate_mock_results(keywords)
        
        # 去重
        unique_items = self._deduplicate_items(all_items)
        
        # 限制结果数量
        unique_items = unique_items[:max_results]
        
        print(f"   ✓ 找到 {len(unique_items)} 条相关资讯")
        
        return SearchResult(
            query="; ".join(keywords),
            total_results=len(unique_items),
            items=unique_items
        )

    def _generate_mock_results(self, keywords: List[str]) -> List[AINewsItem]:
        """生成模拟搜索结果（用于测试）"""
        mock_news = [
            {
                "title": "OpenAI发布GPT-5预览版，性能提升显著",
                "source": "TechCrunch",
                "source_type": "international",
                "url": "https://techcrunch.com/2024/01/20/openai-gpt-5-preview/",
                "summary": "OpenAI今日宣布推出GPT-5预览版，新模型在推理能力和多模态处理方面实现重大突破...",
                "companies": ["OpenAI"],
                "category": "product",
            },
            {
                "title": "谷歌DeepMind发布Gemini 1.5 Pro，支持超长上下文",
                "source": "The Verge",
                "source_type": "international",
                "url": "https://www.theverge.com/2024/01/19/google-gemini-1-5-pro/",
                "summary": "谷歌DeepMind发布新一代Gemini 1.5 Pro模型，支持最高200万token的上下文窗口...",
                "companies": ["Google"],
                "category": "product",
            },
            {
                "title": "百度文心一言4.0发布，中文理解能力再升级",
                "source": "36氪",
                "source_type": "domestic",
                "url": "https://36kr.com/p/123456",
                "summary": "百度今日发布文心一言4.0，新版本在中文语义理解和生成方面取得显著进步...",
                "companies": ["百度"],
                "category": "product",
            },
            {
                "title": "Anthropic发布Claude 3系列模型，性能超越GPT-4",
                "source": "Wired",
                "source_type": "international",
                "url": "https://wired.com/2024/01/18/anthropic-claude-3/",
                "summary": "Anthropic推出Claude 3系列模型，包括Haiku、Sonnet和Opus三个版本，其中Opus版本在多项基准测试中超越GPT-4...",
                "companies": ["Anthropic"],
                "category": "product",
            },
            {
                "title": "阿里云通义千问Qwen2-VL发布，支持视觉理解",
                "source": "虎嗅网",
                "source_type": "domestic",
                "url": "https://www.huxiu.com/article/789012",
                "summary": "阿里云发布通义千问Qwen2-VL视觉语言模型，在图像理解和视觉问答任务上表现优异...",
                "companies": ["阿里巴巴"],
                "category": "product",
            },
            {
                "title": "字节跳动豆包大模型API正式开放，支持128K上下文",
                "source": "机器之心",
                "source_type": "domestic",
                "url": "https://www.jiqizhixin.com/articles/2024-01-17",
                "summary": "字节跳动宣布豆包大模型API正式开放，支持最高128K的上下文窗口，企业用户可申请调用...",
                "companies": ["字节跳动"],
                "category": "product",
            },
            {
                "title": "Meta发布Llama 3.1 405B，开源模型性能创新高",
                "source": "Meta AI Blog",
                "source_type": "international",
                "url": "https://ai.meta.com/blog/llama-3-1-405B/",
                "summary": "Meta发布Llama 3.1 405B参数开源模型，在多项评测中达到闭源模型水平...",
                "companies": ["Meta"],
                "category": "research",
            },
            {
                "title": "智谱AI发布GLM-4系列模型，支持128K上下文",
                "source": "量子位",
                "source_type": "domestic",
                "url": "https://www.qbitai.com/article/345678",
                "summary": "智谱AI发布GLM-4系列模型，新模型在长文本理解和生成方面表现突出...",
                "companies": ["智谱AI"],
                "category": "product",
            },
            {
                "title": "微软Copilot企业版发布，集成GPT-4 Turbo",
                "source": "Microsoft Blog",
                "source_type": "international",
                "url": "https://blogs.microsoft.com/blog/2024/01/16/",
                "summary": "微软宣布Copilot企业版正式发布，新版本集成GPT-4 Turbo，支持更强的企业级AI应用...",
                "companies": ["Microsoft"],
                "category": "product",
            },
            {
                "title": "月之暗面Kimi智能助手升级，支持200K上下文",
                "source": "36氪",
                "source_type": "domestic",
                "url": "https://36kr.com/p/901234",
                "summary": "月之暗面宣布Kimi智能助手升级至支持200K上下文窗口，可处理更长的文档...",
                "companies": ["月之暗面"],
                "category": "product",
            },
            {
                "title": "斯坦福大学发布最新AI研究，揭示大模型涌现能力",
                "source": "MIT Technology Review",
                "source_type": "international",
                "url": "https://technologyreview.com/2024/01/15/",
                "summary": "斯坦福大学研究团队发布最新论文，深入揭示大语言模型的涌现能力及其工作机制...",
                "companies": [],
                "category": "research",
            },
            {
                "title": "OpenAI CEO Altman访谈：AI安全与未来展望",
                "source": "The New York Times",
                "source_type": "international",
                "url": "https://nytimes.com/2024/01/14/",
                "summary": "OpenAI CEO Sam Altman接受专访，分享对AI安全、监管和未来发展的见解...",
                "companies": ["OpenAI"],
                "category": "interview",
            },
        ]
        
        items = []
        for news in mock_news:
            item = AINewsItem(
                title=news["title"],
                source=news["source"],
                source_type=news["source_type"],
                category=news["category"],
                publish_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                url=news["url"],
                summary=news["summary"],
                keywords=keywords,
                companies=news["companies"],
                language="zh" if news["source_type"] == "domestic" else "en",
            )
            items.append(item)
        
        return items

    def _deduplicate_items(self, items: List[AINewsItem]) -> List[AINewsItem]:
        """去重"""
        seen_urls = set()
        unique_items = []
        
        for item in items:
            if item.url not in seen_urls:
                seen_urls.add(item.url)
                unique_items.append(item)
        
        return unique_items

    def search_by_companies(self, companies: List[str], days: int = 7) -> SearchResult:
        """
        按公司搜索新闻
        
        Args:
            companies: 公司列表
            days: 时间范围
            
        Returns:
            搜索结果
        """
        keywords = []
        for company in companies:
            if company in SEARCH_KEYWORDS["companies"]:
                keywords.extend(SEARCH_KEYWORDS["companies"][company].get("zh", []))
                keywords.extend(SEARCH_KEYWORDS["companies"][company].get("en", []))
        
        return self.search(keywords, days, language="all")

    def search_by_category(self, category: str, days: int = 7) -> SearchResult:
        """
        按类别搜索新闻
        
        Args:
            category: 类别
            days: 时间范围
            
        Returns:
            搜索结果
        """
        if category not in SEARCH_KEYWORDS["categories"]:
            print(f"⚠ 未知类别: {category}")
            return SearchResult(query=category, total_results=0, items=[])
        
        keywords = []
        keywords.extend(SEARCH_KEYWORDS["categories"][category].get("zh", []))
        keywords.extend(SEARCH_KEYWORDS["categories"][category].get("en", []))
        
        return self.search(keywords, days, language="all")

    def search_latest_news(self, days: int = 7, limit: int = 50) -> SearchResult:
        """
        搜索最新AI新闻
        
        Args:
            days: 时间范围
            limit: 限制数量
            
        Returns:
            搜索结果
        """
        keywords = []
        keywords.extend(SEARCH_KEYWORDS["general"]["zh"])
        keywords.extend(SEARCH_KEYWORDS["general"]["en"])
        
        return self.search(keywords, days, language="all", max_results=limit)

    def search_international_news(self, days: int = 7, limit: int = 30) -> SearchResult:
        """
        搜索国际AI新闻
        
        Args:
            days: 时间范围
            limit: 限制数量
            
        Returns:
            搜索结果
        """
        keywords = SEARCH_KEYWORDS["general"]["en"]
        return self.search(list(keywords), days, language="en", max_results=limit)

    def search_domestic_news(self, days: int = 7, limit: int = 30) -> SearchResult:
        """
        搜索国内AI新闻
        
        Args:
            days: 时间范围
            limit: 限制数量
            
        Returns:
            搜索结果
        """
        keywords = SEARCH_KEYWORDS["general"]["zh"]
        return self.search(list(keywords), days, language="zh", max_results=limit)


# 异步支持
import asyncio


async def async_search_demo():
    """异步搜索演示"""
    searcher = NewsSearcher()
    result = await searcher.search_latest_news(days=7, limit=10)
    print(f"\n找到 {result.total_results} 条新闻")
    for item in result.items[:3]:
        print(f"  - {item.title}")
        print(f"    来源: {item.source} | 类别: {item.category}")
    return result


if __name__ == "__main__":
    # 运行演示
    result = asyncio.run(async_search_demo())
