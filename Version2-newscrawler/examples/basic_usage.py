"""
AI资讯抓取系统 - 基础用法示例

这个示例展示了系统的基础功能
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import AINewsScraper


async def example_1_get_latest_news():
    """示例1: 获取最新AI资讯"""
    print("\n" + "="*60)
    print("示例1: 获取最新AI资讯")
    print("="*60)
    
    # 创建抓取器
    scraper = AINewsScraper()
    
    # 获取最新资讯
    items = await scraper.fetch_latest_news(
        days=7,      # 最近7天
        limit=20,    # 最多20条
        extract_content=False,  # 不提取详细内容（更快）
        save=True    # 保存数据
    )
    
    # 显示统计报告
    scraper.display_report(items)
    
    # 显示新闻列表（只显示前10条）
    scraper.display_news(items, max_items=10)
    
    return items


async def example_2_get_company_news():
    """示例2: 获取特定公司动态"""
    print("\n" + "="*60)
    print("示例2: 获取OpenAI和Google的最新动态")
    print("="*60)
    
    scraper = AINewsScraper()
    
    # 获取指定公司的动态
    items = await scraper.fetch_by_company(
        companies=["OpenAI", "Google", "Anthropic"],
        days=7,
        limit=20
    )
    
    scraper.display_news(items, max_items=15)
    
    return items


async def example_3_get_category_news():
    """示例3: 按类别获取资讯"""
    print("\n" + "="*60)
    print("示例3: 获取学术突破类资讯")
    print("="*60)
    
    scraper = AINewsScraper()
    
    # 获取特定类别
    items = await scraper.fetch_by_category(
        category="research",  # 学术突破
        days=30,              # 最近30天
        limit=20
    )
    
    scraper.display_report(items, days=30)
    scraper.display_news(items, max_items=10)
    
    return items


async def example_4_get_international_news():
    """示例4: 获取国际AI资讯"""
    print("\n" + "="*60)
    print("示例4: 获取国际AI资讯")
    print("="*60)
    
    scraper = AINewsScraper()
    
    items = await scraper.fetch_international_news(
        days=7,
        limit=20
    )
    
    scraper.display_report(items)
    
    return items


async def example_5_get_domestic_news():
    """示例5: 获取国内AI资讯"""
    print("\n" + "="*60)
    print("示例5: 获取国内AI资讯")
    print("="*60)
    
    scraper = AINewsScraper()
    
    items = await scraper.fetch_domestic_news(
        days=7,
        limit=20
    )
    
    scraper.display_report(items)
    
    return items


async def example_6_custom_search():
    """示例6: 自定义搜索"""
    print("\n" + "="*60)
    print("示例6: 自定义搜索GPT-5相关资讯")
    print("="*60)
    
    scraper = AINewsScraper()
    
    # 自定义搜索关键词
    items = await scraper.custom_search(
        keywords=["GPT-5", "大语言模型", "多模态AI"],
        days=14,
        limit=30
    )
    
    scraper.display_news(items, max_items=20)
    
    return items


async def example_7_export_data():
    """示例7: 导出数据"""
    print("\n" + "="*60)
    print("示例7: 导出数据到JSON和CSV")
    print("="*60)
    
    scraper = AINewsScraper()
    
    items = await scraper.fetch_latest_news(days=7, limit=20)
    
    # 导出为JSON
    scraper.export_data(items, format="json", filename="my_ai_news.json")
    
    # 导出为CSV
    scraper.export_data(items, format="csv", filename="my_ai_news.csv")
    
    return items


async def main():
    """主函数 - 运行所有示例"""
    print("AI资讯抓取系统 - 基础用法示例")
    print("="*60)
    
    # 运行各个示例
    await example_1_get_latest_news()
    
    input("\n按回车键继续下一个示例...")
    
    await example_2_get_company_news()
    
    input("\n按回车键继续下一个示例...")
    
    await example_3_get_category_news()
    
    input("\n按回车键继续下一个示例...")
    
    await example_4_get_international_news()
    
    input("\n按回车键继续下一个示例...")
    
    await example_5_get_domestic_news()
    
    input("\n按回车键继续下一个示例...")
    
    await example_6_custom_search()
    
    input("\n按回车键继续下一个示例...")
    
    await example_7_export_data()
    
    print("\n" + "="*60)
    print("所有示例运行完成！")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
