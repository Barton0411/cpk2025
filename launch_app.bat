@echo off
chcp 65001 >nul
title 牧场数据CPK分析系统

:: 切换到批处理文件所在目录
cd /d "%~dp0"

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Python，请先安装Python3
    echo 按任意键退出...
    pause >nul
    exit /b 1
)

:: 检查并安装依赖
echo 检查依赖...
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo 正在安装必要的依赖包...
    python -m pip install -r requirements.txt
)

:: 启动应用
echo.
echo 正在启动牧场数据CPK分析系统...
echo 应用将在浏览器中打开...
echo.
echo 如果浏览器没有自动打开，请手动访问：
echo http://localhost:8501
echo.
echo 按 Ctrl+C 可以停止程序
echo.

:: 启动Streamlit
python -m streamlit run app.py --server.port 8501

:: 保持窗口打开
echo.
echo 程序已停止。按任意键关闭窗口...
pause >nul