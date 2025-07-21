#!/bin/bash

# 切换到脚本所在目录
cd "$(dirname "$0")"

# 直接使用Python3启动，更简单
python3 -m streamlit run app.py