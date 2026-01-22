"""
AI资讯抓取系统 - 内容提取模块

功能：
- 使用MCP工具提取网页详细内容
- 智能提取标题、来源、时间、摘要、链接
- 支持批量处理和增量更新
"""

import asyncio
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import EXTRACT_CONFIG
from models import AINewsItem


class ContentExtractor:
    """内容提取器"""

    def __init__(self, use_mcp: bool = True):
        """
        初始化内容提取器
        
        Args:
            use_mcp: 是否使用MCP工具
        """
        self.use_mcp = use_mcp
        self.cache = {}  # 简单缓存

    async def extract_from_url(self, url: str, prompt: str = None) -> Dict[str, Any]:
        """
        从URL提取内容
        
        Args:
            url: 网页URL
            prompt: 提取提示词
            
        Returns:
            提取的内容
        """
        if url in self.cache:
            print(f"   ✓ 使用缓存: {url[:50]}...")
            return self.cache[url]
        
        if self.use_mcp:
            try:
                # 使用MCP extract_content_from_websites工具
                from mcp.tools import extract_content_from_websites
                
                if prompt is None:
                    prompt = """请提取以下信息：
1. 文章标题
2. 发布时间和来源
3. 主要内容摘要（200字以内）
4. 关键观点和结论
5. 提到的公司或产品
"""
                
                result = await extract_content_from_websites(
                    tasks=[{
                        "url": url,
                        "prompt": prompt,
                    }]
                )
                
                if result and len(result) > 0:
                    extracted = result[0]
                    self.cache[url] = extracted
                    return extracted
                    
            except Exception as e:
                print(f"   ⚠ MCP提取失败: {e}")
                # 返回模拟数据
                return self._generate_mock_extraction(url)

        # 返回模拟数据
        return self._generate_mock_extraction(url)

    async def extract_batch(self, items: List[AINewsItem], 
                           show_progress: bool = True) -> List[AINewsItem]:
        """
        批量提取内容
        
        Args:
            items: 新闻列表
            show_progress: 显示进度
            
        Returns:
            更新后的新闻列表
        """
        if show_progress:
            print(f"\n📄 开始提取详细内容...")
            print(f"   共 {len(items)} 条新闻")
        
        updated_items = []
        
        for i, item in enumerate(items):
            if show_progress:
                print(f"   进度: {i+1}/{len(items)}", end="\r")
            
            try:
                # 提取内容
                extracted = await self.extract_from_url(item.url)
                
                # 更新新闻条目
                if extracted:
                    # 更新摘要
                    if "summary" in extracted and extracted["summary"]:
                        item.summary = extracted["summary"]
                    
                    # 更新发布时间
                    if "publish_time" in extracted and extracted["publish_time"]:
                        item.publish_time = extracted["publish_time"]
                    
                    # 提取详细内容
                    if "content" in extracted and extracted["content"]:
                        item.content = extracted["content"][:EXTRACT_CONFIG["max_content_length"]]
                    
                    # 更新关键词
                    if "keywords" in extracted and extracted["keywords"]:
                        item.keywords = list(set(item.keywords + extracted["keywords"]))
                
                updated_items.append(item)
                
                # 添加延迟，避免请求过快
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"   ⚠ 提取失败: {e}")
                updated_items.append(item)
        
        if show_progress:
            print(f"   ✓ 完成提取 {len(updated_items)} 条新闻")
        
        return updated_items

    def _generate_mock_extraction(self, url: str) -> Dict[str, Any]:
        """生成模拟提取结果（用于测试）"""
        return {
            "title": "AI新闻详细报道",
            "publish_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source": "模拟来源",
            "summary": "这是根据URL生成的模拟摘要内容。实际使用时会从网页中提取真实内容。",
            "content": """这是文章的详细内容部分。在实际应用中，这里会包含从网页中提取的完整文章内容。
            
文章主要讨论了AI领域的最新发展，包括：
1. 新模型发布和技术突破
2. 行业应用案例
3. 未来发展趋势

AI技术正在快速发展，对各行各业都产生深远影响。""",
            "keywords": ["AI", "人工智能", "大模型", "技术突破"],
            "companies_mentioned": [],
        }

    def extract_article_content(self, content: str) -> Dict[str, Any]:
        """
        从文章内容中提取结构化信息
        
        Args:
            content: 文章内容
            
        Returns:
            提取的信息
        """
        result = {
            "word_count": len(content),
            "paragraph_count": len(content.split("\n\n")),
            "has_numbers": any(c.isdigit() for c in content),
            "has_links": "http" in content.lower(),
        }
        
        return result

    def summarize_content(self, content: str, max_length: int = 200) -> str:
        """
        总结内容
        
        Args:
            content: 内容
            max_length: 最大长度
            
        Returns:
            总结
        """
        # 简单截取
        if len(content) <= max_length:
            return content
        
        # 尝试在句子边界截断
        for i in range(min(max_length, len(content) - 1), max_length - 50, -1):
            if content[i] in "。！？.!?\n":
                return content[:i+1]
        
        return content[:max_length] + "..."


class IncrementalExtractor:
    """增量提取器，支持增量更新"""

    def __init__(self, extractor: ContentExtractor = None):
        """
        初始化增量提取器
        
        Args:
            extractor: 内容提取器
        """
        self.extractor = extractor or ContentExtractor()
        self.processed_urls = set()

    def load_processed_urls(self, filepath: str) -> None:
        """
        加载已处理的URL列表
        
        Args:
            filepath: 文件路径
        """
        try:
            import json
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.processed_urls = set(data.get("processed_urls", []))
            print(f"   ✓ 已加载 {len(self.processed_urls)} 个已处理URL")
        except Exception as e:
            print(f"   ⚠ 加载已处理URL失败: {e}")

    def save_processed_urls(self, filepath: str) -> None:
        """
        保存已处理的URL列表
        
        Args:
            filepath: 文件路径
        """
        try:
            import json
            data = {
                "processed_urls": list(self.processed_urls),
                "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"   ✓ 已保存 {len(self.processed_urls)} 个已处理URL")
        except Exception as e:
            print(f"   ⚠ 保存已处理URL失败: {e}")

    async def extract_new_items(self, items: List[AINewsItem], 
                               show_progress: bool = True) -> List[AINewsItem]:
        """
        只提取新项目
        
        Args:
            items: 新闻列表
            show_progress: 显示进度
            
        Returns:
            更新后的新闻列表
        """
        new_items = []
        
        for item in items:
            if item.url not in self.processed_urls:
                new_items.append(item)
        
        if show_progress:
            print(f"\n🔄 增量提取")
            print(f"   新项目: {len(new_items)}")
            print(f"   已跳过: {len(items) - len(new_items)}")
        
        # 提取新项目
        updated_items = await self.extractor.extract_batch(new_items, show_progress)
        
        # 更新已处理URL集合
        for item in new_items:
            self.processed_urls.add(item.url)
        
        return updated_items


async def extraction_demo():
    """提取演示"""
    extractor = ContentExtractor()
    
    # 测试URL
    test_urls = [
        "https://openai.com/blog",
        "https://www.google.com/ai/",
    ]
    
    print("🧪 内容提取测试")
    for url in test_urls:
        print(f"\n   提取: {url}")
        result = await extractor.extract_from_url(url)
        print(f"   标题: {result.get('title', 'N/A')}")
        print(f"   摘要: {result.get('summary', 'N/A')[:100]}...")


if __name__ == "__main__":
    # 运行演示
    asyncio.run(extraction_demo())
