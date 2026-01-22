"""
定时任务调度器
支持定时自动抓取AI资讯
"""

import schedule
import time
import argparse
import yaml
import logging
import sys
from datetime import datetime

from src.crawler import AINewsCrawler
from src.storage import StorageManager
from src.sources.rss_sources import get_all_sources


def setup_logging(config: dict):
    """配置日志"""
    log_config = config.get('logging', {})
    log_level = getattr(logging, log_config.get('level', 'INFO'))
    log_file = log_config.get('file', './logs/crawler.log')
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
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


def crawl_task(config: dict):
    """执行抓取任务"""
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 60)
    logger.info(f"定时任务执行: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    try:
        # 获取所有数据源
        sources = get_all_sources()
        
        # 初始化爬虫
        crawler = AINewsCrawler(config)
        
        # 抓取文章
        articles = crawler.fetch_all_sources(sources)
        
        if not articles:
            logger.warning("未抓取到任何文章")
            return
        
        # 去重
        if config.get('filter', {}).get('deduplication', True):
            articles = crawler.deduplicate(articles)
        
        # 关键词过滤
        keywords = config.get('filter', {}).get('keywords', [])
        if keywords:
            articles = crawler.filter_by_keywords(articles, keywords)
        
        # 保存数据
        storage = StorageManager(config)
        success = storage.save(articles)
        
        if success:
            logger.info(f"任务完成！共处理 {len(articles)} 篇文章")
        else:
            logger.error("保存数据失败")
            
    except Exception as e:
        logger.error(f"任务执行失败: {e}", exc_info=True)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='AI资讯定时抓取调度器')
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='配置文件路径'
    )
    parser.add_argument(
        '--interval',
        default='1h',
        help='抓取间隔 (例如: 30m, 1h, 2h)'
    )
    parser.add_argument(
        '--cron',
        help='Cron表达式 (例如: "0 9 * * *" 表示每天9点)'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='只执行一次，不循环'
    )
    
    args = parser.parse_args()
    
    # 加载配置
    config = load_config(args.config)
    
    # 配置日志
    setup_logging(config)
    logger = logging.getLogger(__name__)
    
    logger.info("AI资讯定时抓取调度器启动")
    
    # 如果只执行一次
    if args.once:
        crawl_task(config)
        return
    
    # 解析间隔时间
    if args.cron:
        # 简化的cron支持（仅支持每天固定时间）
        # 格式: "分 时 * * *"
        parts = args.cron.split()
        if len(parts) >= 2:
            minute = parts[0]
            hour = parts[1]
            time_str = f"{hour}:{minute}"
            schedule.every().day.at(time_str).do(crawl_task, config)
            logger.info(f"已设置定时任务: 每天 {time_str} 执行")
    else:
        # 解析间隔
        interval = args.interval.lower()
        if interval.endswith('m'):
            minutes = int(interval[:-1])
            schedule.every(minutes).minutes.do(crawl_task, config)
            logger.info(f"已设置定时任务: 每 {minutes} 分钟执行一次")
        elif interval.endswith('h'):
            hours = int(interval[:-1])
            schedule.every(hours).hours.do(crawl_task, config)
            logger.info(f"已设置定时任务: 每 {hours} 小时执行一次")
        else:
            logger.error(f"无效的间隔格式: {interval}")
            sys.exit(1)
    
    # 立即执行一次
    logger.info("立即执行首次抓取...")
    crawl_task(config)
    
    # 循环执行
    logger.info("进入调度循环...")
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    except KeyboardInterrupt:
        logger.info("调度器已停止")


if __name__ == '__main__':
    main()
