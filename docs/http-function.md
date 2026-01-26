# Flask HTTP 云函数部署指南

本指南详细介绍如何将 Flask 应用部署到 CloudBase HTTP 云函数。

> **📋 前置要求**：如果您还没有创建 Flask 项目，请先阅读 [Flask 项目创建指南](./project-setup.md)。

## 📋 目录导航

- [部署特性](#部署特性)
- [准备部署文件](#准备部署文件)
- [项目结构](#项目结构)
- [部署步骤](#部署步骤)
- [访问应用](#访问应用)
- [常见问题](#常见问题)
- [最佳实践](#最佳实践)
- [性能优化](#性能优化)

---

## 部署特性

HTTP 云函数适合以下场景：

- **轻量级 API**：RESTful API 服务、微服务
- **间歇性访问**：不需要持续运行的应用
- **成本敏感**：按请求次数和执行时间计费
- **快速部署**：无需容器化配置

### 技术特点

| 特性 | 说明 |
|------|------|
| **计费方式** | 按请求次数和执行时间 |
| **启动方式** | 冷启动，按需启动 |
| **端口要求** | 固定 9000 端口 |
| **扩缩容** | 自动按请求扩缩 |
| **Python 环境** | 预配置 Python 运行时 |

## 准备部署文件

### 1. 创建启动脚本

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

### 2. 优化 app.py

确保 `app.py` 支持云函数环境：

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

### 3. 依赖管理

确保 `requirements.txt` 包含必要依赖：

```txt
Flask==2.3.3
```

## 项目结构

```
cloudrun-flask/
├── app.py                  # Flask 主应用文件
├── requirements.txt        # Python 依赖
├── scf_bootstrap          # 🔑 云函数启动脚本
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

## 部署步骤

### 通过控制台部署

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

### 通过 CLI 部署

```bash
# 安装 CloudBase CLI
npm install -g @cloudbase/cli

# 登录
tcb login

# 部署云函数
tcb functions:deploy cloudrun-flask-app --dir ./
```

### 打包部署

如果需要手动打包：

```bash
# 创建部署包（包含 env 目录）
zip -r cloudrun-flask-app.zip . -x ".git/*" "*.log" "Dockerfile" ".dockerignore" "__pycache__/*"
```

## 访问应用

### 获取访问地址

部署成功后，您可以参考[通过 HTTP 访问云函数](https://docs.cloudbase.net/service/access-cloud-function)设置自定义域名访问 HTTP 云函数。

访问地址格式：`https://your-function-url/`

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
curl https://your-function-url/health

# 获取用户列表
curl https://your-function-url/api/users

# 分页查询
curl "https://your-function-url/api/users?page=1&limit=2"

# 创建新用户
curl -X POST https://your-function-url/api/users \
  -H "Content-Type: application/json" \
  -d '{"name":"测试用户","email":"test@example.com"}'
```

## 常见问题

### Q: 为什么 HTTP 云函数必须使用 9000 端口？
A: CloudBase HTTP 云函数要求应用监听 9000 端口，这是平台的标准配置。通过在 `scf_bootstrap` 中设置 `PORT=9000` 环境变量来控制端口，本地开发时默认使用 8080 端口。

### Q: Flask 应用如何处理静态文件？
A: 在云函数环境中，建议将静态文件托管到 CDN 或对象存储。如果必须在应用中处理静态文件，可以配置 Flask 的静态文件路由：

```python
@app.route('/static/<path:filename>')
def static_files(filename):
    return app.send_static_file(filename)
```

### Q: 如何处理 CORS 跨域问题？
A: 安装并配置 Flask-CORS：

```bash
pip install Flask-CORS
```

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 允许所有域名跨域访问

# 或者更精确的配置
CORS(app, origins=['https://yourdomain.com'])
```

### Q: 虚拟环境依赖如何处理？
A: HTTP 云函数部署时需要包含 `env` 目录及其依赖包。在 `scf_bootstrap` 中通过 `PYTHONPATH` 环境变量指向虚拟环境的 site-packages 目录。

### Q: 如何查看云函数日志？
A: 在 CloudBase 控制台的云函数页面，点击函数名称进入详情页查看运行日志。

### Q: 云函数支持哪些 Python 版本？
A: CloudBase 支持 Python 3.7、3.8、3.9、3.10、3.11 等版本，建议使用最新的稳定版本。

## 最佳实践

### 1. 环境变量管理

```python
# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    PORT = int(os.environ.get('PORT', 8080))

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': ProductionConfig
}
```

### 2. 优化启动脚本

增强 `scf_bootstrap` 脚本：

```bash
#!/bin/bash
export PORT=9000
export PYTHONPATH="./env/lib/python3.10/site-packages:$PYTHONPATH"
export FLASK_ENV=production

# 检查依赖
if [ ! -d "env" ]; then
    echo "Virtual environment not found"
    exit 1
fi

# 启动应用
/var/lang/python310/bin/python3.10 app.py
```

### 3. 应用工厂模式

```python
# app.py
import os
from flask import Flask

def create_app(config_name=None):
    app = Flask(__name__)
    
    # 加载配置
    config_name = config_name or os.environ.get('FLASK_ENV', 'production')
    app.config.from_object(config[config_name])
    
    # 注册蓝图
    from routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
```

### 4. 请求日志中间件

```python
import time
import logging
from flask import request, g

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.before_request
def before_request():
    g.start_time = time.time()

@app.after_request
def after_request(response):
    if hasattr(g, 'start_time'):
        duration = time.time() - g.start_time
        logger.info(f'{request.method} {request.path} - {response.status_code} - {duration:.3f}s')
    return response
```

### 5. 错误处理增强

```python
import logging
from flask import jsonify

logger = logging.getLogger(__name__)

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f'Unhandled exception: {str(e)}', exc_info=True)
    return jsonify({
        'success': False,
        'message': 'Internal server error'
    }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': 'Resource not found'
    }), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'message': 'Bad request'
    }), 400
```

### 6. 部署前检查清单

- [ ] `scf_bootstrap` 文件存在且有执行权限
- [ ] 端口配置为 9000
- [ ] `requirements.txt` 包含所有必需依赖
- [ ] **包含 `env` 目录及其依赖包**
- [ ] 排除不必要的文件（如 `Dockerfile`、`.dockerignore`）
- [ ] 测试本地启动是否正常
- [ ] 检查启动脚本语法是否正确
- [ ] Flask 应用配置正确

## 性能优化

### 1. 减少冷启动时间

```python
# 全局变量缓存
import os
from flask import Flask

# 缓存应用配置
_app_config = None

def get_app_config():
    global _app_config
    if _app_config is None:
        _app_config = {
            'DEBUG': os.environ.get('DEBUG', 'False').lower() == 'true',
            'SECRET_KEY': os.environ.get('SECRET_KEY', 'dev-key')
        }
    return _app_config

app = Flask(__name__)
app.config.update(get_app_config())
```

### 2. 依赖优化

```bash
# 只安装生产依赖
pip install --no-deps -r requirements.txt

# 清理不必要的文件
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +
```

### 3. 内存管理

```python
import psutil
import logging
from flask import request

logger = logging.getLogger(__name__)

@app.after_request
def monitor_memory(response):
    # 监控内存使用
    process = psutil.Process()
    memory_info = process.memory_info()
    logger.info(f'Memory usage: {memory_info.rss / 1024 / 1024:.2f} MB')
    return response
```

### 4. 响应优化

```python
from flask import jsonify
import json

# 使用更快的 JSON 序列化
class FastJSONResponse:
    @staticmethod
    def dumps(obj):
        return json.dumps(obj, separators=(',', ':'), ensure_ascii=False)

app.json_encoder = FastJSONResponse

# 启用 gzip 压缩
@app.after_request
def after_request(response):
    response.headers['Content-Encoding'] = 'gzip'
    return response
```

---

## 相关文档

- [返回主文档](../README.md)
- [云托管部署指南](./cloud-run.md)
- [CloudBase 官方文档](https://docs.cloudbase.net/)