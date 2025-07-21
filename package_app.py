#!/usr/bin/env python3
"""
打包脚本 - 创建可分发的应用程序包
"""
import os
import shutil
import zipfile
import platform

def create_distribution():
    """创建可分发的应用程序包"""
    
    # 创建dist目录
    dist_dir = "dist"
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir)
    
    # 创建应用目录
    app_name = "牧场数据CPK分析系统"
    app_dir = os.path.join(dist_dir, app_name)
    os.makedirs(app_dir)
    
    # 复制必要文件
    files_to_copy = [
        "app.py",
        "requirements.txt",
        "README.md",
        "launch_app.command",  # Mac
        "launch_app.bat",      # Windows
    ]
    
    for file in files_to_copy:
        if os.path.exists(file):
            shutil.copy2(file, app_dir)
    
    # 复制utils目录
    shutil.copytree("utils", os.path.join(app_dir, "utils"))
    
    # 复制.streamlit配置
    if os.path.exists(".streamlit"):
        shutil.copytree(".streamlit", os.path.join(app_dir, ".streamlit"))
    
    # 创建data目录
    data_dir = os.path.join(app_dir, "data")
    os.makedirs(data_dir)
    
    # 如果有示例数据，复制它
    if os.path.exists("data/2024年全年数据.xlsx"):
        shutil.copy2("data/2024年全年数据.xlsx", data_dir)
    
    # 创建安装说明
    install_instructions = """# 安装使用说明

## Windows用户
1. 确保已安装Python 3.7或更高版本
   - 可从 https://www.python.org 下载安装
   - 安装时勾选"Add Python to PATH"
2. 双击 launch_app.bat 启动程序
3. 首次运行会自动安装依赖，请耐心等待

## Mac用户
1. 确保已安装Python 3.7或更高版本
   - Mac通常自带Python3
   - 可通过终端运行 python3 --version 检查
2. 双击 launch_app.command 启动程序
3. 首次运行会自动安装依赖，请耐心等待
4. 如果提示权限问题，在终端运行：chmod +x launch_app.command

## 使用说明
1. 程序启动后会自动在浏览器中打开
2. 如果没有自动打开，请手动访问 http://localhost:8501
3. 将Excel数据文件放入data文件夹或直接上传
4. 按照界面提示进行操作

## 常见问题
- 如果提示找不到Python，请确保已正确安装并添加到系统PATH
- 如果依赖安装失败，可能需要升级pip：python -m pip install --upgrade pip
- 如果端口8501被占用，可以编辑启动脚本修改端口号
"""
    
    with open(os.path.join(app_dir, "安装使用说明.txt"), "w", encoding="utf-8") as f:
        f.write(install_instructions)
    
    # 创建ZIP包
    zip_name = f"{app_name}_{platform.system()}.zip"
    zip_path = os.path.join(dist_dir, zip_name)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(app_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, dist_dir)
                zipf.write(file_path, arcname)
    
    print(f"✅ 打包完成！")
    print(f"📦 输出文件：{zip_path}")
    print(f"📁 解压后双击启动脚本即可运行")
    
    return zip_path

if __name__ == "__main__":
    create_distribution()