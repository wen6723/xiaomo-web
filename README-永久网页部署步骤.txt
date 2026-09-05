小茉永久网页版部署步骤
========================

需要准备的账号：
1. GitHub 账号（你已经有了）
2. Streamlit Community Cloud（你已经用 GitHub 授权了）

第 1 步：创建 GitHub 私有仓库
1. 打开 https://github.com/new
2. Repository name 填：xiaomo-web
3. 一定要选择 Private
4. 点击 Create repository

第 2 步：上传代码
1. 在刚创建的仓库页面选择 Add file > Upload files
2. 上传本目录里的：
   ai_partner.py
   requirements.txt
   .streamlit 文件夹（里面的 config.toml）
3. 不要上传 partner_memory.json，也不要上传 .gitignore 以外的隐私文件
4. 点击 Commit changes

第 3 步：把记忆放进私有 Gist
1. 打开 https://gist.github.com
2. Gist description 可填：xiaomo memory
3. Filename 填：partner_memory.json
4. 打开本目录旁边的“Gist初始记忆”文件夹，复制 partner_memory.json 的全部内容粘贴进去
5. 选择 Create secret gist（必须是 Secret，不能是 Public）
6. 创建后复制网址里最后一段 ID，例如：
   https://gist.github.com/你的用户名/abcd1234
   其中 abcd1234 就是 GIST_ID

第 4 步：创建 GitHub Token
1. 打开 https://github.com/settings/tokens
2. 点击 Generate new token > Generate new token (classic)
3. Note 填：xiaomo
4. Expiration 可选 90 days 或 No expiration
5. 勾选 gist 这一个 scope
6. 点击 Generate token，并复制 ghp_ 开头的 token

第 5 步：部署到 Streamlit Cloud
1. 打开 https://share.streamlit.io
2. 点击 New app
3. 选择你的 GitHub 仓库 xiaomo-web
4. Branch 选 main
5. Main file path 填：ai_partner.py
6. 点击 Deploy

第 6 步：添加密钥
1. 部署完成后进入 app 的 Settings > Secrets
2. 填入以下内容：

DEEPSEEK_API_KEY="你的 DeepSeek API Key"
APP_PASSWORD="你自己设置的访问密码"
GITHUB_TOKEN="第 4 步复制的 ghp_ token"
GIST_ID="第 3 步复制的 Gist ID"

3. 保存后回到 app 页面刷新

完成：打开 Streamlit 给你的网址，输入 APP_PASSWORD，就能在手机上永久访问小茉。
小茉的记忆会保存在你的私有 Gist 里，刷新、关电脑、服务器重启都不会丢。
