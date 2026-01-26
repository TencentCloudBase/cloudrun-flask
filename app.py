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
