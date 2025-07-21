# 部署到GitHub和Streamlit Cloud指南

## 步骤 1: 准备GitHub仓库

### 1.1 创建GitHub账号（如果还没有）
访问 https://github.com 注册账号

### 1.2 创建新仓库
1. 登录GitHub后，点击右上角的 "+" 按钮
2. 选择 "New repository"
3. 仓库名称建议：`dairy-cpk-analysis`
4. 描述：牧场数据CPK分析系统
5. 选择 "Private"（私有）或 "Public"（公开）
6. 不要勾选 "Initialize this repository with a README"
7. 点击 "Create repository"

## 步骤 2: 上传代码到GitHub

### 2.1 在终端中执行以下命令

```bash
# 1. 进入项目目录
cd "/Users/Shared/Files From d.localized/projects/cpk_data_analyze"

# 2. 初始化Git仓库
git init

# 3. 添加所有文件
git add .

# 4. 创建首次提交
git commit -m "初始提交：牧场数据CPK分析系统"

# 5. 添加远程仓库（替换YOUR_USERNAME为你的GitHub用户名）
git remote add origin https://github.com/YOUR_USERNAME/dairy-cpk-analysis.git

# 6. 推送到GitHub
git branch -M main
git push -u origin main
```

### 2.2 如果提示输入用户名和密码
- 用户名：你的GitHub用户名
- 密码：需要使用Personal Access Token（不是账号密码）
  
#### 创建Personal Access Token：
1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token" → "Generate new token (classic)"
3. Note填写：dairy-cpk-deploy
4. 勾选 "repo" 权限
5. 点击 "Generate token"
6. 复制生成的token（只显示一次！）

## 步骤 3: 部署到Streamlit Cloud

### 3.1 访问Streamlit Cloud
1. 访问 https://streamlit.io/cloud
2. 点击 "Sign up" 或 "Sign in"
3. 使用GitHub账号登录

### 3.2 部署应用
1. 点击 "New app"
2. 选择你刚创建的仓库：dairy-cpk-analysis
3. Branch选择：main
4. Main file path：app.py
5. 点击 "Deploy"

### 3.3 等待部署完成
- 部署通常需要几分钟
- 完成后会获得一个URL，如：https://dairy-cpk-analysis.streamlit.app

## 步骤 4: 配置应用（可选）

### 4.1 设置密码
如果需要修改密码，可以：
1. 在GitHub上编辑 config.py 文件
2. 修改 SYSTEM_PASSWORD = "你的新密码"
3. 提交更改
4. Streamlit会自动重新部署

### 4.2 管理数据文件
- 示例数据文件不会上传到GitHub（已在.gitignore中排除）
- 用户需要在应用中上传自己的数据文件

## 注意事项

1. **数据安全**：确保不要将真实的敏感数据上传到GitHub
2. **密码管理**：建议定期更改访问密码
3. **仓库权限**：如果选择私有仓库，只有你能看到代码
4. **资源限制**：Streamlit Cloud免费版有一定的资源限制

## 常见问题

### Q: 推送失败怎么办？
A: 检查：
- 是否正确设置了远程仓库地址
- 是否使用了正确的Personal Access Token
- 网络连接是否正常

### Q: 部署后应用打不开？
A: 检查：
- requirements.txt中的依赖是否都正确
- app.py是否有语法错误
- 查看Streamlit Cloud的日志

### Q: 如何更新应用？
A: 在本地修改代码后：
```bash
git add .
git commit -m "更新说明"
git push
```
Streamlit会自动检测到更新并重新部署

## 联系支持
如有问题，可以：
1. 查看Streamlit文档：https://docs.streamlit.io
2. 访问Streamlit论坛：https://discuss.streamlit.io