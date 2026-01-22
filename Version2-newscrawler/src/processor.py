"""
AI资讯抓取系统 - 数据处理模块

功能：
- 对抓取的内容进行清洗、分类、格式化
- 按类别组织数据
- 自动去重
- 生成统计报告
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import Counter
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import CATEGORIES, COMPANIES, OUTPUT_CONFIG
from models import (
    AINewsItem, 
    CategoryStats, 
    CompanyStats, 
    ReportData,
    DataStore
)


class NewsProcessor:
    """新闻处理器"""

    def __init__(self, data_dir: str = None):
        """
        初始化处理器
        
        Args:
            data_dir: 数据目录
        """
        self.data_dir = data_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data"
        )
        self.store = DataStore(self.data_dir)

    def clean_text(self, text: str) -> str:
        """
        清洗文本
        
        Args:
            text: 原始文本
            
        Returns:
            清洗后的文本
        """
        if not text:
            return ""
        
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text)
        
        # 移除特殊字符（保留中文、英文、数字、常用标点）
        text = re.sub(r'[^\w\s\u4e00-\u9fff，。！？、""''【】（）()\-—.,!?\'\"]', '', text)
        
        return text.strip()

    def categorize_item(self, item: AINewsItem) -> str:
        """
        自动分类新闻
        
        Args:
            item: 新闻条目
            
        Returns:
            分类名称
        """
        # 合并标题和摘要进行分析
        text = f"{item.title} {item.summary}".lower()
        
        # 计算每个类别的匹配分数
        scores = {}
        
        for category, info in CATEGORIES.items():
            score = 0
            
            # 检查关键词
            for keyword in info.get("keywords_zh", []):
                if keyword in text:
                    score += 2
            
            for keyword in info.get("keywords_en", []):
                if keyword.lower() in text:
                    score += 2
            
            scores[category] = score
        
        # 选择分数最高的类别
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        # 默认返回"news"
        return "news"

    def extract_keywords(self, item: AINewsItem, max_keywords: int = 5) -> List[str]:
        """
        提取关键词
        
        Args:
            item: 新闻条目
            max_keywords: 最大关键词数
            
        Returns:
            关键词列表
        """
        # 合并文本
        text = f"{item.title} {item.summary}"
        
        # 简单关键词提取（基于词频）
        words = re.findall(r'[\w\u4e00-\u9fff]+', text.lower())
        
        # 过滤停用词
        stopwords = set([
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', 
            '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', 
            '没有', '看', '好', '自己', '这', 'the', 'a', 'an', 'is', 'are', 'was',
            'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can',
            'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from', 'as',
            'and', 'or', 'but', 'if', 'then', 'this', 'that', 'these', 'those',
            'ai', 'artificial', 'intelligence', 'new', 'latest', 'news'
        ])
        
        # 统计词频
        word_counts = Counter()
        for word in words:
            if len(word) >= 2 and word not in stopwords:
                word_counts[word] += 1
        
        # 返回高频词
        keywords = [word for word, count in word_counts.most_common(max_keywords)]
        
        return keywords

    def calculate_importance(self, item: AINewsItem) -> int:
        """
        计算重要性评分 (1-10)
        
        Args:
            item: 新闻条目
            
        Returns:
            重要性评分
        """
        score = 5  # 基础分数
        
        # 公司权重
        for company in item.companies:
            if company in COMPANIES:
                score += 1
        
        # 类别权重
        category_priority = CATEGORIES.get(item.category, {}).get("priority", 3)
        score += (7 - category_priority) * 0.5
        
        # 来源权重
        important_sources = ["OpenAI Blog", "Google Blog", "Meta AI", "Microsoft Blog"]
        if item.source in important_sources:
            score += 2
        
        # 内容长度权重
        if len(item.summary) > 100:
            score += 1
        
        # 限制分数范围
        return min(10, max(1, int(score)))

    def process_items(self, items: List[AINewsItem]) -> List[AINewsItem]:
        """
        处理新闻列表
        
        Args:
            items: 新闻列表
            
        Returns:
            处理后的新闻列表
        """
        processed_items = []
        
        for item in items:
            try:
                # 清洗文本
                item.title = self.clean_text(item.title)
                item.summary = self.clean_text(item.summary)
                
                # 重新分类
                item.category = self.categorize_item(item)
                
                # 提取关键词
                item.keywords = self.extract_keywords(item)
                
                # 计算重要性
                item.importance = self.calculate_importance(item)
                
                processed_items.append(item)
                
            except Exception as e:
                print(f"   ⚠ 处理失败: {e}")
                processed_items.append(item)
        
        print(f"   ✓ 处理完成 {len(processed_items)} 条新闻")
        
        return processed_items

    def filter_by_date(self, items: List[AINewsItem], days: int = 7) -> List[AINewsItem]:
        """
        按日期过滤
        
        Args:
            items: 新闻列表
            days: 天数
            
        Returns:
            过滤后的新闻列表
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        filtered_items = []
        for item in items:
            try:
                pub_date = datetime.strptime(item.publish_time, "%Y-%m-%d %H:%M:%S")
                if pub_date >= cutoff_date:
                    filtered_items.append(item)
            except:
                # 如果无法解析日期，保留该项目
                filtered_items.append(item)
        
        return filtered_items

    def filter_by_category(self, items: List[AINewsItem], 
                          categories: List[str]) -> List[AINewsItem]:
        """
        按类别过滤
        
        Args:
            items: 新闻列表
            categories: 类别列表
            
        Returns:
            过滤后的新闻列表
        """
        return [item for item in items if item.category in categories]

    def filter_by_source_type(self, items: List[AINewsItem], 
                             source_type: str) -> List[AINewsItem]:
        """
        按来源类型过滤
        
        Args:
            items: 新闻列表
            source_type: 来源类型 (international/domestic)
            
        Returns:
            过滤后的新闻列表
        """
        return [item for item in items if item.source_type == source_type]

    def sort_by_importance(self, items: List[AINewsItem], 
                          ascending: bool = False) -> List[AINewsItem]:
        """
        按重要性排序
        
        Args:
            items: 新闻列表
            ascending: 升序
            
        Returns:
            排序后的新闻列表
        """
        return sorted(items, key=lambda x: x.importance, reverse=not ascending)

    def sort_by_date(self, items: List[AINewsItem], 
                    ascending: bool = False) -> List[AINewsItem]:
        """
        按日期排序
        
        Args:
            items: 新闻列表
            ascending: 升序
            
        Returns:
            排序后的新闻列表
        """
        return sorted(
            items, 
            key=lambda x: datetime.strptime(x.publish_time, "%Y-%m-%d %H:%M:%S"),
            reverse=not ascending
        )

    def deduplicate(self, items: List[AINewsItem]) -> List[AINewsItem]:
        """
        去重（基于URL）
        
        Args:
            items: 新闻列表
            
        Returns:
            去重后的新闻列表
        """
        seen_urls = set()
        unique_items = []
        
        for item in items:
            if item.url not in seen_urls:
                seen_urls.add(item.url)
                unique_items.append(item)
        
        return unique_items

    def group_by_category(self, items: List[AINewsItem]) -> Dict[str, List[AINewsItem]]:
        """
        按类别分组
        
        Args:
            items: 新闻列表
            
        Returns:
            分组后的字典
        """
        groups = {}
        for item in items:
            if item.category not in groups:
                groups[item.category] = []
            groups[item.category].append(item)
        
        return groups

    def group_by_company(self, items: List[AINewsItem]) -> Dict[str, List[AINewsItem]]:
        """
        按公司分组
        
        Args:
            items: 新闻列表
            
        Returns:
            分组后的字典
        """
        groups = {}
        for item in items:
            for company in item.companies:
                if company not in groups:
                    groups[company] = []
                groups[company].append(item)
        
        return groups

    def generate_report(self, items: List[AINewsItem], 
                       days: int = 7) -> ReportData:
        """
        生成统计报告
        
        Args:
            items: 新闻列表
            days: 时间范围
            
        Returns:
            报告数据
        """
        # 按日期过滤
        filtered_items = self.filter_by_date(items, days)
        
        # 类别统计
        category_counts = Counter(item.category for item in filtered_items)
        categories = []
        for cat, count in category_counts.most_common():
            latest_time = None
            for item in filtered_items:
                if item.category == cat:
                    latest_time = item.publish_time
                    break
            categories.append(CategoryStats(
                category=cat,
                count=count,
                latest_time=latest_time
            ))
        
        # 公司统计
        company_counts = Counter()
        for item in filtered_items:
            company_counts.update(item.companies)
        
        companies = []
        for company, count in company_counts.most_common(10):
            source_type = COMPANIES.get(company, {}).get("type", "unknown")
            latest_time = None
            for item in filtered_items:
                if company in item.companies:
                    latest_time = item.publish_time
                    break
            companies.append(CompanyStats(
                company=company,
                count=count,
                source_type=source_type,
                latest_time=latest_time
            ))
        
        # 来源统计
        international_count = len(self.filter_by_source_type(filtered_items, "international"))
        domestic_count = len(self.filter_by_source_type(filtered_items, "domestic"))
        
        # 最新和最重要新闻
        latest_news = self.sort_by_date(filtered_items)[:10]
        top_news = self.sort_by_importance(filtered_items)[:10]
        
        # 日期范围
        date_range = f"最近{days}天"
        
        return ReportData(
            total_news=len(filtered_items),
            date_range=date_range,
            categories=categories,
            companies=companies,
            international_count=international_count,
            domestic_count=domestic_count,
            latest_news=latest_news,
            top_news=top_news
        )

    def save_processed_data(self, items: List[AINewsItem], 
                           prefix: str = "processed") -> Dict[str, str]:
        """
        保存处理后的数据
        
        Args:
            items: 新闻列表
            prefix: 文件前缀
            
        Returns:
            保存的文件路径字典
        """
        saved_files = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 按类别保存
        by_category = self.group_by_category(items)
        for category, cat_items in by_category.items():
            filename = f"{prefix}_category_{category}_{timestamp}.json"
            filepath = os.path.join(self.data_dir, "by_category", filename)
            self.store.save_items(cat_items, os.path.join("by_category", filename))
            saved_files[f"category_{category}"] = filepath
        
        # 按公司保存
        by_company = self.group_by_company(items)
        for company, comp_items in by_company.items():
            filename = f"{prefix}_company_{company}_{timestamp}.json"
            filepath = os.path.join(self.data_dir, "by_company", filename)
            self.store.save_items(comp_items, os.path.join("by_company", filename))
            saved_files[f"company_{company}"] = filepath
        
        # 保存完整列表
        filename = f"{prefix}_all_{timestamp}.json"
        filepath = os.path.join(self.data_dir, filename)
        self.store.save_items(items, filename)
        saved_files["all"] = filepath
        
        # 保存最新列表
        latest_filename = "latest.json"
        self.store.save_items(items[:OUTPUT_CONFIG["max_items_per_category"]], latest_filename)
        saved_files["latest"] = os.path.join(self.data_dir, latest_filename)
        
        print(f"\n💾 数据保存完成")
        for key, path in saved_files.items():
            print(f"   {key}: {path}")
        
        return saved_files


