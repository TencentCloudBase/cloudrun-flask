from flask import Blueprint, jsonify

user_bp = Blueprint('users', __name__, url_prefix='/api/users')

@user_bp.route('', methods=['GET'])
def index():
    try:
        return jsonify({
                'total': 2,
                'items': [
                    {
                        'id': 0,
                        'name': "zhangsan"
                    },
                    {
                        'id': 1,
                        'name': 'lisi'
                    }
                ]
            })
    except Exception as e:
        return jsonify(e)
