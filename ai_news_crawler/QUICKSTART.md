# 🚀 AI资讯抓取Skill - 快速参考

## 📍 项目位置
```
/Users/liuliu.lilith/Documents/ai_news_crawler
```

## ⚡ 三步开始使用

### 1️⃣ 进入项目目录
```bash
cd /Users/liuliu.lilith/Documents/ai_news_crawler
```

### 2️⃣ 选择一个命令运行

**立即抓取一次:**
```bash
python3 main.py
```

**每小时自动抓取:**
```bash
python3 scheduler.py --interval 1h
```

**启动Web界面查看:**
```bash
python3 web_viewer.py
# 然后访问: http://127.0.0.1:5000
```

**使用交互式菜单:**
```bash
./start.sh
```

### 3️⃣ 查看结果
- **JSON文件**: `data/ai_news.json`
- **Web界面**: http://127.0.0.1:5000
- **日志文件**: `logs/crawler.log`

## 📊 当前数据

已成功抓取 **106篇** AI资讯，包括：
- 研究论文: 57篇
- 新闻动态: 35篇  
- 技术教程: 11篇

来自9个数据源：
- arXiv (AI/ML/CL)
- TechCrunch AI
- AWS ML Blog
- 机器之心
- 量子位
- MIT Tech Review
- Hugging Face

## 🎯 常用场景

| 场景 | 命令 |
|------|------|
| 快速查看最新资讯 | `python3 web_viewer.py` |
| 每天早上9点自动抓取 | `python3 scheduler.py --cron "0 9 * * *"` |
| 只看最近24小时的 | `python3 main.py --hours 24` |
| 导出为Excel可读的CSV | `python3 main.py --output csv --file ai_news.csv` |
| 只抓取特定源 | `python3 main.py --sources openai huggingface` |

## ⚙️ 配置文件

编辑 `config.yaml` 可以：
- 调整抓取频率
- 设置关键词过滤
- 修改存储格式
- 配置时间范围

## 📚 详细文档

- **README.md** - 项目介绍和功能特性
- **USAGE.md** - 完整使用指南和常见问题
- **PROJECT_SUMMARY.md** - 项目总结和技术细节

## 🔍 数据源列表

**国际源 (11个):**
OpenAI, Google AI, Hugging Face, TechCrunch, VentureBeat, MIT Tech Review, arXiv (×3), AWS ML, DeepMind

**国内源 (5个):**
机器之心, 量子位, 雷锋网, 36氪, AI科技评论

## 💡 小贴士

1. **首次使用**: 直接运行 `./start.sh` 最简单
2. **定时任务**: 推荐使用 `scheduler.py --interval 1h`
3. **查看数据**: Web界面比直接看JSON文件更友好
4. **自定义**: 修改 `config.yaml` 而不是代码

## 🐛 遇到问题？

1. 查看日志: `tail -f logs/crawler.log`
2. 检查配置: `cat config.yaml`
3. 重新安装依赖: `pip3 install -r requirements.txt`

## 📞 快速命令备忘

```bash
# 进入项目
cd /Users/liuliu.lilith/Documents/ai_news_crawler

# 立即抓取
python3 main.py

# 定时抓取（每小时）
python3 scheduler.py --interval 1h

# Web查看
python3 web_viewer.py

# 查看数据
cat data/ai_news.json | python3 -m json.tool | less

# 查看日志
tail -f logs/crawler.log
```

---

**项目状态**: ✅ 已完成并测试通过

**最后更新**: 2026-01-22

**已抓取文章**: 106篇

**数据文件**: `/Users/liuliu.lilith/Documents/ai_news_crawler/data/ai_news.json`
