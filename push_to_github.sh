#!/bin/bash

echo "准备推送到GitHub仓库..."

# 初始化Git仓库（如果还没有初始化）
if [ ! -d .git ]; then
    echo "初始化Git仓库..."
    git init
fi

# 添加远程仓库
echo "配置远程仓库..."
git remote remove origin 2>/dev/null || true
git remote add origin https://github.com/Barton0411/cpk2025.git

# 添加所有文件
echo "添加文件..."
git add .

# 创建提交
echo "创建提交..."
git commit -m "牧场数据CPK分析系统 - $(date +%Y%m%d_%H%M%S)" || echo "没有需要提交的更改"

# 设置主分支
git branch -M main

# 推送到GitHub
echo "推送到GitHub..."
echo "如果提示输入用户名和密码："
echo "用户名: Barton0411"
echo "密码: 使用GitHub Personal Access Token（不是账号密码）"
echo ""
git push -u origin main

echo "完成！"