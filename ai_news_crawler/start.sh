#!/bin/bash

# AI资讯抓取系统 - 快速启动脚本

echo "🤖 AI资讯抓取系统"
echo "================================"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3"
    exit 1
fi

# 检查依赖
if [ ! -d "data" ]; then
    mkdir -p data logs
    echo "✅ 创建数据目录"
fi

# 安装依赖
echo "📦 检查依赖..."
python3 -m pip install -r requirements.txt --quiet --user

echo ""
echo "请选择操作:"
echo "1) 立即抓取一次"
echo "2) 启动定时抓取 (每小时)"
echo "3) 启动Web查看器"
echo "4) 查看帮助"
echo ""
read -p "请输入选项 (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🚀 开始抓取..."
        python3 main.py --hours 168
        echo ""
        echo "✅ 抓取完成！数据已保存到 data/ai_news.json"
        ;;
    2)
        echo ""
        echo "⏰ 启动定时抓取 (每小时执行一次)"
        echo "按 Ctrl+C 停止"
        python3 scheduler.py --interval 1h
        ;;
    3)
        echo ""
        echo "🌐 启动Web查看器..."
        echo "浏览器访问: http://127.0.0.1:5000"
        python3 web_viewer.py
        ;;
    4)
        echo ""
        echo "📖 使用帮助"
        echo ""
        echo "基础命令:"
        echo "  python3 main.py                    # 抓取所有源"
        echo "  python3 main.py --hours 24         # 只抓取最近24小时"
        echo "  python3 main.py --sources openai   # 只抓取指定源"
        echo ""
        echo "定时任务:"
        echo "  python3 scheduler.py --interval 1h # 每小时执行"
        echo "  python3 scheduler.py --interval 30m # 每30分钟执行"
        echo ""
        echo "Web查看:"
        echo "  python3 web_viewer.py              # 启动Web界面"
        echo ""
        ;;
    *)
        echo "❌ 无效选项"
        exit 1
        ;;
esac
