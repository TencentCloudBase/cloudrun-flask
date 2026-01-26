# 快速部署 Flask 应用

## 📋 目录导航

- [部署方式对比](#部署方式对比)
- [前置条件](#前置条件)
- [第一步：创建 Flask 应用](#第一步创建-flask-应用)
- [第二步：添加 API 路由](#第二步添加-api-路由)
- [第三步：本地测试](#第三步本地测试)
- [第四步：准备部署文件](#第四步准备部署文件)
- [第五步：项目结构](#第五步项目结构)
- [第六步：部署应用](#第六步部署应用)
- [第七步：访问您的应用](#第七步访问您的应用)
- [常见问题](#常见问题)
- [最佳实践](#最佳实践)
- [进阶功能](#进阶功能)

---

[Flask](https://flask.palletsprojects.com/) 是一个轻量级的 Python Web 框架，它简单易用且高度可扩展。Flask 被称为"微框架"，因为它不需要特定的工具或库，但可以通过扩展来添加功能。

本指南介绍如何在 CloudBase 上部署 Flask 应用程序，支持两种部署方式：

- **HTTP 云函数**：适合轻量级应用和 API 服务，按请求计费，冷启动快
- **云托管**：适合企业级应用，支持更复杂的部署需求，容器化部署

## 部署方式对比

| 特性 | HTTP 云函数 | 云托管 |
|------|------------|--------|
| **计费方式** | 按请求次数和执行时间 | 按资源使用量（CPU/内存） |
| **启动方式** | 冷启动，按需启动 | 持续运行 |
| **适用场景** | API 服务、轻量级应用 | 企业级应用、复杂 Web 应用 |
| **部署文件** | 需要 `scf_bootstrap` 启动脚本 | 需要 `Dockerfile` 容器配置 |
| **端口要求** | 固定 9000 端口 | 可自定义端口（默认 8080） |
| **扩缩容** | 自动按请求扩缩 | 支持自动扩缩容配置 |
| **Python 环境** | 预配置 Python 运行时 | 完全自定义 Python 环境 |

## 前置条件

在开始之前，请确保您已经：

- 安装了 [Python 3.10](https://www.python.org/downloads/) 或更高版本
- 了解基本的 Python 虚拟环境使用
- 拥有腾讯云账号并开通了 CloudBase 服务
- 了解基本的 Python 和 Flask 开发知识

## 第一步：创建 Flask 应用

> 💡 **提示**：如果您已经有一个 Flask 应用，可以跳过此步骤。

### 创建项目目录

```bash
mkdir cloudrun-flask
cd cloudrun-flask
```

### 创建虚拟环境

```bash
# 创建虚拟环境（推荐使用 Python 3.10）
python -m venv env

# 激活虚拟环境
# Windows
env\Scripts\activate
# macOS/Linux
source env/bin/activate
```

### 安装 Flask 和依赖

```bash
# 安装 Flask
pip install flask

# 生成依赖文件
pip freeze > requirements.txt
```

### 创建主应用文件

在 `cloudrun-flask` 目录下创建 `app.py` 文件：

```python
import os
from flask import Flask, jsonify, request

# 创建 Flask 应用实例
app = Flask(__name__)

# 配置应用
app.config['DEBUG'] = os.environ.get('DEBUG', 'False').lower() == 'true'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# 模拟数据
users = [
    {'id': 1, 'name': '张三', 'email': 'zhangsan@example.com'},
    {'id': 2, 'name': '李四', 'email': 'lisi@example.com'},
    {'id': 3, 'name': '王五', 'email': 'wangwu@example.com'}
]

@app.route('/')
def hello():
    """根路径处理函数"""
    return jsonify({'message': 'Hello from Flask on CloudBase!', 'framework': 'Flask', 'version': '2.3.0'})

@app.route('/health')
def health_check():
    """健康检查接口"""
    return jsonify({'status': 'healthy', 'framework': 'Flask', 'python_version': os.sys.version})

@app.route('/api/users', methods=['GET'])
def get_users():
    """获取用户列表（支持分页）"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    # 简单分页逻辑
    start_index = (page - 1) * limit
    end_index = start_index + limit
    paginated_users = users[start_index:end_index]
    return jsonify({
        'success': True,
        'data': {
            'total': len(users),
            'page': page,
            'limit': limit,
            'items': paginated_users
        }
    })

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """根据 ID 获取用户"""
    user = next((u for u in users if u['id'] == user_id), None)
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    return jsonify({'success': True, 'data': user})

@app.route('/api/users', methods=['POST'])
def create_user():
    """创建新用户"""
    data = request.get_json()
    if not data or 'name' not in data or 'email' not in data:
        return jsonify({'success': False, 'message': 'Name and email are required'}), 400
    
    # 检查邮箱是否已存在
    if any(u['email'] == data['email'] for u in users):
        return jsonify({'success': False, 'message': 'Email already exists'}), 400
    
    # 创建新用户
    new_user = {
        'id': max(u['id'] for u in users) + 1 if users else 1,
        'name': data['name'],
        'email': data['email']
    }
    users.append(new_user)
    return jsonify({'success': True, 'data': new_user}), 201

@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """更新用户信息"""
    user_index = next((i for i, u in enumerate(users) if u['id'] == user_id), None)
    if user_index is None:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400
    
    # 检查邮箱是否被其他用户使用
    if 'email' in data and any(u['email'] == data['email'] and u['id'] != user_id for u in users):
        return jsonify({'success': False, 'message': 'Email already exists'}), 400
    
    # 更新用户信息
    if 'name' in data:
        users[user_index]['name'] = data['name']
    if 'email' in data:
        users[user_index]['email'] = data['email']
        
    return jsonify({'success': True, 'data': users[user_index]})

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """删除用户"""
    user_index = next((i for i, u in enumerate(users) if u['id'] == user_id), None)
    if user_index is None:
        return jsonify({'success': False, 'message': 'User not found'}), 404
        
    deleted_user = users.pop(user_index)
    return jsonify({'success': True, 'message': f'User {deleted_user["name"]} deleted successfully'})

# 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'message': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'message': 'Internal server error'}), 500

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'success': False, 'message': 'Bad request'}), 400

if __name__ == '__main__':
    # 默认端口 8080，HTTP 云函数通过环境变量设置为 9000
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
```

### 本地测试应用

启动开发服务器：

```bash
python app.py
```

或者使用 Flask 命令：

```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=8080
```

打开浏览器访问 `http://localhost:8080`，您应该能看到 JSON 响应。

## 第二步：本地测试

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动应用

```bash
python app.py
```

### 测试 API 接口

```bash
# 测试健康检查
curl http://localhost:8080/health

# 测试首页
curl http://localhost:8080/

# 测试用户列表
curl http://localhost:8080/api/users

# 测试分页
curl "http://localhost:8080/api/users?page=1&limit=2"

# 测试获取单个用户
curl http://localhost:8080/api/users/1

# 测试创建用户
curl -X POST http://localhost:8080/api/users \
  -H "Content-Type: application/json" \
  -d '{"name":"新用户","email":"newuser@example.com"}'

# 测试更新用户
curl -X PUT http://localhost:8080/api/users/1 \
  -H "Content-Type: application/json" \
  -d '{"name":"更新的用户名"}'

# 测试删除用户
curl -X DELETE http://localhost:8080/api/users/1
```

## 第三步：准备部署文件

根据您选择的部署方式，需要准备不同的配置文件：

### 📋 选择部署方式

<details>
<summary><strong>🔥 HTTP 云函数部署配置</strong></summary>

HTTP 云函数需要 `scf_bootstrap` 启动脚本和特定的端口配置。

#### 1. 创建启动脚本

创建 `scf_bootstrap` 文件（无扩展名）：

```bash
#!/bin/bash
export PORT=9000
export PYTHONPATH="./env/lib/python3.10/site-packages:$PYTHONPATH"
/var/lang/python310/bin/python3.10 app.py
```

为启动脚本添加执行权限：

```bash
chmod +x scf_bootstrap
```

#### 2. 项目结构

```
cloudrun-flask/
├── app.py                   # 主应用文件
├── requirements.txt         # Python 依赖
├── scf_bootstrap           # 🔑 云函数启动脚本
└── env/                   # 🔑 虚拟环境（部署时需要包含）
    └── lib/
        └── python3.10/
            └── site-packages/  # Python 依赖包
```

> 💡 **说明**：
> - `scf_bootstrap` 是 CloudBase 云函数的启动脚本
> - 设置 `PORT=9000` 环境变量确保应用监听云函数要求的端口
> - 设置 `PYTHONPATH` 环境变量确保应用能找到依赖包
> - 使用云函数运行时环境的 Python 解释器启动应用
> - **重要**：HTTP 云函数部署时需要包含 `env` 目录及其依赖包
> - 云函数会自动安装 `requirements.txt` 中的依赖，但建议同时上传 `env` 目录以确保依赖完整性

</details>

<details>
<summary><strong>🐳 云托管部署配置</strong></summary>

云托管使用 Docker 容器化部署，需要 `Dockerfile` 配置文件。

#### 1. 创建 Dockerfile

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

#### 2. 创建 .dockerignore 文件

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
```

#### 3. 项目结构

```
cloudrun-flask/
├── app.py                   # 主应用文件
├── requirements.txt         # Python 依赖
├── Dockerfile              # 🔑 容器配置文件
├── .dockerignore           # Docker 忽略文件
└── env/                   # 虚拟环境（部署时排除）
```

> 💡 **说明**：
> - 云托管支持自定义端口，默认使用 8080 端口
> - 直接使用 Flask 内置服务器启动应用
> - Docker 容器提供了完整的 Python 环境控制

</details>

## 第五步：项目结构

确保您的项目目录结构包含必要的文件。根据部署方式的不同，某些文件是可选的：

```
cloudrun-flask/
├── app.py                   # 主应用文件
├── requirements.txt         # Python 依赖文件
├── env/                   # 虚拟环境（本地开发用）
├── scf_bootstrap           # HTTP 云函数启动脚本 (仅云函数需要)
├── Dockerfile              # 云托管容器配置 (仅云托管需要)
└── .dockerignore           # Docker 忽略文件 (仅云托管需要)
```

## 第六步：部署应用

选择您需要的部署方式：

### 🚀 部署方式选择

<details>
<summary><strong>🔥 部署到 HTTP 云函数</strong></summary>

#### 通过控制台部署

1. 登录 [CloudBase 控制台](https://console.cloud.tencent.com/tcb)
2. 选择您的环境，进入「云函数」页面
3. 点击「新建云函数」
4. 选择「HTTP 云函数」
5. 填写函数名称（如：`cloudrun-flask-app`）
6. 选择运行时：**Python 3.10**（或其他支持的版本）
7. 提交方法选择：**本地上传文件夹**
8. 函数代码选择 `cloudrun-flask` 目录进行上传
9. **自动安装依赖**：开启此选项
10. 点击「创建」按钮等待部署完成

#### 通过 CLI 部署(敬请期待)

#### 打包部署

如果需要手动打包：

```bash
# 创建部署包（包含 env 目录）
zip -r cloudrun-flask-app.zip . -x ".git/*" "*.log" "Dockerfile" ".dockerignore" "__pycache__/*"
```

</details>

<details>
<summary><strong>🐳 部署到云托管</strong></summary>

#### 通过控制台部署

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

#### 通过 CLI 部署

```bash
# 安装 CloudBase CLI
npm install -g @cloudbase/cli

# 登录
tcb login

# 部署云托管服务
tcb run deploy --port 8080
```

#### 模板部署（快速开始）

1. 登录 [腾讯云托管控制台](https://tcb.cloud.tencent.com/dev#/platform-run/service/create?type=image)
2. 点击「通过模板部署」，选择 **Flask 模板**
3. 输入自定义服务名称，点击部署
4. 等待部署完成后，点击左上角箭头，返回到服务详情页
5. 点击概述，获取默认域名并访问

</details>

## 第七步：访问您的应用

### HTTP 云函数访问

部署成功后，您可以参考[通过 HTTP 访问云函数](https://docs.cloudbase.net/service/access-cloud-function)设置自定义域名访问 HTTP 云函数。

访问地址格式：`https://your-function-url/`

### 云托管访问

云托管部署成功后，系统会自动分配访问地址。您也可以绑定自定义域名。

访问地址格式：`https://your-service-url/`

### 测试接口

无论使用哪种部署方式，您都可以测试以下接口：

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
curl https://your-app-url/health

# 获取用户列表
curl https://your-app-url/api/users

# 分页查询
curl "https://your-app-url/api/users?page=1&limit=2"

# 创建新用户
curl -X POST https://your-app-url/api/users \
  -H "Content-Type: application/json" \
  -d '{"name":"测试用户","email":"test@example.com"}'
```

## 常见问题

### ❓ 问题分类

<details>
<summary><strong>🔥 HTTP 云函数相关问题</strong></summary>

#### Q: 为什么 HTTP 云函数必须使用 9000 端口？
A: CloudBase HTTP 云函数要求应用监听 9000 端口，这是平台的标准配置。通过在 `scf_bootstrap` 中设置 `PORT=9000` 环境变量来控制端口，本地开发时默认使用 8080 端口。应用代码通过 `os.environ.get('PORT', 8080)` 实现端口的动态配置。

#### Q: Python 依赖如何管理？
A: 云函数会自动安装 `requirements.txt` 中列出的依赖包。建议固定版本号以确保部署一致性。

#### Q: 如何优化 Flask 应用的冷启动时间？
A: 
- 减少依赖包数量
- 避免在启动时进行重复的初始化操作
- 使用轻量级的依赖包
- 合理设置内存配置

#### Q: scf_bootstrap 文件有什么作用？
A: `scf_bootstrap` 是云函数的启动脚本，用于设置环境变量和启动 Python 应用。

#### Q: 虚拟环境依赖如何处理？
A: HTTP 云函数部署时需要包含 `env` 目录及其依赖包。在 `scf_bootstrap` 中通过 `PYTHONPATH` 环境变量指向虚拟环境的 site-packages 目录，确保应用能正确加载依赖。同时建议在虚拟环境中生成 `requirements.txt`，避免包含系统级包。

</details>

<details>
<summary><strong>🐳 云托管相关问题</strong></summary>

#### Q: 云托管支持哪些端口？
A: 云托管支持自定义端口，Flask 应用默认使用 8080 端口，也可以根据需要配置其他端口。

#### Q: 为什么直接使用 Flask 内置服务器？
A: 在云托管环境中，容器提供了隔离的运行环境，Flask 内置服务器可以满足基本的生产需求。如需更高性能，可以考虑使用 gunicorn 等 WSGI 服务器。

#### Q: 如何优化 Docker 镜像构建速度？
A: 
- 使用国内 pip 镜像源
- 合理设置 `.dockerignore`
- 使用多阶段构建（如果需要）
- 选择合适的基础镜像

#### Q: Dockerfile 中为什么使用 python:3.11-slim？
A: `python:3.11-slim` 是轻量级的 Python 镜像，包含了运行 Python 应用所需的基本环境，镜像体积小，启动快。

#### Q: CLI 部署和控制台部署有什么区别？
A: 
- **CLI 部署**：适合开发者，支持自动化部署、CI/CD 集成，可以通过配置文件管理
- **控制台部署**：适合可视化操作，界面友好，适合初学者和运维人员

#### Q: 如何配置 cloudbaserc.json？
A: 
- `envId`：CloudBase 环境 ID
- `serviceName`：云托管服务名称
- `containerPort`：容器内应用监听端口
- `cpu` 和 `mem`：资源配置
- `envVariables`：环境变量配置

#### Q: CLI 部署失败怎么办？
A: 
- 检查 CloudBase CLI 是否已登录：`cloudbase auth list`
- 确认环境 ID 是否正确
- 检查 Dockerfile 语法是否正确
- 查看部署日志：`cloudbase run logs --name service-name`

</details>

<details>
<summary><strong>🔧 通用问题</strong></summary>

#### Q: 如何处理静态文件？
A: Flask 可以使用 `send_static_file` 或配置静态文件目录来处理静态资源。

#### Q: 如何查看应用日志？
A: 
- **HTTP 云函数**：在 CloudBase 控制台的云函数页面查看运行日志
- **云托管**：在云托管服务详情页面查看实例日志

#### Q: 支持哪些 Python 版本？
A: CloudBase 支持 Python 3.7、3.8、3.9、3.10、3.11 等版本，建议使用最新的稳定版本。

#### Q: 如何处理 CORS 跨域问题？
A: 可以使用 Flask-CORS 扩展或手动设置响应头来处理跨域请求。

#### Q: 两种部署方式如何选择？
A: 
- **选择 HTTP 云函数**：轻量级 API 服务、间歇性访问、成本敏感
- **选择云托管**：企业级应用、复杂 Web 应用、需要更多控制权

</details>

## 最佳实践

### 1. 环境变量管理

使用 python-dotenv 管理环境变量：

```python
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# Flask 配置
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    DEBUG = os.getenv('FLASK_ENV') == 'development'

app.config.from_object(Config)
```

### 2. 端口配置策略

为了同时支持两种部署方式，建议使用动态端口配置：

```python
import os

if __name__ == '__main__':
    # 默认端口 8080，HTTP 云函数通过环境变量设置为 9000
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
```

### 3. 添加 CORS 支持

```bash
pip install Flask-CORS
```

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=['*'])  # 生产环境应该设置具体域名
```

### 4. 数据验证和错误处理

```python
from functools import wraps
from flask import request, jsonify

def validate_json(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return jsonify({"error": "请求必须是 JSON 格式"}), 400
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/users', methods=['POST'])
@validate_json
def create_user():
    data = request.get_json()
    # 处理逻辑...
```

### 5. 日志配置

```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    # 生产环境日志配置
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Flask application startup')
```

### 6. 蓝图组织代码

```python
from flask import Blueprint

# 创建蓝图
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/users')
def get_users():
    return jsonify({"users": []})

# 注册蓝图
app.register_blueprint(api_bp)
```

### 7. 数据库集成

```bash
pip install Flask-SQLAlchemy
```

```python
from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
```

### 8. 部署前检查清单

<details>
<summary><strong>🔥 HTTP 云函数部署检查</strong></summary>

#### HTTP 云函数部署检查

- [ ] `scf_bootstrap` 文件存在且有执行权限
- [ ] 端口配置为 9000
- [ ] `requirements.txt` 包含所有必需依赖
- [ ] **包含 `env` 目录及其依赖包**
- [ ] 排除不必要的文件（如 `Dockerfile`、`.dockerignore`）
- [ ] 测试本地启动是否正常
- [ ] 检查启动脚本语法是否正确

</details>

<details>
<summary><strong>🐳 云托管部署检查</strong></summary>

#### 云托管部署检查

- [ ] `Dockerfile` 文件存在且配置正确
- [ ] `.dockerignore` 文件配置合理
- [ ] 端口配置灵活（支持环境变量）
- [ ] 容器启动命令正确
- [ ] **排除 `env` 目录**（云托管使用 Docker 容器内的 Python 环境）
- [ ] 排除不必要的文件（如 `scf_bootstrap`）
- [ ] 本地 Docker 构建测试通过

</details>

## 进阶功能

### 数据库集成

集成 SQLAlchemy 和 PostgreSQL：

```bash
pip install Flask-SQLAlchemy psycopg2-binary Flask-Migrate
```

### 身份验证

添加 JWT 身份验证：

```bash
pip install Flask-JWT-Extended
```

### API 文档

使用 Flask-RESTX 生成 API 文档：

```bash
pip install flask-restx
```

### 缓存支持

添加 Redis 缓存：

```bash
pip install Flask-Caching redis
```

### 表单处理

添加 WTForms 表单验证：

```bash
pip install Flask-WTF WTForms
```