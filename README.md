# ZJUMilCubesHelper

ZJUMilCubesHelper 是一个用于与 浙江大学 百万立方未来世界 课程平台进行交互的 Python 客户端库。它提供了简单易用的 API 来管理和操作平台上的项目内容。

项目的主要目的是使项目文章的内容编辑更加自由。

## 功能特性

- 支持多种登录方式（用户名密码、Cookies）
- 项目内容的获取与管理
- 文件上传功能
- 命令行工具支持

## 安装

本项目暂无上传到 PyPI 的包，你可以直接从 GitHub 下载源码并使用

## 快速开始

### 使用用户名密码登录

```python
from milcubes import MilCubesSession

# 创建会话
session = MilCubesSession.from_username_password('your_username', 'your_password')

# 获取项目列表
projects = session.get_projects()
for project in projects:
    print(f"项目ID: {project.id}, 标题: {project.title}")
```

### 使用 Cookies 登录

```python
from milcubes import MilCubesSession

# 从 JSON 文件加载 cookies
with open('cookies.json', 'r', encoding='utf-8') as f:
    cookies_json = f.read()
    
session = MilCubesSession.from_cookies_json(cookies_json)
```

### 下载项目内容

```python
# 获取特定项目
project = session.get_project(project_id)

# 下载项目内容
project.download_content()
```

### 上传文件

```python
# 上传文件
url, file_id = session.upload_file_by_path('path/to/file.pdf')
print(f"文件已上传: {url}")
```

## 命令行工具

ZJUMilCubesHelper 提供了便捷的命令行工具：

### 登录

```bash
python ./MilCubes/cli.py --username your_username --password your_password [operation]
# 或者使用 cookies 文件
python ./MilCubes/cli.py --cookies path/to/cookies.json [operation]
```

### 列出项目

```bash
python ./MilCubes/cli.py --username your_username --password your_password list
```

### 下载项目

```bash
# 通过项目 ID 下载
python ./MilCubes/cli.py --username your_username --password your_password download --id 123

# 通过项目标题下载
python ./MilCubes/cli.py --username your_username --password your_password download --title "项目标题"

# 下载所有项目
python ./MilCubes/cli.py --username your_username --password your_password download --all
```

### 上传项目内容

```bash
python ./MilCubes/cli.py --username your_username --password your_password upload --id 123 --file path/to/content.html
```

### 上传文件

```bash
python ./MilCubes/cli.py --username your_username --password your_password file --file path/to/file.pdf
```

## API 文档

### MilCubesSession

主要的会话类，用于与 MilCubes 平台交互。

#### 方法

- `from_username_password(username, password)`: 使用用户名密码创建会话
- `from_cookies(cookies)`: 使用 cookies 字典创建会话
- `from_cookies_json(cookies_json)`: 使用 JSON 格式的 cookies 创建会话
- `get_projects(offset=0, limit=1000)`: 获取项目列表
- `get_project(project_id)`: 获取单个项目
- `upload_file(content, file_name, mime_type)`: 上传文件内容
- `upload_file_by_path(file_path, mime_type)`: 通过文件路径上传文件

### Project

项目类，表示 MilCubes 平台上的一个项目。

#### 属性

- `id`: 项目 ID
- `title`: 项目标题
- `content`: 项目内容
- `cover`: 封面 URL
- `books`: 书籍 URL 列表
- `images`: 图片 URL 列表
- `videos`: 视频 URL 列表

#### 方法

- `download_content(output_dir='.')`: 下载项目内容到文件
- `upload(session)`: 上传项目内容
- `update(session)`: 从服务器更新项目数据

### ProjectCollection

项目集合类，用于管理多个项目。

#### 方法

- `find_by_id(project_id)`: 通过 ID 查找项目
- `find_by_title(title)`: 通过标题查找项目
- `download_all_content(output_dir='.')`: 下载所有项目内容
