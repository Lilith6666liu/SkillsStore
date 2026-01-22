"""
简单的Web查看器
用Flask提供一个简单的Web界面查看抓取的资讯
"""

from flask import Flask, render_template, jsonify, request
import json
import os
from datetime import datetime
import yaml

app = Flask(__name__)

# 加载配置
def load_config():
    with open('config.yaml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

# 加载数据
def load_articles():
    config = load_config()
    storage_type = config.get('storage', {}).get('type', 'json')
    
    if storage_type == 'json':
        path = config.get('storage', {}).get('path', './data/ai_news.json')
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
    
    return []


@app.route('/')
def index():
    """首页"""
    articles = load_articles()
    
    # 统计信息
    stats = {
        'total': len(articles),
        'sources': len(set(a['source_name'] for a in articles)),
        'categories': {}
    }
    
    for article in articles:
        category = article.get('category', 'unknown')
        stats['categories'][category] = stats['categories'].get(category, 0) + 1
    
    return render_template('index.html', stats=stats)


@app.route('/api/articles')
def api_articles():
    """获取文章列表API"""
    articles = load_articles()
    
    # 分页
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    
    # 过滤
    category = request.args.get('category')
    source = request.args.get('source')
    language = request.args.get('language')
    
    filtered = articles
    
    if category:
        filtered = [a for a in filtered if a.get('category') == category]
    
    if source:
        filtered = [a for a in filtered if a.get('source_id') == source]
    
    if language:
        filtered = [a for a in filtered if a.get('language') == language]
    
    # 分页
    start = (page - 1) * per_page
    end = start + per_page
    
    return jsonify({
        'total': len(filtered),
        'page': page,
        'per_page': per_page,
        'articles': filtered[start:end]
    })


@app.route('/api/stats')
def api_stats():
    """获取统计信息API"""
    articles = load_articles()
    
    # 按源统计
    sources = {}
    for article in articles:
        source = article['source_name']
        sources[source] = sources.get(source, 0) + 1
    
    # 按分类统计
    categories = {}
    for article in articles:
        category = article.get('category', 'unknown')
        categories[category] = categories.get(category, 0) + 1
    
    # 按语言统计
    languages = {}
    for article in articles:
        lang = article.get('language', 'unknown')
        languages[lang] = languages.get(lang, 0) + 1
    
    return jsonify({
        'total': len(articles),
        'sources': sources,
        'categories': categories,
        'languages': languages
    })


if __name__ == '__main__':
    # 创建模板目录
    os.makedirs('templates', exist_ok=True)
    
    # 创建简单的HTML模板
    html_template = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>AI资讯聚合</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header {
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 { color: #333; margin-bottom: 10px; }
        .stats {
            display: flex;
            gap: 20px;
            margin-top: 20px;
        }
        .stat-card {
            flex: 1;
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
        }
        .stat-card h3 { color: #666; font-size: 14px; margin-bottom: 5px; }
        .stat-card .number { font-size: 32px; color: #007bff; font-weight: bold; }
        .filters {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .articles {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .article {
            padding: 20px;
            border-bottom: 1px solid #eee;
        }
        .article:last-child { border-bottom: none; }
        .article h3 { 
            color: #333;
            margin-bottom: 10px;
            font-size: 18px;
        }
        .article a {
            color: #007bff;
            text-decoration: none;
        }
        .article a:hover { text-decoration: underline; }
        .meta {
            color: #666;
            font-size: 14px;
            margin-bottom: 10px;
        }
        .tag {
            display: inline-block;
            background: #e9ecef;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            margin-right: 5px;
            margin-top: 5px;
        }
        .loading { text-align: center; padding: 40px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI资讯聚合</h1>
            <p>实时抓取国内外AI动态、新闻、研究、访谈</p>
            <div class="stats">
                <div class="stat-card">
                    <h3>总文章数</h3>
                    <div class="number" id="total">{{ stats.total }}</div>
                </div>
                <div class="stat-card">
                    <h3>数据源</h3>
                    <div class="number" id="sources">{{ stats.sources }}</div>
                </div>
                <div class="stat-card">
                    <h3>分类</h3>
                    <div class="number" id="categories">{{ stats.categories|length }}</div>
                </div>
            </div>
        </div>
        
        <div class="articles" id="articles">
            <div class="loading">加载中...</div>
        </div>
    </div>
    
    <script>
        async function loadArticles() {
            const response = await fetch('/api/articles?per_page=50');
            const data = await response.json();
            
            const container = document.getElementById('articles');
            container.innerHTML = '';
            
            data.articles.forEach(article => {
                const div = document.createElement('div');
                div.className = 'article';
                
                const tags = article.tags ? article.tags.map(t => 
                    `<span class="tag">${t}</span>`
                ).join('') : '';
                
                div.innerHTML = `
                    <h3><a href="${article.url}" target="_blank">${article.title}</a></h3>
                    <div class="meta">
                        ${article.source_name} · ${article.category} · ${article.language}
                        ${article.publish_time ? '· ' + new Date(article.publish_time).toLocaleDateString() : ''}
                    </div>
                    ${article.summary ? `<p style="color: #666; margin: 10px 0;">${article.summary.substring(0, 200)}...</p>` : ''}
                    <div>${tags}</div>
                `;
                
                container.appendChild(div);
            });
        }
        
        loadArticles();
    </script>
</body>
</html>
    '''
    
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print("Web服务器启动: http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
