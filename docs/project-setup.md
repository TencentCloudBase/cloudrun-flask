# Flask 项目创建指南

本指南详细介绍如何从零开始创建一个适用于 CloudBase 部署的 Flask 项目。

## 📋 目录导航

- [环境准备](#环境准备)
- [创建项目](#创建项目)
- [基础配置](#基础配置)
- [创建应用](#创建应用)
- [路由和视图](#路由和视图)
- [安装依赖](#安装依赖)
- [本地测试](#本地测试)
- [下一步](#下一步)

---

## 环境准备

### 1. 检查 Python 版本

```bash
# 检查 Python 版本（推荐 3.8+）
python --version
# 或
python3 --version
```

### 2. 创建项目目录

```bash
# 创建项目根目录
mkdir cloudrun-flask && cd cloudrun-flask

# 创建虚拟环境
python -m venv env

# 激活虚拟环境
# Windows
env\Scripts\activate
# macOS/Linux
source env/bin/activate
```

## 创建项目

### 1. 安装 Flask

```bash
# 安装 Flask
pip install Flask

# 验证安装
python -c "import flask; print(flask.__version__)"
```

### 2. 创建主应用文件

创建 `app.py` 文件：

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

## 基础配置

### 1. 项目结构

```
cloudrun-flask/
├── app.py                  # Flask 主应用文件
├── requirements.txt        # Python 依赖
├── .gitignore             # Git 忽略文件
└── env/                   # 虚拟环境
```

### 2. 环境变量配置

Flask 应用支持通过环境变量进行配置：

```bash
# 设置端口（可选）
export PORT=8080

# 设置调试模式（可选）
export DEBUG=true
export FLASK_ENV=development

# 设置密钥（生产环境必须）
export SECRET_KEY=your-secret-key-here
```

## 创建应用

### 1. Flask 应用配置

Flask 应用的基本配置：

```python
# app.py
import os
from flask import Flask

app = Flask(__name__)

# 基础配置
app.config['DEBUG'] = os.environ.get('DEBUG', 'False').lower() == 'true'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# 数据库配置（如果需要）
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
```

### 2. 应用工厂模式（可选）

对于更复杂的应用，可以使用应用工厂模式：

```python
# app.py
import os
from flask import Flask

def create_app(config_name=None):
    app = Flask(__name__)
    
    # 加载配置
    if config_name == 'development':
        app.config['DEBUG'] = True
    elif config_name == 'production':
        app.config['DEBUG'] = False
    
    # 注册蓝图
    from routes import api_bp
    app.register_blueprint(api_bp)
    
    return app

if __name__ == '__main__':
    app = create_app(os.environ.get('FLASK_ENV', 'production'))
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
```

## 路由和视图

### 1. API 接口说明

Flask 应用包含以下接口：

- **根路径**：`GET /` - 应用欢迎信息
- **健康检查**：`GET /health` - 应用健康状态
- **用户列表**：`GET /api/users` - 获取用户列表（支持分页）
- **用户详情**：`GET /api/users/<id>` - 获取特定用户
- **创建用户**：`POST /api/users` - 创建新用户
- **更新用户**：`PUT /api/users/<id>` - 更新用户信息
- **删除用户**：`DELETE /api/users/<id>` - 删除用户

### 2. 请求处理

Flask 使用装饰器定义路由：

```python
@app.route('/api/users', methods=['GET', 'POST'])
def users():
    if request.method == 'GET':
        # 处理 GET 请求
        return get_users()
    elif request.method == 'POST':
        # 处理 POST 请求
        return create_user()

@app.route('/api/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
def user_detail(user_id):
    if request.method == 'GET':
        return get_user(user_id)
    elif request.method == 'PUT':
        return update_user(user_id)
    elif request.method == 'DELETE':
        return delete_user(user_id)
```

### 3. 错误处理

Flask 提供了灵活的错误处理机制：

```python
@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'message': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'message': 'Internal server error'}), 500

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'success': False, 'message': 'Bad request'}), 400
```

## 安装依赖

### 1. 基础依赖

```bash
# 安装基础依赖（与项目 requirements.txt 一致）
pip install Flask==2.3.3

# 如果需要数据库支持
pip install Flask-SQLAlchemy

# 如果需要 CORS 支持
pip install Flask-CORS

# 生产服务器
pip install gunicorn
```

### 2. 生成依赖文件

```bash
# 生成 requirements.txt
pip freeze > requirements.txt

# 查看生成的依赖（应该包含以下内容）
cat requirements.txt
# Flask==2.3.3
# Werkzeug==2.3.7
# Jinja2==3.1.2
# MarkupSafe==2.1.3
# itsdangerous==2.1.2
# click==8.1.7
```

### 3. 创建 .gitignore

```bash
cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Flask
instance/
.webassets-cache

# 虚拟环境
env/
venv/
.venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# 操作系统
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# 环境变量
.env
.env.local
.env.production

# 数据库
*.db
*.sqlite3

# 部署文件
deployment.zip
*.tar.gz

# CloudBase
.cloudbaserc.json
cloudbaserc.json
EOF
```

## 本地测试

### 1. 启动开发服务器

```bash
# 使用 Flask 内置开发服务器
python app.py

# 或者使用 flask 命令
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=8080

# 服务器启动后，访问以下地址测试：
# http://127.0.0.1:8080/          - 首页
# http://127.0.0.1:8080/health    - 健康检查
```

### 2. API 测试

```bash
# 测试基础接口
curl http://127.0.0.1:8080/
# 返回: {"framework": "Flask", "message": "Hello from Flask on CloudBase!", "version": "2.3.0"}

curl http://127.0.0.1:8080/health
# 返回: {"framework": "Flask", "python_version": "...", "status": "healthy"}

# 测试用户 API
# 获取用户列表
curl http://127.0.0.1:8080/api/users
curl "http://127.0.0.1:8080/api/users?page=1&limit=2"

# 创建用户
curl -X POST http://127.0.0.1:8080/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "测试用户", "email": "test@example.com"}'

# 获取单个用户
curl http://127.0.0.1:8080/api/users/1

# 更新用户
curl -X PUT http://127.0.0.1:8080/api/users/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "更新用户", "email": "updated@example.com"}'

# 删除用户
curl -X DELETE http://127.0.0.1:8080/api/users/1
```

### 3. 调试模式

在开发过程中启用调试模式：

```bash
export FLASK_ENV=development
export DEBUG=true
python app.py
```

## 下一步

项目创建完成后，根据您的部署需求选择相应的部署指南：

### 🚀 部署选择

| 部署方式 | 适用场景 | 详细指南 |
|----------|----------|----------|
| **HTTP 云函数** | 轻量级 API、间歇性访问 | [HTTP 云函数部署指南](./http-function.md) |
| **云托管** | 企业应用、高并发、持续运行 | [云托管部署指南](./cloud-run.md) |

### 📚 相关文档

- [返回主文档](../README.md)
- [HTTP 云函数部署指南](./http-function.md)
- [云托管部署指南](./cloud-run.md)

### 🔧 进一步开发

1. **数据库集成**：集成 Flask-SQLAlchemy 或 Flask-MongoEngine
2. **用户认证**：添加 Flask-Login 或 JWT 认证
3. **API 文档**：使用 Flask-RESTX 或 Flasgger 生成 API 文档
4. **表单处理**：使用 Flask-WTF 处理表单验证
5. **缓存**：集成 Flask-Caching 提升性能
6. **测试**：使用 pytest 编写单元测试

---

**提示**：Flask 的灵活性使其适合各种规模的应用开发，从简单的 API 到复杂的 Web 应用都能胜任。