# Flask 云托管部署指南

本指南详细介绍如何将 Flask 应用部署到 CloudBase 云托管服务。

> **📋 前置要求**：如果您还没有创建 Flask 项目，请先阅读 [Flask 项目创建指南](./project-setup.md)。

## 📋 目录导航

- [部署特性](#部署特性)
- [准备部署文件](#准备部署文件)
- [项目结构](#项目结构)
- [部署步骤](#部署步骤)
- [访问应用](#访问应用)
- [常见问题](#常见问题)
- [最佳实践](#最佳实践)
- [高级配置](#高级配置)

---

## 部署特性

云托管适合以下场景：

- **企业级应用**：复杂的 Web 应用和管理系统
- **高并发**：需要处理大量并发请求
- **自定义环境**：需要特定的运行时环境
- **微服务架构**：容器化部署和管理

### 技术特点

| 特性 | 说明 |
|------|------|
| **计费方式** | 按资源使用量（CPU/内存） |
| **启动方式** | 持续运行 |
| **端口配置** | 可自定义端口（默认 8080） |
| **扩缩容** | 支持自动扩缩容配置 |
| **Python 环境** | 完全自定义 Python 环境 |

## 准备部署文件

### 1. 创建 Dockerfile

创建 `Dockerfile` 文件：

```dockerfile
# 使用官方 Python 运行时作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 设置 pip 镜像源以提高下载速度
RUN pip config set global.index-url https://mirrors.cloud.tencent.com/pypi/simple/ \
    && pip config set global.trusted-host mirrors.cloud.tencent.com

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8080

# 设置环境变量
ENV PORT=8080
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# 启动命令
CMD ["python", "app.py"]
```

### 2. 创建 .dockerignore 文件

创建 `.dockerignore` 文件以优化构建性能：

```
env/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
.git
.gitignore
README.md
.env
.DS_Store
*.log
.pytest_cache/
.coverage
scf_bootstrap
.vscode/
.idea/
*.db
*.sqlite3
docs/
```

### 3. 优化 app.py

确保 `app.py` 支持云托管环境：

```python
import os
from flask import Flask, jsonify, request

# 创建 Flask 应用实例
app = Flask(__name__)

# 配置应用
app.config['DEBUG'] = os.environ.get('DEBUG', 'False').lower() == 'true'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# ... 其他代码保持不变 ...

if __name__ == '__main__':
    # 默认端口 8080，HTTP 云函数通过环境变量设置为 9000
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
```

### 4. 依赖管理

确保 `requirements.txt` 包含所有必要依赖：

```txt
Flask==2.3.3
gunicorn>=21.0.0
python-dotenv>=1.0.0
```

## 项目结构

```
cloudrun-flask/
├── app.py                  # Flask 主应用文件
├── requirements.txt        # Python 依赖
├── Dockerfile              # 🔑 容器配置文件
├── .dockerignore           # Docker 忽略文件
└── .gitignore             # Git 忽略文件
```

> 💡 **说明**：
> - 云托管支持自定义端口，默认使用 8080 端口
> - 使用 Flask 内置开发服务器或 Gunicorn 启动应用
> - Docker 容器提供了完整的 Python 环境控制

## 部署步骤

### 通过控制台部署

1. 登录 [CloudBase 控制台](https://console.cloud.tencent.com/tcb)
2. 选择您的环境，进入「云托管」页面
3. 点击「新建服务」
4. 填写服务名称（如：`cloudrun-flask-service`）
5. 选择「本地代码」上传方式
6. 上传包含 `Dockerfile` 的项目目录
7. 配置服务参数：
   - **端口**：8080（或您在应用中配置的端口）
   - **CPU**：0.25 核
   - **内存**：0.5 GB
   - **实例数量**：1-10（根据需求调整）
8. 点击「创建」按钮等待部署完成

### 通过 CLI 部署

```bash
# 安装 CloudBase CLI
npm install -g @cloudbase/cli

# 登录
tcb login

# 初始化云托管配置
tcb run init

# 部署云托管服务
tcb run deploy --port 8080
```

### 配置文件部署

创建 `cloudbaserc.json` 配置文件：

```json
{
  "envId": "your-env-id",
  "framework": {
    "name": "flask",
    "plugins": {
      "run": {
        "name": "@cloudbase/framework-plugin-run",
        "options": {
          "serviceName": "cloudrun-flask-service",
          "servicePath": "/",
          "localPath": "./",
          "dockerfile": "./Dockerfile",
          "buildDir": "./",
          "cpu": 0.25,
          "mem": 0.5,
          "minNum": 1,
          "maxNum": 10,
          "policyType": "cpu",
          "policyThreshold": 60,
          "containerPort": 8080,
          "envVariables": {
            "FLASK_ENV": "production",
            "DEBUG": "False"
          }
        }
      }
    }
  }
}
```

然后执行部署：

```bash
tcb framework deploy
```

### 模板部署（快速开始）

1. 登录 [腾讯云托管控制台](https://tcb.cloud.tencent.com/dev#/platform-run/service/create?type=image)
2. 点击「通过模板部署」，选择 **Flask 模板**
3. 输入自定义服务名称，点击部署
4. 等待部署完成后，点击左上角箭头，返回到服务详情页
5. 点击概述，获取默认域名并访问

## 访问应用

### 获取访问地址

云托管部署成功后，系统会自动分配访问地址。您也可以绑定自定义域名。

访问地址格式：`https://your-service-url/`

### 测试接口

- **根路径**：`/` - Flask 欢迎页面
- **健康检查**：`/health` - 查看应用状态
- **用户列表**：`/api/users` - 获取用户列表
- **用户详情**：`/api/users/1` - 获取特定用户
- **创建用户**：`POST /api/users` - 创建新用户
- **更新用户**：`PUT /api/users/1` - 更新用户信息
- **删除用户**：`DELETE /api/users/1` - 删除用户

### 示例请求

```bash
# 健康检查
curl https://your-service-url/health

# 获取用户列表
curl https://your-service-url/api/users

# 分页查询
curl "https://your-service-url/api/users?page=1&limit=2"

# 创建新用户
curl -X POST https://your-service-url/api/users \
  -H "Content-Type: application/json" \
  -d '{"name":"测试用户","email":"test@example.com"}'
```

## 常见问题

### Q: 云托管支持哪些端口？
A: 云托管支持自定义端口，Flask 应用默认使用 8080 端口，也可以根据需要配置其他端口。

### Q: 如何配置生产环境设置？
A: 通过环境变量控制应用配置：

```python
# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///app.db')

class ProductionConfig(Config):
    DEBUG = False

class DevelopmentConfig(Config):
    DEBUG = True

config = {
    'production': ProductionConfig,
    'development': DevelopmentConfig,
    'default': ProductionConfig
}
```

### Q: 如何配置环境变量？
A: 可以通过以下方式配置：
- 控制台服务配置页面
- `cloudbaserc.json` 配置文件
- Dockerfile 中的 ENV 指令

### Q: Flask 应用如何处理静态文件？
A: 在云托管环境中，可以配置 Flask 处理静态文件：

```python
@app.route('/static/<path:filename>')
def static_files(filename):
    return app.send_static_file(filename)
```

### Q: 如何查看云托管日志？
A: 在云托管服务详情页面可以查看：
- 实例日志
- 构建日志
- 访问日志
- 错误日志

## 最佳实践

### 1. 多阶段构建优化

```dockerfile
# 构建阶段
FROM python:3.11-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# 运行阶段
FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .

# 确保 Python 用户包在 PATH 中
ENV PATH=/root/.local/bin:$PATH

EXPOSE 8080
CMD ["python", "app.py"]
```

### 2. 使用 Gunicorn 生产服务器

```dockerfile
# Dockerfile 中使用 Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "app:app"]
```

```python
# gunicorn.conf.py
bind = "0.0.0.0:8080"
workers = 2
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
```

### 3. 环境变量管理

```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    PORT = int(os.getenv('PORT', 8080))
    
    # 数据库配置
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///app.db')

class ProductionConfig(Config):
    DEBUG = False

class DevelopmentConfig(Config):
    DEBUG = True

config = {
    'production': ProductionConfig,
    'development': DevelopmentConfig,
    'default': ProductionConfig
}
```

### 4. 健康检查增强

```python
# app.py
import sys
import os
from flask import Flask, jsonify
from datetime import datetime

@app.route('/health')
def health_check():
    """增强的健康检查接口"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "framework": "Flask",
        "deployment": "云托管",
        "version": "2.3.0",
        "python_version": sys.version,
        "environment": os.environ.get("FLASK_ENV", "production")
    })
```

### 5. 日志配置

```python
# logging_config.py
import logging
import sys
from flask import request, g
import time

def setup_logging(app):
    if not app.debug:
        # 生产环境日志配置
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)

    @app.before_request
    def before_request():
        g.start_time = time.time()

    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            app.logger.info(f'{request.method} {request.path} - {response.status_code} - {duration:.3f}s')
        return response
```

### 6. CORS 配置

```python
from flask_cors import CORS

# 基础 CORS 配置
CORS(app)

# 或者更精确的配置
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://yourdomain.com"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

### 7. 部署前检查清单

- [ ] `Dockerfile` 文件存在且配置正确
- [ ] `.dockerignore` 文件配置合理
- [ ] 端口配置灵活（支持环境变量）
- [ ] 容器启动命令正确
- [ ] **排除 `env` 目录**（云托管使用 Docker 容器内的 Python 环境）
- [ ] **排除 `scf_bootstrap` 文件**（仅用于云函数）
- [ ] 本地 Docker 构建测试通过
- [ ] Flask 应用配置正确

## 高级配置

### 1. 负载均衡配置

```json
{
  "run": {
    "name": "@cloudbase/framework-plugin-run",
    "options": {
      "serviceName": "cloudrun-flask-service",
      "cpu": 1,
      "mem": 2,
      "minNum": 2,
      "maxNum": 20,
      "policyType": "cpu",
      "policyThreshold": 70,
      "containerPort": 8080,
      "customLogs": "stdout",
      "initialDelaySeconds": 2
    }
  }
}
```

### 2. 数据库集成

```python
# database.py
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def init_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
```

### 3. Redis 缓存配置

```python
# cache.py
from flask_caching import Cache
import os

cache = Cache()

def init_cache(app):
    cache_config = {
        'CACHE_TYPE': 'redis',
        'CACHE_REDIS_URL': os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    }
    app.config.update(cache_config)
    cache.init_app(app)
```

### 4. 监控和告警

```python
# monitoring.py
import time
import logging
from flask import request, g

logger = logging.getLogger(__name__)

def init_monitoring(app):
    @app.before_request
    def before_request():
        g.start_time = time.time()

    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            
            # 记录慢请求
            if duration > 1.0:
                logger.warning(f"Slow request: {request.method} {request.path} - {duration:.3f}s")
            
            # 记录错误请求
            if response.status_code >= 400:
                logger.error(f"Error request: {request.method} {request.path} - {response.status_code}")
        
        return response
```

---

## 相关文档

- [返回主文档](../README.md)
- [HTTP 云函数部署指南](./http-function.md)
- [CloudBase 官方文档](https://docs.cloudbase.net/)