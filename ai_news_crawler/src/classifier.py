"""
内容分类器
基于关键词和规则自动分类文章
"""

import re
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class ContentClassifier:
    """内容分类器"""
    
    # 分类关键词映射
    CATEGORY_KEYWORDS = {
        'research': [
            'paper', 'research', 'study', 'arxiv', 'conference',
            '论文', '研究', '学术', '会议', 'CVPR', 'NeurIPS', 'ICLR',
            'transformer', 'neural network', '神经网络', '算法'
        ],
        'news': [
            'announce', 'release', 'launch', 'update', 'breaking',
            '发布', '推出', '更新', '新闻', '动态', '最新',
            'funding', '融资', 'acquisition', '收购'
        ],
        'interview': [
            'interview', 'talk', 'conversation', 'Q&A', 'AMA',
            '访谈', '对话', '专访', '采访', '问答'
        ],
        'tutorial': [
            'tutorial', 'guide', 'how to', 'introduction', 'getting started',
            '教程', '指南', '入门', '实战', '实践', '手把手',
            'example', 'demo', '示例', '演示'
        ],
        'product': [
            'product', 'feature', 'tool', 'platform', 'service',
            '产品', '功能', '工具', '平台', '服务',
            'API', 'SDK', 'app', '应用'
        ]
    }
    
    def __init__(self):
        pass
    
    def classify(self, article: Dict) -> str:
        """
        对文章进行分类
        
        Args:
            article: 文章字典
            
        Returns:
            分类标签
        """
        # 如果已有分类，优先使用
        if article.get('category'):
            return article['category']
        
        # 组合标题和摘要进行分析
        text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
        
        # 计算每个分类的得分
        scores = {}
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in text:
                    score += 1
            scores[category] = score
        
        # 返回得分最高的分类
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        # 默认分类为news
        return 'news'
    
    def classify_batch(self, articles: List[Dict]) -> List[Dict]:
        """
        批量分类
        
        Args:
            articles: 文章列表
            
        Returns:
            分类后的文章列表
        """
        for article in articles:
            if not article.get('category') or article['category'] == 'unknown':
                article['category'] = self.classify(article)
        
        return articles
    
    def extract_tags(self, article: Dict) -> List[str]:
        """
        提取文章标签
        
        Args:
            article: 文章字典
            
        Returns:
            标签列表
        """
        tags = set(article.get('tags', []))
        
        # 常见AI技术标签
        tech_keywords = {
            'GPT': ['gpt', 'gpt-4', 'gpt-3'],
            'LLM': ['llm', 'large language model', '大语言模型'],
            'Transformer': ['transformer'],
            'Diffusion': ['diffusion', 'stable diffusion', 'dall-e', 'midjourney'],
            'Computer Vision': ['computer vision', 'cv', '计算机视觉', 'image', 'video'],
            'NLP': ['nlp', 'natural language processing', '自然语言处理'],
            'Reinforcement Learning': ['reinforcement learning', 'rl', '强化学习'],
            'Deep Learning': ['deep learning', '深度学习'],
            'Machine Learning': ['machine learning', 'ml', '机器学习'],
            'AI Agent': ['agent', 'autonomous', '智能体'],
            'Robotics': ['robot', '机器人'],
            'AGI': ['agi', 'artificial general intelligence', '通用人工智能']
        }
        
        text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
        
        for tag, keywords in tech_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    tags.add(tag)
                    break
        
        return list(tags)
    
    def enhance_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        增强文章信息（分类+标签提取）
        
        Args:
            articles: 文章列表
            
        Returns:
            增强后的文章列表
        """
        for article in articles:
            # 分类
            if not article.get('category'):
                article['category'] = self.classify(article)
            
            # 提取标签
            article['tags'] = self.extract_tags(article)
        
        logger.info(f"完成 {len(articles)} 篇文章的分类和标签提取")
        return articles
