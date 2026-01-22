"""
AI资讯抓取系统 - 主程序

功能：
- 整合搜索、提取、处理功能
- 提供命令行接口
- 支持多种运行模式
"""

import asyncio
import argparse
import sys
import os
from datetime import datetime
from typing import List, Dict, Any

# 添加src目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import CATEGORIES, COMPANIES, DEFAULT_DAYS, OUTPUT_CONFIG
from models import AINewsItem, SearchResult, DataStore
from searcher import NewsSearcher
from extractor import ContentExtractor, IncrementalExtractor
from processor import NewsProcessor, DataSearcher


class AINewsScraper:
    """AI资讯抓取器主类"""

    def __init__(self, use_mcp: bool = True):
        """
        初始化抓取器
        
        Args:
            use_mcp: 是否使用MCP工具
        """
        self.use_mcp = use_mcp
        self.searcher = NewsSearcher(use_mcp=use_mcp)
        self.extractor = ContentExtractor(use_mcp=use_mcp)
        self.processor = NewsProcessor()
        self.searcher_incremental = IncrementalExtractor(self.extractor)
        self.data_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data"
        )
        self.store = DataStore(self.data_dir)
        
        # 加载已处理URL
        self.searcher_incremental.load_processed_urls(
            os.path.join(self.data_dir, "index", "processed_urls.json")
        )

    async def fetch_latest_news(self, days: int = DEFAULT_DAYS, 
                                limit: int = 50,
                                extract_content: bool = False,
                                save: bool = True) -> List[AINewsItem]:
        """
        获取最新AI新闻
        
        Args:
            days: 时间范围（天）
            limit: 限制数量
            extract_content: 是否提取详细内容
            save: 是否保存数据
            
        Returns:
            新闻列表
        """
        print("=" * 60)
        print("🤖 AI资讯实时抓取系统")
        print("=" * 60)
        print(f"\n📡 模式: 获取最新AI资讯")
        print(f"   时间范围: 最近{days}天")
        print(f"   限制数量: {limit}条")
        print(f"   提取详情: {'是' if extract_content else '否'}")
        print(f"   自动保存: {'是' if save else '否'}")
        
        # 1. 搜索新闻
        search_result = await self.searcher.search_latest_news(days=days, limit=limit)
        
        if not search_result.items:
            print("\n⚠ 未找到相关新闻")
            return []
        
        # 2. 提取详细内容（可选）
        if extract_content:
            items = await self.extractor.extract_batch(search_result.items)
        else:
            items = search_result.items
        
        # 3. 处理数据
        processed_items = self.processor.process_items(items)
        
        # 4. 保存数据
        if save:
            self.processor.save_processed_data(processed_items)
            # 保存已处理URL
            self.searcher_incremental.save_processed_urls(
                os.path.join(self.data_dir, "index", "processed_urls.json")
            )
        
        return processed_items

    async def fetch_by_company(self, companies: List[str],
                              days: int = DEFAULT_DAYS,
                              limit: int = 30) -> List[AINewsItem]:
        """
        按公司获取新闻
        
        Args:
            companies: 公司列表
            days: 时间范围
            limit: 限制数量
            
        Returns:
            新闻列表
        """
        print("\n" + "=" * 60)
        print(f"🏢 模式: 获取指定公司动态")
        print(f"   公司: {', '.join(companies)}")
        print(f"   时间范围: 最近{days}天")
        
        search_result = await self.searcher.search_by_companies(companies, days)
        items = self.processor.process_items(search_result.items)
        
        return items

    async def fetch_by_category(self, category: str,
                               days: int = DEFAULT_DAYS,
                               limit: int = 30) -> List[AINewsItem]:
        """
        按类别获取新闻
        
        Args:
            category: 类别
            days: 时间范围
            limit: 限制数量
            
        Returns:
            新闻列表
        """
        print("\n" + "=" * 60)
        print(f"📁 模式: 获取{category}类资讯")
        
        search_result = await self.searcher.search_by_category(category, days)
        items = self.processor.process_items(search_result.items)
        
        return items

    async def fetch_international_news(self, days: int = DEFAULT_DAYS,
                                       limit: int = 30) -> List[AINewsItem]:
        """获取国际AI新闻"""
        print("\n" + "=" * 60)
        print("🌍 模式: 获取国际AI资讯")
        
        search_result = await self.searcher.search_international_news(days, limit)
        items = self.processor.process_items(search_result.items)
        
        return items

    async def fetch_domestic_news(self, days: int = DEFAULT_DAYS,
                                  limit: int = 30) -> List[AINewsItem]:
        """获取国内AI新闻"""
        print("\n" + "=" * 60)
        print("🇨🇳 模式: 获取国内AI资讯")
        
        search_result = await self.searcher.search_domestic_news(days, limit)
        items = self.processor.process_items(search_result.items)
        
        return items

    async def custom_search(self, keywords: List[str],
                           days: int = DEFAULT_DAYS,
                           limit: int = 30) -> List[AINewsItem]:
        """
        自定义搜索
        
        Args:
            keywords: 关键词列表
            days: 时间范围
            limit: 限制数量
            
        Returns:
            新闻列表
        """
        print("\n" + "=" * 60)
        print("🔍 模式: 自定义搜索")
        print(f"   关键词: {', '.join(keywords)}")
        
        search_result = await self.searcher.search(keywords, days, language="all", max_results=limit)
        items = self.processor.process_items(search_result.items)
        
        return items

    def display_news(self, items: List[AINewsItem], 
                    max_items: int = 20,
                    show_content: bool = False):
        """
        显示新闻列表
        
        Args:
            items: 新闻列表
            max_items: 最大显示数量
            show_content: 显示详细内容
        """
        print(f"\n📰 共找到 {len(items)} 条资讯")
        print("-" * 60)
        
        display_items = items[:max_items]
        
        for i, item in enumerate(display_items, 1):
            # 类别名称
            cat_name = CATEGORIES.get(item.category, {}).get("name", item.category)
            
            # 来源类型图标
            type_icon = "🌍" if item.source_type == "international" else "🇨🇳"
            
            # 重要性星级
            stars = "★" * item.importance + "☆" * (10 - item.importance)
            
            print(f"\n{i}. {item.title}")
            print(f"   {type_icon} 来源: {item.source} | 类别: {cat_name}")
            print(f"   📅 时间: {item.publish_time}")
            print(f"   ⭐ 重要: {stars[:5]}")
            print(f"   🔗 链接: {item.url}")
            print(f"   📝 摘要: {item.summary[:200]}...")
            
            if show_content and item.content:
                print(f"\n   📄 内容:")
                for line in item.content[:500].split("\n"):
                    print(f"      {line}")
            
            # 提到的公司
            if item.companies:
                print(f"   🏢 公司: {', '.join(item.companies)}")
            
            print("-" * 60)

    def display_report(self, items: List[AINewsItem], days: int = DEFAULT_DAYS):
        """
        显示统计报告
        
        Args:
            items: 新闻列表
            days: 时间范围
        """
        report = self.processor.generate_report(items, days)
        
        print("\n" + "=" * 60)
        print("📊 AI资讯统计报告")
        print("=" * 60)
        
        print(f"\n📈 总体统计")
        print(f"   资讯总数: {report.total_news}")
        print(f"   时间范围: {report.date_range}")
        print(f"   国际动态: {report.international_count} 条")
        print(f"   国内动态: {report.domestic_count} 条")
        
        print(f"\n📂 类别分布")
        for cat in report.categories:
            cat_name = CATEGORIES.get(cat.category, {}).get("name", cat.category)
            bar = "█" * (cat.count * 50 // max(report.total_news, 1))
            print(f"   {cat_name:10s}: {cat.count:3d} {bar}")
        
        print(f"\n🏢 热门公司")
        for comp in report.companies[:10]:
            icon = "🌍" if comp.source_type == "international" else "🇨🇳"
            print(f"   {icon} {comp.company:10s}: {comp.count:3d} 条动态")
        
        print(f"\n🔥 重要动态 TOP 10")
        for i, item in enumerate(report.top_news[:10], 1):
            cat_name = CATEGORIES.get(item.category, {}).get("name", item.category)
            print(f"   {i:2d}. [{cat_name}] {item.title[:50]}")
            print(f"       来源: {item.source} | 重要度: {item.importance}/10")

    def export_data(self, items: List[AINewsItem], 
                   format: str = "json",
                   filename: str = None):
        """
        导出数据
        
        Args:
            items: 新闻列表
            format: 格式（json/csv）
            filename: 文件名
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ai_news_{timestamp}.{format}"
        
        filepath = os.path.join(self.data_dir, filename)
        
        if format == "json":
            data = [item.to_dict() for item in items]
            with open(filepath, 'w', encoding='utf-8') as f:
                import json
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"\n✅ 数据已导出: {filepath}")
        
        elif format == "csv":
            import csv
            with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
                if items:
                    writer = csv.DictWriter(f, fieldnames=items[0].to_dict().keys())
                    writer.writeheader()
                    for item in items:
                        writer.writerow(item.to_dict())
            print(f"\n✅ 数据已导出: {filepath}")
        
        else:
            print(f"\n⚠ 不支持的格式: {format}")


async def run_demo():
    """运行演示"""
    scraper = AINewsScraper()
    
    # 1. 获取最新资讯
    items = await scraper.fetch_latest_news(days=7, limit=15)
    
    if items:
        # 2. 显示统计报告
        scraper.display_report(items)
        
        # 3. 显示新闻列表
        scraper.display_news(items, max_items=10)
        
        # 4. 导出数据
        scraper.export_data(items, filename="ai_news_demo.json")
    
    return items


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="AI资讯实时抓取系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py --mode latest                    # 获取最新AI资讯
  python main.py --mode company --companies OpenAI Google  # 获取指定公司动态
  python main.py --mode category --category news  # 获取新闻类别
  python main.py --mode international             # 获取国际AI资讯
  python main.py --mode domestic                  # 获取国内AI资讯
  python main.py --mode search --keywords "GPT-5"  # 自定义搜索
        """
    )
    
    parser.add_argument(
        "--mode", 
        type=str, 
        default="latest",
        choices=["latest", "company", "category", "international", "domestic", "search", "demo", "report"],
        help="运行模式"
    )
    
    parser.add_argument(
        "--keywords", 
        type=str, 
        nargs="+",
        default=[],
        help="搜索关键词"
    )
    
    parser.add_argument(
        "--companies",
        type=str,
        nargs="+",
        default=[],
        help="指定公司"
    )
    
    parser.add_argument(
        "--category",
        type=str,
        default="news",
        help="新闻类别"
    )
    
    parser.add_argument(
        "--days",
        type=int,
        default=DEFAULT_DAYS,
        help=f"时间范围（天），默认{DEFAULT_DAYS}天"
    )
    
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="最大数量限制"
    )
    
    parser.add_argument(
        "--extract",
        action="store_true",
        help="是否提取详细内容"
    )
    
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="不保存数据"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default="json",
        choices=["json", "csv"],
        help="输出格式"
    )
    
    parser.add_argument(
        "--display",
        type=str,
        choices=["news", "report", "all"],
        default="all",
        help="显示内容"
    )
    
    args = parser.parse_args()
    
    # 创建抓取器
    scraper = AINewsScraper()
    
    # 运行
    async def run():
        items = []
        
        if args.mode == "latest":
            items = await scraper.fetch_latest_news(
                days=args.days, 
                limit=args.limit,
                extract_content=args.extract,
                save=not args.no_save
            )
        
        elif args.mode == "company":
            if not args.companies:
                print("⚠ 请指定公司名称")
                return
            items = await scraper.fetch_by_company(
                args.companies, 
                days=args.days, 
                limit=args.limit
            )
        
        elif args.mode == "category":
            items = await scraper.fetch_by_category(
                args.category,
                days=args.days,
                limit=args.limit
            )
        
        elif args.mode == "international":
            items = await scraper.fetch_international_news(
                days=args.days,
                limit=args.limit
            )
        
        elif args.mode == "domestic":
            items = await scraper.fetch_domestic_news(
                days=args.days,
                limit=args.limit
            )
        
        elif args.mode == "search":
            if not args.keywords:
                print("⚠ 请指定搜索关键词")
                return
            items = await scraper.custom_search(
                args.keywords,
                days=args.days,
                limit=args.limit
            )
        
        elif args.mode == "demo":
            items = await run_demo()
        
        elif args.mode == "report":
            items = await scraper.fetch_latest_news(
                days=args.days,
                limit=args.limit,
                extract_content=False,
                save=False
            )
        
        # 显示结果
        if items:
            if args.display in ["report", "all"]:
                scraper.display_report(items, days=args.days)
            
            if args.display in ["news", "all"]:
                scraper.display_news(items, max_items=args.limit)
            
            if not args.no_save:
                scraper.export_data(items, format=args.output)
        
        return items
    
    # 运行
    items = asyncio.run(run())
    
    print("\n" + "=" * 60)
    print("✅ 执行完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
