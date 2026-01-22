"""
数据存储模块
支持JSON、SQLite、CSV多种存储格式
"""

import json
import sqlite3
import csv
import os
from datetime import datetime
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class StorageManager:
    """存储管理器"""
    
    def __init__(self, config: dict):
        self.config = config
        self.storage_type = config.get('storage', {}).get('type', 'json')
        
        # 确保数据目录存在
        os.makedirs('./data', exist_ok=True)
        os.makedirs('./logs', exist_ok=True)
    
    def save(self, articles: List[Dict]) -> bool:
        """
        保存文章
        
        Args:
            articles: 文章列表
            
        Returns:
            是否成功
        """
        try:
            if self.storage_type == 'json':
                return self._save_json(articles)
            elif self.storage_type == 'sqlite':
                return self._save_sqlite(articles)
            elif self.storage_type == 'csv':
                return self._save_csv(articles)
            else:
                logger.error(f"不支持的存储类型: {self.storage_type}")
                return False
        except Exception as e:
            logger.error(f"保存数据失败: {e}")
            return False
    
    def _save_json(self, articles: List[Dict]) -> bool:
        """保存为JSON格式"""
        path = self.config.get('storage', {}).get('path', './data/ai_news.json')
        
        # 读取现有数据
        existing_articles = []
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    existing_articles = json.load(f)
            except:
                pass
        
        # 合并新旧数据（去重）
        existing_ids = {a['id'] for a in existing_articles}
        new_articles = [a for a in articles if a['id'] not in existing_ids]
        
        # 转换datetime为字符串
        for article in new_articles:
            if isinstance(article.get('publish_time'), datetime):
                article['publish_time'] = article['publish_time'].isoformat()
            if isinstance(article.get('fetch_time'), datetime):
                article['fetch_time'] = article['fetch_time'].isoformat()
        
        # 合并并保存
        all_articles = existing_articles + new_articles
        
        # 按时间排序（最新的在前）
        all_articles.sort(
            key=lambda x: x.get('fetch_time', ''), 
            reverse=True
        )
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(all_articles, f, ensure_ascii=False, indent=2)
        
        logger.info(f"保存 {len(new_articles)} 篇新文章到 {path}")
        return True
    
    def _save_sqlite(self, articles: List[Dict]) -> bool:
        """保存到SQLite数据库"""
        db_path = self.config.get('storage', {}).get('sqlite', {}).get(
            'database', './data/ai_news.db'
        )
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 创建表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id TEXT PRIMARY KEY,
                title TEXT,
                url TEXT,
                source_id TEXT,
                source_name TEXT,
                language TEXT,
                category TEXT,
                summary TEXT,
                tags TEXT,
                publish_time TEXT,
                fetch_time TEXT
            )
        ''')
        
        # 插入数据
        new_count = 0
        for article in articles:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO articles 
                    (id, title, url, source_id, source_name, language, category, 
                     summary, tags, publish_time, fetch_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    article['id'],
                    article['title'],
                    article['url'],
                    article['source_id'],
                    article['source_name'],
                    article['language'],
                    article['category'],
                    article['summary'],
                    ','.join(article.get('tags', [])),
                    article.get('publish_time', '').isoformat() if isinstance(
                        article.get('publish_time'), datetime
                    ) else article.get('publish_time', ''),
                    article.get('fetch_time', '').isoformat() if isinstance(
                        article.get('fetch_time'), datetime
                    ) else article.get('fetch_time', '')
                ))
                if cursor.rowcount > 0:
                    new_count += 1
            except Exception as e:
                logger.error(f"插入文章失败: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        logger.info(f"保存 {new_count} 篇新文章到 {db_path}")
        return True
    
    def _save_csv(self, articles: List[Dict]) -> bool:
        """保存为CSV格式"""
        csv_path = self.config.get('storage', {}).get('csv', {}).get(
            'file', './data/ai_news.csv'
        )
        
        # 检查文件是否存在
        file_exists = os.path.exists(csv_path)
        
        # 读取现有ID
        existing_ids = set()
        if file_exists:
            try:
                with open(csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    existing_ids = {row['id'] for row in reader}
            except:
                pass
        
        # 过滤新文章
        new_articles = [a for a in articles if a['id'] not in existing_ids]
        
        if not new_articles:
            logger.info("没有新文章需要保存")
            return True
        
        # 写入CSV
        fieldnames = ['id', 'title', 'url', 'source_name', 'language', 
                     'category', 'summary', 'tags', 'publish_time', 'fetch_time']
        
        mode = 'a' if file_exists else 'w'
        with open(csv_path, mode, encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            for article in new_articles:
                row = {
                    'id': article['id'],
                    'title': article['title'],
                    'url': article['url'],
                    'source_name': article['source_name'],
                    'language': article['language'],
                    'category': article['category'],
                    'summary': article['summary'],
                    'tags': ','.join(article.get('tags', [])),
                    'publish_time': article.get('publish_time', '').isoformat() if isinstance(
                        article.get('publish_time'), datetime
                    ) else article.get('publish_time', ''),
                    'fetch_time': article.get('fetch_time', '').isoformat() if isinstance(
                        article.get('fetch_time'), datetime
                    ) else article.get('fetch_time', '')
                }
                writer.writerow(row)
        
        logger.info(f"保存 {len(new_articles)} 篇新文章到 {csv_path}")
        return True
    
    def load(self) -> List[Dict]:
        """
        加载已保存的文章
        
        Returns:
            文章列表
        """
        try:
            if self.storage_type == 'json':
                return self._load_json()
            elif self.storage_type == 'sqlite':
                return self._load_sqlite()
            elif self.storage_type == 'csv':
                return self._load_csv()
        except Exception as e:
            logger.error(f"加载数据失败: {e}")
            return []
    
    def _load_json(self) -> List[Dict]:
        """从JSON加载"""
        path = self.config.get('storage', {}).get('path', './data/ai_news.json')
        
        if not os.path.exists(path):
            return []
        
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_sqlite(self) -> List[Dict]:
        """从SQLite加载"""
        db_path = self.config.get('storage', {}).get('sqlite', {}).get(
            'database', './data/ai_news.db'
        )
        
        if not os.path.exists(db_path):
            return []
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM articles ORDER BY fetch_time DESC')
        rows = cursor.fetchall()
        
        articles = [dict(row) for row in rows]
        conn.close()
        
        return articles
    
    def _load_csv(self) -> List[Dict]:
        """从CSV加载"""
        csv_path = self.config.get('storage', {}).get('csv', {}).get(
            'file', './data/ai_news.csv'
        )
        
        if not os.path.exists(csv_path):
            return []
        
        articles = []
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            articles = list(reader)
        
        return articles
