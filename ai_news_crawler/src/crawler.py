"""
内容爬虫核心模块
负责从各个数据源抓取AI资讯
"""

import feedparser
import requests
from datetime import datetime, timedelta
import hashlib
import logging
from typing import List, Dict, Optional
import time

logger = logging.getLogger(__name__)


class AINewsCrawler:
    """AI资讯爬虫"""
    
    def __init__(self, config: dict):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
    def fetch_rss(self, source_id: str, source_info: dict) -> List[Dict]:
        """
        抓取RSS源
        
        Args:
            source_id: 源ID
            source_info: 源信息（包含url, name等）
            
        Returns:
            文章列表
        """
        articles = []
        
        try:
            logger.info(f"开始抓取: {source_info['name']} ({source_info['url']})")
            
            # 解析RSS
            feed = feedparser.parse(source_info['url'])
            
            if feed.bozo:
                logger.warning(f"RSS解析警告: {source_info['name']} - {feed.bozo_exception}")
            
            # 获取配置的时间范围
            time_range_hours = self.config.get('filter', {}).get('time_range_hours', 0)
            cutoff_time = None
            if time_range_hours > 0:
                cutoff_time = datetime.now() - timedelta(hours=time_range_hours)
            
            # 获取最大文章数
            max_articles = self.config.get('sources', {}).get('max_articles_per_source', 20)
            
            # 处理每篇文章
            for entry in feed.entries[:max_articles]:
                try:
                    article = self._parse_entry(entry, source_id, source_info)
                    
                    # 时间过滤
                    if cutoff_time and article.get('publish_time'):
                        if article['publish_time'] < cutoff_time:
                            continue
                    
                    articles.append(article)
                    
                except Exception as e:
                    logger.error(f"解析文章失败: {e}")
                    continue
            
            logger.info(f"成功抓取 {len(articles)} 篇文章: {source_info['name']}")
            
        except Exception as e:
            logger.error(f"抓取RSS失败: {source_info['name']} - {e}")
        
        return articles
    
    def _parse_entry(self, entry, source_id: str, source_info: dict) -> Dict:
        """
        解析RSS条目
        
        Args:
            entry: RSS条目
            source_id: 源ID
            source_info: 源信息
            
        Returns:
            文章字典
        """
        # 提取标题
        title = entry.get('title', '').strip()
        
        # 提取链接
        url = entry.get('link', '')
        
        # 提取摘要
        summary = ''
        if 'summary' in entry:
            summary = entry.summary
        elif 'description' in entry:
            summary = entry.description
        
        # 清理HTML标签
        if summary:
            from bs4 import BeautifulSoup
            summary = BeautifulSoup(summary, 'html.parser').get_text()
            summary = summary.strip()[:500]  # 限制长度
        
        # 提取发布时间
        publish_time = None
        if 'published_parsed' in entry and entry.published_parsed:
            publish_time = datetime(*entry.published_parsed[:6])
        elif 'updated_parsed' in entry and entry.updated_parsed:
            publish_time = datetime(*entry.updated_parsed[:6])
        
        # 生成唯一ID
        article_id = self._generate_id(url, title)
        
        # 提取标签
        tags = []
        if 'tags' in entry:
            tags = [tag.term for tag in entry.tags if hasattr(tag, 'term')]
        
        article = {
            'id': article_id,
            'title': title,
            'url': url,
            'source_id': source_id,
            'source_name': source_info['name'],
            'language': source_info['language'],
            'category': source_info['category'],
            'summary': summary,
            'tags': tags,
            'publish_time': publish_time,
            'fetch_time': datetime.now()
        }
        
        return article
    
    def _generate_id(self, url: str, title: str) -> str:
        """生成文章唯一ID"""
        content = f"{url}_{title}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def fetch_all_sources(self, sources: dict) -> List[Dict]:
        """
        抓取所有数据源
        
        Args:
            sources: 数据源字典
            
        Returns:
            所有文章列表
        """
        all_articles = []
        
        for source_id, source_info in sources.items():
            try:
                articles = self.fetch_rss(source_id, source_info)
                all_articles.extend(articles)
                
                # 避免请求过快
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"抓取源失败: {source_id} - {e}")
                continue
        
        logger.info(f"总共抓取 {len(all_articles)} 篇文章")
        return all_articles
    
    def deduplicate(self, articles: List[Dict]) -> List[Dict]:
        """
        去重
        
        Args:
            articles: 文章列表
            
        Returns:
            去重后的文章列表
        """
        seen_ids = set()
        unique_articles = []
        
        for article in articles:
            if article['id'] not in seen_ids:
                seen_ids.add(article['id'])
                unique_articles.append(article)
        
        removed = len(articles) - len(unique_articles)
        if removed > 0:
            logger.info(f"去重: 移除 {removed} 篇重复文章")
        
        return unique_articles
    
    def filter_by_keywords(self, articles: List[Dict], keywords: List[str]) -> List[Dict]:
        """
        根据关键词过滤
        
        Args:
            articles: 文章列表
            keywords: 关键词列表
            
        Returns:
            过滤后的文章列表
        """
        if not keywords:
            return articles
        
        filtered = []
        keywords_lower = [k.lower() for k in keywords]
        
        for article in articles:
            text = f"{article['title']} {article['summary']}".lower()
            
            # 检查是否包含任一关键词
            if any(keyword in text for keyword in keywords_lower):
                filtered.append(article)
        
        logger.info(f"关键词过滤: 保留 {len(filtered)}/{len(articles)} 篇文章")
        return filtered
