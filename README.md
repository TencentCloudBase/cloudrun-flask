# 快速部署 Flask 应用

一个完整的 Flask 应用模板，支持快速部署到 CloudBase 平台。

## 🚀 快速开始

### 前置条件

- [Python 3.8](https://www.python.org/downloads/) 或更高版本
- 了解基本的 Python 虚拟环境使用
- 腾讯云账号并开通了 CloudBase 服务
- 基本的 Python 和 Flask 开发知识

### 创建应用

```bash
# 快速创建（基础步骤）
mkdir cloudrun-flask && cd cloudrun-flask
python -m venv env
source env/bin/activate  # Windows: env\Scripts\activate
pip install Flask==3.1.2 gunicorn==24.1.1
```

### 本地测试

```bash
# 启动开发服务器
python app.py
# 或者使用 Flask CLI
flask --app app run --host 0.0.0.0 --port 8080

# 访问应用
open http://localhost:8080
```

## 📦 项目结构

```
cloudrun-flask/
├── app.py                   # Flask 主应用文件
├── requirements.txt         # Python 依赖文件
├── .gitignore              # Git 忽略文件
├── env/                    # 虚拟环境（本地开发用）
├── scf_bootstrap           # HTTP 云函数启动脚本
├── Dockerfile              # 云托管容器配置
└── .dockerignore           # Docker 忽略文件
```

## 🎯 部署方式

### 部署方式对比

| 特性 | HTTP 云函数 | 云托管 |
|------|------------|--------|
| **计费方式** | 按请求次数和执行时间 | 按资源使用量（CPU/内存） |
| **启动方式** | 冷启动，按需启动 | 持续运行 |
| **适用场景** | API 服务、轻量级应用 | 企业级应用、复杂 Web 应用 |
| **端口要求** | 固定 9000 端口 | 可自定义端口（默认 8080） |
| **扩缩容** | 自动按请求扩缩 | 支持自动扩缩容配置 |
| **Python 环境** | 预配置 Python 运行时 | 完全自定义 Python 环境 |

### 选择部署方式

- **选择 HTTP 云函数**：轻量级 API 服务、间歇性访问、成本敏感
- **选择云托管**：企业级应用、复杂 Web 应用、需要更多控制权

## 📚 详细部署指南

### 🔥 HTTP 云函数部署

适合轻量级应用和 API 服务，按请求计费，冷启动快。

**快速部署步骤：**
1. 创建 `scf_bootstrap` 启动脚本
2. 包含虚拟环境目录
3. 通过 CloudBase 控制台上传部署

**scf_bootstrap 示例：**
```bash
#!/bin/bash
export PORT=9000
export PYTHONPATH="./env/lib/python3.10/site-packages:$PYTHONPATH"
/var/lang/python310/bin/python3.10 app.py
```

### 🐳 云托管部署

适合企业级应用，支持更复杂的部署需求，容器化部署。

**快速部署步骤：**
1. 创建 `Dockerfile` 容器配置
2. 配置 `.dockerignore` 文件
3. 通过 CloudBase 控制台或 CLI 部署

**Dockerfile 示例：**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
```

## 🔧 API 接口

本模板包含以下 RESTful API 接口：

### 基础接口
```bash
GET /                        # 欢迎页面
GET /health                  # 健康检查
```

### 用户管理
```bash
GET /api/users               # 获取用户列表（支持分页）
GET /api/users/{user_id}     # 获取单个用户
POST /api/users              # 创建用户
PUT /api/users/{user_id}     # 更新用户
DELETE /api/users/{user_id}  # 删除用户
```

### 示例请求

```bash
# 健康检查
curl https://your-app-url/health

# 获取用户列表（分页）
curl "https://your-app-url/api/users?page=1&limit=5"

# 创建新用户
curl -X POST https://your-app-url/api/users \
  -H "Content-Type: application/json" \
  -d '{"name":"测试用户","email":"test@example.com"}'

# 更新用户
curl -X PUT https://your-app-url/api/users/1 \
  -H "Content-Type: application/json" \
  -d '{"name":"更新用户","email":"updated@example.com"}'

# 删除用户
curl -X DELETE https://your-app-url/api/users/1
```

## ❓ 常见问题

### 端口配置
- **HTTP 云函数**：必须使用 9000 端口
- **云托管**：推荐使用 8080 端口，支持自定义

### 文件要求
- **HTTP 云函数**：需要 `scf_bootstrap` 启动脚本和 `env` 目录
- **云托管**：需要 `Dockerfile` 和 `.dockerignore`

### 数据存储
- 当前使用内存存储（重启后数据丢失）
- 生产环境建议集成数据库（PostgreSQL、MySQL 等）

### 如何选择部署方式？
- **轻量级应用**：选择 HTTP 云函数
- **企业级应用**：选择云托管
- **成本敏感**：选择 HTTP 云函数
- **需要持续运行**：选择云托管

## 🛠️ 开发工具

### 推荐的开发依赖

```bash
# 核心框架
pip install Flask==3.1.2

# 生产服务器
pip install gunicorn==24.1.1

# 数据库支持
pip install Flask-SQLAlchemy psycopg2-binary

# 环境变量
pip install python-dotenv==1.2.1

# API 开发
pip install Flask-RESTful Flask-CORS
```

### 环境变量配置

创建 `.env` 文件：

```env
# 应用配置
DEBUG=True
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
PORT=8080

# 数据库配置（可选）
DATABASE_URL=postgresql://user:password@localhost/dbname
```

## 📖 进阶功能

- **蓝图支持**：模块化应用结构
- **模板引擎**：Jinja2 模板支持
- **数据库集成**：SQLAlchemy ORM 支持
- **会话管理**：Flask-Session 支持
- **认证授权**：Flask-Login 和 Flask-JWT 支持
- **API 文档**：Flask-RESTX 自动文档生成

## 🔗 相关链接

### 🌐 官方文档
- [CloudBase 官方文档](https://docs.cloudbase.net/)
- [Flask 官方文档](https://flask.palletsprojects.com/)
- [Python 官方文档](https://docs.python.org/)

## 📄 许可证

本项目采用 MIT 许可证。详情请查看 [LICENSE](./LICENSE) 文件。

---

**需要帮助？** 

- 查看 [Flask 官方文档](https://flask.palletsprojects.com/)
- 访问 [CloudBase 官方文档](https://docs.cloudbase.net/)
- 参考 [Flask 快速入门](https://flask.palletsprojects.com/quickstart/)