"""
AI资讯抓取系统 - 主程序入口
"""

import argparse
import yaml
import logging
import sys
from datetime import datetime

from src.crawler import AINewsCrawler
from src.storage import StorageManager
from src.classifier import ContentClassifier
from src.sources.rss_sources import get_all_sources, get_source


def setup_logging(config: dict):
    """配置日志"""
    log_config = config.get('logging', {})
    log_level = getattr(logging, log_config.get('level', 'INFO'))
    log_file = log_config.get('file', './logs/crawler.log')
    
    # 创建日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # 配置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


def load_config(config_path: str = 'config.yaml') -> dict:
    """加载配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"加载配置文件失败: {e}")
        sys.exit(1)


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='AI资讯实时抓取系统')
    parser.add_argument(
        '--config', 
        default='config.yaml',
        help='配置文件路径'
    )
    parser.add_argument(
        '--sources',
        nargs='+',
        help='指定要抓取的源（留空表示全部）'
    )
    parser.add_argument(
        '--hours',
        type=int,
        help='只抓取最近N小时的文章'
    )
    parser.add_argument(
        '--output',
        choices=['json', 'sqlite', 'csv'],
        help='输出格式（覆盖配置文件）'
    )
    parser.add_argument(
        '--file',
        help='输出文件路径（用于json和csv）'
    )
    
    args = parser.parse_args()
    
    # 加载配置
    config = load_config(args.config)
    
    # 命令行参数覆盖配置
    if args.hours:
        config.setdefault('filter', {})['time_range_hours'] = args.hours
    
    if args.output:
        config.setdefault('storage', {})['type'] = args.output
    
    if args.file:
        if args.output == 'json':
            config['storage']['path'] = args.file
        elif args.output == 'csv':
            config.setdefault('storage', {}).setdefault('csv', {})['file'] = args.file
    
    # 配置日志
    setup_logging(config)
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 60)
    logger.info("AI资讯抓取系统启动")
    logger.info(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    # 获取数据源
    if args.sources:
        sources = {sid: get_source(sid) for sid in args.sources if get_source(sid)}
        if not sources:
            logger.error("未找到指定的数据源")
            sys.exit(1)
        logger.info(f"指定数据源: {', '.join(sources.keys())}")
    else:
        sources = get_all_sources()
        logger.info(f"使用所有数据源: {len(sources)} 个")
    
    # 初始化爬虫
    crawler = AINewsCrawler(config)
    
    # 抓取文章
    logger.info("开始抓取文章...")
    articles = crawler.fetch_all_sources(sources)
    
    if not articles:
        logger.warning("未抓取到任何文章")
        return
    
    # 去重
    if config.get('filter', {}).get('deduplication', True):
        articles = crawler.deduplicate(articles)
    
    # 内容分类和标签提取
    if config.get('classification', {}).get('enabled', True):
        logger.info("开始内容分类和标签提取...")
        classifier = ContentClassifier()
        articles = classifier.enhance_articles(articles)
    
    # 关键词过滤
    keywords = config.get('filter', {}).get('keywords', [])
    if keywords:
        articles = crawler.filter_by_keywords(articles, keywords)
    
    # 保存数据
    logger.info("保存数据...")
    storage = StorageManager(config)
    success = storage.save(articles)
    
    if success:
        logger.info("=" * 60)
        logger.info(f"抓取完成！共处理 {len(articles)} 篇文章")
        logger.info(f"存储类型: {config['storage']['type']}")
        
        # 统计信息
        sources_count = {}
        categories_count = {}
        for article in articles:
            source = article['source_name']
            category = article['category']
            sources_count[source] = sources_count.get(source, 0) + 1
            categories_count[category] = categories_count.get(category, 0) + 1
        
        logger.info("\n数据源统计:")
        for source, count in sorted(sources_count.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"  {source}: {count} 篇")
        
        logger.info("\n分类统计:")
        for category, count in sorted(categories_count.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"  {category}: {count} 篇")
        
        logger.info("=" * 60)
    else:
        logger.error("保存数据失败")
        sys.exit(1)


if __name__ == '__main__':
    main()
