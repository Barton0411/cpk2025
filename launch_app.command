#!/bin/bash

# 切换到脚本所在目录
cd "$(dirname "$0")"

# 检查Python3是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误：未找到Python3，请先安装Python3"
    echo "按任意键退出..."
    read -n 1
    exit 1
fi

# 检查并安装依赖
echo "检查依赖..."
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "正在安装必要的依赖包..."
    python3 -m pip install -r requirements.txt
fi

# 启动应用
echo "正在启动牧场数据CPK分析系统..."
echo "应用将在浏览器中打开..."
echo ""
echo "如果浏览器没有自动打开，请手动访问："
echo "http://localhost:8501"
echo ""
echo "按 Ctrl+C 可以停止程序"
echo ""

# 启动Streamlit
python3 -m streamlit run app.py --server.port 8501

# 保持窗口打开
echo ""
echo "程序已停止。按任意键关闭窗口..."
read -n 1