class DataSearcher:
    """数据搜索器"""

    def __init__(self, data_dir: str = None):
        """
        初始化搜索器
        
        Args:
            data_dir: 数据目录
        """
        self.data_dir = data_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data"
        )
        self.store = DataStore(self.data_dir)

    def search_items(self, items: List[AINewsItem], 
                    query: str = None,
                    categories: List[str] = None,
                    companies: List[str] = None,
                    source_type: str = None,
                    days: int = None) -> List[AINewsItem]:
        """
        搜索新闻
        
        Args:
            items: 新闻列表
            query: 搜索关键词
            categories: 类别过滤
            companies: 公司过滤
            source_type: 来源类型过滤
            days: 日期过滤
            
        Returns:
            过滤后的新闻列表
        """
        result = items
        
        # 按关键词搜索
        if query:
            query_lower = query.lower()
            result = [
                item for item in result 
                if query_lower in item.title.lower() 
                or query_lower in item.summary.lower()
            ]
        
        # 按类别过滤
        if categories:
            result = [item for item in result if item.category in categories]
        
        # 按公司过滤
        if companies:
            result = [
                item for item in result 
                if any(c in item.companies for c in companies)
            ]
        
        # 按来源类型过滤
        if source_type:
            result = [item for item in result if item.source_type == source_type]
        
        # 按日期过滤
        if days:
            processor = NewsProcessor()
            result = processor.filter_by_date(result, days)
        
        return result

    def load_latest(self) -> List[AINewsItem]:
        """加载最新数据"""
        return self.store.load_items("latest.json")

    def load_by_category(self, category: str) -> List[AINewsItem]:
        """按类别加载数据"""
        # 获取最新的类别文件
        category_dir = os.path.join(self.data_dir, "by_category")
        if not os.path.exists(category_dir):
            return []
        
        files = [f for f in os.listdir(category_dir) 
                if f.startswith("processed") and f"category_{category}" in f]
        
        if not files:
            return []
        
        # 加载最新文件
        files.sort(reverse=True)
        return self.store.load_items(os.path.join("by_category", files[0]))


def processing_demo():
    """处理演示"""
    from searcher import NewsSearcher
    import asyncio
    
    async def demo():
        print("🧪 数据处理测试")
        
        # 搜索新闻
        searcher = NewsSearcher()
        result = await searcher.search_latest_news(days=7, limit=10)
        
        # 处理新闻
        processor = NewsProcessor()
        processed_items = processor.process_items(result.items)
        
        # 生成报告
        report = processor.generate_report(processed_items)
        print(f"\n📊 统计报告")
        print(f"   总新闻数: {report.total_news}")
        print(f"   国际新闻: {report.international_count}")
        print(f"   国内新闻: {report.domestic_count}")
        print(f"\n   类别分布:")
        for cat in report.categories:
            cat_name = CATEGORIES.get(cat.category, {}).get("name", cat.category)
            print(f"     - {cat_name}: {cat.count}")
        
        print(f"\n   热门公司:")
        for comp in report.companies[:5]:
            print(f"     - {comp.company}: {comp.count}")
        
        return processed_items
    
    return asyncio.run(demo())


if __name__ == "__main__":
    processing_demo()
