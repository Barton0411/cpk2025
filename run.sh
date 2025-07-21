#!/bin/bash

# 检查是否已安装依赖
if ! pip3 show streamlit &> /dev/null; then
    echo "正在安装依赖..."
    pip3 install -r requirements.txt
fi

# 启动Streamlit应用
echo "正在启动牧场数据CPK分析系统..."
python3 -m streamlit run app.py --server.port 8501 --server.headless true