"""
AI资讯抓取系统 - 数据模型
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum


class Category(str, Enum):
    """新闻类别枚举"""
    NEWS = "news"
    PRODUCT = "product"
    TECHNICAL = "technical"
    RESEARCH = "research"
    INTERVIEW = "interview"
    OPINION = "opinion"


class SourceType(str, Enum):
    """来源类型枚举"""
    INTERNATIONAL = "international"
    DOMESTIC = "domestic"


@dataclass
class AINewsItem:
    """
    AI新闻数据模型
    
    Attributes:
        id: 唯一标识符
        title: 标题
        source: 来源名称
        source_type: 来源类型（国际/国内）
        category: 新闻类别
        publish_time: 发布时间
        url: 原文链接
        summary: 摘要
        content: 详细内容（可选）
        keywords: 关键词列表
        fetch_time: 抓取时间
        companies: 提到的公司列表
        language: 语言
        importance: 重要性评分 (1-10)
    """
    title: str
    source: str
    source_type: str
    category: str
    publish_time: str
    url: str
    summary: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    fetch_time: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    companies: List[str] = field(default_factory=list)
    language: str = "unknown"
    importance: int = 5

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AINewsItem':
        """从字典创建实例"""
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> 'AINewsItem':
        """从JSON字符串创建实例"""
        return cls.from_dict(json.loads(json_str))

    def is_recent(self, days: int = 7) -> bool:
        """检查是否在指定天数内"""
        try:
            pub_date = datetime.strptime(self.publish_time, "%Y-%m-%d %H:%M:%S")
            now = datetime.now()
            return (now - pub_date).days <= days
        except:
            return True


@dataclass
class SearchResult:
    """
    搜索结果模型
    
    Attributes:
        query: 搜索关键词
        total_results: 总结果数
        items: 新闻列表
        search_time: 搜索时间
    """
    query: str
    total_results: int
    items: List[AINewsItem]
    search_time: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "total_results": self.total_results,
            "items": [item.to_dict() for item in self.items],
            "search_time": self.search_time,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)


@dataclass
class CategoryStats:
    """类别统计模型"""
    category: str
    count: int
    latest_time: Optional[str] = None
    sources: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CompanyStats:
    """公司统计模型"""
    company: str
    count: int
    source_type: str
    latest_time: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ReportData:
    """报告数据模型"""
    total_news: int
    date_range: str
    categories: List[CategoryStats]
    companies: List[CompanyStats]
    international_count: int
    domestic_count: int
    latest_news: List[AINewsItem]
    top_news: List[AINewsItem]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_news": self.total_news,
            "date_range": self.date_range,
            "categories": [c.to_dict() for c in self.categories],
            "companies": [c.to_dict() for c in self.companies],
            "international_count": self.international_count,
            "domestic_count": self.domestic_count,
            "latest_news": [n.to_dict() for n in self.latest_news[:10]],
            "top_news": [n.to_dict() for n in self.top_news[:10]],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)


class DataStore:
    """数据存储管理器"""

    def __init__(self, data_dir: str):
        self.data_dir = data_dir

    def save_items(self, items: List[AINewsItem], filename: str) -> bool:
        """保存新闻列表到文件"""
        filepath = os.path.join(self.data_dir, filename)
        try:
            data = [item.to_dict() for item in items]
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存数据失败: {e}")
            return False

    def load_items(self, filename: str) -> List[AINewsItem]:
        """从文件加载新闻列表"""
        filepath = os.path.join(self.data_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return [AINewsItem.from_dict(item) for item in data]
        except Exception as e:
            print(f"加载数据失败: {e}")
            return []

    def save_index(self, index: Dict[str, List[str]], filename: str = "search_index.json") -> bool:
        """保存搜索索引"""
        filepath = os.path.join(self.data_dir, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(index, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存索引失败: {e}")
            return False

    def load_index(self, filename: str = "search_index.json") -> Dict[str, List[str]]:
        """加载搜索索引"""
        filepath = os.path.join(self.data_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载索引失败: {e}")
            return {}

    def get_latest_file(self, prefix: str = "news_") -> Optional[str]:
        """获取最新的数据文件"""
        try:
            files = [f for f in os.listdir(self.data_dir) if f.startswith(prefix) and f.endswith('.json')]
            if not files:
                return None
            files.sort(reverse=True)
            return files[0]
        except Exception as e:
            print(f"获取最新文件失败: {e}")
            return None

    def cleanup_old_files(self, days: int = 30) -> int:
        """清理旧文件"""
        deleted_count = 0
        try:
            now = datetime.now()
            for filename in os.listdir(self.data_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.data_dir, filename)
                    file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                    if (now - file_time).days > days:
                        os.remove(filepath)
                        deleted_count += 1
        except Exception as e:
            print(f"清理旧文件失败: {e}")
        return deleted_count


# 导入需要的模块
import os
